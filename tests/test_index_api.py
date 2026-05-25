from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpho_cli.core.index import IndexNotFoundError, ProblemNotIndexedError, IndexBuildError
from cpho_cli.core.index.api import (
    add_problem_tags,
    find_related_problems,
    get_problem_entry,
    query_index,
    remove_problem_tags,
    update_problem_tags,
)
from cpho_cli.core.index.notebook import get_problem_notes, set_problem_notes
from cpho_cli.core.index.storage import write_index
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
    UserLearningFingerprint,
    UserNotebookEntry,
)


def _stub_fingerprint() -> IndexFingerprint:
    return IndexFingerprint(
        file=FileFingerprint(
            problem_sha256="a" * 64,
            answer_sha256=None,
            problem_size_bytes=100,
            answer_size_bytes=None,
            problem_mtime_ns=0,
        ),
        semantic=SemanticFingerprint(
            file_fp_hash="a" * 16,
            ocr_engine="rapidocr",
            ocr_engine_version="3.0",
            ocr_config_hash="c" * 64,
            tag_prompt_version="v0.1",
            split_prompt_version="v1",
            tag_schema_version="v1",
            model_name="test",
            model_temperature=0.0,
            vocabulary_version="v0.1",
        ),
        user_learning=UserLearningFingerprint(),
    )


