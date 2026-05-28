---
status: testing
phase: 06-skill
source: [.planning/phases/06-skill/06-01-SUMMARY.md, .planning/phases/06-skill/06-02-SUMMARY.md, .planning/phases/06-skill/06-03-SUMMARY.md, .planning/phases/06-skill/06-04-SUMMARY.md, .planning/phases/06-skill/06-05-SUMMARY.md]
started: 2026-05-28T14:06:35Z
updated: 2026-05-28T14:06:35Z
---

## Current Test

number: 1
name: Skill Pipeline Metadata Is Visible
expected: |
  Loading a built-in skill and calling its description API shows the pipeline steps with step names, resolved prompt paths, default model information, multimodal requirements, and producer edges, while existing v1.0 skill YAML still loads normally.
awaiting: user response

## Tests

### 1. Skill Pipeline Metadata Is Visible
expected: Loading a built-in skill and calling its description API shows the pipeline steps with step names, resolved prompt paths, default model information, multimodal requirements, and producer edges, while existing v1.0 skill YAML still loads normally.
result: [pending]

### 2. Private Knowledge Lookup Returns Relevant Files
expected: Given a workspace problem with indexed tags and private knowledge files under `.cpho/knowledge/files/`, `KnowledgeResolver.find_for_problem(problem_id)` returns matching private knowledge files first, using exact tag matches before same-category fallback.
result: [pending]

### 3. Knowledge Normalize Then Publish Preserves Review Flow
expected: Running the knowledge normalization flow creates a reviewable draft with required frontmatter and hashes instead of publishing immediately; after user review, publishing validates the draft, writes it into the private knowledge area, and preserves the normalized hash while updating the user-edit hash.
result: [pending]

### 4. Knowledge CLI Workflow Is Usable
expected: A user can run `cpho knowledge normalize`, `cpho knowledge publish`, and `cpho knowledge find` for the private KB workflow, and the user documentation explains this Phase 6 behavior without claiming community sync is available yet.
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps

[none yet]
