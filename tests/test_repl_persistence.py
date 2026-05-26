from __future__ import annotations

import json
from pathlib import Path

from cpho_cli.cli.repl.persistence import (
    config_dir,
    data_dir,
    history_path,
    read_session,
    session_path,
    write_session,
)
from cpho_cli.cli.repl.session import IndexMeta, SessionState
from cpho_cli.models.config import AppConfig


def test_xdg_paths_are_isolated(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

    assert config_dir() == tmp_path / "cpho"
    assert data_dir() == tmp_path / "data" / "cpho"
    assert history_path() == tmp_path / "cpho" / "history.txt"
    assert session_path() == tmp_path / "cpho" / "session.json"
    assert config_dir().exists()


def test_read_session_missing_returns_none(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert read_session() is None


def test_write_session_atomic_json_allowlist(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    session = SessionState(workspace_path=tmp_path / "ws", config=AppConfig())
    session.index_meta = IndexMeta(problem_count=1, tag_count=2, index_mtime_ns=3, index_version="v1")
    session.last_search_query = "力学"
    session.last_search_result_ids = ["p1"]
    session.current_problem_id = "p1"
    session.out_dir = tmp_path / "exports"
    session.probe_max_rounds = 12

    write_session(session)
    payload = json.loads(session_path().read_text(encoding="utf-8"))

    assert not (tmp_path / "cpho" / "session.json.tmp").exists()
    assert payload["workspace_path"] == str(tmp_path / "ws")
    assert payload["last_search_query"] == "力学"
    assert payload["last_search_result_ids"] == ["p1"]
    assert payload["current_problem_id"] == "p1"
    assert payload["out_dir"] == str(tmp_path / "exports")
    assert payload["probe_max_rounds"] == 12
    assert payload["index_mtime_ns"] == 3
    assert payload["index_version"] == "v1"
    assert "IndexEntry" not in session_path().read_text(encoding="utf-8")
    assert "current_solve_report" not in payload
    assert read_session() == payload
