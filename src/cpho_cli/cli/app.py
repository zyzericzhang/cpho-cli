from pathlib import Path
from typing import Optional

import typer

from cpho_cli.core.config import ConfigError
from cpho_cli.core.eval import EvalConfigError, run_eval
from cpho_cli.core.solve import SolveError, solve_problem

app = typer.Typer(help="CPHO local physics analysis CLI.")


@app.command()
def solve(
    problem: Path = typer.Argument(..., help="Problem PDF or image path."),
    answer: Optional[Path] = typer.Option(None, "--answer", "-a", help="Answer key path."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Local YAML config path."),
    output_dir: Path = typer.Option(Path("output"), "--output-dir", "-o", help="Output directory."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate inputs without LLM calls."),
) -> None:
    """Solve one physics problem."""
    try:
        result = solve_problem(
            problem,
            answer_path=answer,
            config_path=config,
            output_dir=output_dir,
            dry_run=dry_run,
        )
    except (ConfigError, SolveError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    if result.report_json is None:
        typer.echo("Dry run passed.")
        return
    typer.echo(f"Report JSON: {result.report_json}")
    if result.report_markdown is not None:
        typer.echo(f"Report Markdown: {result.report_markdown}")


@app.command(name="eval")
def eval_command(
    golden_root: Path = typer.Argument(..., help="Golden tests root directory."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Local YAML config path."),
    output_dir: Path = typer.Option(
        Path("eval-output"), "--output-dir", "-o", help="Evaluation output directory."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate cases without LLM calls."),
) -> None:
    """Run golden evaluation cases."""
    try:
        result = run_eval(golden_root, config_path=config, output_dir=output_dir, dry_run=dry_run)
    except EvalConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(
        f"Evaluation complete: total={result.total} passed={result.passed} "
        f"failed={result.failed} skipped={result.skipped}"
    )

