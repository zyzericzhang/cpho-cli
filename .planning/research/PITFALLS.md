# Domain Pitfalls

**Domain:** Physics Olympiad AI Analysis CLI Tool
**Researched:** 2026-05-20
**Confidence:** HIGH (multiple verified sources across all domains)

---

## Critical Pitfalls

Mistakes that cause rewrites or render the product unusable.

### Pitfall 1: Hallucinated Physics Reasoning in Analysis Output

**What goes wrong:** The LLM generates plausible-sounding but factually incorrect derivations, invents physical constants, or "agrees" with incorrect assumptions embedded in the problem statement. In physics competition problems, a single hallucinated step corrupts every downstream derivation.

**Why it happens:** LLMs are trained on internet text, not physics problem-solving. They are biased toward "agreeability" — they confirm user premises rather than correcting errors. Research shows: (a) models frequently produce minor inaccuracies even on straightforward physics problems; (b) models fine-tuned only on textbook content perform worse than those trained on mistake-correction dialogues; (c) the "agreeability" problem is especially dangerous in tutoring contexts.

**Consequences:** Users (physics teachers) lose trust after seeing even one hallucinated derivation. The core value proposition — "quality of analysis output" — collapses. Unlike a chat app where users can tolerate occasional mistakes, physics teachers are domain experts who will detect errors immediately.

**Prevention:**
1. **Ground every analysis step in the provided standard answer** — the answer is the anchor truth. The DAG pipeline must inject the standard answer into every LLM call's context, not just the problem text.
2. **Multi-pass verification built into the DAG** — after generating a derivation, run a separate verification pass that asks: "Does step N logically follow from step N-1 and the known answer? If not, flag for human review."
3. **Anti-agreeability prompting** — explicitly instruct the model: "If the problem statement or the student's reasoning contains a physics error, you MUST identify and correct it before proceeding."
4. **Regression test suite of 20-30 physics problems** with known correct derivations — every prompt change must pass these before deployment.

**Detection:** User reports of wrong derivations; the verification pass consistently flags the same problem types; output that contradicts the standard answer.

**Phase to address:** Phase 1 (core analysis pipeline). This must be solved before any skill system work — it is the foundation.

---

### Pitfall 2: Context Window Pressure Causing Skipped Reasoning Steps

**What goes wrong:** When analyzing long physics competition problems (which can span multiple pages with sub-questions Q1 through Q5), stuffing the entire problem + standard answer + analysis instructions into a single context window causes the model to skip intermediate derivation steps. The model provides correct-looking final answers but omits the "why" between steps — which is exactly what the product exists to provide.

**Why it happens:** Research on LLM context windows consistently shows: (a) "lost in the middle" — models attend poorly to content in the middle of long contexts; (b) proactive interference — earlier content disrupts processing of later content; (c) as context fills, hallucination risk increases and the model takes reasoning shortcuts. Physical competition problems naturally create this condition: Q3's derivation depends on Q2's result, which depends on Q1, but a single long prompt buries these dependencies.

**Consequences:** The product's core differentiator ("why this step leads to that step") is exactly what gets dropped. Users get a shallow summary instead of the deep walkthrough they need.

**Prevention:**
1. **DAG-based step decomposition is mandatory, not optional** — split each sub-question into its own pipeline node. Each node gets only: the problem's base context + the specific sub-question + relevant prior results + the standard answer. This is already in the architecture, but the pitfall is not doing it aggressively enough — every sub-question, no matter how short, should be its own node.
2. **Pruned context per node** — never pass the full problem text to every node. Pass only what that node needs: the base physical setup (compressed), the specific sub-question, and the chain of prior results (just the conclusions, not the full derivations).
3. **Intermediate result compression** — between DAG nodes, compress prior step outputs into structured summaries (final equations, numeric results, key assumptions) rather than passing raw LLM output forward.

**Detection:** Outputs that say "by similar reasoning as above" without explaining the reasoning; derivations that skip from Q1's result to Q3's conclusion without showing Q2's work; token usage metrics showing near-limit context utilization.

**Phase to address:** Phase 1 (DAG pipeline design). This is the architectural foundation — getting it wrong means rewriting the entire pipeline structure.

