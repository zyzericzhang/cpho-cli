"""Workspace, index, config, and resume commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prompt_toolkit.shortcuts import prompt

from cpho_cli.cli.repl import display
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


def confirm_index_run(prompt_text: str) -> bool:
    return prompt(prompt_text).strip().lower() in {"y", "yes"}


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
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--only-new", action="store_true")
    parser.add_argument("--ocr-strategy", default="prompt", choices=("prompt", "reuse", "rebuild", "new-only"))
    return parser


async def do_index(session: SessionState, args: list[str]) -> None:
    try:
        ns = _parser().parse_args(args)
    except SystemExit:
        display.error("参数无效。用法: /index [--dry-run] [--force] [--only-new] [--ocr-strategy prompt|reuse|rebuild|new-only]")
        return
    try:
        preview = build_index(
            session.workspace_path,
            provider_name=session.provider_name,
            force=ns.force,
            only_new=ns.only_new,
            dry_run=True,
            ocr_strategy=ns.ocr_strategy,
        )
        display.info(
            "索引预览: "
            f"扫描 {preview.total_problems} 个输入，试卷 {preview.papers_split} 份，"
            f"将提取 {preview.problems_extracted} 道题。"
        )
        if ns.dry_run:
            return
        if not confirm_index_run("确认执行真实索引? [y/N]: "):
            print("已取消。")
            return
        result = build_index(
            session.workspace_path,
            provider_name=session.provider_name,
            force=ns.force,
            only_new=ns.only_new,
            dry_run=False,
            ocr_strategy=ns.ocr_strategy,
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
    registry["/index"] = Command("/index", "预览并可确认建立索引", "/index [--dry-run]", do_index, category="工作空间")
    registry["/reload-index"] = Command("/reload-index", "刷新索引元数据和补全缓存", "/reload-index", do_reload_index, category="工作空间")
    registry["/resume"] = Command("/resume", "显式恢复上次会话上下文", "/resume", do_resume, category="工作空间")


__all__ = [
    "INDEX_MISSING_MSG",
    "confirm_index_run",
    "do_config",
    "do_index",
    "do_reload_index",
    "do_resume",
    "do_status",
    "do_workspace",
    "register",
]
