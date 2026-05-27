from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml
from typer.testing import CliRunner

from cpho_cli.cli.app import app
from cpho_cli.core.index.storage import write_index
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
)


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
                    }
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _entry() -> IndexEntry:
    return IndexEntry(
        problem_id="p1",
        problem_path=Path("真实题目/第四届芝麻物理联考.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime.now(timezone.utc),
        physics_model_tags=[
            TaggedReference(internal_id="test_model_a", source=TagSource.USER_NOTE)
        ],
        fingerprint=IndexFingerprint(
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
        ),
        ocr_text_length=12,
        tag_prompt_version="v1",
    )


def test_knowledge_normalize_publish_find_cli(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    source = tmp_path / "知识.md"
    source.write_text("受力模型：先选研究对象。", encoding="utf-8")
    runner = CliRunner()

    normalize = runner.invoke(
        app,
        [
            "knowledge",
            "normalize",
            str(source),
            "--workspace",
            str(tmp_path),
            "--canonical-tag-id",
            "test_model_a",
            "--dry-run",
        ],
    )

    assert normalize.exit_code == 0
    draft = Path(normalize.output.strip().removeprefix("草稿: "))
    assert draft.exists()

    publish = runner.invoke(
        app,
        ["knowledge", "publish", str(draft), "--workspace", str(tmp_path)],
    )

    assert publish.exit_code == 0
    assert "已发布" in publish.output
    write_index(tmp_path / ".cpho" / "index.jsonl", [_entry()])

    find = runner.invoke(app, ["knowledge", "find", "p1", "--workspace", str(tmp_path)])

    assert find.exit_code == 0
    assert "test_model_a" in find.output
    assert "published" in find.output
