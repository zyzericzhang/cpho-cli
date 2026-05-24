from __future__ import annotations

import json
from pathlib import Path

import pytest

import cpho_cli.core.splitting as splitting
from cpho_cli.core.splitting import split_paper
from cpho_cli.models.config import ModelParams
from cpho_cli.models.documents import PaperFile, PaperKind, SplitMethod
from cpho_cli.models.ocr import OCRResult


def _fixture_ocr() -> OCRResult:
    data = json.loads(Path("tests/fixtures/paper_with_5_problems.json").read_text(encoding="utf-8"))
    return OCRResult.model_validate(data)


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


def test_split_paper_pairs_answers_by_number() -> None:
    outcome = split_paper(
        _fixture_ocr(),
        _fixture_ocr(),
        paper_file=PaperFile(path=Path("paper.pdf"), paper_kind=PaperKind.PROBLEM, total_pages=7),
        answer_file=PaperFile(path=Path("answers.pdf"), paper_kind=PaperKind.ANSWER, total_pages=7),
        paper_sha256="paper-sha",
    )

    assert outcome.split_method is SplitMethod.RULES
    assert outcome.problems[0].answer_page_range == (1, 1)
    assert outcome.unmatched_answers == []


@pytest.mark.parametrize("suffix", [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"])
def test_image_papers_return_single_problem_without_llm(
    monkeypatch: pytest.MonkeyPatch,
    suffix: str,
) -> None:
    calls: list[object] = []

    def fail_fallback(*args: object, **kwargs: object) -> None:
        calls.append((args, kwargs))
        raise AssertionError("LLM fallback should not be called for image inputs")

    monkeypatch.setattr(splitting, "split_paper_with_llm", fail_fallback)

    outcome = split_paper(
        _ocr_pages("no marker scanned mechanics problem"),
        paper_file=PaperFile(path=Path(f"scan{suffix}"), paper_kind=PaperKind.PROBLEM, total_pages=1),
        paper_sha256="paper-sha",
    )

    assert calls == []
    assert outcome.split_method is SplitMethod.SINGLE
    assert len(outcome.problems) == 1
    assert outcome.problems[0].problem_id == "paper-sha:01"
    assert outcome.problems[0].problem_page_range == (1, 1)
    assert outcome.problems[0].split_method is SplitMethod.SINGLE


def test_one_page_non_pdf_without_markers_returns_single_with_answer_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []

    def fail_fallback(*args: object, **kwargs: object) -> None:
        calls.append((args, kwargs))
        raise AssertionError("LLM fallback should not be called for one-page single input")

    monkeypatch.setattr(splitting, "split_paper_with_llm", fail_fallback)

    outcome = split_paper(
        _ocr_pages("plain one-page problem"),
        _ocr_pages("plain one-page answer"),
        paper_file=PaperFile(path=Path("scan.txt"), paper_kind=PaperKind.PROBLEM, total_pages=1),
        answer_file=PaperFile(path=Path("scan-answer.txt"), paper_kind=PaperKind.ANSWER, total_pages=1),
        paper_sha256="paper-sha",
    )

    assert calls == []
    assert outcome.split_method is SplitMethod.SINGLE
    assert outcome.problems[0].problem_text == "plain one-page problem"
    assert outcome.problems[0].answer_text == "plain one-page answer"
    assert outcome.problems[0].answer_page_range == (1, 1)


def test_multi_page_pdf_without_markers_still_uses_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []

    def fake_fallback(*args: object, **kwargs: object):
        calls.append((args, kwargs))
        return splitting.SplitOutcome(
            problems=[],
            unmatched_answers=[],
            split_method=SplitMethod.LLM,
            split_confidence=0.0,
            diagnostics=["zero problems"],
        )

    monkeypatch.setattr(splitting, "split_paper_with_llm", fake_fallback)

    outcome = split_paper(
        _ocr_pages("intro", "still no marker"),
        paper_file=PaperFile(path=Path("paper.pdf"), paper_kind=PaperKind.PROBLEM, total_pages=2),
        paper_sha256="paper-sha",
        llm_provider=object(),
        llm_params=ModelParams(name="test-model"),
    )

    assert len(calls) == 1
    assert outcome.split_method is SplitMethod.LLM
