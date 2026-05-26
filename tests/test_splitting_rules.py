import json
from pathlib import Path

from cpho_cli.core.splitting.rules import split_paper_by_rules, validate_rule_split
from cpho_cli.models.documents import PaperFile, PaperKind, ProblemEntry, SplitMethod
from cpho_cli.models.ocr import OCRResult


def load_fixture(name: str = "paper_with_5_problems.json") -> OCRResult:
    data = json.loads((Path("tests/fixtures") / name).read_text(encoding="utf-8"))
    return OCRResult.model_validate(data)


def paper_file(path: str = "paper.pdf", pages: int = 7) -> PaperFile:
    return PaperFile(path=Path(path), paper_kind=PaperKind.PROBLEM, total_pages=pages)


def answer_file(path: str = "answers.pdf", pages: int = 7) -> PaperFile:
    return PaperFile(path=Path(path), paper_kind=PaperKind.ANSWER, total_pages=pages)


def test_rule_split_fixture_produces_five_problem_entries() -> None:
    outcome = split_paper_by_rules(
        load_fixture(),
        paper_file=paper_file(),
        paper_sha256="paper-sha",
    )

    assert [problem.problem_number for problem in outcome.problems] == [1, 2, 3, 4, 5]
    assert [problem.problem_id for problem in outcome.problems] == [
        "paper-sha:01",
        "paper-sha:02",
        "paper-sha:03",
        "paper-sha:04",
        "paper-sha:05",
    ]
    assert [problem.problem_page_range for problem in outcome.problems] == [
        (1, 1),
        (2, 3),
        (4, 4),
        (5, 6),
        (7, 7),
    ]
    assert all(problem.split_method is SplitMethod.RULES for problem in outcome.problems)
    assert validate_rule_split(outcome, total_pages=7) == []


def test_rule_split_attaches_answers_by_problem_number() -> None:
    paper_ocr = load_fixture()
    answer_ocr = load_fixture()

    outcome = split_paper_by_rules(
        paper_ocr,
        answer_ocr,
        paper_file=paper_file(),
        answer_file=answer_file(),
        paper_sha256="paper-sha",
    )

    assert [problem.answer_page_range for problem in outcome.problems] == [
        (1, 1),
        (2, 3),
        (4, 4),
        (5, 6),
        (7, 7),
    ]
    assert all(problem.answer_paper_path == Path("answers.pdf") for problem in outcome.problems)
    assert outcome.unmatched_answers == []


def test_rule_split_reports_unmatched_answers_without_raising() -> None:
    answer_ocr = OCRResult.model_validate(
        {
            "pages": [
                {
                    "page_number": 1,
                    "blocks": [{"text": "题6 extra answer", "page_number": 1}],
                }
            ]
        }
    )

    outcome = split_paper_by_rules(
        load_fixture(),
        answer_ocr,
        paper_file=paper_file(),
        answer_file=answer_file(pages=1),
        paper_sha256="paper-sha",
    )

    assert [answer.problem_number for answer in outcome.unmatched_answers] == [6]
    assert "answer-number mismatch" in validate_rule_split(outcome, total_pages=7, answer_numbers=[6])


def entry(number: int, page_range: tuple[int, int]) -> ProblemEntry:
    return ProblemEntry(
        problem_id=f"sha:{number:02d}",
        paper_path=Path("paper.pdf"),
        problem_number=number,
        problem_page_range=page_range,
        problem_text=f"Problem {number}",
        split_method=SplitMethod.RULES,
        split_confidence=0.9,
    )


def test_validate_rule_split_diagnoses_invalid_shapes() -> None:
    empty = split_paper_by_rules(
        OCRResult.model_validate({"pages": [{"page_number": 1, "blocks": [{"text": "intro", "page_number": 1}]}]}),
        paper_file=paper_file(pages=1),
        paper_sha256="paper-sha",
    )
    assert "zero problems" in validate_rule_split(empty, total_pages=1)

    duplicate = empty.model_copy(update={"problems": [entry(1, (1, 1)), entry(1, (2, 2))]})
    assert "duplicate problem numbers" in validate_rule_split(duplicate, total_pages=2)

    gap = empty.model_copy(update={"problems": [entry(1, (1, 1)), entry(3, (2, 2))]})
    assert "non-contiguous problem numbers" in validate_rule_split(gap, total_pages=2)

    page_gap = empty.model_copy(update={"problems": [entry(1, (1, 1)), entry(2, (3, 3))]})
    assert "page gaps or overlaps" in validate_rule_split(page_gap, total_pages=3)

    page_overlap = empty.model_copy(update={"problems": [entry(1, (1, 2)), entry(2, (2, 3))]})
    assert "page gaps or overlaps" in validate_rule_split(page_overlap, total_pages=3)
