from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LLMUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class LLMResponse(BaseModel):
    content: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    raw: dict[str, Any] = Field(default_factory=dict)

