from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SkillStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: str
    input_keys: list[str] = Field(default_factory=list)
    output_keys: list[str] = Field(default_factory=list)
    prompt_template: str | None = None
    depends_on: list[str] = Field(default_factory=list)


class SkillSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    steps: list[SkillStep] = Field(default_factory=list)

