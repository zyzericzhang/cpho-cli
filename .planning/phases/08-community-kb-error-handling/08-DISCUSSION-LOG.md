# Phase 8: 社区 KB + 错误处理 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-27
**Phase:** 08-community-kb-error-handling
**Areas discussed:** 社区同步机制, Prompt injection 防御, 错误分类体系, 错误文档组织

---

## 社区同步机制

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub API tarball | 下载 release tarball，不依赖系统 git | ✓ |
| git clone | `git clone --depth 1 --branch <tag>` | |
| 双路径 fallback | API + git 两套 | |

| Option | Description | Selected |
|--------|-------------|----------|
| 强制 token | 必须配 GitHub token | |
| 纯 unauthenticated | 不配 token | |
| 可选 token | 不配也能跑，配了更稳 | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| `~/.config/cpho/community.yml` | 用户级全局 | ✓ |
| `<workspace>/.cpho/community.yml` | per-workspace | |
| 两层覆盖 | workspace 覆盖 user | |

| Option | Description | Selected |
|--------|-------------|----------|
| 纯幂等 | 已有就跳过 | |
| 检查新 release | 每次查远程 | |
| 幂等 + --force | 默认跳过 + 强制重拉 | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| `community-kb/<repo-name>/` | 按仓库隔离 | ✓ |
| flatten 一层 | 所有文件一层铺开 | |
| 按 tag 分类 | 按受控词汇表 tag 分目录 | |

**User's choice:** 全部认同推荐方案。
**Notes:** 用户确认 GitHub API tarball 方案符合 Python-only 约束。sync 是低频操作，token 策略务实即可。

---

## Prompt injection 防御

| Option | Description | Selected |
|--------|-------------|----------|
| 标签内部 | 每个 reference 内带警告 | |
| system prompt 开头 | 说一次 | |
| 两者都有 | system prompt 原则 + 标签内重申 | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| 校验并拒绝 | sync 时检查 frontmatter，不合格拒绝 | ✓ |
| 不校验 | 使用时报错 | |

| Option | Description | Selected |
|--------|-------------|----------|
| 校验 SHA256 | GitHub API checksum 验证 | ✓ |
| 不校验 | 信任 HTTPS | |

| Option | Description | Selected |
|--------|-------------|----------|
| 报错退出 | 只报错 | |
| 报错 + 提示修配置 | 报错 + 指向解决方案 | ✓ |
| 自动 fallback | 自动换版本 | |

**User's choice:** 全部认同推荐方案。
**Notes:** 用户技术背景不深，方案需用通俗语言解释。确认不做 sync 时内容扫描（"什么是恶意"无法可靠定义）。

---

## 错误分类体系

| Option | Description | Selected |
|--------|-------------|----------|
| 全覆盖 | 所有 raise 三段式 | |
| 只用户可见 | 内部 assert 保持现状 | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| 纯中文 | 不动 | ✓ |
| 中文 + 英文扩展空间 | 预留但不实施 | |

| Option | Description | Selected |
|--------|-------------|----------|
| 单行简洁版 | 一段话 | |
| 多行展开版 | 分三行 | |
| 灵活 | 简单用单行，复杂用多行 | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| 不改结构 | 只在 raise 处改字符串 | |
| 新增 errors.py 集中管理 | 辅助函数集中 + 各模块调用 | ✓ |

**User's choice:** Q1-Q3 指定选项，Q4 让 Claude 决定。
**Notes:** Claude 选择 errors.py 集中方案，理由：grep 守门测试可精确枚举所有 `err_` 前缀函数调用。

---

## 错误文档组织

| Option | Description | Selected |
|--------|-------------|----------|
| 语义化命名 | `config-missing-api-key.md` | ✓ |
| 按异常类 | `config-error.md` | |
| 不强制对应 | 手动映射表 | |

| Option | Description | Selected |
|--------|-------------|----------|
| 极简版 | 错误消息全文 + 修复步骤 | ✓ |
| 标准版 | 何时发生/消息/原因/修复/示例 | |

| Option | Description | Selected |
|--------|-------------|----------|
| 按模块分类列表 | 配置类 / API 类 / 文件类 | |
| 一个大表格 | 错误名 / 一句话 / 链接 | ✓ |
| 先分类再表格 | 分类 + 每类表格 | |

**User's choice:** Q1 "让用户舒服"（语义化命名），Q2 极简版，Q3 大表格。
**Notes:** 文件命名与 `errors.py` 函数名对应，去掉 `err_` 前缀 + 下划线转连字符。

---

## Claude's Discretion
- 错误消息三段式具体措辞模板
- `errors.py` 辅助函数签名设计

## Deferred Ideas
None.
