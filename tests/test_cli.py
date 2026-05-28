from typer.testing import CliRunner

from cpho_cli.cli.app import app


def test_help_lists_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "solve" in result.output
    assert "index" in result.output
    assert "topic" in result.output
    assert "knowledge" in result.output
    assert "diagnostics" in result.output
    assert "eval" not in result.output


def test_solve_help_lists_options() -> None:
    result = CliRunner().invoke(app, ["solve", "--help"])

    assert result.exit_code == 0
    assert "--answer" in result.output
    assert "--config" in result.output
    assert "--provider" in result.output
    assert "--output-dir" in result.output
    assert "--dry-run" in result.output


def test_removed_eval_command_is_unavailable() -> None:
    result = CliRunner().invoke(app, ["eval", "--help"])

    assert result.exit_code != 0


def test_diagnostics_packaging_smoke_reports_runtime_checks() -> None:
    result = CliRunner().invoke(app, ["diagnostics", "--packaging-smoke"])

    assert result.exit_code == 0
    assert "OK package version:" in result.output
    assert "OK package data builtin_skills:" in result.output
    assert "OK package data vocabulary YAML:" in result.output
    assert "OK package data model catalog JSON:" in result.output
    assert "OK fitz import:" in result.output
    assert "OK rapidocr import:" in result.output
    assert "OK onnxruntime import:" in result.output
