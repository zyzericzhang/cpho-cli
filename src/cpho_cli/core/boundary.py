from __future__ import annotations

from pathlib import Path


class BoundaryError(RuntimeError):
    """Raised when a user path crosses the workspace boundary."""


def ensure_workspace_available(workspace: Path) -> Path:
    resolved = workspace.expanduser().resolve()
    if not resolved.is_dir():
        raise BoundaryError(f"工作空间不可用，请检查外接硬盘或路径：{workspace}")
    return resolved


def ensure_in_workspace(workspace: Path, path: Path) -> Path:
    resolved_workspace = ensure_workspace_available(workspace)
    resolved_path = path.expanduser().resolve()
    try:
        resolved_path.relative_to(resolved_workspace)
    except ValueError as exc:
        raise BoundaryError(f"文件不在当前工作空间（{resolved_workspace}）：{path}") from exc
    return resolved_path


__all__ = ["BoundaryError", "ensure_in_workspace", "ensure_workspace_available"]
