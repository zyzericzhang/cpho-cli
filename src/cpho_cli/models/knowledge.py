from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import ConfigDict, Field

from cpho_cli.models.config import StrictModel


class KnowledgeSource(str, Enum):
    PRIVATE = "private"
    COMMUNITY = "community"


class KnowledgeFrontmatter(StrictModel):
    model_config = ConfigDict(extra="allow")

    canonical_tag_id: str
    standardized: bool = False
    last_normalized_hash: str | None = None
    last_user_edit_hash: str | None = None
    title: str | None = None
    source: str | None = None
    tags: list[str] = Field(default_factory=list)
    summary: str | None = None


class KnowledgeDocument(StrictModel):
    path: Path
    frontmatter: KnowledgeFrontmatter
    body: str
    source: KnowledgeSource = KnowledgeSource.PRIVATE
    repo_name: str | None = None


class KnowledgeMatch(StrictModel):
    path: Path
    canonical_tag_id: str
    source: KnowledgeSource
    repo_name: str | None = None
    title: str | None = None
    excerpt: str = ""
    match_kind: str = "exact"
