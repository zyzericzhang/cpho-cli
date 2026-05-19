---
title: "CPHO CLI 产品架构决策"
date: "2026-05-19"
context: "explore session — 物理竞赛题目解析 CLI 工具 ideation"
---

## 核心决策

### 1. 产品形态：纯本地 CLI 优先

- pip/npm install 即可运行，不依赖线上后端
- 用户直接指定本地文件夹路径，批量读取 PDF/扫描图片
- 解析结果输出到本地，用户自行对比判断质量
- 保留和线上平台联动的架构可能性（芯-壳分离）

**Why:** 绕过线上题库建设的后端复杂度，快速验证"更多题目上下文 → 更好解析质量"的假设。调试解析质量不应被前端 UI 开发阻塞。

**How to apply:** 任何涉及解析质量的迭代，优先在 CLI 环境验证，确认有效后再考虑同步到线上。

### 2. 架构模式：芯-壳分离（Core Library + Thin Frontends）

```
cpho-cli/
├── core/          # 纯业务逻辑，零 UI/框架依赖
│   ├── models/    # Pydantic 数据模型
│   ├── services/  # 解析管线、OCR、Agent 编排
│   └── ports/     # I/O 接口定义
├── cli/           # 薄适配层（Typer）
└── web/           # 未来：FastAPI 适配层
```

**Why:** CLI 和线上平台共享同一套 core，避免逻辑重复。调研确认这是业界验证的标准模式（Open Interpreter、Tuist、Ganga 等均采用此模式）。

**How to apply:** core 内绝对不出现 print()/console.log()，所有 I/O 通过依赖注入。CLI 和未来的 web 各自实现 I/O 适配器。

### 3. 技术栈：Python 生态

- CLI 框架：Typer（FastAPI 同作者，共享 Pydantic 类型体系）
- 数据模型：Pydantic
- LLM 调用：OpenRouter API（与现有项目一致）
- OCR：待调研（Tesseract / PaddleOCR / 其他本地方案）

**Why:** AI computation 层（LangChain、LlamaIndex、instructor 等）Python 生态远成熟于 Node.js。未来加 FastAPI 即可和现有 Next.js 前端联动，不需要重写解析逻辑。

**How to apply:** 新 CLI 项目独立仓库，Python ≥3.11。core 包零依赖 Next.js/React/Supabase。

### 4. 参数调试面板：YAML 配置 + JSONL 实验记录

- 参数配置：单一 YAML 文件，包含 prompt 模板引用、模型选择、temperature 等
- 实验记录：JSONL 格式，每行一次实验（参数快照 + 时间戳 + 输出摘要）
- 对比方式：用户肉眼对比输出结果，不引入自动评分

**Why:** 用户说"我自己会判断我会对比"，不需要 LLM-as-Judge。YAML + JSONL 是人可读、git 友好、可 grep 的最简方案。promptfoo 和 autoresearch 均验证了此模式。

**How to apply:** 第一个可用版本只需要 `cpho run --config my-config.yaml ./problems/` 和 `cpho compare exp-001 exp-002` 两个命令。

### 5. 目标用户策略：先重度后普及

- 早期：物理竞赛教练、愿意折腾 CLI 的技术用户
- 后期：降低门槛（TUI 面板 → GUI 应用）

**Why:** 重度用户已有题库积累，动机最强，反馈最专业。先在这个群体里快速迭代核心解析质量，比一开始就做易用性更高效。

**How to apply:** 初期不纠结 UX 细节，README 写清楚命令行用法即可。接口稳定后再考虑 Trogon 自动生成 TUI 或 Electron 套壳。

## 关联

- [[cpho-cli-research-questions]] — 待调研的技术选型问题
- [[cpho-cli-seed]] — 项目种子（待创建）
