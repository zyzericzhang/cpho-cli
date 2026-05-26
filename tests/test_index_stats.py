"""Tests for IndexRunStats accounting in build_index."""

from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.core.index.builder import build_index
from cpho_cli.core.index.tagging import CandidateTagSuggestion, TagRefinementOutput
from cpho_cli.models.index import TagCategory

from conftest import FakeLLMProvider, FakeOCRProvider, setup_workspace


def _patch_rapidocr_version(monkeypatch: pytest.MonkeyPatch, version: str = "3.0.0") -> None:
    monkeypatch.setattr(
        "cpho_cli.core.index.builder._rapidocr_version", lambda: version
    )


def test_stats_total_problems(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1", "p2", "p3"])
    stats = build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    assert stats.total_problems == 3


def test_stats_file_changed_counter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1", "p2", "p3"])
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)

    # Modify one problem file
    (ws / "p1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"modified_p1" + b"\x00" * 50)
    stats = build_index(ws, **kwargs)
    assert stats.file_changed == 1
    assert stats.file_unchanged == 2


def test_stats_ocr_reused_vs_regenerated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1", "p2"])
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)

    # Second run: same files -> all skip -> no OCR regen
    stats = build_index(ws, **kwargs)
    assert stats.ocr_regenerated == 0
    # Tags skipped means no OCR was needed
    assert stats.tags_skipped == 2


def test_stats_candidate_tags_proposed_counter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    llm = FakeLLMProvider(
        fixed_output=TagRefinementOutput(
            selected_physics_models=["energy_conservation"],
            selected_math_techniques=[],
            selected_heuristics=[],
            candidates=[
                CandidateTagSuggestion(
                    internal_id_suggestion="cand1",
                    display_zh_suggestion="候选1",
                    category=TagCategory.PHYSICS_MODEL,
                    rationale="test1",
                ),
                CandidateTagSuggestion(
                    internal_id_suggestion="cand2",
                    display_zh_suggestion="候选2",
                    category=TagCategory.MATH_TECHNIQUE,
                    rationale="test2",
                ),
            ],
        )
    )
    stats = build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=llm,
        ocr_strategy="reuse",
    )
    assert stats.candidate_tags_proposed == 2


def test_stats_pending_review_cumulative(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])

    def _make_llm(name: str, display: str) -> FakeLLMProvider:
        return FakeLLMProvider(
            fixed_output=TagRefinementOutput(
                selected_physics_models=["energy_conservation"],
                selected_math_techniques=[],
                selected_heuristics=[],
                candidates=[
                    CandidateTagSuggestion(
                        internal_id_suggestion=name,
                        display_zh_suggestion=display,
                        category=TagCategory.PHYSICS_MODEL,
                        rationale="test",
                    )
                ],
            )
        )

    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        ocr_strategy="reuse",
    )
    build_index(ws, llm_provider=_make_llm("c1", "候选A"), **kwargs)
    stats2 = build_index(ws, llm_provider=_make_llm("c2", "候选B"), force=True, **kwargs)
    assert stats2.pending_review_items >= 2
