from __future__ import annotations

import io
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml

from cpho_cli.core.community_sync import sync_community_knowledge
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


def _write_vocab(workspace: Path) -> None:
    path = workspace / ".cpho" / "vocabulary" / "private.yml"
    path.parent.mkdir(parents=True)
    path.write_text(
        yaml.safe_dump(
            {
                "version": "phase8",
                "tags": [
                    {
                        "internal_id": "phase8_model",
                        "display_zh": "Phase 8 模型",
                        "category": "physics_model",
                    }
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _entry() -> IndexEntry:
    return IndexEntry(
        problem_id="phase8-p1",
        problem_path=Path("真实题目/phase8.pdf"),
        problem_page_range=(1, 1),
        indexed_at=datetime.now(timezone.utc),
        physics_model_tags=[
            TaggedReference(internal_id="phase8_model", source=TagSource.USER_NOTE)
        ],
        fingerprint=IndexFingerprint(
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
                vocabulary_version="phase8",
            ),
        ),
        ocr_text_length=12,
        tag_prompt_version="v1",
    )


def _tarball() -> bytes:
    knowledge = "\n".join(
        [
            "---",
            "canonical_tag_id: phase8_model",
            "standardized: true",
            "last_normalized_hash: abc",
            "last_user_edit_hash: abc",
            "title: Phase 8 社区知识",
            "---",
            "",
            "社区知识内容。",
        ]
    ).encode("utf-8")
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        info = tarfile.TarInfo("owner-repo-hash/knowledge/phase8.md")
        info.size = len(knowledge)
        archive.addfile(info, io.BytesIO(knowledge))
    return buffer.getvalue()


def _client() -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url).endswith("/releases/tags/v1.0.0"):
            return httpx.Response(200, json={"tarball_url": "https://example.test/archive.tgz"})
        if str(request.url) == "https://example.test/archive.tgz":
            return httpx.Response(200, content=_tarball())
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def test_phase8_sync_resolver_and_error_docs_acceptance(
    monkeypatch,
    tmp_path: Path,
) -> None:
    _write_vocab(tmp_path)
    write_index(tmp_path / ".cpho" / "index.jsonl", [_entry()])
    config_path = tmp_path / ".cpho" / "community-kb.yml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "repositories": [
                    {
                        "url": "https://github.com/cpho/phase8-kb",
                        "tag": "v1.0.0",
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    cache_dir = tmp_path / "community-cache"

    result = sync_community_knowledge(
        tmp_path,
        config_path=config_path,
        cache_dir=cache_dir,
        client=_client(),
    )
    monkeypatch.setenv("CPHO_COMMUNITY_KB_DIR", str(cache_dir))

    synced_file = cache_dir / "phase8-kb" / "knowledge" / "phase8.md"
    matches = KnowledgeResolver(tmp_path).find_for_problem("phase8-p1")

    assert result.repositories[0].files_written == 1
    assert synced_file.exists()
    assert synced_file.stat().st_mode & 0o222 == 0
    assert matches[0].source is KnowledgeSource.COMMUNITY
    assert matches[0].repo_name == "phase8-kb"
    for name in [
        "err_config_missing_api_key",
        "err_api_call_failed",
        "err_skill_prompt_missing",
        "err_knowledge_frontmatter_invalid",
        "err_community_sync_failed",
    ]:
        assert (Path("docs/user/errors") / f"{name}.md").exists()

