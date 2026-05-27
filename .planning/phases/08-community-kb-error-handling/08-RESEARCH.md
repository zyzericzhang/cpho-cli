---
phase: 08-community-kb-error-handling
status: complete
created: 2026-05-27
workflow: gsd-plan-phase --research
---

# Phase 8 Research: Community KB + Error Handling

## RESEARCH COMPLETE

## Objective

Research how to implement:

- KB-05 community knowledge sync.
- ERROR-01 clearer user-facing errors.
- ERROR-02 docs/user/errors index and guard tests.

## Findings

- Phase 6 already has private knowledge files and `KnowledgeResolver`; resolver has a community scan hook using `~/.cache/cpho/community-kb/`.
- Phase 7 Explain already wraps `KnowledgeMatch` data into `<knowledge_reference ...>` blocks.
- CLI is Typer-based; `knowledge_app` already exists and can host `sync`.
- `httpx` is already a dependency.
- The project has many historical `raise` sites. Phase 8 should establish a grep-enforceable helper convention first, then migrate the main user-visible surfaces touched by v1.1.

## Implementation Strategy

1. Add community config + sync:
   - Config path default: `~/.config/cpho/community.yml`.
   - Shape: `repositories: [{url, tag, enabled}]`, optional `github_token`.
   - Use GitHub API release endpoint to resolve `tarball_url`.
   - Download tarball, extract knowledge files, validate basic frontmatter `canonical_tag_id`, write to `~/.cache/cpho/community-kb/<repo-name>/`.
   - Write `metadata.json`.
   - chmod files read-only.
   - Default idempotent skip unless `--force`.

2. Add CLI:
   - `cpho knowledge sync --config ... --cache-dir ... --force`.
   - Never writes private workspace knowledge.

3. Add `core/errors.py`:
   - Helper functions named `err_*`.
   - Use helpers in config missing key, skill prompt missing, knowledge frontmatter, and community sync errors.
   - Tests enumerate helper names and require matching docs files.

4. Docs:
   - `docs/user/community-kb.md`.
   - `docs/user/errors/*.md`.
   - README error index section.

## Validation Architecture

- Mock GitHub release/tarball sync with `httpx.MockTransport`.
- Verify cache layout, metadata, read-only file mode, idempotent skip/force.
- Verify resolver can read from `CPHO_COMMUNITY_KB_DIR` in tests.
- Verify `err_*` docs coverage.
- Full pytest and ruff before closeout.

