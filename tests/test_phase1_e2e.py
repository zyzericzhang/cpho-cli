from cpho_cli.models.solve import DerivationStep, SolveReport


def test_phase1_report_shape_has_answer_refs_and_ocr_warnings() -> None:
    report = SolveReport(
        problem_id="fixture",
        derivation_steps=[
            DerivationStep(
                reasoning="Use conservation of energy",
                expression="mgh = 1/2 mv^2",
                official_answer_refs=["official:equation-1"],
            )
        ],
        discrepancies=[],
        ocr_warnings=["page 1 bbox [0,0,1,1] low confidence"],
        physics_model_tags=["energy-conservation"],
        heuristic_insight_tags=["choose-zero-potential"],
        math_technique_tags=["quadratic"],
    )

    assert report.derivation_steps[0].official_answer_refs
    assert report.ocr_warnings
