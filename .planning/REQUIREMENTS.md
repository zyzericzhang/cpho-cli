# Requirements: CPHO CLI

**Defined:** 2026-05-20
**Core Value:** 生成质量——真正找到题目的难点、启发点，讲清楚每一步推导的"为什么"，关联到相关题目形成知识网络。

## v1 Requirements

### 核心管线 (Core)

- [x] **CORE-01**: 用户可通过默认 `config.local.yml`、显式 `--config` 或环境变量设置 LLM API key；同一配置文件可保存多个 provider/key profile，并通过 `--provider` 选择，密钥不硬编码不提交 git
- [x] **CORE-02**: 用户可指定本地文件夹作为工作空间，工具自动发现其中所有 PDF 和图片文件作为待分析试卷，通过 Phase 02.1 切分器将多题试卷拆分为独立题目条目
- [x] **CORE-03**: 用户可通过抽象 OCR 接口提取 PDF/图片中的文本（含中文+LaTeX 混合内容），默认使用 RapidOCR，接口支持切换其他 OCR 引擎
- [x] **CORE-04**: 用户可运行 `cpho solve <题目>` 命令，通过 DAG 管线引擎分步执行 LLM 调用，每步裁剪上下文聚焦单任务，步骤间通过 blackboard 传递中间结果
- [ ] **CORE-05**: 项目包含 20-30 道精选物理竞赛题的黄金测试集，用于每次 prompt 或模型变更后的回归验证，确保解析质量不退化

### 索引层 (Index)

- [x] **IDX-01**: 用户运行 `cpho index` 对工作空间中所有题目（经 Phase 02.1 从试卷拆分）自动生成标签（物理模型、启发点、难点、数学技巧），标签存入 JSONL 索引文件
- [x] **IDX-02**: 索引系统使用内容哈希检测试卷文件变更（新增/修改），仅对变更文件重新索引
- [x] **IDX-03**: 后续 skill 执行时通过标签索引检索题目，而非重复读取原始文件全文，标签使用受控词汇表保证一致性

### 内置 Skill (Built-in)

- [ ] **SKILL-01**: 用户运行"逐步讲解模式"，对一道题输出完整推导过程，每一步明确说明"为什么想到这一步"的思维逻辑，不只是数学计算的罗列
- [ ] **SKILL-02**: 用户运行"主动提问模式"，工具先检查答案正确性 → 提取启发点和难点（区分于重复性计算）→ 生成标签 → 向学生输出问题列表以检验理解，支持 REPL 对话式交互
- [ ] **SKILL-03**: 用户选择两道或多道题目运行"对比分析模式"，工具找出共同物理模型、共同解题思路，或基于标签自动关联工作空间中的其他相关题目进行联合分析
- [ ] **SKILL-04**: 用户选择一组关联题目运行"组卷输出模式"，工具从原始 PDF 中裁剪对应页面，拼接生成两份 PDF 文件（题目卷 + 答案卷）

### Skill 系统 (Plugin)

- [ ] **PLUGIN-01**: 用户可将自定义 skill 编写为 YAML 配置文件（定义输入、步骤 DAG、prompt 模板引用、输出格式），放入 skills 目录后被系统自动发现和加载
- [ ] **PLUGIN-02**: 用户可通过 Skill Creator 输入自然语言描述，系统自动生成完整的 skill YAML 配置和初始 prompt 模板
- [ ] **PLUGIN-03**: 用户可使用 Python 脚本编写自定义 skill（实现标准 SkillBase 接口），获得完全可编程的扩展能力
- [ ] **PLUGIN-04**: 用户可通过 `pip install` 安装第三方 skill 包（通过 entry points 发现），自动注册到本地 skill 系统

### 知识网络 (Knowledge)

- [ ] **KNOW-01**: 索引系统基于标签相似度自动构建题目之间的知识图谱关联（相同模型、相似启发点、关联思路）
- [ ] **KNOW-02**: 用户在执行任一 skill 分析某道题时，工具自动从索引中拉取标签最相似的相关题目上下文注入分析管线

### TUI REPL 界面 (TUI)

- [ ] **TUI-01**: 用户运行 `cpho repl` 进入 REPL 交互界面，可用 `/` 斜杠命令执行操作，命令支持 Tab 自动补全
- [ ] **TUI-02**: REPL 会话内搜索结果、当前题目等上下文跨命令共享（有状态会话）
- [ ] **TUI-03**: Skill 注册为 Command 对象 + 补全规则，新增 skill 不需要修改 REPL 主循环或 TUI 布局
- [ ] **TUI-04**: 首批实现 `/search`（按标签/关键词查题）和 `/show`（显示题目详情）两个斜杠命令

## v2 Requirements

(暂无——v1 范围已覆盖所有当前规划能力)

## Out of Scope

| Feature | Reason |
|---------|--------|
| GUI / Web 界面 | v1 纯命令行 + TUI REPL，不做图形界面 |
| 数据库存储（PostgreSQL/Supabase） | 文件系统 + JSONL 足够 v1 使用 |
| 多用户 / 权限 / 登录系统 | 本地单用户工具 |
| LaTeX 渲染引擎 | PDF 输出采用图片拼接方案，不重渲染公式 |
| 自主 ReAct-style Agent | 使用确定性 DAG 管线，确保每一步可控可审计 |
| 和线上 CPHO Platform 的数据同步 | v2+ 联动功能 |
| 向量检索 / RAG | v1 使用结构化标签索引，更可控 |
| 手机端 / 平板端 | 仅桌面 CLI |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CORE-01 | Phase 1 | Complete |
| CORE-02 | Phase 1 | Complete |
| CORE-03 | Phase 1 | Complete |
| CORE-04 | Phase 1 | Complete |
| CORE-05 | Phase 1 | Needs Review |
| IDX-01 | Phase 2 | Complete |
| IDX-02 | Phase 2 | Complete |
| IDX-03 | Phase 2 | Complete |
| SKILL-01 | Phase 3 | Pending |
| SKILL-02 | Phase 3 | Pending |
| SKILL-03 | Phase 4 | Pending |
| SKILL-04 | Phase 4 | Pending |
| PLUGIN-01 | Phase 3 | Pending |
| PLUGIN-02 | Phase 4 | Pending |
| PLUGIN-03 | Phase 4 | Pending |
| PLUGIN-04 | Phase 4 | Pending |
| KNOW-01 | Phase 4 | Pending |
| KNOW-02 | Phase 4 | Pending |
| TUI-01 | Phase 02.2 | Pending |
| TUI-02 | Phase 02.2 | Pending |
| TUI-03 | Phase 02.2 | Pending |
| TUI-04 | Phase 02.2 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22 (100%)
- Unmapped: 0

---
*Requirements defined: 2026-05-20*
*Last updated: 2026-05-24 — Phase 2 complete, Phase 02.1 inserted, paper splitting semantics applied*
