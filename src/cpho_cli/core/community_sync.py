from __future__ import annotations

import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import yaml
from pydantic import ValidationError

from cpho_cli.core.errors import err_community_sync_failed
from cpho_cli.core.knowledge.store import TEXT_KNOWLEDGE_EXTENSIONS, KnowledgeError
from cpho_cli.core.knowledge.store import load_knowledge_document
from cpho_cli.models.community import (
    CommunityRepositoryConfig,
    CommunityRepositoryResult,
    CommunitySyncConfig,
    CommunitySyncResult,
)
from cpho_cli.models.knowledge import KnowledgeSource

DEFAULT_COMMUNITY_CONFIG = Path(".cpho") / "community-kb.yml"
DEFAULT_COMMUNITY_CACHE = Path.home() / ".cache" / "cpho" / "community-kb"


class CommunitySyncError(RuntimeError):
    """Raised when community KB sync cannot complete safely."""


def load_community_sync_config(workspace_root: Path, path: Path | None = None) -> CommunitySyncConfig:
    config_path = path or workspace_root / DEFAULT_COMMUNITY_CONFIG
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise CommunitySyncError(
            err_community_sync_failed(str(config_path), "Community KB config not found.")
        ) from exc
    except yaml.YAMLError as exc:
        raise CommunitySyncError(
            err_community_sync_failed(str(config_path), f"Invalid community KB config YAML: {exc}")
        ) from exc
    if not isinstance(raw, dict):
        raise CommunitySyncError(
            err_community_sync_failed(str(config_path), "Community KB config must be a YAML mapping.")
        )
    try:
        return CommunitySyncConfig.model_validate(raw)
    except ValidationError as exc:
        raise CommunitySyncError(
            err_community_sync_failed(str(config_path), f"Invalid community KB config: {exc}")
        ) from exc


def sync_community_knowledge(
    workspace_root: Path,
    *,
    config_path: Path | None = None,
    cache_dir: Path | None = None,
    force: bool = False,
    client: httpx.Client | None = None,
) -> CommunitySyncResult:
    config = load_community_sync_config(workspace_root, config_path)
    root = cache_dir or DEFAULT_COMMUNITY_CACHE
    root.mkdir(parents=True, exist_ok=True)

    own_client = client is None
    active_client = client or httpx.Client(timeout=120.0, follow_redirects=True)
    try:
        results = [
            _sync_repository(
                workspace_root,
                repository,
                cache_root=root,
                github_token=config.github_token,
                force=force,
                client=active_client,
            )
            for repository in config.repositories
            if repository.enabled
        ]
    finally:
        if own_client:
            active_client.close()
    return CommunitySyncResult(repositories=results)


