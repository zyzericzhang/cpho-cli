from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import fitz
from typer.testing import CliRunner

from cpho_cli.cli.app import app
from cpho_cli.core.index.storage import write_index
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
    UserLearningFingerprint,
)

runner = CliRunner()


def _write_pdf(path: Path) -> None:
    doc = fitz.open()
    doc.new_page()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    doc.close()


def _fingerprint() -> IndexFingerprint:
    return IndexFingerprint(
        file=FileFingerprint(
            problem_sha256="a" * 64,
            answer_sha256="b" * 64,
            problem_size_bytes=1,
            answer_size_bytes=1,
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


def _seed_workspace(workspace: Path) -> None:
    problem = workspace / "p1.pdf"
    answer = workspace / "p1-answer.pdf"
    _write_pdf(problem)
    _write_pdf(answer)
    entry = IndexEntry(
        problem_id="p1",
        problem_path=problem.relative_to(workspace),
        answer_path=answer.relative_to(workspace),
        problem_page_range=(1, 1),
        indexed_at=datetime(2026, 5, 26, tzinfo=timezone.utc),
        physics_model_tags=[TaggedReference(internal_id="newton", source=TagSource.OCR_FALLBACK)],
        fingerprint=_fingerprint(),
        ocr_text_length=10,
        tag_prompt_version="v0.1",
        topic_path="力学",
    )
    write_index(workspace / ".cpho" / "index.jsonl", [entry])


def test_compose_new_creates_template(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["compose", "new", "mock", "--count", "2", "--workspace", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert (tmp_path / ".cpho" / "compositions" / "mock.yml").exists()


def test_compose_build_writes_pdfs(tmp_path: Path) -> None:
    _seed_workspace(tmp_path)
    composition = tmp_path / "paper.yml"
    composition.write_text(
        "name: paper\nslots:\n  1:\n    problem_id: p1\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["compose", "build", str(composition), "--workspace", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert (tmp_path / ".cpho" / "exports" / "compose" / "paper-题目.pdf").exists()
    assert "paper-答案.pdf" in result.output


def test_compose_rejects_outside_composition_file(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-compose.yml"
    outside.write_text("name: bad\nslots: {}\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["compose", "build", str(outside), "--workspace", str(tmp_path)],
    )

    assert result.exit_code != 0
    assert "文件不在当前工作空间" in result.output
