"""prompt_toolkit completion and highlighting for CPHO slash commands."""

from __future__ import annotations

import shlex

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.lexers import Lexer

from cpho_cli.cli.repl.commands import Command


class CphoCompleter(Completer):
    def __init__(self, registry: dict[str, Command]) -> None:
        self._registry = registry

    def get_completions(self, document: Document, complete_event):  # type: ignore[no-untyped-def]
        text = document.text_before_cursor
        if text.startswith("/") and " " not in text:
            for name, registered in sorted(self._registry.items()):
                if name.startswith(text):
                    yield Completion(name, start_position=-len(text), display_meta=registered.help)
            return

        try:
            parts = shlex.split(text)
        except ValueError:
            return
        if not parts:
            return
        selected = self._registry.get(parts[0])
        if selected is not None and selected.completer is not None:
            yield from selected.completer.get_completions(document, complete_event)


class CphoLexer(Lexer):
    def lex_document(self, document: Document):  # type: ignore[no-untyped-def]
        def get_line(lineno: int) -> list[tuple[str, str]]:
            tokens: list[tuple[str, str]] = []
            for token in document.lines[lineno].split(" "):
                if token.startswith("/"):
                    style = "class:cmd"
                elif token.startswith("--"):
                    style = "class:flag"
                else:
                    style = "class:arg"
                tokens.append((style, token + " "))
            return tokens

        return get_line


__all__ = ["CphoCompleter", "CphoLexer"]
