from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from cpho_cli.core.index.storage import write_index
from cpho_cli.core.knowledge import KnowledgeError, KnowledgeResolver, load_knowledge_document
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TagSource,
    TaggedReference,
)
from cpho_cli.models.knowledge import KnowledgeSource


def _write_private_vocab(workspace: Path) -> None:
    path = workspace / ".cpho" / "vocabulary" / "private.yml"
    path.parent.mkdir(parents=True)
    path.write_text(
        yaml.safe_dump(
            {
                "version": "test",
                "tags": [
                    {
                        "internal_id": "test_model_a",
                        "display_zh": "测试模型 A",
                        "category": "physics_model",
                    },
                    {
                        "internal_id": "test_model_b",
                        "display_zh": "测试模型 B",
                        "category": "physics_model",
                    },
                    {
                        "internal_id": "test_math",
                        "display_zh": "测试数学",
                        "category": "math_technique",
                    },
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _fingerprint() -> IndexFingerprint:
    return IndexFingerprint(
        file=FileFingerprint(
            problem_sha256="a" * 64,
            answer_sha256=None,
            problem_size_bytes=1,
            answer_size_bytes=None,
            problem_mtime_ns=0,
        ),
        semantic=SemanticFingerprint(
            file_fp_hash="x",
            ocr_engine="rapidocr",
            ocr_engine_version="3.0",
            ocr_config_hash="y",
            tag_prompt_version="v1",
            split_prompt_version="v1",
            tag_schema_version="v2",
            model_name="m",
            model_temperature=0.0,
            vocabulary_version="test",
        ),
    )


def _entry(problem_id: str = "p1", tag_id: str = "test_model_a") -> IndexEntry:
    return IndexEntry(
        problem_id=problem_id,
        problem_path=Path("真实题目/第四届芝麻物理联考.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime.now(timezone.utc),
        physics_model_tags=[TaggedReference(internal_id=tag_id, source=TagSource.USER_NOTE)],
        fingerprint=_fingerprint(),
        ocr_text_length=12,
        tag_prompt_version="v1",
    )


def _write_knowledge(workspace: Path, name: str, tag_id: str) -> Path:
    path = workspace / ".cpho" / "knowledge" / "files" / "published" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                f"canonical_tag_id: {tag_id}",
                "standardized: true",
                "last_normalized_hash: abc",
                "last_user_edit_hash: def",
                "title: 测试知识",
                "---",
                "",
                "这里是用户自己的知识总结。",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_load_knowledge_document_validates_frontmatter(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    path = _write_knowledge(tmp_path, "model.md", "test_model_a")

    document = load_knowledge_document(tmp_path, path)

    assert document.frontmatter.canonical_tag_id == "test_model_a"
    assert document.frontmatter.standardized is True
    assert "知识总结" in document.body


def test_load_knowledge_document_rejects_missing_frontmatter(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    path = tmp_path / ".cpho" / "knowledge" / "files" / "bad.md"
    path.parent.mkdir(parents=True)
    path.write_text("no frontmatter", encoding="utf-8")

    with pytest.raises(KnowledgeError, match="missing YAML frontmatter"):
        load_knowledge_document(tmp_path, path)


def test_load_knowledge_document_rejects_unknown_canonical_tag(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    path = _write_knowledge(tmp_path, "bad.md", "missing_tag")

    with pytest.raises(KnowledgeError, match="Unknown canonical_tag_id"):
        load_knowledge_document(tmp_path, path)


def test_resolver_finds_private_exact_match_for_problem(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    write_index(tmp_path / ".cpho" / "index.jsonl", [_entry()])
    path = _write_knowledge(tmp_path, "model.md", "test_model_a")

    matches = KnowledgeResolver(tmp_path).find_for_problem("p1")

    assert len(matches) == 1
    assert matches[0].path == path
    assert matches[0].source is KnowledgeSource.PRIVATE
    assert matches[0].match_kind == "exact"


def test_resolver_falls_back_to_same_category(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    write_index(tmp_path / ".cpho" / "index.jsonl", [_entry()])
    _write_knowledge(tmp_path, "model-b.md", "test_model_b")
    _write_knowledge(tmp_path, "math.md", "test_math")

    matches = KnowledgeResolver(tmp_path).find_for_problem("p1")

    assert [match.canonical_tag_id for match in matches] == ["test_model_b"]
    assert matches[0].match_kind == "same_category"
