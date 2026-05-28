# Phase 09-02 Packaging Spike：下一步决策分析

本文写给“不熟悉打包、CI、Windows runner、artifact 这些概念”的读者。目标是解释：我们现在做的 packaging spike 到底在验证什么、为什么要交给 GitHub Actions 跑、跑完以后应该怎么做决定。

## 1. 先说明当前状态

代码已经推送到 GitHub 分支：

```text
feature/phase9
```

新增的 workflow 文件是：

```text
.github/workflows/packaging-spike.yml
```

它的设计目标是：在 GitHub 的 Windows 机器上自动运行打包脚本，生成或尝试生成 Windows 可执行程序，然后把结果写进：

```text
packaging/SPIKE-REPORT.md
```

并上传为 GitHub Actions artifact。

不过这次手动触发时遇到一个 GitHub Actions 规则限制：

```text
HTTP 404: workflow packaging-spike.yml not found on the default branch
```

这不是脚本本身的问题，而是 GitHub 的 workflow 发现规则：`workflow_dispatch` 手动触发通常要求 workflow 文件已经存在于默认分支（通常是 `main` 或 `master`）。现在这个 workflow 只在 `feature/phase9` 分支上，所以 `gh workflow run packaging-spike.yml --ref feature/phase9` 暂时找不到它。

因此下一步不是继续本地 macOS 跑 Windows 打包，而是要先让 GitHub 能“看见”这个 workflow。

## 2. 这个 spike 到底在验证什么

CPHO CLI 是一个 Python 命令行工具。开发者本机运行时，一般依赖：

- Python 解释器
- uv 虚拟环境
- 项目依赖包，比如 PyMuPDF、RapidOCR、ONNX Runtime
- 项目自带的数据文件，比如 prompts、skills、vocabulary、model catalog

普通 Windows 用户不一定懂这些。Phase 9 的目标是让用户尽量“下载后就能运行”，而不是要求用户先安装 Python、uv、依赖包。

所以我们要验证：能不能把 CPHO CLI 打包成 Windows 上可以直接运行的程序。

这件事有三个难点：

1. Python 程序不是天然的单个 `.exe`。
2. CPHO CLI 依赖一些带本地二进制库的包，例如 `onnxruntime`、`PyMuPDF`。
3. CPHO CLI 还依赖很多非 Python 代码文件，比如 prompt 模板、YAML 词表、内置 skill 文件；这些文件如果没有被打进包里，程序可能能启动，但一运行功能就找不到资源。

所以 spike 不是“写一个漂亮安装器”，而是先回答一个更基础的问题：

```text
我们能不能在 Windows CI 上稳定构建出可运行的 CPHO 程序，并通过最小烟测？
```

## 3. 为什么不用本地 macOS 跑

Windows 打包必须在 Windows 上验证。

原因很简单：Windows 的可执行文件、动态链接库、路径规则、终端行为和 macOS 不一样。

例如：

- `.exe` 只能在 Windows 上真实运行。
- ONNX Runtime 在 Windows 上依赖 Windows DLL 和 VC Runtime。
- 中文路径在 Windows 上有自己的路径编码和终端显示问题。
- PyInstaller 不是跨平台编译器，不能可靠地在 macOS 上直接构建 Windows 程序。

所以本地 macOS 最多只能检查：

- workflow YAML 是否语法正确
- PowerShell 脚本是否文本结构合理
- Python 测试是否通过
- report 模板是否包含必要章节

但它不能证明 Windows 安装包真的能用。

这就是为什么你要求“spike 报告通过 CI 执行来填充，而不是在本地 macOS 跑”是正确的。

## 4. 现在新增的 CI workflow 会做什么

`.github/workflows/packaging-spike.yml` 的核心工作流是：

1. 在 GitHub 提供的 `windows-2022` runner 上启动一台 Windows CI 机器。
2. checkout 当前代码。
3. 安装 uv 和 Python 3.12。
4. 运行：

```powershell
pwsh -NoProfile -File packaging/build_windows.ps1
```

这个脚本尝试用 PyInstaller 构建：

```text
dist/cpho/cpho.exe
```

5. 如果 PyInstaller 产物存在，就运行：

```powershell
pwsh -NoProfile -File packaging/smoke_packaged_windows.ps1 -ExecutablePath dist/cpho/cpho.exe -Label "PyInstaller clean-VM smoke"
```

6. 运行：

```powershell
pwsh -NoProfile -File packaging/build_nuitka_windows.ps1
```

这个脚本尝试用 Nuitka 构建 fallback 方案。

7. 如果 Nuitka 产物存在，也跑同样的 packaged smoke。
8. 把所有结果追加到：

```text
packaging/SPIKE-REPORT.md
```

9. 上传 artifacts：

```text
phase9-spike-report
cpho-pyinstaller-windows
cpho-nuitka-windows
```

## 5. artifact 是什么

