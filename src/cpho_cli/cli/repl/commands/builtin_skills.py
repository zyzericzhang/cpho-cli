"""REPL commands for built-in Phase 3 skills."""

from __future__ import annotations

import argparse
from pathlib import Path

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.adapters.skill_command import (
    answer_text,
    confirm_strings,
    offer_followup,
    problem_text,
    prompt_user,
    provider_and_params,
    resolve_problem,
    resolve_workspace_path,
)
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.explain import run_explain
from cpho_cli.core.index.api import add_problem_tags
from cpho_cli.core.probe import run_probe
from cpho_cli.core.solve import solve_problem
from cpho_cli.models.explain import ExplainTone
from cpho_cli.models.solve import SolveReport


def _solve_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="/solve", add_help=False)
    parser.add_argument("problem_id", nargs="?")
    parser.add_argument("--auto-confirm", action="store_true")
    parser.add_argument("--persist-tags", action="store_true")
    return parser


def _explain_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="/explain", add_help=False)
    parser.add_argument("problem_id", nargs="?")
    parser.add_argument("--tone", action="append", choices=[tone.value for tone in ExplainTone])
    return parser


def _probe_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="/probe", add_help=False)
    parser.add_argument("problem_id", nargs="?")
    return parser


async def do_solve(session: SessionState, args: list[str]) -> None:
    try:
        ns = _solve_parser().parse_args(args)
    except SystemExit:
        display.error("用法: /solve [problem_id] [--auto-confirm] [--persist-tags]")
        return
    entry = resolve_problem(session, ns.problem_id)
    if entry is None:
        return
    problem_path = resolve_workspace_path(session, entry.problem_path)
    answer_path = resolve_workspace_path(session, entry.answer_path)
    if problem_path is None or answer_path is None:
        display.error("当前索引题目缺少题目或答案文件路径。")
        return
    print("▶ solve: reviewing official answer...")
    result = solve_problem(
        problem_path=problem_path,
        answer_path=answer_path,
        config_path=session.config_path,
        provider_name=session.provider_name,
        output_dir=session.out_dir or Path("output"),
        show_progress=True,
    )
    if result.report is None:
        display.error("Solve 未返回报告。")
        return
    report = result.report
    if not ns.auto_confirm:
        report = await _confirm_solve_report(session, report)
    session.current_solve_report = report
    if ns.persist_tags and report.discrepancies:
        tags = [item.description for item in report.discrepancies]
        add_problem_tags(
            session.workspace_path,
            entry.problem_id,
            tags,
            skill_name="solve",
            reasoning="REPL Solve confirmed discrepancies.",
        )
    print(f"✓ solve: {result.report_markdown or 'done'}")
    await offer_followup(session)


async def _confirm_solve_report(session: SessionState, report: SolveReport) -> SolveReport:
    descriptions = [item.description for item in report.discrepancies]
    confirmed = await confirm_strings(session, descriptions, allow_append=False)
    keep = set(confirmed)
    return report.model_copy(
        update={
            "discrepancies": [item for item in report.discrepancies if item.description in keep]
        }
    )


async def do_explain(session: SessionState, args: list[str]) -> None:
    try:
        ns = _explain_parser().parse_args(args)
    except SystemExit:
        display.error("用法: /explain [problem_id] [--tone teacher|dense|brief]")
        return
    entry = resolve_problem(session, ns.problem_id)
    if entry is None:
        return
    if session.current_solve_report is None:
        display.warn("尚未运行 /solve；Explain 将使用未校正的原答案上下文。")
    provider, params = provider_and_params(session, "explain")
    tones = [ExplainTone(value) for value in (ns.tone or [ExplainTone.TEACHER.value])]
    print("▶ explain: generating...")
    result = await run_explain(
        provider=provider,
        params=params,
        problem_text=problem_text(session, entry),
        answer_text=answer_text(session, entry),
        problem_name=entry.problem_id,
        workspace_path=session.workspace_path,
        tones=tones,
        solve_report=session.current_solve_report,
        output_dir=session.out_dir,
    )
    confirmed_tags = await confirm_strings(session, result.candidate_tags, allow_append=True)
    if confirmed_tags:
        add_problem_tags(
            session.workspace_path,
            entry.problem_id,
            confirmed_tags,
            skill_name="explain",
            reasoning="REPL Explain confirmed candidate tags.",
        )
    print(f"✓ explain: {result.markdown_path}")
    print("→ 进入 Probe 模式？(`/probe` 或 Enter 跳过)")
    probe_answer = (await prompt_user(session, "")).strip()
    if probe_answer == "/probe":
        await do_probe(session, [entry.problem_id])
    await offer_followup(session)


async def do_probe(session: SessionState, args: list[str]) -> None:
    try:
        ns = _probe_parser().parse_args(args)
    except SystemExit:
        display.error("用法: /probe [problem_id]")
        return
    entry = resolve_problem(session, ns.problem_id)
    if entry is None:
        return
    if session.current_solve_report is None:
        display.warn("尚未运行 /solve；Probe 将使用未校正的原答案上下文。")
    provider, params = provider_and_params(session, "probe")
    print("▶ probe: starting...")
    result = await run_probe(
        provider=provider,
        params=params,
        problem_text=problem_text(session, entry),
        problem_name=entry.problem_id,
        workspace_path=session.workspace_path,
        prompt=lambda prompt: prompt_user(session, prompt),
        max_rounds=session.probe_max_rounds,
        solve_report=session.current_solve_report,
        output_dir=session.out_dir,
    )
    print(f"✓ probe: {result.markdown_path}")
    await offer_followup(session)


def register(registry: dict[str, Command]) -> None:
    registry["/solve"] = Command(
        name="/solve",
        help="审查当前题目标答",
        usage="/solve [problem_id] [--auto-confirm] [--persist-tags]",
        handler=do_solve,
        category="技能",
    )
    registry["/explain"] = Command(
        name="/explain",
        help="讲解当前题目",
        usage="/explain [problem_id] [--tone teacher|dense|brief]",
        handler=do_explain,
        category="技能",
    )
    registry["/probe"] = Command(
        name="/probe",
        help="主动追问题目关键点",
        usage="/probe [problem_id]",
        handler=do_probe,
        category="技能",
    )


__all__ = [
    "add_problem_tags",
    "do_explain",
    "do_probe",
    "do_solve",
    "provider_and_params",
    "register",
    "run_explain",
    "run_probe",
    "solve_problem",
]
