import json
from pathlib import Path

import pytest

from cpho_cli.core.skills import load_skill
from cpho_cli.core.solve import solve_problem
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import LLMResponse
from cpho_cli.models.ocr import OCRBlock, OCRPageResult, OCRResult
from cpho_cli.models.solve import DerivationStep, SolveReport


def test_builtin_solve_skill_loads() -> None:
    loaded = load_skill(Path("src/cpho_cli/builtin_skills/solve"))

    assert loaded.spec.name == "solve"
    assert [step.id for step in loaded.spec.steps] == [
        "extract_problem_answer",
        "normalize_problem",
        "validate_answer_structure",
        "derive_subproblems",
        "cross_check_official_answer",
        "mark_discrepancies",
        "assemble_final_report",
    ]


def test_solve_schema_requires_answer_references() -> None:
    with pytest.raises(Exception):
        DerivationStep(reasoning="because", expression="F=ma", official_answer_refs=[])


def test_solve_dry_run_does_not_require_api_key(tmp_path: Path) -> None:
    class FailingProvider:
        def complete(self, messages, params, response_model=None):  # type: ignore[no-untyped-def]
            raise AssertionError("dry run must not call provider.complete")

    problem = tmp_path / "p1.pdf"
    answer = tmp_path / "p1-answer.pdf"
    problem.write_text("problem", encoding="utf-8")
    answer.write_text("answer", encoding="utf-8")

    result = solve_problem(
        problem,
        answer_path=answer,
        output_dir=tmp_path / "out",
        dry_run=True,
        llm_provider=FailingProvider(),
    )

    assert result.report_json is None
    assert result.warnings == []


def test_solve_report_contains_ocr_warnings() -> None:
    report = SolveReport(
        problem_id="p1",
        derivation_steps=[
            DerivationStep(
                reasoning="Newton second law",
                expression="F=ma",
                official_answer_refs=["answer:1"],
            )
        ],
        discrepancies=[],
        ocr_warnings=["low confidence alpha"],
        physics_model_tags=["newton"],
        heuristic_insight_tags=["force-balance"],
        math_technique_tags=["algebra"],
    )

    assert report.ocr_warnings == ["low confidence alpha"]


def test_solve_non_dry_run_executes_builtin_skill_steps(tmp_path: Path) -> None:
    class FakeOCR:
        def extract(self, document):  # type: ignore[no-untyped-def]
            return OCRResult(
                pages=[
                    OCRPageResult(
                        page_number=1,
                        blocks=[
                            OCRBlock(
                                text="problem or answer text",
                                page_number=1,
                                confidence=1.0,
                            )
                        ],
                    )
                ]
            )

    class FakeProvider:
        prompts: list[str]
        response_models: list[object]

        def __init__(self) -> None:
            self.prompts = []
            self.response_models = []

        def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
            self.prompts.append(messages[-1]["content"])
            self.response_models.append(response_model)
            responses = [
                {"normalized_problem": "normalized problem"},
                {"answer_structure": "answer structure"},
                {"subproblem_derivations": "F=ma derivation"},
                {"answer_cross_check": "answer refs checked"},
                {"discrepancies": []},
            ]
            if len(self.prompts) <= len(responses):
                return LLMResponse(content=json.dumps(responses[len(self.prompts) - 1]))
            assert response_model is SolveReport
            return LLMResponse(
                content=SolveReport(
                    problem_id="p1",
                    derivation_steps=[
                        DerivationStep(
                            reasoning="Use Newton second law",
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

    problem = tmp_path / "p1.png"
    answer = tmp_path / "p1-answer.png"
    config = tmp_path / "config.yml"
    problem.write_bytes(b"problem")
    answer.write_bytes(b"answer")
    config.write_text("provider:\n  openrouter_api_key: sk-test\n", encoding="utf-8")
    provider = FakeProvider()

    result = solve_problem(
        problem,
        answer_path=answer,
        config_path=config,
        output_dir=tmp_path / "out",
        dry_run=False,
        ocr_provider=FakeOCR(),
        llm_provider=provider,
    )

    assert len(provider.prompts) == 6
    assert "Problem OCR text:" in provider.prompts[0]
    assert "Official answer OCR text:" in provider.prompts[1]
    assert "Normalized problem:" in provider.prompts[2]
    assert "Cross-check:" in provider.prompts[4]
    assert provider.response_models[-1] is SolveReport
    assert result.report_json is not None
    assert "answer:1" in result.report_json.read_text(encoding="utf-8")
