from pathlib import Path

import pytest

from cpho_cli.core.skills import SkillDefinitionError, load_skill


def write_skill(root: Path, template_ref: str = "derive.md.j2") -> None:
    (root / "prompts").mkdir(parents=True)
    (root / "SKILL.md").write_text("# Solve\n", encoding="utf-8")
    (root / "prompts" / "derive.md.j2").write_text("{{ problem_text }}", encoding="utf-8")
    (root / "skill.yml").write_text(
        f"""
name: solve
inputs:
  - problem_text
outputs:
  - derivation
steps:
  - id: derive
    kind: llm
    input_keys: [problem_text]
    output_keys: [derivation]
    prompt_template: {template_ref}
""",
        encoding="utf-8",
    )


def test_load_skill_folder(tmp_path: Path) -> None:
    write_skill(tmp_path)

    loaded = load_skill(tmp_path)

    assert loaded.spec.name == "solve"
    assert loaded.spec.steps[0].id == "derive"


def test_rejects_template_path_traversal(tmp_path: Path) -> None:
    write_skill(tmp_path, "../outside.md.j2")

    with pytest.raises(SkillDefinitionError):
        load_skill(tmp_path)


def test_rejects_duplicate_output_keys(tmp_path: Path) -> None:
    write_skill(tmp_path)
    with (tmp_path / "skill.yml").open("a", encoding="utf-8") as handle:
        handle.write(
            """
  - id: derive_again
    kind: llm
    input_keys: [problem_text]
    output_keys: [derivation]
    prompt_template: derive.md.j2
"""
        )

    with pytest.raises(SkillDefinitionError):
        load_skill(tmp_path)

