from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cpho_cli.models.config import StrictModel


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


class PaperKind(str, Enum):
    PROBLEM = "problem"
    ANSWER = "answer"


class SplitMethod(str, Enum):
    RULES = "rules"
    LLM = "llm"
    SINGLE = "single"


def make_problem_id(paper_sha256: str, problem_number: int) -> str:
    if problem_number <= 0:
        raise ValueError("problem_number must be positive")
    return f"{paper_sha256}:{problem_number:02d}"


class PaperFile(StrictModel):
    path: Path
    paper_kind: PaperKind
    total_pages: int = Field(gt=0)


class PaperAnswerPair(StrictModel):
    paper: PaperFile
    answer: PaperFile | None

    @property
    def problem(self) -> PaperFile:
        return self.paper


class AmbiguousPaperMatch(StrictModel):
    paper: PaperFile
    candidates: list[PaperFile]

    @property
    def problem(self) -> PaperFile:
        return self.paper


def _validate_page_range(value: tuple[int, int]) -> tuple[int, int]:
    start, end = value
    if start <= 0 or end <= 0:
        raise ValueError("page range must be 1-indexed")
    if end < start:
        raise ValueError("page range end must be >= start")
    return value


class ProblemEntry(StrictModel):
    problem_id: str
    paper_path: Path
    problem_number: int = Field(gt=0)
    problem_page_range: tuple[int, int]
    problem_text: str
    answer_paper_path: Path | None = None
    answer_page_range: tuple[int, int] | None = None
    answer_text: str | None = None
    split_method: SplitMethod
    split_confidence: float = Field(ge=0, le=1)

    @field_validator("problem_page_range")
    @classmethod
    def validate_problem_page_range(cls, value: tuple[int, int]) -> tuple[int, int]:
        return _validate_page_range(value)

    @field_validator("answer_page_range")
    @classmethod
    def validate_answer_page_range(cls, value: tuple[int, int] | None) -> tuple[int, int] | None:
        if value is None:
            return value
        return _validate_page_range(value)

    @field_validator("problem_text")
    @classmethod
    def validate_problem_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("problem_text must not be empty")
        return value


class SplitOutcome(StrictModel):
    problems: list[ProblemEntry]
    unmatched_answers: list[ProblemEntry] = Field(default_factory=list)
    split_method: SplitMethod
    split_confidence: float = Field(ge=0, le=1)
    diagnostics: list[str] = Field(default_factory=list)


class ProblemAnswerPair(BaseModel):
    problem: ProblemFile
    answer: AnswerKeyFile | None


class AmbiguousAnswerMatch(BaseModel):
    problem: ProblemFile
    candidates: list[AnswerKeyFile]


class WorkspaceDiscoveryResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pairs: list[ProblemAnswerPair | PaperAnswerPair]
    unmatched_papers: list[ProblemFile | PaperFile] = Field(alias="unmatched_problems")
    ambiguous: list[AmbiguousAnswerMatch | AmbiguousPaperMatch]

    @property
    def unmatched_problems(self) -> list[ProblemFile | PaperFile]:
        return self.unmatched_papers
