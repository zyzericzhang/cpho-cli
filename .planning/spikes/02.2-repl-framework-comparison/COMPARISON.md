# Spike: cmd2 vs prompt_toolkit 自建轻量 REPL — 对比分析

**Date:** 2026-05-24
**Phase:** 02.2 TUI REPL 骨架
**Context:** Phase 02.2 现有 PLAN 全部基于 cmd2。用户倾向 prompt_toolkit 自建轻量框架，希望做一次分析性对比后再拍板。

---

## 1. 一句话结论

**用 prompt_toolkit 自建轻量 REPL 框架。** 代码量差距不大（约 300-400 行 vs cmd2 的 200-250 行），但换来的灵活性在 Phase 3/4 会持续放大——特别是 Claude Code 风格的补全、语法高亮、和自定义 key binding。cmd2 的 CommandSet/argparse 模式与 cpho 的 skill 驱动架构存在阻抗失配，长期是负债。

---

## 2. 社区与生态

| 维度 | cmd2 | prompt_toolkit |
|------|------|---------------|
| GitHub stars | ~686 | ~10,500 |
| PyPI 下载/周 | ~3,500 | ~12,000,000 |
| 最近发布 | v3.5.1 (2026-04) | v3.0.52 (2025-11) |
| Python 版本 | >=3.8 | >=3.8 |
| 维护者 | 1 人 (Todd Leonhardt) | 社区 (Philip Ieong + contributors) |
| 依赖 | prompt_toolkit, pyperclip, wcwidth | wcwidth |
| 使用者 | 内部工具为主 | IPython, Jupyter, pgcli, mycli, AWS CLI v2, Azure CLI |

**判断:** prompt_toolkit 的生态优势是压倒性的。cmd2 虽然活跃维护但与 prompt_toolkit 不在同一量级。如果 cpho-cli 要长期维护，站在 prompt_toolkit 生态上是更安全的选择。

cmd2 的风险点：单维护者 bus factor = 1。虽然 Todd 维护了 15 年+，但一旦停更，cmd2 的替代品是零（没有同等功能的 prompt_toolkit 包装库）。

---

## 3. 功能对比：Phase 02.2 需求映射

### 3.1 REPL 主循环

| 需求 | cmd2 | prompt_toolkit 自建 |
|------|------|---------------------|
| 启动 REPL loop | `app.cmdloop()` — 一行 | 需手写 `while True: input = session.prompt(...)` 循环 (~15 行) |
| 自定义 prompt | `prompt = "cpho> "` 类属性 | `session.prompt("cpho> ")` 参数 |
| Ctrl+C 不退出 | 默认内置 | 需 catch `KeyboardInterrupt` (~3 行) |
| Ctrl+D 退出 | 默认 EOF 退出 | 默认抛出 `EOFError`，catch 即可 (~3 行) |
| 启动 banner | `intro` 属性或重写 `preloop()` | 在循环前 print (~2 行) |

**差距:** 约 20 行。可忽略。

### 3.2 命令注册与分发

这是最大的架构差异。

**cmd2 方式：** 继承 `cmd2.CommandSet`，方法名 `do_search` 自动映射为 `/search`。

```python
class SearchCommandSet(cmd2.CommandSet):
    def do_search(self, args: str):
        """搜索题目"""
        ...

    # 复杂参数需要 argparse 装饰器
    @cmd2.with_argparser(search_parser)
    def do_search(self, args: argparse.Namespace):
        ...
```

**问题:** cmd2 的命令模型是「方法即命令」，参数解析靠 argparse。但 cpho 的 skill 系统（Phase 3）是「SkillSpec 即命令」，命令元信息（名称、参数、补全）来自 YAML 或 SkillSpec 对象，不是类方法。这导致 `SkillCommandAdapter` 需要把 SkillSpec 逆向适配成 cmd2 的 CommandSet/argparse 模型——这是阻抗失配的核心。

**prompt_toolkit 自建方式：**

```python
# 命令只是一个 dataclass/dict，注册到 registry
@dataclass
class Command:
    name: str
    help: str
    handler: Callable
    completers: dict[str, Completer]  # 按参数名
    arg_parser: Callable | None

# registry 是普通 dict
registry: dict[str, Command] = {}

# 主循环里的分发
input_text = await session.prompt_async("cpho> ")
cmd_name, *args = shlex.split(input_text)
if cmd_name in registry:
    await registry[cmd_name].handler(session, args)
```

