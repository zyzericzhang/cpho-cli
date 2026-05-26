# solve

## 用途

审查标准答案，找出可能的符号、推导或引用问题，为 explain/probe 提供更可信的上下文。

## 前置条件

- 已有题目文件和答案文件。
- 已配置 provider。
- 推荐先建立 workspace index，方便持久化 discrepancy。

## 用法 / 参数

```bash
uv run cpho solve problem.pdf --answer answer.pdf --auto-confirm
```

REPL:

```text
/show 1
/solve --auto-confirm --persist-tags
```

常用参数：`--answer`、`--provider`、`--output-dir`、`--auto-confirm`、`--persist-tags`。

## 典型输出

- `SolveReport`
- 标答步骤列表
- 每步检查结果
- discrepancy 列表

## 导出文件说明

CLI 默认写入 `output/<problem>-report.json` 和 `output/<problem>-report.md`。REPL 可通过 `/set out.dir <dir>` 改变导出根目录。

## 端到端完整示例

```text
cpho> /search 力学
cpho> /show 1
cpho> /solve --auto-confirm --persist-tags
```

完成后，同一 REPL 会话中的 `/explain` 会读取 `session.current_solve_report`。

