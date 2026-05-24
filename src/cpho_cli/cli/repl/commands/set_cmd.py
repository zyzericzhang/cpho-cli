"""Session setting command."""

from __future__ import annotations

from pathlib import Path

from prompt_toolkit.completion import Completer, Completion

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.persistence import write_session
from cpho_cli.cli.repl.session import load_index_meta
from cpho_cli.core.llm import supported_provider_kinds

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
        if not _validate_provider(session, value):
            return
        session.provider_name = value
    write_session(session)
    print(f"已更新 {key}: {_current_value(session, key)}")


def _validate_provider(session, name: str) -> bool:  # type: ignore[no-untyped-def]
    if name == "openrouter":
        return True

    profile = session.config.providers.get(name)
    if profile is None:
        display.error(
            f"未知的 provider: {name}。"
            f"可用: openrouter{_configured_providers_hint(session.config.providers)}"
        )
        return False

    if profile.kind not in supported_provider_kinds():
        display.error(
            f"Provider '{name}' 的 kind '{profile.kind}' 不支持。"
            f"支持: {', '.join(sorted(supported_provider_kinds()))}"
        )
        return False

    if not profile.api_key and not profile.api_key_env:
        display.warn(
            f"Provider '{name}' 未配置 api_key 或 api_key_env，"
            f"使用时将报错。请在 config.local.yml 的 providers.{name} 中设置。"
        )
    return True


def _configured_providers_hint(providers: dict) -> str:  # type: ignore[no-untyped-def]
    names = [n for n in providers if n != "openrouter"]
    if not names:
        return ""
    return ", " + ", ".join(sorted(names))


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
