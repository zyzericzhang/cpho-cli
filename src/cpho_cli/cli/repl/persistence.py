"""Persistence for REPL session.json and history.txt."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from cpho_cli.cli.repl.session import SessionState


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    path = Path(base) / "cpho"
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    path = Path(base) / "cpho"
    path.mkdir(parents=True, exist_ok=True)
    return path


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    path = Path(base) / "cpho"
    path.mkdir(parents=True, exist_ok=True)
    return path


def session_path() -> Path:
    return config_dir() / "session.json"


def history_path() -> Path:
    return config_dir() / "history.txt"


def log_path() -> Path:
    return cache_dir() / "repl.log"


def write_session(session: SessionState) -> None:
    path = session_path()
    tmp = path.with_suffix(".json.tmp")
    payload = {
        "workspace_path": str(session.workspace_path),
        "last_search_query": session.last_search_query,
        "last_search_result_ids": list(session.last_search_result_ids),
        "current_problem_id": session.current_problem_id,
        "index_mtime_ns": session.index_meta.index_mtime_ns if session.index_meta else None,
        "index_version": session.index_meta.index_version if session.index_meta else None,
        "max_results": session.max_results,
        "output_format": session.output_format,
        "out_dir": str(session.out_dir) if session.out_dir is not None else None,
        "probe_max_rounds": session.probe_max_rounds,
    }
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def read_session() -> dict[str, Any] | None:
    path = session_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("session.json must contain an object")
    return data


__all__ = [
    "cache_dir",
    "config_dir",
    "data_dir",
    "history_path",
    "log_path",
    "read_session",
    "session_path",
    "write_session",
]
