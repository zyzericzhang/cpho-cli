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


class OfficialAnswerStep(BaseModel):
    ref: str
    content: str


class AnswerStepCheck(BaseModel):
    official_answer_refs: list[str] = Field(default_factory=list)
    status: str
    finding: str


class SolveReport(BaseModel):
    problem_id: str
    official_steps: list[OfficialAnswerStep] = Field(default_factory=list)
    step_checks: list[AnswerStepCheck] = Field(default_factory=list)
    derivation_steps: list[DerivationStep] = Field(default_factory=list)
    discrepancies: list[Discrepancy] = Field(default_factory=list)
    ocr_warnings: list[str] = Field(default_factory=list)
    physics_model_tags: list[str] = Field(default_factory=list)
    heuristic_insight_tags: list[str] = Field(default_factory=list)
    math_technique_tags: list[str] = Field(default_factory=list)


class SolveRunResult(BaseModel):
    report_json: Path | None
    report_markdown: Path | None = None
    warnings: list[str] = Field(default_factory=list)
    report: SolveReport | None = None
