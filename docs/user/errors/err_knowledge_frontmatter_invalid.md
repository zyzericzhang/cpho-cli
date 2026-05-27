# err_knowledge_frontmatter_invalid

## 发生了什么

知识文件开头的 YAML frontmatter 不符合规范。

## 常见原因

缺少 `---` 包裹、YAML 语法错误、frontmatter 不是 mapping，或 `canonical_tag_id` 不在 workspace 词表中。

## 修复方法

修复文件开头的 YAML。至少保留 `canonical_tag_id`，并确认该 tag 存在于内置词表或 `.cpho/vocabulary/private.yml`。