def _sync_repository(
    workspace_root: Path,
    repository: CommunityRepositoryConfig,
    *,
    cache_root: Path,
    github_token: str | None,
    force: bool,
    client: httpx.Client,
) -> CommunityRepositoryResult:
    owner, repo_name = _parse_github_repo(repository.url)
    target_dir = cache_root / repo_name
    metadata_path = target_dir / "metadata.json"
    if metadata_path.exists() and not force:
        metadata = _load_metadata(metadata_path)
        if metadata.get("url") == repository.url and metadata.get("tag") == repository.tag:
            return CommunityRepositoryResult(
                repo_name=repo_name,
                tag=repository.tag,
                cache_dir=target_dir,
                metadata_path=metadata_path,
                files_written=int(metadata.get("files_written", 0)),
                skipped=True,
            )

    headers = {"Accept": "application/vnd.github+json"}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    release_url = f"https://api.github.com/repos/{owner}/{repo_name}/releases/tags/{repository.tag}"
    release_response = client.get(release_url, headers=headers)
    try:
        release_response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise CommunitySyncError(
            err_community_sync_failed(
                release_url,
                f"Community KB GitHub release request failed: {exc.response.status_code}",
            )
        ) from exc
    tarball_url = release_response.json().get("tarball_url")
    if not isinstance(tarball_url, str) or not tarball_url.strip():
        raise CommunitySyncError(
            err_community_sync_failed(release_url, "Community KB release missing tarball_url.")
        )

    tarball_response = client.get(tarball_url, headers=headers)
    try:
        tarball_response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise CommunitySyncError(
            err_community_sync_failed(
                tarball_url,
                f"Community KB tarball download failed: {exc.response.status_code}",
            )
        ) from exc

    _make_writable(target_dir)
    with tempfile.TemporaryDirectory(prefix=f"{repo_name}-", dir=str(cache_root)) as tmp_name:
        tmp_dir = Path(tmp_name)
        extracted = tmp_dir / "extracted"
        extracted.mkdir()
        _safe_extract_tarball(tarball_response.content, extracted)
        staged = tmp_dir / "staged"
        staged.mkdir()
        files_written = _stage_knowledge_files(workspace_root, extracted, staged, repo_name)
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(str(staged), target_dir)

    metadata = {
        "url": repository.url,
        "tag": repository.tag,
        "repo_name": repo_name,
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "files_written": files_written,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _make_read_only(target_dir)
    return CommunityRepositoryResult(
        repo_name=repo_name,
        tag=repository.tag,
        cache_dir=target_dir,
        metadata_path=metadata_path,
        files_written=files_written,
        skipped=False,
    )


def _parse_github_repo(url: str) -> tuple[str, str]:
    cleaned = url.rstrip("/")
    marker = "github.com/"
    if marker not in cleaned:
        raise CommunitySyncError(
            err_community_sync_failed(url, "Community KB repository must be a GitHub URL.")
        )
    path = cleaned.split(marker, 1)[1]
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        raise CommunitySyncError(
            err_community_sync_failed(
                url,
                "Community KB repository URL must include owner and repo.",
            )
        )
    return parts[0], parts[1].removesuffix(".git")


def _load_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _safe_extract_tarball(content: bytes, target_dir: Path) -> None:
    tar_path = target_dir / "archive.tar.gz"
    tar_path.write_bytes(content)
    with tarfile.open(tar_path, mode="r:*") as archive:
        target_resolved = target_dir.resolve()
        for member in archive.getmembers():
            member_path = (target_dir / member.name).resolve()
            try:
                member_path.relative_to(target_resolved)
            except ValueError as exc:
                raise CommunitySyncError(
                    err_community_sync_failed(
                        member.name,
                        "Unsafe path in community KB tarball.",
                    )
                ) from exc
        archive.extractall(target_dir, filter="data")
    tar_path.unlink(missing_ok=True)


def _stage_knowledge_files(
    workspace_root: Path,
    extracted_dir: Path,
    staged_dir: Path,
    repo_name: str,
) -> int:
    files_written = 0
    roots = [path for path in extracted_dir.iterdir() if path.is_dir()]
    search_roots = roots or [extracted_dir]
    for root in search_roots:
        for source in sorted(root.rglob("*")):
            if not source.is_file() or source.suffix.lower() not in TEXT_KNOWLEDGE_EXTENSIONS:
                continue
            relative = source.relative_to(root)
            target = staged_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            try:
                load_knowledge_document(
                    workspace_root,
                    target,
                    source=KnowledgeSource.COMMUNITY,
                    repo_name=repo_name,
                )
            except KnowledgeError as exc:
                raise CommunitySyncError(
                    err_community_sync_failed(
                        str(target),
                        f"Invalid community KB knowledge file: {exc}",
                    )
                ) from exc
            files_written += 1
    if files_written == 0:
        raise CommunitySyncError(
            err_community_sync_failed(
                str(extracted_dir),
                "Community KB tarball contained no supported knowledge files.",
            )
        )
    return files_written


def _make_writable(path: Path) -> None:
    if not path.exists():
        return
    for item in path.rglob("*"):
        try:
            os.chmod(item, 0o644)
        except OSError:
            pass
    try:
        os.chmod(path, 0o755)
    except OSError:
        pass


def _make_read_only(path: Path) -> None:
    for item in path.rglob("*"):
        try:
            os.chmod(item, 0o555 if item.is_dir() else 0o444)
        except OSError:
            pass
    try:
        os.chmod(path, 0o555)
    except OSError:
        pass