---

### Pitfall 3: Over-Engineering the Skill/Plugin System Before Core Quality Is Validated

**What goes wrong:** Building a sophisticated three-layer skill system (pure prompt / YAML / Python) with full developer documentation, Skill Creator, and plugin marketplace infrastructure before validating that the core analysis pipeline produces high-quality output on real physics problems.

**Why it happens:** Plugin systems are fun to build. They feel like "real engineering." Core analysis quality requires tedious prompt iteration on ugly edge cases. The temptation is to build the extensibility framework first and assume the analysis quality will come later — but if the core analysis isn't good, no amount of plugin infrastructure matters.

**Consequences:** Research on plugin system failures consistently shows: (a) extension points designed before real usage patterns are known end up either too generic (serves nothing well) or too specific (breaks on every new use case); (b) abstractions that hide mechanics create debugging nightmares; (c) the worst outcome is a beautifully architected plugin system wrapped around a mediocre analysis engine. Users don't care about plugin architecture — they care about whether the analysis is correct and insightful.

**Prevention:**
1. **Phase 1: zero plugin system.** Hardcode 1-2 analysis modes directly in the core. Validate analysis quality on 50+ real physics problems first.
2. **Phase 2: extract plugin boundaries only where actual variation exists.** After Phase 1, you'll know which parts users actually want to customize (prompt wording, model choice, output format) vs. which parts are invariant (OCR pipeline, DAG structure, answer grounding).
3. **Start with the simplest extensibility tier** (pure prompt override via YAML) and only add the Python scripting tier when real users hit the YAML tier's limits.
4. **The Skill Creator is a Phase 3 feature at earliest.** Building a meta-tool that generates skills requires a stable, well-understood skill architecture — which doesn't exist until users have written skills manually.

**Detection:** More lines of plugin infrastructure code than analysis pipeline code; skill system has features no user has requested; Skill Creator built before 3+ real users have written skills by hand.

**Phase to address:** Architecture decision now (limit Phase 1 scope), implementation in Phase 2.

---

### Pitfall 4: OCR Accuracy as a Silent Quality Ceiling

**What goes wrong:** Chinese + LaTeX mixed content OCR introduces errors that silently corrupt the LLM's input. The LLM then produces analysis based on misrecognized formulas — but the output looks plausible, so nobody catches the error. The product appears to work while producing subtly wrong analysis.

**Why it happens:** Research on Chinese + math mixed-content OCR reveals: (a) 67% formula rendering error rate with naive pipelines; (b) LaTeX delimiters ($...$) lost, causing formulas to be treated as Chinese text; (c) subscript/superscript confusion (H2O vs H2O); (d) multi-line equation misalignment; (e) Transformer-based OCR models "guess" tokens from language-model priors rather than strictly reading the image, causing systematic errors on non-standard physics notation. The errors are often subtle — a missing subscript or a misrecognized Greek letter — but in physics, one wrong symbol invalidates an entire derivation.

**Consequences:** Garbage-in-garbage-out. The LLM might produce a coherent-looking analysis that is completely wrong because it was given corrupted input. Users blame the AI, not the OCR, and lose trust in the entire tool.

**Prevention:**
1. **OCR quality validation step in the DAG** — after OCR, run a dedicated verification pass: "Here is the OCR output. Here is the original image. Identify any discrepancies in formulas, subscripts, Greek letters, and mathematical notation."
2. **Human-in-the-loop for OCR confidence below threshold** — if the OCR confidence score for formula regions is below a threshold, flag the problem and require manual review before analysis proceeds.
3. **Abstract OCR interface from day one** — the architecture already calls for this, but the pitfall is implementing only one backend and coupling to it. Support at least two OCR backends (e.g., Mathpix for quality, a local open-source option for privacy) so users can trade off accuracy vs. local-only constraints.
4. **Build a test corpus of 10-20 representative physics problems** (scanned PDFs, photos, mixed Chinese/LaTeX) and measure OCR accuracy before claiming the pipeline works.

**Detection:** Random sampling of OCR output vs. original images shows formula errors; LLM output references variable names that don't appear in the problem; users report "the analysis doesn't match the problem."

