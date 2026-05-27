# Milestones

## v1.0 MVP — SHIPPED 2026-05-27

**Phases:** 1, 2, 02.1, 02.2, 02.3, 3, 4, 5  
**Plans:** 51  
**Timeline:** 2026-05-19 → 2026-05-27 (8 days)  
**LOC:** ~17,458 Python | 415 tests passing  

### Delivered

Full physics competition CLI from raw PDFs to AI-driven skill analysis: paper splitting, tag indexing, TUI REPL, and core skills (Explain, Solve, Probe, Related, Compose).

### Key Accomplishments

1. **Core OCR+DAG pipeline** — `cpho solve` with RapidOCR + OpenRouter, multimodal image/PDF support via `--vision`
2. **JSONL tag indexing** — Controlled vocabulary (42 canonical tags), three-tier content hashing, incremental updates, Python API
3. **Paper splitting** — PaperFile/ProblemEntry model; rule-first + LLM fallback splitter handles real-world multi-problem exam PDFs
4. **TUI REPL** — prompt_toolkit REPL with slash command registry; /search /show; new skills register in one step
5. **Index read/write API** — Tag provenance model; LLM tags vs skill-written tags stored separately; `cpho index --force` preserves skill tags
6. **Explain + Probe + Solve skills** — Multi-tone explain with section layout and index writeback; active questioning to markdown; answer review with tag provenance
7. **Related + Compose skills** — Similarity-based related problems; PDF composition from orchestration YAML (image stitching, no LaTeX re-render); boundary exception handling
8. **Open-source packaging** — README with asciinema, docs/user/ per-skill, Python extension guide

### Known Gaps at Close

- CORE-05: Real golden test set (20-30 problems) never populated — deferred to v1.1
- SKILL-EXPLAIN-NEW (Tone design): superseded by v1.1 板块 selection design (docs/new-understanding-2026-05-27.md)

### Archive

- Roadmap: `.planning/milestones/v1.0-ROADMAP.md`
- Requirements: `.planning/milestones/v1.0-REQUIREMENTS.md`
