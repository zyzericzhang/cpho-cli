from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.cli.repl.commands import model_panel
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.models.config import AppConfig, ProviderProfile
from cpho_cli.core.model_catalog import ModelCatalog, ModelCatalogEntry


@pytest.mark.asyncio
async def test_skill_panel_prints_pipeline_metadata(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await model_panel.do_skill(session, ["panel", "solve"])

    output = capsys.readouterr().out
    assert "extract_official_steps" in output
    assert "assemble_final_report" in output
    assert "prompts" in output


@pytest.mark.asyncio
async def test_skill_set_model_writes_workspace_override(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await model_panel.do_skill(
        session,
        ["set-model", "solve", "extract_official_steps", "openai/gpt-4o-mini"],
    )

    output = capsys.readouterr().out
    assert "已更新 solve.extract_official_steps" in output
    assert (tmp_path / ".cpho" / "skills" / "solve.yml").exists()


@pytest.mark.asyncio
async def test_model_refresh_uses_catalog_loader(tmp_path: Path, monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    session = SessionState(
        workspace_path=tmp_path,
        config=AppConfig(
            providers={
                "openrouter": ProviderProfile(
                    kind="openrouter",
                    api_key="sk-test",
                    default_model="openai/gpt-4o-mini",
                )
            }
        ),
        provider_name="openrouter",
    )

    def fake_load_model_catalog(*args, **kwargs):  # type: ignore[no-untyped-def]
        return ModelCatalog(
            provider="openrouter",
            models=[ModelCatalogEntry(id="m1")],
            source="live",
        )

    monkeypatch.setattr(model_panel, "load_model_catalog", fake_load_model_catalog)

    await model_panel.do_model(session, ["refresh"])

    assert "已刷新 openrouter 模型列表: 1 个" in capsys.readouterr().out
