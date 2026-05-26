"""Debug command for inspecting skill folders."""

from __future__ import annotations

from pathlib import Path

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands import Command
from cpho_cli.core.skills import SkillDefinitionError, load_skill


async def do_run(session, args: list[str]) -> None:  # type: ignore[no-untyped-def]
    if not args:
        display.error("用法: /run <skill_dir>")
        return
    try:
        loaded = load_skill(Path(args[0]).expanduser())
    except SkillDefinitionError as exc:
        display.error(str(exc))
        return
    print(f"Skill root: {loaded.root}")
    print(f"Name: {loaded.spec.name}")
    print(f"Steps: {len(loaded.spec.steps)}")
    print("Prompt templates:")
    for step_id, path in loaded.prompt_paths.items():
        print(f"  {step_id}: {path}")


def register(registry: dict[str, Command]) -> None:
    registry["/run"] = Command(
        name="/run",
        help="调试读取 skill 目录，不执行步骤",
        usage="/run <skill_dir>",
        handler=do_run,
        category="技能",
    )


__all__ = ["do_run", "register"]
