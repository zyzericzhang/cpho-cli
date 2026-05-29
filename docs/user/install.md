# 安装

## Windows

适合不熟悉命令行的用户。

1. 打开最新版本下载页：<https://github.com/zyzericzhang/cpho-cli/releases/latest>
2. 下载 `cpho-cli-<version>-windows-x64-setup.exe`。
3. 双击安装器。
4. 从开始菜单打开 `CPHO CLI`，或在终端运行 `cpho --help`。

第一次运行时，Windows 可能显示 Microsoft Defender SmartScreen 提示。这通常是因为新发布的软件还没有足够下载信誉，不代表一定有病毒。看到提示时，点 `More info`，再点 `Run anyway`。不要为了运行 CPHO CLI 去关闭 Defender 或关闭系统安全保护。

Windows 安装器由 GitHub Actions 在 `windows-2022` runner 上构建。开发阶段不需要你在 Mac 上安装 Windows 打包工具，也不需要本地跑 PyInstaller。

## Mac Apple Silicon

适合 M1/M2/M3 芯片的 Mac。

先安装 Homebrew，然后安装 uv：

```bash
brew install uv
```

再安装 CPHO CLI：

```bash
uv tool install git+https://github.com/zyzericzhang/cpho-cli
```

更新时重新运行：

```bash
uv tool upgrade cpho-cli
```

v1.1 不提供 `.dmg`。这是有意选择：Mac 用户继续走命令行安装路径，Windows 用户走图形安装器。

## Intel Mac / fallback

Intel Mac 或 Homebrew 路径不顺时，使用 uv 或 pipx。

uv：

```bash
uv tool install git+https://github.com/zyzericzhang/cpho-cli
```

pipx：

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install git+https://github.com/zyzericzhang/cpho-cli
```

验证安装：

```bash
cpho --help
cpho diagnostics --packaging-smoke
```
