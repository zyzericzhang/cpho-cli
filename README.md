# CPHO CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](pyproject.toml)
[![uv](https://img.shields.io/badge/package%20manager-uv-5C3EE8.svg)](https://github.com/astral-sh/uv)

物理竞赛题库的本地命令行工作台：索引 PDF/图片题库，审查标答，生成多风格讲解，主动追问关键步骤，查找同类题，并按编排文件拼装 PDF 试卷。

![CPHO CLI demo](.github/assets/cpho-demo.svg)

## Quick Start

目标：10 分钟内在 REPL 里跑出一次 `/explain`。

```bash
git clone https://github.com/your-org/cpho-cli.git
cd cpho-cli
uv sync
```

创建本地配置。不要提交真实 key。

```yaml
# config.local.yml
active_provider: openrouter
providers:
  openrouter:
    kind: openrouter
    api_key: sk-...
    base_url: https://openrouter.ai/api/v1
model:
  name: openai/gpt-4o-mini
  temperature: 0.2
```

索引示例题库或你自己的题库目录：

```bash
uv run cpho index build examples --config config.local.yml
```

进入 REPL：

```bash
uv run cpho repl --workspace examples --config config.local.yml
```

在 REPL 中：

```text
/search 力学
/show 1
/solve --auto-confirm
/explain --tone teacher --tone dense
/probe
```

Markdown 导出默认写到本机 `.cpho` 输出目录；也可以在 REPL 里设置：

```text
/set out.dir ./exports
```

把 `examples` 替换成 `/Users/你/物理竞赛资料` 这类真实题库目录即可。

## 这是什么

CPHO CLI 面向物理竞赛教练和学生。它不要求你把题目导入云端系统，文件夹就是题库：PDF、扫描图、答案、解析都可以留在本地。

核心差异：

| 需求 | ChatGPT 网页 | 普通 OCR 工具 | CPHO CLI |
|---|---|---|---|
| 批量索引本地题库 | 手动上传 | 只抽文本 | `cpho index build` |
| 标答可信审查 | 容易直接顺着错解讲 | 不理解物理 | `/solve` 给标答挑错 |
| 多风格讲解 | 需要反复 prompt | 不支持 | `/explain --tone teacher --tone dense` |
| 追问关键点 | 临时聊天 | 不支持 | `/probe` 连续问答并导出 |
| 找同类题 | 靠人工记忆 | 不支持 | `/search-related` |
| 组卷 | 手动复制 PDF | 不支持 | `cpho compose build` |

## 功能矩阵

| 功能 | CLI | REPL | 输出 |
|---|---|---|---|
| 建索引 | `cpho index build` | `/index` | `.cpho/index.jsonl` |
| 搜索题目 | `cpho topic browse` | `/search`, `/show` | 表格 |
| 标答审查 | `cpho solve` | `/solve` | JSON + Markdown |
| 多 Tone 讲解 | - | `/explain` | `.explain.md` |
| 主动追问 | - | `/probe` | `.probe.md` |
| 找同类题 | - | `/search-related` | 表格 + Markdown |
| 组卷 | `cpho compose new/build/auto` | `/compose` | 题目 PDF + 答案 PDF |

## REPL 用法

```bash
uv run cpho repl --workspace /path/to/题库
```

常用命令：

```text
/help
/workspace /path/to/题库
/index --only-new
/search newton
/show 1
/set out.dir ./exports
/set probe.max_rounds 12
/solve --auto-confirm --persist-tags
/explain --tone teacher --tone brief
/search-related --top 10
/compose new weekly --count 5
/compose build .cpho/compositions/weekly.yml
```

## Skill 列表

### `/solve`

定位：审查标准答案，不是重新解题。它提取标答步骤、逐步核查，发现符号、推导、引用等问题后写入 `SolveReport`。

```text
/solve --auto-confirm
```

可选 `--persist-tags` 把接受的 discrepancy 写入 index 的 `user_tags`。

### `/explain`

定位：基于题目、答案和可选 Solve 审查结果生成讲解。

```text
/explain --tone teacher --tone dense --tone brief
```

三种 tone：

| Tone | 用途 |
|---|---|
| `teacher` | 老师讲课式，引导性强 |
| `dense` | 知识点密集，推导更完整 |
| `brief` | 简短抓主线 |

### `/probe`

连续主动提问，帮助定位关键物理点和处理步骤。

```text
/probe
```

退出方式：`/exit` 或连续两次空回答。

### `/search-related`

基于 index tag overlap 找同类题。

```text
/search-related p1 --top 10 --min-shared 1
```

REPL 会保存 `last_related`，供组卷时显式使用。

### `compose`

创建编排文件：

```bash
uv run cpho compose new weekly --count 5 --workspace examples
```

构建 PDF：

```bash
uv run cpho compose build examples/.cpho/compositions/weekly.yml --workspace examples
```

自动选题：

```bash
uv run cpho compose auto --count 5 --topic 力学 --tags newton --workspace examples
```

## 配置

最小配置：

```yaml
provider:
  openrouter_api_key: sk-...
```

推荐 profile 配置：

```yaml
active_provider: openrouter
providers:
  openrouter:
    kind: openrouter
    api_key: sk-primary
  backup:
    kind: openrouter
    api_key: sk-backup
    base_url: https://openrouter.ai/api/v1
model:
  name: openai/gpt-4o-mini
  temperature: 0.2
```

临时选择 provider：

```bash
uv run cpho solve problem.pdf --answer answer.pdf --provider backup
```

## 扩展指南

当前支持的是简单 Python 扩展：复制已有 `src/cpho_cli/cli/repl/commands/*.py` 或 `src/cpho_cli/builtin_skills/*` 的结构，写一个明确的 Python service，再在 REPL command installer 里注册 slash command。

详细示例见 [docs/user/extensions.md](docs/user/extensions.md)。

## 依赖与鸣谢

主要依赖：

| 依赖 | 用途 |
|---|---|
| `uv` | Python 项目管理 |
| `typer` | CLI |
| `prompt_toolkit` | REPL |
| `rapidocr` | OCR |
| `pymupdf` | PDF 读取与组卷 |
| `pydantic` | 严格数据模型 |
| `openrouter` | OpenAI-compatible LLM provider |
| `rich` | 进度显示 |

各依赖遵循其各自 license。

## Out of Scope

> **不在计划内：**
> YAML 配置式第三方 skill loader、自然语言生成 skill、`pip install` 第三方 skill 包、GitBook/Docusaurus 文档站、多语言 README。

## License

MIT. See [LICENSE](LICENSE).
