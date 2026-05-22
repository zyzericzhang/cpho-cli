# Phase 1: Core Foundation - Research

**Researched:** 2026-05-22
**Status:** Ready for planning
**Question answered:** What do we need to know to plan Phase 1 well?

## User Constraints

Source: `.planning/phases/01-core-foundation/01-CONTEXT.md`

### Phase Boundary

Phase 1 交付端到端的分析管线 -- 从 API key 配置和 workspace 发现，经 OCR 提取，到结构化 LLM 物理推导 + 答案交叉验证，由 golden test suite 保障输出质量。用户可运行 `cpho solve <problem.pdf>` 获得可信的、分步的物理推导，推导与标准答案交叉对照，OCR 错误被检测并标记而非静默传播。

这不是一次性解题脚本。这是 CPHO 物理竞赛知识库 + skills runtime + agent workflow 原型的核心管线。Skills 必须可复用、可追踪、可调试、可重复调用 -- 这个架构约束从 Phase 1 第一天就要成立。

### Locked Decisions

- D-01: 包管理器使用 uv，负责依赖、虚拟环境、lock 文件和运行命令
- D-02: 项目布局采用 src-layout (`src/cpho_cli/`)，pyproject.toml 在根目录
- D-03: 最低 Python 版本 3.11+
- D-04: 代码质量工具 ruff + mypy。必须有 `uv sync`、`uv run cpho --help`、`uv run ruff check .`、`uv run mypy .`、`uv run pytest`
- D-05: 自定义轻量 skill runner，不做 hardcoded 求解器
- D-06: Hybrid skill-based 架构：`SKILL.md` + YAML 元数据 + Jinja2 prompt 模板 + 可选 Python tools
- D-07: 声明式 key-based blackboard，step 声明 input_keys/output_keys，执行前验证 key 存在
- D-08: LLM/API 瞬时故障指数退避重试；非可重试错误 fail fast；每个 step 写 trace record 和 checkpoint；fallback chain 不默认开启
- D-09: 内置 solve skill 管线七步：提取题目+答案、normalize、验证答案、逐小问推导、cross-check、标记差异、合成结构化报告
- D-10: 轻量 provider 抽象 + OpenRouter 实现
- D-11: Jinja2 模板文件 `prompts/*.md.j2`
- D-12: 结构化输出用 JSON mode + Pydantic 验证；解析失败写入 trace；必要时显式 JSON repair step；不静默正则兜底
- D-13: 模型参数三层优先级：`config.yml` 全局默认 -> per-skill YAML -> CLI flag
- D-14: Golden tests 采用 manual-first evaluation loop
- D-15: Golden test 格式为 per-problem YAML，支持自然语言/`EXPECTATION.md` 转 `spec.yml`
- D-16: 早期人工判断为主，中后期 rubric + LLM judge 辅助；LLM judge 只是筛查器
- D-17: 运行方式：pytest + `cpho eval golden_tests/`
- D-18: 初始规模 3-5 道手动测试起步，架构支持扩展为 20-30 道 regression suite

### Deferred Ideas

无。

## Project Constraints (from AGENTS.md)

- 实现前要明确假设和权衡；不确定时提问。
- 简单优先：不为单一用途创建抽象，不做未要求的灵活性。
- 精准修改：只动必须动的，匹配现有风格，不清理无关代码。
- 目标驱动执行：每项工作要有可验证目标，bug/验证类任务优先用测试复现再修复。

## Standard Stack

Use the following stack for Phase 1 planning:

