from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.commands.workspace import (
    do_config,
    do_index,
    do_reload_index,
    do_resume,
    do_status,
    do_workspace,
    register,
)
from cpho_cli.cli.repl.persistence import write_session
from cpho_cli.cli.repl.session import SessionState, load_index_meta
from cpho_cli.models.config import AppConfig


@pytest.mark.asyncio
async def test_workspace_status_config_and_register(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await do_workspace(session, [])
    await do_status(session, [])
    await do_config(session, [])
    registry: dict[str, Command] = {}
    register(registry)

    output = capsys.readouterr().out
    assert "当前工作空间" in output
    assert "索引状态: 未建立" in output
    assert "api_key" not in output.lower()
    assert {"/workspace", "/status", "/config", "/index", "/reload-index", "/resume"} <= set(registry)


@pytest.mark.asyncio
async def test_workspace_switch_existing_dir(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    session = SessionState(workspace_path=tmp_path / "old", config=AppConfig())
    new_workspace = tmp_path / "new"
    new_workspace.mkdir()

    await do_workspace(session, [str(new_workspace)])

    assert session.workspace_path == new_workspace


@pytest.mark.asyncio
async def test_index_dry_run_cancel_and_success(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[bool] = []

    def fake_build_index(*args, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(bool(kwargs["dry_run"]))
        from cpho_cli.models.index import IndexRunStats

        return IndexRunStats(total_problems=2, papers_split=1, problems_extracted=2)

    monkeypatch.setattr("cpho_cli.cli.repl.commands.workspace.build_index", fake_build_index)
    monkeypatch.setattr("cpho_cli.cli.repl.commands.workspace.confirm_index_run", lambda _: True)
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await do_index(session, [])

    assert calls == [True, False]


@pytest.mark.asyncio
async def test_reload_and_resume(
    repl_workspace_with_index: tuple[Path, list[str]],
    monkeypatch,
) -> None:
    workspace, ids = repl_workspace_with_index
    session = SessionState(workspace_path=workspace, config=AppConfig())
    session.index_meta = load_index_meta(workspace)
    session.last_search_query = "力学"
    session.last_search_result_ids = ids
    session.current_problem_id = ids[0]
    write_session(session)
    session.last_search_query = None
    session.last_search_result_ids = []
    session.current_problem_id = None

    await do_resume(session, [])
    await do_reload_index(session, [])

    assert session.last_search_query == "力学"
    assert session.last_search_result_ids == ids
    assert session.index_meta is not None
