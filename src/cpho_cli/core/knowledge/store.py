from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from cpho_cli.core.index.vocabulary import load_merged_vocabulary
from cpho_cli.models.knowledge import KnowledgeDocument, KnowledgeFrontmatter, KnowledgeSource

TEXT_KNOWLEDGE_EXTENSIONS = {".md", ".markdown", ".tex", ".txt", ".rst"}


class KnowledgeError(ValueError):
    """Raised when a knowledge file is invalid."""


def _split_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise KnowledgeError(f"Knowledge file missing YAML frontmatter: {path}")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            raw = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :]).strip()
            try:
                data = yaml.safe_load(raw) or {}
            except yaml.YAMLError as exc:
                raise KnowledgeError(f"Invalid YAML frontmatter in {path}: {exc}") from exc
            if not isinstance(data, dict):
                raise KnowledgeError(f"Knowledge frontmatter must be a mapping: {path}")
            return data, body
    raise KnowledgeError(f"Knowledge file frontmatter is not closed with ---: {path}")


def _validate_canonical_tag(workspace_root: Path, frontmatter: KnowledgeFrontmatter, path: Path) -> None:
    vocabulary = load_merged_vocabulary(workspace_root)
    if frontmatter.canonical_tag_id not in vocabulary.tags:
        raise KnowledgeError(
            "Unknown canonical_tag_id in knowledge file "
            f"{path}: {frontmatter.canonical_tag_id}"
        )


def load_knowledge_document(
    workspace_root: Path,
    path: Path,
    *,
    source: KnowledgeSource = KnowledgeSource.PRIVATE,
    repo_name: str | None = None,
) -> KnowledgeDocument:
    if path.suffix.lower() not in TEXT_KNOWLEDGE_EXTENSIONS:
        raise KnowledgeError(f"Unsupported knowledge file type: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KnowledgeError(f"Knowledge file not found: {path}") from exc

    data, body = _split_frontmatter(text, path)
    try:
        frontmatter = KnowledgeFrontmatter.model_validate(data)
    except ValidationError as exc:
        raise KnowledgeError(f"Invalid knowledge frontmatter in {path}: {exc}") from exc
    _validate_canonical_tag(workspace_root, frontmatter, path)
    return KnowledgeDocument(
        path=path,
        frontmatter=frontmatter,
        body=body,
        source=source,
        repo_name=repo_name,
    )


def iter_private_knowledge_files(workspace_root: Path) -> list[Path]:
    roots = [
        workspace_root / ".cpho" / "knowledge" / "files",
        workspace_root / ".cpho" / "knowledge" / "files" / "published",
    ]
    files: dict[Path, None] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_KNOWLEDGE_EXTENSIONS:
                files[path] = None
    return sorted(files)
