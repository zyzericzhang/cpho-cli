from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpho_cli.core.index import VocabularyError
from cpho_cli.core.index.vocabulary import (
    _build_alias_index,
    list_pending_candidates,
    load_merged_vocabulary,
    load_yaml_vocab,
    normalize_alias,
)
from cpho_cli.models.index import (
    CandidateTag,
    CanonicalTag,
    TagCategory,
    TagLayer,
    Vocabulary,
)


def _write_vocab(path: Path, display_zh: str, layer: str = "builtin") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""
version: "v0.1"
tags:
  - internal_id: newton_second_law
    display_zh: {display_zh}
    category: physics_model
    aliases: ["F=ma", "Newton 第二"]
    layer: {layer}
""",
        encoding="utf-8",
    )


def test_normalize_alias_nfkc_full_width() -> None:
    assert normalize_alias("Ｆ＝ｍａ") == normalize_alias("f=ma")


def test_normalize_alias_chinese_punctuation_stripped() -> None:
    assert normalize_alias("牛顿 第二（定律）") == normalize_alias("牛顿第二定律")


def test_alias_index_maps_aliases_to_internal_id() -> None:
    vocab = Vocabulary(
        version="v0.1",
        tags={
            "newton_second_law": CanonicalTag(
                internal_id="newton_second_law",
                display_zh="牛顿第二定律",
                category=TagCategory.PHYSICS_MODEL,
                aliases=["F=ma", "Newton 第二"],
            )
        },
        alias_index={},
    )
    alias_index = _build_alias_index(vocab.tags)

    assert alias_index[normalize_alias("Newton 第二")] == "newton_second_law"


def test_workspace_layer_overrides_builtin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    builtin = tmp_path / "builtin.yml"
    workspace = tmp_path / ".cpho" / "vocabulary" / "workspace.yml"
    _write_vocab(builtin, "牛顿第二")
    _write_vocab(workspace, "牛顿第二（自定义）", layer="workspace")
    monkeypatch.setattr("cpho_cli.core.index.vocabulary._builtin_vocab_path", lambda: builtin)

    vocab = load_merged_vocabulary(tmp_path)

    assert vocab.tags["newton_second_law"].display_zh == "牛顿第二（自定义）"
    assert vocab.tags["newton_second_law"].layer == TagLayer.WORKSPACE


def test_private_layer_overrides_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    builtin = tmp_path / "builtin.yml"
    workspace = tmp_path / ".cpho" / "vocabulary" / "workspace.yml"
    private = tmp_path / ".cpho" / "vocabulary" / "private.yml"
    _write_vocab(builtin, "牛顿第二")
    _write_vocab(workspace, "牛顿第二（团队）", layer="workspace")
    _write_vocab(private, "牛顿第二（个人）", layer="user_private")
    monkeypatch.setattr("cpho_cli.core.index.vocabulary._builtin_vocab_path", lambda: builtin)

    vocab = load_merged_vocabulary(tmp_path)

    assert vocab.tags["newton_second_law"].display_zh == "牛顿第二（个人）"
    assert vocab.tags["newton_second_law"].layer == TagLayer.USER_PRIVATE


def test_optional_layers_missing_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    builtin = tmp_path / "builtin.yml"
    _write_vocab(builtin, "牛顿第二")
    monkeypatch.setattr("cpho_cli.core.index.vocabulary._builtin_vocab_path", lambda: builtin)

    vocab = load_merged_vocabulary(tmp_path)

    assert "newton_second_law" in vocab.tags
    assert "ws-none+pv-none" in vocab.version


def test_load_yaml_vocab_invalid_yaml_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.yml"
    path.write_text("tags: [", encoding="utf-8")

    with pytest.raises(VocabularyError):
        load_yaml_vocab(path, layer=TagLayer.BUILTIN)


def test_load_yaml_vocab_unknown_field_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.yml"
    path.write_text(
        """
version: "v0.1"
tags:
  - internal_id: newton_second_law
    display_zh: 牛顿第二定律
    category: physics_model
    foobar: 1
""",
        encoding="utf-8",
    )

    with pytest.raises(VocabularyError):
        load_yaml_vocab(path, layer=TagLayer.BUILTIN)


def test_layer_attribute_forced_on_load(tmp_path: Path) -> None:
    path = tmp_path / "workspace.yml"
    _write_vocab(path, "牛顿第二", layer="builtin")

    vocab = load_yaml_vocab(path, layer=TagLayer.WORKSPACE)

    assert vocab is not None
    assert vocab.tags["newton_second_law"].layer == TagLayer.WORKSPACE


def test_list_pending_candidates_empty_when_missing(tmp_path: Path) -> None:
    assert list_pending_candidates(tmp_path) == []


def test_list_pending_candidates_loads_yaml(tmp_path: Path) -> None:
    path = tmp_path / ".cpho" / "vocabulary" / "pending.yml"
    path.parent.mkdir(parents=True)
    candidate = CandidateTag(
        internal_id_suggestion="energy_method",
        display_zh_suggestion="能量法",
        category=TagCategory.HEURISTIC,
        rationale="题目需要用能量守恒处理。",
        first_seen_problem_id="p1",
        first_seen_at=datetime.now(timezone.utc),
    )
    path.write_text(candidate.model_dump_json(), encoding="utf-8")

    with pytest.raises(VocabularyError):
        list_pending_candidates(tmp_path)
