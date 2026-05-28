---
phase: 07-explain-v2
status: complete
created: 2026-05-27
workflow: gsd-plan-phase --research
---

# Phase 7 Research: Explain v2 + Model Panel + Input Routing

## RESEARCH COMPLETE

## Objective

Research how to implement Phase 7 after Phase 6:

- EXPLAIN-V2-01 through EXPLAIN-V2-04
- MODEL-PANEL-01 through MODEL-PANEL-04
- INPUT-01 through INPUT-03

## Existing Code Findings

- `core/explain.py` is still tone-based: teacher/dense/brief, two streamed stages per tone, plus candidate tag extraction.
- `models/explain.py` exposes `ExplainTone`, `ToneExplainOutput`, and `ExplainStreamChunk(tone=...)`; these should be hard-cut.
- REPL `/explain` currently accepts `--tone` and then asks whether to enter probe mode.
- `SkillSpec.describe()` from Phase 6 gives enough metadata for a first model panel.
- `core/llm.py` already calls OpenRouter `/models` for capability lookup; Phase 7 can extend the same endpoint into a cached model list service.
- `core/multimodal.py` supports PDF `file` blocks and image blocks, but current skill handlers only attach `problem_file` and `answer_file` opportunistically.
- `SessionState` already carries `model_capabilities`; this can be used for REPL fallback messaging.

## Implementation Strategy

1. Add a lightweight model catalog service:
   - Fetch OpenRouter `/models` live.
   - Cache to `~/.cache/cpho/models/openrouter.json` with default TTL 1h.
   - Bundle a small fallback JSON in the package for first-offline use.
   - Expose `refresh_model_catalog(..., force=True)` for `/model refresh`.

2. Add skill model configuration:
   - Workspace path: `.cpho/skills/<skill_id>.yml`
   - User path: `~/.config/cpho/skills/<skill_id>.yml`
   - Shape: `steps.<step_id>.model`.
   - Resolution order: workspace > user > `SkillStep.default_model` > provider default/current model.

3. Add REPL commands:
   - `/skill panel <name>` prints pipeline steps, prompt paths, current model, and dependencies.
   - `/skill set-model <name> <step_id> <model>` persists a workspace override.
   - `/model refresh` refreshes provider model list but never blocks REPL startup.

4. Replace Explain Tone with Explain v2 panels:
   - Panels: `approach`, `answer_replacement`, `alternative_methods`.
   - Default: approach + answer_replacement.
   - Markdown contains only selected panels.
   - First step queries `KnowledgeResolver`.
   - Prompt includes knowledge references with source labels.
   - Output includes provenance with `input_modality_used`.

5. Add input routing helper:
   - Index remains OCR/text.
   - Explain can use original PDF/image when model capabilities allow.
   - Fallback chain: PDF file -> page images (deferred if needed) -> OCR text.
   - Phase 7 should at least record and warn when falling back to OCR text.

## Validation Architecture

Targeted tests:

- Model catalog fetch/cache/fallback.
- Skill config persistence and model resolution.
- `/skill panel`, `/skill set-model`, `/model refresh`.
- Explain v2 markdown, selected panel omission, knowledge citation, candidate tag extraction.
- Explain v2 removes `--tone` from REPL parser and rejects old usage.
- Provenance records `input_modality_used`.
- Phase 7 acceptance over tiny workspace: indexed problem + published knowledge + explain output file.

Full verification:

- `uv run pytest tests/test_models_catalog.py tests/test_skill_config.py tests/test_repl_model_panel.py tests/test_explain.py tests/test_phase07_acceptance.py -q`
- `uv run pytest -q`
- `uv run ruff check .`

