from __future__ import annotations

import json
from pathlib import Path

import pytest

import cpho_cli.core.splitting as splitting
from cpho_cli.core.splitting import split_paper
from cpho_cli.models.documents import PaperFile, PaperKind
from cpho_cli.models.ocr import OCRResult


FIXTURE_DIR = Path("tests/fixtures/splitting")
EXPECTED_PATH = FIXTURE_DIR / "ipho_style_multi_problem.expected.json"


def _load_expected() -> dict[str, object]:
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


def test_golden_ipho_style_multi_problem_split_uses_committed_ocr_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = _load_expected()
    paper_path = FIXTURE_DIR / str(expected["paper_pdf"])
    answer_path = FIXTURE_DIR / str(expected["answer_pdf"])
    assert paper_path.exists()
    assert answer_path.exists()

    def fail_llm_fallback(*args: object, **kwargs: object) -> None:
        raise AssertionError("Golden splitting regression must not call live LLM fallback")

    monkeypatch.setattr(splitting, "split_paper_with_llm", fail_llm_fallback)

    paper_ocr = OCRResult.model_validate(expected["problem_ocr_pages"])
    answer_ocr = OCRResult.model_validate(expected["answer_ocr_pages"])
    outcome = split_paper(
        paper_ocr,
        answer_ocr,
        paper_file=PaperFile(
            path=paper_path,
            paper_kind=PaperKind.PROBLEM,
            total_pages=len(paper_ocr.pages),
        ),
        answer_file=PaperFile(
            path=answer_path,
            paper_kind=PaperKind.ANSWER,
            total_pages=len(answer_ocr.pages),
        ),
        paper_sha256="golden-paper-sha",
    )

    expected_numbers = set(expected["expected_problem_numbers"])
    problems_by_number = {problem.problem_number: problem for problem in outcome.problems}
    assert set(problems_by_number) == expected_numbers

    expected_ranges = expected["expected_problem_page_ranges"]
    assert isinstance(expected_ranges, dict)
    for problem_number, expected_range in expected_ranges.items():
        actual_start, actual_end = problems_by_number[int(problem_number)].problem_page_range
        expected_start, expected_end = expected_range
        assert abs(actual_start - expected_start) <= 1
        assert abs(actual_end - expected_end) <= 1

    expected_answer_ranges = expected["expected_answer_page_ranges"]
    assert isinstance(expected_answer_ranges, dict)
    paired_numbers = {
        problem.problem_number
        for problem in outcome.problems
        if problem.answer_paper_path == answer_path
        and problem.answer_page_range is not None
        and problem.answer_text
    }
    assert paired_numbers == expected_numbers
    for problem_number, expected_range in expected_answer_ranges.items():
        assert problems_by_number[int(problem_number)].answer_page_range == tuple(expected_range)

    assert outcome.unmatched_answers == []
