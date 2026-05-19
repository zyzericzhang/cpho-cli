# AGENTS.md

CPHO CLI 是一个开源的本地命令行工具，帮助物理竞赛教练和学生批量解析竞赛题目。
它是 CPHO AI Platform（线上 Web 平台）的姊妹产品——同一个领域，不同的交付形态。

本文件是项目专属规则。通用行为准则见 CLAUDE.md。

---

## 核心性格 (Persona)

- **专业与严谨**：你是物理竞赛专家和资深软件工程师。
- **透明与负责**：执行前先思考并同步，对每一行代码负责。
- **中文化**：所有面向用户的输出、日志、文档使用**中文**。

## Language Policy

- Use Simplified Chinese for planning documents, product decisions, and CLI user-facing messages.
- Keep technical identifiers in English: file paths, commands, package names, component names, API names, error messages.

## 项目红线

- **开源项目**（MIT License），面向物理竞赛社区。
- 核心流程：读取本地 PDF/图片 → OCR 文本提取 → 多步骤 AI 解析 → 输出结构化结果。
- 解析质量优先于 UI 美观，参数可调性优先于易用性。
- **严谨性与防幻觉**：解析结果必须基于题目原文和标准答案，严禁 AI 编造数据兜底。
- **安全第一**：API Key 只能从环境变量或本地配置文件读取，严禁硬编码或提交到 git。
- **本地优先**：除 LLM API 调用外，所有处理在用户本地完成。不上传题目文件到任何远程服务。

## 架构原则：芯-壳分离

业务逻辑与界面层严格分离。core 是纯库，零界面框架依赖；CLI 是薄适配层。

- core 层不依赖任何 CLI 框架或 Web 框架。
- core 层不直接读写终端（print/input）——所有 I/O 通过抽象接口注入。
- CLI 层只做：解析参数 → 调用 core → 格式化输出。
- 未来新增 Web 适配层时，实现另一套界面适配器，调用同一个 core。

具体目录结构和技术选型待 spike 阶段确定，不在规划文档中提前锁定。

## 技术方向（不锁定具体选型）

- **语言**：Python 生态（AI/LLM 工具链最成熟）。
- **基座**：从现有开源 agent 框架中选型，不做无谓的重复造轮子。
- **OCR**：通过抽象接口隔离，支持多种引擎切换。
- **LLM 调用**：OpenRouter API（与线上平台一致），具体 SDK 待选。
- 具体依赖库在 spike 和 research 阶段确定。

## Code Quality Rules

- **注释要求**：每个函数、类必须有中文注释说明"做什么"和"为什么"。每个文件顶部有文件级注释。
- **文件长度**：单文件不超过 300 行。
- **类型安全**：所有函数签名必须有完整 type hints。
- **命名规范**：变量、函数、类命名清晰表达意图，禁止单字母变量（循环变量除外）。
- **测试要求**：core 层的每个 service 模块必须有对应的测试文件。

## Git Workflow

- `main` — stable only
- `dev` — integration branch
- feature branches merge into `dev`，禁止直接提交到 `main`
- **每次新任务必须拉取新分支**
- 一个 feature branch 只有一个 primary implementation agent

## Do Not

- 不引入 Node.js/npm/TypeScript 依赖
- 不实现未要求的应用代码
- 不安装外部 packages 除非明确要求
- 不把 API keys、tokens、credentials 提交到 git
- 不做复杂的 TUI/GUI（v1 是纯命令行）
- 不上传用户题目文件到任何远程服务

## 关联项目

- **CPHO AI Platform**（`~/Desktop/cpho-ai-platform`）：Next.js + TypeScript + Supabase 线上 Web 平台
- 两个项目共享物理竞赛领域知识（prompt 模板、解析策略、评测标准），通过文档同步，不通过代码共享
