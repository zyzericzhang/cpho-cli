# Phase 3 REPL and Index Decisions

REPL skill commands are explicit built-ins (`/solve`, `/explain`, `/probe`) rather than generic `SkillSpec` auto-registration. The adapter layer still holds shared command glue, but the user-facing flows need skill-specific confirmation and handoff behavior.

Solve writes the accepted `SolveReport` into `SessionState.current_solve_report` for the hot path. Persisting Solve discrepancies to index `user_tags` is opt-in via `--persist-tags`, because discrepancies are not always useful search tags.

Explain warns when no Solve report exists but does not block. When a Solve report is present, the exact in-session report is passed into `run_explain(...)`; Explain candidate tags are confirmed before `add_problem_tags(skill_name="explain")`.

The Explain-to-Probe secondary entry prompt accepts `/probe` or Enter only. This keeps the flow discoverable without making Explain automatically start another interactive loop.

REPL Explain passes OCR problem text when available and passes answer text for text answers, otherwise an answer source path. Full answer OCR remains owned by Solve/indexing instead of being duplicated in the REPL glue.

