"""Shared helpers for REPL skill commands."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands.workspace import INDEX_MISSING_MSG
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.config import resolve_model_params, resolve_provider_config
from cpho_cli.core.index import IndexNotFoundError, ProblemNotIndexedError, get_problem_entry
from cpho_cli.core.llm import create_llm_provider
from cpho_cli.models.index import IndexEntry


async def prompt_user(session: SessionState, prompt: str) -> str:
    prompt_session = session.prompt_session
    prompt_async = getattr(prompt_session, "prompt_async", None)
    if prompt_async is None:
        return ""
    return await prompt_async(prompt)


def provider_and_params(session: SessionState, skill_name: str) -> tuple[Any, Any]:
    provider_config = resolve_provider_config(session.config, os.environ, session.provider_name)
    provider = create_llm_provider(
        kind=provider_config.kind,
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
        timeout=provider_config.timeout,
    )
    params = resolve_model_params(
        session.config,
        skill_name,
        provider_name=session.provider_name,
    )
    return provider, params


def resolve_problem(session: SessionState, problem_id: str | None) -> IndexEntry | None:
    resolved_id = problem_id or session.current_problem_id
    if resolved_id is None:
        display.error("请先 /show <problem_id>，或在命令后指定 problem_id。")
        return None
    try:
        entry = get_problem_entry(session.workspace_path, resolved_id)
    except (IndexNotFoundError, ProblemNotIndexedError):
        display.error(INDEX_MISSING_MSG.format(workspace=session.workspace_path))
        return None
    if entry is None:
        display.error(f"未找到题目: {resolved_id}")
        return None
    session.current_problem_id = entry.problem_id
    return entry


def resolve_workspace_path(session: SessionState, path: Path | None) -> Path | None:
    if path is None:
        return None
    return path if path.is_absolute() else session.workspace_path / path


def problem_text(session: SessionState, entry: IndexEntry) -> str:
    if entry.ocr_cache_path is not None:
        path = resolve_workspace_path(session, entry.ocr_cache_path)
        if path is not None and path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    return f"{entry.problem_id}\n来源: {entry.problem_path}"


def answer_text(session: SessionState, entry: IndexEntry) -> str:
    path = resolve_workspace_path(session, entry.answer_path)
    if path is None:
        return "无答案文件。"
    if path.suffix.lower() in {".txt", ".md"} and path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return f"答案来源: {entry.answer_path}"


async def confirm_strings(
    session: SessionState,
    items: list[str],
    *,
    allow_append: bool,
) -> list[str]:
    confirmed: list[str] = []
    for item in items:
        while True:
            answer = (await prompt_user(session, f"确认 `{item}`？[Y/n/e] ")).strip()
            if not answer or answer.lower() == "y":
                confirmed.append(item)
                break
            if answer.lower() == "n":
                break
            if answer.lower() == "e":
                edited = (await prompt_user(session, "编辑为: ")).strip()
                if edited:
                    confirmed.append(edited)
                break
            display.warn("请输入 y/n/e。")
    if allow_append:
        while True:
            extra = (await prompt_user(session, "追加标签（+tag，空行结束）: ")).strip()
            if not extra:
                break
            if extra.startswith("+"):
                tag = extra[1:].strip()
                if tag:
                    confirmed.append(tag)
    return confirmed


async def offer_followup(session: SessionState) -> bool:
    answer = (await prompt_user(session, "→ 进入 Follow-up？(`/followup` 或 Enter 跳过) ")).strip()
    return answer == "/followup"


__all__ = [
    "confirm_strings",
    "answer_text",
    "offer_followup",
    "problem_text",
    "prompt_user",
    "provider_and_params",
    "resolve_problem",
    "resolve_workspace_path",
]
