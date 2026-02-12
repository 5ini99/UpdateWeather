# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img'), ('font', 'font'), ('legacy', 'legacy')],
    hiddenimports=['pystray', 'PIL', 'PIL.Image', 'PIL.ImageDraw', 'psutil', 'requests', 'hid'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='UpdateWeather',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.icns'],
)
app = BUNDLE(
    exe,
    name='UpdateWeather.app',
    icon='icon.icns',
    bundle_identifier=None,
)
