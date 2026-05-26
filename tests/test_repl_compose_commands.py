from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.cli.repl.commands.compose import do_compose
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.models.config import AppConfig


@pytest.mark.asyncio
async def test_repl_compose_new_creates_template(tmp_path: Path, capsys) -> None:
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await do_compose(session, ["new", "mock", "--count", "2"])

    assert (tmp_path / ".cpho" / "compositions" / "mock.yml").exists()
    assert "mock.yml" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_repl_compose_requires_explicit_last_related(tmp_path: Path, capsys) -> None:
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await do_compose(session, ["auto", "--from", "last-related", "--count", "1"])

    assert "last_related 为空" in capsys.readouterr().out