**优势:** 命令模型与 cpho 的 SkillSpec 同构——Phase 3 的 `SkillCommandAdapter` 只需把 `SkillSpec` 字段映射到 `Command` dataclass，没有概念转换。`/help` 直接遍历 `registry.values()` 生成，不用靠 cmd2 的 argparse 元编程。

**判断:** cmd2 在此维度的"便利"是假的——它帮你省了命令分发的 30 行代码，但引入了与 cpho 架构的阻抗失配，Phase 3 要花更多代码去适配。

### 3.3 Tab 补全

| 需求 | cmd2 | prompt_toolkit 自建 |
|------|------|---------------------|
| 命令名补全 | 自动（从 CommandSet 方法名） | 手写 `WordCompleter` (~5 行) |
| 参数补全 | argparse choices 自动生成 | 手写自定义 `Completer` 类 |
| 标签补全（动态列表） | 需用 `cmd2.Cmd.path_complete` 等工具方法 | `Completer` 类天然支持异步/动态数据源 |
| 上下文感知补全 | 困难（argparse 模型是静态的） | 简单（`Completer.get_completions` 接收当前文档状态） |

**关键差异：上下文感知补全。** Phase 3 的 `/explain <problem_id>` 需要从当前搜索结果列表中补全 problem_id，这不是静态的 argparse choices。prompt_toolkit 的 `Completer` 接口天然支持这种模式；cmd2 需要绕过 argparse 手动实现。

**代码量差距:** prompt_toolkit 多写约 30 行（一个自定义 Completer 类），但能力更强。

### 3.4 帮助系统

**cmd2:** `--help` 从 argparse 自动生成，`/help` 列出所有命令。零代码。

**prompt_toolkit 自建:** 手写 `/help` 命令 (~20 行)，遍历 `registry` 生成帮助文本。参数级别的 `--help` 需要自己在 Command 里存储参数说明并格式化输出。

**差距:** cmd2 确实省事。但 `/help` 的 UI 完全可控对 cpho 是加分项——可以用中文、分组、带示例的格式，而不是 argparse 的美式英文风格。`/help` 是一个写一次就不会再动的模块。

### 3.5 历史持久化

**cmd2:** `persistent_history_file` 参数一行搞定，自动压缩 JSON 存储。

**prompt_toolkit:** `FileHistory` 类，也是两行：
```python
from prompt_toolkit.history import FileHistory
session = PromptSession(history=FileHistory(".cpho_history"))
```

**差距:** 零。prompt_toolkit 甚至更灵活（可以选择 `InMemoryHistory` 用于测试）。

### 3.6 会话状态（SessionState）

两种方案完全一致——都是 dataclass 挂在 app 实例上。REPL 框架不涉及此维度。

### 3.7 输出格式化（表格、分页、颜色）

| 需求 | cmd2 | prompt_toolkit 自建 |
|------|------|---------------------|
| 表格 | 内置 `SimpleTable`/`BorderedTable` | 需手写或引入 `tabulate`/`rich` |
| 分页 | 内置 `ppaged()` | 无内置，可手写 (~30 行) 或用 `less` subprocess |
| ANSI 颜色 | 内置 `cmd2.ansi.style()` | `prompt_toolkit.formatted_text` 或直接用 ANSI escape |
| 语法高亮 | 仅输入行 | 内置 `Lexer` 接口，可高亮命令名、参数、值 |

**判断:** cmd2 的表格/分页很实用。prompt_toolkit 没有这些——但 cpho 的 Phase 02.2 上下文（D-12）已经明确说"不引入 Rich"。如果选 prompt_toolkit，表格和分页需要自己实现，预估多 50-80 行。

但反过来说，prompt_toolkit 的语法高亮是 cmd2 没有的——`/search 力学` 可以把 `/search` 渲染成蓝色、`力学` 渲染成绿色，大幅提升 UX。

### 3.8 Settable（可 set 的配置项）

**cmd2:** `Settable` 自动暴露为 `set max_results 50` 命令。

**prompt_toolkit 自建:** 手写 `/set` 命令 (~30 行)。但 UX 更好——`/set max_results 50` 带补全，而不是 cmd2 的全局 `set` 命令混在一起。

