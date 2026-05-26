from __future__ import annotations

import hashlib
import re
from pathlib import Path

from cpho_cli.cli.repl.persistence import data_dir

_UNSAFE_FILENAME_CHARS = re.compile(r"[\\/:*?\"<>|\x00-\x1f]")


def workspace_hash(workspace_path: Path) -> str:
    resolved = str(workspace_path.expanduser().resolve())
    return hashlib.sha256(resolved.encode("utf-8")).hexdigest()[:12]


def safe_problem_filename(problem_id_or_title: str, suffix: str) -> str:
    stem = _UNSAFE_FILENAME_CHARS.sub("_", problem_id_or_title).strip()
    stem = stem.strip(".")
    if not stem:
        stem = "problem"
    if not suffix.startswith("."):
        suffix = "." + suffix
    return stem if stem.endswith(suffix) else stem + suffix


def default_markdown_path(
    workspace_path: Path,
    skill_name: str,
    problem_name: str,
    *,
    override_dir: Path | None = None,
) -> Path:
    filename = safe_problem_filename(problem_name, ".md")
    if override_dir is not None:
        return override_dir.expanduser() / skill_name / filename
    return data_dir() / "outputs" / workspace_hash(workspace_path) / skill_name / filename


def write_markdown_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def append_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


__all__ = [
    "append_markdown",
    "default_markdown_path",
    "safe_problem_filename",
    "workspace_hash",
    "write_markdown_atomic",
]
