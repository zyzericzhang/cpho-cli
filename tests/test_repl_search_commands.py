from __future__ import annotations

from pathlib import Path

import pytest
from prompt_toolkit.document import Document

from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.commands.search import (
    TagCompleter,
    _TAG_CACHE,
    do_search,
    do_show,
    refresh_tag_cache,
    register,
)
from cpho_cli.cli.repl.session import SessionState, load_index_meta
from cpho_cli.models.config import AppConfig


@pytest.mark.asyncio
async def test_search_missing_index_reports_error(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await do_search(session, ["力学"])

    assert "未找到索引" in capsys.readouterr().out


def test_tag_cache_and_completion(repl_workspace_with_index: tuple[Path, list[str]]) -> None:
    workspace, _ = repl_workspace_with_index
    session = SessionState(workspace_path=workspace, config=AppConfig())

    refresh_tag_cache(session)
    prefix = next(iter(_TAG_CACHE["physics_model"]))[:3]
    completions = list(TagCompleter("physics_model").get_completions(Document(prefix), None))

    assert _TAG_CACHE["physics_model"]
    assert completions


@pytest.mark.asyncio
async def test_search_and_show_flow(
    repl_workspace_with_index: tuple[Path, list[str]],
    capsys,
) -> None:
    workspace, ids = repl_workspace_with_index
    session = SessionState(workspace_path=workspace, config=AppConfig())
    session.index_meta = load_index_meta(workspace)

    await do_search(session, ["--physics-model", "newton_second_law"])
    await do_show(session, ["1"])

    output = capsys.readouterr().out
    assert ids[0] in session.last_search_result_ids
    assert "牛顿第二定律" in output
    assert session.current_problem_id == ids[0]


@pytest.mark.asyncio
async def test_show_full_uses_pager(
    repl_workspace_with_index: tuple[Path, list[str]],
    monkeypatch,
) -> None:
    workspace, ids = repl_workspace_with_index
    session = SessionState(workspace_path=workspace, config=AppConfig())
    session.index_meta = load_index_meta(workspace)
    seen: list[str] = []
    monkeypatch.setattr("cpho_cli.cli.repl.commands.search.display.pager", seen.append)

    await do_show(session, [ids[0], "--full"])

    assert "OCR 文本" in seen[0]


def test_register_adds_search_commands() -> None:
    registry: dict[str, Command] = {}

    register(registry)

    assert {"/search", "/show"} <= set(registry)
