from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from cpho_cli.cli.repl.session import IndexMeta, SessionState, load_index_meta
from cpho_cli.core.index.storage import write_index
from cpho_cli.models.config import AppConfig
from cpho_cli.models.llm import ModelCapabilities
from conftest import make_index_entry


def test_session_state_defaults_and_mutability(tmp_path: Path) -> None:
    session = SessionState(workspace_path=tmp_path, config=AppConfig())

    assert session.index_path is None
    assert session.last_search_result_ids == []
    assert session.current_problem_id is None
    assert session.current_solve_report is None
    assert session.out_dir is None
    assert session.probe_max_rounds == 10
    assert session.max_results == 20
    assert session.output_format == "compact"
    assert session.model_capabilities == ModelCapabilities()

    session.last_search_query = "力学"
    assert session.last_search_query == "力学"


def test_index_meta_is_frozen_and_strict() -> None:
    meta = IndexMeta(problem_count=10, tag_count=42, index_mtime_ns=123, index_version="v1")

    with pytest.raises(ValidationError):
        meta.problem_count = 5
    with pytest.raises(ValidationError):
        IndexMeta(
            problem_count=10,
            tag_count=42,
            index_mtime_ns=123,
            index_version="v1",
            extra="x",
        )


def test_load_index_meta_missing_returns_none(tmp_path: Path) -> None:
    assert load_index_meta(tmp_path) is None


def test_load_index_meta_counts_entries_and_tags(tmp_path: Path) -> None:
    entries = [
        make_index_entry("p1", physics_model_tags=["newton"], math_technique_tags=["scale"]),
        make_index_entry("p2", physics_model_tags=["newton"], heuristic_tags=["symmetry"]),
    ]
    write_index(tmp_path / ".cpho" / "index.jsonl", entries)

    meta = load_index_meta(tmp_path)

    assert meta is not None
    assert meta.problem_count == 2
    assert meta.tag_count == 3
    assert meta.index_version == "v2"
