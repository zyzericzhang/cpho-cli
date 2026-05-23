"""Topic taxonomy 3-layer loader (builtin / workspace / private)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml
from pydantic import ValidationError

from cpho_cli.core.index import VocabularyError
from cpho_cli.models.topic import TopicNode, TopicTaxonomy


def _builtin_topic_path() -> Path:
    # core/index/topic_vocabulary.py -> cpho_cli/ -> vocabulary/topics/builtin_topics.yml
    return Path(__file__).resolve().parents[2] / "vocabulary" / "topics" / "builtin_topics.yml"


def _load_topic_yaml(path: Path, *, optional: bool = False) -> TopicTaxonomy | None:
    if not path.exists():
        if optional:
            return None
        raise VocabularyError(f"Topic taxonomy file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return TopicTaxonomy.model_validate(raw)
    except yaml.YAMLError as exc:
        raise VocabularyError(f"Invalid YAML at {path}: {exc}") from exc
    except ValidationError as exc:
        raise VocabularyError(f"Invalid topic taxonomy at {path}: {exc}") from exc


def _merge_nodes(base_node: TopicNode, override_node: TopicNode) -> TopicNode:
    """Merge override node into base node: override display_zh, recursively merge children."""
    base_children_by_id = {child.id: child for child in base_node.children}
    for override_child in override_node.children:
        if override_child.id in base_children_by_id:
            base_children_by_id[override_child.id] = _merge_nodes(
                base_children_by_id[override_child.id], override_child
            )
        else:
            base_children_by_id[override_child.id] = override_child
    return TopicNode(
        id=base_node.id,
        display_zh=override_node.display_zh,
        children=list(base_children_by_id.values()),
    )


def _merge_taxonomies(base: TopicTaxonomy, override: TopicTaxonomy | None) -> TopicTaxonomy:
    if override is None:
        return base
    base_roots_by_id = {root.id: root for root in base.roots}
    for override_root in override.roots:
        if override_root.id in base_roots_by_id:
            base_roots_by_id[override_root.id] = _merge_nodes(
                base_roots_by_id[override_root.id], override_root
            )
        else:
            base_roots_by_id[override_root.id] = override_root
    return TopicTaxonomy(
        version=f"{base.version}+{override.version}",
        roots=list(base_roots_by_id.values()),
    )


def _short_sha8(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def load_merged_topic_taxonomy(workspace_root: Path) -> TopicTaxonomy:
    """Load and merge topic taxonomy from builtin, workspace, and private layers."""
    builtin_path = _builtin_topic_path()
    builtin = _load_topic_yaml(builtin_path)
    assert builtin is not None  # non-optional, would have raised

    ws_path = workspace_root / ".cpho" / "topics" / "workspace_topics.yml"
    pv_path = workspace_root / ".cpho" / "topics" / "private_topics.yml"
    workspace = _load_topic_yaml(ws_path, optional=True)
    private = _load_topic_yaml(pv_path, optional=True)

    merged = _merge_taxonomies(builtin, workspace)
    merged = _merge_taxonomies(merged, private)

    bt_sha8 = _short_sha8(builtin_path) or "none"
    ws_sha8 = _short_sha8(ws_path) or "none"
    pv_sha8 = _short_sha8(pv_path) or "none"
    version = f"{builtin.version}+bt-{bt_sha8}+ws-{ws_sha8}+pv-{pv_sha8}"

    return TopicTaxonomy(version=version, roots=merged.roots)
