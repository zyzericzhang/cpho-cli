from __future__ import annotations

from pathlib import Path
from typing import Any

import jinja2
import yaml
from pydantic import Field, ValidationError

from cpho_cli.core.llm import LLMProvider
from cpho_cli.models.config import ModelParams, StrictModel
from cpho_cli.models.documents import (
    PaperFile,
    ProblemEntry,
    SplitMethod,
    SplitOutcome,
    make_problem_id,
)
from cpho_cli.models.llm import LLMResponse
from cpho_cli.models.ocr import OCRResult


SYSTEM_PROMPT = (
    "你是物理竞赛试卷切分助手。只根据用户提供的 OCR 页文本输出结构化 JSON，"
    "不要补充 OCR 中不存在的题号或页码。"
)


class SplitLLMError(ValueError):
    """Raised when the LLM split response cannot be validated."""


class _LLMProblem(StrictModel):
    problem_number: int = Field(gt=0)
    problem_page_range: tuple[int, int]
    problem_text: str
    answer_number: int | None = Field(default=None, gt=0)
    answer_page_range: tuple[int, int] | None = None
    answer_text: str | None = None
    confidence: float = Field(ge=0, le=1)


class _LLMAnswer(StrictModel):
    answer_number: int = Field(gt=0)
    answer_page_range: tuple[int, int]
    answer_text: str
    confidence: float = Field(ge=0, le=1)


class _LLMSplitResponse(StrictModel):
    problems: list[_LLMProblem]
    unmatched_answers: list[_LLMAnswer] = Field(default_factory=list)
    diagnostics: list[str] = Field(default_factory=list)


def _prompts_dir() -> Path:
    return Path(__file__).parent / "prompts"


def load_split_prompt_version() -> str:
    data = yaml.safe_load((_prompts_dir() / "MANIFEST.yml").read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SplitLLMError("Split prompt manifest must be a YAML mapping.")
    version = data.get("split_prompt_version")
    if not isinstance(version, str):
        raise SplitLLMError("Split prompt manifest is missing split_prompt_version.")
    return version


def _build_jinja_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(_prompts_dir())),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )


def _ocr_pages(ocr: OCRResult | None) -> list[dict[str, Any]]:
    if ocr is None:
        return []
    return [
        {
            "page_number": page.page_number,
            "text": "\n".join(block.text for block in page.blocks if block.text.strip()),
        }
        for page in sorted(ocr.pages, key=lambda item: item.page_number)
    ]


def _render_prompt(
    paper_ocr: OCRResult,
    answer_ocr: OCRResult | None,
    *,
    paper_file: PaperFile,
    answer_file: PaperFile | None,
    paper_sha256: str,
    split_prompt_version: str,
) -> str:
    template = _build_jinja_env().get_template("split_paper.md.j2")
    return template.render(
        split_prompt_version=split_prompt_version,
        paper_file=str(paper_file.path),
        answer_file=str(answer_file.path) if answer_file is not None else None,
        paper_sha256=paper_sha256,
        paper_total_pages=paper_file.total_pages,
        answer_total_pages=answer_file.total_pages if answer_file is not None else None,
        paper_pages=_ocr_pages(paper_ocr),
        answer_pages=_ocr_pages(answer_ocr),
    )


def _parse_response(response: LLMResponse) -> _LLMSplitResponse:
    try:
        return _LLMSplitResponse.model_validate_json(response.content)
    except ValidationError as exc:
        raise SplitLLMError("LLM split response did not match the split schema.") from exc


def _problem_entry(
    problem: _LLMProblem,
    *,
    paper_file: PaperFile,
    answer_file: PaperFile | None,
    paper_sha256: str,
) -> ProblemEntry:
    has_answer = problem.answer_page_range is not None or problem.answer_text is not None
    return ProblemEntry(
        problem_id=make_problem_id(paper_sha256, problem.problem_number),
        paper_path=paper_file.path,
        problem_number=problem.problem_number,
        problem_page_range=problem.problem_page_range,
        problem_text=problem.problem_text,
        answer_paper_path=answer_file.path if has_answer and answer_file is not None else None,
        answer_page_range=problem.answer_page_range,
        answer_text=problem.answer_text,
        split_method=SplitMethod.LLM,
        split_confidence=problem.confidence,
    )


def _unmatched_answer_entry(answer: _LLMAnswer, answer_file: PaperFile | None) -> ProblemEntry:
    answer_path = answer_file.path if answer_file is not None else Path("<missing-answer-file>")
    return ProblemEntry(
        problem_id=f"unmatched-answer:{answer.answer_number:02d}",
        paper_path=answer_path,
        problem_number=answer.answer_number,
        problem_page_range=answer.answer_page_range,
        problem_text=answer.answer_text,
        split_method=SplitMethod.LLM,
        split_confidence=answer.confidence,
    )


def split_paper_with_llm(
    paper_ocr: OCRResult,
    answer_ocr: OCRResult | None = None,
    *,
    paper_file: PaperFile,
    answer_file: PaperFile | None = None,
    paper_sha256: str,
    provider: LLMProvider,
    params: ModelParams,
) -> SplitOutcome:
    split_prompt_version = load_split_prompt_version()
    user_prompt = _render_prompt(
        paper_ocr,
        answer_ocr,
        paper_file=paper_file,
        answer_file=answer_file,
        paper_sha256=paper_sha256,
        split_prompt_version=split_prompt_version,
    )
    response = provider.complete(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        params,
        response_model=_LLMSplitResponse,
    )
    split_response = _parse_response(response)
    problems = [
        _problem_entry(
            problem,
            paper_file=paper_file,
            answer_file=answer_file,
            paper_sha256=paper_sha256,
        )
        for problem in split_response.problems
    ]
    confidences = [problem.split_confidence for problem in problems]
    unmatched_answers = [
        _unmatched_answer_entry(answer, answer_file)
        for answer in split_response.unmatched_answers
    ]
    return SplitOutcome(
        problems=problems,
        unmatched_answers=unmatched_answers,
        split_method=SplitMethod.LLM,
        split_confidence=min(confidences) if confidences else 0.0,
        diagnostics=split_response.diagnostics,
    )
