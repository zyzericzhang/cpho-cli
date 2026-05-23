"""Topic query API: find problems by topic prefix, get topic tree."""

from __future__ import annotations

from pathlib import Path

from cpho_cli.core.index.storage import load_index
from cpho_cli.core.index.topic_vocabulary import load_merged_topic_taxonomy
from cpho_cli.models.index import IndexEntry
from cpho_cli.models.topic import TopicTaxonomy


def find_problems_by_topic(workspace_root: Path, topic_path: str) -> list[IndexEntry]:
    """Return entries whose topic_path matches or is a descendant of the given path."""
    entries = load_index(workspace_root)
    return [
        e
        for e in entries
        if e.topic_path is not None
        and (e.topic_path == topic_path or e.topic_path.startswith(topic_path + "/"))
    ]


def get_topic_tree(workspace_root: Path) -> TopicTaxonomy:
    """Return the merged topic taxonomy for the workspace."""
    return load_merged_topic_taxonomy(workspace_root)
