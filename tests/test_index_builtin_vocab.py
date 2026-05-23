from collections import Counter
from pathlib import Path

import yaml

from cpho_cli.core.index.vocabulary import load_merged_vocabulary, normalize_alias
from cpho_cli.models.index import TagCategory, TagLayer


def test_builtin_vocabulary_loads(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert 30 <= len(vocab.tags) <= 50


def test_builtin_vocabulary_has_required_anchors(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert {
        "newton_second_law",
        "momentum_conservation",
        "energy_conservation",
        "dimensional_analysis",
        "system_selection",
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

    assert counts[TagCategory.PHYSICS_MODEL] == 15
    assert counts[TagCategory.MATH_TECHNIQUE] == 12
    assert (
        counts[TagCategory.HEURISTIC]
        + counts[TagCategory.APPROXIMATION]
        + counts[TagCategory.SYSTEM_SELECTION]
        == 15
    )


def test_builtin_vocabulary_all_layer_builtin(tmp_path: Path) -> None:
    vocab = load_merged_vocabulary(tmp_path)

    assert all(tag.layer == TagLayer.BUILTIN for tag in vocab.tags.values())


def test_builtin_vocabulary_no_duplicate_internal_ids() -> None:
    path = Path("src/cpho_cli/vocabulary/builtin.yml")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    ids = [tag["internal_id"] for tag in raw["tags"]]

    assert len(ids) == len(set(ids))
