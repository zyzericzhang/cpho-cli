from __future__ import annotations

from pathlib import Path

from pydantic import Field

from cpho_cli.models.config import StrictModel


class CommunityRepositoryConfig(StrictModel):
    url: str
    tag: str
    enabled: bool = True


class CommunitySyncConfig(StrictModel):
    repositories: list[CommunityRepositoryConfig] = Field(default_factory=list)
    github_token: str | None = None


class CommunityRepositoryResult(StrictModel):
    repo_name: str
    tag: str
    cache_dir: Path
    metadata_path: Path
    files_written: int = 0
    skipped: bool = False


class CommunitySyncResult(StrictModel):
    repositories: list[CommunityRepositoryResult] = Field(default_factory=list)

