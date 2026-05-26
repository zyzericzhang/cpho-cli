# related

## 用途

基于 index tags 查找当前题目的同类题。

## 前置条件

- 已运行 `cpho index build` 或 REPL `/index`。
- 当前题目存在于 index。

## 用法 / 参数

```text
/search-related
/search-related p1 --top 10 --min-shared 1
```

## 典型输出

表格列出题目 ID、相似度分数、topic、tags 和来源文件。

## 导出文件说明

同时写出 related markdown。REPL 会保存 `session.last_related`，但不会隐式组卷。

## 端到端完整示例

```text
cpho> /show 1
cpho> /search-related --top 5
cpho> /compose auto --from last-related --count 3
```

