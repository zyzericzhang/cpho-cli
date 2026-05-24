from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModelParams(StrictModel):
    name: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


class ProviderConfig(StrictModel):
    openrouter_api_key: str | None = None
    base_url: str = "https://openrouter.ai/api/v1"


class ProviderProfile(StrictModel):
    kind: str = "openrouter"
    api_key: str | None = None
    api_key_env: str | None = None
    base_url: str | None = None
    default_model: str | None = None


class ResolvedProviderConfig(StrictModel):
    name: str
    kind: str
    api_key: str
    base_url: str


class SkillConfig(StrictModel):
    model: ModelParams | None = None


class AppConfig(StrictModel):
    active_provider: str = "openrouter"
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    providers: dict[str, ProviderProfile] = Field(default_factory=dict)
    model: ModelParams = Field(
        default_factory=lambda: ModelParams(name="openai/gpt-4o-mini", temperature=0.2)
    )
    skills: dict[str, SkillConfig] = Field(default_factory=dict)
