from __future__ import annotations

import ast
from pathlib import Path

from cpho_cli.core.config import ConfigError, load_config, resolve_api_key
from cpho_cli.core.skills import SkillDefinitionError, load_skill


def _error_helper_names() -> set[str]:
    tree = ast.parse(Path("src/cpho_cli/core/errors.py").read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("err_")
    }


def test_every_error_helper_has_user_doc() -> None:
    docs_dir = Path("docs/user/errors")
    documented = {path.stem for path in docs_dir.glob("err_*.md")}

    assert _error_helper_names() <= documented


def test_error_docs_index_links_all_error_docs() -> None:
    index = Path("docs/user/errors/README.md").read_text(encoding="utf-8")
    for name in _error_helper_names():
        assert f"{name}.md" in index


def test_missing_api_key_error_uses_structured_pattern(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text("provider:\n  openrouter_api_key: ''\n", encoding="utf-8")
    config = load_config(config_path)

    try:
        resolve_api_key(config, {})
    except ConfigError as exc:
        message = str(exc)
    else:
        raise AssertionError("resolve_api_key should fail")

    assert "[发生了什么]" in message
    assert "[原因]" in message
    assert "[修复方法]" in message
    assert "OPENROUTER_API_KEY" in message
    assert "sk-" not in message


def test_missing_skill_prompt_names_file_to_fix(tmp_path: Path) -> None:
    (tmp_path / "prompts").mkdir()
    (tmp_path / "SKILL.md").write_text("# Test\n", encoding="utf-8")
    (tmp_path / "skill.yml").write_text(
        """
name: test
inputs: [problem_text]
outputs: [answer]
steps:
  - id: derive
    kind: llm
    input_keys: [problem_text]
    output_keys: [answer]
    prompt_template: missing.md.j2
""",
        encoding="utf-8",
    )

    try:
        load_skill(tmp_path)
    except SkillDefinitionError as exc:
        message = str(exc)
    else:
        raise AssertionError("load_skill should fail")

    assert "[修复方法]" in message
    assert "missing.md.j2" in message
    assert "skill.yml" in message
