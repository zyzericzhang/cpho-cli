# Phase 3 Explain Decisions

Streaming support is intentionally provider-level and prose-only. `provider.stream()` yields visible
markdown chunks for the Explain UI, while structured outputs such as candidate tags are validated
after a complete response. This avoids parsing partial JSON and keeps the existing `complete()`
tool-call behavior unchanged.

Explain tone fan-out is implemented in `core.explain` with one isolated two-stage stream per selected
tone, instead of teaching `SkillRuntime` about fan-out/fan-in. This conflicts slightly with the early
idea that every built-in skill should be a single runtime DAG, but it keeps runtime semantics simple
and matches the requirement that tone fan-out stays outside `SkillRuntime`.

Solve review context is injected as prompt text, not by mutating the official answer. If no Solve
report exists, prompts receive an explicit `无已确认 Solve 审查结果。` context. This prevents Explain
from silently assuming that the original answer has already been verified.

The Explain skill emits candidate index tags only as candidates. They are returned by the service
for later confirmation/persistence in REPL integration rather than being written to the index during
Explain generation.
