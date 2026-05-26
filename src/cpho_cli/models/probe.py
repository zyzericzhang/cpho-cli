from __future__ import annotations

from pathlib import Path

from pydantic import Field

from cpho_cli.models.config import StrictModel


class ProbeTurn(StrictModel):
    question: str
    answer: str


class ProbeTranscript(StrictModel):
    problem_name: str
    turns: list[ProbeTurn] = Field(default_factory=list)
    markdown_path: Path


__all__ = ["ProbeTranscript", "ProbeTurn"]
