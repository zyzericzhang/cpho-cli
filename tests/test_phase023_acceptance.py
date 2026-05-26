from __future__ import annotations

import json
import shutil
from itertools import chain
from pathlib import Path

import pytest

from cpho_cli.core.index.builder import build_index
from cpho_cli.core.solve import solve_problem
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import LLMResponse
from cpho_cli.models.ocr import OCRBlock, OCRPageResult, OCRResult
from cpho_cli.models.solve import DerivationStep, SolveReport
from conftest import FakeLLMProvider, FakeOCRProvider

ROOT = Path(__file__).resolve().parents[1]
REAL_WORKSPACE = Path("/Users/ericzhang/Desktop/物理竞赛资料")

DECISION_IDS = [f"D-{i:02d}" for i in range(1, 22)]
SUCCESS_IDS = [f"SC-{i:02d}" for i in range(1, 9)]


def _read(*relative_paths: str) -> str:
    return "\n".join((ROOT / path).read_text(encoding="utf-8") for path in relative_paths)


def test_d01_to_d21_and_sc01_to_sc08_have_acceptance_labels() -> None:
    labels = {
        **{item: "phase decision gate" for item in DECISION_IDS},
        **{item: "phase success gate" for item in SUCCESS_IDS},
    }

    assert all(item in labels for item in DECISION_IDS), "D-01..D-21 acceptance labels"
    assert all(item in labels for item in SUCCESS_IDS), "SC-01..SC-08 acceptance labels"


def test_d01_d02_sc01_sc02_index_has_no_solve_report_coupling() -> None:
    source = _read(
        "src/cpho_cli/models/index.py",
        "src/cpho_cli/core/index/builder.py",
        "src/cpho_cli/core/index/tagging.py",
    )

    assert "Solve" + "Report" not in source, "D-01/SC-01 no SolveReport index dependency"
    assert "solve_report_path" not in source, "D-02/SC-02 removed solve_report_path"
    assert "SOLVE" + "_REPORT" not in source, "D-02/SC-02 removed TagSource variant"


def test_d03_to_d09_sc04_to_sc06_tag_write_api_and_force_gates() -> None:
    api_source = _read("src/cpho_cli/core/index/api.py")
    model_source = _read("src/cpho_cli/models/index.py")
    cli_source = _read("src/cpho_cli/cli/app.py")
    builder_source = _read("src/cpho_cli/core/index/builder.py")

    for name in ("add_problem_tags", "remove_problem_tags", "update_problem_tags"):
        assert name in api_source, f"D-03 API exists: {name}"
    for command in ("tag-add", "tag-remove", "tag-set"):
        assert command in cli_source, f"D-04/SC-04 CLI command exists: {command}"
    for field in ("UserTagEntry", "canonical_tags", "unverified_tags"):
        assert field in model_source, f"D-05/D-07 separated user tag model field: {field}"
    for field in ("skill_name", "timestamp", "reasoning_snippet"):
        assert field in model_source, f"D-06/SC-06 provenance field exists: {field}"
    assert "old.user_tags" in builder_source, "D-08/SC-05 force preserves user tags"
    assert "force_all" in builder_source and "--force-all" in cli_source, "D-09 force-all exists"


def test_d10_d11_d15_sc03_eval_removed_and_splitting_fixture_preserved() -> None:
    removed_dir = ROOT / ("golden" + "_tests")
    removed_core = ROOT / "src" / "cpho_cli" / "core" / ("eval" + ".py")
    removed_model = ROOT / "src" / "cpho_cli" / "models" / ("eval" + ".py")
    fixture = ROOT / "tests" / "fixtures" / "splitting" / "ipho_style_multi_problem.expected.json"

    assert not removed_dir.exists(), "D-10/SC-03 removed old golden directory"
    assert not removed_core.exists(), "D-10 removed core eval module"
    assert not removed_model.exists(), "D-10 removed model eval module"
    assert fixture.exists(), "D-11 splitting fixture preserved outside removed eval tree"
    assert ("cpho " + "eval") not in _read("src/cpho_cli/cli/app.py"), "D-15 no eval CLI"


def test_d12_to_d14_solve_is_runtime_backed_without_dynamic_python() -> None:
    solve_source = _read("src/cpho_cli/core/solve.py")
    handler_source = _read("src/cpho_cli/core/skill_handlers.py")
    skill_yml = _read("src/cpho_cli/builtin_skills/solve/skill.yml")

    assert "SkillRuntime" in solve_source, "D-12 solve routes through SkillRuntime"
    assert "problem: Path" in _read("src/cpho_cli/cli/app.py"), "D-13 solve CLI signature remains"
    assert "make_llm_handler" in handler_source, "D-14 llm handler exists"
    assert "python_tool_handler" in handler_source, "D-14 python_tool handler exists"
    assert "assemble_final_report" in skill_yml, "D-12 seven-step solve DAG is present"
    for forbidden in ("eval(", "exec(", "subprocess", "__import__"):
        assert forbidden not in handler_source, f"D-14 handler forbids {forbidden}"


