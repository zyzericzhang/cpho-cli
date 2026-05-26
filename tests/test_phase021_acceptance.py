from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import cpho_cli.core.index.builder as builder_module
from cpho_cli.cli.app import app
from cpho_cli.core.index.builder import build_index
from cpho_cli.core.index.hashing import sha256_file
from cpho_cli.core.index.storage import load_index
from cpho_cli.core.index.tagging import TagRefinementOutput
from cpho_cli.core.workspace import _looks_like_answer
from cpho_cli.models.config import ModelParams
from cpho_cli.models.documents import PaperFile, ProblemEntry, SplitMethod, make_problem_id
from cpho_cli.models.index import IndexEntry, IndexRunStats
from cpho_cli.models.llm import LLMResponse, LLMUsage
from cpho_cli.models.ocr import OCRBlock, OCRPageResult, OCRResult

from conftest import setup_workspace


REAL_WORKSPACE = Path("/Users/ericzhang/Desktop/物理竞赛资料")
runner = CliRunner()


def _write_pdf(path: Path, pages: list[str]) -> None:
    import fitz

    document = fitz.open()
    for text in pages:
        page = document.new_page()
        page.insert_text((72, 72), text)
    document.save(path)
    document.close()


def _write_config(workspace: Path) -> None:
    (workspace / "config.local.yml").write_text(
        "provider:\n  openrouter_api_key: test-key-fake\n",
        encoding="utf-8",
    )


class AcceptanceOCRProvider:
    def __init__(self, pages_by_name: dict[str, list[str]] | None = None) -> None:
        self.pages_by_name = pages_by_name or {}
        self.calls: list[Path] = []

    def extract(self, document: Any) -> OCRResult:
        self.calls.append(document.path)
        pages = self.pages_by_name.get(
            document.path.name,
            [f"第1题 {document.path.stem}\n识别题干", f"第2题 {document.path.stem}\n继续识别题干"],
        )
        return OCRResult(
            pages=[
                OCRPageResult(
                    page_number=index,
                    blocks=[OCRBlock(text=text, page_number=index, confidence=1.0)],
                )
                for index, text in enumerate(pages, start=1)
            ]
        )


class AcceptanceLLMProvider:
    def __init__(self) -> None:
        self.calls: list[str | None] = []

    def complete(
        self,
        messages: list[dict[str, str]],
        params: ModelParams,
        response_model: type[Any] | None = None,
    ) -> LLMResponse:
        schema_name = response_model.__name__ if response_model is not None else None
        self.calls.append(schema_name)
        if schema_name == "_LLMSplitResponse":
            raise AssertionError("Acceptance tests should not require split LLM fallback")
        if schema_name == "TopicAssignmentOutput":
            content = '{"topic_path":"力学/运动学","confidence":0.8,"rationale":"test"}'
        else:
            content = TagRefinementOutput(
                selected_physics_models=["energy_conservation"],
                selected_math_techniques=["dimensional_analysis"],
                selected_heuristics=["free_body_diagram"],
                difficulty_aspects=["受力分析"],
            ).model_dump_json()
        return LLMResponse(
            content=content,
            usage=LLMUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            raw={},
        )


def test_phase021_public_imports() -> None:
    assert PaperFile is not None
    assert ProblemEntry is not None
    assert SplitMethod.RULES.value == "rules"
    assert IndexEntry is not None
    assert IndexRunStats().problems_extracted == 0


