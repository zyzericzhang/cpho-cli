# Retrospective

## Milestone: v1.0 MVP

**Shipped:** 2026-05-27  
**Phases:** 8 | **Plans:** 51  

### What Was Built

- Core OCR+DAG pipeline with OpenRouter + multimodal support
- JSONL tag indexing with controlled vocabulary and incremental updates
- Multi-problem paper splitting (PaperFile/ProblemEntry)
- TUI REPL with slash command registry (prompt_toolkit)
- Index read/write API with tag provenance separation
- Explain (multi-tone + sections + index writeback), Probe (active questioning), Solve (answer review + tag provenance)
- Related problems search + PDF composition (image stitching)
- Boundary exception handling throughout
- README, docs/user/, Python extension guide

### What Worked

- **Decimal phase insertions** — 02.1/02.2/02.3 let urgent work land without breaking the integer phase sequence; numbering stayed intuitive
- **Provenance model** — separating LLM-generated tags from skill-written tags early (Phase 02.3) avoided major refactors later in Phase 3
- **Core/shell separation** — `core/` pure library with no UI dependencies made Phase 3-5 skill additions friction-free
- **Acceptance test pattern** — each phase ended with a `test_phaseXX_acceptance.py` that covered the four success criteria; kept scope honest

### What Was Inefficient

- Requirements traceability not updated in sync with phase execution — required bulk catch-up at milestone close; future milestones should check off reqs per phase
- SKILL-EXPLAIN-NEW designed around Tone selection, then superseded in next planning round — a design discussion round before Phase 3 execution would have caught this
- CORE-05 (golden test set) was deferred from the start but never resolved — it's still open at v1.0 close

### Patterns Established

- `docs/new-understanding-YYYY-MM-DD.md` as the trigger for roadmap evolution between milestones
- Phase decimal numbering for urgent insertions
- Two-level hashing (file hash + semantic hash) for incremental index invalidation
- All real-workspace reads are sample-only; acceptance tests always write to `tmp_path`

### Key Lessons

1. Design the "supersedable" surface first — Explain Tone was designed before the user had refined the mental model; a lighter sketch/spike would have validated the right direction
2. Requirements traceability rows need updating per phase, not at milestone close
3. CORE-05 needs a real fixture set — structure tests pass but quality regression requires actual physics problems
4. The `new-understanding` doc format worked well: 三分类（确定设计 / 大致思路 / 公开提问）prevents half-baked features sneaking into phases

### Cost Observations

- Model: Claude Sonnet 4.6 (switched mid-session)
- Sessions: multiple (exact count not tracked)
- Notable: 8 days end-to-end for 51 plans is fast; velocity enabled by clear phase success criteria and acceptance test discipline

---

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Phases | 8 |
| Plans | 51 |
| Timeline | 8 days |
| Python LOC | ~17,458 |
| Tests passing | 415 |
| Deferred items | 2 |
