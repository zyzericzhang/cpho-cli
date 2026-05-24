"""Phase 3 skill command placeholders."""

from __future__ import annotations

from cpho_cli.cli.repl.commands import Command

PHASE3_MSG = "Phase 3 未实现，请期待。"


async def do_phase3_stub(session, args: list[str]) -> None:  # type: ignore[no-untyped-def]
    print(PHASE3_MSG)


def register(registry: dict[str, Command]) -> None:
    for name, help_text in {
        "/explain": "讲解当前题目（Phase 3）",
        "/quiz": "基于当前题目生成追问（Phase 3）",
    }.items():
        registry[name] = Command(
            name=name,
            help=help_text,
            usage=name,
            handler=do_phase3_stub,
            category="技能",
        )


__all__ = ["PHASE3_MSG", "do_phase3_stub", "register"]
