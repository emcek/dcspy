# -*- mode: python ; coding: utf-8 -*-
import sys
import os
os.environ["TCL_LIBRARY"] = os.path.join(sys.base_prefix, "tcl", "tcl8.6")
os.environ["TK_LIBRARY"] = os.path.join(sys.base_prefix, "tcl", "tk8.6")

from PyInstaller.utils.hooks import collect_data_files

images = [(f'src/dcspy/img/{res}', 'dcspy/img') for res in ['splash.png', 'dcspy_white.ico', 'dcspy_black.ico']]
resources = [(f'src/dcspy/resources/{res}', 'dcspy/resources') for res in ['falconded.ttf', 'license.txt', 'AH-64D_BLK_II.yaml', 'AV8BNA.yaml', 'F-4E-45MC.yaml', 'F-14A-135-GR.yaml', 'F-14B.yaml',
                                                                       'F-15ESE.yaml', 'F-16C_50.yaml', 'FA-18C_hornet.yaml', 'Ka-50.yaml', 'Ka-50_3.yaml', 'config.yaml',]]
headers = [(f'src/dcspy/resources/{head}', 'dcspy/resources') for head in ['LogitechLCDLib.h', 'LogitechLEDLib.h', 'LogitechGkeyLib.h']]
block_cipher = None


a = Analysis(
    ['src/dcs_py.py'],
    pathex=[],
    binaries=[],
    datas=images + resources + headers,
    hiddenimports=[],
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
splash = Splash(
    'src/dcspy/img/splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    [],
    exclude_binaries=True,
    name='dcspy_pyinstaller',
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
    version='file_version_info.txt',
    icon=['src/dcspy/img/dcspy_white.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dcs_py',
)
