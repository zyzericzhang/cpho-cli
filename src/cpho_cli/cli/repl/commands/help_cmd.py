"""Help command for the REPL."""

from __future__ import annotations

from collections import defaultdict

from cpho_cli.cli.repl.commands import Command


async def do_help(session, args: list[str]) -> None:  # type: ignore[no-untyped-def]
    registry: dict[str, Command] = getattr(session, "registry", {})
    if args:
        name = args[0]
        if not name.startswith("/"):
            name = "/" + name
        command = registry.get(name)
        if command is None:
            print(f"未知命令: {name}")
            return
        print(f"{command.name}\n{command.help}\n用法: {command.usage}")
        return

    grouped: dict[str, list[Command]] = defaultdict(list)
    for command in registry.values():
        grouped[command.category].append(command)
    for category in sorted(grouped):
        print(f"[{category}]")
        for command in sorted(grouped[category], key=lambda item: item.name):
            print(f"  {command.name:<14} {command.help}")


def register(registry: dict[str, Command]) -> None:
    registry["/help"] = Command(
        name="/help",
        help="显示可用命令或单个命令说明",
        usage="/help [command]",
        handler=do_help,
        category="帮助",
    )


__all__ = ["do_help", "register"]
