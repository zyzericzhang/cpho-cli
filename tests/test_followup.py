from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.core.followup import run_followup
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import LLMResponse


class FakeProvider:
    def __init__(self) -> None:
        self.messages = []

    def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
        self.messages.append(messages)
        return LLMResponse(content="follow-up answer")


class Prompt:
    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.prompts: list[str] = []

    async def __call__(self, prompt_text: str) -> str:
        self.prompts.append(prompt_text)
        return self.lines.pop(0)


@pytest.mark.asyncio
async def test_followup_exits_on_exit_and_appends_transcript(tmp_path: Path) -> None:
    provider = FakeProvider()
    export_path = tmp_path / "skill.md"
    export_path.write_text("# Skill\n", encoding="utf-8")
    prompt = Prompt(["为什么这样做？", "/exit"])

    turns = await run_followup(
        prompt=prompt,
        provider=provider,
        params=ModelParams(name="fake"),
        skill_context_markdown="context",
        export_path=export_path,
    )

    assert len(turns) == 1
    assert provider.messages[0][0]["content"] == "context"
    assert prompt.prompts == ["cpho:followup> ", "cpho:followup> "]
    text = export_path.read_text(encoding="utf-8")
    assert "## Follow-up" in text
    assert "为什么这样做？" in text
    assert "follow-up answer" in text


@pytest.mark.asyncio
async def test_followup_exits_on_two_empty_lines() -> None:
    provider = FakeProvider()

    turns = await run_followup(
        prompt=Prompt(["", ""]),
        provider=provider,
        params=ModelParams(name="fake"),
        skill_context_markdown="context",
    )

    assert turns == []
    assert provider.messages == []
