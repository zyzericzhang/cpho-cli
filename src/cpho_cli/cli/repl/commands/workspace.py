"""Workspace, index, config, and resume commands."""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.display import make_index_progress_printer
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.persistence import read_session, write_session
from cpho_cli.cli.repl.session import SessionState, load_index_meta
from cpho_cli.core.config import ConfigError
from cpho_cli.core.index import (
    IndexBuildError,
    OcrUpgradeDecisionRequired,
    VocabularyError,
    build_index,
)
from cpho_cli.core.workspace import discover_workspace

INDEX_MISSING_MSG = "未找到索引，请先运行: cpho index --workspace {workspace}"


def _refresh_tag_cache_if_available(session: SessionState) -> None:
    try:
        from cpho_cli.cli.repl.commands.search import refresh_tag_cache
    except ImportError:
        return
    refresh_tag_cache(session)


async def _confirm_index_run(session: SessionState, prompt_text: str) -> bool:
    ps = session.prompt_session
    if ps is None:
        return input(prompt_text).strip().lower() in {"y", "yes"}
    result = await ps.prompt_async(prompt_text)  # type: ignore[union-attr]
    return result.strip().lower() in {"y", "yes"}


def _list_subdirs(root: Path) -> list[str]:
    """Return relative paths of all directories under *root*, sorted."""
    dirs: list[str] = []
    for p in sorted(root.rglob("*")):
        if p.is_dir() and not p.name.startswith("."):
            try:
                rel = p.relative_to(root).as_posix()
                if rel != ".":
                    dirs.append(rel)
            except ValueError:
                continue
    return dirs


async def _resolve_target_path(
    session: SessionState,
    path_arg: str | None,
) -> Path | None:
    """Resolve user input to a subpath under workspace.

    Supports relative paths (``subdir/nested``) and absolute paths
    (``/Users/.../workspace/subdir``, ``~/...``) that are under workspace.

    If *path_arg* is given (via --path) and resolves immediately, returns the
    relative Path.  Otherwise enters an interactive loop until a valid path is
    entered or the user presses Enter on an empty line.

    Returns the relative subpath, or None if user cancels (empty input).
    """
    ws_root = session.workspace_path.resolve()
    ps = session.prompt_session

    if path_arg is not None:
        user_input = path_arg.strip()
        if not user_input:
            display.error("--path 需要指定一个路径")
            return None
        # Resolve once; if it fails, drop into interactive loop for retry.
        target = Path(user_input)
        if user_input.startswith("~") or target.is_absolute():
            full_path = target.expanduser().resolve()
        else:
            full_path = (ws_root / target).resolve()
        try:
            full_path.relative_to(ws_root)
        except ValueError:
            display.error("路径必须在工作空间内")
        else:
            if full_path.is_dir():
                return full_path.relative_to(ws_root)

    while True:
        if ps is None:
            display.error("当前环境不支持交互式输入")
            return None
        hint = "待索引路径（相对/绝对均可，回车退出）"
        user_input = await ps.prompt_async(f"{hint}: ")  # type: ignore[union-attr]
        user_input = user_input.strip()

        if not user_input:
            print("已取消。")
            return None

        # Resolve: absolute (~ or /) vs relative
        target = Path(user_input)
        if user_input.startswith("~") or target.is_absolute():
            full_path = target.expanduser().resolve()
        else:
            full_path = (ws_root / target).resolve()

        # Security: must be within workspace
        try:
            full_path.relative_to(ws_root)
        except ValueError:
            display.error("路径必须在工作空间内")
            continue

        if full_path.is_dir():
            return full_path.relative_to(ws_root)

        # Fuzzy match
        all_dirs = _list_subdirs(ws_root)
        if not all_dirs:
            display.error(f"目录不存在: {user_input}")
            continue

        matches = difflib.get_close_matches(user_input, all_dirs, n=5, cutoff=0.4)
        if not matches:
            display.error(f"目录不存在: {user_input}，也找不到相似目录")
            continue

        print(f"目录 '{user_input}' 不存在。相似目录:")
        for i, name in enumerate(matches, 1):
            print(f"  [{i}] {name}")

        if ps is None:
            choice = input("选择序号 (直接回车重试): ").strip()
        else:
            choice = await ps.prompt_async("选择序号 (直接回车重试): ")  # type: ignore[union-attr]
        if not choice:
            continue
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                return Path(matches[idx])
        except ValueError:
            pass
        display.error("无效选择")


