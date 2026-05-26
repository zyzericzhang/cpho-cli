# /index live verification

Date: 2026-05-25

## Test workspace

To keep cost and runtime low while still matching the real user workspace shape, I created four temporary workspaces under `/tmp` from the first two pages of this real file:

```text
/Users/ericzhang/Desktop/物理竞赛资料/杂题/各路模拟题/2022-12yue-GPhO-47G-A4.pdf
```

Each workspace contained one PDF:

```text
gpho-small.pdf
```

The source PDF uses Chinese exam-paper text and does not match the current deterministic numeric marker regex cleanly, so the run exercises the LLM split fallback path.

## Provider configuration

OpenRouter used the cheap configured model:

```text
openai/gpt-4o-mini
```

DeepSeek used a transient local config with the existing API key but a tool-call-capable model:

```text
deepseek-chat
```

The existing `deepseek-v4-pro` profile was not used for final verification because it rejected forced `tool_choice` in thinking mode.

The transient config file was removed after verification.

## Automated checks

```bash
uv run ruff check src/cpho_cli/core/llm.py src/cpho_cli/core/index/builder.py src/cpho_cli/cli/repl/session.py src/cpho_cli/cli/repl/app.py src/cpho_cli/cli/repl/commands/workspace.py tests/test_llm.py tests/test_index_builder.py
```

Result:

```text
All checks passed.
```

```bash
uv run pytest tests/test_llm.py tests/test_splitting_fallback.py tests/test_index_builder.py::test_build_index_constructs_provider_for_split_fallback_without_network tests/test_repl_workspace_commands.py -q
```

Result:

```text
15 passed, 5 warnings
```

```bash
uv run pytest -q
```

Result:

```text
311 passed, 5 warnings
```

The warnings are existing PyMuPDF/SWIG deprecation warnings, not failures.

## Live CLI verification

OpenRouter CLI:

```bash
uv run cpho index /tmp/cpho-index-openrouter-cli --config /Users/ericzhang/Desktop/cpho-cli/config.local.yml --provider openrouter --ocr-strategy reuse
```

Result:

```text
切分试卷数: 1
提取题目数: 2
规则切分: 0
LLM 切分: 2
单题路径: 0
重新生成: 2
完成. 索引: /tmp/cpho-index-openrouter-cli/.cpho/index.jsonl
```

DeepSeek CLI:

```bash
uv run cpho index /tmp/cpho-index-deepseek-cli --config /tmp/cpho-index-tool-config.yml --provider deepseek --ocr-strategy reuse
```

Result:

```text
切分试卷数: 1
提取题目数: 2
规则切分: 0
LLM 切分: 2
单题路径: 0
重新生成: 2
完成. 索引: /tmp/cpho-index-deepseek-cli/.cpho/index.jsonl
```

## Live REPL verification

The REPL command path was exercised through `ReplApp.dispatch()` with a prompt session stub that answered `y` to the confirmation prompt.

OpenRouter REPL:

```text
/index --all --ocr-strategy reuse
```

Result:

```text
切分完成 [1/1]: 累计提取 2 题
索引完成: 2 个输入
```

DeepSeek REPL:

```text
/index --all --ocr-strategy reuse
```

Result:

```text
切分完成 [1/1]: 累计提取 2 题
索引完成: 2 个输入
```

## Final status

The `/index` feature now runs end to end through both CLI and REPL entry points with OpenRouter and DeepSeek, including the LLM split fallback path that previously failed schema validation.
