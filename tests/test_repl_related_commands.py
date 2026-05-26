from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpho_cli.cli.repl.commands.related import do_search_related
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.index.storage import write_index
from cpho_cli.models.config import AppConfig
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


def _entry(problem_id: str, *, physics: list[str], topic: str) -> IndexEntry:
    return IndexEntry(
        problem_id=problem_id,
        problem_path=Path(f"{problem_id}.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime(2026, 5, 26, tzinfo=timezone.utc),
        physics_model_tags=[
            TaggedReference(internal_id=value, source=TagSource.OCR_FALLBACK) for value in physics
        ],
        fingerprint=_fingerprint(),
        ocr_text_length=10,
        tag_prompt_version="v0.1",
        topic_path=topic,
    )


@pytest.mark.asyncio
async def test_search_related_uses_current_problem_and_sets_last_related(
    tmp_path: Path,
    capsys,
) -> None:
    write_index(
        tmp_path / ".cpho" / "index.jsonl",
        [
            _entry("p1", physics=["newton"], topic="力学"),
            _entry("p2", physics=["newton"], topic="力学/动力学"),
        ],
    )
    session = SessionState(
        workspace_path=tmp_path,
        config=AppConfig(),
        current_problem_id="p1",
    )

    await do_search_related(session, ["--top", "5"])

    output = capsys.readouterr().out
    assert "p2" in output
    assert session.last_related is not None
    assert [row.problem_id for row in session.last_related] == ["p2"]
