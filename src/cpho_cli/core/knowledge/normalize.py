from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jinja2
import yaml

from cpho_cli.core.config import load_config, resolve_model_params, resolve_provider_config
from cpho_cli.core.documents import IMAGE_EXTENSIONS
from cpho_cli.core.index.vocabulary import load_merged_vocabulary
from cpho_cli.core.json_utils import loads_json_object
from cpho_cli.core.knowledge.store import KnowledgeError, load_knowledge_document
from cpho_cli.core.llm import LLMProvider, create_llm_provider
from cpho_cli.core.multimodal import build_multimodal_content
from cpho_cli.models.config import ModelParams
from cpho_cli.models.knowledge import KnowledgeDocument, KnowledgeSource
from cpho_cli.models.llm import ModelCapabilities

TEXT_EXTENSIONS = {".md", ".markdown", ".tex", ".txt", ".rst"}
DOCX_EXTENSIONS = {".docx"}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]+", "-", value).strip("-")
    return slug or "knowledge"


def _draft_path(workspace_root: Path, source_path: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return (
        workspace_root
        / ".cpho"
        / "knowledge"
        / "drafts"
        / f"{timestamp}-{_slug(source_path.stem)}.md"
    )


def _prompt_template() -> jinja2.Template:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(Path(__file__).parent / "prompts")),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )
    return env.get_template("normalize_knowledge.md.j2")


def _read_source_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix in DOCX_EXTENSIONS:
        import mammoth

        with path.open("rb") as handle:
            result = mammoth.convert_to_markdown(handle)
        return result.value
    raise KnowledgeError(f"Knowledge normalize requires LLM for non-text file: {path}")


def _resolve_provider(
    config_path: Path | None,
    provider_name: str | None,
) -> tuple[LLMProvider, ModelParams, ModelCapabilities]:
    config = load_config(config_path)
    provider_config = resolve_provider_config(config, os.environ, provider_name)
    provider = create_llm_provider(
        kind=provider_config.kind,
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
        timeout=provider_config.timeout,
    )
    params = resolve_model_params(config, "knowledge", provider_name=provider_name)
    get_model_capabilities = getattr(provider, "get_model_capabilities", None)
    capabilities = (
        get_model_capabilities(params.name)
        if callable(get_model_capabilities)
        else ModelCapabilities()
    )
    return provider, params, capabilities


def _normalize_with_llm(
    *,
    workspace_root: Path,
    source_path: Path,
    source_text: str,
    config_path: Path | None,
    provider_name: str | None,
    canonical_tag_id: str | None,
    llm_provider: LLMProvider | None,
    llm_params: ModelParams | None,
) -> tuple[str, str, str | None]:
    if llm_provider is None or llm_params is None:
        provider, params, capabilities = _resolve_provider(config_path, provider_name)
    else:
        provider = llm_provider
        params = llm_params
        capabilities = getattr(provider, "capabilities", ModelCapabilities())
    vocabulary = load_merged_vocabulary(workspace_root)
    prompt = _prompt_template().render(
        source_text=source_text,
        source_filename=source_path.name,
        canonical_tag_id=canonical_tag_id or "",
        vocabulary=[
            {
                "id": tag.internal_id,
                "display_zh": tag.display_zh,
                "category": tag.category.value,
                "description": tag.description or "",
            }
            for tag in vocabulary.tags.values()
        ],
    )
    content: str | list[dict[str, Any]] = prompt
    if source_path.suffix.lower() in IMAGE_EXTENSIONS:
        content = build_multimodal_content(prompt, [source_path], capabilities) or prompt
    response = provider.complete(
        [{"role": "user", "content": content}],
        params,
    )
    try:
        data = loads_json_object(response.content)
    except ValueError as exc:
        raise KnowledgeError(f"Knowledge normalize LLM returned invalid JSON: {exc}") from exc
    tag_id = str(data.get("canonical_tag_id") or canonical_tag_id or "")
    body = str(data.get("markdown_body") or source_text)
    title = data.get("title")
    return tag_id, body, str(title) if title else None


def _write_markdown(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        [
            "---",
            yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip(),
            "---",
            "",
            body.strip(),
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def normalize_knowledge_file(
    workspace_root: Path,
    source_path: Path,
    *,
    config_path: Path | None = None,
    provider_name: str | None = None,
    canonical_tag_id: str | None = None,
    dry_run: bool = False,
    llm_provider: LLMProvider | None = None,
    llm_params: ModelParams | None = None,
) -> Path:
    workspace_root = workspace_root.resolve()
    source_path = source_path.resolve()
    if not source_path.exists():
        raise KnowledgeError(f"Knowledge source file not found: {source_path}")

    source_text = "" if source_path.suffix.lower() in IMAGE_EXTENSIONS else _read_source_text(source_path)
    title: str | None = None
    body = source_text
    tag_id = canonical_tag_id
    if not dry_run:
        tag_id, body, title = _normalize_with_llm(
            workspace_root=workspace_root,
            source_path=source_path,
            source_text=source_text,
            config_path=config_path,
            provider_name=provider_name,
            canonical_tag_id=canonical_tag_id,
            llm_provider=llm_provider,
            llm_params=llm_params,
        )
    if not tag_id:
        raise KnowledgeError(
            "Knowledge normalize needs canonical_tag_id for deterministic draft generation."
        )
    vocabulary = load_merged_vocabulary(workspace_root)
    if tag_id not in vocabulary.tags:
        raise KnowledgeError(f"Unknown canonical_tag_id for knowledge draft: {tag_id}")

    normalized_hash = _sha256_text(body)
    frontmatter: dict[str, Any] = {
        "canonical_tag_id": tag_id,
        "standardized": True,
        "last_normalized_hash": normalized_hash,
        "last_user_edit_hash": normalized_hash,
        "title": title or source_path.stem,
        "source": str(source_path),
    }
    path = _draft_path(workspace_root, source_path)
    _write_markdown(path, frontmatter, body)
    return path


def publish_knowledge_draft(workspace_root: Path, draft_path: Path) -> KnowledgeDocument:
    workspace_root = workspace_root.resolve()
    draft_path = draft_path if draft_path.is_absolute() else workspace_root / draft_path
    document = load_knowledge_document(workspace_root, draft_path, source=KnowledgeSource.PRIVATE)
    body_hash = _sha256_text(document.body)
    frontmatter = document.frontmatter.model_dump(exclude_none=True)
    frontmatter["standardized"] = True
    frontmatter["last_user_edit_hash"] = body_hash
    if not frontmatter.get("last_normalized_hash"):
        frontmatter["last_normalized_hash"] = body_hash

    target = (
        workspace_root
        / ".cpho"
        / "knowledge"
        / "files"
        / "published"
        / draft_path.name
    )
    _write_markdown(target, frontmatter, document.body)
    return load_knowledge_document(workspace_root, target, source=KnowledgeSource.PRIVATE)
