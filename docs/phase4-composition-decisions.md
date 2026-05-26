# Phase 4 Composition Decisions

Composition files use strict YAML with exactly one mode per slot: `problem_id`, `pass`, or `spec`. The implementation keeps `pass` as the YAML key and maps it to `pass_slot` in Python to avoid using a reserved word in code.

Auto-selection is deterministic: it uses existing index order from `compose_problem_list()` and skips problem ids already used earlier in the same composition. If a slot cannot be filled, the command raises a clear error instead of relaxing filters or silently passing the slot.

