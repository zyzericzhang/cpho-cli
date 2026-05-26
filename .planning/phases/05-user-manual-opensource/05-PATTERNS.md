---
phase: 05-user-manual-opensource
type: patterns
created_at: 2026-05-26
branch: feature/phase5
---

# Phase 5 Patterns

## Docs Style

- Chinese prose.
- Commands in fenced shell blocks.
- Short tables over long paragraphs.
- Put operational details in `docs/user/`, not README.

## Open Source Files

- Keep `CONTRIBUTING.md` short.
- Use standard issue template frontmatter.
- Do not rewrite git history.

## Skill Chapter Template

Each `docs/user/*.md` skill chapter follows:

1. 用途
2. 前置条件
3. 用法 / 参数
4. 典型输出
5. 导出文件说明
6. 端到端完整示例

## Verification

Docs tests should assert files exist and mention the actual command names so future command churn breaks documentation checks.

