from __future__ import annotations

import json
from pathlib import Path

import yaml
from pydantic import ValidationError

from cpho_cli.core.solve import solve_problem
from cpho_cli.models.eval import EvalCase, EvalRunResult


class EvalConfigError(ValueError):
    """Raised when golden evaluation config is invalid."""


def load_eval_cases(root: Path) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for spec_path in sorted(root.glob("*/spec.yml")):
        try:
            raw = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
            raw["problem"] = spec_path.parent / raw.get("problem", "")
            raw["answer"] = spec_path.parent / raw.get("answer", "")
            expectation = spec_path.parent / "EXPECTATION.md"
            if expectation.exists():
                raw["expectation_markdown"] = expectation
            cases.append(EvalCase.model_validate(raw))
        except (yaml.YAMLError, ValidationError) as exc:
            raise EvalConfigError(f"Invalid eval case {spec_path}: {exc}") from exc
    return cases


def run_eval(
    root: Path,
    config_path: Path | None = None,
    provider_name: str | None = None,
    output_dir: Path = Path("eval-output"),
    dry_run: bool = False,
) -> EvalRunResult:
    cases = load_eval_cases(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    passed = failed = skipped = 0
    for case in cases:
        if dry_run or not case.problem.exists() or not case.answer.exists():
            skipped += 1
            rows.append({"id": case.id, "status": "SKIPPED", "reason": "dry-run or missing files"})
            continue
        result = solve_problem(
            case.problem,
            answer_path=case.answer,
            config_path=config_path,
            provider_name=provider_name,
            output_dir=output_dir / case.id,
        )
        if result.report_json is None:
            skipped += 1
            rows.append({"id": case.id, "status": "SKIPPED", "reason": "no report"})
            continue
        passed += 1
        rows.append({"id": case.id, "status": "PASS", "reason": ""})
    total = len(cases)
    failed = total - passed - skipped
    report_json = output_dir / "eval-report.json"
    report_markdown = output_dir / "eval-report.md"
    report_json.write_text(
        json.dumps({"total": total, "passed": passed, "failed": failed, "skipped": skipped, "cases": rows}, indent=2),
        encoding="utf-8",
    )
    report_markdown.write_text(
        "\n".join(["# Eval Report", "", *(f"- {row['id']}: {row['status']}" for row in rows)]),
        encoding="utf-8",
    )
    return EvalRunResult(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        report_json=report_json,
        report_markdown=report_markdown,
    )
