from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cpho_cli.core.index.storage import write_index
from cpho_cli.core.index.topic_api import find_problems_by_topic, get_topic_tree
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
    UserLearningFingerprint,
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
    topic_path: str | None = None,
    physics: list[str] | None = None,
) -> IndexEntry:
    refs = [
        TaggedReference(internal_id=i, source=TagSource.OCR_FALLBACK) for i in (physics or [])
    ]
    return IndexEntry(
        problem_id=problem_id,
        problem_path=Path(f"{problem_id}.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        physics_model_tags=refs,
        fingerprint=_stub_fingerprint(),
        ocr_text_length=100,
        tag_prompt_version="v0.1",
        topic_path=topic_path,
    )


def _seed_index(workspace_root: Path, entries: list[IndexEntry]) -> None:
    write_index(workspace_root / ".cpho" / "index.jsonl", entries)


def test_find_problems_by_topic_exact_match(tmp_path: Path) -> None:
    entries = [
        _make_entry("p1", topic_path="力学/天体运动/轨道理论"),
        _make_entry("p2", topic_path="力学/动力学"),
        _make_entry("p3", topic_path="热学/气体定律"),
    ]
    _seed_index(tmp_path, entries)
    result = find_problems_by_topic(tmp_path, "力学/天体运动/轨道理论")
    assert [e.problem_id for e in result] == ["p1"]


def test_find_problems_by_topic_prefix_match(tmp_path: Path) -> None:
    entries = [
        _make_entry("p1", topic_path="力学/天体运动/轨道理论"),
        _make_entry("p2", topic_path="力学/动力学"),
        _make_entry("p3", topic_path="热学/气体定律"),
    ]
    _seed_index(tmp_path, entries)
    result = find_problems_by_topic(tmp_path, "力学")
    ids = {e.problem_id for e in result}
    assert ids == {"p1", "p2"}


def test_find_problems_by_topic_no_match(tmp_path: Path) -> None:
    entries = [
        _make_entry("p1", topic_path="力学/天体运动/轨道理论"),
    ]
    _seed_index(tmp_path, entries)
    result = find_problems_by_topic(tmp_path, "光学")
    assert result == []


def test_find_problems_by_topic_skips_none_topic(tmp_path: Path) -> None:
    entries = [
        _make_entry("p1", topic_path=None),
        _make_entry("p2", topic_path="力学/动力学"),
    ]
    _seed_index(tmp_path, entries)
    result = find_problems_by_topic(tmp_path, "力学")
    assert [e.problem_id for e in result] == ["p2"]


def test_get_topic_tree(tmp_path: Path) -> None:
    taxonomy = get_topic_tree(tmp_path)
    assert len(taxonomy.roots) > 0
