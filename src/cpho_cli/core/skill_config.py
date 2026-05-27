from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import Field

from cpho_cli.models.config import StrictModel
from cpho_cli.models.skills import SkillStep


class SkillStepModelOverride(StrictModel):
    model: str | None = None


class SkillModelConfig(StrictModel):
    steps: dict[str, SkillStepModelOverride] = Field(default_factory=dict)


def user_skill_config_dir() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "cpho" / "skills"


def workspace_skill_config_path(workspace_root: Path, skill_id: str) -> Path:
    return workspace_root / ".cpho" / "skills" / f"{skill_id}.yml"


def user_skill_config_path(skill_id: str) -> Path:
    return user_skill_config_dir() / f"{skill_id}.yml"


def load_skill_model_config(path: Path) -> SkillModelConfig:
    if not path.exists():
        return SkillModelConfig()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return SkillModelConfig()
    return SkillModelConfig.model_validate(raw)


def save_workspace_step_model(
    workspace_root: Path,
    skill_id: str,
    step_id: str,
    model: str,
) -> Path:
    path = workspace_skill_config_path(workspace_root, skill_id)
    config = load_skill_model_config(path)
    config.steps[step_id] = SkillStepModelOverride(model=model)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def resolve_step_model(
    workspace_root: Path,
    skill_id: str,
    step: SkillStep,
    *,
    provider_default: str | None,
) -> str | None:
    workspace_config = load_skill_model_config(workspace_skill_config_path(workspace_root, skill_id))
    user_config = load_skill_model_config(user_skill_config_path(skill_id))
    for config in (workspace_config, user_config):
        override = config.steps.get(step.id)
        if override is not None and override.model:
            return override.model
    return step.default_model or provider_default
