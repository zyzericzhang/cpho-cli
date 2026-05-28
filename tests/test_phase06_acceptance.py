from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from cpho_cli.core.index.storage import write_index
from cpho_cli.core.knowledge import (
    KnowledgeResolver,
    normalize_knowledge_file,
    publish_knowledge_draft,
)
from cpho_cli.core.skills import load_skill
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
)


def _write_vocab(workspace: Path) -> None:
    path = workspace / ".cpho" / "vocabulary" / "private.yml"
    path.parent.mkdir(parents=True)
    path.write_text(
        yaml.safe_dump(
            {
                "version": "phase06",
                "tags": [
                    {
                        "internal_id": "phase06_force_model",
                        "display_zh": "受力模型",
                        "category": "physics_model",
                    }
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _index_entry() -> IndexEntry:
    return IndexEntry(
        problem_id="phase06:01",
        problem_path=Path("芝麻物理第四届联考/第四届芝麻物理联考 (复赛) 理论试题.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime.now(timezone.utc),
        physics_model_tags=[
            TaggedReference(
                internal_id="phase06_force_model",
                source=TagSource.USER_NOTE,
            )
        ],
        fingerprint=IndexFingerprint(
            file=FileFingerprint(
                problem_sha256="b" * 64,
                answer_sha256=None,
                problem_size_bytes=1,
                answer_size_bytes=None,
                problem_mtime_ns=0,
            ),
            semantic=SemanticFingerprint(
                file_fp_hash="phase06-file",
                ocr_engine="rapidocr",
                ocr_engine_version="3.0",
                ocr_config_hash="phase06-ocr",
                tag_prompt_version="v1",
                split_prompt_version="v1",
                tag_schema_version="v2",
                model_name="openai/gpt-4o-mini",
                model_temperature=0.0,
                vocabulary_version="phase06",
            ),
        ),
        ocr_text_length=20,
        tag_prompt_version="v1",
    )


def test_phase06_private_kb_end_to_end_with_real_workspace_shape(tmp_path: Path) -> None:
    workspace = tmp_path / "物理竞赛资料"
    workspace.mkdir()
    _write_vocab(workspace)
    write_index(workspace / ".cpho" / "index.jsonl", [_index_entry()])
    source = workspace / "我的知识.md"
    source.write_text("受力模型：先明确研究对象，再写约束方程。", encoding="utf-8")

    draft = normalize_knowledge_file(
        workspace,
        source,
        canonical_tag_id="phase06_force_model",
        dry_run=True,
    )
    publish_knowledge_draft(workspace, draft)

    matches = KnowledgeResolver(workspace).find_for_problem("phase06:01")

    assert len(matches) == 1
    assert matches[0].canonical_tag_id == "phase06_force_model"
    assert "published" in matches[0].path.parts


def test_phase06_skill_pipeline_metadata_available_for_builtin_solve() -> None:
    loaded = load_skill(Path("src/cpho_cli/builtin_skills/solve"))

    description = loaded.spec.describe(loaded.root)

    assert description.name == "solve"
    assert all(step.prompt_path is not None for step in description.steps)
    assert {step.requires_multimodal for step in description.steps} == {False}
    assert any(edge.reason.startswith("input:") for edge in description.edges)