- Project management: `uv`, `pyproject.toml`, `src/cpho_cli/`, Python `>=3.11`. [CITED: https://docs.astral.sh/uv/guides/projects/]
- CLI: `typer` for `cpho solve`, `cpho eval`, and `cpho --help`, with `typer.testing.CliRunner` for command tests. [CITED: https://typer.tiangolo.com/tutorial/first-steps/] [CITED: https://typer.tiangolo.com/tutorial/testing/]
- PDF/image handling: `PyMuPDF` for PDF opening, page rendering, and image/text extraction. [CITED: https://pymupdf.readthedocs.io/en/latest/how-to-open-a-file.html] [CITED: https://pymupdf.readthedocs.io/en/latest/recipes-images.html]
- OCR: `rapidocr` with ONNX Runtime CPU as the default local OCR engine. RapidOCR docs state default Chinese/English OCR models and show `RapidOCR()` callable usage; this matches the Chinese+English Phase 1 need better than starting with Tesseract. [CITED: https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/usage/] [CITED: https://github.com/RapidAI/RapidOCR]
- DAG scheduling: Python stdlib `graphlib.TopologicalSorter` for deterministic DAG order and cycle detection; no external workflow engine is needed for Phase 1. [CITED: https://docs.python.org/3/library/graphlib.html]
- HTTP client: `httpx` for OpenRouter calls, configured with explicit timeouts and retry wrapper at the provider layer. [CITED: https://www.python-httpx.org/advanced/timeouts/]
- LLM structured output: OpenRouter Chat API with `response_format` `json_schema` where the selected model supports it; always validate again with Pydantic after receipt. [CITED: https://openrouter.ai/docs/guides/features/structured-outputs] [CITED: https://openrouter.ai/docs/api-reference/overview]
- Schemas and validation: Pydantic v2 models for skill metadata, blackboard schemas, step outputs, trace records, and golden spec files. Pydantic can generate JSON Schema from models via `model_json_schema`. [CITED: https://docs.pydantic.dev/usage/schema/]
- Prompt rendering: Jinja2 templates under each skill's `prompts/` directory. [CITED: https://jinja.palletsprojects.com/]
- YAML: PyYAML with `yaml.safe_load()` only for user-editable config and skill metadata. `yaml.load()` is unsafe for untrusted input. [CITED: https://pyyaml.org/wiki/PyYAMLDocumentation]
- Test stack: `pytest`, `typer.testing.CliRunner`, fixture-driven golden specs, and fast unit tests for discovery, DAG validation, config precedence, schema validation, and report assembly.

## Architecture Patterns

### Core-shell split

Keep `src/cpho_cli/core/` independent from Typer, terminal printing, and process exit behavior. CLI code in `src/cpho_cli/cli/` should translate command arguments into core calls and render returned results.

Recommended package shape:

- `src/cpho_cli/cli/app.py` -- Typer app and command wiring
- `src/cpho_cli/core/config.py` -- config discovery, API key loading, model parameter precedence
- `src/cpho_cli/core/workspace.py` -- workspace file discovery and problem/answer pairing
- `src/cpho_cli/core/documents.py` -- PDF/image loading and page rasterization helpers
- `src/cpho_cli/core/ocr.py` -- OCR provider protocol, RapidOCR adapter, confidence/region outputs
- `src/cpho_cli/core/llm.py` -- provider protocol, OpenRouter implementation, retry/error taxonomy
- `src/cpho_cli/core/skills.py` -- skill metadata loader, prompt loader, DAG compiler
- `src/cpho_cli/core/runtime.py` -- blackboard, topological execution, trace/checkpoint writing
- `src/cpho_cli/core/solve.py` -- solve orchestration around the built-in skill
- `src/cpho_cli/core/eval.py` -- golden test runner and result report
- `src/cpho_cli/models/` -- Pydantic models for configs, skill specs, OCR outputs, LLM outputs, trace, eval specs
- `src/cpho_cli/builtin_skills/solve/` -- `SKILL.md`, `skill.yml`, `prompts/*.md.j2`, optional schemas/examples

### DAG runtime

Use `graphlib.TopologicalSorter` to validate step dependencies and produce executable order. Each skill step should declare:

- `id`
- `kind`: `python_tool` or `llm`
- `input_keys`
- `output_keys`
- `prompt_template` for LLM steps
- optional `schema` model name for Pydantic validation
- optional `retry` policy for transient provider failures

The runtime should reject duplicate output keys, missing input keys, cycles, and fallback chains unless the skill explicitly defines them.

### Trace and checkpoint records

Every step writes one JSONL trace record containing:

- run id, skill name, step id, started/finished timestamps
- input key names and file references, not API keys
- rendered prompt path/hash or prompt text only if safe to persist
- model id and non-secret parameters
- output keys, validation status, parse errors, retry count
- checkpoint path for resume

Never write OpenRouter API keys or raw environment values to trace.

### OCR confidence handling

RapidOCR returns text detection/recognition results with confidence-like fields in structured output classes. The Phase 1 plan should normalize OCR output into project-owned `OCRBlock` records with text, bounding box/page, confidence, and `low_confidence` flag rather than leaking RapidOCR-native objects through the rest of core.

For PDFs, PyMuPDF should first extract embedded text when useful, then rasterize pages/images for OCR where embedded text is absent or clearly insufficient. OCR must surface low-confidence or suspicious mathematical regions to the final solve report rather than silently feeding them to the LLM.

### LLM output validation

OpenRouter structured outputs reduce parse failures but are not the trust boundary. Each LLM step must:

1. Request JSON schema where the model supports it.
2. Parse JSON.
3. Validate with Pydantic.
4. On parse/validation failure, write raw output and errors to trace.
5. Run explicit JSON repair only if the skill step declares a repair strategy.

### Answer-key grounding

The solve skill should require a discovered or explicitly supplied answer key before derivation. It should separate derivation generation from answer cross-checking, then synthesize a report that includes:

- main derivation
- why each step follows
- official-answer references
- discrepancies and likely source: OCR issue, model reasoning issue, answer-key ambiguity, or possible answer error
- physics model tags, heuristic insight tags, math technique tags

## Don't Hand-Roll

- Do not build a custom CLI parser; use Typer.
- Do not implement dependency sorting manually; use `graphlib.TopologicalSorter`.
- Do not parse YAML with `yaml.load()` or a custom parser; use `yaml.safe_load()`.
- Do not use regex fallback as the normal structured-output parser; use JSON + Pydantic.
- Do not hardcode a physics solver path into `cpho solve`; execute the built-in solve skill through the same skill runtime used by future skills.
- Do not store API keys in source, trace, golden specs, or git-tracked local config.
- Do not use a database for Phase 1; local files and JSONL are enough per project scope.

## Common Pitfalls

- **OCR is the quality ceiling.** A plan that only calls OCR and forwards text is insufficient; it must preserve page/region/confidence and expose doubtful regions.
- **Answer pairing ambiguity.** Workspace discovery needs deterministic heuristics plus visible diagnostics for unmatched or ambiguous answer files.
- **JSON mode is not validation.** OpenRouter can enforce structured outputs for compatible models, but provider/model support varies; local Pydantic validation remains mandatory.
- **Trace leaks.** Rendered prompts and trace records can accidentally include API keys or full local paths; filter secrets before persistence.
- **Over-abstracting skill runtime.** Phase 1 needs a small DAG runner with key validation and trace/resume, not a full plugin marketplace implementation.
- **Golden tests becoming fake automation.** Early tests should record human expectations and known failure modes; do not pretend LLM judge output is authoritative.
- **Fallback chains hiding quality issues.** Default fallback is off; if a step repairs or retries, trace must show it.

## Security Notes

- API key handling is the primary Phase 1 secret risk. Read from `OPENROUTER_API_KEY` or a local gitignored config file. Reject committed/example configs that contain real-looking keys.
- YAML skill/config files are user-controlled input. Use `safe_load`, schema validation, and explicit allowed fields.
- Prompt templates are executable in the sense that they influence model behavior. Keep template loading path-confined to skill directories and avoid arbitrary includes in Phase 1.
- Trace files can contain problem text and generated reasoning. Store locally under the workspace output directory and document that users should not publish traces blindly.
- Network access should be limited to the OpenRouter provider; OCR and PDF processing are local.

## Code Examples

### DAG validation shape

Use this pattern in implementation tasks, not as final code to paste blindly:

```python
from graphlib import TopologicalSorter

graph = {step.id: set(step.depends_on) for step in steps}
order = tuple(TopologicalSorter(graph).static_order())
```

### OpenRouter structured output shape

Provider calls should send a Pydantic-generated schema in `response_format` when the model supports structured outputs, then validate returned content locally:

```python
schema = DerivationStep.model_json_schema()
payload["response_format"] = {
    "type": "json_schema",
    "json_schema": {"name": "derivation_step", "strict": True, "schema": schema},
}
```

### YAML loading rule

```python
import yaml

data = yaml.safe_load(path.read_text(encoding="utf-8"))
skill = SkillSpec.model_validate(data)
```

## Planning Recommendations

Plan Phase 1 in five dependent plans:

1. Project scaffold, CLI shell, config, and quality gates.
2. Workspace discovery, answer pairing, PDF/image loading, and OCR adapter.
3. Skill runtime, schemas, DAG execution, trace/checkpoint/resume.
4. OpenRouter provider, solve skill prompts/schemas, answer cross-check, and `cpho solve` integration.
5. Golden eval suite, `cpho eval golden_tests/`, sample specs, and end-to-end regression report.

This split keeps the first plan as foundation, allows OCR/document work and runtime/provider work to stay focused, and reserves end-to-end solve/eval wiring for later waves when contracts exist.

## Sources

- uv project docs: https://docs.astral.sh/uv/guides/projects/
- Typer first steps: https://typer.tiangolo.com/tutorial/first-steps/
- Typer testing: https://typer.tiangolo.com/tutorial/testing/
- RapidOCR usage docs: https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/usage/
- RapidOCR repository: https://github.com/RapidAI/RapidOCR
- PyMuPDF opening files: https://pymupdf.readthedocs.io/en/latest/how-to-open-a-file.html
- PyMuPDF images: https://pymupdf.readthedocs.io/en/latest/recipes-images.html
- Python graphlib: https://docs.python.org/3/library/graphlib.html
- HTTPX timeouts: https://www.python-httpx.org/advanced/timeouts/
- OpenRouter structured outputs: https://openrouter.ai/docs/guides/features/structured-outputs
- OpenRouter API overview: https://openrouter.ai/docs/api-reference/overview
- Pydantic JSON Schema: https://docs.pydantic.dev/usage/schema/
- Jinja docs: https://jinja.palletsprojects.com/
- PyYAML docs: https://pyyaml.org/wiki/PyYAMLDocumentation

## RESEARCH COMPLETE

