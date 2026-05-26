from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field

from cpho_cli.models.config import StrictModel


class ExplainTone(str, Enum):
    TEACHER = "teacher"
    DENSE = "dense"
    BRIEF = "brief"

    @property
    def display_zh(self) -> str:
        return {
            ExplainTone.TEACHER: "老师型",
            ExplainTone.DENSE: "知识点密集型",
            ExplainTone.BRIEF: "简短型",
        }[self]


class ExplainStreamChunk(StrictModel):
    tone: ExplainTone
    text: str
    stage: str


class ToneExplainOutput(StrictModel):
    tone: ExplainTone
    stage_one_markdown: str
    sentence_markdown: str


class ExplainResult(StrictModel):
    problem_name: str
    tone_outputs: list[ToneExplainOutput]
    candidate_tags: list[str] = Field(default_factory=list)
    markdown_path: Path


__all__ = [
    "ExplainResult",
    "ExplainStreamChunk",
    "ExplainTone",
    "ToneExplainOutput",
]
