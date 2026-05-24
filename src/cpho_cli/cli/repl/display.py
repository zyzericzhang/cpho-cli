"""Small display helpers for the REPL."""

from __future__ import annotations

import pydoc
import sys
from collections.abc import Iterable

from wcwidth import wcswidth

from cpho_cli.cli.repl.session import SessionState

RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"


def _width(text: str) -> int:
    value = wcswidth(text)
    return max(value, 0)


def _fit(text: str, width: int) -> str:
    if _width(text) <= width:
        return text + " " * (width - _width(text))
    if width <= 3:
        return "." * width
    out = ""
    for char in text:
        if _width(out + char + "...") > width:
            break
        out += char
    return out + " " * max(width - _width(out + "..."), 0) + "..."


def render_table(
    headers: list[str],
    rows: list[list[str]],
    max_widths: list[int] | None = None,
) -> str:
    all_rows = [headers, *rows]
    widths = [
        max(_width(str(row[i])) for row in all_rows)
        for i in range(len(headers))
    ]
    if max_widths is not None:
        widths = [min(width, max_widths[i]) for i, width in enumerate(widths)]

    def line(values: Iterable[str]) -> str:
        return " | ".join(_fit(str(value), widths[i]) for i, value in enumerate(values))

    sep = "-+-".join("-" * width for width in widths)
    return "\n".join([line(headers), sep, *(line(row) for row in rows)])


def pager(text: str) -> None:
    try:
        pydoc.pager(text)
    except Exception:
        print(text)


def error(msg: str) -> None:
    print(f"{RED}错误: {msg}{RESET}")


def warn(msg: str) -> None:
    print(f"{YELLOW}警告: {msg}{RESET}")


def info(msg: str) -> None:
    print(f"{BLUE}{msg}{RESET}")


def banner(session: SessionState) -> str:
    provider = session.provider_name or session.config.active_provider
    if session.index_meta is None:
        index_status = "未建立"
    else:
        index_status = (
            f"{session.index_meta.problem_count} 题 / {session.index_meta.tag_count} 标签"
        )
    return "\n".join(
        [
            "╔════════════════════════════════════════════════════╗",
            "║ CPHO REPL                                          ║",
            "╚════════════════════════════════════════════════════╝",
            f"工作空间: {session.workspace_path}",
            f"索引状态: {index_status}",
            f"Provider: {provider}",
            f"max_results: {session.max_results}",
            f"output_format: {session.output_format}",
        ]
    )


__all__ = ["banner", "error", "info", "make_index_progress_printer", "pager", "render_table", "warn"]


def make_index_progress_printer():
    """Return a callable for build_index on_progress.

    Maintains a multi-line status panel using ANSI cursor movement.
    Falls back to sequential output when stdout is not a TTY.
    """
    tty = sys.stdout.isatty()
    seq = tty

    def printer(event: dict) -> None:
        nonlocal seq
        phase = event.get("phase", "")

        if phase == "begin":
            lines = [
                f"{BLUE}索引进度: {event['total_files']} 个文件待处理{RESET}",
                "───────────────────────────",
            ]
        elif phase == "paper_split_start":
            path = event.get("file_path", "")[-50:]
            lines = [
                f"{BLUE}切分 [{event['file_index']}/{event['total_files']}]:{RESET} {path}",
                "───────────────────────────",
            ]
        elif phase == "paper_split_done":
            lines = [
                f"{BLUE}切分完成 [{event['file_index']}/{event['total_files']}]:{RESET} "
                f"累计提取 {event['problems_extracted_so_far']} 题",
                "───────────────────────────",
            ]
        elif phase == "problem_tag_start":
            lines = [
                f"{BLUE}标签 [{event['problem_id']}]:{RESET} 正在分配...",
            ]
        elif phase == "problem_tag_done":
            tag_summary = (
                f"物理={event['physics_count']} "
                f"数学={event['math_count']} "
                f"启发={event['heuristic_count']}"
            )
            topic = event.get("topic_path") or "未分类"
            lines = [
                f"完成 [{event['problem_id']}]: {tag_summary} | 主题: {topic}",
                f"累计: {event['problems_processed_so_far']} 题",
                "───────────────────────────",
            ]
        elif phase == "problem_skip":
            lines = [
                f"跳过 [{event['problem_id']}]: 指纹未变",
            ]
        elif phase == "complete":
            lines = []
            seq = False
            return
        else:
            return

        if tty:
            if seq:
                sys.stdout.write("\033[F\033[K" * 3)
            sys.stdout.write("\n".join(lines) + "\033[K\n")
            sys.stdout.flush()
        else:
            for line in lines:
                print(line)

    return printer
