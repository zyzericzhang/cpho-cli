# Golden Tests

Golden tests are manual-first regression cases. Each case lives in its own folder with:

- `spec.yml` for machine-readable criteria
- `EXPECTATION.md` for human-readable expectations
- local problem and answer files supplied by the user

Start with 3-5 real cases, then grow toward 20-30 regression cases as failures are found. Human-defined criteria are authoritative. Any future LLM judge is advisory only.

