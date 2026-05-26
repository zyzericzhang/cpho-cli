from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpho_cli.core.composition import CompositionError, resolve_composition_slots
from cpho_cli.core.index.storage import write_index
from cpho_cli.models.composition import CompositionFile, CompositionSlot, SlotSpec
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
    UserLearningFingerprint,
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
            file_fp_hash="a" * 16,
            ocr_engine="rapidocr",
            ocr_engine_version="3.0",
            ocr_config_hash="c" * 64,
            tag_prompt_version="v0.1",
            split_prompt_version="v1",
            tag_schema_version="v1",
            model_name="fake",
            model_temperature=0.0,
            vocabulary_version="v0.1",
        ),
        user_learning=UserLearningFingerprint(),
    )


def _entry(problem_id: str, *, topic: str, tags: list[str]) -> IndexEntry:
    return IndexEntry(
        problem_id=problem_id,
        problem_path=Path(f"{problem_id}.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime(2026, 5, 26, tzinfo=timezone.utc),
        physics_model_tags=[
            TaggedReference(internal_id=tag, source=TagSource.OCR_FALLBACK) for tag in tags
        ],
        fingerprint=_fingerprint(),
        ocr_text_length=10,
        tag_prompt_version="v0.1",
        topic_path=topic,
    )


def test_resolve_composition_slots_handles_explicit_pass_and_spec(tmp_path: Path) -> None:
    write_index(
        tmp_path / ".cpho" / "index.jsonl",
        [
            _entry("p1", topic="力学", tags=["newton"]),
            _entry("p2", topic="力学/动力学", tags=["newton"]),
        ],
    )
    composition = CompositionFile(
        name="mock",
        slots={
            1: CompositionSlot(problem_id="p1"),
            2: CompositionSlot(pass_slot=True),
            3: CompositionSlot(spec=SlotSpec(topic="力学", tags=["newton"])),
        },
    )

    resolved = resolve_composition_slots(tmp_path, composition)

    assert [slot.problem_id for slot in resolved] == ["p1", None, "p2"]
    assert resolved[1].is_pass is True


def test_resolve_composition_slots_raises_when_no_spec_match(tmp_path: Path) -> None:
    write_index(
        tmp_path / ".cpho" / "index.jsonl",
        [_entry("p1", topic="力学", tags=["newton"])],
    )
    composition = CompositionFile(
        name="mock",
        slots={1: CompositionSlot(spec=SlotSpec(topic="光学"))},
    )

    with pytest.raises(CompositionError, match="找不到符合 slot 1"):
        resolve_composition_slots(tmp_path, composition)
