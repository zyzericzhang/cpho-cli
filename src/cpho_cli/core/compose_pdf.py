from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import fitz

from cpho_cli.core.boundary import ensure_in_workspace
from cpho_cli.core.composition import ResolvedCompositionSlot


@dataclass(frozen=True)
class ComposePdfResult:
    problem_pdf: Path
    answer_pdf: Path
    warnings: list[str] = field(default_factory=list)


def assemble_composition_pdfs(
    workspace: Path,
    resolved_slots: list[ResolvedCompositionSlot],
    *,
    output_dir: Path | None = None,
    name: str,
) -> ComposePdfResult:
    output_root = output_dir or workspace / ".cpho" / "exports" / "compose"
    output_root.mkdir(parents=True, exist_ok=True)
    problem_pdf = output_root / f"{name}-题目.pdf"
    answer_pdf = output_root / f"{name}-答案.pdf"
    warnings: list[str] = []

    problem_doc = fitz.open()
    answer_doc = fitz.open()
    problem_toc: list[list[int | str]] = []
    answer_toc: list[list[int | str]] = []
    try:
        for resolved in resolved_slots:
            if resolved.is_pass or resolved.entry is None:
                _append_blank(problem_doc)
                _append_blank(answer_doc)
                problem_toc.append([1, f"第 {resolved.slot} 题", problem_doc.page_count])
                answer_toc.append([1, f"第 {resolved.slot} 题 答案", answer_doc.page_count])
                continue

            entry = resolved.entry
            problem_start = problem_doc.page_count + 1
            _insert_entry_pages(
                workspace, problem_doc, entry.problem_path, entry.problem_page_range
            )
            problem_toc.append([1, f"第 {resolved.slot} 题", problem_start])

            if entry.answer_path is None:
                warnings.append(f"slot {resolved.slot}: 缺少答案 PDF")
                continue
            answer_path = workspace / entry.answer_path
            if not answer_path.exists():
                warnings.append(f"slot {resolved.slot}: 缺少答案 PDF：{entry.answer_path}")
                continue
            answer_start = answer_doc.page_count + 1
            _insert_entry_pages(workspace, answer_doc, entry.answer_path, entry.problem_page_range)
            answer_toc.append([1, f"第 {resolved.slot} 题 答案", answer_start])

        if answer_doc.page_count == 0:
            _append_blank(answer_doc)
        if problem_toc:
            problem_doc.set_toc(problem_toc)
        if answer_toc:
            answer_doc.set_toc(answer_toc)
        problem_doc.save(problem_pdf)
        answer_doc.save(answer_pdf)
    finally:
        problem_doc.close()
        answer_doc.close()
    return ComposePdfResult(problem_pdf=problem_pdf, answer_pdf=answer_pdf, warnings=warnings)


def _insert_entry_pages(
    workspace: Path,
    output: fitz.Document,
    source_path: Path,
    page_range: tuple[int, int],
) -> None:
    source = ensure_in_workspace(workspace, workspace / source_path)
    start, end = page_range
    with fitz.open(source) as source_doc:
        output.insert_pdf(source_doc, from_page=start - 1, to_page=end - 1)


def _append_blank(document: fitz.Document) -> None:
    document.new_page(width=595, height=842)


__all__ = ["ComposePdfResult", "assemble_composition_pdfs"]
