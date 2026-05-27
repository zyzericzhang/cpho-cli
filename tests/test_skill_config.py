from __future__ import annotations

from pathlib import Path

from cpho_cli.core.skill_config import (
    resolve_step_model,
    save_workspace_step_model,
    user_skill_config_path,
)
from cpho_cli.models.skills import SkillStep


def test_resolve_step_model_uses_code_default_then_provider(tmp_path: Path) -> None:
    assert (
        resolve_step_model(
            tmp_path,
            "solve",
            SkillStep(id="s1", kind="llm", default_model="code/model"),
            provider_default="provider/model",
        )
        == "code/model"
    )
    assert (
        resolve_step_model(
            tmp_path,
            "solve",
            SkillStep(id="s2", kind="llm"),
            provider_default="provider/model",
        )
        == "provider/model"
    )


def test_workspace_step_model_override_wins(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    user_path = user_skill_config_path("solve")
    user_path.parent.mkdir(parents=True)
    user_path.write_text("steps:\n  step:\n    model: user/model\n", encoding="utf-8")
    save_workspace_step_model(tmp_path, "solve", "step", "workspace/model")

    model = resolve_step_model(
        tmp_path,
        "solve",
        SkillStep(id="step", kind="llm"),
        provider_default="provider/model",
    )

    assert model == "workspace/model"
