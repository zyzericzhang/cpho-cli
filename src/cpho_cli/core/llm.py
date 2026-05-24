from __future__ import annotations

import time
import re
from typing import Any, Protocol, TypeVar

import httpx
from pydantic import BaseModel

from cpho_cli.core.runtime import redact_secrets
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import LLMResponse, LLMUsage

ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


class LLMProviderError(RuntimeError):
    """Raised when the LLM provider cannot return a usable response."""


class LLMProvider(Protocol):
    def complete(
        self,
        messages: list[dict[str, str]],
        params: ModelParams,
        response_model: type[ResponseModel] | None = None,
    ) -> LLMResponse:
        """Complete a chat request."""


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
        messages: list[dict[str, str]],
        params: ModelParams,
        response_model: type[ResponseModel] | None = None,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": params.name,
            "messages": messages,
        }
        if params.temperature is not None:
            payload["temperature"] = params.temperature
        if params.max_tokens is not None:
            payload["max_tokens"] = params.max_tokens
        if response_model is not None:
            schema_name = re.sub(r"(?<!^)(?=[A-Z])", "_", response_model.__name__).lower()
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": schema_name,
                        "description": f"Return a {response_model.__name__} structured object.",
                        "parameters": response_model.model_json_schema(),
                    },
                }
            ]

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
                            f"{self.label} request failed: {response.status_code} {response.text}",
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
            redact_secrets(f"{self.label} request failed: {last_error}", [self.api_key])
        )


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
