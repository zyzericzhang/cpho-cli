from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cpho_cli.core.index.storage import write_index
from cpho_cli.core.related import find_related_report
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


def _entry(
    problem_id: str,
    *,
    physics: list[str] | None = None,
    math: list[str] | None = None,
    heuristic: list[str] | None = None,
    topic: str | None = None,
) -> IndexEntry:
    def refs(values: list[str] | None) -> list[TaggedReference]:
        return [
            TaggedReference(internal_id=value, source=TagSource.OCR_FALLBACK)
            for value in (values or [])
        ]

    return IndexEntry(
        problem_id=problem_id,
        problem_path=Path(f"{problem_id}.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime(2026, 5, 26, tzinfo=timezone.utc),
        physics_model_tags=refs(physics),
        math_technique_tags=refs(math),
        heuristic_tags=refs(heuristic),
        fingerprint=_fingerprint(),
        ocr_text_length=10,
        tag_prompt_version="v0.1",
        topic_path=topic,
    )


def test_find_related_report_writes_markdown_and_preserves_index(tmp_path: Path) -> None:
    write_index(
        tmp_path / ".cpho" / "index.jsonl",
        [
            _entry("p1", physics=["newton"], math=["algebra"], topic="力学"),
            _entry("p2", physics=["newton"], topic="力学/动力学"),
            _entry("p3", heuristic=["free_body"], topic="力学"),
        ],
    )

    report = find_related_report(
        tmp_path,
        "p1",
        max_results=10,
        min_shared_tags=1,
        output_dir=tmp_path / "exports",
    )

    assert [row.problem_id for row in report.rows] == ["p2"]
    assert report.rows[0].score == 1.0
    assert report.markdown_path.exists()
    text = report.markdown_path.read_text(encoding="utf-8")
    assert "# Related Problems: p1" in text
    assert "| p2 | 1.00 |" in text
