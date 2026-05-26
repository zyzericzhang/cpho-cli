# Phase 4 Compose CLI Decisions

The old top-level `cpho compose --topic/--tags` filter command is superseded by a command group: `compose new`, `compose build`, and `compose auto`. This is a deliberate compatibility break because Phase 4 composition now creates durable YAML files and PDFs, not just a printed candidate list.

Relative composition and output paths are resolved under the workspace before boundary checks. Absolute paths are still allowed only when they resolve inside the workspace.

REPL `/compose auto --from last-related` consumes `SessionState.last_related` only when explicitly requested. The related search result is never injected implicitly.

