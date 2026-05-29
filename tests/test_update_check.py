from __future__ import annotations

import httpx
from typer.testing import CliRunner

from cpho_cli import get_version
from cpho_cli.cli.app import app
from cpho_cli.core.update_check import check_for_update


def _client(status_code: int, payload: dict[str, object]) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=payload)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_check_for_update_detects_newer_release() -> None:
    client = _client(
        200,
        {
            "tag_name": "v0.2.0",
            "html_url": "https://github.com/zyzericzhang/cpho-cli/releases/tag/v0.2.0",
        },
    )

    result = check_for_update("0.1.0", client=client)

    assert result.available is True
    assert result.latest_version == "0.2.0"
    assert result.release_url == "https://github.com/zyzericzhang/cpho-cli/releases/tag/v0.2.0"
    assert result.error is None


def test_check_for_update_same_release_not_available() -> None:
    client = _client(200, {"tag_name": "v0.1.0", "html_url": "https://example.test/release"})

    result = check_for_update("0.1.0", client=client)

    assert result.available is False
    assert result.latest_version == "0.1.0"
    assert result.error is None


def test_check_for_update_reports_api_error() -> None:
    result = check_for_update("0.1.0", client=_client(404, {}))

    assert result.available is False
    assert result.error == "GitHub API returned 404"


def test_check_for_update_reports_invalid_tag() -> None:
    result = check_for_update("0.1.0", client=_client(200, {"tag_name": "not a version"}))

    assert result.available is False
    assert result.error is not None


def test_check_for_update_reports_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out")

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = check_for_update("0.1.0", client=client)

    assert result.available is False
    assert result.error == "timed out"


def test_version_command_prints_version_and_repository() -> None:
    result = CliRunner().invoke(app, ["version"])

    assert result.exit_code == 0
    assert f"cpho-cli {get_version()}" in result.output
    assert "https://github.com/zyzericzhang/cpho-cli" in result.output
