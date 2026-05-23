from __future__ import annotations

from pathlib import Path

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
