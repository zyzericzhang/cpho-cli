import httpx
import pytest

from cpho_cli.core.llm import LLMProviderError, OpenRouterProvider
from cpho_cli.models.config import ModelParams
from cpho_cli.models.solve import DerivationStep


def test_openrouter_request_includes_tool_call_for_structured_output() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.read().decode()
        return httpx.Response(
            200,
            json={
                "choices": [{
                    "message": {
                        "tool_calls": [{
                            "function": {"arguments": '{"reasoning": "test", "expression": "x", "official_answer_refs": ["a"]}'}
                        }]
                    }
                }],
                "usage": {},
            },
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

    assert '"tools"' in captured["json"]
    assert "derivation_step" in captured["json"]
    assert "tool_choice" not in captured["json"]


def test_openrouter_request_extracts_from_content_when_no_tool_calls() -> None:
    """Fallback: when model returns content directly without calling the tool."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.read().decode()
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"reasoning": "t", "expression": "x", "official_answer_refs": ["a"]}'}}], "usage": {}},
        )

    provider = OpenRouterProvider(
        api_key="sk-test-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = provider.complete(
        messages=[{"role": "user", "content": "derive"}],
        params=ModelParams(name="test-model"),
        response_model=DerivationStep,
    )

    assert "tool_choice" not in captured["json"]
    assert "t" in result.content


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

