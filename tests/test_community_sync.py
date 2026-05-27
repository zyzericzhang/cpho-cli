from __future__ import annotations

import io
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
import yaml

from cpho_cli.core.community_sync import CommunitySyncError, sync_community_knowledge
from cpho_cli.core.index.storage import write_index
from cpho_cli.core.knowledge import KnowledgeResolver
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    TagSource,
    TaggedReference,
)
from cpho_cli.models.knowledge import KnowledgeSource


def _write_private_vocab(workspace: Path) -> None:
    path = workspace / ".cpho" / "vocabulary" / "private.yml"
    path.parent.mkdir(parents=True)
    path.write_text(
        yaml.safe_dump(
            {
                "version": "test",
                "tags": [
                    {
                        "internal_id": "test_model_a",
                        "display_zh": "测试模型 A",
                        "category": "physics_model",
                    },
                    {
                        "internal_id": "test_model_b",
                        "display_zh": "测试模型 B",
                        "category": "physics_model",
                    },
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _fingerprint() -> IndexFingerprint:
    return IndexFingerprint(
        file=FileFingerprint(
            problem_sha256="a" * 64,
            answer_sha256=None,
            problem_size_bytes=1,
            answer_size_bytes=None,
            problem_mtime_ns=0,
        ),
        semantic=SemanticFingerprint(
            file_fp_hash="x",
            ocr_engine="rapidocr",
            ocr_engine_version="3.0",
            ocr_config_hash="y",
            tag_prompt_version="v1",
            split_prompt_version="v1",
            tag_schema_version="v2",
            model_name="m",
            model_temperature=0.0,
            vocabulary_version="test",
        ),
    )


def _entry(problem_id: str = "p1", tag_id: str = "test_model_a") -> IndexEntry:
    return IndexEntry(
        problem_id=problem_id,
        problem_path=Path("真实题目/第四届芝麻物理联考.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime.now(timezone.utc),
        physics_model_tags=[TaggedReference(internal_id=tag_id, source=TagSource.USER_NOTE)],
        fingerprint=_fingerprint(),
        ocr_text_length=12,
        tag_prompt_version="v1",
    )


def _knowledge_text(tag_id: str = "test_model_a", title: str = "社区知识") -> str:
    return "\n".join(
        [
            "---",
            f"canonical_tag_id: {tag_id}",
            "standardized: true",
            "last_normalized_hash: abc",
            "last_user_edit_hash: abc",
            f"title: {title}",
            "---",
            "",
            "这是社区知识库同步得到的内容。",
        ]
    )


def _tarball(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, text in files.items():
            payload = text.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    return buffer.getvalue()


def _client_for_tarball(content: bytes) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url).endswith("/releases/tags/v1.0.0"):
            return httpx.Response(200, json={"tarball_url": "https://example.test/tarball"})
        if str(request.url) == "https://example.test/tarball":
            return httpx.Response(200, content=content)
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def _write_sync_config(workspace: Path) -> Path:
    config = workspace / ".cpho" / "community-kb.yml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        yaml.safe_dump(
            {
                "repositories": [
                    {
                        "url": "https://github.com/cpho/example-kb",
                        "tag": "v1.0.0",
                        "enabled": True,
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return config


def test_sync_downloads_release_tarball_to_read_only_cache(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    config = _write_sync_config(tmp_path)
    cache_dir = tmp_path / "cache"
    client = _client_for_tarball(
        _tarball({"owner-repo-hash/docs/model.md": _knowledge_text("test_model_a")})
    )

    result = sync_community_knowledge(
        tmp_path,
        config_path=config,
        cache_dir=cache_dir,
        client=client,
    )

    repo = result.repositories[0]
    assert repo.repo_name == "example-kb"
    assert repo.files_written == 1
    synced_file = cache_dir / "example-kb" / "docs" / "model.md"
    assert synced_file.exists()
    assert not (tmp_path / ".cpho" / "knowledge" / "files" / "docs" / "model.md").exists()
    assert synced_file.stat().st_mode & 0o222 == 0
    assert repo.metadata_path.exists()


def test_sync_skips_same_release_without_force(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    config = _write_sync_config(tmp_path)
    cache_dir = tmp_path / "cache"
    client = _client_for_tarball(_tarball({"repo/first.md": _knowledge_text()}))
    first = sync_community_knowledge(tmp_path, config_path=config, cache_dir=cache_dir, client=client)

    skipped = sync_community_knowledge(
        tmp_path,
        config_path=config,
        cache_dir=cache_dir,
        client=_client_for_tarball(_tarball({"repo/second.md": _knowledge_text()})),
    )

    assert first.repositories[0].skipped is False
    assert skipped.repositories[0].skipped is True
    assert not (cache_dir / "example-kb" / "second.md").exists()


def test_sync_force_refreshes_cache(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    config = _write_sync_config(tmp_path)
    cache_dir = tmp_path / "cache"
    sync_community_knowledge(
        tmp_path,
        config_path=config,
        cache_dir=cache_dir,
        client=_client_for_tarball(_tarball({"repo/first.md": _knowledge_text()})),
    )

    refreshed = sync_community_knowledge(
        tmp_path,
        config_path=config,
        cache_dir=cache_dir,
        client=_client_for_tarball(_tarball({"repo/second.md": _knowledge_text()})),
        force=True,
    )

    assert refreshed.repositories[0].skipped is False
    assert not (cache_dir / "example-kb" / "first.md").exists()
    assert (cache_dir / "example-kb" / "second.md").exists()


def test_sync_rejects_invalid_knowledge_frontmatter(tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    config = _write_sync_config(tmp_path)
    bad = "\n".join(["---", "canonical_tag_id: missing_tag", "---", "", "bad"])

    with pytest.raises(CommunitySyncError, match="Invalid community KB knowledge file"):
        sync_community_knowledge(
            tmp_path,
            config_path=config,
            cache_dir=tmp_path / "cache",
            client=_client_for_tarball(_tarball({"repo/bad.md": bad})),
        )


def test_resolver_reads_community_cache_after_private(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_private_vocab(tmp_path)
    write_index(tmp_path / ".cpho" / "index.jsonl", [_entry()])
    cache_dir = tmp_path / "cache"
    config = _write_sync_config(tmp_path)
    sync_community_knowledge(
        tmp_path,
        config_path=config,
        cache_dir=cache_dir,
        client=_client_for_tarball(_tarball({"repo/model.md": _knowledge_text()})),
    )
    monkeypatch.setenv("CPHO_COMMUNITY_KB_DIR", str(cache_dir))

    matches = KnowledgeResolver(tmp_path).find_for_problem("p1")

    assert len(matches) == 1
    assert matches[0].source is KnowledgeSource.COMMUNITY
    assert matches[0].repo_name == "example-kb"
