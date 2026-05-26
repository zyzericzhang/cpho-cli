from pathlib import Path

import pytest
from pydantic import ValidationError

from cpho_cli.models.documents import (
    AnswerKeyFile,
    PaperFile,
    PaperKind,
    ProblemAnswerPair,
    ProblemEntry,
    ProblemFile,
    SplitMethod,
    WorkspaceDiscoveryResult,
    make_problem_id,
)


def valid_problem_entry(**overrides: object) -> ProblemEntry:
    data: dict[str, object] = {
        "problem_id": "abc123:01",
        "paper_path": Path("paper.pdf"),
        "problem_number": 1,
        "problem_page_range": (1, 2),
        "problem_text": "第1题 A mechanics problem",
        "split_method": SplitMethod.RULES,
        "split_confidence": 0.95,
    }
    data.update(overrides)
    return ProblemEntry(**data)


@pytest.mark.parametrize(
    "field",
    [
        "problem_id",
        "paper_path",
        "problem_number",
        "problem_page_range",
        "problem_text",
        "split_method",
        "split_confidence",
    ],
)
def test_problem_entry_requires_core_fields(field: str) -> None:
    data = valid_problem_entry().model_dump()
    data.pop(field)

    with pytest.raises(ValidationError):
        ProblemEntry(**data)


@pytest.mark.parametrize(
    "page_range",
    [
        (0, 1),
        (-1, 1),
        (3, 2),
        (1, 2, 3),
    ],
)
def test_problem_entry_rejects_invalid_page_ranges(page_range: tuple[int, ...]) -> None:
    with pytest.raises(ValidationError):
        valid_problem_entry(problem_page_range=page_range)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_problem_entry_rejects_invalid_confidence(confidence: float) -> None:
    with pytest.raises(ValidationError):
        valid_problem_entry(split_confidence=confidence)


def test_problem_entry_rejects_empty_text_and_non_positive_number() -> None:
    with pytest.raises(ValidationError):
        valid_problem_entry(problem_text="   ")

    with pytest.raises(ValidationError):
        valid_problem_entry(problem_number=0)


def test_make_problem_id_is_reproducible() -> None:
    assert make_problem_id("abc123", 1) == "abc123:01"
    assert make_problem_id("abc123", 12) == "abc123:12"
    assert make_problem_id("abc123", 1) == make_problem_id("abc123", 1)


def test_split_method_single_exists() -> None:
    assert SplitMethod.SINGLE.value == "single"


def test_paper_file_validates_page_count() -> None:
    PaperFile(path=Path("paper.pdf"), paper_kind=PaperKind.PROBLEM, total_pages=1)

    with pytest.raises(ValidationError):
        PaperFile(path=Path("paper.pdf"), paper_kind=PaperKind.PROBLEM, total_pages=0)


def test_existing_document_imports_remain_compatible() -> None:
    problem = ProblemFile(path=Path("problem.pdf"))
    answer = AnswerKeyFile(path=Path("problem-answer.pdf"))
    pair = ProblemAnswerPair(problem=problem, answer=answer)
    result = WorkspaceDiscoveryResult(pairs=[pair], unmatched_problems=[problem], ambiguous=[])

    assert result.pairs[0].problem.path == problem.path
    assert result.unmatched_problems == [problem]
    assert result.unmatched_papers == [problem]
