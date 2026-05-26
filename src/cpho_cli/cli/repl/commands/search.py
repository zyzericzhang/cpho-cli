"""Search and show commands for indexed problems."""

from __future__ import annotations

import argparse

from prompt_toolkit.completion import Completer, Completion

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.commands.workspace import INDEX_MISSING_MSG
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.index import (
    IndexNotFoundError,
    ProblemNotIndexedError,
    VocabularyError,
    get_problem_entry,
    load_vocabulary,
    query_index,
)
from cpho_cli.models.index import IndexEntry, TagCategory

_TAG_CACHE: dict[str, dict[str, str]] = {
    "physics_model": {},
    "math_technique": {},
    "heuristic": {},
}


def refresh_tag_cache(session: SessionState) -> None:
    try:
        vocabulary = load_vocabulary(session.workspace_path)
    except VocabularyError:
        for values in _TAG_CACHE.values():
            values.clear()
        return
    for values in _TAG_CACHE.values():
        values.clear()
    category_map = {
        TagCategory.PHYSICS_MODEL: "physics_model",
        TagCategory.MATH_TECHNIQUE: "math_technique",
        TagCategory.HEURISTIC: "heuristic",
    }
    for tag in vocabulary.tags.values():
        bucket = category_map.get(tag.category)
        if bucket is not None:
            _TAG_CACHE[bucket][tag.internal_id] = tag.display_zh


class TagCompleter(Completer):
    def __init__(self, category: str | None = None) -> None:
        self.category = category

    def get_completions(self, document, complete_event):  # type: ignore[no-untyped-def]
        token = document.text_before_cursor.split()[-1] if document.text_before_cursor.split() else ""
        current = token.rsplit(",", 1)[-1]
        start = -len(current)
        buckets = [self.category] if self.category else list(_TAG_CACHE)
        for bucket in buckets:
            if bucket is None:
                continue
            for internal_id, display_zh in sorted(_TAG_CACHE[bucket].items()):
                if internal_id.startswith(current) or display_zh.startswith(current):
                    yield Completion(internal_id, start_position=start, display_meta=display_zh)


def _split_ids(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _ids_for_query(query: str | None, explicit: list[str] | None, bucket: str) -> list[str] | None:
    if explicit:
        return explicit
    if not query:
        return None
    matches = [
        internal_id
        for internal_id, display_zh in _TAG_CACHE[bucket].items()
        if query in {internal_id, display_zh} or query in display_zh or query in internal_id
    ]
    return matches or None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="/search", add_help=False)
    parser.add_argument("query", nargs="?")
    parser.add_argument("--physics-model")
    parser.add_argument("--math-technique")
    parser.add_argument("--heuristic")
    parser.add_argument("--match-mode", default="any", choices=("any", "all"))
    parser.add_argument("--limit", type=int)
    return parser


def _entry_tags(entry: IndexEntry) -> str:
    refs = entry.physics_model_tags + entry.math_technique_tags + entry.heuristic_tags
    return ", ".join(ref.internal_id for ref in refs)


def _summary(entry: IndexEntry) -> str:
    if entry.difficulty_aspects:
        return "；".join(entry.difficulty_aspects[:2])
    return entry.topic_path or "未分类"


