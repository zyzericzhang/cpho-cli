from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import ValidationError

from cpho_cli.core.config import load_config, resolve_model_params, resolve_provider_config
from cpho_cli.core.documents import load_document
from cpho_cli.core.llm import LLMProvider, create_llm_provider
from cpho_cli.core.ocr import OCRProvider, RapidOCRProvider
from cpho_cli.core.runtime import SkillRuntime, SkillRuntimeError
from cpho_cli.core.skill_handlers import make_llm_handler, python_tool_handler
from cpho_cli.core.skills import load_skill
from cpho_cli.models.solve import SolveReport, SolveRunResult


class SolveError(RuntimeError):
    """Raised when solve cannot run."""


def _builtin_solve_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "builtin_skills" / "solve"


def _write_report(report: SolveReport, output_dir: Path) -> SolveRunResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{report.problem_id}-report.json"
    md_path = output_dir / f"{report.problem_id}-report.md"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(
        "\n".join(
            [
                f"# Solve Report: {report.problem_id}",
                "",
                "## OCR Warnings",
                *(f"- {warning}" for warning in report.ocr_warnings),
                "",
                "## Derivation",
                *(f"- {step.expression}: {step.reasoning}" for step in report.derivation_steps),
            ]
        ),
        encoding="utf-8",
    )
    return SolveRunResult(report_json=json_path, report_markdown=md_path, warnings=report.ocr_warnings)


def solve_problem(
    problem_path: Path,
    answer_path: Path | None = None,
    config_path: Path | None = None,
    provider_name: str | None = None,
    output_dir: Path = Path("output"),
    dry_run: bool = False,
    ocr_provider: OCRProvider | None = None,
    llm_provider: LLMProvider | None = None,
) -> SolveRunResult:
    if not problem_path.exists():
        raise SolveError(f"Problem file not found: {problem_path}")
    if answer_path is None or not answer_path.exists():
        raise SolveError("Missing answer key. Provide --answer or use workspace pairing.")

    if dry_run:
        load_skill(_builtin_solve_skill_dir())
        return SolveRunResult(report_json=None, warnings=[])

    config = load_config(config_path)
    provider_config = resolve_provider_config(config, os.environ, provider_name)
    problem_doc = load_document(problem_path)
    answer_doc = load_document(answer_path)
    ocr = ocr_provider or RapidOCRProvider()
    problem_ocr = ocr.extract(problem_doc)
    answer_ocr = ocr.extract(answer_doc)
    warnings = [
        f"page {block.page_number}: {block.text}"
        for page in problem_ocr.pages
        for block in page.blocks
        if block.low_confidence
    ]
    provider = llm_provider or create_llm_provider(
        kind=provider_config.kind,
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
        timeout=provider_config.timeout,
    )
    params = resolve_model_params(config, "solve", provider_name=provider_name)
    skill = load_skill(_builtin_solve_skill_dir())
    runtime = SkillRuntime(
        handlers={
            "python_tool": python_tool_handler,
            "llm": make_llm_handler(provider, params, skill.root),
        },
        secrets=[provider_config.api_key],
    )
    try:
        result = runtime.run(
            skill.spec,
            {
                "problem_text": problem_ocr.text,
                "answer_text": answer_ocr.text,
                "ocr_warnings": warnings,
                "problem_path": str(problem_path),
                "answer_path": str(answer_path),
                "problem_file": problem_path,
                "answer_file": answer_path,
            },
        )
        raw_report = result.blackboard["solve_report"]
        if isinstance(raw_report, SolveReport):
            report = raw_report
        elif isinstance(raw_report, str):
            report = SolveReport.model_validate_json(raw_report)
        else:
            report = SolveReport.model_validate(raw_report)
    except (SkillRuntimeError, ValidationError) as exc:
        raise SolveError(f"Solve skill failed: {exc}") from exc
    if warnings:
        report.ocr_warnings = sorted(set(report.ocr_warnings + warnings))
    return _write_report(report, output_dir)


def report_has_assertion(report_path: Path, assertion: str) -> bool:
    data = json.loads(report_path.read_text(encoding="utf-8"))
    return assertion in json.dumps(data, ensure_ascii=False)
