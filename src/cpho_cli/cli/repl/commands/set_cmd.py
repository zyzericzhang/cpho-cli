"""Session setting command."""

from __future__ import annotations

from pathlib import Path

from prompt_toolkit.completion import Completer, Completion

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.persistence import write_session
from cpho_cli.cli.repl.session import load_index_meta

ALLOWED_KEYS = ("workspace", "max_results", "output_format", "provider")


class SetCompleter(Completer):
    def get_completions(self, document, complete_event):  # type: ignore[no-untyped-def]
        text = document.text_before_cursor.split()[-1] if document.text_before_cursor.split() else ""
        for key in ALLOWED_KEYS:
            if key.startswith(text):
                yield Completion(key, start_position=-len(text))


def _current_value(session, key: str) -> str:  # type: ignore[no-untyped-def]
    if key == "workspace":
        return str(session.workspace_path)
    if key == "provider":
        return session.provider_name or str(session.config.active_provider)
    return str(getattr(session, key))


async def do_set(session, args: list[str]) -> None:  # type: ignore[no-untyped-def]
    if not args:
        for key in ALLOWED_KEYS:
            print(f"{key}: {_current_value(session, key)}")
        return
    key = args[0]
    if key not in ALLOWED_KEYS:
        display.error(f"不支持的设置: {key}")
        return
    if len(args) == 1:
        print(f"{key}: {_current_value(session, key)}")
        return

    value = " ".join(args[1:])
    if key == "workspace":
        path = Path(value).expanduser().resolve()
        if not path.is_dir():
            display.error(f"工作空间不存在: {path}")
            return
        session.workspace_path = path
        session.index_path = path / ".cpho" / "index.jsonl"
        session.index_meta = load_index_meta(path)
    elif key == "max_results":
        try:
            parsed = int(value)
        except ValueError:
            display.error("max_results 必须是整数")
            return
        if parsed <= 0:
            display.error("max_results 必须大于 0")
            return
        session.max_results = parsed
    elif key == "output_format":
        if value not in {"compact", "full"}:
            display.error("output_format 必须是 compact 或 full")
            return
        session.output_format = value
    elif key == "provider":
        session.provider_name = value
    write_session(session)
    print(f"已更新 {key}: {_current_value(session, key)}")


def register(registry: dict[str, Command]) -> None:
    registry["/set"] = Command(
        name="/set",
        help="查看或修改会话设置",
        usage="/set [workspace|max_results|output_format|provider] [value]",
        handler=do_set,
        completer=SetCompleter(),
        category="设置",
    )


__all__ = ["do_set", "register"]
