from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class DocumentPage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    page_number: int
    embedded_text: str = ""
    image_bytes: bytes | None = None


class DocumentInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: Path
    pages: list[DocumentPage]


class ProblemFile(BaseModel):
    path: Path


class AnswerKeyFile(BaseModel):
    path: Path


class ProblemAnswerPair(BaseModel):
    problem: ProblemFile
    answer: AnswerKeyFile | None


class AmbiguousAnswerMatch(BaseModel):
    problem: ProblemFile
    candidates: list[AnswerKeyFile]


class WorkspaceDiscoveryResult(BaseModel):
    pairs: list[ProblemAnswerPair]
    unmatched_problems: list[ProblemFile]
    ambiguous: list[AmbiguousAnswerMatch]