**Phase to address:** Phase 1 (OCR is the pipeline entry point — everything downstream depends on it).

---

### Pitfall 5: File-Based Index Staleness and Corruption

**What goes wrong:** The tag index (stored as JSON/JSONL files in the problem folder) drifts out of sync with the actual files. Tags from frontmatter edits aren't detected. Files deleted outside the tool leave ghost entries. The index becomes untrustworthy, and users stop relying on tag-based retrieval — defeating the entire "folder as knowledge base" model.

**Why it happens:** Research on file-based indexing systems consistently surfaces these failure modes: (a) incremental re-index skips files already in the database, checking only existence not modification time or content hash; (b) tag format incompatibility (e.g., comma-separated vs. YAML list format) causes silent parse failures; (c) large indexes hit practical limits (JSON files >300MB crash on parse, in-memory indexes exhaust RAM); (d) duplicate indexing across overlapping watch directories pollutes results.

**Consequences:** Users search by tag "rigid body rotation" and miss problems that should match — or get results for deleted files. The knowledge graph connections that are the product's core value become unreliable.

**Prevention:**
1. **Content-hash-based change detection, not existence checks** — every index entry stores a hash of the source file. Re-index when hash changes, not just when file is "new."
2. **Index as a derived artifact that can be fully regenerated** — the index is always rebuildable from the source files. If corruption is detected, `cpho index --rebuild` fixes it.
3. **SQLite for the index, not raw JSON** — for any vault beyond ~100 problems, JSON files become a scalability bottleneck (parse time, memory, atomic writes). SQLite handles concurrent reads, provides atomic transactions, and scales to 10K+ problems without issue. Reserve JSON/JSONL for human-readable exports.
4. **Validate index integrity on every read** — check that referenced files still exist, tags are in valid format, and cross-references point to real entries. Surface corruption immediately, don't silently return partial results.
5. **Start simple** — the initial index should store: filename, content hash, tags array, last-indexed timestamp. Don't pre-design a complex schema for features that don't exist yet.

**Detection:** Tag search returns problems the user knows are deleted; index file grows unboundedly; `cpho index --stats` shows file count mismatch with actual directory contents.

**Phase to address:** Phase 1 (index is needed from the start for tag-based retrieval).

---

## Moderate Pitfalls

### Pitfall 6: OpenRouter Reliability Without Local Guardrails

**What goes wrong:** Reliance on OpenRouter's automatic failover without implementing local retry, timeout, and circuit-breaker logic. Requests hang, fail silently, or route to providers with incompatible capabilities (e.g., a 33K context window when the problem requires 128K).

**Why it happens:** OpenRouter abstracts away provider selection, but research shows: (a) upstream 403 errors cascade without retry; (b) "skip instead of wait" rate limiting causes 99.5% failure rates; (c) provider cooldown state can silently fail through to expensive fallback models; (d) different providers serving the same model have wildly different context windows.

**Consequences:** Non-technical physics teachers see inscrutable API errors and abandon the tool. Even technical users lose hours of analysis work to transient failures.

**Prevention:**
1. **Always set explicit HTTP timeouts** (30s default) on every OpenRouter call.
2. **Implement exponential backoff with jitter** — check `Retry-After` header, then 5s -> 10s -> 20s -> 40s with random jitter, max 3 retries.
3. **Pin specific providers for production use** — use OpenRouter's `:nitro` or provider-specific routing. Don't rely on automatic load balancing for consistent quality.
4. **Implement a local circuit breaker** — after 3 consecutive failures, stop attempting and surface a clear error message with recovery instructions.
5. **Surface model/provider info in verbose output** — users should see which model and provider handled their request, so they can diagnose quality issues.

**Detection:** Intermittent timeouts with no clear error message; analysis that "completes" but is from a different model than expected; users reporting "it worked yesterday but not today."

**Phase to address:** Phase 1 (LLM calls are fundamental to every pipeline).

---

### Pitfall 7: Prompt Rot Across Model Versions

