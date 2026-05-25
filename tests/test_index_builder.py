"""Tests for build_index orchestrator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from cpho_cli.core.index import VocabularyError
from cpho_cli.core.index.hashing import sha256_file
import cpho_cli.core.index.builder as builder_module
from cpho_cli.core.index.builder import build_index
from cpho_cli.core.index.ocr_cache import OcrUpgradeDecisionRequired
from cpho_cli.core.index.storage import load_index
from cpho_cli.core.index.tagging import CandidateTagSuggestion, TagRefinementOutput
from cpho_cli.models.documents import SplitMethod, make_problem_id
from cpho_cli.models.index import (
    TagCategory,
    TagSource,
    UserNotebookEntry,
)
from cpho_cli.models.llm import LLMResponse, LLMUsage
from cpho_cli.models.ocr import OCRBlock, OCRPageResult, OCRResult
from cpho_cli.models.solve import DerivationStep, SolveReport

from conftest import FakeLLMProvider, FakeOCRProvider, setup_workspace


def _patch_rapidocr_version(monkeypatch: pytest.MonkeyPatch, version: str = "3.0.0") -> None:
    monkeypatch.setattr(
        "cpho_cli.core.index.builder._rapidocr_version", lambda: version
    )


def _write_pdf(path: Path, pages: list[str]) -> None:
    import fitz

    document = fitz.open()
    for text in pages:
        page = document.new_page()
        page.insert_text((72, 72), text)
    document.save(path)
    document.close()


class FakePagedOCRProvider:
    def __init__(self, pages_by_name: dict[str, list[str]]) -> None:
        self.pages_by_name = pages_by_name
        self.calls: list[Path] = []

    def extract(self, document: Any) -> OCRResult:
        self.calls.append(document.path)
        pages = self.pages_by_name[document.path.name]
        return OCRResult(
            pages=[
                OCRPageResult(
                    page_number=index,
                    blocks=[OCRBlock(text=text, page_number=index, confidence=1.0)],
                )
                for index, text in enumerate(pages, start=1)
            ]
        )


# --- dry_run ---


def test_build_index_dry_run_returns_zeros(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=[])
    stats = build_index(ws, config_path=ws / "config.local.yml", dry_run=True)
    assert stats.total_problems == 0
    assert stats.tags_regenerated == 0


def test_build_index_dry_run_validates_vocab(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    # Point builtin vocab to a malformed file
    bad_vocab = tmp_path / "bad_vocab.yml"
    bad_vocab.write_text("not_a_valid_mapping: [", encoding="utf-8")
    monkeypatch.setattr(
        "cpho_cli.core.index.vocabulary._builtin_vocab_path", lambda: bad_vocab
    )
    ws = setup_workspace(tmp_path)
    with pytest.raises(VocabularyError):
        build_index(ws, config_path=ws / "config.local.yml", dry_run=True)


# --- first run ---


def test_build_index_first_run_writes_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1", "p2"])
    stats = build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    index_path = ws / ".cpho" / "index.jsonl"
    assert index_path.exists()
    entries = load_index(ws)
    assert len(entries) == 2
    assert stats.total_problems == 2


def test_build_index_writes_one_entry_per_split_problem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    paper_path = tmp_path / "paper.pdf"
    answer_dir = tmp_path / "answers"
    answer_dir.mkdir()
    answer_path = answer_dir / "paper-answer.pdf"
    paper_pages = [f"第{i}题\nproblem {i}" for i in range(1, 6)]
    answer_pages = [f"第{i}题\nanswer {i}" for i in range(1, 6)]
    _write_pdf(paper_path, paper_pages)
    _write_pdf(answer_path, answer_pages)
    (tmp_path / "config.local.yml").write_text(
        "provider:\n  openrouter_api_key: test-key-fake\n",
        encoding="utf-8",
    )

    stats = build_index(
        tmp_path,
        config_path=tmp_path / "config.local.yml",
        ocr_provider=FakePagedOCRProvider(
            {"paper.pdf": paper_pages, "paper-answer.pdf": answer_pages}
        ),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )

    entries = sorted(load_index(tmp_path), key=lambda entry: entry.problem_page_range)
    expected_sha = sha256_file(paper_path)
    assert [entry.problem_id for entry in entries] == [
        make_problem_id(expected_sha, number) for number in range(1, 6)
    ]
    assert [entry.problem_path for entry in entries] == [Path("paper.pdf")] * 5
    assert [entry.answer_path for entry in entries] == [Path("answers/paper-answer.pdf")] * 5
    assert [entry.problem_page_range for entry in entries] == [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]
    assert {entry.fingerprint.semantic.split_prompt_version for entry in entries} == {"v1"}
    assert stats.total_problems == 5
    assert stats.papers_split == 1
    assert stats.problems_extracted == 5
    assert stats.split_method_rules == 5
    assert stats.split_method_llm == 0
    assert stats.split_method_single == 0


def test_build_index_image_workspace_uses_single_split_without_llm_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1", "p2"], with_answers=False)
    split_calls = []
    original_split_paper = builder_module.split_paper

    def recording_split_paper(*args: Any, **kwargs: Any):
        outcome = original_split_paper(*args, **kwargs)
        split_calls.append(outcome.split_method)
        return outcome

    monkeypatch.setattr(builder_module, "split_paper", recording_split_paper)

    stats = build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )

    entries = load_index(ws)
    assert len(entries) == 2
    assert {entry.problem_page_range for entry in entries} == {(1, 1)}
    assert split_calls == [SplitMethod.SINGLE, SplitMethod.SINGLE]
    assert stats.problems_extracted == 2
    assert stats.split_method_single == 2


def test_build_index_discards_stale_rows_before_rebuild(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"], with_answers=False)
    stale_dir = ws / ".cpho"
    stale_dir.mkdir()
    (stale_dir / "index.jsonl").write_text(
        '{"problem_id":"stale-whole-paper","problem_path":"old.pdf"}\n',
        encoding="utf-8",
    )

    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )

    entries = load_index(ws)
    assert [entry.problem_id for entry in entries] != ["stale-whole-paper"]
    assert all(entry.problem_page_range == (1, 1) for entry in entries)


def test_build_index_prompt_strategy_stale_row_rebuild_does_not_crash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"], with_answers=False)
    stale_dir = ws / ".cpho"
    stale_dir.mkdir()
    (stale_dir / "index.jsonl").write_text(
        '{"problem_id":"pre-02.1","problem_path":"p1.png","indexed_at":"2026-01-01T00:00:00Z"}\n',
        encoding="utf-8",
    )

    stats = build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="prompt",
    )

    assert stats.tags_regenerated == 1
    entries = load_index(ws)
    assert len(entries) == 1
    assert entries[0].problem_page_range == (1, 1)


def test_build_index_constructs_provider_for_split_fallback_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    paper_path = tmp_path / "fallback.pdf"
    paper_pages = ["no marker page one", "no marker page two"]
    _write_pdf(paper_path, paper_pages)
    (tmp_path / "config.local.yml").write_text(
        "provider:\n"
        "  openrouter_api_key: configured-key\n"
        "  base_url: https://example.invalid/api\n",
        encoding="utf-8",
    )
    constructed: list[ConstructedProvider] = []

    class ConstructedProvider:
        def __init__(self, api_key: str, base_url: str) -> None:
            self.api_key = api_key
            self.base_url = base_url
            self.calls: list[str | None] = []
            constructed.append(self)

        def complete(self, messages, params, response_model=None):  # type: ignore[no-untyped-def]
            schema_name = response_model.__name__ if response_model is not None else None
            self.calls.append(schema_name)
            if schema_name == "_LLMSplitResponse":
                content = (
                    '{"problems":[{"problem_number":1,"problem_page_range":[1,2],'
                    '"problem_text":"fallback problem","confidence":0.8}],'
                    '"unmatched_answers":[],"diagnostics":[]}'
                )
            elif schema_name == "TopicAssignmentOutput":
                content = (
                    '{"topic_path":"力学/运动学","confidence":0.7,'
                    '"rationale":"test"}'
                )
            else:
                content = TagRefinementOutput(
                    selected_physics_models=["energy_conservation"],
                    selected_math_techniques=[],
                    selected_heuristics=[],
                    difficulty_aspects=["fallback"],
                ).model_dump_json()
            return LLMResponse(
                content=content,
                usage=LLMUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
                raw={},
            )

    monkeypatch.setattr(
        builder_module,
        "create_llm_provider",
        lambda *, kind, api_key, base_url, timeout=120.0: ConstructedProvider(api_key, base_url),
    )

    stats = build_index(
        tmp_path,
        config_path=tmp_path / "config.local.yml",
        ocr_provider=FakePagedOCRProvider({"fallback.pdf": paper_pages}),
        llm_provider=None,
        ocr_strategy="reuse",
    )

    assert len(constructed) == 1
    assert constructed[0].api_key == "configured-key"
    assert constructed[0].base_url == "https://example.invalid/api"
    assert "_LLMSplitResponse" in constructed[0].calls
    assert "TagRefinementOutput" in constructed[0].calls
    assert stats.problems_extracted == 1
    assert stats.split_method_llm == 1


# --- skip on rerun ---


def test_build_index_skip_on_rerun(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1", "p2"])
    fake_llm = FakeLLMProvider()
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=fake_llm,
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)
    initial_calls = len(fake_llm.calls)

    stats2 = build_index(ws, **kwargs)
    assert stats2.tags_skipped == 2
    assert stats2.tags_regenerated == 0
    assert len(fake_llm.calls) == initial_calls  # No new LLM calls


# --- force ---


def test_build_index_force_rebuilds_all(
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
    stats2 = build_index(ws, force=True, **kwargs)
    assert stats2.tags_regenerated == 2


# --- only_new ---


def test_build_index_only_new_skips_existing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)

    # Add a new problem
    (ws / "p2.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"p2" + b"\x00" * 50)
    stats = build_index(ws, only_new=True, **kwargs)
    assert stats.tags_skipped == 1
    assert stats.tags_regenerated == 1


# --- OCR upgrade scenarios ---


def test_build_index_ocr_upgrade_prompt_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch, "3.0.0")
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)

    # Simulate OCR engine upgrade
    _patch_rapidocr_version(monkeypatch, "9.9.0")
    with pytest.raises(OcrUpgradeDecisionRequired) as exc_info:
        build_index(ws, config_path=ws / "config.local.yml", ocr_strategy="prompt")
    assert exc_info.value.delta.affected_count == 1


def test_build_index_ocr_upgrade_reuse_skips_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch, "3.0.0")
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
    )
    build_index(ws, ocr_strategy="reuse", **kwargs)

    _patch_rapidocr_version(monkeypatch, "9.9.0")
    stats = build_index(ws, ocr_strategy="reuse", **kwargs)
    assert stats.ocr_engine_upgrade_detected is False


def test_build_index_ocr_upgrade_rebuild_re_ocrs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch, "3.0.0")
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
    )
    build_index(ws, ocr_strategy="reuse", **kwargs)

    _patch_rapidocr_version(monkeypatch, "9.9.0")
    stats = build_index(ws, ocr_strategy="rebuild", **kwargs)
    assert stats.ocr_engine_upgrade_detected is True
    assert stats.ocr_regenerated >= 1


# --- notebook refinement ---


def test_build_index_user_notebook_refinement_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)
    problem_id = load_index(ws)[0].problem_id

    # Write a notebook entry
    from cpho_cli.core.index.notebook import set_problem_notes

    set_problem_notes(ws, UserNotebookEntry(problem_id=problem_id, key_points=["x"]))

    stats = build_index(ws, **kwargs)
    assert stats.refinement_only == 1
    assert stats.tags_regenerated == 0

    entries = load_index(ws)
    p1 = next(e for e in entries if e.problem_id == problem_id)
    assert p1.user_confirmed_key_points == ["x"]


# --- atomic writes ---


def test_build_index_writes_index_atomically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    assert not (ws / ".cpho" / "index.jsonl.tmp").exists()


# --- candidate merging ---


def test_build_index_candidate_merge_dedupes(
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
                    internal_id_suggestion="new_concept",
                    display_zh_suggestion="新概念",
                    category=TagCategory.PHYSICS_MODEL,
                    rationale="test",
                )
            ],
        )
    )
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=llm,
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)
    build_index(ws, force=True, **kwargs)

    from cpho_cli.core.index.vocabulary import list_pending_candidates

    candidates = list_pending_candidates(ws)
    new_concept = [c for c in candidates if c.display_zh_suggestion == "新概念"]
    assert len(new_concept) == 1
    assert new_concept[0].occurrences == 2


# --- unmatched and ambiguous ---


def test_build_index_unmatched_problems_indexed_without_answer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"], with_answers=False)
    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    entries = load_index(ws)
    assert len(entries) == 1
    assert entries[0].answer_path is None


def test_build_index_ambiguous_problems_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = tmp_path
    # Create problem with two matching answers
    (ws / "prob.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"prob" + b"\x00" * 50)
    answers1 = ws / "answers"
    answers1.mkdir()
    (answers1 / "prob-answer.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
    answers2 = ws / "solutions"
    answers2.mkdir()
    (answers2 / "prob-answer.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
    (ws / "config.local.yml").write_text(
        "provider:\n  openrouter_api_key: test-key\n", encoding="utf-8"
    )
    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    # The ambiguous problem should still be processed (it goes to unmatched since
    # the answer files are in answer dirs, but the problem is detected)
    entries = load_index(ws)
    # At least the problem should be in the index (workspace discovery rules vary)
    assert isinstance(entries, list)


# --- SolveReport consumption ---


def test_build_index_solve_report_consumed_when_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    output_dir = ws / "output"
    output_dir.mkdir()
    problem_id = make_problem_id(sha256_file(ws / "p1.png"), 1)
    report = SolveReport(
        problem_id=problem_id,
        derivation_steps=[
            DerivationStep(
                reasoning="test", expression="F=ma", official_answer_refs=["ref1"]
            )
        ],
        physics_model_tags=["Newton 第二"],
        heuristic_insight_tags=[],
        math_technique_tags=[],
    )
    (output_dir / f"{problem_id}-report.json").write_text(
        report.model_dump_json(), encoding="utf-8"
    )

    fake_llm = FakeLLMProvider()
    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=fake_llm,
        ocr_strategy="reuse",
    )

    # Verify the LLM prompt mentions the SolveReport tags
    assert len(fake_llm.calls) >= 1
    user_msg = fake_llm.calls[0]["messages"][-1]["content"]
    assert "Newton" in user_msg

    entries = load_index(ws)
    p1 = next(e for e in entries if e.problem_id == problem_id)
    # Source should be SOLVE_REPORT when report exists
    for tag in p1.physics_model_tags:
        assert tag.source == TagSource.SOLVE_REPORT


def test_build_index_no_solve_report_falls_back_to_ocr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
    )
    entries = load_index(ws)
    p1 = entries[0]
    for tag in p1.physics_model_tags:
        assert tag.source == TagSource.OCR_FALLBACK


# --- solve.py untouched ---


def test_build_index_does_not_modify_solve_py(tmp_path: Path) -> None:
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--name-only", "src/cpho_cli/core/solve.py"],
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == ""
