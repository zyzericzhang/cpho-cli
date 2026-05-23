from collections import Counter
from pathlib import Path

import yaml

from cpho_cli.core.index.vocabulary import load_merged_vocabulary, normalize_alias
from cpho_cli.models.index import TagCategory, TagLayer


def test_builtin_vocabulary_loads(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert len(vocab.tags) >= 800


def test_builtin_vocabulary_has_required_anchors(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert {
        "newton_second_law",
        "momentum_conservation",
        "energy_conservation",
        "dimensional_analysis",
        "system_selection",
        "fermat_principle",
        "pion_decay_kinematics",
        "image_charge_method",
    } <= set(vocab.tags)


def test_builtin_vocabulary_chinese_display_names(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert vocab.tags["newton_second_law"].display_zh == "牛顿第二定律"


def test_builtin_vocabulary_alias_index_resolves_aliases(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert vocab.alias_index[normalize_alias("F=ma")] == "newton_second_law"


def test_builtin_vocabulary_categories_have_expected_counts(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)
    counts = Counter(tag.category for tag in vocab.tags.values())

    assert counts[TagCategory.PHYSICS_LAW] >= 10
    assert counts[TagCategory.PHYSICS_MODEL] >= 4
    assert counts[TagCategory.MATH_TECHNIQUE] >= 12
    assert counts[TagCategory.HEURISTIC] >= 14
    assert counts[TagCategory.APPROXIMATION] >= 2


def test_builtin_vocabulary_all_layer_builtin(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert all(tag.layer == TagLayer.BUILTIN for tag in vocab.tags.values())


def test_builtin_vocabulary_no_duplicate_internal_ids() -> None:
    paths = [
        Path("src/cpho_cli/vocabulary/builtin.yml"),
        *sorted(Path("src/cpho_cli/vocabulary/builtin").glob("*.yml")),
    ]
    ids: list[str] = []
    for path in paths:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        file_ids = [tag["internal_id"] for tag in raw["tags"]]
        assert len(file_ids) == len(set(file_ids)), path
        ids.extend(file_ids)

    assert len(ids) >= len(set(ids))


def test_builtin_vocabulary_split_files_loaded(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert vocab.tags["fermat_principle"].category == TagCategory.PHYSICS_LAW
    assert vocab.tags["pion_decay_kinematics"].category == TagCategory.PHYSICS_MODEL
    assert vocab.tags["image_charge_method"].category == TagCategory.HEURISTIC
    assert vocab.tags["fermat_principle"].layer == TagLayer.BUILTIN
