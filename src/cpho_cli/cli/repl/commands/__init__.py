"""Built-in REPL commands (commands.* sub-modules each expose register(registry))."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prompt_toolkit.completion import Completer

    from cpho_cli.cli.repl.session import SessionState

Handler = Callable[["SessionState", list[str]], Awaitable[None]]


@dataclass
class Command:
    name: str
    help: str
    usage: str
    handler: Handler
    completer: "Completer | None" = None
    category: str = "其他"


registry: dict[str, Command] = {}


def install_builtin_commands(registry: dict[str, Command]) -> None:
    from cpho_cli.cli.repl.commands import (
        builtin_skills,
        compose,
        help_cmd,
        related,
        run_debug,
        search,
        set_cmd,
        workspace,
    )

    for module in (
        search,
        workspace,
        help_cmd,
        set_cmd,
        run_debug,
        builtin_skills,
        related,
        compose,
    ):
        module.register(registry)


__all__ = ["Command", "Handler", "registry", "install_builtin_commands"]
