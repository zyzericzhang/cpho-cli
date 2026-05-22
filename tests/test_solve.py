from pathlib import Path

import pytest

from cpho_cli.core.skills import load_skill
from cpho_cli.core.solve import solve_problem
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

