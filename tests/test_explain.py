from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from cpho_cli.core.explain import run_explain
from cpho_cli.core.index.storage import write_index
from cpho_cli.core.knowledge import normalize_knowledge_file, publish_knowledge_draft
from cpho_cli.models.config import ModelParams
from cpho_cli.models.explain import ExplainPanel
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
)
from cpho_cli.models.llm import LLMResponse
from cpho_cli.models.solve import Discrepancy, SolveReport


class FakeExplainProvider:
    def __init__(self) -> None:
        self.stream_messages: list[str] = []
        self.complete_messages: list[str] = []

    def stream(self, messages, params: ModelParams):  # type: ignore[no-untyped-def]
        content = str(messages[-1]["content"])
        self.stream_messages.append(content)
        if "思路描述" in content:
            yield "## 思路描述\n先看受力模型。"
        elif "标答替换" in content:
            yield "## 标答替换\n补全答案跳步。"
        else:
            yield "## 其他方法\n可以比较能量法。"

    def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
        self.complete_messages.append(str(messages[-1]["content"]))
        return LLMResponse(content=json.dumps({"candidate_tags": ["受力模型", "符号检查"]}))


def _write_vocab(workspace: Path) -> None:
    path = workspace / ".cpho" / "vocabulary" / "private.yml"
    path.parent.mkdir(parents=True)
    path.write_text(
        yaml.safe_dump(
            {
                "version": "explain",
                "tags": [
                    {
                        "internal_id": "explain_force_model",
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
            vocabulary_version="explain",
        ),
    )


def _seed_knowledge(workspace: Path) -> None:
    _write_vocab(workspace)
    write_index(
        workspace / ".cpho" / "index.jsonl",
        [
            IndexEntry(
                problem_id="p1",
                problem_path=Path("第四届芝麻物理联考.pdf"),
                problem_page_range=(1, 1),
                indexed_at=datetime.now(timezone.utc),
                physics_model_tags=[
                    TaggedReference(
                        internal_id="explain_force_model",
                        source=TagSource.USER_NOTE,
                    )
                ],
                fingerprint=_fingerprint(),
                ocr_text_length=20,
                tag_prompt_version="v1",
            )
        ],
    )
    source = workspace / "force.md"
    source.write_text("受力模型总结：先选研究对象。", encoding="utf-8")
    draft = normalize_knowledge_file(
        workspace,
        source,
        canonical_tag_id="explain_force_model",
        dry_run=True,
    )
    publish_knowledge_draft(workspace, draft)


@pytest.mark.asyncio
async def test_run_explain_v2_streams_selected_panels_and_uses_knowledge(
    tmp_path: Path,
) -> None:
    _seed_knowledge(tmp_path)
    provider = FakeExplainProvider()
    chunks: list[tuple[str, str]] = []
    solve_report = SolveReport(
        problem_id="p1",
        discrepancies=[
            Discrepancy(
                description="符号可能错误",
                likely_source="sign error",
                official_answer_refs=["answer:1"],
            )
        ],
    )

    result = await run_explain(
        provider=provider,
        params=ModelParams(name="fake"),
        problem_text="题目",
        answer_text="答案",
        problem_name="p1",
        workspace_path=tmp_path,
        panels=[ExplainPanel.APPROACH, ExplainPanel.ANSWER_REPLACEMENT],
        solve_report=solve_report,
        on_chunk=lambda chunk: chunks.append((chunk.panel.value, chunk.text)),
        input_modality_used="multimodal_pdf",
    )

    assert ("approach", "## 思路描述\n先看受力模型。") in chunks
    assert ("answer_replacement", "## 标答替换\n补全答案跳步。") in chunks
    assert result.markdown_path.exists()
    markdown = result.markdown_path.read_text(encoding="utf-8")
    assert "## 思路描述" in markdown
    assert "## 标答替换" in markdown
    assert "## 其他方法" not in markdown
    assert "### 参考来源" in markdown
    assert "explain_force_model" in markdown
    assert "input_modality_used: multimodal_pdf" in markdown
    assert result.candidate_tags == ["受力模型", "符号检查"]
    assert any("knowledge_reference" in message for message in provider.stream_messages)
    assert any("符号可能错误" in message for message in provider.stream_messages)


@pytest.mark.asyncio
async def test_run_explain_v2_without_solve_report_uses_explicit_empty_context(
    tmp_path: Path,
) -> None:
    provider = FakeExplainProvider()

    await run_explain(
        provider=provider,
        params=ModelParams(name="fake"),
        problem_text="题目",
        answer_text="答案",
        problem_name="not-indexed",
        workspace_path=tmp_path,
        panels=[ExplainPanel.ALTERNATIVE_METHODS],
        solve_report=None,
    )

    assert provider.stream_messages
    assert all("无已确认 Solve 审查结果" in message for message in provider.stream_messages)
