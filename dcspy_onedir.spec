# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

files = [(f'dcspy/{res}', 'dcspy') for res in  ['config.yaml', 'qtgui_rc.py']]
images = [(f'dcspy/img/{res}', 'dcspy/img') for res in ['splash.png', 'dcspy_white.ico', 'dcspy_black.ico']]
resources = [(f'dcspy/resources/{res}', 'dcspy/resources') for res in ['falconded.ttf', 'license.txt']]
headers = [(f'dcspy/sdk/{head}', 'dcspy/sdk') for head in ['LogitechLCDLib.h', 'LogitechLEDLib.h', 'LogitechGkeyLib.h']]
__version__ = '3.0.0-rc1'
block_cipher = None


a = Analysis(
    ['dcs_py.py'],
    pathex=[],
    binaries=[],
    datas=files + images + resources + headers,
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
    'dcspy/img/new_splash.png',
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
    name=f'dcspy_{__version__}',
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
    icon=['dcspy/img/dcspy_white.ico'],
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
