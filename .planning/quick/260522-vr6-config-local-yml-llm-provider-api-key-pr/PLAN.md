---
quick_id: 260522-vr6
slug: config-local-yml-llm-provider-api-key-pr
status: in_progress
created: 2026-05-22T14:51:48.075Z
---

# Quick Task: Default local config and provider profile selection

## Goal

Make `config.local.yml` the default config source for CLI runs, while preserving the existing OpenRouter key format and adding a provider profile model so later API providers or multiple API keys can live in the same local file.

## Assumptions

- `config.local.yml` remains local-only and gitignored.
- Existing configs with `provider.openrouter_api_key` must continue to work.
- The first selection interface should be a low-surface CLI option, `--provider <name>`, shared by `solve` and `eval`.
- Only OpenRouter is implemented as a runtime provider today; unknown provider kinds should fail clearly when selected.

## Steps

1. Add tests for default `config.local.yml` loading, provider profile resolution, secret-safe errors, and CLI `--provider` help.
   Verification: focused pytest for config and CLI tests.
2. Extend config models and resolver with `active_provider`, `providers.<name>`, and resolved provider config output.
   Verification: old `resolve_api_key` tests still pass, new profile tests pass.
3. Wire selected provider profile through `solve`, `eval`, and Typer commands.
   Verification: CLI help exposes `--provider`; existing solve/eval tests remain compatible.
4. Update README and GSD planning context so future work uses the new config shape.
   Verification: docs mention default local config and profile selection without real keys.
