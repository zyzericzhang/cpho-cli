---
phase: 06-skill
status: complete
created: 2026-05-27
workflow: gsd-plan-phase --research
---

# Phase 6 Research: Knowledge Base + Skill Pipeline Foundation

## RESEARCH COMPLETE

## Objective

Research how to implement Phase 6 well enough for execution planning:

- KB-01 through KB-04
- SKILL-PIPE-01 through SKILL-PIPE-03

This research uses the existing v1.0 codebase, Phase 6 context, v1.1 requirements, and the real user workspace at `/Users/ericzhang/Desktop/物理竞赛资料`.

## Real Workspace Findings

Sampled real workspace shape:

- PDF-heavy Chinese file names, e.g. `第四届芝麻物理联考 (复赛) 理论试题.pdf`, `第四届芝麻物理联考试卷参考答案.pdf`, `CPhOfan2023年度试题.pdf`.
- Existing hidden `.cpho/` directory is present in the real workspace.
- File organization is folder-based by source/year, not one problem per folder.
- Phase 6 knowledge files must therefore live under `.cpho/knowledge/` and must not assume problem files are renamed or moved.

Implication: Knowledge files should reference canonical tags, not physical problem paths. Resolver should read the existing `.cpho/index.jsonl` and map problem tags to knowledge frontmatter.

## Existing Architecture

Reusable v1.0 patterns:

- `src/cpho_cli/models/skills.py` already has declarative `SkillStep` and `SkillSpec`.
- `src/cpho_cli/core/runtime.py` already executes a DAG via input/output key dependencies and explicit `depends_on`.
- `src/cpho_cli/core/skill_handlers.py` already routes LLM steps through Jinja2 prompts and can attach `problem_file` / `answer_file` as multimodal content when capabilities allow.
- `src/cpho_cli/core/index/vocabulary.py` loads built-in plus workspace vocabulary and should be reused to validate `canonical_tag_id`.
- `src/cpho_cli/core/index/api.py` exposes problem lookup helpers and should be reused by `KnowledgeResolver.find_for_problem(problem_id)`.

## Design Decisions for Execution

1. Treat current `SkillSpec` as the concrete `SkillPipeline` rather than adding a parallel framework. Add optional fields to `SkillStep`:
   - `description: str | None`
   - `default_model: str | None`
   - `requires_multimodal: bool = False`
   Existing skill YAML remains valid.

2. Add `SkillSpec.describe(skill_root: Path | None = None) -> PipelineDescription`.
   - Step descriptions include id, kind, description, default model, requires_multimodal, prompt template, resolved prompt path, inputs, outputs, and dependencies.
   - Edges include explicit `depends_on` plus implicit input/output producer edges.

3. Add `SkillPipeline = SkillSpec` alias for naming clarity and future Phase 7 consumers.

4. Implement private KB under:
   - `.cpho/knowledge/files/inbox/`
   - `.cpho/knowledge/files/published/`
   - `.cpho/knowledge/drafts/`
   Also scan `.cpho/knowledge/files/*.md` for compatibility with the requirement wording.

5. Knowledge frontmatter minimum:
   - `canonical_tag_id`
   - `standardized`
   - `last_normalized_hash`
   - `last_user_edit_hash`
   Optional: `title`, `source`, `tags`, `summary`.

6. `KnowledgeResolver.find_for_problem(problem_id)` reads the index entry, collects all tag ids from physics/math/heuristic/user tags, validates knowledge file tags against the merged vocabulary, and returns private matches first. Community discovery is stubbed through `~/.cache/cpho/community-kb/` so Phase 8 can fill sync without changing the resolver signature.

7. Standardization uses a simple two-step CLI:
   - `cpho knowledge normalize <file>` writes or updates a draft under `.cpho/knowledge/drafts/`.
   - `cpho knowledge publish <draft>` validates frontmatter and copies to `.cpho/knowledge/files/published/`.
   A `--publish` flag may combine the two for tests, but the normal path remains review-first.

8. Text/markdown/LaTeX inputs can be normalized locally into a draft shell. Images and docx must call LLM normalization when not in `--dry-run` mode. This preserves Phase 6's multimodal direction while keeping deterministic tests available.

9. Do not migrate solve/probe/related/compose behavior in Phase 6. Compatibility is verified by existing tests plus targeted skill model tests.

## Risks

- Existing OpenAI-compatible multimodal code only attaches keys named `problem_file` and `answer_file`. Phase 6 should keep normalize multimodal routing narrow and avoid broad handler refactors until Phase 7 input routing.
- Docx image extraction is richer than Phase 6 needs. Use `mammoth` for semantic markdown text and pass the original file path to the LLM when supported later; avoid LibreOffice or system dependencies.
- `canonical_tag_id` validation must be explicit. Silent skips would break the trust model for Explain v2.

## Validation Architecture

Unit tests should cover:

- SkillStep optional fields and `SkillSpec.describe()` output.
- Existing built-in skills still load unchanged.
- Knowledge frontmatter parser accepts valid files and rejects missing/unknown canonical tags with clear paths/fields.
- Resolver finds knowledge files for an indexed problem by canonical tag and returns private before community.
- Normalize writes a draft with required frontmatter; publish validates and writes to `files/published`.
- CLI smoke tests for `cpho knowledge normalize`, `cpho knowledge publish`, and `cpho knowledge find`.

Integration smoke:

- Use a tiny temporary workspace modeled after `/Users/ericzhang/Desktop/物理竞赛资料`: Chinese PDF-style names are enough for path handling, while index entries can be fixture JSONL.
- Run `uv run pytest tests/test_skills.py tests/test_knowledge.py tests/test_knowledge_cli.py -q`.
- Run full `uv run pytest -q` before Phase 6 closeout.

