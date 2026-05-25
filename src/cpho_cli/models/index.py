from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import Field, field_validator

from cpho_cli.models.config import StrictModel


class TagCategory(str, Enum):
    PHYSICS_LAW = "physics_law"
    PHYSICS_MODEL = "physics_model"
    MATH_TECHNIQUE = "math_technique"
    HEURISTIC = "heuristic"
    APPROXIMATION = "approximation"


class TagVisibility(str, Enum):
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class TagStatus(str, Enum):
    CANONICAL = "canonical"
    CANDIDATE = "candidate"
    DEPRECATED = "deprecated"


class TagLayer(str, Enum):
    BUILTIN = "builtin"
    WORKSPACE = "workspace"
    USER_PRIVATE = "user_private"


class TagSource(str, Enum):
    USER_NOTE = "user_note"
    QA_HISTORY = "qa_history"
    OCR_FALLBACK = "ocr_fallback"


class CanonicalTag(StrictModel):
    internal_id: str
    display_zh: str
    category: TagCategory
    aliases: list[str] = Field(default_factory=list)
    description: str | None = None
    status: TagStatus = TagStatus.CANONICAL
    visibility: TagVisibility = TagVisibility.PUBLIC
    layer: TagLayer = TagLayer.BUILTIN


class Vocabulary(StrictModel):
    version: str
    tags: dict[str, CanonicalTag]
    alias_index: dict[str, str]


class CandidateTag(StrictModel):
    internal_id_suggestion: str
    display_zh_suggestion: str
    category: TagCategory
    proposed_aliases: list[str] = Field(default_factory=list)
    rationale: str
    first_seen_problem_id: str
    first_seen_at: datetime
    occurrences: int = 1
    status: TagStatus = TagStatus.CANDIDATE


class FileFingerprint(StrictModel):
    problem_sha256: str
    answer_sha256: str | None
    problem_size_bytes: int
    answer_size_bytes: int | None
    problem_mtime_ns: int


class SemanticFingerprint(StrictModel):
    file_fp_hash: str
    ocr_engine: str
    ocr_engine_version: str
    ocr_config_hash: str
    tag_prompt_version: str
    split_prompt_version: str
    tag_schema_version: str
    model_name: str
    model_temperature: float
    vocabulary_version: str


class UserLearningFingerprint(StrictModel):
    notes_sha256: str | None = None
    user_tags_sha256: str | None = None
    qa_history_sha256: str | None = None


class IndexFingerprint(StrictModel):
    file: FileFingerprint
    semantic: SemanticFingerprint
    user_learning: UserLearningFingerprint = Field(default_factory=UserLearningFingerprint)


class TaggedReference(StrictModel):
    internal_id: str
    source: TagSource
    confidence: float | None = None


class UserTagEntry(StrictModel):
    tags: list[str] = Field(default_factory=list)
    canonical_tags: list[str] = Field(default_factory=list)
    unverified_tags: list[str] = Field(default_factory=list)
    skill_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reasoning_snippet: str


class UserNotebookEntry(StrictModel):
    problem_id: str
    key_points: list[str] = Field(default_factory=list)
    stuck_points: list[str] = Field(default_factory=list)
    free_text_notes: str = ""
    user_tags: list[str] = Field(default_factory=list)
    updated_at: datetime | None = None


class IndexEntry(StrictModel):
    problem_id: str
    problem_path: Path
    problem_page_range: tuple[int, int]
    answer_path: Path | None = None
    indexed_at: datetime
    physics_model_tags: list[TaggedReference] = Field(default_factory=list)
    math_technique_tags: list[TaggedReference] = Field(default_factory=list)
    heuristic_tags: list[TaggedReference] = Field(default_factory=list)
    difficulty_aspects: list[str] = Field(default_factory=list)
    user_confirmed_key_points: list[str] = Field(default_factory=list)
    user_confirmed_stuck_points: list[str] = Field(default_factory=list)
    user_tags: list[UserTagEntry] = Field(default_factory=list)
    fingerprint: IndexFingerprint
    ocr_cache_path: Path | None = None
    ocr_text_length: int
    tag_prompt_version: str
    topic_path: str | None = None

    @field_validator("problem_page_range")
    @classmethod
    def validate_problem_page_range(cls, value: tuple[int, int]) -> tuple[int, int]:
        start, end = value
        if start <= 0 or end <= 0:
            raise ValueError("problem_page_range must be 1-indexed")
        if end < start:
            raise ValueError("problem_page_range end must be >= start")
        return value


class IndexRunStats(StrictModel):
    total_problems: int = 0
    file_changed: int = 0
    file_unchanged: int = 0
    ocr_reused: int = 0
    ocr_regenerated: int = 0
    ocr_engine_upgrade_detected: bool = False
    tags_regenerated: int = 0
    tags_skipped: int = 0
    refinement_only: int = 0
    candidate_tags_proposed: int = 0
    pending_review_items: int = 0
    forced_regenerations: int = 0
    papers_split: int = 0
    problems_extracted: int = 0
    split_method_rules: int = 0
    split_method_llm: int = 0
    split_method_single: int = 0
