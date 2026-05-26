# Phase 3 Probe Decisions

Probe is implemented as a continuous service loop rather than a revived Quiz/YAML generator. The LLM proposes one next question per turn, the user answers it, and the completed Q+A pair is appended immediately to markdown.

The final Probe markdown is rewritten into `## 问题` followed by `## 解答` so a coach can scan all prompts first and then review corresponding answers. The incremental transcript exists only as a recovery-friendly intermediate format while the session is active.

The `probe.max_rounds` value is a soft limit. At the limit, Probe asks whether to continue before making another model call, so exiting at the limit does not spend tokens on an unanswered question.
