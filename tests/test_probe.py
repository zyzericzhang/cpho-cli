from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.core.probe import finalize_probe_markdown, run_probe, write_probe_header
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import LLMResponse
from cpho_cli.models.probe import ProbeTranscript, ProbeTurn
from cpho_cli.models.solve import Discrepancy, SolveReport


class FakeProbeProvider:
    def __init__(self, questions: list[str]) -> None:
        self.questions = questions
        self.messages: list[str] = []

    def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
        self.messages.append(str(messages[-1]["content"]))
        index = len(self.messages) - 1
        return LLMResponse(content=self.questions[index])


class PromptScript:
    def __init__(self, answers: list[str]) -> None:
        self.answers = answers
        self.prompts: list[str] = []

    async def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.answers.pop(0)


@pytest.mark.asyncio
async def test_probe_appends_turns_and_finalizes_questions_before_answers(
    tmp_path: Path,
) -> None:
    provider = FakeProbeProvider(["先判断研究对象是什么？", "为什么动量守恒？"])
    prompt = PromptScript(["小球和斜面", "/exit"])

    result = await run_probe(
        provider=provider,
        params=ModelParams(name="fake"),
        problem_text="第四届芝麻物理联考 (复赛) 理论试题",
        problem_name="第四届芝麻物理联考 (复赛) 理论试题",
        workspace_path=tmp_path,
        prompt=prompt,
        max_rounds=10,
        output_dir=tmp_path,
    )

    assert result.turns == [ProbeTurn(question="先判断研究对象是什么？", answer="小球和斜面")]
    markdown = result.markdown_path.read_text(encoding="utf-8")
    assert "## 问题" in markdown
    assert "## 解答" in markdown
    assert markdown.index("## 问题") < markdown.index("## 解答")
    assert "1. 先判断研究对象是什么？" in markdown
    assert "1. 小球和斜面" in markdown
    assert "为什么动量守恒？" not in markdown
    assert any("第四届芝麻物理联考" in message for message in provider.messages)


@pytest.mark.asyncio
async def test_probe_exits_on_two_empty_answers(tmp_path: Path) -> None:
    provider = FakeProbeProvider(["这一步用了什么近似？"])
    prompt = PromptScript(["", ""])

    result = await run_probe(
        provider=provider,
        params=ModelParams(name="fake"),
        problem_text="题目",
        problem_name="题目",
        workspace_path=tmp_path,
        prompt=prompt,
        max_rounds=10,
        output_dir=tmp_path,
    )

    assert result.turns == []
    assert len(provider.messages) == 1
    assert prompt.prompts == [
        "这一步用了什么近似？\ncpho:probe> ",
        "这一步用了什么近似？\ncpho:probe> ",
    ]


@pytest.mark.asyncio
async def test_probe_soft_limit_prompts_before_continuing(tmp_path: Path) -> None:
    provider = FakeProbeProvider(["第一问？", "第二问？"])
    prompt = PromptScript(["第一答", "y", "第二答", "/exit"])

    result = await run_probe(
        provider=provider,
        params=ModelParams(name="fake"),
        problem_text="题目",
        problem_name="题目",
        workspace_path=tmp_path,
        prompt=prompt,
        max_rounds=1,
        output_dir=tmp_path,
    )

    assert [turn.answer for turn in result.turns] == ["第一答", "第二答"]
    assert any("已达最大轮次" in item for item in prompt.prompts)
    assert len(provider.messages) == 2


@pytest.mark.asyncio
async def test_probe_injects_solve_context(tmp_path: Path) -> None:
    provider = FakeProbeProvider(["先找出符号问题会影响哪一步？"])
    prompt = PromptScript(["/exit"])
    report = SolveReport(
        problem_id="p1",
        discrepancies=[
            Discrepancy(
                description="答案第 2 行符号可能错误",
                likely_source="sign error",
                official_answer_refs=["answer:2"],
            )
        ],
    )

    await run_probe(
        provider=provider,
        params=ModelParams(name="fake"),
        problem_text="题目",
        problem_name="题目",
        workspace_path=tmp_path,
        prompt=prompt,
        max_rounds=10,
        solve_report=report,
        output_dir=tmp_path,
    )

    assert any("答案第 2 行符号可能错误" in message for message in provider.messages)


def test_probe_incremental_markdown_is_recoverable_before_final_rewrite(
    tmp_path: Path,
) -> None:
    path = tmp_path / "probe.md"
    transcript = ProbeTranscript(problem_name="芝士研学自命题50例", markdown_path=path)
    write_probe_header(path, transcript.problem_name)
    transcript.turns.append(ProbeTurn(question="关键受力是什么？", answer="重力和支持力"))

    from cpho_cli.core.probe import append_probe_turn

    append_probe_turn(path, transcript.turns[0], 1)
    text = path.read_text(encoding="utf-8")
    assert "## Incremental Transcript" in text
    assert "**Q:** 关键受力是什么？" in text
    assert "**A:** 重力和支持力" in text

    finalize_probe_markdown(transcript)
    final = path.read_text(encoding="utf-8")
    assert "## Incremental Transcript" not in final
    assert final.index("## 问题") < final.index("## 解答")
