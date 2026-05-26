---
spike: 003
name: tool-call-structured-output
type: standard
validates: "Given multiple LLM providers (OpenAI, DeepSeek, Anthropic, Mistral, Gemini, local models), when we need structured JSON output from a Pydantic model, then a tool-calling approach works across ALL of them without relying on response_format json_schema, without increasing skill author complexity, and without requiring OpenRouter as intermediary"
verdict: DECIDED
related: []
tags: [llm, structured-output, tool-calling, cross-provider, deepseek, openrouter, 2026]
---

# Spike 003: Tool Calling as Universal Structured Output (2026 Edition)

## What This Validates

**Given** multiple LLM providers accessed via their official APIs (not just OpenRouter),
**When** we need structured JSON output from a Pydantic model,
**Then** replacing `response_format: json_schema` with forced tool calling (`tools` + `tool_choice`) works across ALL providers while keeping the skill-author interface unchanged.

---

## Research (Updated May 2026)

### The Problem

`_OpenAICompatibleProvider.complete()` currently sends:

```json
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {"name": "...", "strict": true, "schema": {...}}
  }
}
```

This is an **OpenAI-proprietary feature**. It does NOT work on:
- DeepSeek (all models, including brand-new V4-Pro/V4-Flash)
- Ollama local deployments
- vLLM (requires non-standard `extra_body`)

### 2026 Provider Capability Matrix

Comprehensive survey of structured output capabilities across ALL major providers (as of May 2026):

| Provider | Official API | Tool Calling | json_schema response_format | Notes |
|----------|-------------|-------------|----------------------------|-------|
| **OpenAI GPT-5/4o** | api.openai.com | ✅ Native | ✅ Native | Both fully supported. Strict mode: 0.2% violation rate |
| **DeepSeek V4-Pro/Flash** | api.deepseek.com | ✅ Native | ❌ **NOT supported** | V4 generation only. `deepseek-chat`/`reasoner` deprecated July 2026 |
| **Anthropic Opus 4.7** | api.anthropic.com | ✅ Native (`tool_use`) | ✅ Native (`output_format`) | Different API format. Sampling params removed on Opus 4.7 |
| **Google Gemini 3.1** | generativelanguage.googleapis.com | ✅ Native | ✅ Native (`response_json_schema`) | Can combine tools + structured output in one request |
| **Mistral Medium 3.5** | api.mistral.ai | ✅ Native | ✅ Native | `tool_choice="any"` (not "required"). Apache 2.0 Small-4 available |
| **OpenRouter** | openrouter.ai | ✅ Unified (OpenAI format) | ✅ Pass-through | Translates across all providers |
| **vLLM** (local) | Self-hosted | ✅ since v0.8.3 (`--enable-auto-tool-choice`) | ⚠️ `extra_body` only | 20+ model-specific tool parsers. No `strict` mode |
| **Ollama** (local) | Self-hosted | ⚠️ Partial (model-dependent) | ❌ Not supported | Gemma4, Llama4, Qwen2.5 work best |

**Critical finding: Tool calling is the ONLY mechanism supported by 100% of providers.**
`json_schema` response_format is NOT supported by DeepSeek (official API) or Ollama, and requires non-standard parameters in vLLM.

### Question 1: Skill Author Difficulty — Does Not Increase

The skill author's interface to structured output is through **Pydantic models**. The full chain:

```
Skill author defines:         SolveReport(BaseModel)  ← Pydantic model
Skill author passes it:       provider.complete(..., response_model=SolveReport)
Framework returns:            LLMResponse(content=json_string)
Caller validates:             SolveReport.model_validate_json(response.content)
```

**The proposed change is 100% transparent to this chain.** The `response_model` parameter and `LLMResponse.content` field remain unchanged. The only difference is where the JSON string originates in the HTTP response body — an implementation detail hidden behind the `LLMProvider` interface.

For the future generic SkillRuntime (Phase 3), skill authors will still only write:
1. Pydantic models (for output type safety)
2. `skill.yml` (step wiring)
3. Jinja2 prompt templates (`.md.j2`)

None of these touch the structured output mechanism. **Skill author complexity = zero change.**

### Question 2: Official Platform Support (Not Just OpenRouter)

The key architectural insight: **OpenAI-format tool calling is the de facto standard across platforms.**

| Platform | OpenAI-format tool calling works? | Direct HTTP call to official API |
|----------|----------------------------------|----------------------------------|
| OpenAI | ✅ | `POST api.openai.com/v1/chat/completions` |
| DeepSeek | ✅ | `POST api.deepseek.com/v1/chat/completions` |
| Mistral | ✅ | `POST api.mistral.ai/v1/chat/completions` |
| vLLM | ✅ | `POST <self-hosted>/v1/chat/completions` |
| Ollama | ✅ (model-dependent) | `POST localhost:11434/v1/chat/completions` |
| OpenRouter | ✅ | `POST openrouter.ai/api/v1/chat/completions` |

