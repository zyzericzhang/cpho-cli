# Phase 1: Core Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-21
**Phase:** 1-Core Foundation
**Areas discussed:** Project scaffold & toolchain, DAG pipeline engine, LLM & prompt management, Golden test suite design

---

## Project Scaffold & Toolchain

| Option | Description | Selected |
|--------|-------------|----------|
| uv (Recommended) | Fastest — Rust-based, pip-compatible, built-in venv + lockfile | ✓ |
| Poetry | Mature, widely adopted, strong dependency resolver | |
| pip + venv + pip-tools | Simplest — no extra tool, pip-tools for lockfiles | |

| Option | Description | Selected |
|--------|-------------|----------|
| src-layout (Recommended) | `src/cpho_cli/` package, prevents accidental root imports | ✓ |
| Flat layout | `cpho_cli/` directly at root, simpler dev imports | |

| Option | Description | Selected |
|--------|-------------|----------|
| 3.11+ (Recommended) | tomllib built-in, better errors, Ubuntu 24.04 ships 3.12 | ✓ |
| 3.10+ | Broader compatibility (Ubuntu 22.04 LTS), needs tomli | |
| 3.12+ | Cutting edge, best typing/perf, may miss older systems | |

| Option | Description | Selected |
|--------|-------------|----------|
| ruff + mypy (Recommended) | ruff for lint+format, mypy for type checking | ✓ |
| Ruff only | Simpler, skip type checking for now | |
| Full suite: ruff + mypy + pre-commit | pre-commit hooks on every commit, most thorough | |

---

## DAG Pipeline Engine

| Option | Description | Selected |
|--------|-------------|----------|
| Custom lightweight (Recommended) | Thin DAG scheduler — topological sort + blackboard + async runner | ✓ |
| Existing framework | LangGraph/Haystack/DSPy — faster start, more dependencies | |

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid skill-based | SKILL.md + YAML + Jinja2 prompts + optional Python tools + trace. Users create skills without Python | ✓ (user customized) |
| Python functions + decorator | Each step is an async function — most natural for devs | |
| YAML config-based | Steps defined in YAML — users add custom steps without Python | |
| Hardcoded modules | No runtime step definitions — hardcoded in solve_*.py | |

| Option | Description | Selected |
|--------|-------------|----------|
| Declarative key-based blackboard (Recommended) | Steps declare input_keys/output_keys in YAML, engine validates | ✓ |
| Typed Pydantic state chain | Return typed models per step, engine merges — more boilerplate | |
| Unstructured namespace | Free read/write namespace — simplest but least safe | |

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid: retry + fail fast + checkpoint/resume | Transient retry + fail fast with diagnostics + trace & checkpoint per step | ✓ (user customized) |
| Simple retry + fail fast | LLM failures retry N times, non-retryable bubble up | |
| Fallback chain | Simpler prompt/model on failure — may mask quality issues | |
| Checkpoint & resume | Create checkpoint on failure, resume from fix point | |

| Option | Description | Selected |
|--------|-------------|----------|
| Linear with cross-check (Recommended) | 7-step pipeline with dedicated answer-key cross-check, step boundaries for future upgrade | ✓ |
| Single LLM pass + post-compare | One LLM call for all derivation, post-hoc answer comparison | |
| Derive-verify-reconcile loop | Independent verify + reconcile per sub-question — thorough but more calls | |

| Option | Description | Selected |
|--------|-------------|----------|
| Per-skill prompts/ dir (Recommended) | Self-contained in skill folder, portable, shareable | ✓ |
| Global prompts/ directory | Centralized — easier to find, less portable | |
| Inline in YAML | Simplest for short prompts, not for long ones | |

---

## LLM & Prompt Management

| Option | Description | Selected |
|--------|-------------|----------|
| 轻量抽象接口 (Recommended) | Base class + OpenRouter impl — future providers just implement same interface | ✓ |
| 先硬编码 OpenRouter | No abstraction layer, add when second provider needed | |

| Option | Description | Selected |
|--------|-------------|----------|
| Jinja2 (Recommended) | Mature, lightweight — conditions, loops, variable injection. Templates: prompts/*.md.j2 | ✓ |
| 简单占位符替换 | {var} placeholders, str.format() — zero learning, no conditions | |
| Frontmatter + {{ }} | YAML frontmatter declares vars, {{ var }} in body | |

| Option | Description | Selected |
|--------|-------------|----------|
| JSON mode + Pydantic (Recommended) | response_format JSON, Pydantic validation, failures → trace + optional JSON repair | ✓ |
| Markdown 解析 + 正则 | Regex parse of Markdown — no model capability dependency, weaker | |
| JSON mode + 正则兜底 | Try JSON first, fallback to regex — may hide parse failures | |

| Option | Description | Selected |
|--------|-------------|----------|
| 三层优先级 (Recommended) | config.yml → per-skill YAML → CLI flag (highest) | ✓ |
| 仅全局配置 | All params in config.yml, skill can't override model | |
| Per-skill 独立配置 | Each skill has own model/params, no global default | |

---

## Golden Test Suite Design

| Option | Description | Selected |
|--------|-------------|----------|
| Manual-first loop | User runs skill → inspects output → identifies gaps → Agent fixes → regressible failures → golden cases | ✓ (user customized) |
| Full YAML suite upfront | 20-30 problems fully spec'd before any implementation | |

| Option | Description | Selected |
|--------|-------------|----------|
| Per-problem YAML + EXPECTATION.md | YAML as machine storage, user writes natural language EXPECTATION.md → Agent generates spec.yml | ✓ (user customized) |
| 单一 JSONL | Single file for all problems — programmatic, less human-editable | |
| pytest 参数化 | Python-based test cases — most flexible, non-technical users can't edit | |

| Option | Description | Selected |
|--------|-------------|----------|
| Rubric 人工评分 (Recommended) → LLM judge later | Early: human. Mid/late: rubric + LLM judge as auto-screener. Human review for boundaries/releases/major changes | ✓ |
| LLM-as-judge | Stronger model as judge — fast but extra cost + judging bias | |
| Rubric + LLM judge | Both required — complementary but more complex | |

| Option | Description | Selected |
|--------|-------------|----------|
| pytest + CLI (Recommended) | pytest for dev/CI, `cpho eval` for user-friendly local evaluation | ✓ |
| 独立 CLI | Custom `cpho test` without pytest dependency | |
| Makefile 封装 | Makefile wrapping pytest — extra layer | |

| Option | Description | Selected |
|--------|-------------|----------|
| 用户自定义测试集 → 3-5 道起步 | Architecture supports user-defined sets. Start 3-5 manual → grow through failure precipitation. Optional official recommended set | ✓ (user customized) |
| 五大领域均匀分布 | 4-6 problems each in mechanics, EM, thermo, optics, modern | |
| 聚焦力学+电磁学 | 80% in mechanics + EM — core difficulty areas | |

---

## Claude's Discretion

无——所有关键实现决策均由用户明确指定。

## Deferred Ideas

无——讨论全程在 Phase 1 范围内。