def test_phase021_builder_writes_one_index_entry_per_problem(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(builder_module, "_rapidocr_version", lambda: "3.0.0")
    paper_path = tmp_path / "sample.pdf"
    answer_path = tmp_path / "sample-answer.pdf"
    _write_pdf(paper_path, ["paper page 1", "paper page 2"])
    _write_pdf(answer_path, ["answer page 1", "answer page 2"])
    _write_config(tmp_path)

    stats = build_index(
        tmp_path,
        config_path=tmp_path / "config.local.yml",
        ocr_provider=AcceptanceOCRProvider(
            {
                "sample.pdf": ["第1题 样例卷\nfirst problem", "第2题 样例卷\nsecond problem"],
                "sample-answer.pdf": ["第1题 样例卷\nfirst answer", "第2题 样例卷\nsecond answer"],
            }
        ),
        llm_provider=AcceptanceLLMProvider(),
        ocr_strategy="reuse",
    )

    entries = sorted(load_index(tmp_path), key=lambda entry: entry.problem_page_range)
    expected_sha = sha256_file(paper_path)
    assert stats.papers_split == 1
    assert stats.problems_extracted == 2
    assert stats.problems_extracted > stats.papers_split
    assert [entry.problem_id for entry in entries] == [
        make_problem_id(expected_sha, 1),
        make_problem_id(expected_sha, 2),
    ]
    assert [entry.problem_page_range for entry in entries] == [(1, 1), (2, 2)]
    assert [entry.problem_path for entry in entries] == [Path("sample.pdf"), Path("sample.pdf")]


def test_phase021_image_single_path_and_stale_index_discard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(builder_module, "_rapidocr_version", lambda: "3.0.0")
    workspace = setup_workspace(tmp_path, problem_names=["scan"], with_answers=False)
    stale_dir = workspace / ".cpho"
    stale_dir.mkdir(exist_ok=True)
    (stale_dir / "index.jsonl").write_text(
        '{"problem_id":"pre-split","problem_path":"old.pdf"}\n',
        encoding="utf-8",
    )

    stats = build_index(
        workspace,
        config_path=workspace / "config.local.yml",
        ocr_provider=AcceptanceOCRProvider({"scan.png": ["single image text"]}),
        llm_provider=AcceptanceLLMProvider(),
        ocr_strategy="reuse",
    )

    entries = load_index(workspace)
    assert [entry.problem_id for entry in entries] != ["pre-split"]
    assert stats.papers_split == 1
    assert stats.problems_extracted == 1
    assert stats.split_method_single == 1
    assert entries[0].problem_page_range == (1, 1)


def test_phase021_cli_renders_split_stats(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_stats = IndexRunStats(papers_split=1, problems_extracted=2)
    monkeypatch.setattr("cpho_cli.cli.app.build_index", lambda *args, **kwargs: fake_stats)

    result = runner.invoke(app, ["index", str(tmp_path)])

    assert result.exit_code == 0
    assert "切分试卷数" in result.output
    assert "提取题目数" in result.output


def _sample_real_papers() -> list[Path]:
    if not REAL_WORKSPACE.exists():
        return []
    extra_answer_markers = ("sol", "解答", "参考答案")
    papers = [
        path
        for path in sorted(REAL_WORKSPACE.rglob("*.pdf"), key=lambda item: item.as_posix())
        if path.is_file() and not _looks_like_answer(path)
        and not any(marker in path.stem.lower() for marker in extra_answer_markers)
    ]
    return papers[:3]


def test_phase021_guarded_real_workspace_offline_acceptance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sampled = _sample_real_papers()
    if not sampled:
        pytest.skip("Real physics workspace absent or has no non-answer PDFs")

    monkeypatch.setattr(builder_module, "_rapidocr_version", lambda: "3.0.0")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    pages_by_name: dict[str, list[str]] = {}
    copied_names: list[str] = []

    for index, source in enumerate(sampled, start=1):
        sample_dir = workspace / f"sample_{index}"
        sample_dir.mkdir()
        target = sample_dir / source.name
        shutil.copy2(source, target)
        copied_names.append(source.name)
        pages_by_name[source.name] = [
            f"第1题 {source.stem}\n真实工作区样本题干 1",
            f"第2题 {source.stem}\n真实工作区样本题干 2",
        ]

    _write_config(workspace)
    stats = build_index(
        workspace,
        config_path=workspace / "config.local.yml",
        ocr_provider=AcceptanceOCRProvider(pages_by_name),
        llm_provider=AcceptanceLLMProvider(),
        ocr_strategy="reuse",
    )
    entries = load_index(workspace)

    counts_by_paper: dict[str, int] = {name: 0 for name in copied_names}
    for entry in entries:
        counts_by_paper[entry.problem_path.name] += 1

    assert stats.papers_split == 3
    assert stats.problems_extracted >= 6
    assert all(count >= 2 for count in counts_by_paper.values())

    first_snippets: dict[str, str] = {}
    for source in sampled:
        matching_text = pages_by_name[source.name][0]
        assert source.stem in matching_text
        assert "第1题" in matching_text
        first_snippets[source.name] = matching_text[:80]

    record = {
        "sampled_files": copied_names,
        "problem_counts": counts_by_paper,
        "first_problem_text_snippets": first_snippets,
    }
    record_path = tmp_path / "phase021-real-workspace-acceptance.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    loaded = json.loads(record_path.read_text(encoding="utf-8"))
    assert loaded["sampled_files"]
    assert loaded["problem_counts"]
    assert loaded["first_problem_text_snippets"]
