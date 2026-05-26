from __future__ import annotations

import json
from pathlib import Path

import pytest

from cpho_cli.core.explain import run_explain
from cpho_cli.models.config import ModelParams
from cpho_cli.models.explain import ExplainTone
from cpho_cli.models.llm import LLMResponse
from cpho_cli.models.solve import Discrepancy, SolveReport


class FakeExplainProvider:
    def __init__(self) -> None:
        self.stream_messages: list[str] = []
        self.complete_messages: list[str] = []

    def stream(self, messages, params: ModelParams):  # type: ignore[no-untyped-def]
        content = str(messages[-1]["content"])
        self.stream_messages.append(content)
        if "teacher" in content and "sentence" not in content:
            yield "老师型物理图像"
            yield "老师型逐步讲解"
        elif "dense" in content and "sentence" not in content:
            yield "密集型物理图像"
            yield "密集型详细推导"
        elif "teacher" in content:
            yield "老师型句子级 explain"
        else:
            yield "密集型句子级 explain"

    def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
        self.complete_messages.append(str(messages[-1]["content"]))
        return LLMResponse(content=json.dumps({"candidate_tags": ["牛顿定律", "符号检查"]}))


@pytest.mark.asyncio
async def test_run_explain_streams_each_tone_and_merges_markdown(tmp_path: Path) -> None:
    provider = FakeExplainProvider()
    chunks: list[tuple[str, str]] = []
    solve_report = SolveReport(
        problem_id="p1",
        discrepancies=[
            Discrepancy(
                description="符号可能错误",
                likely_source="sign error",
                official_answer_refs=["answer:1"],
            )
        ],
    )

    result = await run_explain(
        provider=provider,
        params=ModelParams(name="fake"),
        problem_text="题目",
        answer_text="答案",
        problem_name="力学2试题",
        workspace_path=tmp_path,
        tones=[ExplainTone.TEACHER, ExplainTone.DENSE],
        solve_report=solve_report,
        on_chunk=lambda chunk: chunks.append((chunk.tone.value, chunk.text)),
    )

    assert ("teacher", "老师型物理图像") in chunks
    assert ("dense", "密集型物理图像") in chunks
    assert result.markdown_path.exists()
    markdown = result.markdown_path.read_text(encoding="utf-8")
    assert "## Tone: 老师型" in markdown
    assert "## Tone: 知识点密集型" in markdown
    assert "整道题物理图像与思路" in markdown
    assert "原答案逐步讲解" in markdown
    assert "超越原答案的更清晰推导" in markdown
    assert "句子级 explain" in markdown
    assert result.candidate_tags == ["牛顿定律", "符号检查"]
    assert any("符号可能错误" in message for message in provider.stream_messages)
    assert len(provider.stream_messages) == 4


@pytest.mark.asyncio
async def test_run_explain_without_solve_report_uses_explicit_empty_context(
    tmp_path: Path,
) -> None:
    provider = FakeExplainProvider()

    await run_explain(
        provider=provider,
        params=ModelParams(name="fake"),
        problem_text="题目",
        answer_text="答案",
        problem_name="电学1试题",
        workspace_path=tmp_path,
        tones=[ExplainTone.BRIEF],
        solve_report=None,
    )

    assert provider.stream_messages
    assert all("无已确认 Solve 审查结果" in message for message in provider.stream_messages)
