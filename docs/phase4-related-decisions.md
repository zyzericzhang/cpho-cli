# Phase 4 Related Decisions

The related-problems skill is a thin wrapper around the existing `find_related_problems()` API. It does not introduce a new scoring mode in v1; it exports the current weighted score, writes markdown, and stores the latest REPL rows in `SessionState.last_related`.

`last_related` is session-local and explicit. Later compose commands may consume it only when the user passes `--from last-related`; related search itself never creates or mutates composition files.

