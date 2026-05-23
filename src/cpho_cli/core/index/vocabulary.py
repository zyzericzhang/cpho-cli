from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from cpho_cli.core.index import VocabularyError
from cpho_cli.models.index import CandidateTag, CanonicalTag, TagLayer, Vocabulary

"""Vocabulary loading for builtin, workspace, and gitignored .cpho private layers."""


def _builtin_vocab_path() -> Path:
    # core/index/vocabulary.py -> cpho_cli/ -> vocabulary/builtin.yml
    return Path(__file__).resolve().parents[2] / "vocabulary" / "builtin.yml"


def _builtin_vocab_paths() -> list[Path]:
    root = _builtin_vocab_path().parent
    paths = [_builtin_vocab_path()]
    paths.extend(sorted((root / "builtin").glob("*.yml")))
    return paths


def normalize_alias(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.casefold()
    text = re.sub(r"[\s\-_.,;:'\"()（）「」]+", "", text)
    return text


def _load_yaml_vocab_raw(path: Path, optional: bool, layer: TagLayer) -> Vocabulary | None:
    if not path.exists():
        if optional:
            return None
        raise VocabularyError(f"Vocabulary file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            raise VocabularyError(f"Vocabulary file must contain a YAML mapping: {path}")
        raw_tags = raw.get("tags", [])
        if not isinstance(raw_tags, list):
            raise VocabularyError(f"Vocabulary tags must be a YAML list: {path}")

        tags: dict[str, CanonicalTag] = {}
        for tag_raw in raw_tags:
            if not isinstance(tag_raw, dict):
                raise VocabularyError(f"Vocabulary tag must be a YAML mapping: {path}")
            tag_data: dict[str, Any] = dict(tag_raw)
            tag_data["layer"] = layer
            tag = CanonicalTag.model_validate(tag_data)
            tags[tag.internal_id] = tag

        return Vocabulary.model_validate(
            {"version": raw.get("version", "v0.1"), "tags": tags, "alias_index": {}}
        )
    except yaml.YAMLError as exc:
        raise VocabularyError(f"Invalid YAML at {path}: {exc}") from exc
    except ValidationError as exc:
        raise VocabularyError(f"Invalid vocabulary at {path}: {exc}") from exc
    except OSError as exc:
        raise VocabularyError(f"Vocabulary file not found: {path}") from exc


def load_yaml_vocab(path: Path, layer: TagLayer, optional: bool = False) -> Vocabulary | None:
    return _load_yaml_vocab_raw(path, optional=optional, layer=layer)


def _build_alias_index(tags: dict[str, CanonicalTag]) -> dict[str, str]:
    index: dict[str, str] = {}
    for tag in tags.values():
        for label in [tag.internal_id, tag.display_zh, *tag.aliases]:
            index[normalize_alias(label)] = tag.internal_id
    return index


def _short_sha8(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def load_merged_vocabulary(workspace_root: Path) -> Vocabulary:
    builtin_layers = [
        vocab
        for vocab in (
            load_yaml_vocab(path, layer=TagLayer.BUILTIN, optional=False)
            for path in _builtin_vocab_paths()
        )
        if vocab is not None
    ]
    if not builtin_layers:
        raise VocabularyError("Builtin vocabulary unexpectedly missing.")

    workspace_path = workspace_root / ".cpho" / "vocabulary" / "workspace.yml"
    private_path = workspace_root / ".cpho" / "vocabulary" / "private.yml"
    workspace = load_yaml_vocab(workspace_path, layer=TagLayer.WORKSPACE, optional=True)
    private = load_yaml_vocab(private_path, layer=TagLayer.USER_PRIVATE, optional=True)

    merged: dict[str, CanonicalTag] = {}
    for vocabulary in [*builtin_layers, workspace, private]:
        if vocabulary is None:
            continue
        for tag in vocabulary.tags.values():
            merged[tag.internal_id] = tag

    builtin_hash = hashlib.sha256()
    for path in _builtin_vocab_paths():
        builtin_hash.update(path.name.encode("utf-8"))
        builtin_hash.update(path.read_bytes())
    builtin_version = f"{builtin_layers[0].version}+bt-{builtin_hash.hexdigest()[:8]}"
    version = (
        f"{builtin_version}+ws-{_short_sha8(workspace_path) or 'none'}"
        f"+pv-{_short_sha8(private_path) or 'none'}"
    )
    return Vocabulary(version=version, tags=merged, alias_index=_build_alias_index(merged))


def list_pending_candidates(workspace_root: Path) -> list[CandidateTag]:
    path = workspace_root / ".cpho" / "vocabulary" / "pending.yml"
    if not path.exists():
        return []
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if not isinstance(raw, list):
            raise VocabularyError(f"Pending candidates must be a YAML list: {path}")
        return [CandidateTag.model_validate(item) for item in raw]
    except yaml.YAMLError as exc:
        raise VocabularyError(f"Invalid YAML at {path}: {exc}") from exc
    except ValidationError as exc:
        raise VocabularyError(f"Invalid pending candidates at {path}: {exc}") from exc
    except OSError as exc:
        raise VocabularyError(f"Pending candidates file not found: {path}") from exc
