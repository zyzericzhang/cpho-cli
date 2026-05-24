from __future__ import annotations

import json
from pathlib import Path

from cpho_cli.core.splitting import split_paper
from cpho_cli.models.documents import PaperFile, PaperKind, SplitMethod
from cpho_cli.models.ocr import OCRResult


def _fixture_ocr() -> OCRResult:
    data = json.loads(Path("tests/fixtures/paper_with_5_problems.json").read_text(encoding="utf-8"))
    return OCRResult.model_validate(data)


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
