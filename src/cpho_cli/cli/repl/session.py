"""SessionState and index metadata for the REPL session."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from cpho_cli.core.index import IndexNotFoundError
from cpho_cli.core.index.storage import load_index
from cpho_cli.models.config import AppConfig, StrictModel
from cpho_cli.models.llm import ModelCapabilities
from pydantic import ConfigDict

if TYPE_CHECKING:
    from cpho_cli.models.solve import SolveReport


class IndexMeta(StrictModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    problem_count: int
    tag_count: int
    index_mtime_ns: int
    index_version: str


@dataclass
class SessionState:
    workspace_path: Path
    config: AppConfig
    config_path: Path | None = None
    provider_name: str | None = None
    index_path: Path | None = None
    index_meta: IndexMeta | None = None
    last_search_query: str | None = None
    last_search_result_ids: list[str] = field(default_factory=list)
    current_problem_id: str | None = None
    current_solve_report: SolveReport | None = None
    max_results: int = 20
    output_format: str = "compact"
    out_dir: Path | None = None
    probe_max_rounds: int = 10
    model_capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    prompt_session: object | None = None


def load_index_meta(workspace_root: Path) -> IndexMeta | None:
    index_path = workspace_root / ".cpho" / "index.jsonl"
    if not index_path.exists():
        return None
    try:
        entries = load_index(workspace_root)
    except IndexNotFoundError:
        return None

    tag_ids = {
        ref.internal_id
        for entry in entries
        for ref in entry.physics_model_tags + entry.math_technique_tags + entry.heuristic_tags
    }
    index_version = "unknown"
    if entries:
        try:
            index_version = entries[0].fingerprint.semantic.tag_schema_version
        except AttributeError:
            index_version = "unknown"
    return IndexMeta(
        problem_count=len(entries),
        tag_count=len(tag_ids),
        index_mtime_ns=index_path.stat().st_mtime_ns,
        index_version=index_version,
    )


__all__ = ["SessionState", "IndexMeta", "load_index_meta"]
