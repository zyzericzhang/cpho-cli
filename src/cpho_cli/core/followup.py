from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

from cpho_cli.core.skill_outputs import append_markdown
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import ChatMessage


@dataclass(frozen=True)
class FollowupTurn:
    question: str
    answer: str


PromptFunc = Callable[[str], Awaitable[str]]


async def run_followup(
    *,
    prompt: PromptFunc,
    provider,
    params: ModelParams,
    skill_context_markdown: str,
    export_path: Path | None = None,
) -> list[FollowupTurn]:
    messages: list[ChatMessage] = [{"role": "system", "content": skill_context_markdown}]
    turns: list[FollowupTurn] = []
    empty_count = 0
    while True:
        user_text = (await prompt("cpho:followup> ")).strip()
        if user_text == "/exit":
            break
        if not user_text:
            empty_count += 1
            if empty_count >= 2:
                break
            continue
        empty_count = 0
        messages.append({"role": "user", "content": user_text})
        response = provider.complete(messages=messages, params=params)
        answer = response.content
        messages.append({"role": "assistant", "content": answer})
        turn = FollowupTurn(question=user_text, answer=answer)
        turns.append(turn)
        if export_path is not None:
            append_markdown(
                export_path,
                "\n\n## Follow-up\n\n"
                if len(turns) == 1
                else ""
            )
            append_markdown(export_path, f"\n### Q{len(turns)}\n\n{user_text}\n\n{answer}\n")
    return turns


__all__ = ["FollowupTurn", "run_followup"]
