from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from cpho_cli.models.index import (
    CandidateTag,
    CanonicalTag,
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    IndexRunStats,
    SemanticFingerprint,
    TagCategory,
    TaggedReference,
    TagSource,
    TagVisibility,
    UserNotebookEntry,
    Vocabulary,
)


def _fingerprint() -> IndexFingerprint:
    return IndexFingerprint(
        file=FileFingerprint(
            problem_sha256="a" * 64,
            answer_sha256=None,
            problem_size_bytes=1,
            answer_size_bytes=None,
            problem_mtime_ns=0,
        ),
        semantic=SemanticFingerprint(
            file_fp_hash="file-hash",
            ocr_engine="rapidocr",
            ocr_engine_version="3.0",
            ocr_config_hash="ocr-config",
            tag_prompt_version="v1",
            split_prompt_version="v1",
            tag_schema_version="v1",
            model_name="openai/gpt-4o-mini",
            model_temperature=0.0,
            vocabulary_version="builtin-v0.1+ws-none+pv-none",
        ),
    )


def _index_entry(**overrides: object) -> IndexEntry:
    data = {
        "problem_id": "p1",
        "problem_path": Path("problem.pdf"),
        "problem_page_range": (1, 2),
        "answer_path": None,
        "indexed_at": datetime.now(timezone.utc),
        "physics_model_tags": [
            TaggedReference(internal_id="newton_second_law", source=TagSource.OCR_FALLBACK)
        ],
        "math_technique_tags": [],
        "heuristic_tags": [],
        "difficulty_aspects": [],
        "fingerprint": _fingerprint(),
        "ocr_cache_path": None,
        "ocr_text_length": 0,
        "tag_prompt_version": "v1",
    }
    data.update(overrides)
    return IndexEntry(**data)


def test_index_entry_round_trip() -> None:
    entry = _index_entry(difficulty_aspects=["选系统时容易忽略约束"])

    restored = IndexEntry.model_validate_json(entry.model_dump_json())

    assert restored == entry


def test_index_entry_rejects_unknown_fields() -> None:
    data = _index_entry().model_dump(mode="json")
    data["unknown_field"] = 1

    with pytest.raises(ValidationError):
        IndexEntry.model_validate(data)


def test_index_entry_rejects_legacy_report_path() -> None:
    data = _index_entry().model_dump(mode="json")
    data["solve_" + "report_path"] = "output/p1-report.json"

    with pytest.raises(ValidationError):
        IndexEntry.model_validate(data)


def test_tag_source_does_not_include_solve_report() -> None:
    assert "solve_report" not in {source.value for source in TagSource}


def test_index_entry_requires_problem_page_range() -> None:
    data = _index_entry().model_dump()
    data.pop("problem_page_range")

    with pytest.raises(ValidationError):
        IndexEntry.model_validate(data)


def test_index_entry_validates_problem_page_range() -> None:
    with pytest.raises(ValidationError):
        _index_entry(problem_page_range=(2, 1))


def test_semantic_fingerprint_requires_split_prompt_version() -> None:
    data = _fingerprint().semantic.model_dump()
    data.pop("split_prompt_version")

    with pytest.raises(ValidationError):
        SemanticFingerprint.model_validate(data)


def test_vocabulary_round_trip() -> None:
    vocab = Vocabulary(
        version="v0.1",
        tags={
            "momentum_conservation": CanonicalTag(
                internal_id="momentum_conservation",
                display_zh="动量守恒",
                category=TagCategory.PHYSICS_LAW,
                aliases=["p 守恒"],
            )
        },
        alias_index={"p守恒": "momentum_conservation"},
    )

    assert Vocabulary.model_validate_json(vocab.model_dump_json()) == vocab


def test_candidate_tag_round_trip() -> None:
    candidate = CandidateTag(
        internal_id_suggestion="energy_method",
        display_zh_suggestion="能量法",
        category=TagCategory.HEURISTIC,
        rationale="题目需要用能量守恒处理。",
        first_seen_problem_id="p1",
        first_seen_at=datetime.now(timezone.utc),
    )

    assert CandidateTag.model_validate_json(candidate.model_dump_json()) == candidate


def test_user_notebook_entry_round_trip() -> None:
    note = UserNotebookEntry(
        problem_id="p1",
        key_points=["列牛顿第二定律"],
        stuck_points=["研究对象选择"],
        updated_at=datetime.now(timezone.utc),
    )

    assert UserNotebookEntry.model_validate_json(note.model_dump_json()) == note


def test_index_fingerprint_round_trip() -> None:
    fingerprint = _fingerprint()

    assert IndexFingerprint.model_validate_json(fingerprint.model_dump_json()) == fingerprint


def test_index_run_stats_round_trip() -> None:
    stats = IndexRunStats(
        total_problems=2,
        file_changed=1,
        ocr_engine_upgrade_detected=False,
        papers_split=1,
        problems_extracted=2,
        split_method_rules=2,
        split_method_llm=0,
        split_method_single=0,
    )

    assert IndexRunStats.model_validate_json(stats.model_dump_json()) == stats


def test_user_notebook_entry_reserves_phase3_fields() -> None:
    note = UserNotebookEntry(problem_id="p1")
    fingerprint = _fingerprint()

    assert note.free_text_notes == ""
    assert note.user_tags == []
    assert fingerprint.user_learning.qa_history_sha256 is None


def test_difficulty_uses_free_text_not_enum() -> None:
    entry = _index_entry(difficulty_aspects=["选系统时容易忽略约束"])

    assert entry.difficulty_aspects == ["选系统时容易忽略约束"]


def test_tag_visibility_enum_has_three_levels() -> None:
    assert {item.value for item in TagVisibility} == {"private", "team", "public"}