async def do_workspace(session: SessionState, args: list[str]) -> None:
    if not args:
        print(f"当前工作空间: {session.workspace_path}")
        return
    path = Path(args[0]).expanduser().resolve()
    if not path.is_dir():
        display.error(f"工作空间不存在: {path}")
        return
    discover_workspace(path)
    session.workspace_path = path
    session.index_path = path / ".cpho" / "index.jsonl"
    session.index_meta = load_index_meta(path)
    write_session(session)
    _refresh_tag_cache_if_available(session)
    print(f"已切换工作空间: {path}")


async def do_status(session: SessionState, args: list[str]) -> None:
    provider = session.provider_name or session.config.active_provider
    model = session.config.model.name or "未设置"
    print(f"工作空间: {session.workspace_path}")
    if session.index_meta is None:
        print("索引状态: 未建立")
    else:
        print(f"索引状态: {session.index_meta.problem_count} 题 / {session.index_meta.tag_count} 标签")
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"max_results: {session.max_results}")
    print(f"output_format: {session.output_format}")


async def do_config(session: SessionState, args: list[str]) -> None:
    config = session.config
    print(f"active_provider: {session.provider_name or config.active_provider}")
    print(f"model.name: {config.model.name}")
    print(f"model.temperature: {config.model.temperature}")
    names = sorted(config.providers) or ["openrouter"]
    print("provider profiles: " + ", ".join(names))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="/index", add_help=False)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--path", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--force-all", action="store_true")
    parser.add_argument("--only-new", action="store_true")
    parser.add_argument("--vision", action="store_true")
    parser.add_argument(
        "--ocr-strategy", default="prompt", choices=("prompt", "reuse", "rebuild", "new-only")
    )
    return parser


async def do_index(session: SessionState, args: list[str]) -> None:
    try:
        ns = _parser().parse_args(args)
    except SystemExit:
        display.error(
            "参数无效。用法: /index [--all] [--path PATH] [--dry-run] [--force]"
            " [--force-all] [--only-new] [--vision]"
            " [--ocr-strategy prompt|reuse|rebuild|new-only]\n"
            "  --vision 默认关闭；开启后可能上传 PDF/图片到配置的 provider。\n"
            "  PATH 支持相对路径或绝对路径（必须在工作空间内）"
        )
        return

    if ns.all and ns.path:
        display.error("--all 和 --path 不能同时使用")
        return

    # Resolve target
    if ns.all:
        target_subpath: Path | None = None
        show_preview = True
    elif ns.path is not None:
        try:
            target_subpath = await _resolve_target_path(session, ns.path)
        except ValueError as exc:
            display.error(str(exc))
            return
        if target_subpath is None:
            return
        show_preview = False
    else:
        try:
            target_subpath = await _resolve_target_path(session, None)
        except ValueError as exc:
            display.error(str(exc))
            return
        if target_subpath is None:
            return
        show_preview = False

    try:
        if show_preview:
            preview = build_index(
                session.workspace_path,
                config_path=session.config_path,
                provider_name=session.provider_name,
                force=ns.force,
                force_all=ns.force_all,
                vision=ns.vision,
                only_new=ns.only_new,
                dry_run=True,
                ocr_strategy=ns.ocr_strategy,
                on_progress=make_index_progress_printer(),
            )
            display.info(
                "索引预览: "
                f"扫描 {preview.total_problems} 个输入；真实题目数将在 OCR/切分后确定。"
            )
            if ns.dry_run:
                return
            if not await _confirm_index_run(session, "确认执行真实索引? [y/N]: "):
                print("已取消。")
                return
            result = build_index(
                session.workspace_path,
                config_path=session.config_path,
                provider_name=session.provider_name,
                force=ns.force,
                force_all=ns.force_all,
                vision=ns.vision,
                only_new=ns.only_new,
                dry_run=False,
                ocr_strategy=ns.ocr_strategy,
                on_progress=make_index_progress_printer(),
            )
        else:
            result = build_index(
                session.workspace_path,
                config_path=session.config_path,
                provider_name=session.provider_name,
                force=ns.force,
                force_all=ns.force_all,
                vision=ns.vision,
                only_new=ns.only_new,
                dry_run=False,
                ocr_strategy=ns.ocr_strategy,
                target_subpath=target_subpath,
                on_progress=make_index_progress_printer(),
            )
    except (ConfigError, IndexBuildError, VocabularyError, OcrUpgradeDecisionRequired, ValueError) as exc:
        display.error(str(exc))
        return

    session.index_meta = load_index_meta(session.workspace_path)
    _refresh_tag_cache_if_available(session)
    print(f"索引完成: {result.total_problems} 个输入")


