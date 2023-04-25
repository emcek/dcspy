# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['dcspy\\run.py'],
    pathex=[],
    binaries=[],
    datas=[('venv311/Lib/site-packages/customtkinter', 'customtkinter'),
           ('venv311/Lib/site-packages/CTkMessagebox', 'CTkMessagebox'),
           ('dcspy/dcspy.ico', '.'),
           ('dcspy/dcspy_white.ico', '.'),
           ('dcspy/config.yaml', 'dcspy'),
           ('dcspy/falconded.ttf', 'dcspy'),
           ('dcspy/dcspy.png', 'dcspy'),
           ('dcspy/G13.png', 'dcspy'),
           ('dcspy/G19.png', 'dcspy'),
           ('dcspy/G510.png', 'dcspy'),
           ('dcspy/G15v1.png', 'dcspy'),
           ('dcspy/G15v2.png', 'dcspy'),
           ('dcspy/license.txt', 'dcspy')],
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DCSpy',
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
    icon=['dcspy\\dcspy.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dcspy',
)
