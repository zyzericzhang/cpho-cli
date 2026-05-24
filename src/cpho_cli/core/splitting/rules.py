from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from cpho_cli.models.documents import (
    PaperFile,
    ProblemEntry,
    SplitMethod,
    SplitOutcome,
    make_problem_id,
)
from cpho_cli.models.ocr import OCRResult


_MARKER_RE = re.compile(
    r"^\s*(?:第\s*(?P<di>\d+)\s*题|题\s*(?P<ti>\d+)|\((?P<paren>\d+)\)|"
    r"(?P<dot>\d+)[.．、]|Problem\s+(?P<problem>\d+)\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class _Marker:
    number: int
    page_number: int
    ordinal: int


@dataclass(frozen=True)
class _Section:
    number: int
    page_range: tuple[int, int]
    text: str


def split_paper_by_rules(
    paper_ocr: OCRResult,
    answer_ocr: OCRResult | None = None,
    *,
    paper_file: PaperFile,
    answer_file: PaperFile | None = None,
    paper_sha256: str,
) -> SplitOutcome:
    paper_sections = _sections_from_ocr(paper_ocr)
    answer_sections = _sections_from_ocr(answer_ocr) if answer_ocr is not None else []
    answers_by_number = {section.number: section for section in answer_sections}

    problems: list[ProblemEntry] = []
    for section in paper_sections:
        answer = answers_by_number.get(section.number)
        problems.append(
            ProblemEntry(
                problem_id=make_problem_id(paper_sha256, section.number),
                paper_path=paper_file.path,
                problem_number=section.number,
                problem_page_range=section.page_range,
                problem_text=section.text,
                answer_paper_path=answer_file.path if answer and answer_file else None,
                answer_page_range=answer.page_range if answer else None,
                answer_text=answer.text if answer else None,
                split_method=SplitMethod.RULES,
                split_confidence=1.0,
            )
        )

    problem_numbers = {problem.problem_number for problem in problems}
    unmatched_answers = [
        _answer_entry(section, answer_file.path if answer_file else paper_file.path)
        for section in answer_sections
        if section.number not in problem_numbers
    ]
    outcome = SplitOutcome(
        problems=problems,
        unmatched_answers=unmatched_answers,
        split_method=SplitMethod.RULES,
        split_confidence=1.0 if problems else 0.0,
        diagnostics=[],
    )
    diagnostics = validate_rule_split(
        outcome,
        total_pages=_total_pages(paper_ocr),
        answer_numbers=[section.number for section in answer_sections] if answer_ocr is not None else None,
    )
    return outcome.model_copy(update={"diagnostics": diagnostics})


def validate_rule_split(
    outcome: SplitOutcome,
    total_pages: int,
    answer_numbers: list[int] | None = None,
) -> list[str]:
    diagnostics: list[str] = []
    if not outcome.problems:
        diagnostics.append("zero problems")
        return diagnostics

    numbers = [problem.problem_number for problem in outcome.problems]
    if len(numbers) != len(set(numbers)):
        diagnostics.append("duplicate problem numbers")

    sorted_numbers = sorted(set(numbers))
    expected_numbers = list(range(sorted_numbers[0], sorted_numbers[-1] + 1))
    if sorted_numbers != expected_numbers:
        diagnostics.append("non-contiguous problem numbers")

    ranges = sorted(problem.problem_page_range for problem in outcome.problems)
    if ranges[0][0] != 1 or ranges[-1][1] != total_pages:
        diagnostics.append("page gaps or overlaps")
    else:
        for previous, current in zip(ranges, ranges[1:]):
            if current[0] != previous[1] + 1:
                diagnostics.append("page gaps or overlaps")
                break

    if answer_numbers is not None and set(answer_numbers) != set(numbers):
        diagnostics.append("answer-number mismatch")

    return diagnostics


def _answer_entry(section: _Section, answer_path: Path) -> ProblemEntry:
    return ProblemEntry(
        problem_id=f"unmatched-answer:{section.number:02d}",
        paper_path=answer_path,
        problem_number=section.number,
        problem_page_range=section.page_range,
        problem_text=section.text,
        split_method=SplitMethod.RULES,
        split_confidence=1.0,
    )


def _sections_from_ocr(ocr: OCRResult | None) -> list[_Section]:
    if ocr is None or not ocr.pages:
        return []

    markers = _find_markers(ocr)
    if not markers:
        return []

    total_pages = _total_pages(ocr)
    sections: list[_Section] = []
    for index, marker in enumerate(markers):
        next_page = markers[index + 1].page_number if index + 1 < len(markers) else total_pages + 1
        page_range = (marker.page_number, next_page - 1)
        sections.append(
            _Section(
                number=marker.number,
                page_range=page_range,
                text=_text_for_range(ocr, page_range),
            )
        )
    return sections


def _find_markers(ocr: OCRResult) -> list[_Marker]:
    markers: list[_Marker] = []
    pages_with_marker: set[int] = set()
    ordinal = 0
    for page in sorted(ocr.pages, key=lambda item: item.page_number):
        for block in page.blocks:
            for line in block.text.splitlines():
                match = _MARKER_RE.match(line)
                if match is None or page.page_number in pages_with_marker:
                    continue
                number_text = next(value for value in match.groupdict().values() if value is not None)
                markers.append(_Marker(number=int(number_text), page_number=page.page_number, ordinal=ordinal))
                pages_with_marker.add(page.page_number)
                ordinal += 1
    return sorted(markers, key=lambda marker: (marker.page_number, marker.ordinal))


def _text_for_range(ocr: OCRResult, page_range: tuple[int, int]) -> str:
    start, end = page_range
    lines: list[str] = []
    for page in sorted(ocr.pages, key=lambda item: item.page_number):
        if start <= page.page_number <= end:
            lines.extend(block.text for block in page.blocks if block.text.strip())
    return "\n".join(lines)


def _total_pages(ocr: OCRResult) -> int:
    return max((page.page_number for page in ocr.pages), default=0)
