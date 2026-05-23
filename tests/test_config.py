from pathlib import Path

import pytest

from cpho_cli.core.config import (
    ConfigError,
    load_config,
    resolve_api_key,
    resolve_model_params,
    resolve_provider_config,
)
from cpho_cli.models.config import ModelParams


def test_resolve_api_key_from_environment() -> None:
    config = load_config(None)

    assert resolve_api_key(config, {"OPENROUTER_API_KEY": "sk-test"}) == "sk-test"


def test_load_config_defaults_to_local_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.local.yml"
    config_path.write_text("provider:\n  openrouter_api_key: sk-local\n", encoding="utf-8")
    nested_dir = tmp_path / "problems"
    nested_dir.mkdir()
    monkeypatch.chdir(nested_dir)

    config = load_config(None)

    assert resolve_api_key(config, {}) == "sk-local"


def test_resolve_provider_profile_from_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
active_provider: backup
providers:
  openrouter:
    kind: openrouter
    api_key: sk-primary
  backup:
    kind: openrouter
    api_key: sk-backup
    base_url: https://openrouter.example/api/v1
""",
        encoding="utf-8",
    )
    config = load_config(config_path)

    resolved = resolve_provider_config(config, {}, "backup")

    assert resolved.name == "backup"
    assert resolved.kind == "openrouter"
    assert resolved.api_key == "sk-backup"
    assert resolved.base_url == "https://openrouter.example/api/v1"


def test_resolve_provider_profile_by_env_reference(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
providers:
  school:
    kind: openrouter
    api_key_env: SCHOOL_OPENROUTER_KEY
""",
        encoding="utf-8",
    )
    config = load_config(config_path)

    resolved = resolve_provider_config(config, {"SCHOOL_OPENROUTER_KEY": "sk-school"}, "school")

    assert resolved.api_key == "sk-school"


def test_unknown_provider_profile_fails_without_secret(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
providers:
  openrouter:
    kind: openrouter
    api_key: sk-primary
""",
        encoding="utf-8",
    )
    config = load_config(config_path)

    with pytest.raises(ConfigError) as exc:
        resolve_provider_config(config, {}, "missing")

    assert "missing" in str(exc.value)
    assert "sk-primary" not in str(exc.value)


def test_missing_api_key_error_does_not_include_secret(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text("provider:\n  openrouter_api_key: ''\n", encoding="utf-8")
    config = load_config(config_path)

    with pytest.raises(ConfigError) as exc:
        resolve_api_key(config, {})

    assert "OPENROUTER_API_KEY" in str(exc.value)
    assert "sk-" not in str(exc.value)


def test_model_param_precedence(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
model:
  name: global-model
  temperature: 0.7
skills:
  solve:
    model:
      name: skill-model
      max_tokens: 1000
""",
        encoding="utf-8",
    )
    config = load_config(config_path)

    resolved = resolve_model_params(
        config,
        "solve",
        cli_overrides=ModelParams(temperature=0.1),
    )

    assert resolved.name == "skill-model"
    assert resolved.temperature == 0.1
    assert resolved.max_tokens == 1000


def test_unknown_config_fields_fail(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text("unexpected: true\n", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(config_path)
