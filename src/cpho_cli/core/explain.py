from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import jinja2

from cpho_cli.core.skill_outputs import default_markdown_path, write_markdown_atomic
from cpho_cli.models.config import ModelParams
from cpho_cli.models.explain import (
    ExplainResult,
    ExplainStreamChunk,
    ExplainTone,
    ToneExplainOutput,
)
from cpho_cli.models.solve import SolveReport


def _builtin_explain_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "builtin_skills" / "explain"


async def run_explain(
    *,
    provider,
    params: ModelParams,
    problem_text: str,
    answer_text: str,
    problem_name: str,
    workspace_path: Path,
    tones: list[ExplainTone],
    solve_report: SolveReport | None = None,
    output_dir: Path | None = None,
    on_chunk: Callable[[ExplainStreamChunk], None] | None = None,
) -> ExplainResult:
    outputs = await asyncio.gather(
        *[
            _run_tone(
                provider=provider,
                params=params,
                problem_text=problem_text,
                answer_text=answer_text,
                tone=tone,
                solve_report=solve_report,
                on_chunk=on_chunk,
            )
            for tone in tones
        ]
    )
    candidate_tags = _extract_tags(provider, params, problem_text, answer_text, outputs)
    markdown_path = default_markdown_path(
        workspace_path,
        "explain",
        f"{problem_name}.explain",
        override_dir=output_dir,
    )
    write_markdown_atomic(markdown_path, _merge_markdown(problem_name, outputs))
    return ExplainResult(
        problem_name=problem_name,
        tone_outputs=outputs,
        candidate_tags=candidate_tags,
        markdown_path=markdown_path,
    )


async def _run_tone(
    *,
    provider,
    params: ModelParams,
    problem_text: str,
    answer_text: str,
    tone: ExplainTone,
    solve_report: SolveReport | None,
    on_chunk: Callable[[ExplainStreamChunk], None] | None,
) -> ToneExplainOutput:
    stage_one_prompt = _render_prompt(
        f"{tone.value}_stage1.md.j2",
        tone=tone.value,
        problem_text=problem_text,
        answer_text=answer_text,
        solve_context=_solve_context(solve_report),
    )
    stage_one = _collect_stream(provider, params, stage_one_prompt, tone, "stage1", on_chunk)
    sentence_prompt = _render_prompt(
        f"{tone.value}_sentence.md.j2",
        tone=tone.value,
        problem_text=problem_text,
        answer_text=answer_text,
        stage_one=stage_one,
        solve_context=_solve_context(solve_report),
    )
    sentence = _collect_stream(provider, params, sentence_prompt, tone, "sentence", on_chunk)
    return ToneExplainOutput(
        tone=tone,
        stage_one_markdown=stage_one,
        sentence_markdown=sentence,
    )


def _collect_stream(
    provider,
    params: ModelParams,
    prompt: str,
    tone: ExplainTone,
    stage: str,
    on_chunk: Callable[[ExplainStreamChunk], None] | None,
) -> str:
    chunks: list[str] = []
    for text in provider.stream([{"role": "user", "content": prompt}], params):
        chunks.append(text)
        if on_chunk is not None:
            on_chunk(ExplainStreamChunk(tone=tone, text=text, stage=stage))
    return "".join(chunks)


def _extract_tags(
    provider,
    params: ModelParams,
    problem_text: str,
    answer_text: str,
    outputs: list[ToneExplainOutput],
) -> list[str]:
    prompt = _render_prompt(
        "extract_tags.md.j2",
        problem_text=problem_text,
        answer_text=answer_text,
        explanations="\n\n".join(
            output.stage_one_markdown + "\n" + output.sentence_markdown for output in outputs
        ),
    )
    response = provider.complete([{"role": "user", "content": prompt}], params)
    data: Any = json.loads(response.content)
    tags = data.get("candidate_tags", []) if isinstance(data, dict) else []
    return [str(tag) for tag in tags]


def _render_prompt(template_name: str, **values: Any) -> str:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(_builtin_explain_skill_dir() / "prompts")),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )
    return env.get_template(template_name).render(**values)


def _solve_context(report: SolveReport | None) -> str:
    if report is None:
        return "无已确认 Solve 审查结果。"
    lines = ["已确认 Solve 审查结果:"]
    for item in report.discrepancies:
        refs = ", ".join(item.official_answer_refs) or "无引用"
        lines.append(f"- {item.description} [{refs}]")
    return "\n".join(lines)


def _merge_markdown(problem_name: str, outputs: list[ToneExplainOutput]) -> str:
    lines = [f"# Explain: {problem_name}", ""]
    for output in outputs:
        stage_sections = _split_stage_sections(output.stage_one_markdown)
        lines.extend(
            [
                f"## Tone: {output.tone.display_zh}",
                "",
                "### 整道题物理图像与思路",
                "",
                stage_sections.get("整道题物理图像与思路", output.stage_one_markdown),
                "",
                "### 原答案逐步讲解",
                "",
                stage_sections.get("原答案逐步讲解", ""),
                "",
                "### 超越原答案的更清晰推导",
                "",
                stage_sections.get("超越原答案的更清晰推导", ""),
                "",
                "### 句子级 explain",
                "",
                _strip_heading(output.sentence_markdown, "句子级 explain"),
                "",
            ]
        )
    return "\n".join(lines)


def _split_stage_sections(markdown: str) -> dict[str, str]:
    headings = ["整道题物理图像与思路", "原答案逐步讲解", "超越原答案的更清晰推导"]
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            heading = stripped[4:].strip()
            current = heading if heading in headings else None
            if current is not None:
                sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def _strip_heading(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].strip() == f"### {heading}":
        return "\n".join(lines[1:]).strip()
    return markdown


__all__ = ["run_explain"]
