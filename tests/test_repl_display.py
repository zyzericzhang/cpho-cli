from __future__ import annotations

from pathlib import Path

from cpho_cli.cli.repl.display import banner, render_table
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.models.config import AppConfig


def test_render_table_handles_chinese_width_and_truncation() -> None:
    output = render_table(["名称", "说明"], [["力学", "很长的中文说明"]], [4, 8])

    assert "名称" in output
    assert "..." in output


def test_banner_without_index(tmp_path: Path) -> None:
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    output = banner(session)

    assert str(tmp_path) in output
    assert "未建立" in output
    assert "openrouter" in output
