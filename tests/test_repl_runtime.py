from __future__ import annotations

from pathlib import Path

import pytest
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from cpho_cli.cli.repl.app import ReplApp
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.completers import CphoCompleter, CphoLexer


class FakePromptSession:
    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    async def prompt_async(self, prompt_text: str) -> str:
        if not self.lines:
            raise EOFError
        line = self.lines.pop(0)
        if line == "<EOF>":
            raise EOFError
        return line


class FakeCompleter(Completer):
    def get_completions(self, document, complete_event):  # type: ignore[no-untyped-def]
        yield Completion("delegated", start_position=0)


async def _noop(session, args: list[str]) -> None:  # type: ignore[no-untyped-def]
    session.called = True


def test_completer_command_and_delegation() -> None:
    registry = {
        "/help": Command("/help", "帮助", "/help", _noop),
        "/x": Command("/x", "x", "/x", _noop, completer=FakeCompleter()),
    }

    names = list(CphoCompleter(registry).get_completions(Document("/h"), None))
    delegated = list(CphoCompleter(registry).get_completions(Document("/x "), None))

    assert names[0].text == "/help"
    assert delegated[0].text == "delegated"


def test_lexer_marks_command_flag_and_arg() -> None:
    lexer = CphoLexer()
    get_line = lexer.lex_document(Document("/search --limit 力学"))

    assert get_line(0)[0][0] == "class:cmd"
    assert get_line(0)[1][0] == "class:flag"
    assert get_line(0)[2][0] == "class:arg"


@pytest.mark.asyncio
async def test_repl_dispatch_unknown_and_help(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    monkeypatch.setenv("CPHO_DISABLE_UPDATE_CHECK", "1")
    app = ReplApp(workspace=tmp_path, prompt_session=FakePromptSession(["/help", "/missing", "<EOF>"]))

    await app.run()

    assert (tmp_path / "xdg" / "cpho" / "session.json").exists()


@pytest.mark.asyncio
async def test_repl_prints_update_notice(tmp_path: Path, monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    from cpho_cli.cli.repl import app as repl_app
    from cpho_cli.models.update import UpdateCheckResult

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    monkeypatch.delenv("CPHO_DISABLE_UPDATE_CHECK", raising=False)
    monkeypatch.setattr(
        repl_app,
        "check_for_update",
        lambda current_version: UpdateCheckResult(
            available=True,
            current_version=current_version,
            latest_version="0.2.0",
            release_url="https://github.com/zyzericzhang/cpho-cli/releases/tag/v0.2.0",
        ),
    )
    app = ReplApp(workspace=tmp_path, prompt_session=FakePromptSession(["<EOF>"]))

    await app.run()

    output = capsys.readouterr().out
    assert "发现新版本 0.2.0" in output
    assert "https://github.com/zyzericzhang/cpho-cli/releases/tag/v0.2.0" in output


def test_importing_typer_app_does_not_import_prompt_toolkit() -> None:
    import sys

    sys.modules.pop("prompt_toolkit", None)
    import cpho_cli.cli.app  # noqa: F401

    assert "prompt_toolkit" not in sys.modules
