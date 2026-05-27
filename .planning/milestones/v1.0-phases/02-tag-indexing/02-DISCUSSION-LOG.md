# Phase 2: Tag Indexing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-23
**Phase:** 2-Tag Indexing
**Areas discussed:** Index architecture, Tag source strategy, Controlled vocabulary enforcement, Incremental update hash strategy

---

## Index Architecture

| Option | Description | Selected |
|--------|-------------|----------|
| Core module | Standalone cpho_cli/core/index.py, direct CLI integration | |
| Built-in skill | Like solve, runs through SkillRuntime | |
| Hybrid | Core module owns schema/storage/hash/query; LLM tagging borrows DAG conventions | ✓ |

**User's choice:** Hybrid with core-module ownership. Core module owns schema, JSONL storage, hashing, stale detection, vocabulary normalization, and query functions. LLM tagging reuses existing DAG/skill-runtime conventions for prompt versioning, traceability, structured output validation. Must use existing cpho_cli/core/llm.py provider abstraction. Must export Python APIs: query_index, get_problem_entry, find_related_problems.

**Notes:** Skills call index APIs directly, not via CLI subprocess. Index is infrastructure consumed by downstream skills, not a user-facing analysis command.

---

## Tag Source Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Always dedicated LLM tagging | Single-purpose prompt per problem | |
| Reuse solve report tags + fallback | Free for solved problems, LLM only for unsolved | |
| Solve tags as seed + refine | Lower cost than full re-tag | |
| Multi-source with normalization pass | User notes → SolveReport → Q&A → OCR fallback, then refine | ✓ |

**User's choice:** Index is a learning memory / mistake-book layer, not pure auto-tagging. Source priority: (1) User notes/key points → (2) SolveReport structured analysis → (3) Q&A history → (4) Cached OCR fallback. Dedicated normalization/refinement pass consumes available artifacts → controlled index fields. No generic difficulty labels — capture WHY the problem is hard.

**Notes:** Index fields: canonical knowledge/model tags, math technique tags, heuristic/insight tags, user-confirmed key points, user-confirmed 卡点, source provenance.

---

## Controlled Vocabulary Enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Closed vocabulary | Fixed list, LLM selects only from it | |
| Open with self-consistency | LLM sees prior tags, adds new only when justified | |
| Freeform + post-hoc normalization | LLM freeform, then normalize | |
| Three-tier vocabulary system | Built-in base + workspace/team + user-private | ✓ |

**User's choice:** Three-tier vocabulary. System-readable physics taxonomy + user-facing mistake-book language, connected via review skill. Built-in base vocabulary shipped with project. Workspace/local vocabulary grows over time. User-private vocabulary/notes not committed by default. Semi-open: LLM reuses existing, new tags enter candidate/pending, user approves. Chinese display names + English internal IDs + aliases. Review skill suggests mappings; user confirmation required before merge into canonical vocabulary.

**Notes:** git commit/export must prompt user to decide which vocabulary layers to include. No automatic merge of user language into system taxonomy.

---

## Incremental Update: Hash Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Single-layer hash | All inputs combined, any change = full re-index | |
| Two-layer hash | File layer + content layer | |
| Three-layer hash | File → semantic/system → user learning/refinement | ✓ |

**User's choice:** Three-layer hash with layered output statistics. Separate storage: main system index, hash/fingerprint state, vocabulary file, user notes, OCR cache. OCR engine upgrade: detect via fingerprint, mark stale, prompt user with options (rebuild all / affected only / skip / new files only).

**Notes:** User note changes counted separately as refinement-layer change, not full re-index. cpho index output shows layered statistics: file changes, OCR reuse, tag regeneration, note changes, refinement suggestions, pending reviews.

---

## Claude's Discretion

所有关键实现决策均由用户明确指定。具体实现细节（文件格式、API 签名、错误处理）由 planner 和 researcher 根据代码库既有模式决定。

## Deferred Ideas

无——讨论全程在 Phase 2 范围内。
