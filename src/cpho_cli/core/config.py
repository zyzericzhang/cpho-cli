from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from cpho_cli.core.errors import err_config_missing_api_key
from cpho_cli.core.llm import supported_provider_kinds
from cpho_cli.models.config import AppConfig, ModelParams, ProviderProfile, ResolvedProviderConfig


DEFAULT_CONFIG_FILENAMES = ("config.local.yml", "config.local.yaml")


class ConfigError(ValueError):
    """Raised when config cannot be loaded or resolved."""


def find_default_config_path(cwd: Path | None = None) -> Path | None:
    root = cwd or Path.cwd()
    for directory in (root, *root.parents):
        for filename in DEFAULT_CONFIG_FILENAMES:
            candidate = directory / filename
            if candidate.exists():
                return candidate
    return None


def load_config(path: Path | None) -> AppConfig:
    if path is None:
        path = find_default_config_path()
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
    return resolve_provider_config(config, env).api_key


def _legacy_openrouter_profile(config: AppConfig) -> ProviderProfile:
    return ProviderProfile(
        kind="openrouter",
        api_key=config.provider.openrouter_api_key,
        api_key_env="OPENROUTER_API_KEY",
        base_url=config.provider.base_url,
    )


def _provider_key(profile: ProviderProfile, env: Mapping[str, str]) -> str | None:
    if profile.api_key_env:
        return env.get(profile.api_key_env) or profile.api_key
    return profile.api_key


_DEFAULT_BASE_URLS: dict[str, str] = {
    "openrouter": "https://openrouter.ai/api/v1",
    "deepseek": "https://api.deepseek.com",
}


def resolve_provider_config(
    config: AppConfig,
    env: Mapping[str, str],
    provider_name: str | None = None,
) -> ResolvedProviderConfig:
    name = provider_name or config.active_provider
    profile = config.providers.get(name)
    legacy_profile = False
    if profile is None:
        if name != "openrouter":
            raise ConfigError(f"Unknown provider profile: {name}")
        profile = _legacy_openrouter_profile(config)
        legacy_profile = True

    kind = profile.kind
    if kind not in supported_provider_kinds():
        raise ConfigError(
            f"Unsupported provider kind for profile '{name}': {kind}. "
            f"Supported: {', '.join(sorted(supported_provider_kinds()))}"
        )

    api_key = _provider_key(profile, env)
    if not api_key:
        if legacy_profile:
            raise ConfigError(
                err_config_missing_api_key(
                    "openrouter",
                    "OPENROUTER_API_KEY or provider.openrouter_api_key",
                )
            )
        source = f"providers.{name}.api_key"
        if profile.api_key_env:
            source = f"{profile.api_key_env} or {source}"
        raise ConfigError(err_config_missing_api_key(name, source))

    base_url = profile.base_url or _DEFAULT_BASE_URLS.get(kind, config.provider.base_url)

    timeout = profile.timeout
    if timeout is None:
        timeout_str = env.get("LLM_TIMEOUT")
        timeout = float(timeout_str) if timeout_str and timeout_str.strip() else 120.0

    return ResolvedProviderConfig(
        name=name,
        kind=kind,
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
    )


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
    provider_name: str | None = None,
) -> ModelParams:
    params = config.model
    if provider_name:
        profile = config.providers.get(provider_name)
        if profile is not None and profile.default_model:
            params = _merge_params(params, ModelParams(name=profile.default_model))
    skill = config.skills.get(skill_name)
    if skill is not None:
        params = _merge_params(params, skill.model)
    return _merge_params(params, cli_overrides)
