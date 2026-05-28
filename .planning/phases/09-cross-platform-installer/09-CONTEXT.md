# Phase 9: 跨平台 + 安装包 - Context

**Gathered:** 2026-05-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 9 收尾 v1.1 分发体验——三步走：
1. 验证 CPHO CLI 在 Windows 10/11 上完整可运行（全功能对等、中文正常显示、CI 自动化验证）
2. 3 天打包方案 spike——评估 PyInstaller/Nuitka 打包成 .exe 的可行性，输出烟测脚本 + 体积报告 + 签名风险评估
3. 根据 spike 结果交付——Windows 走完整 .exe 安装包（GitHub Actions 自动构建 + GitHub Releases 发布），Mac 走文档化安装路径（README 引导用户安装 homebrew 后用命令行安装），Redis 不做安装包

**依赖：** Phase 6（代码层稳定）；可与 Phase 7/8 完全并行

**需求：** INSTALLER-01, INSTALLER-02, INSTALLER-03

</domain>

<decisions>
## Implementation Decisions

### Windows 兼容性验证范围
- **D-01:** Windows 上所有功能必须与 Mac 对等运行——不做功能裁剪，如有依赖库问题必须根本上解决而非降级绕过
- **D-02:** 中文/Unicode 标准：中文正常显示、界面不混乱即可（不需要与 Mac 显示效果逐像素一致）
- **D-03:** 验证方式：全自动 CI（GitHub Actions），每次代码更新自动在 Windows 虚拟机上跑测试

### 安装方式与用户体验
- **D-04:** 用户画像：覆盖两类用户——(a) 物理竞赛教练/学生不熟悉命令行 (b) 有技术基础愿意用命令行
- **D-05:** Windows 交付方式：完整 .exe 安装包，用户下载双击即可运行；体积不设上限，功能完整性优先
- **D-06:** Mac 交付方式：文档化安装路径，README 中一步步引导用户安装 homebrew 后通过命令行安装（不走 .dmg 安装包）
- **D-07:** 更新策略：用户打开软件时自动检测新版本并提醒下载，不需要手动关注 GitHub
- **D-08:** macOS 签名：不做 Apple 开发者签名——README 提供绕过安全警告的说明即可。Apple Developer ID $99/年 不需要

### 安装包发布方式
- **D-09:** 安装包放在 GitHub Releases 页面免费下载，README 中放链接引导用户前往
- **D-10:** Mac 支持范围：只支持 Apple Silicon（M1/M2/M3 芯片，2020 年后的 Mac），Intel Mac 走 pipx 文档化路径
- **D-11:** Linux 不做额外处理——README 里不提 Linux 安装步骤

### Spike 决策权与成败标准
- **D-12:** Spike 判断标准：打包成功 + CI 自动构建 + 干净虚拟机烟测通过——三者全部满足才算通过
- **D-13:** 决策权：用户亲自看 spike 报告与测试结果后拍板决定做/不做
- **D-14:** 最终目标始终是一键安装包——spike 的作用是提供决策信息，不是替代决策。即使 spike 结果不理想，仍倾向寻找可行性而非放弃

### Claude's Discretion
- PyInstaller vs Nuitka 的技术选择——Claude 在 spike 阶段自行评估，根据实际打包结果做推荐
- Windows Terminal 的具体兼容性问题修复方案——每个具体问题自行判断最优解法
- GitHub Actions CI 的具体配置——矩阵构建、触发条件、artifact 上传等细节自行设计
- 自动更新检测的具体实现方式（启动时检查 GitHub API 最新 release / 本地版本号对比等）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 项目顶层
- `.planning/PROJECT.md` — 项目约束（Python only / 本地优先 / 安全）、Key Decisions 表格、技术栈约束
- `.planning/REQUIREMENTS.md` — v1.1 完整需求定义，Phase 9 覆盖 INSTALLER-01, INSTALLER-02, INSTALLER-03
- `.planning/ROADMAP.md` — Phase 9 目标与成功标准详情

### Phase 9 直接相关
- `docs/new-understanding-2026-05-27.md` §四（跨平台兼容与安装包）——用户原始设计意图，"公开提问"标注了安装包/Windows 方案的不确定性
- `pyproject.toml` — 当前项目依赖列表（RapidOCR ONNX ~200MB、PyMuPDF、prompt_toolkit 等是需要关注的打包关键依赖）

### 现有代码参考
- `src/cpho_cli/cli/app.py` — CLI 入口点（`pyproject.toml` 中 `cpho = "cpho_cli.cli.app:app"`）
- `src/cpho_cli/core/ocr.py` — RapidOCR 适配器，`onnxruntime` 依赖（Windows 上的关键验证项）
- `src/cpho_cli/core/llm.py` — httpx HTTP 客户端，API 调用在打包后网络行为不变
- `tests/` — 现有 415 测试用例，Windows CI 基准

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **pyproject.toml 打包配置:** 已有 `[project.scripts]` 入口点、`[tool.setuptools.packages.find]`、`[tool.setuptools.package-data]` 配置——PyInstaller spec 文件需要对应的数据文件收集逻辑
- **GitHub Actions:** 项目已有 `.github/` 目录，需新增 Windows 构建矩阵

### Established Patterns
- **Rich 终端输出:** 项目已使用 `rich` 库做终端格式化，Windows Terminal 兼容性主要验证 rich + prompt_toolkit 组合
- **Unicode 路径:** 核心代码已处理中文路径/文件名（workspace discovery 等模块），Windows 路径分隔符 `\` vs `/` 是额外需要关注的
- **httpx 统一 HTTP:** 所有 LLM API 调用通过 httpx，打包后网络行为无特殊差异

### Integration Points
- **GitHub Releases:** `.exe` 安装包上传到 GitHub Releases，README 链接引导
- **GitHub Actions CI:** 新增 Windows runner 矩阵构建 + 烟测
- **README.md:** 新增 Windows 安装说明（下载 .exe）+ Mac 安装说明（homebrew 路径）

### 打包关键依赖体积参考
- `onnxruntime` + RapidOCR 模型: ~200MB（最大体积贡献者）
- `pymupdf`: ~30-50MB
- Python 运行时（PyInstaller 自带）: ~30-50MB
- 预计总包体积: 300-500MB

</code_context>

<specifics>
## Specific Ideas

- 用户提到"我不知道目前是否需要用户安装好 UV 或者等等之间的插件，希望让用户直接下载之后可以直接运行"——这是 Phase 9 的核心驱动力：让非技术用户无需安装任何环境即可使用
- 用户明确 "Windows 做完整安装包，Mac 一步步引导"——不对称交付策略，不同平台不同体验
- 用户对安装包体积的态度是"可以接受，功能完整比体积重要"——不需要为缩小体积做额外优化
- 关于 Apple 签名：用户愿意先用文档说明绕过不签名安全警告，不急着花 $99/年
- 用户希望软件启动时自动检测新版本——不是纯静态安装包，需要有版本感知能力

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 09-cross-platform-installer*
*Context gathered: 2026-05-28*