**差距:** cmd2 省事，但 `Settable` 把所有配置项塞进一个全局命名空间，随着配置项增多会变混乱。手写 `/set` 虽然多点代码，但可以分组、限制可见范围、加验证。

---

## 4. Phase 3/4 前瞻

这是选择 prompt_toolkit 的核心原因。

### 4.1 Skill → Command 映射

Phase 3 的 SkillSpec 需要动态生成 REPL 命令。在 cmd2 下，这意味着运行时用 `type()` 动态创建 CommandSet 子类并注册——可行但 hacky。在 prompt_toolkit 自建下，就是 `registry[skill.name] = Command(...)` 一行。

### 4.2 自定义 Key Binding

Phase 3/4 可能需要类似 Claude Code 的快捷键（Ctrl+R 搜索历史、Ctrl+O 查看详情、Esc 退出当前模式）。prompt_toolkit 的 key binding 系统是原生能力；cmd2 没有暴露这个层。

### 4.3 多行输入

`/quiz` 的 Socratic 对话可能需要多行输入。prompt_toolkit 天然支持（`multiline=True`）；cmd2 需要用 `terminator=` 或 `continuation_prompt`，体验较差。

### 4.4 语法高亮

```python
# prompt_toolkit: 输入行实时语法高亮
class CphoLexer(Lexer):
    def lex_document(self, document):
        # /command 蓝色, args 绿色, --flags 黄色
        ...
```

cmd2 无法做到输入行的语法高亮（它只是调用 prompt_toolkit 的默认输入）。

---

## 5. 代码量估算

以下是实现 Phase 02.2 完整功能（含 `/search`、`/show`、`/workspace`、`/status`、`/config`、`/index`、`/reload-index`、`/resume`）的预估代码量：