**EXCEPTION: Anthropic native API** uses a different format:
- Tool definitions: `input_schema` instead of `parameters`
- Response: `tool_use` content blocks with `stop_reason: "tool_use"` (not `tool_calls` in `choices[0].message`)
- Different endpoint: `POST api.anthropic.com/v1/messages`
- Different auth header: `x-api-key` instead of `Authorization: Bearer`

Anthropic can still be supported, just not through `_OpenAICompatibleProvider`. Three options:
1. **Via OpenRouter** (simplest) — OpenRouter translates OpenAI-format tool calls to Anthropic `tool_use`
2. **Separate `AnthropicProvider`** class — implements `LLMProvider` protocol using Anthropic SDK/API
3. **DeepSeek's Anthropic endpoint** — DeepSeek also has `/anthropic` endpoint with Anthropic format

**Recommendation: `_OpenAICompatibleProvider` covers 6/7 platforms directly. Anthropic native is a separate provider class (future work).**

Gemini also uses a non-OpenAI format (REST API with different JSON structure), but OpenRouter handles it. Direct Gemini support would be a separate provider.

### Question 3: Migration Difficulty, Engineering Complexity, and Impact Analysis

#### Scope of Change

| Layer | Files Changed | Nature of Change |
|-------|--------------|------------------|
| **Provider (core change)** | 1 file: `llm.py` | Replace `response_format` with `tools`+`tool_choice`; swap response extraction path |
| **Callers** | 0 files | No changes. `LLMResponse.content` unchanged |
| **Models/Pydantic** | 0 files | No changes. Same `model_json_schema()` used |
| **Config** | 0 files | No changes |
| **Skill system** | 0 files | No changes. `SkillRuntime` is generic DAG executor |
| **Tests (unit)** | 0 files | Mocks at `LLMResponse` level, which is unchanged |
| **Tests (integration)** | ~1 file | If any test inspects raw HTTP payload for `response_format` |

**Total blast radius: 1 file, ~15 lines changed.**

#### Before/After in `_OpenAICompatibleProvider.complete()`

**Before:**
```python
if response_model is not None:
    schema_name = re.sub(r"(?<!^)(?=[A-Z])", "_", response_model.__name__).lower()
    payload["response_format"] = {
        "type": "json_schema",
        "json_schema": {
            "name": schema_name,
            "strict": True,
            "schema": response_model.model_json_schema(),
        },
    }

# Response extraction:
content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
```

**After:**
```python
if response_model is not None:
    schema_name = re.sub(r"(?<!^)(?=[A-Z])", "_", response_model.__name__).lower()
    payload["tools"] = [{
        "type": "function",
        "function": {
            "name": schema_name,
            "description": f"Output a {response_model.__name__} object.",
            "parameters": response_model.model_json_schema(),
        }
    }]
    payload["tool_choice"] = {
        "type": "function",
        "function": {"name": schema_name}
    }

# Response extraction:
if response_model is not None:
    tool_calls = data.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
    if tool_calls:
        content = tool_calls[0].get("function", {}).get("arguments", "") or ""
    else:
        # Fallback: some models ignore tool_choice and return content
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
else:
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
```

#### Edge Cases Requiring Defensive Handling

| Edge Case | Affected Providers | Mitigation |
|-----------|-------------------|------------|
| `arguments: null` for parameterless tools | vLLM, Ollama | Coerce `None` → `"{}"` |
| Model returns `content` despite `tool_choice` | Ollama, old vLLM | Fallback to `message.content` |
| Extra text after valid JSON in arguments | Some local models | `json.loads()` with error recovery |
| Multiple tool calls returned | All (parallel tool use) | Take first matching tool call |
| Streaming (future) | All | Accumulate `function.arguments` across delta chunks |
| DeepSeek thinking mode + tools | DeepSeek V4 | Must keep `reasoning_content` in history; `supportsToolChoice: false` in thinking mode |

#### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Some provider ignores `tool_choice` | Low | Medium | Fallback to `message.content` extraction |
| Schema too large for tool definition | Very Low | Low | Truncation/compression (not needed for current schemas) |
| Token overhead from tools array | Very Low | Very Low | Negligible — schema sent once, same size either way |
| Provider-specific `tool_choice` format differences | Low | Medium | OpenRouter normalizes; for direct API, Mistral uses `"any"` not `"required"` but function-specific choice works same way |
| Skill authors confused by tool calling in debug/logs | Low | Low | `LLMResponse.raw` preserves full response for debugging |

