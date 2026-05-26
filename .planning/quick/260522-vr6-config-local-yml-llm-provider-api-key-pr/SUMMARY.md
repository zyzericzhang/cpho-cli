---
quick_id: 260522-vr6
slug: config-local-yml-llm-provider-api-key-pr
status: complete
completed: 2026-05-22T15:04:00.000Z
---

# Summary: Default local config and provider profile selection

Implemented default `config.local.yml` loading and provider profile selection.

## Changes

- `load_config(None)` now looks for `config.local.yml` or `config.local.yaml` from the current working directory upward before falling back to defaults.
- Existing `provider.openrouter_api_key` config remains supported.
- Added `active_provider` and `providers.<name>` config profiles, resolved through `resolve_provider_config`.
- Added `--provider/-p` to `cpho solve` and `cpho eval`.
- Updated README and planning context to describe default local config and profile selection.

## Verification

- `uv run pytest -q` passed.
- `uv run ruff check .` passed.
- `uv run mypy .` passed.

Last action: updated docs, planning context, tests, and provider wiring for default local config/profile selection.
