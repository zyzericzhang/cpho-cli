from pathlib import Path

import pytest

from cpho_cli.core.config import ConfigError, load_config, resolve_api_key, resolve_model_params
from cpho_cli.models.config import ModelParams


def test_resolve_api_key_from_environment() -> None:
    config = load_config(None)

    assert resolve_api_key(config, {"OPENROUTER_API_KEY": "sk-test"}) == "sk-test"


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

