# index

## 用途

把本地 PDF/图片题库转换为可检索的 `.cpho/index.jsonl`。

## 前置条件

- workspace 是一个本地文件夹。
- 已配置 OCR/LLM provider；默认路径优先 OCR。

## 用法 / 参数

```bash
uv run cpho index build /path/to/workspace --config config.local.yml
```

REPL:

```text
/workspace /path/to/workspace
/index --only-new
/reload-index
```

## 典型输出

索引统计：文件变化数、OCR cache 复用数、tag 生成数、topic 信息。

## 导出文件说明

主要文件：

- `.cpho/index.jsonl`
- `.cpho/ocr/`
- `.cpho/traces/`
- `.cpho/compositions/`

## 端到端完整示例

```text
cpho> /workspace /Users/you/物理竞赛资料
cpho> /index --only-new
cpho> /search 牛顿
cpho> /show 1
```

