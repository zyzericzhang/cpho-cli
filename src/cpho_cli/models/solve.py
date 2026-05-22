from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class NormalizedProblem(BaseModel):
    problem_id: str
    statement: str
    subproblems: list[str] = Field(default_factory=list)


class AnswerStructure(BaseModel):
    references: list[str]
    text: str


class DerivationStep(BaseModel):
    reasoning: str
    expression: str
    official_answer_refs: list[str]

    @field_validator("official_answer_refs")
    @classmethod
    def refs_required(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("DerivationStep requires at least one official answer reference.")
        return value


class Discrepancy(BaseModel):
    description: str
    likely_source: str
    official_answer_refs: list[str] = Field(default_factory=list)


class SolveReport(BaseModel):
    problem_id: str
    derivation_steps: list[DerivationStep]
    discrepancies: list[Discrepancy] = Field(default_factory=list)
    ocr_warnings: list[str] = Field(default_factory=list)
    physics_model_tags: list[str] = Field(default_factory=list)
    heuristic_insight_tags: list[str] = Field(default_factory=list)
    math_technique_tags: list[str] = Field(default_factory=list)


class SolveRunResult(BaseModel):
    report_json: Path | None
    report_markdown: Path | None = None
    warnings: list[str] = Field(default_factory=list)

