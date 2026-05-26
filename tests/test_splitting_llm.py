from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from cpho_cli.core.splitting.llm import SplitLLMError, load_split_prompt_version, split_paper_with_llm
from cpho_cli.models.config import ModelParams
from cpho_cli.models.documents import PaperFile, PaperKind, SplitMethod
from cpho_cli.models.llm import LLMResponse, LLMUsage
from cpho_cli.models.ocr import OCRResult


class FakeSplitProvider:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        messages: list[dict[str, str]],
        params: ModelParams,
        response_model: type[Any] | None = None,
    ) -> LLMResponse:
        self.calls.append(
            {
                "messages": messages,
                "params": params,
                "response_model": response_model,
            }
        )
        return LLMResponse(content=self.content, usage=LLMUsage())


def _ocr(text: str, page_number: int = 1) -> OCRResult:
    return OCRResult.model_validate(
        {
            "pages": [
                {
                    "page_number": page_number,
                    "blocks": [{"text": text, "page_number": page_number}],
                }
            ]
        }
    )


def _paper(path: str = "paper.pdf", pages: int = 1) -> PaperFile:
    return PaperFile(path=Path(path), paper_kind=PaperKind.PROBLEM, total_pages=pages)


def _answer(path: str = "answers.pdf", pages: int = 1) -> PaperFile:
    return PaperFile(path=Path(path), paper_kind=PaperKind.ANSWER, total_pages=pages)


def test_load_split_prompt_version_reads_manifest() -> None:
    assert load_split_prompt_version() == "v1"


def test_splitting_prompt_files_are_in_package_data() -> None:
    text = Path("pyproject.toml").read_text(encoding="utf-8")

    assert "core/splitting/prompts/*" in text


def test_split_paper_with_llm_calls_provider_with_response_model() -> None:
    fake = FakeSplitProvider(
        """
        {
          "problems": [
            {
              "problem_number": 1,
              "problem_page_range": [1, 1],
              "problem_text": "第1题 mechanics",
              "answer_number": 1,
              "answer_page_range": [1, 1],
              "answer_text": "答案1",
              "confidence": 0.82
            }
          ],
          "unmatched_answers": [],
          "diagnostics": []
        }
        """
    )

    outcome = split_paper_with_llm(
        _ocr("第1题 mechanics"),
        _ocr("答案1"),
        paper_file=_paper(),
        answer_file=_answer(),
        paper_sha256="paper-sha",
        provider=fake,
        params=ModelParams(name="test-model", temperature=0.0),
    )

    assert fake.calls[0]["response_model"] is not None
    assert fake.calls[0]["response_model"].__name__ == "_LLMSplitResponse"
    assert outcome.split_method is SplitMethod.LLM
    assert outcome.problems[0].problem_id == "paper-sha:01"
    assert outcome.problems[0].problem_page_range == (1, 1)
    assert outcome.problems[0].answer_page_range == (1, 1)
    assert outcome.problems[0].split_confidence == 0.82


def test_split_paper_with_llm_rejects_malformed_model_output() -> None:
    fake = FakeSplitProvider('{"problems": [{"problem_number": 1}]}')

    with pytest.raises(SplitLLMError):
        split_paper_with_llm(
            _ocr("第1题 mechanics"),
            paper_file=_paper(),
            paper_sha256="paper-sha",
            provider=fake,
            params=ModelParams(name="test-model"),
        )
