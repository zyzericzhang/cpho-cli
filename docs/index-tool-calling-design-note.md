# /index tool-calling implementation note

Date: 2026-05-25

## Planning intent referenced

I reviewed the existing `.planning` design for `/index` before changing code:

- Phase 02 tag indexing defines `cpho index` as the local workspace index builder, producing structured per-problem JSONL for later skills.
- Phase 02.1 paper splitting changes the index unit from whole PDF file to virtual `ProblemEntry`, with rules-first splitting and LLM fallback when rule diagnostics are unsafe.
- Phase 02.2 REPL workspace commands requires `/index` to call `build_index()` directly from the command registry, show a preview before cost-bearing work, and avoid shelling out to the Typer CLI.
- Phase 02.3 keeps index as the read/write API surface for downstream skills.

The implementation keeps that design: `/index` still flows through `build_index()` and `split_paper()`, and LLM fallback still returns structured data validated by the existing Pydantic models.

## Implementation strategy change

The failing symptom was:

```text
LLM split response did not match the split schema.
```

The root cause was that `response_model` only added a `tools` array. It did not force the model to call the tool, so compatible providers could still return ordinary message content. That made split fallback brittle: if the model wrote prose or loosely formatted JSON, `_LLMSplitResponse.model_validate_json()` failed.

Per the current project decision, structured output is now implemented uniformly through tool calling:

- `src/cpho_cli/core/llm.py` adds one function tool for each `response_model`.
- The request sets `tool_choice` to that exact function name.
- The request sets `parallel_tool_calls` to `false`.
- The code does not use `response_format: json_schema` or DeepSeek JSON mode.
- Response parsing still accepts provider tool-call arguments, with the existing content fallback retained for compatibility.

This is a small provider-layer change, so split, tagging, topic assignment, solve, and future skills all share the same structured-output behavior.

## Provider compatibility note

DeepSeek models are not interchangeable for tool calling. The existing local config used `deepseek-v4-pro`, which rejected forced tool choice with:

```text
Thinking mode does not support this tool_choice
```

For `/index` tool-calling mode, the DeepSeek provider profile must use a model that supports function/tool calls, such as `deepseek-chat`. This is a model selection requirement, not a schema implementation change.

## REPL behavior fix

`/index` in the REPL now passes `session.config_path` into `build_index()`. Without this, a REPL started with `cpho repl --config ...` could display one config in `/config` but index using whatever `load_config(None)` found from the process working directory.

The REPL dry-run preview text was also adjusted. Dry-run intentionally does not OCR or split, so it cannot honestly predict extracted problem count. The preview now says the real problem count will be known after OCR/splitting.

## Files changed

- `src/cpho_cli/core/llm.py`
- `src/cpho_cli/core/index/builder.py`
- `src/cpho_cli/cli/repl/session.py`
- `src/cpho_cli/cli/repl/app.py`
- `src/cpho_cli/cli/repl/commands/workspace.py`
- `tests/test_llm.py`
- `tests/test_index_builder.py`

