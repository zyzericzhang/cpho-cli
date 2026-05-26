# Phase 05: 用户手册 + 开源准备 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-26
**Phase:** 05-user-manual-opensource
**Mode:** --all --batch --analyze（所有灰区自动选中，批量提问，含权衡分析表）
**Areas discussed:** README 风格定位与版面、Demo 媒介与覆盖范围、docs/user 结构与模板、Python 扩展机制契约、10 分钟 Quick Start 路径、开源准备清单

---

## 灰区 1：README 风格定位与版面

| 选项 | 说明 | 选中 |
|------|------|------|
| uv / ruff 骨架 | Python 工具系，章节简洁，安装一行命令 | |
| Continue.dev / cline 风 | 面向终端用户，截图 hero，中文社区接受度高 | |
| **ripgrep / fzf 风** | 极简 hero，密集对比表格，强说服力对比段 | ✓ |
| 传统 GNU 风 | 文档全但视觉冷，上手慢 | |

**用户选择：** `1c`——ripgrep/fzf 风  
**语言：** `2a`——纯中文（命令/代码原样）  
**章节顺序：** `3c`——Quick Start 最前，"5 分钟跑起来"先于所有介绍  
**长度：** `4b`——300–600 行，含完整 skill 简介 + 示例  

---

## 灰区 2：Demo 媒介与覆盖范围

| 选项 | 说明 | 选中 |
|------|------|------|
| **asciinema SVG** | GitHub README 可直接播放，体积小，可编辑 | ✓ |
| GIF（vhs） | 任何渲染器直接显示，但文件大 | |
| 静态截图 PNG | 制作最快但静态，切断上下文 | |
| PNG + asciinema 组合 | 两者都要 | |

**用户选择：** `1a`——asciinema SVG  
**Demo 内容：** `2c`——完整学习流程（index → /solve → /explain → 找同类题），Phase 4 完成后内容  
**放置位置：** `3` GitHub 惯例——`.github/assets/`  
**录制时机：** `4c`——Phase 5 执行时一次性录制所有 Demo  

---

## 灰区 3：`docs/user/` 结构与模板

| 选项 | 说明 | 选中 |
|------|------|------|
| **按 skill 分章** | 与代码目录对应，维护成本低 | ✓ |
| 按用户任务分章 | 新手友好，但内容易重复 | |
| 混合（skill + workflow 导航） | 两者兼顾但文档量翻倍 | |

**用户选择：** `1a`——按 skill 分章  
**章节模板：** `2a+c`（跳过 b）——用途 + 前置条件 + 用法/参数 + 典型输出 + 导出文件 + 端到端完整示例（不含"常见坑"段）  
**顶层导航：** GitHub 惯例——`docs/user/README.md`  
**REPL 章节：** `4b`——不单独成章，REPL 用法分散在各 skill 章节  

---

## 灰区 4：Python 扩展机制契约

| 选项 | 说明 | 选中 |
|------|------|------|
| **复制 builtin_skill 目录模板** | 零新接口，纯 Python，最低门槛 | ✓ |
| SkillBase 子类 + 自动发现 | 结构清晰但需新增接口 | |
| 函数装饰器 `@skill()` | 最轻量，但 Phase 5 引入新运行时机制有风险 | |

**用户选择：** 按推荐——复制 builtin_skill 目录模板  
**REPL 注册：** `2a`——自动扫描 `builtin_skills/` 目录，符合命名约定即注册  
**文档覆盖：** `3c`——核心 API + REPL 注册方式 + 完整最小 skill 示例代码  
**Out of Scope 声明：** `4a`——扩展文档开头 Out of Scope 框  

---

## 灰区 5：10 分钟 Quick Start 路径

| 选项 | 说明 | 选中 |
|------|------|------|
| 从 `cpho index examples/` 开始 | 展示完整流程，体现"文件夹即题库"核心价值 | |
| 从 `/solve` 单题开始 | 零前置依赖，但不展示 index | |
| **从 `/explain` 开始（REPL 为主）** | 展示最具吸引力的核心 skill | ✓ |
| 从 `cpho index 你的题库路径` 开始 | 不附 sample，用户用自己文件 | |

**用户选择：** 从 `/explain` 开始，重心在 REPL 交互体验  
**流程：** clone → config.local.yml API key → `cpho index examples/` → 进 REPL → `/explain`（选 Tone → 看输出）  
**Sample 数据：** `2c`——`examples/` 放 1 道 IPhO 公开题（PNG + 答案 PNG），注明来源  
**API key 引导：** `3a`——Quick Start 第 1 步就提示配置  

---

## 灰区 6：开源准备清单

**用户选择：** 全都要  

| 项目 | 说明 | 决定 |
|------|------|------|
| LICENSE（MIT） | 开源必须 | ✓ Phase 5 新建 |
| CONTRIBUTING.md | 轻量版 5–10 行 | ✓ Phase 5 新建 |
| CODE_OF_CONDUCT.md | 标准模板 | ✓ Phase 5 新建 |
| .github/ISSUE_TEMPLATE/ | bug report + feature request | ✓ Phase 5 新建 |
| README 依赖与鸣谢段 | 末尾列主要依赖 | ✓ |
| README Out of Scope 段 | 废弃功能公开声明 | ✓ 独立一段 |
| Badges | License + Python + uv | ✓ |
| .gitignore 补 .claude/ | 显式排除 | ✓ |

**关于 .planning/ 的曲折：** 用户最初要移除 .planning/ 和 .claude/，后撤回，改为只排除不应公开的文件。经确认，.planning/ 随仓库公开，只在 .gitignore 补 .claude/ 显式排除。

---

## Claude's Discretion

- asciinema 录制工具选型（vhs / asciinema 原生 / termtosvg）
- docs/user/ 各章具体示例输出内容（基于 Phase 3/4 真实交付生成）
- IPhO 具体选哪道题（由研究 agent 确认版权后选定）
- CONTRIBUTING.md 贡献流程细节（参照 ripgrep/uv 同类模板）

## Deferred Ideas

- 多语言 README（EN/CN 切换）——用户选纯中文，英文版推后
- GitBook / Docusaurus 文档站——社区增长后再升级
- asciinema 托管（asciinema.org）——仓库成熟后迁移
- SECURITY.md——有社区后补
