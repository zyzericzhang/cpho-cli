"""Shared fakes for index builder tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import pytest

from cpho_cli.core.index.storage import write_index
from cpho_cli.core.index.tagging import TagRefinementOutput
from cpho_cli.models.config import ModelParams
from cpho_cli.models.documents import DocumentInput
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TaggedReference,
    TagSource,
)
from cpho_cli.models.llm import LLMResponse, LLMUsage
from cpho_cli.models.ocr import OCRBlock, OCRPageResult, OCRResult


class FakeOCRProvider:
    """Returns file content as OCR text (reads problem file as UTF-8 fallback to repr)."""

    def __init__(self, default_text: str = "fake ocr text") -> None:
        self.default_text = default_text
        self.calls = 0

    def extract(self, document: DocumentInput) -> OCRResult:
        self.calls += 1
        try:
            text = document.path.read_bytes().decode("utf-8", errors="replace")
        except Exception:
            text = self.default_text
        return OCRResult(
            pages=[
                OCRPageResult(
                    page_number=1,
                    blocks=[OCRBlock(text=text, page_number=1, confidence=1.0)],
                )
            ]
        )


class FakeLLMProvider:
    """Returns a fixed TagRefinementOutput JSON or a per-problem mapping."""

    def __init__(
        self,
        fixed_output: TagRefinementOutput | None = None,
        per_problem: dict[str, TagRefinementOutput] | None = None,
    ) -> None:
        self.fixed_output = fixed_output or TagRefinementOutput(
            selected_physics_models=["energy_conservation"],
            selected_math_techniques=["dimensional_analysis"],
            selected_heuristics=["free_body_diagram"],
            difficulty_aspects=["受力分析"],
        )
        self.per_problem = per_problem or {}
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        messages: list[dict[str, str]],
        params: ModelParams,
        response_model: type[Any] | None = None,
    ) -> LLMResponse:
        self.calls.append({"messages": messages, "params": params})
        # Try to detect problem_id from user message content
        user_content = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
                break

        output = self.fixed_output
        for pid, out in self.per_problem.items():
            if pid in user_content:
                output = out
                break

        return LLMResponse(
            content=output.model_dump_json(),
            usage=LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            raw={},
        )


def setup_workspace(
    tmp_path: Path,
    problem_names: list[str] | None = None,
    with_answers: bool = True,
    with_config: bool = True,
) -> Path:
    """Create a minimal workspace with PNG problem/answer files."""
    if problem_names is None:
        problem_names = ["p1", "p2"]

    for name in problem_names:
        (tmp_path / f"{name}.png").write_bytes(
            b"\x89PNG\r\n\x1a\n" + name.encode() + b"\x00" * 50
        )
        if with_answers:
            answer_dir = tmp_path / "answers"
            answer_dir.mkdir(exist_ok=True)
            (answer_dir / f"{name}-answer.png").write_bytes(
                b"\x89PNG\r\n\x1a\n" + f"{name}_ans".encode() + b"\x00" * 50
            )

    if with_config:
        (tmp_path / "config.local.yml").write_text(
            "provider:\n  openrouter_api_key: test-key-fake\n",
            encoding="utf-8",
        )

    return tmp_path


def make_index_entry(
    problem_id: str,
    *,
    problem_path: Path | None = None,
    ocr_cache_path: Path | None = None,
    physics_model_tags: list[str] | None = None,
    math_technique_tags: list[str] | None = None,
    heuristic_tags: list[str] | None = None,
) -> IndexEntry:
    def refs(values: list[str] | None) -> list[TaggedReference]:
        return [
            TaggedReference(internal_id=value, source=TagSource.OCR_FALLBACK, confidence=0.9)
            for value in (values or [])
        ]

    return IndexEntry(
        problem_id=problem_id,
        problem_path=problem_path or Path(f"{problem_id}.pdf"),
        problem_page_range=(1, 1),
        answer_path=None,
        indexed_at=datetime.now(timezone.utc),
        physics_model_tags=refs(physics_model_tags),
        math_technique_tags=refs(math_technique_tags),
        heuristic_tags=refs(heuristic_tags),
        difficulty_aspects=["力学建模"],
        fingerprint=IndexFingerprint(
            file=FileFingerprint(
                problem_sha256="a" * 64,
                answer_sha256=None,
                problem_size_bytes=1,
                answer_size_bytes=None,
                problem_mtime_ns=0,
            ),
            semantic=SemanticFingerprint(
                file_fp_hash="x",
                ocr_engine="rapidocr",
                ocr_engine_version="3.0",
                ocr_config_hash="y",
                tag_prompt_version="v1",
                split_prompt_version="v1",
                tag_schema_version="v2",
                model_name="m",
                model_temperature=0.0,
                vocabulary_version="builtin-v0.1+ws-none+pv-none",
            ),
        ),
        ocr_cache_path=ocr_cache_path,
        ocr_text_length=0,
        tag_prompt_version="v1",
    )


@pytest.fixture
def repl_workspace_with_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, list[str]]:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg-config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg-cache"))
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    workspace = setup_workspace(workspace_root, problem_names=["p1", "p2"], with_config=False)
    ocr_dir = workspace / ".cpho" / "ocr"
    ocr_dir.mkdir(parents=True)
    (ocr_dir / "p1.txt").write_text("牛顿第二定律与能量守恒 OCR 文本", encoding="utf-8")
    (ocr_dir / "p2.txt").write_text("几何光学 OCR 文本", encoding="utf-8")
    entries = [
        make_index_entry(
            "p1",
            problem_path=Path("p1.png"),
            ocr_cache_path=Path(".cpho/ocr/p1.txt"),
            physics_model_tags=["newton_second_law"],
            math_technique_tags=["dimensional_analysis"],
        ),
        make_index_entry(
            "p2",
            problem_path=Path("p2.png"),
            ocr_cache_path=Path(".cpho/ocr/p2.txt"),
            physics_model_tags=["geometric_optics"],
            heuristic_tags=["symmetry"],
        ),
    ]
    for entry in entries:
        IndexEntry.model_validate(entry.model_dump())
    write_index(workspace / ".cpho" / "index.jsonl", entries)
    return workspace, [entry.problem_id for entry in entries]
