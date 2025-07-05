# PyInstaller spec file for ArgusSight

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'azure.identity',
        'azure.monitor.query',
        'azure.core',
        # Add other hidden imports discovered during testing
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['config'],  # Exclude the config file from the bundle
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ArgusSight',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Create a console-based application
    icon=None
)
