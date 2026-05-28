from __future__ import annotations

import os
from pathlib import Path

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.config import ConfigError, resolve_provider_config
from cpho_cli.core.llm import LLMProviderError
from cpho_cli.core.model_catalog import ModelCatalogError, load_model_catalog
from cpho_cli.core.skill_config import resolve_step_model, save_workspace_step_model
from cpho_cli.core.skills import SkillDefinitionError, load_skill

_BUILTIN_SKILL_DIRS = {
    "solve": Path("src/cpho_cli/builtin_skills/solve"),
    "explain": Path("src/cpho_cli/builtin_skills/explain"),
    "probe": Path("src/cpho_cli/builtin_skills/probe"),
}


def _skill_dir(name: str) -> Path | None:
    return _BUILTIN_SKILL_DIRS.get(name)


async def do_skill(session: SessionState, args: list[str]) -> None:
    if not args:
        display.error("用法: /skill panel <name> 或 /skill set-model <name> <step_id> <model>")
        return
    action = args[0]
    if action == "panel":
        await _do_panel(session, args[1:])
        return
    if action == "set-model":
        await _do_set_model(session, args[1:])
        return
    display.error("用法: /skill panel <name> 或 /skill set-model <name> <step_id> <model>")


async def _do_panel(session: SessionState, args: list[str]) -> None:
    if not args:
        display.error("用法: /skill panel <name>")
        return
    skill_name = args[0]
    root = _skill_dir(skill_name)
    if root is None:
        display.error(f"未知 skill: {skill_name}")
        return
    try:
        loaded = load_skill(root)
    except SkillDefinitionError as exc:
        display.error(str(exc))
        return
    provider_default = session.config.model.name
    description = loaded.spec.describe(loaded.root)
    rows = []
    for step in loaded.spec.steps:
        step_description = next(item for item in description.steps if item.id == step.id)
        rows.append(
            [
                step.id,
                step.kind,
                resolve_step_model(
                    session.workspace_path,
                    skill_name,
                    step,
                    provider_default=provider_default,
                )
                or "",
                "yes" if step.requires_multimodal else "no",
                str(step_description.prompt_path or ""),
            ]
        )
    print(display.render_table(["Step", "Kind", "Model", "Multimodal", "Prompt"], rows, [22, 8, 28, 10, 48]))
    if description.edges:
        print("Edges:")
        for edge in description.edges:
            print(f"  {edge.source} -> {edge.target} ({edge.reason})")


async def _do_set_model(session: SessionState, args: list[str]) -> None:
    if len(args) < 3:
        display.error("用法: /skill set-model <name> <step_id> <model>")
        return
    skill_name, step_id, model = args[0], args[1], " ".join(args[2:])
    root = _skill_dir(skill_name)
    if root is None:
        display.error(f"未知 skill: {skill_name}")
        return
    loaded = load_skill(root)
    if step_id not in {step.id for step in loaded.spec.steps}:
        display.error(f"未知 step: {step_id}")
        return
    path = save_workspace_step_model(session.workspace_path, skill_name, step_id, model)
    print(f"已更新 {skill_name}.{step_id}: {model}")
    print(f"配置: {path}")


async def do_model(session: SessionState, args: list[str]) -> None:
    action = args[0] if args else "list"
    if action != "refresh":
        display.error("用法: /model refresh")
        return
    try:
        provider_config = resolve_provider_config(session.config, os.environ, session.provider_name)
        catalog = load_model_catalog(
            provider_config.kind,
            api_key=provider_config.api_key,
            base_url=provider_config.base_url,
            force_refresh=True,
        )
    except (ConfigError, LLMProviderError, ModelCatalogError, ValueError) as exc:
        display.error(f"模型列表刷新失败: {exc}")
        return
    print(f"已刷新 {catalog.provider} 模型列表: {len(catalog.models)} 个 ({catalog.source})")


def register(registry: dict[str, Command]) -> None:
    registry["/skill"] = Command(
        name="/skill",
        help="查看或修改 skill pipeline 模型设置",
        usage="/skill panel <name> | /skill set-model <name> <step_id> <model>",
        handler=do_skill,
        category="模型",
    )
    registry["/model"] = Command(
        name="/model",
        help="刷新 provider 模型列表",
        usage="/model refresh",
        handler=do_model,
        category="模型",
    )


__all__ = ["do_model", "do_skill", "register"]
