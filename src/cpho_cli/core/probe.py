from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import jinja2

from cpho_cli.core.skill_outputs import (
    append_markdown,
    default_markdown_path,
    write_markdown_atomic,
)
from cpho_cli.models.config import ModelParams
from cpho_cli.models.probe import ProbeTranscript, ProbeTurn
from cpho_cli.models.solve import SolveReport

PromptFunc = Callable[[str], Awaitable[str]]


def _builtin_probe_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "builtin_skills" / "probe"


async def run_probe(
    *,
    provider,
    params: ModelParams,
    problem_text: str,
    problem_name: str,
    workspace_path: Path,
    prompt: PromptFunc,
    max_rounds: int,
    solve_report: SolveReport | None = None,
    output_dir: Path | None = None,
) -> ProbeTranscript:
    markdown_path = default_markdown_path(
        workspace_path,
        "probe",
        f"{problem_name}.probe",
        override_dir=output_dir,
    )
    transcript = ProbeTranscript(problem_name=problem_name, markdown_path=markdown_path)
    write_probe_header(markdown_path, problem_name)
    empty_count = 0
    latest_user_response = ""

    while True:
        if transcript.turns and len(transcript.turns) >= max_rounds:
            should_continue = (await prompt("已达最大轮次，是否继续？[y/N] ")).strip().lower()
            if should_continue not in {"y", "yes", "是", "继续"}:
                break

        question = _next_question(
            provider=provider,
            params=params,
            problem_text=problem_text,
            solve_context=_solve_context(solve_report),
            turns=transcript.turns,
            latest_user_response=latest_user_response,
        )

        while True:
            answer = (await prompt(f"{question}\ncpho:probe> ")).strip()
            if answer == "/exit":
                finalize_probe_markdown(transcript)
                return transcript
            if not answer:
                empty_count += 1
                if empty_count >= 2:
                    finalize_probe_markdown(transcript)
                    return transcript
                continue
            empty_count = 0
            break

        turn = ProbeTurn(question=question, answer=answer)
        transcript.turns.append(turn)
        append_probe_turn(markdown_path, turn, len(transcript.turns))
        latest_user_response = answer

    finalize_probe_markdown(transcript)
    return transcript


def write_probe_header(path: Path, problem_name: str) -> None:
    write_markdown_atomic(path, f"# Probe: {problem_name}\n\n## Incremental Transcript\n")


def append_probe_turn(path: Path, turn: ProbeTurn, index: int) -> None:
    append_markdown(
        path,
        f"\n### Turn {index}\n\n**Q:** {turn.question}\n\n**A:** {turn.answer}\n",
    )


def finalize_probe_markdown(transcript: ProbeTranscript) -> None:
    lines = [f"# Probe: {transcript.problem_name}", "", "## 问题", ""]
    if transcript.turns:
        for index, turn in enumerate(transcript.turns, start=1):
            lines.append(f"{index}. {turn.question}")
    else:
        lines.append("无已完成问题。")
    lines.extend(["", "## 解答", ""])
    if transcript.turns:
        for index, turn in enumerate(transcript.turns, start=1):
            lines.append(f"{index}. {turn.answer}")
    else:
        lines.append("无已完成解答。")
    write_markdown_atomic(transcript.markdown_path, "\n".join(lines) + "\n")


def _next_question(
    *,
    provider,
    params: ModelParams,
    problem_text: str,
    solve_context: str,
    turns: list[ProbeTurn],
    latest_user_response: str,
) -> str:
    prompt = _render_prompt(
        "next_turn.md.j2",
        problem_text=problem_text,
        solve_context=solve_context,
        previous_turns=_format_turns(turns),
        latest_user_response=latest_user_response or "无",
    )
    response = provider.complete([{"role": "user", "content": prompt}], params)
    return response.content.strip()


def _format_turns(turns: list[ProbeTurn]) -> str:
    if not turns:
        return "无"
    return "\n".join(
        f"{index}. Q: {turn.question}\n   A: {turn.answer}"
        for index, turn in enumerate(turns, start=1)
    )


def _render_prompt(template_name: str, **values: Any) -> str:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(_builtin_probe_skill_dir() / "prompts")),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )
    return env.get_template(template_name).render(**values)


def _solve_context(report: SolveReport | None) -> str:
    if report is None:
        return "无已确认 Solve 审查结果。"
    if not report.discrepancies:
        return "Solve 审查未发现需修正的差异。"
    lines = ["已确认 Solve 审查结果:"]
    for item in report.discrepancies:
        refs = ", ".join(item.official_answer_refs) or "无引用"
        lines.append(f"- {item.description} [{refs}]")
    return "\n".join(lines)


__all__ = [
    "append_probe_turn",
    "finalize_probe_markdown",
    "run_probe",
    "write_probe_header",
]
