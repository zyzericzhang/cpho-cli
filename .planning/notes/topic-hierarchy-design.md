---
title: "Topic Hierarchy + Category Redesign — Design Decisions"
date: 2026-05-23
context: "Exploration session with gsd-explore. Decisions for Phase 2 extension."
---

## Summary

This note captures design decisions made during exploration of three related topics:
1. Category system redesign for the vocabulary/tag system
2. Exam paper → individual problem splitting strategy
3. Hierarchical topic classification as a new dimension (separate from flat tags)

## Decision 1: Category System Redesign

### What changed

Old 5 categories → New 5 categories:

| Old | New | Semantic shift |
|-----|-----|---------------|
| `physics_model` | `physics_law` | Narrowed: specific physics laws (partition function, effective potential). Textbook basics like Newton's laws should NOT be tagged as physics_law. |
| — | `physics_model` | New meaning: concrete models extracted from papers (e.g., rainbow scattering model). Specific, not generic. |
| `math_technique` | `math_technique` | Kept. Refined to include things like exact differentials in ODEs. |
| `heuristic` | `heuristic` | Kept. Refined to include strategies like phase diagrams, optical-mechanical analogy. |
| `approximation` | `approximation` | Kept. Refined: concrete approximation methods (integral expansion, etc.), not generic "small angle approx". |
| `system_selection` | (removed) | Merged into `heuristic`. |

### Action items

- [ ] Update `TagCategory` enum in `src/cpho_cli/models/index.py`
- [ ] Reassign 16 existing tags in `builtin.yml` to new categories (15 `physics_model` tags + 1 `system_selection` tag)
- [ ] `docs/vocabulary-extraction-prompt.md` already updated by user

## Decision 2: Exam Paper → Individual Problem Splitting

### Problem

Source materials are exam papers (7-8 problems per paper), but the index needs per-problem granularity for:
- Accurate tagging (tags describe what a specific problem uses, not the whole exam)
- Exam composition (future feature, minimum unit = individual problem)

### Decision

- **Problem = atomic unit of the index.** One `IndexEntry` per problem.
- **Exam paper = input container only.** Papers are split before indexing.
- **Splitting method: LLM auto-split.** An agent reads the exam PDF and outputs problem boundaries (start/end pages, problem numbers). No manual pre-processing, no sidecar files.
- **Implementation note:** Splitting step happens before the existing index pipeline. Split output = individual problem files → then normal indexing flow.

### Implications

- `IndexEntry.problem_path` already points to a single problem file — model is aligned
- Need a splitting step (likely a CLI command or pre-index hook)
- Splitting should be idempotent and fingerprint-aware (don't re-split unchanged exams)

## Decision 3: Two Independent Systems — Tags vs Topics

### Tags (flat, multiple per problem)

- Semantic: "What knowledge/techniques/insights does this problem use?"
- Cardinality: many per problem
- Source: discovered during solving, user follow-up, LLM analysis
- Example: a problem tagged with `angular_momentum_conservation` + `binnet_equation` + `coordinate_transform`

### Topics (hierarchical, single per problem)

- Semantic: "What subject area does this problem belong to?"
- Cardinality: exactly one per problem (single taxonomic path)
- Source: LLM classification based on content
- Purpose: primary retrieval axis for browsing and exam composition
- Example: 力学/天体运动/轨道理论

### Why not merge them?

Tags are multi-dimensional insights discovered organically. Topics are a single navigational hierarchy. Merging would force artificial parent-child relationships on tags that are naturally flat (e.g., is "coordinate transform" a child of "mechanics" or "math"?).

## Decision 4: Topic Hierarchy Extends Phase 2

### Rationale

- Topic classification uses the same infrastructure (LLM calls, index storage, query API) being built in Phase 2
- Adding it to Phase 2 avoids a separate phase bootstrap overhead
- Phase 2 already owns "index infrastructure" — topic hierarchy is part of indexing

### Plan structure

Current Phase 2 plans + new addition:

```
02-01: Data model + storage [DONE]
02-02: 3-layer hashing [DONE]
02-03: OCR cache wrapper [pending]
02-04: LLM tag generation pipeline [pending]
02-05: Orchestration + CLI + query API [pending]
02-06: Builtin vocabulary [pending review]
02-07: Topic hierarchy classification [NEW — to be planned]
```

### What 02-07 needs to deliver

- `TopicNode` data model (Pydantic, tree structure, parent-child)
- Topic taxonomy YAML (builtin, shipped with project — initial structure TBD)
- `IndexEntry` extension: `topic_path` field (e.g., "力学/天体运动/轨道理论")
- LLM-based topic assignment: given a problem, output its single topic path
- Query API extension: `find_problems_by_topic(topic_path)`, `get_topic_tree()`
- CLI: `cpho topic list`, `cpho topic browse <path>`
- Topic-aware exam composition: filter problems by topic + tags (MVP for composition feature)
- Topic vocabulary layer support (builtin / workspace / private, same as tags)
- Integration with the existing index build pipeline (topic assignment runs as part of `cpho index`)

### Scope boundary for 02-07

Must deliver:
- Data model + taxonomy file + LLM assignment + query API + basic CLI
- MVP exam composition: `cpho compose --topic <path> --tags <tag1,tag2>` → outputs problem list

Deferred:
- Full exam PDF generation (just output problem list for now)
- Topic conflict resolution (if LLM is uncertain between two topics)
- Topic taxonomy editor/browser UI
- Auto-generation of topic taxonomy from problem corpus

## Handoff Notes for Plan-Writing Agent

When writing 02-07-PLAN.md:

1. **Read `02-CONTEXT.md` first** — the supplement section at the bottom has Phase 2 integration details
2. **The topic model is a tree, not a DAG** — each node has exactly one parent, each problem has exactly one topic path
3. **Topic assignment is LLM-driven** — prompt the LLM with the full taxonomy tree, ask it to choose the best matching leaf node
4. **Topic vocabulary follows the same 3-layer pattern as tags** (builtin / workspace / private), reuse existing vocabulary loader patterns
5. **The `topic_path` field** should be stored as a string path (e.g., "力学/天体运动/轨道理论"), not as a foreign key — this avoids integrity issues when the taxonomy changes
6. **Exam composition is in scope** for 02-07 as an MVP feature — it's the primary use case for topic hierarchy
7. **Reuse patterns from existing plans** — 02-01 for data model patterns, 02-04 for LLM prompt patterns, 02-05 for CLI/API patterns
