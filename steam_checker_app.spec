# PyInstaller: pyinstaller steam_checker_app.spec
# Готовый exe: dist\SteamGameChecker\SteamGameChecker.exe
# При ошибках Qt добавьте: --collect-all PyQt6

from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas_pyqt, binaries_pyqt, hidden_pyqt = collect_all("PyQt6")

a = Analysis(
    ['steam_checker_app.py'],
    pathex=[],
    binaries=binaries_pyqt,
    datas=datas_pyqt,
    hiddenimports=hidden_pyqt,
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
    name='SteamGameChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    upx=True,
    upx_exclude=[],
    name='SteamGameChecker',
)
