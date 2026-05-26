# Phase 3 Verification

## Automated Commands

- `uv run pytest tests/test_skill_outputs.py tests/test_repl_persistence.py tests/test_repl_session.py tests/test_repl_builtin_commands.py -q`
- `uv run pytest tests/test_llm.py -q`
- `uv run pytest tests/test_skill_progress.py tests/test_followup.py tests/test_repl_display.py -q`
- `uv run pytest tests/test_solve.py tests/test_skills.py tests/test_cli.py -q`
- `uv run pytest tests/test_explain.py tests/test_skills.py -q`
- `uv run pytest tests/test_probe.py tests/test_skills.py -q`
- `uv run pytest tests/test_repl_builtin_commands.py tests/test_repl_runtime.py tests/test_index_api.py -q`
- `uv run pytest tests/test_phase03_acceptance.py -q`
- `uv run pytest tests/test_skill_outputs.py tests/test_repl_persistence.py tests/test_repl_session.py tests/test_repl_builtin_commands.py tests/test_llm.py tests/test_skill_progress.py tests/test_followup.py tests/test_repl_display.py tests/test_solve.py tests/test_skills.py tests/test_cli.py tests/test_explain.py tests/test_probe.py tests/test_repl_runtime.py tests/test_index_api.py tests/test_phase03_acceptance.py -q`
  - Result: 86 passed, 5 existing PDF dependency deprecation warnings.
- `uv run pytest -q`
  - Result: 384 passed, 5 existing PDF dependency deprecation warnings.

## Real Workspace Policy

Acceptance coverage reads `/Users/ericzhang/Desktop/物理竞赛资料` only to copy one representative PDF into `tmp_path`. All generated index files, markdown exports, transcripts, and user tag writes happen under the temporary workspace. The test asserts copied paths are not aliases back to the original workspace.

## Seeded Index Policy

Phase 3 acceptance uses a compact seeded `.cpho/index.jsonl` instead of scanning the full real workspace. Skill writeback goes through `add_problem_tags`, so accepted Solve/Explain output is stored in `user_tags` and existing machine tag buckets remain unchanged. Existing index builder tests cover force rebuild preservation of `old.user_tags`.

## Superseded Decisions

- Solve is an official-answer review skill, not a fresh solver. Its findings remain free-text discrepancies, with optional index persistence through `user_tags`.
- Explain tone fan-out runs outside `SkillRuntime`; each selected tone has isolated streamed calls and the service merges markdown afterward.
- Probe replaces the older Quiz/YAML direction. It is a continuous coaching loop with questions-first/answers-second markdown, not a scored quiz exporter.
- Follow-up uses local `provider.complete` message history and optional markdown append. No LangChain or additional chat framework was introduced.
- Rich is used only as a progress display dependency; non-TTY output falls back to plain progress lines.
- REPL skill registration is explicit for `/solve`, `/explain`, and `/probe` because each command has distinct confirmation and handoff behavior.
