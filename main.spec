# -*- mode: python ; coding: utf-8 -*-

# 打包模式為單一執行檔（onefile）：dist/EpubConv.exe。
# config.ini 不打包進 exe，需放在 EpubConv.exe 旁邊（config/config.py 會切換到 exe 所在目錄讀取）。
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='EpubConv',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='epub.ico',
    version='file_version_info.txt',
)
