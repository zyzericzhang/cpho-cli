from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from cpho_cli.core.index import IndexNotFoundError
from cpho_cli.models.index import IndexEntry


def write_index(path: Path, entries: list[IndexEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(entry.model_dump_json() + "\n")
    tmp.replace(path)


def load_index(workspace_root: Path) -> list[IndexEntry]:
    path = workspace_root / ".cpho" / "index.jsonl"
    if not path.exists():
        raise IndexNotFoundError(f"Index not found: {path}")
    return [
        IndexEntry.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@dataclass(frozen=True)
class ExistingIndexForRebuild:
    entries: list[IndexEntry]
    stale_reason: str | None = None


def load_existing_index_for_rebuild(
    workspace_root: Path,
    expected_schema_version: str,
) -> ExistingIndexForRebuild:
    try:
        entries = load_index(workspace_root)
    except IndexNotFoundError:
        return ExistingIndexForRebuild(entries=[])
    except (ValidationError, json.JSONDecodeError, ValueError) as exc:
        return ExistingIndexForRebuild(
            entries=[],
            stale_reason=f"stale index schema: {exc.__class__.__name__}",
        )

    for entry in entries:
        if entry.fingerprint.semantic.tag_schema_version != expected_schema_version:
            return ExistingIndexForRebuild(
                entries=[],
                stale_reason=(
                    "stale index schema: "
                    f"{entry.fingerprint.semantic.tag_schema_version} != {expected_schema_version}"
                ),
            )
    return ExistingIndexForRebuild(entries=entries)
