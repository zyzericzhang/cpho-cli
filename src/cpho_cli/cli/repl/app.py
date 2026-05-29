"""prompt_toolkit REPL runtime."""

from __future__ import annotations

import logging
import os
import shlex
import sys
import traceback
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.styles import Style

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands import Command, install_builtin_commands, registry
from cpho_cli.cli.repl.completers import CphoCompleter, CphoLexer
from cpho_cli.cli.repl.persistence import history_path, log_path, read_session, write_session
from cpho_cli.cli.repl.session import SessionState, load_index_meta
from cpho_cli import get_version
from cpho_cli.core.config import ConfigError, load_config
from cpho_cli.core.update_check import check_for_update

STYLE = Style.from_dict({"cmd": "#5f87ff", "flag": "#ffd700", "arg": "#5fd75f"})


def _logger() -> logging.Logger:
    logger = logging.getLogger("cpho_cli.repl")
    logger.setLevel(logging.ERROR)
    if not logger.handlers:
        handler = logging.FileHandler(log_path(), encoding="utf-8")
        logger.addHandler(handler)
    return logger


def _read_persisted_workspace() -> Path | None:
    try:
        payload = read_session()
    except Exception:
        return None
    if payload is None:
        return None
    raw = payload.get("workspace_path")
    if not isinstance(raw, str):
        return None
    path = Path(raw).expanduser()
    return path if path.is_dir() else None


class ReplApp:
    def __init__(
        self,
        *,
        workspace: Path | None = None,
        config_path: Path | None = None,
        provider_name: str | None = None,
        prompt_session: object | None = None,
    ) -> None:
        resolved_workspace = (
            workspace.expanduser().resolve()
            if workspace is not None
            else (_read_persisted_workspace() or Path.cwd()).resolve()
        )
        try:
            config = load_config(config_path)
        except ConfigError as exc:
            display.warn(str(exc))
            config = load_config(None)
        self.registry: dict[str, Command] = dict(registry)
        install_builtin_commands(self.registry)
        prompt_kwargs = {
            "history": FileHistory(str(history_path())),
            "completer": CphoCompleter(self.registry),
            "lexer": CphoLexer(),
            "style": STYLE,
        }
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            prompt_kwargs["output"] = DummyOutput()
        self.prompt_session = prompt_session or PromptSession(
            **prompt_kwargs,
        )
        self.session = SessionState(
            workspace_path=resolved_workspace,
            config=config,
            config_path=config_path,
            provider_name=provider_name,
            index_path=resolved_workspace / ".cpho" / "index.jsonl",
            index_meta=load_index_meta(resolved_workspace),
            prompt_session=self.prompt_session,
        )
        setattr(self.session, "registry", self.registry)

    async def dispatch(self, line: str) -> None:
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            display.error(f"输入解析失败: {exc}")
            return
        if not parts:
            return
        command = self.registry.get(parts[0])
        if command is None:
            display.error(f"未知命令: {parts[0]}，输入 /help 查看可用命令")
            return
        try:
            await command.handler(self.session, parts[1:])
        except KeyboardInterrupt:
            display.warn("中断")
        except Exception as exc:
            _logger().error("handler failed\n%s", traceback.format_exc())
            display.error(str(exc))

    async def run(self) -> None:
        print(display.banner(self.session))
        if os.environ.get("CPHO_DISABLE_UPDATE_CHECK") != "1":
            result = check_for_update(get_version())
            if result.available and result.latest_version and result.release_url:
                display.warn(f"发现新版本 {result.latest_version}: {result.release_url}")
        while True:
            try:
                line = await self.prompt_session.prompt_async("cpho> ")  # type: ignore[attr-defined]
            except KeyboardInterrupt:
                display.warn("中断")
                continue
            except EOFError:
                break
            await self.dispatch(line)
        try:
            write_session(self.session)
        except Exception as exc:
            display.error(f"保存 session 失败: {exc}")


async def run_repl(
    *,
    workspace: Path | None = None,
    config_path: Path | None = None,
    provider_name: str | None = None,
) -> None:
    app = ReplApp(workspace=workspace, config_path=config_path, provider_name=provider_name)
    await app.run()


__all__ = ["ReplApp", "run_repl"]
