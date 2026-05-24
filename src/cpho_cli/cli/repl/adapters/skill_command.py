"""Skill-to-command adapter placeholders for Phase 3.

Data flow: 第三方 skill -> core SkillSpec -> cli/repl SkillCommandAdapter -> REPL command.
"""

from __future__ import annotations

from typing import Any


def make_skill_handler(skill: Any) -> Any:
    """Return an async REPL handler for a SkillSpec in Phase 3."""
    raise NotImplementedError("Phase 3")


def make_skill_completer(skill: Any) -> Any:
    """Return a prompt_toolkit completer from SkillSpec completion metadata in Phase 3."""
    raise NotImplementedError("Phase 3")


def register_skill_adapters(registry: dict[str, Any], skills: list[Any]) -> None:
    """Register SkillSpec objects as slash commands in Phase 3."""
    raise NotImplementedError("Phase 3")


__all__ = ["make_skill_completer", "make_skill_handler", "register_skill_adapters"]
