from __future__ import annotations

import json
import shutil
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpho_cli.core.explain import run_explain
from cpho_cli.core.followup import run_followup
from cpho_cli.core.index.api import add_problem_tags, get_problem_entry
from cpho_cli.core.index.storage import write_index
from cpho_cli.core.probe import run_probe
from cpho_cli.core.skill_outputs import default_markdown_path
from cpho_cli.core.skill_progress import PlainProgressReporter, wrap_handlers
from cpho_cli.models.config import ModelParams
from cpho_cli.models.explain import ExplainTone
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
    UserLearningFingerprint,
)
from cpho_cli.models.llm import LLMResponse
from cpho_cli.models.skills import SkillStep
from cpho_cli.models.solve import Discrepancy, SolveReport

REAL_WORKSPACE = Path("/Users/ericzhang/Desktop/物理竞赛资料")


class FakePhase3Provider:
    def __init__(self) -> None:
        self.complete_calls: list[str] = []
        self.stream_calls: list[str] = []

    def stream(self, messages, params: ModelParams) -> Iterator[str]:  # type: ignore[no-untyped-def]
        content = str(messages[-1]["content"])
        self.stream_calls.append(content)
        if "sentence" in content:
            yield "### 句子级 explain\n逐句解释。"
        else:
            yield (
                "### 整道题物理图像与思路\n先看受力。\n"
                "### 原答案逐步讲解\n逐步检查。\n"
                "### 超越原答案的更清晰推导\n补一个更清晰推导。"
            )

    def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
        content = str(messages[-1]["content"])
        self.complete_calls.append(content)
        if "Extract index tag candidates" in content:
            return LLMResponse(content=json.dumps({"candidate_tags": ["受力分析"]}))
        if "oral probe" in content:
            return LLMResponse(content="这一步选择哪个研究对象？")
        return LLMResponse(content="follow-up answer")


class PromptScript:
    def __init__(self, answers: list[str]) -> None:
        self.answers = answers

    async def __call__(self, prompt: str) -> str:
        return self.answers.pop(0)


def _fingerprint() -> IndexFingerprint:
    return IndexFingerprint(
        file=FileFingerprint(
            problem_sha256="a" * 64,
            answer_sha256="b" * 64,
            problem_size_bytes=1,
            answer_size_bytes=1,
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
            model_name="fake",
            model_temperature=0.0,
            vocabulary_version="v0.1",
        ),
        user_learning=UserLearningFingerprint(),
    )


def _seed_index(workspace: Path, problem_path: Path) -> IndexEntry:
    entry = IndexEntry(
        problem_id="phase3-real-shape",
        problem_path=problem_path.relative_to(workspace),
        answer_path=problem_path.relative_to(workspace),
        problem_page_range=(1, 1),
        indexed_at=datetime(2026, 5, 26, tzinfo=timezone.utc),
        physics_model_tags=[
            TaggedReference(internal_id="newton_second_law", source=TagSource.OCR_FALLBACK)
        ],
        fingerprint=_fingerprint(),
        ocr_cache_path=None,
        ocr_text_length=100,
        tag_prompt_version="v0.1",
    )
    write_index(workspace / ".cpho" / "index.jsonl", [entry])
    return entry


def _copy_real_shape_sample(tmp_path: Path) -> Path:
    workspace = tmp_path / "phase3-real-shape"
    workspace.mkdir()
    if REAL_WORKSPACE.exists():
        sample = next(REAL_WORKSPACE.rglob("*.pdf"), None)
        if sample is not None:
            target = workspace / sample.relative_to(REAL_WORKSPACE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sample, target)
            return target
    fallback = Path("tests/fixtures/splitting/ipho_style_multi_problem.pdf")
    target = workspace / "fixtures" / fallback.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fallback, target)
    return target


@pytest.mark.asyncio
async def test_phase3_end_to_end_acceptance_uses_temp_copy_and_seeded_index(
    tmp_path: Path,
    capsys,
) -> None:
    copied_problem = _copy_real_shape_sample(tmp_path)
    workspace = (
        copied_problem.parents[1]
        if copied_problem.parent.name != "fixtures"
        else copied_problem.parents[1]
    )
    assert copied_problem.is_relative_to(tmp_path)
    assert not copied_problem.is_relative_to(REAL_WORKSPACE)
    entry = _seed_index(workspace, copied_problem)
    provider = FakePhase3Provider()
    params = ModelParams(name="fake")
    solve_report = SolveReport(
        problem_id=entry.problem_id,
        discrepancies=[
            Discrepancy(
                description="标答符号需复核",
                likely_source="sign",
                official_answer_refs=["answer:1"],
            )
        ],
    )

    explain = await run_explain(
        provider=provider,
        params=params,
        problem_text="真实工作空间形状题目文本",
        answer_text="答案文本",
        problem_name=entry.problem_id,
        workspace_path=workspace,
        tones=[ExplainTone.TEACHER, ExplainTone.DENSE],
        solve_report=solve_report,
        output_dir=tmp_path / "exports",
    )
    probe = await run_probe(
        provider=provider,
        params=params,
        problem_text="真实工作空间形状题目文本",
        problem_name=entry.problem_id,
        workspace_path=workspace,
        prompt=PromptScript(["研究对象", "/exit"]),
        max_rounds=10,
        solve_report=solve_report,
        output_dir=tmp_path / "exports",
    )
    await run_followup(
        prompt=PromptScript(["继续解释", "/exit"]),
        provider=provider,
        params=params,
        skill_context_markdown=explain.markdown_path.read_text(encoding="utf-8"),
        export_path=explain.markdown_path,
    )
    add_problem_tags(
        workspace,
        entry.problem_id,
        [*explain.candidate_tags, solve_report.discrepancies[0].description],
        skill_name="explain",
        reasoning="Phase 3 acceptance confirmed tags.",
    )
    wrapped = wrap_handlers(
        {"fake": lambda step, values: {"ok": True}},
        PlainProgressReporter(),
    )
    wrapped["fake"](SkillStep(id="acceptance", kind="fake"), {})

    reloaded = get_problem_entry(workspace, entry.problem_id)
    assert reloaded is not None
    assert [tag.internal_id for tag in reloaded.physics_model_tags] == ["newton_second_law"]
    assert reloaded.user_tags[0].skill_name == "explain"
    assert "## Tone: 老师型" in explain.markdown_path.read_text(encoding="utf-8")
    assert "## 问题" in probe.markdown_path.read_text(encoding="utf-8")
    assert "## Follow-up" in explain.markdown_path.read_text(encoding="utf-8")
    assert default_markdown_path(
        workspace, "probe", "综合题", override_dir=tmp_path
    ).is_relative_to(tmp_path)
    assert "done: acceptance" in capsys.readouterr().out
