# Golden Index Workspace

Fake-LLM fixture for end-to-end determinism testing. Problem files are intentionally
trivial text (not real physics problems). The fake LLM returns a hardcoded
`TagRefinementOutput` so that tests can verify canonical tags without network calls.
