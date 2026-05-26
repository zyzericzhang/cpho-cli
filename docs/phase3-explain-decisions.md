# Phase 3 Explain Decisions

Streaming support is intentionally provider-level and prose-only. `provider.stream()` yields visible
markdown chunks for the Explain UI, while structured outputs such as candidate tags are validated
after a complete response. This avoids parsing partial JSON and keeps the existing `complete()`
tool-call behavior unchanged.
