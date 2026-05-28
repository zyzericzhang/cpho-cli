from __future__ import annotations

import tomllib
from pathlib import Path

from cpho_cli.cli.repl.display import render_table
from cpho_cli.core.boundary import ensure_in_workspace, ensure_workspace_available


def test_nested_chinese_workspace_paths_are_preserved(tmp_path: Path) -> None:
    workspace = tmp_path / "物理竞赛资料"
    problem = workspace / "2023机构卷" / "2023北斗学友暑假" / "力学2试题.pdf"
    problem.parent.mkdir(parents=True)
    problem.write_bytes(b"%PDF-1.4\n")

    resolved_workspace = ensure_workspace_available(workspace)
    resolved_problem = ensure_in_workspace(workspace, problem)

    assert resolved_workspace == workspace.resolve()
    assert resolved_problem == problem.resolve()
    assert "物理竞赛资料" in str(resolved_problem)
    assert "2023北斗学友暑假" in str(resolved_problem)


def test_render_table_handles_chinese_cells_without_negative_widths() -> None:
    output = render_table(
        ["题目", "状态", "说明"],
        [["第四届芝麻物理联考", "通过", "中文路径和表格渲染正常"]],
        [10, 4, 12],
    )

    assert "题目" in output
    assert "通过" in output
    assert "..." in output
    for line in output.splitlines():
        assert len(line) > 0


def test_package_data_covers_runtime_resources() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    package_data = data["tool"]["setuptools"]["package-data"]["cpho_cli"]

    expected = [
        "builtin_skills",
        "core/index/prompts",
        "core/knowledge/prompts",
        "vocabulary",
        "data/model_catalog",
    ]

    for item in expected:
        assert any(item in pattern for pattern in package_data)
