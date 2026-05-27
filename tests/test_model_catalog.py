from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from cpho_cli.core.model_catalog import load_model_catalog


def _client(payload: dict, status: int = 200) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/models"
        return httpx.Response(status, json=payload)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_load_model_catalog_fetches_openrouter_and_writes_cache(tmp_path: Path) -> None:
    catalog = load_model_catalog(
        "openrouter",
        api_key="sk-test",
        cache_dir=tmp_path,
        client=_client(
            {
                "data": [
                    {
                        "id": "provider/model",
                        "name": "Model",
                        "architecture": {"input_modalities": ["text", "image"]},
                        "context_length": 1234,
                    }
                ]
            }
        ),
    )

    assert catalog.source == "live"
    assert catalog.models[0].id == "provider/model"
    assert catalog.models[0].input_modalities == ["text", "image"]
    assert (tmp_path / "openrouter.json").exists()


def test_load_model_catalog_reuses_fresh_cache(tmp_path: Path) -> None:
    cache = tmp_path / "openrouter.json"
    cache.write_text(
        json.dumps(
            {
                "provider": "openrouter",
                "models": [{"id": "cached/model", "name": "Cached"}],
                "source": "live",
                "fetched_at": time.time(),
            }
        ),
        encoding="utf-8",
    )

    catalog = load_model_catalog(
        "openrouter",
        api_key="sk-test",
        cache_dir=tmp_path,
        client=_client({"data": [{"id": "live/model"}]}),
    )

    assert catalog.source == "cache"
    assert catalog.models[0].id == "cached/model"


def test_load_model_catalog_refreshes_expired_cache(tmp_path: Path) -> None:
    cache = tmp_path / "openrouter.json"
    cache.write_text(
        json.dumps({"provider": "openrouter", "models": [{"id": "old/model"}]}),
        encoding="utf-8",
    )
    old = time.time() - 7200
    cache.touch()
    import os

    os.utime(cache, (old, old))

    catalog = load_model_catalog(
        "openrouter",
        api_key="sk-test",
        cache_dir=tmp_path,
        ttl_seconds=1,
        client=_client({"data": [{"id": "new/model"}]}),
    )

    assert catalog.source == "live"
    assert catalog.models[0].id == "new/model"


def test_load_model_catalog_uses_fallback_when_first_fetch_fails(tmp_path: Path) -> None:
    catalog = load_model_catalog(
        "openrouter",
        api_key="sk-test",
        cache_dir=tmp_path,
        client=_client({"error": "no"}, status=500),
    )

    assert catalog.source == "fallback"
    assert any(model.id == "openai/gpt-4o-mini" for model in catalog.models)
