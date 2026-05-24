---
spike: 003
name: tool-call-structured-output
type: standard
validates: "Given multiple LLM providers (DeepSeek, OpenAI, Anthropic), when we need structured JSON output from a Pydantic model, then a tool-calling approach works across all of them without relying on response_format json_schema"
verdict: VALIDATED
related: []
tags: [llm, structured-output, tool-calling, cross-provider, deepseek, openrouter]
---

# Spike 003: Tool Calling as Universal Structured Output

## What This Validates

**Given** an LLM provider that supports tool/function calling but NOT `response_format: {type: "json_schema"}` (e.g., DeepSeek),
**When** we send a request with the Pydantic model schema wrapped as a tool definition and `tool_choice: "required"`,
**Then** the model returns structured JSON matching the schema in `tool_calls[0].function.arguments`.

## Research

### Problem

The current `_OpenAICompatibleProvider.complete()` sends:
```json
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {"name": "...", "strict": true, "schema": {...}}
  }
}
```

DeepSeek API does NOT support `response_format` with `json_schema` type. Many other providers (Ollama, local models via vLLM, older OpenAI-compatible APIs) also lack this feature. This blocks using any provider except OpenAI/OpenRouter.

### DeepSeek API Capabilities (2025)

| Feature | deepseek-chat (V3) | deepseek-reasoner (R1-0528+) | deepseek-reasoner (pre-0528) |
|---------|-------------------|------------------------------|------------------------------|
| Tool calling | ✅ Full support | ✅ Supported | ❌ Falls back to chat model |
| json_schema response_format | ❌ | ❌ | ❌ |
| json_object response_format | ⚠️ Partial | ⚠️ Partial | ⚠️ Partial |
| Strict mode (beta) | ✅ V3.1+ | ❌ | ❌ |

Key finding: **DeepSeek supports tool calling on all current models but does NOT support `json_schema` response format on any model.**

DeepSeek also has an Anthropic-compatible endpoint at `https://api.deepseek.com/anthropic` that supports Anthropic-format `tool_use` blocks.

### Cross-Provider Tool Calling Support

| Provider | Tool Calling | json_schema response_format | Notes |
|----------|-------------|----------------------------|-------|
| OpenAI | ✅ Native | ✅ Native | Both fully supported |
| DeepSeek V3+ | ✅ Native | ❌ | Tool calling is the way |
| Anthropic | ✅ Native (`tool_use`) | ❌ Different API format | Uses `tool_use` content blocks |
| OpenRouter | ✅ Unified | ✅ Pass-through | Translates tool calls across all providers uniformly |
| vLLM (local) | ✅ with `--enable-auto-tool-choice` | ⚠️ Via `extra_body` | Not standard OpenAI format |
| Ollama (local) | ⚠️ Partial | ❌ | Requires post-processing |

### The Established Pattern: Tool Calling for Structured Output

Multiple major frameworks use tool calling as their **primary or fallback** mechanism for structured output:

- **Instructor** — `TOOLS` / `TOOLS_STRICT` modes use tool calling with forced tool choice
- **LangChain** — `with_structured_output()` falls back to tool calling when `json_schema` isn't available
- **pydantic-ai** — implements structured output *solely* using tool-calling APIs
- **AG2** — creates a special tool with your schema, forces tool choice, extracts data

### How It Works

Instead of:
```python
# Current approach (breaks on DeepSeek)
payload["response_format"] = {
    "type": "json_schema",
    "json_schema": {"name": "solve_report", "strict": True, "schema": {...}}
}
# Response data in: response["choices"][0]["message"]["content"]
```

Use:
```python
# Tool-calling approach (works everywhere)
payload["tools"] = [{
    "type": "function",
    "function": {
        "name": "output_solve_report",
        "description": "Return the solve report",
        "parameters": schema  # Same Pydantic model_json_schema()
    }
}]
payload["tool_choice"] = {"type": "function", "function": {"name": "output_solve_report"}}
# Response data in: response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]
```

The model is forced to "call" the output tool, and the structured JSON is in the tool call arguments. This is effectively one API call — no actual tool execution needed.

### OpenRouter as Universal Translator

OpenRouter already standardizes tool calling across all providers using the OpenAI format. If we send:
```json
{
  "model": "deepseek/deepseek-chat",
  "tools": [{"type": "function", "function": {...}}],
  "tool_choice": {...}
}
```

OpenRouter handles the translation for Anthropic models (converting to `tool_use` blocks) and other provider-specific formats. This means a single tool-calling code path works for ALL providers through OpenRouter.

### Anthropic Native API Consideration

