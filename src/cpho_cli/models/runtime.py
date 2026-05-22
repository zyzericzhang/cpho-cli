from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class TraceRecord(BaseModel):
    step_id: str
    status: Literal["passed", "failed"]
    input_keys: list[str]
    output_keys: list[str]
    retry_count: int = 0
    started_at: datetime
    finished_at: datetime
    error: str | None = None


class CheckpointRecord(BaseModel):
    failed_step_id: str
    blackboard_keys: list[str]
    error: str


class ResumeState(BaseModel):
    failed_step_id: str
    blackboard: dict[str, Any] = Field(default_factory=dict)


class SkillRunResult(BaseModel):
    blackboard: dict[str, Any]
    step_statuses: dict[str, str]

