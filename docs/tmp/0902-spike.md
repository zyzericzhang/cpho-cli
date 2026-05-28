# Phase 09-02 Packaging Spike：最终决策分析

这份文档用中文从零解释本次 Windows 打包 spike 的结论。读者不需要先懂 Python 打包、GitHub Actions、Windows runner、artifact、PyInstaller 或 Nuitka。

## 1. 最终结论

结论：进入 `build-installer` 路线，主线选择 PyInstaller。

不要继续把 Nuitka 当成当前阶段的主线。Nuitka 可以保留为以后优化体积或性能时的研究项，但现在不应该阻塞 Windows 安装包。

本结论来自 GitHub Actions 的真实 Windows CI，不是本地 macOS 模拟。

最终依据：

- Workflow: `Packaging spike`
- Runner: `windows-2022`
- Run: https://github.com/zyzericzhang/cpho-cli/actions/runs/26589444663
- Commit: `2a50cacff92e6426cef45550fc5cf9ef591844da`
- Artifact: `phase9-spike-report`
- Artifact: `cpho-pyinstaller-windows`

最终 CI 报告里的关键结果：

```text
PyInstaller:
- Exit code: 0
- Elapsed: 49.7s
- Bundle size: 297.77 MB
- PASS help
- PASS diagnostics
- PASS Chinese workspace dry-run

Nuitka:
- Timeout: 10 minutes
- Exit code: 124
- Output size: 0 MB
- No executable produced
```

所以判断很直接：

```text
PyInstaller 已经能在 Windows CI 上构建并通过关键 smoke。
Nuitka 没有在合理 spike 时间内产出可执行文件。
下一步应该围绕 PyInstaller 做 Windows installer/release，而不是继续比较打包器。
```

## 2. 这次 spike 到底验证了什么

CPHO CLI 是 Python 命令行工具。开发者本机可以用 Python 和 uv 运行它，但普通 Windows 用户通常不想先安装 Python、配置虚拟环境、理解依赖包。

Phase 9 要解决的问题是：

```text
能不能给 Windows 用户一个可下载、可运行的程序？
```

这次 spike 不是要马上做出最终安装器，而是先验证更基础的问题：

```text
这个项目能不能在一台干净的 Windows CI 机器上被打包成可执行程序，并且启动后能跑关键命令？
```

这比“本地能跑”难很多，因为 CPHO CLI 依赖：

- Python 解释器本身
- PyMuPDF 的 `fitz`
- RapidOCR
- ONNX Runtime
- OpenCV、NumPy 等本地二进制依赖
- 项目自带的 prompts、skills、vocabulary、model catalog 等数据文件

如果这些东西漏打包，程序可能能生成 `.exe`，但用户一运行就会报错。

所以这次真正要看的是：

1. 能不能构建出 Windows 程序。
2. 程序能不能启动。
3. 程序能不能找到包内数据。
4. 程序能不能加载 OCR/ONNX/PyMuPDF 这类二进制依赖。
5. 程序能不能处理中文路径。

## 3. 为什么必须用 GitHub Actions 的 Windows runner

Windows 打包不能用 macOS 本地结果代替。

原因：

- Windows 程序是 `.exe`，macOS 不能真实执行。
- Windows 的动态链接库是 DLL，macOS 没有相同加载规则。
- Windows 文件路径、终端编码、中文路径行为和 macOS 不一样。
- PyInstaller 不是可靠的跨平台编译器，不能在 macOS 上证明 Windows 产物可用。

所以本次报告必须由 CI 填充，而不是本地 macOS 写一个看起来像结果的文件。

这次最终采用的证据链是：

```text
push 到 main
→ GitHub Actions 启动 windows-2022 runner
→ 在 Windows 上执行 build_windows.ps1
→ 在 Windows 上执行 smoke_packaged_windows.ps1
→ 上传 phase9-spike-report 和构建产物 artifact
→ 根据 artifact 做决策
```

## 4. PyInstaller 结果怎么理解

PyInstaller 的作用可以理解成：

```text
把 Python 程序、Python 解释器、依赖库、数据文件收集成一个可分发目录。
```

这次使用的是 `onedir` 形式，不是单个 `onefile`。

`onedir` 的意思是：用户会拿到一个目录，里面有 `cpho.exe` 和 `_internal` 依赖目录。

这对当前阶段是正确选择：

- 比 onefile 更容易调试。
- 不需要每次运行先解压到临时目录。
- 出问题时能看到 DLL 和数据文件是否存在。
- 后续可以被 Inno Setup 这类安装器包装。

最终 PyInstaller 结果：

```text
构建成功。
产物大小约 297.77 MB。
help 命令通过。
diagnostics 命令通过。
中文 workspace dry-run 通过。
```

297.77 MB 不小，但在这个项目里可以接受。原因是包里包含 Python runtime、PyMuPDF、ONNX Runtime、RapidOCR、OpenCV 等大依赖。

这个体积不应该阻止进入 installer 阶段。真正重要的是功能完整性。

## 5. smoke 测试说明了什么

Smoke test 可以理解成“冒烟测试”：它不覆盖所有业务功能，只确认程序没有一启动就坏。

本次 smoke 测了三类关键能力。

第一类：入口能启动。

```text
cpho --help
```

这证明打包后的 CLI 入口有效。

第二类：运行时依赖和包内数据完整。

```text
cpho diagnostics --packaging-smoke
```

它检查：

