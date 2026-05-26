# Phase 3 Export and Settings Decisions

Phase 3 uses one shared markdown export rule for built-in skills:

- Default path: `XDG_DATA_HOME/cpho/outputs/<workspace_hash>/<skill>/<problem>.md`.
- `/set out.dir <path>` overrides the root directory; skill-specific subfolders are still used.
- Filenames preserve readable Chinese names and strip path separators/reserved characters.
- Writes are deterministic overwrites through an atomic temp-file replace.

The roadmap text says Solve findings may become controlled tags, but the locked Phase 3 context
chooses free-text discrepancies first. Optional persistence still uses the existing index
`user_tags` layer through `add_problem_tags`, so machine-generated tags remain separate.
