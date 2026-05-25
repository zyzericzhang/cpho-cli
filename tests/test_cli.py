from typer.testing import CliRunner

from cpho_cli.cli.app import app


def test_help_lists_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "solve" in result.output
    assert "index" in result.output
    assert "topic" in result.output
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
