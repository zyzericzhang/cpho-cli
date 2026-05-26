from __future__ import annotations

import hashlib
from pathlib import Path

from cpho_cli.cli.repl.persistence import data_dir
from cpho_cli.core.skill_outputs import (
    append_markdown,
    default_markdown_path,
    safe_problem_filename,
    workspace_hash,
    write_markdown_atomic,
)


def test_default_markdown_path_uses_xdg_data_and_workspace_hash(
    tmp_path: Path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg-data"))
    workspace = tmp_path / "workspace with spaces"
    workspace.mkdir()

    path = default_markdown_path(workspace, "explain", "力学2试题.pdf")

    expected_hash = hashlib.sha256(str(workspace.resolve()).encode("utf-8")).hexdigest()[:12]
    assert data_dir() == tmp_path / "xdg-data" / "cpho"
    assert path == data_dir() / "outputs" / expected_hash / "explain" / "力学2试题.pdf.md"
    assert workspace_hash(workspace) == expected_hash


def test_safe_problem_filename_preserves_chinese_and_strips_separators() -> None:
    name = safe_problem_filename("2023暑期猿辅导物理刷题  电子版/力学2试题:第1题", ".md")

    assert "2023暑期猿辅导物理刷题  电子版" in name
    assert "力学2试题" in name
    assert "/" not in name
    assert ":" not in name
    assert name.endswith(".md")


def test_default_markdown_path_uses_override_dir(tmp_path: Path) -> None:
    override = tmp_path / "out"

    path = default_markdown_path(tmp_path, "probe", "综合试题", override_dir=override)

    assert path == override / "probe" / "综合试题.md"


def test_markdown_writes_create_parent_and_append(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "report.md"

    write_markdown_atomic(path, "# 标题\n")
    append_markdown(path, "\n追加")

    assert path.read_text(encoding="utf-8") == "# 标题\n\n追加"
    assert not path.with_suffix(".md.tmp").exists()
