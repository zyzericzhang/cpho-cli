from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import cpho_cli.core.splitting as splitting
from cpho_cli.core.splitting import split_paper
from cpho_cli.models.config import ModelParams
from cpho_cli.models.documents import PaperFile, PaperKind, SplitMethod, SplitOutcome
from cpho_cli.models.ocr import OCRResult


def _ocr_pages(*texts: str) -> OCRResult:
    return OCRResult.model_validate(
        {
            "pages": [
                {
                    "page_number": index + 1,
                    "blocks": [{"text": text, "page_number": index + 1}],
                }
                for index, text in enumerate(texts)
            ]
        }
    )


def _paper(path: str = "paper.pdf", pages: int = 2) -> PaperFile:
    return PaperFile(path=Path(path), paper_kind=PaperKind.PROBLEM, total_pages=pages)


def _answer(path: str = "answers.pdf", pages: int = 1) -> PaperFile:
    return PaperFile(path=Path(path), paper_kind=PaperKind.ANSWER, total_pages=pages)


class ProviderSentinel:
    pass


def test_valid_rule_split_returns_without_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fail_fallback(*args: object, **kwargs: object) -> SplitOutcome:
        calls.append({"args": args, "kwargs": kwargs})
        raise AssertionError("LLM fallback should not be called")

    monkeypatch.setattr(splitting, "split_paper_with_llm", fail_fallback)

    outcome = split_paper(
        _ocr_pages("第1题 mechanics", "第2题 optics"),
        paper_file=_paper(),
        paper_sha256="paper-sha",
        llm_provider=ProviderSentinel(),
        llm_params=ModelParams(name="unused"),
    )

    assert calls == []
    assert outcome.split_method is SplitMethod.RULES
    assert outcome.diagnostics == []
    assert [problem.problem_number for problem in outcome.problems] == [1, 2]


@pytest.mark.parametrize(
    ("paper_ocr", "answer_ocr", "paper_file", "answer_file", "expected_diagnostic"),
    [
        (_ocr_pages("intro only"), None, _paper(pages=1), None, "zero problems"),
        (_ocr_pages("第1题 mechanics", "第3题 optics"), None, _paper(), None, "non-contiguous problem numbers"),
        (_ocr_pages("第1题 mechanics", "第1题 optics"), None, _paper(), None, "duplicate problem numbers"),
        (
            _ocr_pages("第1题 mechanics"),
            _ocr_pages("第2题 answer"),
            _paper(pages=1),
            _answer(pages=1),
            "answer-number mismatch",
        ),
    ],
)
def test_invalid_rule_diagnostics_trigger_llm_once(
    monkeypatch: pytest.MonkeyPatch,
    paper_ocr: OCRResult,
    answer_ocr: OCRResult | None,
    paper_file: PaperFile,
    answer_file: PaperFile | None,
    expected_diagnostic: str,
) -> None:
    calls: list[dict[str, Any]] = []

    def fake_fallback(*args: object, **kwargs: object) -> SplitOutcome:
        calls.append({"args": args, "kwargs": kwargs})
        return SplitOutcome(
            problems=[],
            unmatched_answers=[],
            split_method=SplitMethod.LLM,
            split_confidence=0.0,
            diagnostics=[expected_diagnostic],
        )

    monkeypatch.setattr(splitting, "split_paper_with_llm", fake_fallback)

    outcome = split_paper(
        paper_ocr,
        answer_ocr,
        paper_file=paper_file,
        answer_file=answer_file,
        paper_sha256="paper-sha",
        llm_provider=ProviderSentinel(),
        llm_params=ModelParams(name="test-model"),
    )

    assert outcome.split_method is SplitMethod.LLM
    assert len(calls) == 1
    assert calls[0]["kwargs"]["provider"].__class__ is ProviderSentinel
    assert calls[0]["kwargs"]["params"].name == "test-model"


def test_required_fallback_without_provider_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="LLM provider"):
        split_paper(
            _ocr_pages("intro only"),
            paper_file=_paper(pages=1),
            paper_sha256="paper-sha",
        )
