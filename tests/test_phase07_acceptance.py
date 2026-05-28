from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpho_cli.cli.repl.commands import builtin_skills
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.index.storage import write_index
from cpho_cli.models.config import AppConfig
from cpho_cli.models.explain import ExplainResult
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    UserLearningFingerprint,
)


class PromptScript:
    def __init__(self, answers: list[str]) -> None:
        self.answers = answers
        self.prompts: list[str] = []

    async def prompt_async(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.answers.pop(0) if self.answers else ""


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
            model_name="test",
            model_temperature=0.0,
            vocabulary_version="v0.1",
        ),
        user_learning=UserLearningFingerprint(),
    )


def _seed_problem(tmp_path: Path) -> None:
    problem = tmp_path / "第四届芝麻物理联考 (复赛) 理论试题.pdf"
    answer = tmp_path / "第四届芝麻物理联考试卷参考答案.pdf"
    ocr = tmp_path / ".cpho" / "ocr" / "p1.txt"
    problem.write_text("problem", encoding="utf-8")
    answer.write_text("answer", encoding="utf-8")
    ocr.parent.mkdir(parents=True, exist_ok=True)
    ocr.write_text("OCR 题目文本", encoding="utf-8")
    entry = IndexEntry(
        problem_id="p1",
        problem_path=problem.relative_to(tmp_path),
        answer_path=answer.relative_to(tmp_path),
        problem_page_range=(1, 1),
        indexed_at=datetime.now(timezone.utc),
        fingerprint=_fingerprint(),
        ocr_cache_path=ocr.relative_to(tmp_path),
        ocr_text_length=8,
        tag_prompt_version="v0.1",
    )
    write_index(tmp_path / ".cpho" / "index.jsonl", [entry])


@pytest.mark.asyncio
async def test_phase07_repl_explain_panel_flow_writes_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _seed_problem(tmp_path)
    output = tmp_path / "exports" / "p1.explain.md"
    calls = {}

    async def fake_run_explain(**kwargs):  # type: ignore[no-untyped-def]
        calls["panels"] = [panel.value for panel in kwargs["panels"]]
        output.parent.mkdir(parents=True)
        output.write_text("# Explain: p1\n\n## 思路描述\n", encoding="utf-8")
        return ExplainResult(
            problem_name="p1",
            panel_outputs=[],
            candidate_tags=[],
            markdown_path=output,
        )

    monkeypatch.setattr(builtin_skills, "run_explain", fake_run_explain)
    monkeypatch.setattr(
        builtin_skills,
        "provider_and_params",
        lambda session, skill_name: (object(), object()),
    )
    session = SessionState(
        workspace_path=tmp_path,
        config=AppConfig(),
        current_problem_id="p1",
        out_dir=tmp_path / "exports",
        prompt_session=PromptScript(["", ""]),
    )

    await builtin_skills.do_explain(session, ["--panel", "approach"])

    assert calls["panels"] == ["approach"]
    assert output.exists()


@pytest.mark.asyncio
async def test_phase07_repl_explain_old_tone_is_rejected(tmp_path: Path, capsys) -> None:
    _seed_problem(tmp_path)
    session = SessionState(
        workspace_path=tmp_path,
        config=AppConfig(),
        current_problem_id="p1",
        prompt_session=PromptScript([""]),
    )

    await builtin_skills.do_explain(session, ["--tone", "teacher"])

    assert "用法: /explain" in capsys.readouterr().out
