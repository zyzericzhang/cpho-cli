from __future__ import annotations

from pathlib import Path


def test_windows_packaging_and_release_workflows_are_coherent() -> None:
    packaging = Path(".github/workflows/packaging-spike.yml").read_text(encoding="utf-8")
    release = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
    smoke = Path("packaging/smoke_packaged_windows.ps1").read_text(encoding="utf-8")

    assert "windows-2022" in packaging
    assert "smoke_packaged_windows.ps1" in packaging
    assert "diagnostics --packaging-smoke" in smoke
    assert "actions/upload-artifact@v4" in packaging
    assert "phase9-spike-report" in packaging

    assert "windows-2022" in release
    assert "tags:" in release
    assert '"v*"' in release
    assert "pull_request" not in release
    assert "branches:" not in release
    assert "packaging/build_windows.ps1" in release
    assert "packaging/build_nuitka_windows.ps1" not in release
    assert "packaging/installer.iss" in release
    assert "gh release upload" in release
    assert "contents: write" in release


def test_spike_report_and_release_checklist_record_pyinstaller_decision() -> None:
    report = Path("packaging/SPIKE-REPORT.md").read_text(encoding="utf-8")
    checklist = Path("packaging/RELEASE-CHECKLIST.md").read_text(encoding="utf-8")

    assert report.count("Recommendation:") == 1
    assert "Recommendation: build-installer" in report
    assert "PyInstaller bundle" in report
    assert "Nuitka timed out" in report
    assert "User approval recorded" in checklist
    assert "PyInstaller onedir" in checklist
    assert "SmartScreen" in checklist


def test_install_docs_match_phase9_platform_scope() -> None:
    install = Path("docs/user/install.md").read_text(encoding="utf-8")
    index = Path("docs/user/README.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "https://github.com/zyzericzhang/cpho-cli/releases/latest" in install
    assert "Mac Apple Silicon" in install
    assert "Intel Mac / fallback" in install
    assert "uv tool install git+https://github.com/zyzericzhang/cpho-cli" in install
    assert "disable Defender" not in install
    assert "不要为了运行 CPHO CLI 去关闭 Defender" in install
    assert "install.md" in index
    assert "docs/user/install.md" in readme
    assert "跨平台安装器。跨平台/安装包属于 Phase 9" not in readme


def test_update_check_artifacts_are_present() -> None:
    assert Path("src/cpho_cli/core/update_check.py").is_file()
    assert Path("src/cpho_cli/models/update.py").is_file()
    text = Path("tests/test_update_check.py").read_text(encoding="utf-8")
    assert "MockTransport" in text
    assert "test_version_command_prints_version_and_repository" in text
