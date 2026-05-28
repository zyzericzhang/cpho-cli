from __future__ import annotations

import json
import time
import re
from collections.abc import Iterator
from typing import Any, Protocol, TypeVar

import httpx
from pydantic import BaseModel

from cpho_cli.core.errors import err_api_call_failed
from cpho_cli.core.runtime import redact_secrets
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import ChatMessage, LLMResponse, LLMUsage, ModelCapabilities

ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
_CAPABILITY_CACHE: dict[tuple[str, str, str], ModelCapabilities] = {}
_STREAM_DONE = object()


class LLMProviderError(RuntimeError):
    """Raised when the LLM provider cannot return a usable response."""


class LLMProvider(Protocol):
    def complete(
        self,
        messages: list[ChatMessage],
        params: ModelParams,
        response_model: type[ResponseModel] | None = None,
    ) -> LLMResponse:
        """Complete a chat request."""

    def stream(
        self,
        messages: list[ChatMessage],
        params: ModelParams,
    ) -> Iterator[str]:
        """Stream chat completion text chunks."""


class _OpenAICompatibleProvider:
    """Shared implementation for OpenAI-compatible chat completions APIs."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        client: httpx.Client | None = None,
        max_retries: int = 2,
        label: str = "provider",
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=httpx.Timeout(timeout))
        self.max_retries = max_retries
        self.label = label

    def complete(
        self,
        messages: list[ChatMessage],
        params: ModelParams,
        response_model: type[ResponseModel] | None = None,
    ) -> LLMResponse:
        payload = self._chat_payload(messages, params)
        if response_model is not None:
            self._add_structured_output(payload, response_model)

        headers = {"Authorization": f"Bearer {self.api_key}"}
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise httpx.HTTPStatusError("transient provider error", request=response.request, response=response)
                if response.status_code >= 400:
                    raise LLMProviderError(
                        redact_secrets(
                            err_api_call_failed(
                                self.label,
                                "request",
                                f"{response.status_code} {response.text}",
                            ),
                            [self.api_key],
                        )
                    )
                data = response.json()
                message = data.get("choices", [{}])[0].get("message", {})
                if response_model is not None:
                    tool_calls = message.get("tool_calls", [])
                    if tool_calls:
                        content = tool_calls[0].get("function", {}).get("arguments") or ""
                    else:
                        content = message.get("content", "")
                else:
                    content = message.get("content", "")
                usage_data = data.get("usage") or {}
                return LLMResponse(
                    content=content,
                    usage=LLMUsage(
                        prompt_tokens=usage_data.get("prompt_tokens"),
                        completion_tokens=usage_data.get("completion_tokens"),
                        total_tokens=usage_data.get("total_tokens"),
                    ),
                    raw=data,
                )
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(0.1 * (2**attempt))
        raise LLMProviderError(
            redact_secrets(
                err_api_call_failed(self.label, "request", str(last_error)),
                [self.api_key],
            )
        )

    def stream(
        self,
        messages: list[ChatMessage],
        params: ModelParams,
    ) -> Iterator[str]:
        payload = self._chat_payload(messages, params)
        payload["stream"] = True
        headers = {"Authorization": f"Bearer {self.api_key}"}
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with self.client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status_code in {429, 500, 502, 503, 504}:
                        raise httpx.HTTPStatusError(
                            "transient provider error",
                            request=response.request,
                            response=response,
                        )
                    if response.status_code >= 400:
                        raise LLMProviderError(
                            redact_secrets(
                                err_api_call_failed(
                                    self.label,
                                    "stream",
                                    f"{response.status_code} {response.text}",
                                ),
                                [self.api_key],
                            )
                        )
                    for line in response.iter_lines():
                        chunk = _parse_sse_line(line)
                        if chunk is _STREAM_DONE:
                            return
                        if chunk:
                            yield chunk
                    return
            except LLMProviderError:
                raise
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(0.1 * (2**attempt))
        raise LLMProviderError(
            redact_secrets(
                err_api_call_failed(self.label, "stream", str(last_error)),
                [self.api_key],
            )
        )

    def _chat_payload(
        self,
        messages: list[ChatMessage],
        params: ModelParams,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": params.name,
            "messages": messages,
        }
        if params.temperature is not None:
            payload["temperature"] = params.temperature
        if params.max_tokens is not None:
            payload["max_tokens"] = params.max_tokens
        return payload

    def _add_structured_output(
        self,
        payload: dict[str, Any],
        response_model: type[ResponseModel],
    ) -> None:
        schema_name = _schema_name(response_model)
        payload["tools"] = [_tool_schema(schema_name, response_model)]
        payload["tool_choice"] = {
            "type": "function",
            "function": {"name": schema_name},
        }
        payload["parallel_tool_calls"] = False


class OpenRouterProvider(_OpenAICompatibleProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        client: httpx.Client | None = None,
        max_retries: int = 2,
        timeout: float = 120.0,
    ) -> None:
        super().__init__(api_key, base_url, client, max_retries, label="OpenRouter", timeout=timeout)

    def get_model_capabilities(self, model_name: str | None) -> ModelCapabilities:
        if not model_name:
            return ModelCapabilities()
        return fetch_openrouter_model_capabilities(
            client=self.client,
            base_url=self.base_url,
            api_key=self.api_key,
            provider_label=self.label,
            model_name=model_name,
        )


class DeepSeekProvider(_OpenAICompatibleProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        client: httpx.Client | None = None,
        max_retries: int = 2,
        timeout: float = 120.0,
    ) -> None:
        super().__init__(api_key, base_url, client, max_retries, label="DeepSeek", timeout=timeout)


def _schema_name(response_model: type[BaseModel]) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", response_model.__name__).lower().lstrip("_")


def _parse_sse_line(line: str) -> str | object | None:
    if not line:
        return None
    if not line.startswith("data:"):
        return None
    data = line.removeprefix("data:").strip()
    if data == "[DONE]":
        return _STREAM_DONE
    try:
        payload = json.loads(data)
    except json.JSONDecodeError as exc:
        raise LLMProviderError(f"Provider stream returned invalid JSON chunk: {exc}") from exc
    choices = payload.get("choices") or []
    if not choices:
        return None
    delta = choices[0].get("delta") or {}
    content = delta.get("content")
    return content if isinstance(content, str) else None


def _tool_schema(schema_name: str, response_model: type[BaseModel]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": schema_name,
            "description": f"Return a {response_model.__name__} structured object.",
            "parameters": response_model.model_json_schema(),
        },
    }


def _capability_from_model_metadata(model_data: dict[str, Any]) -> ModelCapabilities:
    architecture = model_data.get("architecture") or {}
    input_modalities = architecture.get("input_modalities") or ["text"]
    supported_parameters = model_data.get("supported_parameters") or []
    return ModelCapabilities(
        input_modalities=set(input_modalities),
        supported_parameters=set(supported_parameters),
    )


def fetch_openrouter_model_capabilities(
    *,
    client: httpx.Client,
    base_url: str,
    api_key: str,
    provider_label: str,
    model_name: str,
) -> ModelCapabilities:
    cache_key = (provider_label, base_url.rstrip("/"), model_name)
    if cache_key in _CAPABILITY_CACHE:
        return _CAPABILITY_CACHE[cache_key]

    try:
        response = client.get(
            f"{base_url.rstrip('/')}/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        if response.status_code >= 400:
            raise LLMProviderError(
                redact_secrets(
                    f"{provider_label} model metadata failed: {response.status_code} {response.text}",
                    [api_key],
                )
            )
        data = response.json()
    except httpx.TransportError as exc:
        raise LLMProviderError(
            redact_secrets(f"{provider_label} model metadata failed: {exc}", [api_key])
        ) from exc

    for model_data in data.get("data", []):
        if model_data.get("id") == model_name:
            capabilities = _capability_from_model_metadata(model_data)
            _CAPABILITY_CACHE[cache_key] = capabilities
            return capabilities

    capabilities = ModelCapabilities()
    _CAPABILITY_CACHE[cache_key] = capabilities
    return capabilities


def detect_model_capabilities(
    provider: LLMProvider,
    model_name: str | None,
) -> ModelCapabilities:
    get_model_capabilities = getattr(provider, "get_model_capabilities", None)
    if not callable(get_model_capabilities):
        return ModelCapabilities()
    return get_model_capabilities(model_name)


_PROVIDER_REGISTRY: dict[str, type[_OpenAICompatibleProvider]] = {
    "openrouter": OpenRouterProvider,
    "deepseek": DeepSeekProvider,
}


def create_llm_provider(kind: str, api_key: str, base_url: str, *, timeout: float = 120.0) -> LLMProvider:
    cls = _PROVIDER_REGISTRY.get(kind)
    if cls is None:
        raise LLMProviderError(f"Unsupported provider kind: {kind}")
    return cls(api_key=api_key, base_url=base_url, timeout=timeout)


def supported_provider_kinds() -> frozenset[str]:
    return frozenset(_PROVIDER_REGISTRY.keys())
