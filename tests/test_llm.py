import httpx
import pytest

from cpho_cli.core.llm import LLMProviderError, OpenRouterProvider
from cpho_cli.models.config import ModelParams
from cpho_cli.models.solve import DerivationStep


def test_openrouter_request_includes_json_schema() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.read().decode()
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"ok": true}'}}], "usage": {}},
        )

    provider = OpenRouterProvider(
        api_key="sk-test-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    provider.complete(
        messages=[{"role": "user", "content": "derive"}],
        params=ModelParams(name="test-model"),
        response_model=DerivationStep,
    )

    assert "json_schema" in captured["json"]
    assert "derivation_step" in captured["json"]


def test_provider_error_redacts_api_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "bad key sk-test-secret"})

    provider = OpenRouterProvider(
        api_key="sk-test-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(LLMProviderError) as exc:
        provider.complete(messages=[], params=ModelParams(name="test-model"))

    assert "sk-test-secret" not in str(exc.value)

