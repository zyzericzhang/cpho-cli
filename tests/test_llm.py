import json

import httpx
import pytest

from cpho_cli.core.llm import DeepSeekProvider, LLMProviderError, OpenRouterProvider
from cpho_cli.core.multimodal import build_multimodal_content
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import ModelCapabilities
from cpho_cli.models.solve import DerivationStep


def test_openrouter_request_forces_tool_call_for_structured_output() -> None:
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
    assert '"tool_choice"' in captured["json"]
    assert '"response_format"' not in captured["json"]


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

    assert "tool_choice" in captured["json"]
    assert "t" in result.content


def test_deepseek_request_uses_tool_call_not_json_mode() -> None:
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

    provider = DeepSeekProvider(
        api_key="sk-test-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    provider.complete(
        messages=[{"role": "user", "content": "derive"}],
        params=ModelParams(name="test-model"),
        response_model=DerivationStep,
    )

    assert '"tools"' in captured["json"]
    assert '"tool_choice"' in captured["json"]
    assert '"response_format"' not in captured["json"]


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


def test_openrouter_preserves_multimodal_content_blocks(tmp_path) -> None:  # type: ignore[no-untyped-def]
    captured = {}
    image = tmp_path / "problem.png"
    pdf = tmp_path / "answer.pdf"
    image.write_bytes(b"\x89PNG\r\n\x1a\nimage")
    pdf.write_bytes(b"%PDF-1.7\nfile")
    content = build_multimodal_content(
        "inspect these files",
        [image, pdf],
        ModelCapabilities(input_modalities={"image", "file"}),
    )
    assert content is not None

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.read().decode())
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}], "usage": {}})

    provider = OpenRouterProvider(
        api_key="sk-test-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    provider.complete(
        messages=[{"role": "user", "content": content}],
        params=ModelParams(name="test-model"),
    )

    blocks = captured["payload"]["messages"][0]["content"]
    assert blocks[0] == {"type": "text", "text": "inspect these files"}
    assert blocks[1]["type"] == "image_url"
    assert blocks[1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert blocks[2]["type"] == "file"
    assert blocks[2]["file"]["filename"] == "answer.pdf"
    assert blocks[2]["file"]["file_data"].startswith("data:application/pdf;base64,")


def test_openrouter_model_capabilities_from_mocked_metadata() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "test/multimodal",
                        "architecture": {"input_modalities": ["text", "image", "file"]},
                        "supported_parameters": ["tools"],
                    }
                ]
            },
        )

    provider = OpenRouterProvider(
        api_key="sk-test-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    first = provider.get_model_capabilities("test/multimodal")
    second = provider.get_model_capabilities("test/multimodal")

    assert first.supports_image
    assert first.supports_file
    assert "tools" in first.supported_parameters
    assert second == first
    assert calls == 1


def test_openrouter_model_capability_error_redacts_api_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="bad key sk-test-secret")

    provider = OpenRouterProvider(
        api_key="sk-test-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(LLMProviderError) as exc:
        provider.get_model_capabilities("test/model")

    assert "sk-test-secret" not in str(exc.value)
