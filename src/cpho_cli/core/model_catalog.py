from __future__ import annotations

import json
import time
from importlib import resources
from pathlib import Path

import httpx
from pydantic import Field

from cpho_cli.core.runtime import redact_secrets
from cpho_cli.models.config import StrictModel


class ModelCatalogError(RuntimeError):
    """Raised when a model catalog cannot be loaded."""


class ModelCatalogEntry(StrictModel):
    id: str
    name: str | None = None
    input_modalities: list[str] = Field(default_factory=lambda: ["text"])
    context_length: int | None = None


class ModelCatalog(StrictModel):
    provider: str
    models: list[ModelCatalogEntry] = Field(default_factory=list)
    source: str = "live"
    fetched_at: float | None = None


def default_model_cache_dir() -> Path:
    return Path.home() / ".cache" / "cpho" / "models"


def _cache_path(cache_dir: Path, provider: str) -> Path:
    return cache_dir / f"{provider}.json"


def _is_fresh(path: Path, ttl_seconds: int) -> bool:
    if not path.exists():
        return False
    return time.time() - path.stat().st_mtime <= ttl_seconds


def _read_catalog(path: Path, *, source: str) -> ModelCatalog:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["source"] = source
    return ModelCatalog.model_validate(data)


def _write_catalog(path: Path, catalog: ModelCatalog) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = catalog.model_dump(mode="json")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _fallback_catalog(provider: str) -> ModelCatalog:
    if provider != "openrouter":
        return ModelCatalog(provider=provider, models=[], source="fallback", fetched_at=time.time())
    data_path = resources.files("cpho_cli").joinpath("data/model_catalog/openrouter_fallback.json")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    data["source"] = "fallback"
    data["fetched_at"] = time.time()
    return ModelCatalog.model_validate(data)


def fetch_openrouter_model_catalog(
    *,
    api_key: str,
    base_url: str = "https://openrouter.ai/api/v1",
    client: httpx.Client | None = None,
) -> ModelCatalog:
    active_client = client or httpx.Client(timeout=httpx.Timeout(30.0))
    try:
        response = active_client.get(
            f"{base_url.rstrip('/')}/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
    except httpx.TransportError as exc:
        raise ModelCatalogError(
            redact_secrets(f"OpenRouter model list failed: {exc}", [api_key])
        ) from exc
    if response.status_code >= 400:
        raise ModelCatalogError(
            redact_secrets(
                f"OpenRouter model list failed: {response.status_code} {response.text}",
                [api_key],
            )
        )
    data = response.json()
    models: list[ModelCatalogEntry] = []
    for item in data.get("data", []):
        architecture = item.get("architecture") or {}
        top_provider = item.get("top_provider") or {}
        models.append(
            ModelCatalogEntry(
                id=str(item.get("id")),
                name=item.get("name"),
                input_modalities=list(architecture.get("input_modalities") or ["text"]),
                context_length=item.get("context_length") or top_provider.get("context_length"),
            )
        )
    return ModelCatalog(
        provider="openrouter",
        models=models,
        source="live",
        fetched_at=time.time(),
    )


def load_model_catalog(
    provider: str,
    *,
    api_key: str | None = None,
    base_url: str = "https://openrouter.ai/api/v1",
    cache_dir: Path | None = None,
    ttl_seconds: int = 3600,
    force_refresh: bool = False,
    client: httpx.Client | None = None,
) -> ModelCatalog:
    cache_root = cache_dir or default_model_cache_dir()
    path = _cache_path(cache_root, provider)
    if not force_refresh and _is_fresh(path, ttl_seconds):
        return _read_catalog(path, source="cache")

    if provider == "openrouter" and api_key:
        try:
            catalog = fetch_openrouter_model_catalog(
                api_key=api_key,
                base_url=base_url,
                client=client,
            )
        except ModelCatalogError:
            if path.exists():
                return _read_catalog(path, source="cache-stale")
            return _fallback_catalog(provider)
        _write_catalog(path, catalog)
        return catalog

    if path.exists():
        return _read_catalog(path, source="cache-stale")
    return _fallback_catalog(provider)
