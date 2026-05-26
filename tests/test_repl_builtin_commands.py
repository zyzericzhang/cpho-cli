from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.commands.builtin_skills import register as register_skills
from cpho_cli.cli.repl.commands.help_cmd import register as register_help
from cpho_cli.cli.repl.commands.set_cmd import do_set
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
from cpho_cli.models.solve import Discrepancy, SolveReport, SolveRunResult
from cpho_cli.models.probe import ProbeTranscript


def test_help_uses_registry_source_of_truth(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    registry: dict[str, Command] = {}
    register_help(registry)
    session = SessionState(workspace_path=tmp_path, config=AppConfig())
    setattr(session, "registry", registry)

    import asyncio

    asyncio.run(registry["/help"].handler(session, []))

    assert "/help" in capsys.readouterr().out


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


def _seed_problem(tmp_path: Path, problem_id: str = "p1") -> IndexEntry:
    problem = tmp_path / "第四届芝麻物理联考 (复赛) 理论试题.pdf"
    answer = tmp_path / "第四届芝麻物理联考试卷参考答案.pdf"
    ocr = tmp_path / ".cpho" / "ocr" / f"{problem_id}.txt"
    problem.write_text("problem", encoding="utf-8")
    answer.write_text("answer", encoding="utf-8")
    ocr.parent.mkdir(parents=True, exist_ok=True)
    ocr.write_text("OCR 题目文本", encoding="utf-8")
    entry = IndexEntry(
        problem_id=problem_id,
        problem_path=problem.relative_to(tmp_path),
        answer_path=answer.relative_to(tmp_path),
        problem_page_range=(1, 1),
        indexed_at="2026-05-26T00:00:00Z",
        fingerprint=_fingerprint(),
        ocr_cache_path=ocr.relative_to(tmp_path),
        ocr_text_length=8,
        tag_prompt_version="v0.1",
    )
    write_index(tmp_path / ".cpho" / "index.jsonl", [entry])
    return entry


def test_phase3_skill_commands_registered() -> None:
    registry: dict[str, Command] = {}
    register_skills(registry)

    assert {"/solve", "/explain", "/probe"} <= set(registry)
    assert "/quiz" not in registry


@pytest.mark.asyncio
async def test_repl_solve_auto_confirm_persists_and_stores_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _seed_problem(tmp_path)
    report = SolveReport(
        problem_id="p1",
        discrepancies=[
            Discrepancy(
                description="答案符号错误",
                likely_source="sign",
                official_answer_refs=["answer:2"],
            )
        ],
    )
    calls: dict[str, object] = {}

    def fake_solve_problem(**kwargs):  # type: ignore[no-untyped-def]
        calls["solve"] = kwargs
        return SolveRunResult(
            report_json=None, report_markdown=tmp_path / "solve.md", report=report
        )

    def fake_add_problem_tags(*args, **kwargs):  # type: ignore[no-untyped-def]
        calls["tags"] = (args, kwargs)

    from cpho_cli.cli.repl.commands import builtin_skills

    monkeypatch.setattr(builtin_skills, "solve_problem", fake_solve_problem)
    monkeypatch.setattr(builtin_skills, "add_problem_tags", fake_add_problem_tags)
    session = SessionState(
        workspace_path=tmp_path,
        config=AppConfig(),
        current_problem_id="p1",
        prompt_session=PromptScript([""]),
    )

    await builtin_skills.do_solve(session, ["--auto-confirm", "--persist-tags"])

    assert session.current_solve_report == report
    assert calls["solve"]  # resolved current problem and ran service
    assert calls["tags"][1]["skill_name"] == "solve"  # type: ignore[index]


@pytest.mark.asyncio
async def test_repl_explain_passes_solve_report_confirms_tags_and_probe_entry(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    _seed_problem(tmp_path)
    solve_report = SolveReport(
        problem_id="p1",
        discrepancies=[Discrepancy(description="答案第 2 行符号错误", likely_source="sign")],
    )
    calls: dict[str, object] = {}

    async def fake_run_explain(**kwargs):  # type: ignore[no-untyped-def]
        calls["solve_report"] = kwargs["solve_report"]
        return ExplainResult(
            problem_name="p1",
            tone_outputs=[],
            candidate_tags=["牛顿定律", "错误标签"],
            markdown_path=tmp_path / "explain.md",
        )

    async def fake_run_probe(**kwargs):  # type: ignore[no-untyped-def]
        calls["probe_problem"] = kwargs["problem_name"]
        return ProbeTranscript(
            problem_name=kwargs["problem_name"], markdown_path=tmp_path / "probe.md"
        )

    def fake_add_problem_tags(*args, **kwargs):  # type: ignore[no-untyped-def]
        calls["tags"] = (args, kwargs)

    from cpho_cli.cli.repl.commands import builtin_skills

    monkeypatch.setattr(builtin_skills, "run_explain", fake_run_explain)
    monkeypatch.setattr(builtin_skills, "run_probe", fake_run_probe)
    monkeypatch.setattr(builtin_skills, "add_problem_tags", fake_add_problem_tags)
    monkeypatch.setattr(
        builtin_skills,
        "provider_and_params",
        lambda session, skill_name: (object(), object()),
    )
    session = SessionState(
        workspace_path=tmp_path,
        config=AppConfig(),
        current_problem_id="p1",
        current_solve_report=solve_report,
        prompt_session=PromptScript(["y", "n", "+补充标签", "", "/probe", "/exit"]),
    )

    await builtin_skills.do_explain(session, ["--tone", "teacher"])

    assert calls["solve_report"] is solve_report
    assert calls["tags"][0][2] == ["牛顿定律", "补充标签"]  # type: ignore[index]
    assert calls["tags"][1]["skill_name"] == "explain"  # type: ignore[index]
    assert calls["probe_problem"] == "p1"
    assert "→ 进入 Probe 模式？(`/probe` 或 Enter 跳过)" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_repl_explain_warns_without_prior_solve(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    _seed_problem(tmp_path)

    async def fake_run_explain(**kwargs):  # type: ignore[no-untyped-def]
        assert kwargs["solve_report"] is None
        return ExplainResult(
            problem_name="p1",
            tone_outputs=[],
            candidate_tags=[],
            markdown_path=tmp_path / "explain.md",
        )

    from cpho_cli.cli.repl.commands import builtin_skills

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
        prompt_session=PromptScript([""]),
    )

    await builtin_skills.do_explain(session, [])

    assert "尚未运行 /solve" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_set_validates_session_fields(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    await do_set(session, ["max_results", "5"])
    await do_set(session, ["output_format", "full"])
    await do_set(session, ["out.dir", str(tmp_path / "exports")])
    await do_set(session, ["probe.max_rounds", "15"])

    assert session.max_results == 5
    assert session.output_format == "full"
    assert session.out_dir == (tmp_path / "exports").resolve()
    assert session.probe_max_rounds == 15
