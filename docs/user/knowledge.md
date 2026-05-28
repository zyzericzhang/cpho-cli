# knowledge

## 用途

维护本地私有知识文件，并按题目 tag 查找可供后续 skill 使用的知识总结。

## 前置条件

- workspace 已有 `.cpho/vocabulary/` 或内置词表中的 canonical tag。
- 要发布的知识文件必须包含 `canonical_tag_id`。
- Phase 6 只交付私有知识库；社区同步在 Phase 8 完成后再使用。

## 用法 / 参数

生成草稿：

```bash
uv run cpho knowledge normalize /path/to/note.md --workspace /path/to/workspace --canonical-tag-id newton_second_law --dry-run
```

发布审核后的草稿：

```bash
uv run cpho knowledge publish .cpho/knowledge/drafts/20260527000000-note.md --workspace /path/to/workspace
```

查找题目对应知识：

```bash
uv run cpho knowledge find <problem_id> --workspace /path/to/workspace
```

## 典型输出

- `草稿: <workspace>/.cpho/knowledge/drafts/...md`
- `已发布: <workspace>/.cpho/knowledge/files/published/...md`
- `private <canonical_tag_id> (exact): <path>`

## 导出文件说明

主要文件：

- `.cpho/knowledge/drafts/` — 生成后等待用户审核的草稿。
- `.cpho/knowledge/files/published/` — 已发布、可被 `KnowledgeResolver` 读取的私有知识文件。

知识 frontmatter 至少包含：

```yaml
---
canonical_tag_id: newton_second_law
standardized: true
last_normalized_hash: ...
last_user_edit_hash: ...
---
```

## 端到端完整示例

```text
cpho> cpho knowledge normalize ./notes/牛顿第二定律.md --workspace /Users/you/物理竞赛资料 --canonical-tag-id newton_second_law --dry-run
cpho> # 手工审核并修改 drafts 里的 markdown
cpho> cpho knowledge publish .cpho/knowledge/drafts/20260527000000-牛顿第二定律.md --workspace /Users/you/物理竞赛资料
cpho> cpho knowledge find abc123:01 --workspace /Users/you/物理竞赛资料
```