| 模块 | cmd2 | prompt_toolkit 自建 | 差额 |
|------|------|---------------------|------|
| REPL 主循环 (app.py) | ~60 行 | ~80 行 | +20 |
| 命令注册系统 (registry.py) | ~20 行 | ~40 行 | +20 |
| 命令分发 (commands/*.py) | ~150 行 (argparse) | ~180 行 (shlex + 手写解析) | +30 |
| 补全系统 | ~50 行 (内置于 argparse) | ~80 行 (自定义 Completer) | +30 |
| 帮助系统 | ~0 行 (自动) | ~30 行 | +30 |
| 历史持久化 | ~5 行 | ~5 行 | 0 |
| 表格输出 | ~40 行 (内置) | ~60 行 (手写 tabulate) | +20 |
| 分页 | ~5 行 (ppaged) | ~30 行 | +25 |
| Settable | ~0 行 (内置) | ~30 行 | +30 |
| 启动 banner | ~10 行 | ~10 行 | 0 |
| **合计** | **~340 行** | **~545 行** | **+205 行** |

差额约 200 行。这是**整个 Phase 02.2 REPL 层的总代码量差值**，不是"额外脚手架"。而且这 200 行中：

- 约 100 行（帮助系统、表格、分页、Settable）是写一次就不再动的 UI 代码
- 约 50 行（补全系统）在 Phase 3 会因为 cmd2 的阻抗失配而反向追平
- 约 50 行（命令解析）换来的是与 SkillSpec 同构的命令模型

**实质上，净差额在 50-100 行之间，但灵活性和未来扩展性差距巨大。**

---

## 6. 风险

### cmd2 风险

1. **Bus factor = 1.** Todd Leonhardt 是唯一维护者。项目依赖 `pyperclip`，而 `pyperclip` 也已多年未更新。
2. **社区规模不足以推动演进。** 686 stars 意味着几乎没有外部 contributor。如果有 bug，修的速度取决于一个人。
3. **Phase 3 阻抗失配。** SkillCommandAdapter 需要在 cmd2 CommandSet 模型和 SkillSpec 模型之间做概念转换，未来每个新 skill 类型都要重复这个转换。
4. **无法做 Claude Code 级别的 UX。** 语法高亮、自定义 key binding、上下文感知补全——这些 cmd2 要么不支持，要么需要 hack。

### prompt_toolkit 自建风险

1. **自建框架质量。** REPL 循环、命令分发、帮助系统——这些需要自己写，质量取决于实现。但如果遵循 cpho 的芯-壳分离（REPL 在 `cli/repl/`），框架代码与业务逻辑完全隔离，质量是可控的。
2. **初期开发速度慢约 20-30%。** 需要在 Phase 02.2 多投入半天到一天写脚手架。
3. **没有现成的"REPL 框架参考"。** 需要自己设计 REPL 的抽象层，但可以参考 Claude Code 的开源实现模式和 IPython 的架构。

---

## 7. 架构草图：prompt_toolkit 自建方案

```
src/cpho_cli/cli/repl/
  __init__.py
  app.py              # prompt_toolkit 主循环, PromptSession
  commands.py         # Command dataclass + registry dict (~80 行)
  completers.py       # 自定义 Completer: 命令名/标签/problem_id/文件路径
  session.py          # SessionState dataclass (与 cmd2 方案相同)
  display.py          # 表格/分页/ANSI 工具
  commands/
    search.py         # do_search, do_show, do_related handler 函数
    workspace.py      # do_workspace, do_status, do_index 等 handler 函数
    help.py           # do_help handler
    set_cmd.py        # do_set handler
  adapters/
    skill_command.py  # SkillSpec → Command 适配 (Phase 3 实现)
```

核心抽象只有两个：

```python
@dataclass
class Command:
    name: str                    # "/search"
    help: str                    # "按标签搜索题目"
    usage: str                   # "/search <tag> [--limit N]"
    handler: Callable            # async def do_search(session, args)
    completer: Completer | None  # 参数补全
    category: str                # "搜索" / "工作空间" / "技能"

# 全局注册表 — 纯 dict，Phase 3 SkillCommandAdapter 就是 registry[name] = Command(...)
registry: dict[str, Command] = {}
```

主循环不到 40 行：

```python
async def repl_loop(session_state: SessionState) -> None:
    prompt_session = PromptSession(
        history=FileHistory(history_path),
        completer=CphoCompleter(registry),
    )
    while True:
        try:
            line = await prompt_session.prompt_async("cpho> ")
        except (EOFError, KeyboardInterrupt):
            break
        cmd_name, *args = shlex.split(line)
        cmd = registry.get(cmd_name)
        if cmd:
            await cmd.handler(session_state, args)
        else:
            print(f"未知命令: {cmd_name}，输入 /help 查看可用命令")
```

这个架构的一个关键优势：**Phase 3 的 `SkillCommandAdapter` 就是一行注册：**

```python
# Phase 3 — 把 core 层的 SkillSpec 暴露为 REPL 命令
def register_skill_adapters(registry: dict, skills: list[SkillSpec]) -> None:
    for skill in skills:
        registry[f"/{skill.name}"] = Command(
            name=f"/{skill.name}",
            help=skill.description,
            usage=skill.usage,
            handler=make_skill_handler(skill),
            completer=make_skill_completer(skill),
            category="技能",
        )
```

---

## 8. 建议

选择 **prompt_toolkit 自建轻量 REPL 框架**。理由排序：

1. **生态碾压** — 12M vs 3.5k 周下载量，不在一个量级
2. **架构同构** — Command dataclass 与 SkillSpec 天然对齐，Phase 3 适配零阻抗
3. **UX 上限** — 语法高亮、上下文补全、自定义 key binding 是 cmd2 做不到的
4. **长期风险低** — prompt_toolkit 的 bus factor 远超 cmd2
5. **代码量差距小** — 净差额约 50-100 行，不是 500-800 行
6. **Claude Code 风格** — 用户明确想要的方向，prompt_toolkit 是唯一能达成的基础

代价：Phase 02.2 初期多投入半天到一天搭建脚手架，但这是值得的——脚手架写一次，Phase 3/4/5 都在省钱。

---

## 9. 如果要改，下一步

1. 更新 `02.2-CONTEXT.md` 中的 D-01 决策（cmd2 → prompt_toolkit）及理由
2. 重写 `02.2-01-PLAN.md`（当前 PLAN 全部基于 cmd2 的类和方法）
3. 在 `02.2-PATTERNS.md` 中记录 REPL 层的新架构模式
4. 开始实现：先建 `Command` dataclass + registry + 主循环，再逐个实现命令
