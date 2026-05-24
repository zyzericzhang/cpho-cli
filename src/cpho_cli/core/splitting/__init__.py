from __future__ import annotations

from cpho_cli.core.llm import LLMProvider
from cpho_cli.core.splitting.llm import split_paper_with_llm
from cpho_cli.core.splitting.rules import split_paper_by_rules, validate_rule_split
from cpho_cli.models.config import ModelParams
from cpho_cli.models.documents import PaperFile, SplitOutcome
from cpho_cli.models.ocr import OCRResult


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
    rule_outcome = split_paper_by_rules(
        paper_ocr,
        answer_ocr,
        paper_file=paper_file,
        answer_file=answer_file,
        paper_sha256=paper_sha256,
    )
    if not rule_outcome.diagnostics:
        return rule_outcome

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


__all__ = [
    "split_paper",
    "split_paper_by_rules",
    "split_paper_with_llm",
    "validate_rule_split",
]
