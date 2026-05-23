"""Exam composition: filter problems by topic + tag intersection."""

from __future__ import annotations

from pathlib import Path

from cpho_cli.core.index.storage import load_index
from cpho_cli.models.index import IndexEntry


def compose_problem_list(
    workspace_root: Path,
    *,
    topic_path: str | None = None,
    tag_ids: list[str] | None = None,
) -> list[IndexEntry]:
    """Return entries matching both topic prefix and tag filters (intersection).

    If both filters are None, returns all entries.
    """
    entries = load_index(workspace_root)

    if topic_path is not None:
        entries = [
            e
            for e in entries
            if e.topic_path is not None
            and (e.topic_path == topic_path or e.topic_path.startswith(topic_path + "/"))
        ]

    if tag_ids:
        filtered: list[IndexEntry] = []
        tag_set = set(tag_ids)
        for e in entries:
            all_ids = {
                ref.internal_id
                for ref in (
                    e.physics_model_tags + e.math_technique_tags + e.heuristic_tags
                )
            }
            if tag_set & all_ids:
                filtered.append(e)
        entries = filtered

    return entries
