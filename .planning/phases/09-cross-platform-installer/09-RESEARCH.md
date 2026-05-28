# Phase 09: cross-platform-installer - Research

**Gathered:** 2026-05-28
**Status:** Ready for planning
**Scope:** INSTALLER-01, INSTALLER-02, INSTALLER-03

## Research Question

What needs to be true before planning Phase 9 so CPHO CLI can be verified on Windows, packaged for non-technical Windows users, and documented for Mac users without drifting away from the real physics-coach workspace?

## Inputs Checked

- `.planning/phases/09-cross-platform-installer/09-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `pyproject.toml`
- `src/cpho_cli/cli/app.py`
- `src/cpho_cli/cli/repl/app.py`
- `src/cpho_cli/core/ocr.py`
- `src/cpho_cli/core/boundary.py`
- `README.md`
- Real workspace sample: `/Users/ericzhang/Desktop/物理竞赛资料`

## Real Workspace Findings

The real coach workspace is not a small flat fixture. A quick inventory found:

- `pdf=1018`
- `jpg=8`
- `docx=7`
- `other=43`
- Chinese directory and file names are normal, including spaces, punctuation, `试题`, `解析`, `答案`, `扫描全能王`, and year/vendor folders.

Phase 9 tests should therefore avoid assuming ASCII paths, flat directories, or only one problem file. CI cannot use the private workspace, but smoke scripts should accept a real workspace path when available and generated tests should include Chinese names and nested folders.

## Upstream Documentation Findings

### PyInstaller

PyInstaller is the best first spike target because it directly supports spec-file driven builds, onedir/onefile outputs, hidden imports, data collection, binary collection, and package-wide collection. Official docs list `--collect-data`, `--collect-binaries`, and `--collect-all`, which map directly to this project because `cpho_cli` ships prompt templates, skill YAML, vocabulary YAML, and model catalog JSON as package data.

Important implications:

- Prefer `--onedir` during spike and smoke testing. It keeps package data inspectable and avoids onefile temp extraction issues.
- Disable UPX on Windows. PyInstaller docs note UPX is Windows-focused and can corrupt collected shared libraries; this project has `onnxruntime` binaries and PyMuPDF native extensions, so size optimization should not be the first priority.
- Build on the target OS. PyInstaller is not a cross-compiler, so Windows artifacts need a Windows runner.

Source: https://www.pyinstaller.org/en/stable/usage.html

### Nuitka

Nuitka remains a credible fallback, but it needs explicit treatment of data files and package data. Its docs distinguish code from data and provide `--include-package-data`, `--include-data-files`, and `--include-data-dir`. That makes it suitable for the spike report, but not the lowest-risk first implementation path for this package-data-heavy CLI.

Source: https://nuitka.net/user-documentation/user-manual.html

### PyMuPDF

PyMuPDF has official wheels for Windows x86/x64 and macOS Intel/ARM. The current project only supports Python `>=3.11`, and PyMuPDF docs state their wheels use a stable ABI and work with supported Python versions. Windows failures may still require the latest VC runtime, so clean-VM smoke should import PyMuPDF and open a tiny PDF, not just run `cpho --help`.

Source: https://pymupdf.readthedocs.io/en/latest/installation.html

### ONNX Runtime / RapidOCR

`onnxruntime` is the critical binary dependency under RapidOCR. Official ONNX Runtime docs call out that Windows builds require the Visual C++ 2019 runtime, latest recommended. The installer spike must verify whether the PyInstaller bundle carries enough runtime DLLs or whether the installer must ship/check VC runtime prerequisites.

Source: https://onnxruntime.ai/docs/install/

### pipx and uv fallback paths

`pipx install PACKAGE` installs a Python CLI into its own virtual environment and exposes entry points on PATH, which is a clean fallback for technical users. `uv tool install` provides a similar tool-install path and uv itself has official install paths for macOS, Windows, Homebrew, WinGet, Scoop, and GitHub Releases.

Sources:

- https://pipx.pypa.io/latest/tutorial/install-applications/
- https://docs.astral.sh/uv/
- https://docs.astral.sh/uv/getting-started/installation/

### GitHub Releases

GitHub CLI supports `gh release upload <tag> <files>...`, which is enough for release workflow upload without adding a third-party marketplace action. The workflow should use `contents: write` and avoid `--clobber` unless the release job is explicitly retrying a failed draft.

Source: https://cli.github.com/manual/gh_release_upload

### Windows SmartScreen

Microsoft's current SmartScreen docs say SmartScreen uses publisher reputation and file hash reputation. A valid OV/EV certificate can still show an unrecognized-app warning until reputation accumulates, and EV no longer gives automatic first-download bypass. For v1.1, the plan should document the warning honestly and avoid telling users to disable Defender globally.

Source: https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation

## Project-Specific Technical Findings

### Current Entry Point

`pyproject.toml` exposes:

```toml
[project.scripts]
cpho = "cpho_cli.cli.app:app"
```

For PyInstaller, the executable entry can be a tiny wrapper script that imports `cpho_cli.cli.app:app`, or a spec-file entry against a generated `packaging/entrypoints/cpho.py`.

### Package Data That Must Be Bundled

The current package data includes:

- `src/cpho_cli/builtin_skills/**`
- `src/cpho_cli/core/index/prompts/*`
- `src/cpho_cli/core/splitting/prompts/*`
- `src/cpho_cli/core/knowledge/prompts/*`
- `src/cpho_cli/vocabulary/**/*.yml`
- `src/cpho_cli/data/model_catalog/*`

The spike must include a packaged smoke that reads these resources through the same runtime paths the app uses. A packaged binary that starts but cannot find prompts is a false pass.

### Windows Compatibility Hotspots

- `prompt_toolkit` REPL: needs Windows Terminal smoke for prompt startup, command dispatch, and Unicode display.
- `Rich` and manual ANSI output: REPL display uses ANSI constants and `wcwidth`; smoke should verify Chinese table rendering does not misalign or crash.
- `Path.resolve()` and `relative_to()`: `core/boundary.py` should be tested on Windows paths and nested Chinese paths.
- PyMuPDF: import and one-page PDF read smoke.
- RapidOCR/ONNX: instantiate `RapidOCRProvider` on an image fixture or a real workspace image/PDF when available.
- `httpx`: update checks and GitHub API release checks must use short timeouts and never block REPL startup.

### Roadmap / Context Conflict

`ROADMAP.md` still says spike success produces `.dmg + .exe/.msi`. `09-CONTEXT.md` is newer and more specific: Windows gets a full `.exe` installer, Mac gets documented Homebrew/command-line installation, Apple Silicon only for the easy path, and Intel Mac uses pipx docs. The plan should follow `09-CONTEXT.md` and document this as an intentional scope decision.

## Recommended Planning Shape

1. Windows compatibility baseline first: add CI and smoke tests before packaging.
2. Packaging spike second: produce `packaging/cpho.spec`, smoke scripts, size report, PyInstaller vs Nuitka comparison, and SmartScreen/signing risk.
3. Insert an explicit user decision gate after the spike. `D-13` says the user must personally review the spike report before deciding.
4. Add update-checking and release metadata before shipping installers, because the packaged binary needs a stable version and release URL.
5. Deliver Windows installer automation only after the spike passes.
6. Deliver Mac and fallback docs as a separate closeout so README stays coherent even if Windows packaging needs a follow-up.

## Recommendation

Plan PyInstaller `--onedir` plus an Inno Setup wrapper as the primary Windows path, keep Nuitka as a measured fallback in the spike, and document pipx/uv tool install as the fallback path. Do not plan a macOS `.dmg` in this phase unless the user reverses the Phase 9 context decision.

## Open Risks for Execution

- Windows runner smoke is not a true "clean VM with a non-technical user's desktop" unless the plan adds a separate clean-VM/manual smoke script and records the result.
- SmartScreen warnings cannot be eliminated by simply paying for EV signing; documentation must set expectations.
- The real workspace is large and private, so automated CI needs synthetic fixtures, while local/manual smoke scripts should allow running against `/Users/ericzhang/Desktop/物理竞赛资料`.
- Current README still points at `your-org/cpho-cli`; update checking and release links should use the actual git remote `zyzericzhang/cpho-cli`.

## RESEARCH COMPLETE