def _make_entry(
    problem_id: str,
    physics: list[str] | None = None,
    math: list[str] | None = None,
    heuristic: list[str] | None = None,
) -> IndexEntry:
    def _refs(ids: list[str] | None) -> list[TaggedReference]:
        if not ids:
            return []
        return [
            TaggedReference(internal_id=i, source=TagSource.OCR_FALLBACK) for i in ids
        ]

    return IndexEntry(
        problem_id=problem_id,
        problem_path=Path(f"{problem_id}.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        physics_model_tags=_refs(physics),
        math_technique_tags=_refs(math),
        heuristic_tags=_refs(heuristic),
        fingerprint=_stub_fingerprint(),
        ocr_text_length=100,
        tag_prompt_version="v0.1",
    )


def _seed_index(workspace_root: Path, entries: list[IndexEntry]) -> None:
    write_index(workspace_root / ".cpho" / "index.jsonl", entries)


# --- query_index tests ---


def test_query_index_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(IndexNotFoundError):
        query_index(tmp_path)


def test_query_index_by_physics_model(tmp_path: Path) -> None:
    p1 = _make_entry("p1", physics=["newton_second_law"])
    p2 = _make_entry("p2", physics=["energy_conservation"])
    p3 = _make_entry("p3", physics=["newton_second_law", "energy_conservation"])
    _seed_index(tmp_path, [p1, p2, p3])

    result = query_index(tmp_path, physics_model_ids=["newton_second_law"])
    ids = {e.problem_id for e in result}
    assert ids == {"p1", "p3"}


def test_query_index_match_mode_all(tmp_path: Path) -> None:
    p1 = _make_entry("p1", physics=["newton_second_law"])
    p2 = _make_entry("p2", physics=["newton_second_law", "energy_conservation"])
    _seed_index(tmp_path, [p1, p2])

    result = query_index(
        tmp_path,
        physics_model_ids=["newton_second_law", "energy_conservation"],
        match_mode="all",
    )
    assert [e.problem_id for e in result] == ["p2"]


def test_query_index_match_mode_any(tmp_path: Path) -> None:
    p1 = _make_entry("p1", physics=["newton_second_law"])
    p2 = _make_entry("p2", physics=["newton_second_law", "energy_conservation"])
    _seed_index(tmp_path, [p1, p2])

    result = query_index(
        tmp_path,
        physics_model_ids=["newton_second_law", "energy_conservation"],
        match_mode="any",
    )
    ids = {e.problem_id for e in result}
    assert ids == {"p1", "p2"}


def test_query_index_across_categories_conjunctive(tmp_path: Path) -> None:
    p1 = _make_entry("p1", physics=["newton_second_law"], math=["dimensional_analysis"])
    p2 = _make_entry("p2", physics=["newton_second_law"])
    _seed_index(tmp_path, [p1, p2])

    result = query_index(
        tmp_path,
        physics_model_ids=["newton_second_law"],
        math_technique_ids=["dimensional_analysis"],
    )
    assert [e.problem_id for e in result] == ["p1"]


def test_query_index_invalid_match_mode_raises(tmp_path: Path) -> None:
    _seed_index(tmp_path, [_make_entry("p1")])
    with pytest.raises(ValueError, match="match_mode must be any or all"):
        query_index(tmp_path, match_mode="bad")


# --- get_problem_entry tests ---


def test_get_problem_entry_returns_entry(tmp_path: Path) -> None:
    p1 = _make_entry("p1", physics=["newton_second_law"])
    _seed_index(tmp_path, [p1])
    entry = get_problem_entry(tmp_path, "p1")
    assert entry is not None
    assert entry.problem_id == "p1"


def test_get_problem_entry_returns_none_when_missing(tmp_path: Path) -> None:
    _seed_index(tmp_path, [_make_entry("p1")])
    assert get_problem_entry(tmp_path, "nonexistent") is None


# --- find_related_problems tests ---


def test_find_related_problems_same_category_overlap(tmp_path: Path) -> None:
    p1 = _make_entry("p1", physics=["newton_second_law", "energy_conservation"])
    p2 = _make_entry("p2", physics=["newton_second_law"])
    p3 = _make_entry("p3", math=["dimensional_analysis"])
    _seed_index(tmp_path, [p1, p2, p3])

    related = find_related_problems(tmp_path, "p1")
    # p2 shares 1 same-category tag, p3 shares 0
    assert len(related) >= 1
    assert related[0][0].problem_id == "p2"
    assert related[0][1] == 1.0


def test_find_related_problems_cross_category_bonus(tmp_path: Path) -> None:
    p1 = _make_entry(
        "p1", physics=["newton_second_law"], heuristic=["free_body_diagram"]
    )
    p2 = _make_entry(
        "p2", physics=["newton_second_law"], heuristic=["free_body_diagram"]
    )
    p3 = _make_entry("p3", physics=["newton_second_law"])
    _seed_index(tmp_path, [p1, p2, p3])

    related = find_related_problems(tmp_path, "p1", same_category_weight=True)
    scores = {r[0].problem_id: r[1] for r in related}
    assert scores["p2"] == 2.0  # 2 same-category overlaps
    assert scores["p3"] == 1.0


def test_find_related_min_shared_tags_threshold(tmp_path: Path) -> None:
    p1 = _make_entry(
        "p1", physics=["newton_second_law"], heuristic=["free_body_diagram"]
    )
    p2 = _make_entry(
        "p2", physics=["newton_second_law"], heuristic=["free_body_diagram"]
    )
    p3 = _make_entry("p3", physics=["newton_second_law"])
    _seed_index(tmp_path, [p1, p2, p3])

    related = find_related_problems(tmp_path, "p1", min_shared_tags=2)
    ids = [r[0].problem_id for r in related]
    assert "p2" in ids
    assert "p3" not in ids


def test_find_related_max_results_truncates(tmp_path: Path) -> None:
    focal = _make_entry("focal", physics=["newton_second_law"])
    others = [
        _make_entry(f"p{i}", physics=["newton_second_law"]) for i in range(15)
    ]
    _seed_index(tmp_path, [focal, *others])

    related = find_related_problems(tmp_path, "focal", max_results=5)
    assert len(related) == 5


def test_find_related_problem_not_indexed_raises(tmp_path: Path) -> None:
    _seed_index(tmp_path, [_make_entry("p1")])
    with pytest.raises(ProblemNotIndexedError, match="Not indexed"):
        find_related_problems(tmp_path, "nonexistent")


# --- notebook tests ---


def test_get_problem_notes_returns_none_when_missing(tmp_path: Path) -> None:
    assert get_problem_notes(tmp_path, "p1") is None


def test_set_then_get_problem_notes_roundtrip(tmp_path: Path) -> None:
    now = datetime.now(timezone.utc)
    notes = UserNotebookEntry(
        problem_id="p1",
        key_points=["关键步骤"],
        stuck_points=["卡点"],
        updated_at=now,
    )
    set_problem_notes(tmp_path, notes)
    loaded = get_problem_notes(tmp_path, "p1")
    assert loaded is not None
    assert loaded.problem_id == "p1"
    assert loaded.key_points == ["关键步骤"]
    assert loaded.stuck_points == ["卡点"]


def test_set_problem_notes_rejects_path_traversal(tmp_path: Path) -> None:
    notes = UserNotebookEntry(problem_id="../escape", key_points=["x"])
    with pytest.raises(IndexBuildError, match="Invalid problem_id"):
        set_problem_notes(tmp_path, notes)


def test_set_problem_notes_atomic_no_tmp_left(tmp_path: Path) -> None:
    notes = UserNotebookEntry(problem_id="p1", key_points=["a"])
    set_problem_notes(tmp_path, notes)
    assert not (tmp_path / ".cpho" / "notebook" / "p1.json.tmp").exists()
    assert (tmp_path / ".cpho" / "notebook" / "p1.json").exists()


# --- user tag write API tests ---


def test_add_problem_tags_records_provenance_and_classification(tmp_path: Path) -> None:
    _seed_index(tmp_path, [_make_entry("p1")])

    entry = add_problem_tags(
        tmp_path,
        "p1",
        ["energy_conservation", "自定义标签"],
        skill_name="solve",
        reasoning="根据解析补充标签。",
    )

    assert len(entry.user_tags) == 1
    tag_entry = entry.user_tags[0]
    assert tag_entry.tags == ["energy_conservation", "自定义标签"]
    assert tag_entry.canonical_tags == ["energy_conservation"]
    assert tag_entry.unverified_tags == ["自定义标签"]
    assert tag_entry.skill_name == "solve"
    assert tag_entry.reasoning_snippet == "根据解析补充标签。"
    assert tag_entry.timestamp.tzinfo is not None

    reloaded = get_problem_entry(tmp_path, "p1")
    assert reloaded is not None
    assert reloaded.user_tags == entry.user_tags


def test_update_problem_tags_replaces_all_user_tag_entries(tmp_path: Path) -> None:
    _seed_index(tmp_path, [_make_entry("p1")])
    add_problem_tags(tmp_path, "p1", ["old"], skill_name="solve", reasoning="old")

    entry = update_problem_tags(
        tmp_path,
        "p1",
        ["free_body_diagram"],
        skill_name="explain",
        reasoning="替换为当前 skill 输出。",
    )

    assert len(entry.user_tags) == 1
    assert entry.user_tags[0].tags == ["free_body_diagram"]
    assert entry.user_tags[0].canonical_tags == ["free_body_diagram"]
    assert entry.user_tags[0].skill_name == "explain"


def test_remove_problem_tags_removes_matching_strings(tmp_path: Path) -> None:
    _seed_index(tmp_path, [_make_entry("p1")])
    add_problem_tags(
        tmp_path,
        "p1",
        ["energy_conservation", "自定义标签"],
        skill_name="solve",
        reasoning="根据解析补充标签。",
    )

    entry = remove_problem_tags(tmp_path, "p1", ["自定义标签"])

    assert len(entry.user_tags) == 1
    assert entry.user_tags[0].tags == ["energy_conservation"]
    assert entry.user_tags[0].canonical_tags == ["energy_conservation"]
    assert entry.user_tags[0].unverified_tags == []


def test_add_problem_tags_missing_problem_raises(tmp_path: Path) -> None:
    _seed_index(tmp_path, [_make_entry("p1")])

    with pytest.raises(ProblemNotIndexedError):
        add_problem_tags(
            tmp_path,
            "missing",
            ["energy_conservation"],
            skill_name="solve",
            reasoning="x",
        )


def test_add_problem_tags_rejects_path_traversal_problem_id(tmp_path: Path) -> None:
    _seed_index(tmp_path, [_make_entry("p1")])

    with pytest.raises(IndexBuildError, match="Invalid problem_id"):
        add_problem_tags(
            tmp_path,
            "../escape",
            ["energy_conservation"],
            skill_name="solve",
            reasoning="x",
        )
