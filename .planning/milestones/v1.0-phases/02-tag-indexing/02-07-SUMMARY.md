---
phase: 02
plan: "02-07"
subsystem: "index/topic"
tags: [topic-hierarchy, llm-classification, query-api, cli, compose]
dependency_graph:
  requires: ["02-01", "02-04", "02-05", "02-06"]
  provides: ["topic-model", "topic-taxonomy", "topic-assignment", "topic-api", "compose-api", "topic-cli"]
  affects: ["index-entry", "build-index", "cli-app", "core-index-init"]
tech_stack:
  added: []
  patterns: ["3-layer-vocabulary-topics", "llm-topic-classification", "prefix-matching-query", "topic-tag-intersection-compose"]
key_files:
  created:
    - src/cpho_cli/models/topic.py
    - src/cpho_cli/vocabulary/topics/builtin_topics.yml
    - src/cpho_cli/core/index/topic_vocabulary.py
    - src/cpho_cli/core/index/topic_assignment.py
    - src/cpho_cli/core/index/prompts/topic_assignment.md.j2
    - src/cpho_cli/core/index/topic_api.py
    - src/cpho_cli/core/index/compose.py
    - tests/test_topic_models.py
    - tests/test_topic_vocabulary.py
    - tests/test_topic_assignment.py
    - tests/test_topic_api.py
    - tests/test_compose.py
    - tests/test_topic_cli.py
    - tests/test_topic_builder_integration.py
  modified:
    - src/cpho_cli/models/index.py
    - src/cpho_cli/core/index/__init__.py
    - src/cpho_cli/core/index/builder.py
    - src/cpho_cli/core/index/prompts/MANIFEST.yml
    - src/cpho_cli/cli/app.py
    - pyproject.toml
decisions:
  - "Topic assignment is non-blocking in build_index: failure sets topic_path=None but does not prevent tag indexing"
  - "Topic taxonomy loading failure is non-blocking: disables topic assignment for the entire run"
  - "FakeLLMProviderWithTopic routes by response_model.__name__ to support both tag and topic calls"
metrics:
  duration: "8m"
  completed: "2026-05-23T12:26:04Z"
  tasks: 4
  tests_added: 36
  files_created: 14
  files_modified: 6
---

# Phase 02 Plan 07: Topic Hierarchy Classification, Query API, CLI, and MVP Exam Composition Summary

Hierarchical topic classification as a second indexing dimension alongside flat tags, with LLM-driven assignment, prefix-matching query API, CLI commands, and exam composition by topic+tag intersection.

## Commits

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| T1 | Topic data models, taxonomy YAML, 3-layer loader, IndexEntry extension | 583392a | models/topic.py, builtin_topics.yml, topic_vocabulary.py, index.py |
| T2 | LLM topic assignment pipeline with Jinja2 prompt and trace | 336dd6c | topic_assignment.py, topic_assignment.md.j2, MANIFEST.yml |
| T3 | Topic query API, compose API, CLI commands, and re-exports | b8391de | topic_api.py, compose.py, app.py, __init__.py |
| T4 | Wire assign_topic into build_index orchestrator | bae5d46 | builder.py, test_topic_builder_integration.py |

## What Was Built

### Topic Data Models (T1)
- `TopicNode` tree model with self-referential children, `TopicTaxonomy` container
- `flatten_paths()` returns all slash-separated display_zh paths for prompt rendering
- `find_node_by_path()` validates LLM output against the taxonomy tree
- `IndexEntry.topic_path: str | None = None` field added (backward compatible)

### Builtin Topic Taxonomy (T1)
- 5 root categories: mechanics, thermodynamics, electromagnetism, optics, modern physics
- 2-3 levels deep covering CPhO/IPhO competition topic areas
- YAML structure validated by Pydantic TopicTaxonomy model

### 3-Layer Topic Loader (T1)
- builtin -> workspace override -> private override (same pattern as tag vocabulary)
- Merge strategy: override display_zh by id, add new children, append new roots
- Version string: `v0.1+bt-{sha8}+ws-{sha8}+pv-{sha8}`

### LLM Topic Assignment (T2)
- `assign_topic()` with provider injection, response_model, taxonomy validation
- Jinja2 prompt template with anti-injection warning
- Trace writing with API key redaction (reuses tagging.py patterns)
- Invalid topic paths from LLM rejected with IndexBuildError

### Topic Query API (T3)
- `find_problems_by_topic()` with prefix matching (query "力学" returns all mechanics subtopics)
- `get_topic_tree()` returns merged taxonomy
- `compose_problem_list()` intersects topic prefix and tag filters for exam composition

### CLI Commands (T3)
- `cpho topic list` displays the full topic tree as indented Chinese text
- `cpho topic browse <path>` lists problems matching a topic prefix
- `cpho compose --topic <path> --tags <id1,id2>` combined filtering for exam composition

### Build Index Integration (T4)
- Topic taxonomy loaded at build_index start (non-blocking on failure)
- assign_topic called after refine_tags for each problem
- Topic assignment failures are non-blocking (topic_path=None, tags preserved)
- Skip and refinement_only actions preserve existing topic_path

## Test Results

- 36 new tests added across 7 test files
- Full suite: 216 tests passing, zero regressions
- All ruff checks pass
- All new source files lint clean

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED
