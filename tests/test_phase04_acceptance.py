from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import fitz
import pytest

from cpho_cli.core.boundary import BoundaryError, ensure_in_workspace
from cpho_cli.core.compose_pdf import assemble_composition_pdfs
from cpho_cli.core.composition import (
    CompositionError,
    load_composition,
    resolve_composition_slots,
)
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

REAL_WORKSPACE = Path("/Users/ericzhang/Desktop/物理竞赛资料")


def _write_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), path.stem)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    doc.close()


def _copy_or_create_pdf(workspace: Path, name: str) -> Path:
    if REAL_WORKSPACE.exists():
        sample = next(REAL_WORKSPACE.rglob("*.pdf"), None)
        if sample is not None:
            target = workspace / name
            shutil.copy2(sample, target)
            return target
    target = workspace / name
    _write_pdf(target)
    return target


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


def _entry(problem_id: str, path: Path, workspace: Path) -> IndexEntry:
    return IndexEntry(
        problem_id=problem_id,
        problem_path=path.relative_to(workspace),
        answer_path=path.relative_to(workspace),
        problem_page_range=(1, 1),
        indexed_at=datetime(2026, 5, 26, tzinfo=timezone.utc),
        physics_model_tags=[TaggedReference(internal_id="newton", source=TagSource.OCR_FALLBACK)],
        fingerprint=_fingerprint(),
        ocr_text_length=10,
        tag_prompt_version="v0.1",
        topic_path="力学",
    )


def test_phase04_related_to_pdf_compose_acceptance(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    focal_pdf = _copy_or_create_pdf(workspace, "focal.pdf")
    related_pdf = _copy_or_create_pdf(workspace, "related.pdf")
    assert focal_pdf.is_relative_to(tmp_path)
    assert not focal_pdf.is_relative_to(REAL_WORKSPACE)
    write_index(
        workspace / ".cpho" / "index.jsonl",
        [_entry("focal", focal_pdf, workspace), _entry("related", related_pdf, workspace)],
    )

    related = find_related_report(
        workspace,
        "focal",
        output_dir=tmp_path / "exports",
    )
    composition_path = workspace / ".cpho" / "compositions" / "phase4.yml"
    composition_path.parent.mkdir(parents=True)
    composition_path.write_text(
        f"name: phase4\nslots:\n  1:\n    problem_id: {related.rows[0].problem_id}\n",
        encoding="utf-8",
    )
    composition = load_composition(composition_path)
    resolved = resolve_composition_slots(workspace, composition)
    result = assemble_composition_pdfs(workspace, resolved, name="phase4")

    assert related.rows[0].problem_id == "related"
    assert related.markdown_path.exists()
    assert result.problem_pdf.exists()
    assert result.answer_pdf.exists()
    with fitz.open(result.problem_pdf) as doc:
        assert len(doc) >= 1
        assert doc.get_toc()[0][1] == "第 1 题"


def test_phase04_boundary_and_no_match_failures_are_explicit(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.pdf"
    outside.write_text("x", encoding="utf-8")

    with pytest.raises(BoundaryError, match="文件不在当前工作空间"):
        ensure_in_workspace(workspace, outside)

    write_index(workspace / ".cpho" / "index.jsonl", [])
    composition_path = workspace / "empty.yml"
    composition_path.write_text(
        "name: empty\nslots:\n  1:\n    spec:\n      topic: 光学\n",
        encoding="utf-8",
    )
    with pytest.raises(CompositionError, match="找不到符合 slot 1"):
        resolve_composition_slots(workspace, load_composition(composition_path))
