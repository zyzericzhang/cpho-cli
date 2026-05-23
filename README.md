# CPHO CLI

一个开源的本地命令行工具，帮助物理竞赛教练和学生批量解析竞赛题目。

## 这是什么

CPHO CLI 让你在终端里就能对本地文件夹中的题目（PDF、扫描试卷图片）运行 AI 解析——
输出结构化的逐步推导、物理图景重建、模型归类和关键易错点分析。

它是 [CPHO AI Platform](https://github.com/xxx/cpho-ai-platform) 的姊妹产品。线上平台提供 Web UI 和题库管理，
CLI 提供本地批量处理和参数调试能力。两者共享同一套物理竞赛解析的领域知识（prompt 策略、评测标准）。

## 为什么做这个

调试 AI 解析质量需要在"改参数 → 跑题 → 看结果 → 对比"之间快速循环。
Web UI 的每一次调整都需要前端和后端配合，真正花在解析质量本身的时间被稀释了。

CLI 把所有和解析无关的东西全部剥离，只留下一个最干净的实验环境：
- 没有按钮、表单、页面路由
- 定义一个配置文件，跑一批题，看结果，改参数，再跑
- 物理竞赛教练手头本就有成百上千道题，不需要"导入"——文件夹就是题库

## 当前状态

项目处于 Phase 1 核心管线实现阶段。当前仓库已采用 `uv` + `src/` 布局，并提供基础 CLI、配置加载、workspace 发现、OCR 抽象、skill runtime、solve/eval 入口。

## 开发命令

```bash
uv sync
uv run cpho --help
uv run ruff check .
uv run mypy .
uv run pytest
```

本地 API key 默认从仓库根目录的 `config.local.yml` 读取；也可以继续使用
`OPENROUTER_API_KEY` 或显式传入 `--config`。本地配置文件已被 git ignore，不能硬编码或提交真实 key。

最简单配置仍兼容旧格式：

```yaml
provider:
  openrouter_api_key: sk-...
```

如果要在同一个文件里保存多组 key 或后续接入更多 provider，使用 profile 格式：

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
```

默认使用 `active_provider`。临时选择另一组 key：

```bash
uv run cpho solve problem.pdf --answer answer.pdf --provider backup
uv run cpho eval golden_tests/ --provider backup
```

详细产品说明见 [docs/product-spec.md](docs/product-spec.md)。
