---
phase: 05-user-manual-opensource
type: research
created_at: 2026-05-26
branch: feature/phase5
---

# Phase 5 Research

## Current Repository State

- `README.md` is still Phase 1 oriented and mentions removed `eval`.
- `docs/user/` does not exist.
- Phase 3/4 decision docs exist and should be the source of truth for user docs.
- REPL skill registration is explicit, not auto-discovered from arbitrary `builtin_skills/` directories.
- The codebase is MIT-oriented in planning docs but no `LICENSE` file exists yet.
- `.github/ISSUE_TEMPLATE/` does not exist.

## Real Workspace Shape

Sampled `/Users/ericzhang/Desktop/物理竞赛资料` again. User data is a deeply nested Chinese PDF workspace with mixed problem, answer, notice, and compiled handout files. Documentation must emphasize:

- index a whole folder;
- use `/search` and `/show` before skill commands;
- outputs go under `.cpho` or configured export paths;
- real workspaces can include unrelated PDFs, so preview/dry-run style commands matter.

## Implementation Conclusions

- README should be rewritten around the current Phase 3/4 command surface, not Phase 1.
- `docs/user/` should document actual implemented commands: solve, explain, probe, related, compose, index.
- Extension docs should be honest: current extension path is copying a built-in command/service pattern and registering a REPL command explicitly. Automatic arbitrary directory scanning is deferred because the actual implementation does not support it.
- Demo asset can be a checked-in SVG terminal transcript under `.github/assets/`, avoiding dependency on an external recorder during tests.
- Examples can be small repository-local sample files and instructions. Full third-party IPhO image assets should be added only after explicit license/source verification.

