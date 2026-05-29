from __future__ import annotations

import httpx
from packaging.version import InvalidVersion, Version

from cpho_cli.models.update import UpdateCheckResult


def check_for_update(
    current_version: str,
    *,
    repo: str = "zyzericzhang/cpho-cli",
    client: httpx.Client | None = None,
    timeout: float = 1.5,
) -> UpdateCheckResult:
    result_kwargs = {"current_version": current_version}
    close_client = client is None
    http_client = client or httpx.Client(timeout=timeout)
    try:
        response = http_client.get(f"https://api.github.com/repos/{repo}/releases/latest")
        if response.status_code != 200:
            return UpdateCheckResult(
                **result_kwargs, error=f"GitHub API returned {response.status_code}"
            )
        payload = response.json()
        raw_tag = payload.get("tag_name")
        if not isinstance(raw_tag, str) or not raw_tag.strip():
            return UpdateCheckResult(**result_kwargs, error="latest release has no tag_name")
        latest = raw_tag.strip().removeprefix("v")
        release_url = payload.get("html_url")
        if release_url is not None and not isinstance(release_url, str):
            release_url = None
        current = Version(current_version.removeprefix("v"))
        latest_version = Version(latest)
        return UpdateCheckResult(
            available=latest_version > current,
            current_version=current_version,
            latest_version=latest,
            release_url=release_url,
        )
    except (httpx.HTTPError, ValueError, InvalidVersion) as exc:
        return UpdateCheckResult(**result_kwargs, error=str(exc))
    finally:
        if close_client:
            http_client.close()
