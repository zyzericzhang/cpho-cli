# Phase 9: 跨平台 + 安装包 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-28
**Phase:** 09-cross-platform-installer
**Areas discussed:** Windows 兼容性及格线, 安装方式用户体验, Spike 判断标准, 跨平台分发范围

---

## Windows 兼容性及格线

### 功能范围

| Option | Description | Selected |
|--------|-------------|----------|
| 全面对等 | 所有功能在 Windows 上和 Mac 完全一样 | ✓ |
| 核心可用 | explain/solve/probe 完美，其他可用就行 | |
| 最低验证 | REPL 能跑不崩就行 | |

**用户选择:** 全部功能对等，不做降级

### 中文显示

| Option | Description | Selected |
|--------|-------------|----------|
| 与 Mac 一模一样 | 逐像素一致 | |
| 中文正常显示 | 不乱，界面不混乱 | ✓ |
| 不出乱码就行 | 最低要求 | |

**用户选择:** 中文正常显示，界面不乱即可

### 验证方式

| Option | Description | Selected |
|--------|-------------|----------|
| 手动验证 | 自己 Windows 电脑跑 | |
| 找人帮忙 | 随便测测 | |
| 全自动 CI | GitHub Actions Windows runner | ✓ |

**用户选择:** 全自动 CI 验证

### 依赖库问题

| Option | Description | Selected |
|--------|-------------|----------|
| 必须搞定 | 硬需求，不妥协 | ✓ |
| 功能降级 | OCR 走在线 API 替代 | |
| 看情况 | 不确定 | |

**用户选择:** 必须搞定，底层依赖问题从根本上解决

---

## 安装方式用户体验

### 用户画像

| Option | Description | Selected |
|--------|-------------|----------|
| 非技术用户 | 物理教练/学生，双击即用 | |
| 技术用户 | 不介意命令行 | |
| 两类都有 | 两种方式都要考虑 | ✓ |

**用户选择:** 覆盖两类用户

### 安装包体积

| Option | Description | Selected |
|--------|-------------|----------|
| 可以接受 | 功能完整 > 体积 | ✓ |
| 控制在 200MB 内 | 体积优先 | |
| 不确定 | 看具体多大 | |

**用户选择:** 体积不设上限，功能完整性优先

### 更新方式

| Option | Description | Selected |
|--------|-------------|----------|
| 自动检测更新 | 启动时提醒下载新版 | ✓ |
| 手动前往 GitHub | 用户自己关注 | |
| 不需要 | 每个版本独立 | |

**用户选择:** 自动检测新版本并提醒

### 平台策略

**用户自行指定:** Windows 做完整安装包（.exe），Mac 一步步引导用户先安装 homebrew 再命令行安装，README 里写清楚。不对称交付策略。

---

## Spike 判断标准

### 体积门槛

| Option | Description | Selected |
|--------|-------------|----------|
| 多大都行 | 只要功能正常 | ✓ |
| 太大不值得 | 走命令行 | |

**用户选择:** 体积不设上限

### 决策权

| Option | Description | Selected |
|--------|-------------|----------|
| 用户拍板 | 看 spike 报告决定 | ✓ |
| 接受建议 | 技术评估直接执行 | |

**用户选择:** 亲自看报告后决定

### 对"不做安装包"的态度

| Option | Description | Selected |
|--------|-------------|----------|
| 同样是成功 | spike 就是为了摸清情况 | |
| 有点失望 | 可接受但遗憾 | |
| 目标仍是做成 | spike 只是确认可行性 | ✓ |

**用户选择:** 目标始终是安装包，spike 提供决策信息而非替代决策

---

## 跨平台分发范围

### Mac 芯片支持

| Option | Description | Selected |
|--------|-------------|----------|
| 只支持 Apple Silicon | M1/M2/M3，2020 年后 | ✓ |
| 两者都支持 | Intel + Apple Silicon | |
| 不关心 | 能跑就行 | |

**用户选择:** 只支持 Apple Silicon，Intel Mac 走 pipx

### Linux

| Option | Description | Selected |
|--------|-------------|----------|
| 写一下 | 一行命令的事 | |
| 不管 | 只做 Mac/Windows | ✓ |
| 不确定 | | |

**用户选择:** 不做 Linux

### 发布方式

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub Releases | README 链接引导 | ✓ |
| 项目官网 | 建个页面 | |
| 无所谓 | 有地方下就行 | |

**用户选择:** GitHub Releases 免费下载

---

## Claude's Discretion

- PyInstaller vs Nuitka 的技术选择——spike 阶段评估后推荐
- Windows Terminal 兼容性问题具体修复方案
- GitHub Actions CI 配置细节（矩阵构建、触发条件、artifact 上传）
- 自动更新检测的实现方式（GitHub API latest release / 本地版本号对比）
