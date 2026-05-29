from __future__ import annotations

from cpho_cli.models.config import StrictModel


class UpdateCheckResult(StrictModel):
    available: bool = False
    current_version: str
    latest_version: str | None = None
    release_url: str | None = None
    error: str | None = None
