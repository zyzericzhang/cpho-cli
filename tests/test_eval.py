from pathlib import Path

import pytest

from cpho_cli.core.eval import EvalConfigError, load_eval_cases, run_eval


def write_case(root: Path) -> None:
    case = root / "case1"
    case.mkdir(parents=True)
    (case / "EXPECTATION.md").write_text("Must reference official answer.", encoding="utf-8")
    (case / "spec.yml").write_text(
        """
id: case1
problem: problem.pdf
answer: answer.pdf
criteria:
  - id: C1
    area: grounding
    priority: must
    expectation: final report references official answer
""",
        encoding="utf-8",
    )


def test_load_eval_case(tmp_path: Path) -> None:
    write_case(tmp_path)

    cases = load_eval_cases(tmp_path)

    assert cases[0].id == "case1"
    assert cases[0].criteria[0].id == "C1"


def test_invalid_eval_case_fails(tmp_path: Path) -> None:
    case = tmp_path / "case1"
    case.mkdir()
    (case / "spec.yml").write_text("id: case1\ncriteria: []\n", encoding="utf-8")

    with pytest.raises(EvalConfigError):
        load_eval_cases(tmp_path)


def test_run_eval_dry_run_reports_skipped_missing_files(tmp_path: Path) -> None:
    write_case(tmp_path)

    result = run_eval(tmp_path, output_dir=tmp_path / "out", dry_run=True)

    assert result.total == 1
    assert result.skipped == 1
    assert (tmp_path / "out" / "eval-report.json").exists()

