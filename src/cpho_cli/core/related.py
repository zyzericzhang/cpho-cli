from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cpho_cli.core.index.api import find_related_problems
from cpho_cli.core.skill_outputs import default_markdown_path, write_markdown_atomic
from cpho_cli.models.index import IndexEntry


@dataclass(frozen=True)
class RelatedProblemRow:
    problem_id: str
    score: float
    topic_path: str
    source: str
    tags: list[str]


@dataclass(frozen=True)
class RelatedProblemReport:
    problem_id: str
    rows: list[RelatedProblemRow]
    markdown_path: Path


def find_related_report(
    workspace_root: Path,
    problem_id: str,
    *,
    min_shared_tags: int = 1,
    max_results: int = 10,
    output_dir: Path | None = None,
) -> RelatedProblemReport:
    related = find_related_problems(
        workspace_root,
        problem_id,
        min_shared_tags=min_shared_tags,
        max_results=max_results,
        same_category_weight=True,
    )
    rows = [_row(entry, score) for entry, score in related]
    markdown_path = default_markdown_path(
        workspace_root,
        "related",
        f"{problem_id}.related",
        override_dir=output_dir,
    )
    write_markdown_atomic(markdown_path, _render_markdown(problem_id, rows))
    return RelatedProblemReport(problem_id=problem_id, rows=rows, markdown_path=markdown_path)


def _row(entry: IndexEntry, score: float) -> RelatedProblemRow:
    tags = [
        ref.internal_id
        for ref in (entry.physics_model_tags + entry.math_technique_tags + entry.heuristic_tags)
    ]
    return RelatedProblemRow(
        problem_id=entry.problem_id,
        score=score,
        topic_path=entry.topic_path or "",
        source=str(entry.problem_path),
        tags=tags[:4],
    )


def _render_markdown(problem_id: str, rows: list[RelatedProblemRow]) -> str:
    lines = [
        f"# Related Problems: {problem_id}",
        "",
        "| Problem | Score | Topic | Tags | Source |",
        "|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.problem_id} | {row.score:.2f} | {row.topic_path} | "
            f"{', '.join(row.tags)} | {row.source} |"
        )
    if not rows:
        lines.append("| _none_ | 0.00 |  |  |  |")
    return "\n".join(lines) + "\n"


__all__ = ["RelatedProblemReport", "RelatedProblemRow", "find_related_report"]