GitHub Actions artifact 可以理解成“CI 跑完以后打包保存下来的文件”。

它不是 git commit，也不会自动改回仓库代码。它是某一次 CI 运行的输出附件。

本 spike 里最重要的 artifact 是：

```text
phase9-spike-report
```

它里面应该包含 CI 执行后填充过的 `SPIKE-REPORT.md`。这个文件比仓库里的模板更重要，因为模板只说明“要跑什么”，artifact 才记录“实际跑出来什么结果”。

如果构建成功，还会有：

```text
cpho-pyinstaller-windows
cpho-nuitka-windows
```

这些是打包产物。它们可以下载下来做人工检查。

## 6. 为什么同时测 PyInstaller 和 Nuitka

PyInstaller 和 Nuitka 都是 Python 打包工具，但思路不同。

### PyInstaller

PyInstaller 更像“把 Python 程序运行时需要的东西收集起来”。它通常更容易上手，适合先做 spike。

优点：

- Python CLI 项目常用。
- spec 文件可控。
- 比较容易显式收集数据文件。
- 对“先做出可运行产物”更友好。

风险：

- 产物可能比较大。
- 带二进制依赖的包有时需要手动 hidden import 或 collect DLL。
- onefile 模式可能有临时解压问题，所以现在先用 onedir。

### Nuitka

Nuitka 更像“把 Python 编译成 C/C++ 层面的程序再打包”。它可能带来更好的运行时表现，但配置成本通常更高。

优点：

- 可能有更好的启动或分发特性。
- 对某些项目可以生成更干净的独立目录。

风险：

- 对数据文件和复杂依赖的处理需要更细配置。
- 构建时间可能更长。
- spike 阶段更容易遇到工具链问题。

所以本阶段不是要争论哪个工具理论上更好，而是让 CI 用真实项目跑一遍，看哪个更接近“可以交付给用户”。

## 7. smoke 测试在测什么

Smoke test 可以理解成“冒烟测试”：不是完整测试所有功能，而是确认程序没有一启动就坏，关键依赖能加载，基础路径能跑通。

本项目的 packaged smoke 做几件事：

1. 跑：

```text
cpho --help
```

确认命令行入口能启动。

2. 跑：

```text
cpho diagnostics --packaging-smoke
```

确认这些关键东西能加载：

- package version
- 内置 skills
- vocabulary YAML
- model catalog JSON
- PyMuPDF 的 `fitz`
- RapidOCR
- ONNX Runtime

这一步很重要，因为一个包“能启动”不代表它“资源完整”。如果 prompt、词表、模型 catalog 没有被打包进去，用户后面运行功能会失败。

3. 跑：

```text
cpho index <中文嵌套路径> --dry-run
```

确认中文路径和最基础 workspace 逻辑能通过。

这对应真实用户工作空间的形状：真实资料目录里大量中文文件夹、空格、试题/解析 PDF，而不是简单的 ASCII 测试目录。

## 8. 如何读 CI 结果

CI 跑完以后，先看 workflow 总体是否成功。

但不要只看绿色或红色。更重要的是下载 `phase9-spike-report` artifact，读里面这些部分。

### PyInstaller result

重点看：

- exit code 是否为 0
- bundle size 是多少
- 是否生成 `dist/cpho/cpho.exe`
- PyInstaller smoke 是否通过

如果 PyInstaller 构建成功、smoke 通过，说明 Windows installer 方向有真实基础。

### Nuitka result

重点看：

- 是否成功构建
- 构建耗时是否明显过长
- 输出大小是否明显优于 PyInstaller
- smoke 是否通过

如果 Nuitka 失败但 PyInstaller 成功，不一定是坏事。Nuitka 在本阶段是 fallback/spike 对照，不是必须赢。

### Clean-VM smoke

重点看：

- `help` 是否 PASS
- `diagnostics` 是否 PASS
- `Chinese workspace dry-run` 是否 PASS

其中 `diagnostics` 是最关键的，因为它覆盖了打包最容易漏掉的运行时依赖和包内数据。

### Bundle size

体积大不是立即失败。

Phase 9 的前提是：功能完整性优先，体积可以接受。因为 ONNX Runtime、RapidOCR、PyMuPDF、本地 Python runtime 都会增加体积。

如果包是 300-500 MB，这在本项目里属于可预期范围。

真正需要担心的是：

- 体积异常大，比如超过 1 GB，且没有清楚原因。
- 体积虽然小，但 smoke 失败，说明依赖可能没打进去。

## 9. 三种决策分别代表什么

CI artifact 看完以后，才应该做下面三种决策之一。

### A. Recommendation: build-installer

含义：继续做 Windows 安装包。

适合条件：

- PyInstaller 或 Nuitka 至少一个能在 `windows-2022` 构建成功。
- 对应 packaged smoke 通过。
- 产物大小可接受。
- report 没有显示无法绕过的 DLL、资源缺失、启动失败问题。