async def do_search(session: SessionState, args: list[str]) -> None:
    if session.index_meta is None:
        display.error(INDEX_MISSING_MSG.format(workspace=session.workspace_path))
        return
    try:
        ns = _parser().parse_args(args)
    except SystemExit:
        display.error("参数无效。用法: /search [query] [--physics-model id] [--limit N]")
        return
    limit = ns.limit or session.max_results
    physics_ids = _ids_for_query(ns.query, _split_ids(ns.physics_model), "physics_model")
    math_ids = _ids_for_query(ns.query, _split_ids(ns.math_technique), "math_technique")
    heuristic_ids = _ids_for_query(ns.query, _split_ids(ns.heuristic), "heuristic")
    try:
        results = query_index(
            session.workspace_path,
            physics_model_ids=physics_ids,
            math_technique_ids=math_ids,
            heuristic_ids=heuristic_ids,
            match_mode=ns.match_mode,
        )
    except IndexNotFoundError:
        display.error(INDEX_MISSING_MSG.format(workspace=session.workspace_path))
        return
    shown = results[:limit]
    session.last_search_query = " ".join(args) if args else ""
    session.last_search_result_ids = [entry.problem_id for entry in shown]
    if not shown:
        print("未找到匹配题目。")
        return
    rows = [
        [
            str(i),
            entry.problem_id,
            _summary(entry),
            _entry_tags(entry),
            f"{entry.problem_path}:{entry.problem_page_range[0]}-{entry.problem_page_range[1]}",
        ]
        for i, entry in enumerate(shown, start=1)
    ]
    print(display.render_table(["序号", "ID", "题目摘要", "标签", "来源"], rows, [4, 24, 32, 40, 48]))
    if len(results) > limit:
        print(f"仅显示前 {limit} 条，共 {len(results)} 条；可用 /set max_results 调整。")


def _clean_text(text: str) -> str:
    return text.replace("\x1b", "").replace("\r", "\n")


def _read_ocr_text(session: SessionState, entry: IndexEntry) -> str:
    if entry.ocr_cache_path is None:
        return ""
    path = entry.ocr_cache_path
    if not path.is_absolute():
        path = session.workspace_path / path
    if not path.exists():
        return ""
    return _clean_text(path.read_text(encoding="utf-8", errors="replace"))


def _render_detail(session: SessionState, entry: IndexEntry, *, full: bool) -> str:
    ocr_text = _read_ocr_text(session, entry)
    body = ocr_text if full else ocr_text[:200]
    if not body:
        body = "无 OCR 缓存文本"
    return "\n".join(
        [
            f"ID: {entry.problem_id}",
            f"来源: {entry.problem_path} 页码 {entry.problem_page_range[0]}-{entry.problem_page_range[1]}",
            f"索引时间: {entry.indexed_at}",
            f"标签: {_entry_tags(entry) or '无'}",
            "",
            body,
            "" if full else "\n使用 /show <id> --full 查看完整文本。",
        ]
    )


async def do_show(session: SessionState, args: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="/show", add_help=False)
    parser.add_argument("ref", nargs="?")
    parser.add_argument("--full", action="store_true")
    try:
        ns = parser.parse_args(args)
    except SystemExit:
        display.error("参数无效。用法: /show <序号|problem_id> [--full]")
        return
    if not ns.ref:
        display.error("用法: /show <序号|problem_id> [--full]")
        return
    if ns.ref.isdigit():
        if not session.last_search_result_ids:
            display.error("尚未搜索，请先 /search ...")
            return
        index = int(ns.ref) - 1
        if index < 0 or index >= len(session.last_search_result_ids):
            display.error("序号超出范围")
            return
        problem_id = session.last_search_result_ids[index]
    else:
        problem_id = ns.ref
    try:
        entry = get_problem_entry(session.workspace_path, problem_id)
    except (IndexNotFoundError, ProblemNotIndexedError):
        display.error(INDEX_MISSING_MSG.format(workspace=session.workspace_path))
        return
    if entry is None:
        display.error(f"未找到题目: {problem_id}")
        return
    session.current_problem_id = entry.problem_id
    detail = _render_detail(session, entry, full=ns.full)
    if ns.full:
        display.pager(detail)
    else:
        print(detail)


def register(registry: dict[str, Command]) -> None:
    registry["/search"] = Command(
        "/search",
        "按标签搜索题目",
        "/search [tag] [--physics-model id] [--limit N]",
        do_search,
        completer=TagCompleter(),
        category="搜索",
    )
    registry["/show"] = Command(
        "/show",
        "显示搜索结果中的题目详情",
        "/show <序号|problem_id> [--full]",
        do_show,
        category="搜索",
    )


__all__ = ["TagCompleter", "do_search", "do_show", "refresh_tag_cache", "register"]
