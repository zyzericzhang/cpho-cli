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
    problem = tmp_path / "p1.pdf"
    answer = tmp_path / "p1-answer.pdf"
    problem.write_text("problem", encoding="utf-8")
    answer.write_text("answer", encoding="utf-8")

    result = solve_problem(problem, answer_path=answer, output_dir=tmp_path / "out", dry_run=True)

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


def test_solve_non_dry_run_uses_llm_provider(tmp_path: Path) -> None:
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
        called = False

        def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
            self.called = True
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

    assert provider.called is True
    assert result.report_json is not None
    assert "answer:1" in result.report_json.read_text(encoding="utf-8")