下一步应该做：

1. 用成功路线作为主线，通常优先 PyInstaller。
2. 加 release workflow，把产物上传到 GitHub Releases。
3. 做 Inno Setup 或类似 installer 包装。
4. README 写清楚 Windows 下载、SmartScreen 提示、更新方式。

### B. Recommendation: fallback-docs

含义：暂时不做一键安装包，改成交付清晰的命令行安装文档。

适合条件：

- PyInstaller 和 Nuitka 都无法稳定构建。
- 或者构建成功但 packaged smoke 失败，且失败不是小修能解决。
- 或者产物需要复杂手工安装 VC Runtime / DLL，已经背离“普通用户下载即用”。

下一步应该做：

1. 提供 `pipx install` 或 `uv tool install` 路径。
2. README 给非技术用户写尽量清楚的步骤。
3. 暂时把 installer 放到后续版本。
4. 记录具体失败原因，避免以后重复踩坑。

这不是“放弃 Windows”，而是承认当前阶段的一键安装成本过高。

### C. Recommendation: continue-spike

含义：现有 CI 结果还不足以做最终判断，需要继续修打包脚本或 smoke。

适合条件：

- workflow 本身跑起来了，但因为脚本小错误失败。
- 构建失败原因看起来可修，比如缺 hidden import、漏 data file、路径写错。
- PyInstaller 或 Nuitka 已经接近成功，但还缺一两个明显修复。
- smoke 暴露了明确的小问题。

下一步应该做：

1. 根据 report 里的第一处失败修脚本。
2. 不要同时大改多个方向。
3. 再跑 CI。
4. 直到进入 `build-installer` 或 `fallback-docs` 的清晰状态。

## 10. 我建议你看到 CI 结果后怎么判断

可以按这个顺序问：

1. workflow 是否真正启动并上传了 `phase9-spike-report`？
   - 否：先修 GitHub Actions 触发/权限问题。
   - 是：继续。

2. PyInstaller 是否构建成功？
   - 是：优先看 PyInstaller smoke。
   - 否：看失败是不是可修的小问题。

3. PyInstaller smoke 是否通过？
   - 是：基本倾向 `build-installer`。
   - 否：看失败点是否是资源缺失、DLL 缺失、还是 CLI 逻辑问题。

4. Nuitka 是否明显比 PyInstaller 更好？
   - 如果没有明显优势，不要为了工具洁癖切换到 Nuitka。
   - spike 的目标是交付，不是证明某个打包器更高级。

5. 用户体验是否接近“一键运行”？
   - 如果仍要求用户安装很多系统依赖，就不算真正达标。

## 11. 当前最实际的下一步

因为 workflow 文件现在只在 `feature/phase9` 分支上，而 GitHub 手动 dispatch 找不到默认分支上的 workflow，下一步有两个务实选择。

### 选择 1：先把 workflow 合到默认分支

这是最干净的方式。

步骤：

1. 为 `feature/phase9` 创建 PR。
2. 审查 `.github/workflows/packaging-spike.yml`。
3. 合并到默认分支。
4. 再运行：

```bash
gh workflow run packaging-spike.yml --ref main
```

优点：

- 符合 GitHub Actions 的默认工作方式。
- 以后可以随时手动触发。
- workflow artifact 也更容易找。

缺点：

- 需要先把 workflow 文件合入主分支。

### 选择 2：保留在 PR 中，让 push/PR 触发已有默认分支 workflow

这个方式只有在默认分支上已经存在相关 workflow 时才可靠。

当前 `gh workflow list --all` 没有列出 workflow，所以这个仓库目前不像是已经有默认分支 Actions 配置。也就是说，仅靠 PR 不一定能触发新的 `packaging-spike.yml`。

因此我更建议选择 1：先让 workflow 文件进入默认分支，再手动 dispatch。

## 12. 不建议做什么

不建议在 macOS 本地模拟 Windows 打包结果。

原因：这会产生“看起来有报告，但没有真实 Windows 证据”的假安全感。

也不建议现在直接写 release installer。

原因：如果 spike 还没证明可构建、可 smoke、可上传 artifact，那么 release workflow 只会把不稳定问题放大。

## 13. 最终决策标准

可以用一句话总结：

```text
如果 Windows CI 能构建出产物，并且 packaged smoke 证明入口、依赖、包内数据、中文路径都能跑通，就继续 build-installer；否则根据失败是否可修，选择 continue-spike 或 fallback-docs。
```

对这个项目来说，最重要的不是安装包看起来像不像“正式产品”，而是物理竞赛教练下载后能不能真的打开、索引中文题库、运行核心功能。

所以 Phase 9 的正确顺序是：

```text
CI 真实构建 → artifact 报告 → 人工读报告 → 决策 → 再做 installer/release/docs
```