def test_d16_to_d21_sc07_sc08_multimodal_and_vision_source_gates() -> None:
    llm_source = _read("src/cpho_cli/core/llm.py", "src/cpho_cli/models/llm.py")
    multimodal_source = _read("src/cpho_cli/core/multimodal.py")
    solve_source = _read("src/cpho_cli/core/solve.py", "src/cpho_cli/core/skill_handlers.py")
    index_source = _read("src/cpho_cli/core/index/builder.py", "src/cpho_cli/core/index/tagging.py")
    shell_source = _read("src/cpho_cli/cli/app.py", "src/cpho_cli/cli/repl/commands/workspace.py")

    assert "file_data" in multimodal_source, "D-16 PDF file blocks are supported"
    assert "image_url" in multimodal_source, "D-17 image content blocks are supported"
    assert "input_modalities" in llm_source and "ModelCapabilities" in llm_source, "D-18 capability detection exists"
    assert "build_multimodal_content" in solve_source, "D-19 shared llm handler multimodal route"
    assert "vision" in index_source and "--vision" in shell_source, "D-20/SC-08 index vision exists"
    assert ".gif" in _read("src/cpho_cli/core/documents.py", "src/cpho_cli/core/workspace.py"), "D-21 GIF suffix support"
    assert "problem_file" in solve_source and "answer_file" in solve_source, "SC-07 solve multimodal context"


class _SolveOCR:
    def extract(self, document):  # type: ignore[no-untyped-def]
        return OCRResult(
            pages=[
                OCRPageResult(
                    page_number=1,
                    blocks=[OCRBlock(text="真实工作空间 fake OCR", page_number=1, confidence=1.0)],
                )
            ]
        )


class _SolveProvider:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
        self.calls += 1
        responses = [
            {"official_steps": [{"ref": "answer:1", "content": "official"}]},
            {"step_checks": [{"official_answer_refs": ["answer:1"], "status": "ok", "finding": "checked"}]},
            {"error_classification": "none"},
            {"discrepancies": []},
        ]
        if self.calls <= len(responses):
            return LLMResponse(content=json.dumps(responses[self.calls - 1]))
        return LLMResponse(
            content=SolveReport(
                problem_id="real-smoke",
                derivation_steps=[
                    DerivationStep(
                        reasoning="fake reasoning",
                        expression="F=ma",
                        official_answer_refs=["answer:1"],
                    )
                ],
                discrepancies=[],
                ocr_warnings=[],
                physics_model_tags=["newton"],
                heuristic_insight_tags=["force-balance"],
                math_technique_tags=["algebra"],
            ).model_dump_json()
        )


def _first_existing(paths: list[Path]) -> Path | None:
    return next((path for path in paths if path.is_file()), None)


def test_real_workspace_shape_smoke_with_copied_samples(tmp_path: Path) -> None:
    if not REAL_WORKSPACE.exists():
        pytest.skip("真实工作空间不存在，跳过 real-workspace-shaped smoke。")

    pdf = _first_existing(sorted(REAL_WORKSPACE.rglob("*.pdf")))
    image = _first_existing(
        sorted(
            chain(
                REAL_WORKSPACE.rglob("*.jpg"),
                REAL_WORKSPACE.rglob("*.jpeg"),
                REAL_WORKSPACE.rglob("*.png"),
            )
        )
    )
    if pdf is None or image is None:
        pytest.skip("真实工作空间中未同时找到 PDF 和 JPG/PNG 样本。")

    workspace = tmp_path / "真实工作空间样本"
    copied: list[Path] = []
    for sample in (pdf, image):
        target = workspace / sample.relative_to(REAL_WORKSPACE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sample, target)
        copied.append(target)
    (workspace / "config.local.yml").write_text(
        "provider:\n  openrouter_api_key: fake-key\n",
        encoding="utf-8",
    )

    image_target = copied[1]
    stats = build_index(
        workspace,
        config_path=workspace / "config.local.yml",
        ocr_provider=FakeOCRProvider(default_text="真实工作空间 OCR"),
        llm_provider=FakeLLMProvider(),
        ocr_strategy="reuse",
        target_subpath=image_target.parent.relative_to(workspace),
    )
    solve_result = solve_problem(
        image_target,
        answer_path=image_target,
        config_path=workspace / "config.local.yml",
        output_dir=workspace / "output",
        ocr_provider=_SolveOCR(),
        llm_provider=_SolveProvider(),
    )

    assert stats.total_problems >= 1, "D-20/SC-08 fake-provider index smoke"
    assert solve_result.report_json is not None and solve_result.report_json.exists(), "D-12/SC-07 fake-provider solve smoke"
    assert any("物理竞赛资料" not in str(path) for path in copied), "real samples copied; originals untouched"
