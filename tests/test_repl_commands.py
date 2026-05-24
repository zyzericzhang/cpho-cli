from __future__ import annotations

import subprocess
import sys
from types import SimpleNamespace

import pytest

from cpho_cli.cli.repl.commands import Command, registry


async def _handler(session: object, args: list[str]) -> None:
    calls = getattr(session, "calls", 0)
    setattr(session, "calls", calls + 1)


def test_command_defaults_and_registry_empty() -> None:
    cmd = Command(name="/x", help="h", usage="u", handler=_handler)

    assert cmd.completer is None
    assert cmd.category == "其他"
    assert registry == {}


@pytest.mark.asyncio
async def test_registered_command_handler_invokes() -> None:
    local = {"/x": Command(name="/x", help="h", usage="u", handler=_handler)}
    session = SimpleNamespace()

    await local["/x"].handler(session, [])

    assert getattr(session, "calls") == 1


def test_command_is_mutable_and_prompt_toolkit_lazy() -> None:
    cmd = Command(name="/x", help="h", usage="u", handler=_handler)

    cmd.help = "新"

    assert cmd.help == "新"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import cpho_cli.cli.repl.commands; "
            "assert 'prompt_toolkit' not in sys.modules",
        ],
        check=True,
    )
    assert result.returncode == 0
