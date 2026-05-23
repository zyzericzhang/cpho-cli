from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.core.index import VocabularyError
from cpho_cli.core.index.topic_vocabulary import load_merged_topic_taxonomy


def test_builtin_topic_taxonomy_loads(tmp_path: Path) -> None:
    taxonomy = load_merged_topic_taxonomy(tmp_path)
    assert len(taxonomy.roots) > 0
    assert taxonomy.roots[0].display_zh == "力学"


def test_workspace_topic_override_adds_child(tmp_path: Path) -> None:
    ws_dir = tmp_path / ".cpho" / "topics"
    ws_dir.mkdir(parents=True)
    (ws_dir / "workspace_topics.yml").write_text(
        'version: "ws"\n'
        "roots:\n"
        "  - id: mechanics\n"
        "    display_zh: 力学\n"
        "    children:\n"
        "      - id: new_child\n"
        "        display_zh: 新分支\n"
        "        children: []\n",
        encoding="utf-8",
    )
    taxonomy = load_merged_topic_taxonomy(tmp_path)
    mechanics = next(r for r in taxonomy.roots if r.id == "mechanics")
    child_ids = {c.id for c in mechanics.children}
    assert "new_child" in child_ids
    # Original children should still be present
    assert "kinematics" in child_ids


def test_workspace_topic_override_replaces_display_zh(tmp_path: Path) -> None:
    ws_dir = tmp_path / ".cpho" / "topics"
    ws_dir.mkdir(parents=True)
    (ws_dir / "workspace_topics.yml").write_text(
        'version: "ws"\n'
        "roots:\n"
        "  - id: mechanics\n"
        "    display_zh: Mechanics\n"
        "    children: []\n",
        encoding="utf-8",
    )
    taxonomy = load_merged_topic_taxonomy(tmp_path)
    mechanics = next(r for r in taxonomy.roots if r.id == "mechanics")
    assert mechanics.display_zh == "Mechanics"


def test_missing_builtin_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "cpho_cli.core.index.topic_vocabulary._builtin_topic_path",
        lambda: Path("/nonexistent/topics.yml"),
    )
    with pytest.raises(VocabularyError):
        load_merged_topic_taxonomy(Path("/tmp/fake"))


def test_invalid_yaml_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bad_file = tmp_path / "bad_topics.yml"
    bad_file.write_text("{{invalid yaml", encoding="utf-8")
    monkeypatch.setattr(
        "cpho_cli.core.index.topic_vocabulary._builtin_topic_path",
        lambda: bad_file,
    )
    with pytest.raises(VocabularyError):
        load_merged_topic_taxonomy(tmp_path)


def test_version_string_format(tmp_path: Path) -> None:
    taxonomy = load_merged_topic_taxonomy(tmp_path)
    assert "v0.1" in taxonomy.version
    assert "+ws-" in taxonomy.version
    assert "+pv-" in taxonomy.version
