# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs, collect_submodules


block_cipher = None
root = Path.cwd()
entrypoint = root / "build" / "pyinstaller_entry" / "cpho_entry.py"
entrypoint.parent.mkdir(parents=True, exist_ok=True)
entrypoint.write_text("from cpho_cli.cli.app import app\napp()\n", encoding="utf-8")

datas = []
binaries = []
hiddenimports = []

for package in ["cpho_cli", "rapidocr", "onnxruntime"]:
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

hiddenimports += collect_submodules("cpho_cli")
datas += collect_data_files("cpho_cli", include_py_files=False)
datas += [
    (str(root / "src" / "cpho_cli" / "builtin_skills"), "cpho_cli/builtin_skills"),
    (str(root / "src" / "cpho_cli" / "core" / "index" / "prompts"), "cpho_cli/core/index/prompts"),
    (str(root / "src" / "cpho_cli" / "core" / "splitting" / "prompts"), "cpho_cli/core/splitting/prompts"),
    (str(root / "src" / "cpho_cli" / "core" / "knowledge" / "prompts"), "cpho_cli/core/knowledge/prompts"),
    (str(root / "src" / "cpho_cli" / "vocabulary"), "cpho_cli/vocabulary"),
    (str(root / "src" / "cpho_cli" / "data" / "model_catalog"), "cpho_cli/data/model_catalog"),
]
binaries += collect_dynamic_libs("onnxruntime")

a = Analysis(
    [str(entrypoint)],
    pathex=[str(root / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="cpho",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="cpho",
)
