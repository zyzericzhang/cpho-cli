"""User-notebook data layer: get/set notes per problem (Phase 2 data model only, no editor UX)."""

from __future__ import annotations

import re
from pathlib import Path

from cpho_cli.core.index import IndexBuildError
from cpho_cli.models.index import UserNotebookEntry

PROBLEM_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")


def _validate_problem_id(problem_id: str) -> None:
    if not PROBLEM_ID_PATTERN.fullmatch(problem_id):
        raise IndexBuildError(
            f"Invalid problem_id (contains forbidden characters): {problem_id!r}"
        )


def _notebook_path(workspace_root: Path, problem_id: str) -> Path:
    _validate_problem_id(problem_id)
    return workspace_root / ".cpho" / "notebook" / f"{problem_id}.json"


def get_problem_notes(workspace_root: Path, problem_id: str) -> UserNotebookEntry | None:
    path = _notebook_path(workspace_root, problem_id)
    if not path.exists():
        return None
    return UserNotebookEntry.model_validate_json(path.read_text(encoding="utf-8"))


def set_problem_notes(workspace_root: Path, notes: UserNotebookEntry) -> None:
    path = _notebook_path(workspace_root, notes.problem_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(notes.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(path)
