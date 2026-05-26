# Probe

Probe asks one focused question at a time for a physics competition problem. The loop is owned by `cpho_cli.core.probe`: the skill prompt only proposes the next question from the problem, Solve context, previous turns, and the latest user response.

Probe replaces the old Quiz/YAML direction. It does not score answers, generate flashcards, or export Anki/Obsidian data in Phase 3.

