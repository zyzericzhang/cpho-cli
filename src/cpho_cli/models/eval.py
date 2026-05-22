from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvalCriterion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    area: str
    priority: str
    expectation: str


class EvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    problem: Path
    answer: Path
    criteria: list[EvalCriterion]
    expectation_markdown: Path | None = None
    known_failure_modes: list[str] = Field(default_factory=list)

    @field_validator("criteria")
    @classmethod
    def criteria_required(cls, value: list[EvalCriterion]) -> list[EvalCriterion]:
        if not value:
            raise ValueError("At least one criterion is required.")
        return value


class EvalRunResult(BaseModel):
    total: int
    passed: int
    failed: int
    skipped: int
    report_json: Path
    report_markdown: Path

