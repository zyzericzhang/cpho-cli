"""Golden workspace determinism tests for build_index."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from cpho_cli.core.index.builder import build_index
from cpho_cli.core.index.hashing import sha256_file
from cpho_cli.core.index.storage import load_index
from cpho_cli.core.index.tagging import TagRefinementOutput
from cpho_cli.models.documents import make_problem_id

from conftest import FakeLLMProvider, FakeOCRProvider

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden_index_workspace"


def _expected_tags() -> dict[str, dict[str, list[str]]]:
    return json.loads((GOLDEN_DIR / "expected_canonical_tags.json").read_text(encoding="utf-8"))


def _expected_tags_by_problem_id(ws: Path) -> dict[str, dict[str, list[str]]]:
    return {
        make_problem_id(sha256_file(ws / f"{stem}.png"), 1): tags
        for stem, tags in _expected_tags().items()
    }


def _golden_llm() -> FakeLLMProvider:
    """FakeLLM that returns expected canonical tags for golden problems."""
    expected = _expected_tags()
    per_problem: dict[str, TagRefinementOutput] = {}
    for pid, tags in expected.items():
        per_problem[pid] = TagRefinementOutput(
            selected_physics_models=tags["physics_model_tags"],
            selected_math_techniques=tags["math_technique_tags"],
            selected_heuristics=tags["heuristic_tags"],
            difficulty_aspects=["受力分析"],
        )
    return FakeLLMProvider(per_problem=per_problem)


def _copy_golden_workspace(tmp_path: Path) -> Path:
    """Copy golden fixture into tmp_path and add a config."""
    ws = tmp_path / "workspace"
    shutil.copytree(GOLDEN_DIR, ws)
    (ws / "config.local.yml").write_text(
        "provider:\n  openrouter_api_key: golden-test-key\n",
        encoding="utf-8",
    )
    return ws


def _patch_rapidocr_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "cpho_cli.core.index.builder._rapidocr_version", lambda: "3.0.0"
    )


def test_golden_workspace_first_indexing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = _copy_golden_workspace(tmp_path)
    expected = _expected_tags_by_problem_id(ws)

    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=_golden_llm(),
        ocr_strategy="reuse",
    )
    entries = load_index(ws)
    assert len(entries) == len(expected)

    for entry in entries:
        assert entry.problem_id in expected, f"Unexpected problem_id: {entry.problem_id}"
        exp = expected[entry.problem_id]
        actual_physics = sorted(t.internal_id for t in entry.physics_model_tags)
        actual_math = sorted(t.internal_id for t in entry.math_technique_tags)
        actual_heuristic = sorted(t.internal_id for t in entry.heuristic_tags)
        assert actual_physics == sorted(exp["physics_model_tags"])
        assert actual_math == sorted(exp["math_technique_tags"])
        assert actual_heuristic == sorted(exp["heuristic_tags"])


def test_golden_workspace_reindex_identical_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = _copy_golden_workspace(tmp_path)
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=_golden_llm(),
        ocr_strategy="reuse",
    )

    build_index(ws, **kwargs)
    entries_first = load_index(ws)

    # Force rebuild to get fresh entries
    build_index(ws, force=True, **kwargs)
    entries_second = load_index(ws)

    assert len(entries_first) == len(entries_second)
    first_by_id = {e.problem_id: e for e in entries_first}
    second_by_id = {e.problem_id: e for e in entries_second}

    for pid in first_by_id:
        e1 = first_by_id[pid]
        e2 = second_by_id[pid]
        # Compare everything except indexed_at (timestamps differ)
        assert e1.physics_model_tags == e2.physics_model_tags
        assert e1.math_technique_tags == e2.math_technique_tags
        assert e1.heuristic_tags == e2.heuristic_tags
        assert e1.difficulty_aspects == e2.difficulty_aspects
        assert e1.fingerprint.file == e2.fingerprint.file


def test_golden_workspace_skip_on_rerun(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = _copy_golden_workspace(tmp_path)
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=_golden_llm(),
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)
    stats = build_index(ws, **kwargs)
    assert stats.tags_skipped == 2
    assert stats.tags_regenerated == 0
