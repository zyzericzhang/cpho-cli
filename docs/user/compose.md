# compose

## 用途

用 YAML 编排文件从原始 PDF 裁页拼装题目卷和答案卷。

## 前置条件

- 已建立 index。
- index 条目包含 `problem_path`、`answer_path` 和页码范围。

## 用法 / 参数

```bash
uv run cpho compose new weekly --count 5 --workspace examples
uv run cpho compose build examples/.cpho/compositions/weekly.yml --workspace examples
uv run cpho compose auto --count 5 --topic 力学 --workspace examples
```

REPL:

```text
/compose new weekly --count 5
/compose build .cpho/compositions/weekly.yml
/compose auto --from last-related --count 3
```

## 典型输出

- `<name>-题目.pdf`
- `<name>-答案.pdf`
- PDF outline 中有 `第 N 题` 书签

## 导出文件说明

默认输出到 `.cpho/exports/compose/`。可用 `--output` 覆盖，但路径必须在 workspace 内。

## 端到端完整示例

```text
cpho> /search-related p1 --top 3
cpho> /compose auto --from last-related --count 3
题目卷: .cpho/exports/compose/auto-题目.pdf
答案卷: .cpho/exports/compose/auto-答案.pdf
```