- package version
- builtin skills
- vocabulary YAML
- model catalog JSON
- PyMuPDF / fitz
- RapidOCR
- ONNX Runtime

这一步很关键。很多打包失败不是 `.exe` 不存在，而是 `.exe` 启动后找不到数据文件或 DLL。

第三类：中文路径能跑。

```text
cpho index <中文嵌套路径> --dry-run
```

这对应真实物理竞赛教练的工作区形状：大量中文目录、中文 PDF、空格和较深层级路径。

最终结果是三项都 PASS。

## 6. 过程中修过什么问题

这次 spike 暴露并修复了几个真实 Windows 问题。

第一，smoke 脚本一开始没有严格检查 `.exe` 的退出码。

这会导致程序明明退出 1，报告却写成 PASS。已经修复：现在 smoke 每一步都会检查 `$LASTEXITCODE`。

第二，Windows runner 默认终端编码导致中文 help 输出失败。

英文 Windows CI 默认编码不是 UTF-8。CPHO CLI 的 help 里包含中文命令说明，打包后的 `.exe` 在输出帮助时曾出现 `UnicodeEncodeError`。

已经做了两层修复：

- 关闭 Typer 的 Rich help 渲染，改用普通 Click help。
- Windows 上显式把 stdout/stderr 配成 UTF-8，并用 `replace` 避免编码异常直接杀掉进程。

第三，Nuitka 脚本一开始会因下载确认、空输出目录统计等问题让 workflow 红掉。

已经修复为：

- 自动允许 Nuitka 下载依赖工具。
- 给 Nuitka spike 设置 10 分钟上限。
- 即使 Nuitka 不适合作为打包路线，也把原因写进 report，而不是让 report 丢失。

这些修复都属于 spike 过程中应该做的初步修复：它们让 CI 结果可信，而不是掩盖失败。

## 7. Nuitka 为什么不作为当前主线

Nuitka 的理论目标是把 Python 编译到更底层的 C/C++ 路线，再生成分发产物。

它不一定不好，但对当前项目和当前阶段不合适。

本次 Windows CI 里，Nuitka 结果是：

```text
10 分钟超时。
没有产出可执行文件。
没有 smoke 可跑。
```

日志还显示它进入了 C 编译/Scons 阶段，并涉及大量包和二进制依赖处理。这说明它的调试成本明显高于 PyInstaller。

如果 PyInstaller 失败，那值得继续研究 Nuitka。但现在 PyInstaller 已经能构建并通过 smoke，继续投入 Nuitka 的收益不够明确。

所以决策是：

```text
Nuitka 暂停，不作为 v1.1 Windows installer 的主路径。
```

## 8. 下一步应该做什么

下一步不是继续 spike，而是把 PyInstaller 成功路线产品化。

建议顺序：

1. 保留 `packaging/build_windows.ps1` 和 `packaging/cpho.spec` 作为 Windows 构建主线。
2. 新增 release workflow，在打 tag 时构建 PyInstaller onedir 产物。
3. 把 onedir 产物先上传为 zip artifact/release asset。
4. 再用 Inno Setup 或同类工具把 onedir 包成安装器。
5. 在 README 里写清楚 Windows 下载、首次运行、SmartScreen 提示和卸载方式。
6. 在正式 release 前补一个 `version` 命令或调整 smoke，不要长期保留 `PENDING update command`。
7. 继续保留 `diagnostics --packaging-smoke`，它是以后防止打包回归的核心检查。

## 9. 还需要注意什么

### SmartScreen

未签名 Windows 程序可能出现 Microsoft Defender SmartScreen 提示。

这不是 PyInstaller 独有问题，而是新发布、低信誉、未签名 Windows 程序的常见问题。

v1.1 可以先文档说明，不要教用户全局关闭 Defender。后续如果要更正式分发，再评估代码签名证书。

### 体积

297.77 MB 对 CLI 来说偏大，但对含 OCR/ONNX/PyMuPDF 的离线工具来说可接受。

不要为了先把体积降到很小而牺牲可运行性。体积优化可以排在安装器成功之后。

### Windows compatibility workflow

同一次 push 触发的 `Windows compatibility` workflow 仍然失败，但失败点不是 PyInstaller 产物：

- notebook 文件名里包含 `:`，Windows 不允许这种文件名。
- REPL 测试在 GitHub Actions 非交互控制台里创建 prompt_toolkit 输出失败。

这些是 Windows 测试兼容性问题，应该单独排期修。它们不推翻本次 packaging spike 的结论，因为最终 packaged smoke 已经在 Windows runner 上通过。

## 10. 明确不建议做什么

不建议继续用 macOS 本地模拟 Windows 结果。

不建议现在切到 Nuitka。

不建议马上做复杂体积优化。

不建议先做漂亮安装器界面再补 smoke。安装器只是外壳，核心是里面的 `cpho.exe` 可运行。

## 11. 最终决策

最终决策如下：

```text
Recommendation: build-installer
Primary packaging route: PyInstaller onedir
Fallback route: documented uv/pipx install, only if installer later遇到无法接受的问题
Nuitka: pause for v1.1, revisit only after PyInstaller installer is usable
```

下一阶段的成功标准：

```text
Windows release workflow 能从 tag 构建 PyInstaller onedir；
产物被上传到 GitHub Releases；
安装器或 zip 下载后能运行 cpho --help、diagnostics、中文 workspace dry-run；
README 能让非技术用户按步骤完成下载和首次运行。
```
