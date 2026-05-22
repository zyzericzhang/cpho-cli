from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from cpho_cli.models.config import AppConfig, ModelParams


class ConfigError(ValueError):
    """Raised when config cannot be loaded or resolved."""


def load_config(path: Path | None) -> AppConfig:
    if path is None:
        return AppConfig()
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Config file not found: {path}") from exc
    try:
        raw = yaml.safe_load(raw_text) or {}
        if not isinstance(raw, dict):
            raise ConfigError("Config file must contain a YAML mapping.")
        return AppConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"Invalid config: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML config: {exc}") from exc


def resolve_api_key(config: AppConfig, env: Mapping[str, str]) -> str:
    key = env.get("OPENROUTER_API_KEY") or config.provider.openrouter_api_key
    if not key:
        raise ConfigError(
            "OpenRouter API key missing. Set OPENROUTER_API_KEY or provider.openrouter_api_key "
            "in a local gitignored config file."
        )
    return key


def _merge_params(base: ModelParams, override: ModelParams | None) -> ModelParams:
    if override is None:
        return base
    data: dict[str, Any] = base.model_dump()
    for key, value in override.model_dump(exclude_none=True).items():
        data[key] = value
    return ModelParams.model_validate(data)


def resolve_model_params(
    config: AppConfig,
    skill_name: str,
    cli_overrides: ModelParams | None = None,
) -> ModelParams:
    params = config.model
    skill = config.skills.get(skill_name)
    if skill is not None:
        params = _merge_params(params, skill.model)
    return _merge_params(params, cli_overrides)

