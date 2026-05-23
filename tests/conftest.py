"""Shared fakes for index builder tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cpho_cli.core.index.tagging import TagRefinementOutput
from cpho_cli.core.llm import LLMProvider
from cpho_cli.core.ocr import OCRProvider
from cpho_cli.models.config import ModelParams
from cpho_cli.models.documents import DocumentInput, DocumentPage
from cpho_cli.models.llm import LLMResponse, LLMUsage
from cpho_cli.models.ocr import OCRBlock, OCRPageResult, OCRResult


class FakeOCRProvider:
    """Returns file content as OCR text (reads problem file as UTF-8 fallback to repr)."""

    def __init__(self, default_text: str = "fake ocr text") -> None:
        self.default_text = default_text
        self.calls = 0

    def extract(self, document: DocumentInput) -> OCRResult:
        self.calls += 1
        try:
            text = document.path.read_bytes().decode("utf-8", errors="replace")
        except Exception:
            text = self.default_text
        return OCRResult(
            pages=[
                OCRPageResult(
                    page_number=1,
                    blocks=[OCRBlock(text=text, page_number=1, confidence=1.0)],
                )
            ]
        )


class FakeLLMProvider:
    """Returns a fixed TagRefinementOutput JSON or a per-problem mapping."""

    def __init__(
        self,
        fixed_output: TagRefinementOutput | None = None,
        per_problem: dict[str, TagRefinementOutput] | None = None,
    ) -> None:
        self.fixed_output = fixed_output or TagRefinementOutput(
            selected_physics_models=["energy_conservation"],
            selected_math_techniques=["dimensional_analysis"],
            selected_heuristics=["free_body_diagram"],
            difficulty_aspects=["受力分析"],
        )
        self.per_problem = per_problem or {}
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        messages: list[dict[str, str]],
        params: ModelParams,
        response_model: type[Any] | None = None,
    ) -> LLMResponse:
        self.calls.append({"messages": messages, "params": params})
        # Try to detect problem_id from user message content
        user_content = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
                break

        output = self.fixed_output
        for pid, out in self.per_problem.items():
            if pid in user_content:
                output = out
                break

        return LLMResponse(
            content=output.model_dump_json(),
            usage=LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            raw={},
        )


def setup_workspace(
    tmp_path: Path,
    problem_names: list[str] | None = None,
    with_answers: bool = True,
    with_config: bool = True,
) -> Path:
    """Create a minimal workspace with PNG problem/answer files."""
    if problem_names is None:
        problem_names = ["p1", "p2"]

    for name in problem_names:
        (tmp_path / f"{name}.png").write_bytes(
            b"\x89PNG\r\n\x1a\n" + name.encode() + b"\x00" * 50
        )
        if with_answers:
            answer_dir = tmp_path / "answers"
            answer_dir.mkdir(exist_ok=True)
            (answer_dir / f"{name}-answer.png").write_bytes(
                b"\x89PNG\r\n\x1a\n" + f"{name}_ans".encode() + b"\x00" * 50
            )

    if with_config:
        (tmp_path / "config.local.yml").write_text(
            "provider:\n  openrouter_api_key: test-key-fake\n",
            encoding="utf-8",
        )

    return tmp_path
