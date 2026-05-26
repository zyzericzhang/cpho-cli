from __future__ import annotations

import argparse

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.index import IndexNotFoundError, ProblemNotIndexedError
from cpho_cli.core.related import RelatedProblemRow, find_related_report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="/search-related", add_help=False)
    parser.add_argument("problem_id", nargs="?")
    parser.add_argument("--top", type=int, default=None)
    parser.add_argument("--min-shared", type=int, default=1)
    return parser


async def do_search_related(session: SessionState, args: list[str]) -> None:
    try:
        ns = _parser().parse_args(args)
    except SystemExit:
        display.error("用法: /search-related [problem_id] [--top N] [--min-shared N]")
        return
    problem_id = ns.problem_id or session.current_problem_id
    if problem_id is None:
        display.error("请先 /show <problem_id>，或指定 problem_id。")
        return
    max_results = ns.top or session.max_results
    try:
        report = find_related_report(
            session.workspace_path,
            problem_id,
            min_shared_tags=ns.min_shared,
            max_results=max_results,
            output_dir=session.out_dir,
        )
    except (IndexNotFoundError, ProblemNotIndexedError) as exc:
        display.error(str(exc))
        return
    session.current_problem_id = problem_id
    session.last_related = report.rows
    print(_render_rows(report.rows))
    print(f"Markdown: {report.markdown_path}")


def _render_rows(rows: list[RelatedProblemRow]) -> str:
    if not rows:
        return "未找到同类题。"
    return display.render_table(
        ["ID", "Score", "Topic", "Tags", "Source"],
        [
            [
                row.problem_id,
                f"{row.score:.2f}",
                row.topic_path,
                ", ".join(row.tags),
                row.source,
            ]
            for row in rows
        ],
        [24, 8, 24, 32, 40],
    )


def register(registry: dict[str, Command]) -> None:
    registry["/search-related"] = Command(
        "/search-related",
        "查找当前题目的同类题",
        "/search-related [problem_id] [--top N] [--min-shared N]",
        do_search_related,
        category="技能",
    )


__all__ = ["do_search_related", "register"]
