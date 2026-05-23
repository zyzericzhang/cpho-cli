from __future__ import annotations

from typer.testing import CliRunner

from cpho_cli.cli.app import app

runner = CliRunner()


def test_topic_list_shows_tree() -> None:
    result = runner.invoke(app, ["topic", "list"])
    assert result.exit_code == 0
    assert "力学" in result.output


def test_topic_browse_help() -> None:
    result = runner.invoke(app, ["topic", "browse", "--help"])
    assert result.exit_code == 0
    assert "主题路径" in result.output


def test_compose_help() -> None:
    result = runner.invoke(app, ["compose", "--help"])
    assert result.exit_code == 0
    assert "--topic" in result.output
    assert "--tags" in result.output
