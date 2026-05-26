from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import fitz

from cpho_cli.core.compose_pdf import assemble_composition_pdfs
from cpho_cli.core.composition import ResolvedCompositionSlot
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    UserLearningFingerprint,
)


def _write_pdf(path: Path, pages: int) -> None:
    doc = fitz.open()
    for index in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"{path.stem} page {index + 1}")
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    doc.close()


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
    problem_path: Path,
    answer_path: Path | None,
    page_range: tuple[int, int],
) -> IndexEntry:
    return IndexEntry(
        problem_id=problem_id,
        problem_path=problem_path,
        answer_path=answer_path,
        problem_page_range=page_range,
        indexed_at=datetime(2026, 5, 26, tzinfo=timezone.utc),
        fingerprint=_fingerprint(),
        ocr_text_length=10,
        tag_prompt_version="v0.1",
    )


def test_assemble_composition_pdfs_preserves_pages_and_outlines(tmp_path: Path) -> None:
    problem = tmp_path / "problems" / "p1.pdf"
    answer = tmp_path / "answers" / "p1-answer.pdf"
    _write_pdf(problem, 3)
    _write_pdf(answer, 3)
    entry = _entry(
        "p1",
        problem_path=problem.relative_to(tmp_path),
        answer_path=answer.relative_to(tmp_path),
        page_range=(1, 2),
    )

    result = assemble_composition_pdfs(
        tmp_path,
        [
            ResolvedCompositionSlot(slot=1, problem_id="p1", entry=entry),
            ResolvedCompositionSlot(slot=2, problem_id=None, entry=None, is_pass=True),
        ],
        output_dir=tmp_path / "out",
        name="mock",
    )

    with fitz.open(result.problem_pdf) as doc:
        assert len(doc) == 3
        assert doc.get_toc()[0][1] == "第 1 题"
        assert doc.get_toc()[1][1] == "第 2 题"
    with fitz.open(result.answer_pdf) as doc:
        assert len(doc) == 3
        assert doc.get_toc()[0][1] == "第 1 题 答案"
    assert result.warnings == []


def test_assemble_composition_pdfs_warns_for_missing_answer(tmp_path: Path) -> None:
    problem = tmp_path / "p1.pdf"
    _write_pdf(problem, 1)
    entry = _entry(
        "p1",
        problem_path=problem.relative_to(tmp_path),
        answer_path=Path("missing-answer.pdf"),
        page_range=(1, 1),
    )

    result = assemble_composition_pdfs(
        tmp_path,
        [ResolvedCompositionSlot(slot=1, problem_id="p1", entry=entry)],
        output_dir=tmp_path / "out",
        name="missing",
    )

    assert result.problem_pdf.exists()
    assert result.answer_pdf.exists()
    assert any("缺少答案 PDF" in warning for warning in result.warnings)
