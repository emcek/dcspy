# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

img = ['dcspy.ico', 'dcspy_white.ico', 'dcspy.png', 'splash.png', 'G13.png', 'G19.png', 'G510.png', 'G15v1.png', 'G15v2.png', 'G13device.png', 'G19device.png', 'G510device.png', 'G15v1device.png', 'G15v2device.png']
resource = ['falconded.ttf', 'license.txt']
logi_sdk = ['LogitechLCDLib.h', 'LogitechLEDLib.h', 'LogitechGkeyLib.h']

files = [(f'dcspy/{res}', 'dcspy') for res in  ['config.yaml']]
images = [(f'dcspy/img/{res}', 'dcspy/img') for res in img]
resources = [(f'dcspy/resources/{res}', 'dcspy/resources') for res in resource]
headers = [(f'dcspy/sdk/{head}', 'dcspy/sdk') for head in logi_sdk]
gui_packages = collect_data_files('customtkinter') + collect_data_files('CTkMessagebox')
__version__ = '3.0.0'
block_cipher = None


a = Analysis(
    ['dcs_py.py'],
    pathex=[],
    binaries=[],
    datas=files + images + resources + headers + gui_packages,
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
    'dcspy/img/splash.png',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    splash,
    splash.binaries,
    [],
    name=f'dcspy_{__version__}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    icon=['dcspy/img/dcspy.ico'],
)
