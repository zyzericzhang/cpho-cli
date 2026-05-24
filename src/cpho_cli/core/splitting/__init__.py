from __future__ import annotations

from cpho_cli.core.llm import LLMProvider
from cpho_cli.core.splitting.llm import split_paper_with_llm
from cpho_cli.core.splitting.rules import split_paper_by_rules, validate_rule_split
from cpho_cli.models.config import ModelParams
from cpho_cli.models.documents import (
    PaperFile,
    ProblemEntry,
    SplitMethod,
    SplitOutcome,
    make_problem_id,
)
from cpho_cli.models.ocr import OCRResult


_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def split_paper(
    paper_ocr: OCRResult,
    answer_ocr: OCRResult | None = None,
    *,
    paper_file: PaperFile,
    answer_file: PaperFile | None = None,
    paper_sha256: str,
    llm_provider: LLMProvider | None = None,
    llm_params: ModelParams | None = None,
) -> SplitOutcome:
    if paper_file.path.suffix.lower() in _IMAGE_SUFFIXES:
        return _single_outcome(
            paper_ocr,
            answer_ocr,
            paper_file=paper_file,
            answer_file=answer_file,
            paper_sha256=paper_sha256,
        )

    rule_outcome = split_paper_by_rules(
        paper_ocr,
        answer_ocr,
        paper_file=paper_file,
        answer_file=answer_file,
        paper_sha256=paper_sha256,
    )
    if not rule_outcome.diagnostics:
        return rule_outcome
    if rule_outcome.diagnostics == ["zero problems"] and paper_file.total_pages == 1:
        return _single_outcome(
            paper_ocr,
            answer_ocr,
            paper_file=paper_file,
            answer_file=answer_file,
            paper_sha256=paper_sha256,
        )

    if llm_provider is None:
        raise ValueError("LLM provider configuration is required for split fallback.")

    return split_paper_with_llm(
        paper_ocr,
        answer_ocr,
        paper_file=paper_file,
        answer_file=answer_file,
        paper_sha256=paper_sha256,
        provider=llm_provider,
        params=llm_params or ModelParams(),
    )


def _single_outcome(
    paper_ocr: OCRResult,
    answer_ocr: OCRResult | None,
    *,
    paper_file: PaperFile,
    answer_file: PaperFile | None,
    paper_sha256: str,
) -> SplitOutcome:
    answer_text = _ocr_text(answer_ocr) if answer_ocr is not None else None
    problem = ProblemEntry(
        problem_id=make_problem_id(paper_sha256, 1),
        paper_path=paper_file.path,
        problem_number=1,
        problem_page_range=(1, paper_file.total_pages),
        problem_text=_ocr_text(paper_ocr),
        answer_paper_path=answer_file.path if answer_text is not None and answer_file else None,
        answer_page_range=(1, answer_file.total_pages) if answer_text is not None and answer_file else None,
        answer_text=answer_text,
        split_method=SplitMethod.SINGLE,
        split_confidence=1.0,
    )
    return SplitOutcome(
        problems=[problem],
        unmatched_answers=[],
        split_method=SplitMethod.SINGLE,
        split_confidence=1.0,
        diagnostics=[],
    )


def _ocr_text(ocr: OCRResult) -> str:
    return "\n".join(
        block.text
        for page in sorted(ocr.pages, key=lambda item: item.page_number)
        for block in page.blocks
        if block.text.strip()
    )


__all__ = [
    "split_paper",
    "split_paper_by_rules",
    "split_paper_with_llm",
    "validate_rule_split",
]
