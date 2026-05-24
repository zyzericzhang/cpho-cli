from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.commands.builtin_skills import PHASE3_MSG, register as register_skills
from cpho_cli.cli.repl.commands.help_cmd import register as register_help
from cpho_cli.cli.repl.commands.set_cmd import do_set
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.models.config import AppConfig


def test_help_uses_registry_source_of_truth(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    registry: dict[str, Command] = {}
    register_help(registry)
    session = SessionState(workspace_path=tmp_path, config=AppConfig())
    setattr(session, "registry", registry)

    import asyncio

    asyncio.run(registry["/help"].handler(session, []))

    assert "/help" in capsys.readouterr().out


def test_phase3_placeholders(capsys) -> None:  # type: ignore[no-untyped-def]
    registry: dict[str, Command] = {}
    register_skills(registry)

    import asyncio

    asyncio.run(registry["/explain"].handler(object(), []))

    assert PHASE3_MSG in capsys.readouterr().out


@pytest.mark.asyncio
async def test_set_validates_session_fields(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await do_set(session, ["max_results", "5"])
    await do_set(session, ["output_format", "full"])

    assert session.max_results == 5
    assert session.output_format == "full"