**What goes wrong:** Prompts carefully tuned for one model version produce degraded output when the underlying model is updated (by OpenRouter's provider routing or Anthropic/OpenAI model updates). The degradation is silent — output still looks plausible but quality drops. No one notices until a teacher compares old output to new output and finds the new version worse.

**Why it happens:** LLM model weights change frequently. A prompt optimized for Claude 3.5 Sonnet may produce different (often worse) results on Claude 4 Sonnet. Without regression testing, prompt degradation goes undetected. Research on prompt management shows "silent degradation" is the #1 preventable AI production incident.

**Consequences:** Analysis quality regresses over time. Users who built workflows around consistent output quality find their results deteriorating. Debugging is painful because the cause (model update) is invisible to the user.

**Prevention:**
1. **Pin model versions, not model families** — use `anthropic/claude-sonnet-4-20250514` not `anthropic/claude-sonnet-4`. When you want to upgrade, do it deliberately and test.
2. **Golden test suite of 20-30 problems with expected outputs** — run before every prompt change and before every model version upgrade. Compare outputs using both automated metrics (ROUGE-L, BLEU for formula accuracy) and manual spot-checks.
3. **Prompt versioning in YAML with metadata** — every prompt file records: which model version it was tuned for, when it was last validated, and what the golden test suite results were.
4. **Git-track all prompts** — prompts live in `prompts/` as versioned YAML files. Every change is a commit with rationale.

**Detection:** Golden test suite scores drop after model upgrade; user reports of "the analysis used to be better"; same problem produces noticeably different derivations across runs.

**Phase to address:** Phase 1 (prompt management infrastructure), ongoing after.

---

### Pitfall 8: The "Obsidian Envy" Trap — Building a General Knowledge Manager Instead of a Physics Tool

**What goes wrong:** The project scope creeps toward becoming a general-purpose knowledge management tool (like Obsidian but with AI). Features like generic note linking, graph visualization, arbitrary file type support, and general-purpose search get prioritized over physics-specific analysis quality.

**Why it happens:** The "folder as knowledge base" metaphor naturally invites Obsidian comparisons. Tag indexing, cross-referencing, and knowledge graphs are Obsidian's domain. It's easy to start building Obsidian features instead of physics features. The project spec already calls this out ("物理竞赛领域的 Obsidian + AI agent") — the pitfall is taking the "Obsidian" part too literally and building a note-taking app that happens to have a physics plugin, rather than a physics analysis tool that happens to index files.

**Consequences:** The tool becomes mediocre at both knowledge management (Obsidian is better) and physics analysis (the core value proposition is diluted). Physics teachers don't want another note-taking app — they want deep, accurate physics problem analysis.

**Prevention:**
1. **Tag indexing exists solely to serve analysis retrieval** — tags feed into "find related problems," "compare similar models," and "assemble exam papers." If a tag/index feature doesn't directly improve analysis quality or retrieval for analysis, it's out of scope.
2. **No graph visualization in v1** — the CLI has no visual output. Graph visualization is a GUI feature and belongs in a future TUI/Web phase.
3. **No generic Markdown editing** — the tool reads problem files but does not edit them (except for writing index/tag metadata). It is not a note editor.
4. **Revisit the project description** — replace "物理竞赛领域的 Obsidian + AI agent" with something that emphasizes the analysis tool identity. The Obsidian comparison is a useful shorthand but a dangerous north star.

**Detection:** Sprint planning includes "add backlinks view," "support for non-physics files," "graph visualization prototype"; the tag system has more features than the analysis pipeline.

**Phase to address:** Architecture decision now, scope discipline in every phase.

---

### Pitfall 9: Python Script Skill Tier Security and Footgun Risk

**What goes wrong:** The Python scripting tier of the skill system allows users to install skills that execute arbitrary Python code. A malicious or buggy skill can read the user's API keys from environment variables, delete files in the problem folder, or exfiltrate problem content. Even non-malicious skills can corrupt the index or produce broken analysis output.

**Why it happens:** The three-tier skill system (prompt / YAML / Python) is designed for progressive power, but Python scripts have full process privileges. Research on plugin systems shows that security is consistently an afterthought — "we'll add sandboxing later" — and later never comes.

**Consequences:** A single incident of a skill stealing API keys or deleting problem files destroys trust in the entire ecosystem. Physics teachers will not use a tool that can execute arbitrary third-party code.

**Prevention:**
1. **Python tier is gated behind explicit user opt-in** — the CLI warns: "This skill contains executable Python code. Running untrusted skills can compromise your system. Continue? [y/N]" on first run.
2. **Document a minimal sandbox** — restrict filesystem access to the problem folder and a skill-specific data directory. Block network access from skill scripts (LLM calls go through the core, not the skill directly).
3. **Skills ship as inspected source, not opaque packages** — users can read the Python code before running it. No `pip install` from arbitrary URLs inside skills.
4. **The core API exposed to skills is read-only by default** — skills read problem data and produce output; they don't modify the index or delete files unless the user explicitly passes a `--write` flag.
5. **Start without the Python tier** — launch with only the prompt and YAML tiers. Add Python scripting only after real users have demonstrated they need it and the security model is validated.

**Detection:** Skill distribution channels emerge with no review process; users report "my API key was used without my knowledge"; skill installation is a one-liner with no security warning.

**Phase to address:** Phase 2 (Skill system design), potentially deferred to Phase 3.

---

### Pitfall 10: Assuming Teachers Will Tolerate CLI Complexity

**What goes wrong:** The project targets physics competition teachers — domain experts who may have zero command-line experience. The assumption that "they can handle it because they're technical in their domain" is false. A CLI tool that requires memorizing flags, understanding JSON output, or debugging Python tracebacks will be abandoned after the first attempt.

**Why it happens:** The architecture decisions doc states "初期不纠结输出格式的美观程度" (don't worry about output formatting in early stage) and "README 写清楚命令行用法即可" (just write clear README). This is correct for Phase 1 with developer users, but the scope says the target users are physics teachers — and there's a tension between "early adopter developers" and "physics teachers" that needs explicit management.

**Consequences:** The tool is built for the wrong early users. Developers don't have physics problem corpora. Physics teachers can't use a raw CLI. Neither group validates the core value proposition.

**Prevention:**
1. **Phase 1 users are developers and technically-inclined coaches who can tolerate CLI.** Do not pitch this to general physics teachers until after Phase 2 or 3.
2. **Invest in CLI UX early, just not GUI** — clear error messages in Chinese, sensible defaults (zero-config for common workflows), `--help` output that explains concepts not just flags, colored output for scannability.
3. **One command to do the common thing** — `cpho analyze ./problem1.pdf` should run the default analysis pipeline with sensible defaults. No configuration required for the happy path.
4. **Error messages must be in Chinese** — the target users think in Chinese. An English stack trace is useless to them. Every error message, help text, and output label must be in Chinese (or bilingual).
5. **Ship with a tutorial, not just a README** — a walkthrough that takes a teacher from "I have a folder of PDFs" to "I have tagged, analyzed problems" in 5 minutes.

**Detection:** Early user feedback says "I couldn't figure out how to start"; GitHub issues are all about installation and basic usage, not about analysis quality; users ask for a GUI in the first week.

**Phase to address:** Phase 1 (CLI design), Phase 3+ (TUI/GUI consideration).

---

## Minor Pitfalls

### Pitfall 11: The "Reference Answer" Not Being Authoritative Enough

**What goes wrong:** The DAG grounds analysis in the provided standard answer, but for some problems the "standard answer" is itself incomplete (just the final numeric answer, no derivation). The grounding strategy fails silently — the LLM has nothing to verify against.

**Prevention:** Detect answer completeness during input validation. If the answer file is just a numeric result (<50 chars), warn the user that analysis quality will be reduced. For Phase 1, require answers to include at least a sketch of the derivation.

**Phase to address:** Phase 1 (input validation).

---

### Pitfall 12: PDF Handling — Assuming All PDFs Are Created Equal

**What goes wrong:** Physics problem PDFs come in three forms: (a) digitally-born PDFs with selectable text and embedded fonts, (b) scanned image PDFs where each page is a bitmap, (c) mixed PDFs with some text pages and some scanned pages. Treating them uniformly produces garbage output for types (b) and (c).

**Prevention:** Auto-detect PDF type on load. Route digitally-born PDFs to text extraction; route image PDFs to OCR. Surface the detection result to the user so they know what pipeline was used.

**Phase to address:** Phase 1 (file ingestion).

---

### Pitfall 13: Tag Taxonomy Drift

**What goes wrong:** The tags used to classify problems ("物理模型", "启发点", "难点", "数学技巧") are generated by the LLM with no controlled vocabulary. Over time, the same physical model gets tagged as "刚体转动", "rigid body rotation", "刚体旋转" — creating three separate tag islands that should be one.

**Prevention:** Maintain a curated tag vocabulary in a YAML file. The LLM maps its analysis to the controlled vocabulary, not free-text tags. Allow users to customize the vocabulary, but always normalize against it.

**Phase to address:** Phase 1 (tagging system design).

---

## Phase-Specific Warnings

| Phase | Likely Pitfall | Mitigation |
|-------|---------------|------------|
| Phase 1: Core Pipeline | Pitfall #1 (hallucination) + #2 (context dilution) + #4 (OCR ceiling) | Start with 10-problem golden test set. Run every pipeline change against it. Do not ship Phase 1 until derivation quality is verified by a physics domain expert. |
| Phase 1: Indexing | Pitfall #5 (index staleness) + #13 (tag drift) | Use SQLite with content-hash change detection. Define controlled tag vocabulary in YAML before first LLM tag generation. |
| Phase 2: Skill System | Pitfall #3 (over-engineering) + #9 (Python security) | Launch with prompt and YAML tiers only. Gather real usage data before designing Python tier. |
| Phase 3: Built-in Skills | Pitfall #7 (prompt rot) + #8 (scope creep) | Golden test suite expanded to 30+ problems. Every new skill includes regression tests. |
| Phase 4: Distribution | Pitfall #10 (CLI complexity) | Invest in Chinese-language error messages, tutorials, and zero-config defaults before wider distribution. |

---

## Dependency Chain of Pitfalls

```
Pitfall #4 (OCR errors)
    └── Pitfall #1 (hallucinated analysis) ← fed corrupted input
            └── Pitfall #7 (prompt rot) ← can't tell if it's the OCR or the prompt
                    └── Pitfall #10 (teacher abandons tool) ← lost trust

Pitfall #5 (index corruption)
    └── Pitfall #8 (build index features instead of fixing corruption)
            └── Pitfall #3 (over-engineered plugin system around broken index)
```

---

## Sources

- Nikolic et al. (2026) — "Generative AI 24x7 Tutor: Simulating ChatGPT/Wolfram GPT/Tutor Me GPT on Engineering and Math Content" — verified accuracy failures in LLM tutoring
- Chevalier, Mizera & Annala (2024, IAS/ICML) — "Can AI Teach Science?" — agreeability problem, synthetic mistake-correction training
- Mok et al. (2024, UCL) — LLM grading of undergraduate physics solutions — mathematical errors and hallucination prevalence
- Syal et al. (2026, arXiv:2605.04131) — "Multimodal Interference Effect" — 96% text-only vs. significant drop on image-based physics problems
- arXiv:2603.04474 — Error cascades in multi-agent DAGs; genealogy-graph defense (0.32 -> 0.89 success rate)
- justinchuby/flightdeck#64 — DAG state machine limitations, stale state, race conditions in agent orchestration
- bug-ops/zeph#1494 — Silent failure: RunInline without tool definitions produces text-output-only hallucinations
- allan-mobley-jr/forge#146 — Deterministic bash scripts vs. LLM-driven orchestration
- Adam Bien — "Pros and Cons of Modularization" — extension point design difficulty
- Tiki CMS — "Coping with Complexity" — plugin ecosystem combinatorial explosion
- arxiv:2602.17018 — Obsidian plugin ecosystem analysis, 6 functional clusters
- OpenRouter production issues: ktenman/portfolio#1040 (99.5% rate-limit failure), openclaw/openclaw#1405 (rate limit failover)
- Prompt management: Microsoft GenAIOps training, Pipeline Prompt System (hexdocs), production YAML prompt patterns
- Chinese+LaTeX OCR: MinerU delimiter fixes, dual-stream architecture papers, Mathpix comparative evaluations
- Obsidian indexing: copilot partition overflow, IndexedDB caps, frontmatter format incompatibility issues
