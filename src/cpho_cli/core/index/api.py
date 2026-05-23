"""Python query API for the index (Phase 3 surface)."""

from __future__ import annotations

from pathlib import Path

from cpho_cli.core.index import ProblemNotIndexedError
from cpho_cli.core.index.storage import load_index
from cpho_cli.models.index import IndexEntry


def query_index(
    workspace_root: Path,
    *,
    physics_model_ids: list[str] | None = None,
    math_technique_ids: list[str] | None = None,
    heuristic_ids: list[str] | None = None,
    match_mode: str = "any",
) -> list[IndexEntry]:
    """Filter index entries by tag internal_ids.

    Each non-None filter list constrains one tag bucket (physics_model_tags,
    math_technique_tags, heuristic_tags).  ``match_mode`` controls matching
    *within* each bucket:

    - ``"any"``: entry matches a bucket if it shares at least one id with the
      filter list.
    - ``"all"``: entry matches a bucket if it contains *all* ids in the filter
      list.

    Across buckets the logic is *conjunctive* -- an entry is returned only when
    it matches **every** non-None bucket filter.

    Example::

        # Find entries that have newton_second_law AND dimensional_analysis
        query_index(ws, physics_model_ids=["newton_second_law"],
                    math_technique_ids=["dimensional_analysis"])
    """
    if match_mode not in {"any", "all"}:
        raise ValueError(f"match_mode must be any or all, got {match_mode!r}")

    entries = load_index(workspace_root)

    filters: list[tuple[list[str], str]] = []
    if physics_model_ids is not None:
        filters.append((physics_model_ids, "physics_model_tags"))
    if math_technique_ids is not None:
        filters.append((math_technique_ids, "math_technique_tags"))
    if heuristic_ids is not None:
        filters.append((heuristic_ids, "heuristic_tags"))

    if not filters:
        return entries

    result: list[IndexEntry] = []
    for entry in entries:
        matched_all_buckets = True
        for filter_ids, attr in filters:
            entry_ids = {ref.internal_id for ref in getattr(entry, attr)}
            if match_mode == "any":
                if not (set(filter_ids) & entry_ids):
                    matched_all_buckets = False
                    break
            else:  # "all"
                if not set(filter_ids).issubset(entry_ids):
                    matched_all_buckets = False
                    break
        if matched_all_buckets:
            result.append(entry)
    return result


def get_problem_entry(workspace_root: Path, problem_id: str) -> IndexEntry | None:
    entries = load_index(workspace_root)
    for entry in entries:
        if entry.problem_id == problem_id:
            return entry
    return None


def find_related_problems(
    workspace_root: Path,
    problem_id: str,
    *,
    min_shared_tags: int = 1,
    max_results: int = 10,
    same_category_weight: bool = True,
) -> list[tuple[IndexEntry, float]]:
    """Find problems related to *problem_id* by tag overlap.

    Scoring: each same-category shared canonical tag contributes 1.0.
    If ``same_category_weight`` is True, each cross-category shared tag
    contributes 0.5.

    ``min_shared_tags`` filters on the raw integer count of shared canonical
    internal_ids (not the weighted score).
    """
    entries = load_index(workspace_root)

    focal: IndexEntry | None = None
    for entry in entries:
        if entry.problem_id == problem_id:
            focal = entry
            break
    if focal is None:
        raise ProblemNotIndexedError(f"Not indexed: {problem_id}")

    def _ids(entry: IndexEntry, attr: str) -> set[str]:
        return {ref.internal_id for ref in getattr(entry, attr)}

    focal_pm = _ids(focal, "physics_model_tags")
    focal_mt = _ids(focal, "math_technique_tags")
    focal_h = _ids(focal, "heuristic_tags")
    focal_all = focal_pm | focal_mt | focal_h

    scored: list[tuple[IndexEntry, float]] = []
    for other in entries:
        if other.problem_id == problem_id:
            continue
        other_pm = _ids(other, "physics_model_tags")
        other_mt = _ids(other, "math_technique_tags")
        other_h = _ids(other, "heuristic_tags")

        same_cat_count = (
            len(focal_pm & other_pm)
            + len(focal_mt & other_mt)
            + len(focal_h & other_h)
        )
        other_all = other_pm | other_mt | other_h
        total_shared = len(focal_all & other_all)

        if total_shared < min_shared_tags:
            continue

        score = float(same_cat_count)
        if same_category_weight:
            cross = total_shared - same_cat_count
            score += cross * 0.5

        scored.append((other, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:max_results]
