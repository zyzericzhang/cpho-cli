# Phase 2.1 Exploration Notes — Paper-level Splitting

**Date:** 2026-05-23
**Source:** `/gsd-explore` session
**Trigger:** 用户指出真实工作空间里 PDF 是"一份试卷含多道题"，不是"一道题一份 PDF"——这是 Phase 1/2 整个数据模型的形状错配。

## Reference Workspace Sampled

`/Users/ericzhang/Desktop/物理竞赛资料/`

抽样阅读：
- `2024机构卷/2024博知汇/试卷一.pdf` + `试卷一解析.pdf` — scanned，无文字层
- `2024机构卷/2024博知汇/实验试卷一.pdf` — scanned
- `2024机构卷/2024爱培优/理论1.pdf` — scanned
- `2022机构卷/2022学而思/第1套 试题.pdf` — scanned
- `2023机构卷/CPhOfan2023年度试题.pdf` — **PDF 损坏**（corrupt object stream）
- `芝麻物理第四届联考/第四届芝麻物理联考 (复赛) 理论试题.pdf` — **唯一有文字层**（自主 LaTeX 排版）
- `芝麻物理第四届联考/第四届芝麻物理联考 (复赛) 答题卷.pdf` — 答题卷也带题号 anchor
- `2022机构卷/第一届芝麻物理联考试题.pdf` — 文字层

## Reality Constraints

1. **绝大多数试卷 PDF 是扫描件**，无文字层。OCR 不是性价比选项——是**唯一可能的输入**。
2. **机构卷的真实题号格式我们目前看不到**（未 OCR 前未知）；我们只看到芝麻物理一家的格式。规则必须可扩展。
3. **存在损坏 PDF**，pipeline 必须 graceful skip + report，不崩。
4. **试卷封面常带"共 N 道题，共 M 页，总分 X 分"**——切分质量的自校验锚。

## 已观察到的题号格式（芝麻物理样本，仅作初始规则种子）

| 层级 | 格式 | 例子 |
|---|---|---|
| 大题 | 中文序号 + 顿号 + (满分) | `一、(45 分)` / `二、(40 分)` / `三、` |
| 大题命名小节 | 顿号后跟描述性标题 | `三、轨道运动的平均值和virial 定理.` |
| 一级小问 | 全角括号 + 数字 | `（1）` `（2）` |
| 二级小问 | 全角括号 + 罗马字母 | `（i）` `（ii）` `（iii）` |
| 命名子节（混在小问位置） | 全角括号+编号+描述 | `（1）相位差与磁通量.` |

## Locked Design Decisions

### D1 — 切分模式（Q1）
**(a) OCR 之后、索引之前切分**。试卷文件保留为一等公民，但索引 entry 单元是切分后的产物。

### D2 — 索引粒度（Q5）
**大题为 entry**。小问作为 entry 内部 `subquestions` 子结构存在，不独立成 entry。小问的 tag roll up 到大题级。

### D3 — 视觉信息分工（Q6）
- **索引阶段**：OCR 即可（与现实约束一致——扫描件本来就只能 OCR）
- **Phase 3 内置 skills 的真正解析/solve**：用图片或 PDF 直接喂多模态模型，OCR 文本仅作辅助
- 用户自定义 skill 应同时拿到 OCR 文本和原始图片/PDF

### D4 — 题号切分策略（Q7）
**规则先行 + LLM 兜底**：
- 规则 (anchor regex YAML) 是主路径，覆盖大多数情况
- 触发 LLM 兜底的条件：候选大题数 ≠ 封面声明数 / 未检测到任何边界
- LLM 兜底结果持久化到 sidecar，避免重复非确定性调用

### D5 — Sidecar 位置（Q9）
试卷 PDF **同目录**，文件名加 `.cpho.` 前缀（如 `.cpho.试卷一.split.json`）。理由：用户能直接看到、编辑、git 管理；符合"文件夹即工作空间"原则。

### D6 — Phase 2 索引迁移策略（Q8）
**(a) 旧 index 失效**，强制 `cpho index --rebuild`。索引可重建，破坏性变更不写兼容垫片。

### D7 — 索引范围可选择（Q10，新增）
`cpho index` 不再默认整个工作空间扫描。用户可以指定子目录、glob include/exclude。具体 CLI 形态在 spec 阶段定。

## Meta Rule (saved to memory)

设计 cpho 任何功能/plan 时**必须先参考真实工作空间样例**（典型 `~/Desktop/物理竞赛资料`），观察文件夹结构、命名约定、PDF 形态再设计数据模型。
Memory: `feedback_design_reference_real_workspace.md`

## Proposed Phase 2.1 SPEC Outline

- 现实约束（扫描件主导、损坏文件兜底、机构格式未知）
- 数据模型：PaperEntry（一等公民）+ ProblemEntry（索引粒度=大题）
- 切分 pipeline 嵌入点：OCR 之后、tagging 之前
- 题号 anchor 规则的 YAML schema（机构可扩展）
- LLM 兜底触发条件、sidecar 持久化、与 Phase 2 determinism 的协调
- 试题↔解析 题级对齐（同 regex + 按序映射）
- `cpho index` CLI 形态升级：scope selection（path / include / exclude）
- 旧 index 失效策略与用户提示
- UAT 验收点（用真实样例）

## Open Items for SPEC Phase

- `cpho index` scope selection 的精确 CLI 形态：positional path / `--include` / `--exclude` / interactive 选择？
- 切分失败的人工修正 UX：sidecar 手改后是否需要 `cpho split --review`？
- 实验卷 vs 理论卷的题号格式差异（实验卷的样本都是扫描件，未确认）
