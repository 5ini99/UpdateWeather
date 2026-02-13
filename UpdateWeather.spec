# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('img', 'img'), ('font', 'font'), ('legacy', 'legacy')]
binaries = []
hiddenimports = ['pystray', 'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont', 'psutil', 'requests', 'hid', 'threading', 'configparser', 'tkinter', 'tkinter.simpledialog', 'tkinter.messagebox', 'tkinter.filedialog', 'datetime']
tmp_ret = collect_all('app')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='UpdateWeather',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='UpdateWeather',
)
app = BUNDLE(
    coll,
    name='UpdateWeather.app',
    icon='icon.icns',
    bundle_identifier=None,
)
