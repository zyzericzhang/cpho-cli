# Spike Manifest

## Idea

Redesign cpho-cli's LLM structured output mechanism to use tool calling (function calling) instead of OpenAI's `response_format: {type: "json_schema"}`. This would make the system compatible with DeepSeek API and many other providers that don't support the `json_schema` response format but do support tool calling.

## Requirements

- Must work with DeepSeek direct API (primary target)
- Must work through OpenRouter (unified provider gateway)
- Must not break existing callers of `LLMProvider.complete()`
- Single code path preferred over dual-mode fallback

## Spikes

| # | Name | Type | Validates | Verdict | Tags |
|---|------|------|-----------|---------|------|
| 003 | tool-call-structured-output | standard | Tool calling can replace json_schema response_format for structured output across all major providers | ✓ VALIDATED | llm, structured-output, tool-calling, deepseek |