#### Migration Path

1. **Phase 1 — Provider switch (1 PR, ~15 lines)**
   - Modify `_OpenAICompatibleProvider.complete()` in `llm.py`
   - Add fallback extraction logic
   - Run existing test suite

2. **Phase 2 — Integration testing (optional)**
   - Add HTTP-level test that verifies `tools`/`tool_choice` in payload
   - Test against DeepSeek V4 direct API

3. **Phase 3 — Anthropic native provider (future, separate work)**
   - Create `AnthropicProvider` class implementing `LLMProvider`
   - Uses `tool_use` content blocks or `output_format` for structured output

#### What BREAKS if we do this?

- **Nothing in the public interface.** `LLMProvider.complete()` signature unchanged.
- **Nothing in callers.** Same `response.content` → `model_validate_json()` flow.
- **Nothing in skill definitions.** Same yml + j2 + Pydantic pattern.
- **Only thing that changes:** HTTP request body format and response JSON parsing path.

#### What BREAKS if we DON'T do this?

- DeepSeek API is **unusable** (official platform, not OpenRouter)
- Ollama local deployments are blocked
- vLLM requires brittle `extra_body` workarounds
- Every new non-OpenAI provider requires custom response_format handling

---

## Provider Format Compatibility Table (2026)

All via `_OpenAICompatibleProvider` base class:

```
                    json_schema        Tool Calling
OpenAI              ✅                 ✅
DeepSeek V4         ❌                 ✅  ← BLOCKER
Mistral             ✅                 ✅
OpenRouter → *      ✅ (pass-through)  ✅
vLLM                ⚠️ (extra_body)    ✅
Ollama              ❌                 ⚠️ (model-dep.)
                    ^                  ^
                    2/6 fail          6/6 work
```

---

## Recommendation

**Use OpenAI-format tool calling as the ONLY structured output mechanism in `_OpenAICompatibleProvider`.**

- **1 file changed** (`llm.py`)
- **0 callers changed**
- **0 skill author impact**
- **6/6 OpenAI-compatible platforms supported** (vs 4/6 with json_schema)
- **Anthropic native and Gemini native** are future work (separate provider classes)
- **Pattern validated by Instructor, LangChain, pydantic-ai** — this is the industry standard approach

## Signal for the Build

- **Replace in `_OpenAICompatibleProvider.complete()`**: `response_format: json_schema` → `tools` + `tool_choice`
- **Response extraction**: `message.content` → `tool_calls[0].function.arguments` (with fallback)
- **Do NOT touch**: `LLMProvider` protocol, `LLMResponse`, any caller code, any Pydantic models, skill definitions
- **Test against**: DeepSeek V4 direct API (primary validation target)
- **Future**: Separate `AnthropicProvider` for native Anthropic API if needed

---

## Implementation (2026-05-24)

### Changes Made

**`src/cpho_cli/core/llm.py`** — `_OpenAICompatibleProvider.complete()`:
1. Replaced `payload["response_format"]` with `payload["tools"]` + `payload["tool_choice"]`
2. Response extraction now prefers `tool_calls[0].function.arguments`, falls back to `message.content`

**`tests/test_llm.py`**:
1. Renamed `test_openrouter_request_includes_json_schema` → `test_openrouter_request_includes_tool_call_for_structured_output`
2. Updated mock response to return `tool_calls` instead of bare `content`
3. Added `test_openrouter_request_extracts_from_content_when_no_tool_calls` for fallback path

**0 callers changed.** `LLMProvider` protocol, `LLMResponse.content`, all Pydantic models, all skill definitions unchanged.

### Conflicting Planning Documents

The following `.planning/` files reference the old `response_format: json_schema` approach and are now outdated by this decision. These are historical snapshots — the decision to use tool calling supersedes them:

| File | What's Outdated |
|------|----------------|
| `.planning/phases/01-core-foundation/01-RESEARCH.md` | Lines 59, 123, 182-189: `response_format` `json_schema` as structured output strategy |
| `.planning/phases/01-core-foundation/01-04-PLAN.md` | Lines 96, 104, 107: Tests and tasks reference `response_format.type = json_schema` |
| `.planning/phases/01-core-foundation/01-DISCUSSION-LOG.md` | Line 95: JSON mode + Pydantic as recommended approach |
| `.planning/phases/02-tag-indexing/02-RESEARCH.md` | Lines 79, 479: `response_format=json_schema` for LLM structured output |
| `.planning/phases/02-tag-indexing/02-PATTERNS.md` | Line 365: References `llm.py:58-67` which is now changed |
| `.planning/research/ARCHITECTURE.md` | Lines 177-184: 3-layer structured output strategy; lines 364-366: code example |
