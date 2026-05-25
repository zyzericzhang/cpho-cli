"""Tests for the cpho index CLI command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from cpho_cli.cli.app import app
from cpho_cli.core.index.ocr_cache import OcrEngineDelta, OcrUpgradeDecisionRequired
from cpho_cli.models.index import IndexRunStats

runner = CliRunner()


def test_index_help_lists_options() -> None:
    result = runner.invoke(app, ["index", "--help"])
    assert result.exit_code == 0
    assert "--force" in result.output
    assert "--force-all" in result.output
    assert "--only-new" in result.output
    assert "--dry-run" in result.output
    assert "--ocr-strategy" in result.output
    assert "--list-candidates" in result.output
    assert "--quiet" in result.output
    assert "工作空间" in result.output
    assert "强制重建全部索引" in result.output


def test_index_tag_subcommand_help() -> None:
    for command in ("tag-add", "tag-remove", "tag-set"):
        result = runner.invoke(app, ["index", command, "--help"])
        assert result.exit_code == 0
        assert "--problem-id" in result.output
        assert "--tag" in result.output


def test_index_tag_add_calls_core_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_add(workspace_root, problem_id, tags, *, skill_name, reasoning):
        called.update(
            workspace_root=workspace_root,
            problem_id=problem_id,
            tags=tags,
            skill_name=skill_name,
            reasoning=reasoning,
        )

    monkeypatch.setattr("cpho_cli.cli.app.add_problem_tags", fake_add)

    result = runner.invoke(
        app,
        [
            "index",
            "tag-add",
            "--workspace",
            str(tmp_path),
            "--problem-id",
            "p1",
            "--tag",
            "energy_conservation",
            "--tag",
            "自定义标签",
            "--skill-name",
            "solve",
            "--reasoning",
            "根据解析追加",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert called == {
        "workspace_root": tmp_path,
        "problem_id": "p1",
        "tags": ["energy_conservation", "自定义标签"],
        "skill_name": "solve",
        "reasoning": "根据解析追加",
    }


def test_index_tag_remove_calls_core_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_remove(workspace_root, problem_id, tags):
        called.update(workspace_root=workspace_root, problem_id=problem_id, tags=tags)

    monkeypatch.setattr("cpho_cli.cli.app.remove_problem_tags", fake_remove)

    result = runner.invoke(
        app,
        [
            "index",
            "tag-remove",
            "--workspace",
            str(tmp_path),
            "--problem-id",
            "p1",
            "--tag",
            "自定义标签",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert called == {
        "workspace_root": tmp_path,
        "problem_id": "p1",
        "tags": ["自定义标签"],
    }


def test_index_tag_set_calls_core_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_update(workspace_root, problem_id, tags, *, skill_name, reasoning):
        called.update(
            workspace_root=workspace_root,
            problem_id=problem_id,
            tags=tags,
            skill_name=skill_name,
            reasoning=reasoning,
        )

    monkeypatch.setattr("cpho_cli.cli.app.update_problem_tags", fake_update)

    result = runner.invoke(
        app,
        [
            "index",
            "tag-set",
            "--workspace",
            str(tmp_path),
            "--problem-id",
            "p1",
            "--tag",
            "free_body_diagram",
            "--skill-name",
            "explain",
            "--reasoning",
            "替换 skill 标签",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert called == {
        "workspace_root": tmp_path,
        "problem_id": "p1",
        "tags": ["free_body_diagram"],
        "skill_name": "explain",
        "reasoning": "替换 skill 标签",
    }


def test_index_dry_run_no_llm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "cpho_cli.core.index.builder._rapidocr_version", lambda: "3.0.0"
    )
    result = runner.invoke(app, ["index", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "扫描题目数" in result.output


def test_index_invalid_ocr_strategy_rejected() -> None:
    result = runner.invoke(app, ["index", ".", "--ocr-strategy=bogus"])
    assert result.exit_code != 0
    assert "must be one of" in result.output


def test_index_list_candidates_empty(tmp_path: Path) -> None:
    result = runner.invoke(app, ["index", str(tmp_path), "--list-candidates"])
    assert result.exit_code == 0
    assert "无待审候选标签" in result.output


def test_index_command_propagates_config_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "cpho_cli.core.index.builder._rapidocr_version", lambda: "3.0.0"
    )
    bad_config = tmp_path / "config.local.yml"
    bad_config.write_text("not_a_valid: [", encoding="utf-8")
    result = runner.invoke(app, ["index", str(tmp_path), "--config", str(bad_config)])
    assert result.exit_code != 0


def test_index_ocr_upgrade_prompt_interactive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    call_count = 0

    def fake_build_index(workspace_root, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1 and kwargs.get("ocr_strategy") == "prompt":
            raise OcrUpgradeDecisionRequired(
                OcrEngineDelta(
                    old_engine="rapidocr",
                    old_version="3.0",
                    old_config_hash="old",
                    new_engine="rapidocr",
                    new_version="9.0",
                    new_config_hash="new",
                    affected_count=1,
                    affected_problem_ids=["p1"],
                )
            )
        return IndexRunStats(total_problems=1, tags_regenerated=1, file_changed=1, ocr_regenerated=1)

    monkeypatch.setattr("cpho_cli.cli.app.build_index", fake_build_index)

    result = runner.invoke(app, ["index", str(tmp_path)], input="a\n")
    assert result.exit_code == 0
    assert "OCR 引擎升级" in result.output
    assert "请选择" in result.output
    assert call_count == 2


def test_index_layered_stats_rendered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_stats = IndexRunStats(
        total_problems=3,
        file_changed=1,
        file_unchanged=2,
        ocr_reused=2,
        ocr_regenerated=1,
        ocr_engine_upgrade_detected=False,
        tags_regenerated=1,
        tags_skipped=2,
        refinement_only=0,
        candidate_tags_proposed=0,
        pending_review_items=0,
        papers_split=2,
        problems_extracted=5,
        split_method_rules=3,
        split_method_llm=1,
        split_method_single=1,
    )
    monkeypatch.setattr(
        "cpho_cli.cli.app.build_index", lambda *a, **kw: fake_stats
    )
    result = runner.invoke(app, ["index", str(tmp_path)])
    assert result.exit_code == 0
    assert "扫描题目数" in result.output
    assert "3" in result.output
    assert "切分试卷数" in result.output
    assert "提取题目数" in result.output
    assert "规则切分" in result.output
    assert "LLM 切分" in result.output
    assert "单题路径" in result.output
    assert "5" in result.output
    assert "标签层" in result.output
    assert "候选词表" in result.output


def test_index_quiet_suppresses_stats(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_stats = IndexRunStats(total_problems=3)
    monkeypatch.setattr(
        "cpho_cli.cli.app.build_index", lambda *a, **kw: fake_stats
    )
    result = runner.invoke(app, ["index", str(tmp_path), "--quiet"])
    assert result.exit_code == 0
    assert "扫描题目数" not in result.output
    assert "切分试卷数" not in result.output
    assert "提取题目数" not in result.output
