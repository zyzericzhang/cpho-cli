from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.core.boundary import (
    BoundaryError,
    ensure_in_workspace,
    ensure_workspace_available,
)


def test_ensure_workspace_available_accepts_existing_directory(tmp_path: Path) -> None:
    assert ensure_workspace_available(tmp_path) == tmp_path.resolve()


def test_ensure_workspace_available_rejects_missing_directory(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(BoundaryError, match="工作空间不可用"):
        ensure_workspace_available(missing)


def test_ensure_in_workspace_accepts_child_path(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    child = workspace / "a" / "problem.pdf"
    child.parent.mkdir(parents=True)
    child.write_text("x", encoding="utf-8")

    assert ensure_in_workspace(workspace, child) == child.resolve()


def test_ensure_in_workspace_rejects_outside_path(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside.pdf"
    workspace.mkdir()
    outside.write_text("x", encoding="utf-8")

    with pytest.raises(BoundaryError, match="文件不在当前工作空间"):
        ensure_in_workspace(workspace, outside)


def test_ensure_in_workspace_rejects_symlink_to_outside(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside.pdf"
    link = workspace / "linked.pdf"
    workspace.mkdir()
    outside.write_text("x", encoding="utf-8")
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink unavailable on this filesystem")

    with pytest.raises(BoundaryError, match="文件不在当前工作空间"):
        ensure_in_workspace(workspace, link)