async def do_reload_index(session: SessionState, args: list[str]) -> None:
    session.index_meta = load_index_meta(session.workspace_path)
    _refresh_tag_cache_if_available(session)
    if session.index_meta is None:
        print("索引未建立")
    else:
        print(f"索引已刷新: {session.index_meta.problem_count} 题")


def _apply_search_context(session: SessionState, payload: dict[str, object]) -> None:
    raw_query = payload.get("last_search_query")
    session.last_search_query = raw_query if isinstance(raw_query, str) else None
    ids = payload.get("last_search_result_ids")
    session.last_search_result_ids = [str(item) for item in ids] if isinstance(ids, list) else []
    current = payload.get("current_problem_id")
    session.current_problem_id = current if isinstance(current, str) else None


async def do_resume(session: SessionState, args: list[str]) -> None:
    try:
        payload = read_session()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        display.error(f"无法读取 session.json: {exc}")
        return
    if payload is None:
        print("没有可恢复的会话。")
        return
    workspace = Path(str(payload.get("workspace_path", session.workspace_path))).expanduser()
    if workspace.is_dir():
        session.workspace_path = workspace
        session.index_path = workspace / ".cpho" / "index.jsonl"
    else:
        display.warn("保存的工作空间不存在，保留当前工作空间。")
    session.index_meta = load_index_meta(session.workspace_path)
    max_results = payload.get("max_results")
    if isinstance(max_results, int) and max_results > 0:
        session.max_results = max_results
    output_format = payload.get("output_format")
    if output_format in {"compact", "full"}:
        session.output_format = str(output_format)

    saved_mtime = payload.get("index_mtime_ns")
    saved_version = payload.get("index_version")
    current_meta = session.index_meta
    if (
        current_meta is not None
        and saved_mtime == current_meta.index_mtime_ns
        and saved_version == current_meta.index_version
    ):
        _apply_search_context(session, payload)
        print("已恢复上次搜索上下文。")
    else:
        session.last_search_query = None
        session.last_search_result_ids = []
        session.current_problem_id = None
        display.warn("索引已变化或未建立，已丢弃上次搜索上下文。")


def register(registry: dict[str, Command]) -> None:
    registry["/workspace"] = Command("/workspace", "查看或切换工作空间", "/workspace [path]", do_workspace, category="工作空间")
    registry["/status"] = Command("/status", "显示当前工作空间与索引状态", "/status", do_status, category="工作空间")
    registry["/config"] = Command("/config", "显示安全配置摘要", "/config", do_config, category="工作空间")
    registry["/index"] = Command("/index", "预览并可确认建立索引", "/index [--all] [--path PATH] [--dry-run] [--force] [--force-all] [--only-new] [--vision]", do_index, category="工作空间")
    registry["/reload-index"] = Command("/reload-index", "刷新索引元数据和补全缓存", "/reload-index", do_reload_index, category="工作空间")
    registry["/resume"] = Command("/resume", "显式恢复上次会话上下文", "/resume", do_resume, category="工作空间")


__all__ = [
    "INDEX_MISSING_MSG",
    "do_config",
    "do_index",
    "do_reload_index",
    "do_resume",
    "do_status",
    "do_workspace",
    "register",
]