If we ever add a native Anthropic provider (bypassing OpenRouter), the tool format differs:
- Tool definitions use `input_schema` instead of `parameters`
- Response uses `tool_use` content blocks with `stop_reason: "tool_use"`
- Tool results sent back as `tool_result` content blocks with `role: "user"`

However, through OpenRouter, everything is normalized to OpenAI format.

### Known Edge Cases

1. **Empty arguments**: Some providers (vLLM, Ollama) return `arguments: null` for parameterless tools → coerce to `"{}"`
2. **Garbage after JSON**: Some local models emit extra text after valid JSON in tool call arguments → strip/re-extract
3. **Parallel tool calls**: Some models return multiple tool calls → handle by taking the first matching one
4. **Streaming**: Tool calls arrive in chunks via streaming deltas → need to accumulate `function.arguments` across chunks

## Design Options for cpho-cli

### Option A: Tool-Call-Only (Recommended)

Abandon `response_format` entirely. Always use tool calling for structured output.

**Pros:**
- Single code path, minimal maintenance
- Works with every provider that supports tool calling (much broader than json_schema)
- DeepSeek-native compatible
- OpenRouter normalizes everything to this format

**Cons:**
- Slightly more complex response parsing (extract from `tool_calls[0].function.arguments` instead of `message.content`)
- Doesn't leverage OpenAI's native `json_schema` strict mode (but strict mode is not available anywhere else anyway)

### Option B: Dual-Mode with Capability Detection

Try `response_format` first, fall back to tool calling.

**Pros:**
- Uses native features when available
- Better error messages from OpenAI's strict mode

**Cons:**
- Two code paths to maintain and test
- Need per-provider capability flags
- More complex error handling

### Option C: Per-Provider Strategy Pattern

Each provider class chooses its own structured output strategy.

**Pros:**
- Maximum flexibility per provider
- Clean OOP design

**Cons:**
- Overengineered for current needs (2 providers)
- Duplicated logic across providers

### Recommendation

**Option A (tool-call-only)** for Phase 1. It's the simplest change with the broadest compatibility. If OpenAI's strict mode becomes important later, we can add it as a provider-specific optimization.

## Implementation Sketch

The change to `_OpenAICompatibleProvider.complete()` would look like:

```python
def complete(self, messages, params, response_model=None):
    payload = {
        "model": params.name,
        "messages": messages,
    }
    if params.temperature is not None:
        payload["temperature"] = params.temperature
    if params.max_tokens is not None:
        payload["max_tokens"] = params.max_tokens

    if response_model is not None:
        schema_name = re.sub(r"(?<!^)(?=[A-Z])", "_", response_model.__name__).lower()
        payload["tools"] = [{
            "type": "function",
            "function": {
                "name": schema_name,
                "description": f"Return a {response_model.__name__} structured object.",
                "parameters": response_model.model_json_schema(),
            }
        }]
        payload["tool_choice"] = {
            "type": "function",
            "function": {"name": schema_name}
        }

    # ... HTTP request ...

    # Extract content from tool_calls when response_model is set
    if response_model is not None:
        tool_calls = data.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
        if tool_calls:
            content = tool_calls[0].get("function", {}).get("arguments", "")
        else:
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    else:
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
```

**Callers do NOT need to change.** The `LLMResponse.content` field still contains the JSON string — it just comes from a different place in the response. All callers do `SomeModel.model_validate_json(response.content)` which remains unchanged.

## Results

**Verdict: VALIDATED** — Tool calling is a viable and well-established replacement for `response_format: json_schema`.

Key findings:
1. DeepSeek supports tool calling on all current models (V3, R1-0528+, V3.1, V3.2) but does NOT support `json_schema` response format
2. Using `tool_choice` to force a tool call for structured output is a pattern used by Instructor, LangChain, pydantic-ai, and AG2
3. OpenRouter normalizes tool calling across all providers using OpenAI format — single code path
4. Response parsing change is minimal: extract from `tool_calls[0].function.arguments` instead of `message.content`
5. The `LLMProvider.complete()` interface (`LLMResponse.content`) does NOT need to change — callers are unaffected
6. Anthropic native API uses different format (`tool_use` blocks) but OpenRouter handles translation

## Signal for the Build

- **Use:** OpenAI-format tool calling with forced `tool_choice` as the universal structured output mechanism
- **Drop:** `response_format: {type: "json_schema"}` from `_OpenAICompatibleProvider`
- **Watch for:** Empty/missing `tool_calls` array (some models may still return content instead), streaming deltas if streaming is added later
- **Test matrix:** DeepSeek direct, OpenRouter→DeepSeek, OpenRouter→OpenAI, OpenRouter→Anthropic
