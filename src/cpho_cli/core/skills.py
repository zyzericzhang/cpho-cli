from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import ValidationError

from cpho_cli.models.skills import SkillSpec


class SkillDefinitionError(ValueError):
    """Raised when a skill folder is invalid."""


@dataclass(frozen=True)
class LoadedSkill:
    root: Path
    readme: str
    spec: SkillSpec
    prompt_paths: dict[str, Path]


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def load_skill(skill_dir: Path) -> LoadedSkill:
    readme_path = skill_dir / "SKILL.md"
    spec_path = skill_dir / "skill.yml"
    if not readme_path.exists() or not spec_path.exists():
        raise SkillDefinitionError("Skill folder must contain SKILL.md and skill.yml.")
    try:
        raw = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
        spec = SkillSpec.model_validate(raw)
    except (yaml.YAMLError, ValidationError) as exc:
        raise SkillDefinitionError(f"Invalid skill metadata: {exc}") from exc

    seen_outputs: set[str] = set()
    prompt_paths: dict[str, Path] = {}
    for step in spec.steps:
        overlap = seen_outputs & set(step.output_keys)
        if overlap:
            raise SkillDefinitionError(f"Duplicate output keys: {sorted(overlap)}")
        seen_outputs.update(step.output_keys)
        if step.prompt_template:
            prompt_path = skill_dir / "prompts" / step.prompt_template
            if not _inside(prompt_path, skill_dir / "prompts"):
                raise SkillDefinitionError("Prompt template path escapes skill prompts directory.")
            prompt_paths[step.id] = prompt_path

    return LoadedSkill(
        root=skill_dir,
        readme=readme_path.read_text(encoding="utf-8"),
        spec=spec,
        prompt_paths=prompt_paths,
    )

