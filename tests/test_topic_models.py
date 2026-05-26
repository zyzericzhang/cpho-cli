from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    UserLearningFingerprint,
)
from cpho_cli.models.topic import TopicNode, TopicTaxonomy


def _stub_fingerprint() -> IndexFingerprint:
    return IndexFingerprint(
        file=FileFingerprint(
            problem_sha256="a" * 64,
            answer_sha256=None,
            problem_size_bytes=100,
            answer_size_bytes=None,
            problem_mtime_ns=0,
        ),
        semantic=SemanticFingerprint(
            file_fp_hash="a" * 16,
            ocr_engine="rapidocr",
            ocr_engine_version="3.0",
            ocr_config_hash="c" * 64,
            tag_prompt_version="v0.1",
            split_prompt_version="v1",
            tag_schema_version="v1",
            model_name="test",
            model_temperature=0.0,
            vocabulary_version="v0.1",
        ),
        user_learning=UserLearningFingerprint(),
    )


def _small_taxonomy() -> TopicTaxonomy:
    return TopicTaxonomy(
        version="test",
        roots=[
            TopicNode(
                id="mechanics",
                display_zh="力学",
                children=[
                    TopicNode(id="kinematics", display_zh="运动学"),
                ],
            ),
            TopicNode(
                id="thermodynamics",
                display_zh="热学",
                children=[
                    TopicNode(id="gas_laws", display_zh="气体定律"),
                ],
            ),
        ],
    )


def test_topic_node_round_trip() -> None:
    node = TopicNode(
        id="mechanics",
        display_zh="力学",
        children=[TopicNode(id="kinematics", display_zh="运动学")],
    )
    json_str = node.model_dump_json()
    restored = TopicNode.model_validate_json(json_str)
    assert restored == node
    assert len(restored.children) == 1
    assert restored.children[0].display_zh == "运动学"


def test_topic_node_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TopicNode(id="x", display_zh="X", unknown_field="bad")  # type: ignore[call-arg]


def test_topic_taxonomy_flatten_paths() -> None:
    taxonomy = _small_taxonomy()
    paths = taxonomy.flatten_paths()
    assert paths == ["力学", "力学/运动学", "热学", "热学/气体定律"]


def test_topic_taxonomy_find_node_by_path() -> None:
    taxonomy = _small_taxonomy()
    node = taxonomy.find_node_by_path("力学/运动学")
    assert node is not None
    assert node.id == "kinematics"

    assert taxonomy.find_node_by_path("不存在") is None
    assert taxonomy.find_node_by_path("力学/不存在") is None


def test_index_entry_topic_path_default_none() -> None:
    entry = IndexEntry(
        problem_id="p1",
        problem_path=Path("p1.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        fingerprint=_stub_fingerprint(),
        ocr_text_length=100,
        tag_prompt_version="v0.1",
    )
    assert entry.topic_path is None


def test_index_entry_topic_path_round_trip() -> None:
    entry = IndexEntry(
        problem_id="p1",
        problem_path=Path("p1.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        fingerprint=_stub_fingerprint(),
        ocr_text_length=100,
        tag_prompt_version="v0.1",
        topic_path="力学/天体运动/轨道理论",
    )
    json_str = entry.model_dump_json()
    restored = IndexEntry.model_validate_json(json_str)
    assert restored.topic_path == "力学/天体运动/轨道理论"
