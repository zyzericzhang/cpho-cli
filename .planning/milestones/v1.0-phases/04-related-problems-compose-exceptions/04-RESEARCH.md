---
phase: 04-related-problems-compose-exceptions
type: research
created_at: 2026-05-26
branch: feature/phase4
---

# Phase 4 Research

## Real Workspace Shape

Sampled `/Users/ericzhang/Desktop/物理竞赛资料` before planning. The workspace contains many nested institution/year folders and paired PDF naming patterns such as:

- `力学2试题.pdf` / `力学2解析.pdf`
- `理论5试题.pdf` / `理论5-答案.pdf`
- `复赛模拟一.题目.pdf` / `复赛模拟一.解析.pdf`
- combined files such as `测试3试题及参考答案v2.0.pdf`

Implications:

- Composition must work from indexed `IndexEntry.problem_path`, `answer_path`, `problem_page_range`, and answer page ranges when available, rather than filename guessing at compose time.
- Output should preserve original pages because source PDFs are already formatted as coach-facing handouts.
- Tests should copy representative PDFs into `tmp_path`; never write into the real workspace.

## Existing Code

- `core.index.api.find_related_problems()` already computes tag-overlap related entries and returns `(IndexEntry, score)`.
- `core.index.compose.compose_problem_list()` already filters entries by topic prefix and tag intersection.
- `models.index.IndexEntry` stores `problem_path`, optional `answer_path`, and problem page ranges.
- `models.documents.ProblemEntry` has answer page ranges, but `IndexEntry` currently does not expose answer page ranges.
- `core.workspace._paper_total_pages()` already uses `fitz`, confirming PyMuPDF is available.
- `core.runtime.SkillRuntime` already writes trace records and failure checkpoints, but not a completed-step checkpoint after every successful DAG step.
- REPL commands are explicit modules; Phase 3 added `/solve`, `/explain`, and `/probe` with shared skill command helpers.

## Technical Conclusions

- Related skill should be a thin service around `find_related_problems()` plus markdown export and REPL `last_related`.
- Composition should add a dedicated `models.composition` and `core.composition` rather than overloading `core.index.compose`.
- The first PDF assembly implementation should use `fitz.Document.insert_pdf()` and preserve source pages exactly.
- Because `IndexEntry` lacks `answer_page_range`, answer assembly should use the same page range against `answer_path` when present for v1, and document that exact per-problem answer ranges require a later index model extension.
- Boundary checks should be shared in `core.boundary.ensure_in_workspace()` and used by compose/REPL paths first.
- Runtime success checkpoints can be added without changing handler APIs by extending `_write_checkpoint` calls after successful steps.

## Verification Strategy

- Unit tests seed compact index fixtures rather than scanning real workspace.
- PDF tests generate tiny PDFs with `fitz` in `tmp_path`.
- Related tests assert machine tags remain unchanged and markdown export is deterministic.
- Boundary tests assert path traversal and missing workspace errors are Chinese, explicit, and non-hanging.

