# Python 扩展

> **不支持：** YAML 配置式 skill、自然语言生成 skill、pip 安装第三方 skill。

当前扩展方式是最小 Python 路径：复制一个现有 REPL command 或 core service，改成自己的逻辑，然后显式注册 slash command。

## 推荐结构

```text
src/cpho_cli/core/count.py
src/cpho_cli/cli/repl/commands/count.py
```

## 可用 API

- `core/llm.py`：`LLMProvider.complete()` / `stream()`。
- `core/index/api.py`：`get_problem_entry()`、`query_index()`、`add_problem_tags()`、`remove_problem_tags()`、`update_problem_tags()`。
- `cli/repl/commands/__init__.py`：在 `install_builtin_commands()` 中调用模块的 `register(registry)`。

## 最小示例：`/count`

`src/cpho_cli/core/count.py`：

```python
from pathlib import Path

from cpho_cli.core.index.storage import load_index


def count_indexed_problems(workspace: Path) -> int:
    return len(load_index(workspace))
```

`src/cpho_cli/cli/repl/commands/count.py`：

```python
from cpho_cli.cli.repl.commands import Command
from cpho_cli.core.count import count_indexed_problems


async def do_count(session, args):
    print(f"已索引题目数: {count_indexed_problems(session.workspace_path)}")


def register(registry):
    registry["/count"] = Command(
        "/count",
        "统计当前 workspace 的题目数",
        "/count",
        do_count,
        category="技能",
    )
```

最后在 `src/cpho_cli/cli/repl/commands/__init__.py` 导入并注册：

```python
from cpho_cli.cli.repl.commands import count

count.register(registry)
```

## 注意事项

- 保持 core/cli 分离：可测试逻辑放 `core/`，输入输出放 `cli/`。
- 需要写 index 时只用 `core/index/api.py`，不要直接改 JSONL。
- 用户可见错误信息使用中文。

