# -*- mode: python ; coding: utf-8 -*-
"""
KM Layout Tables Studio - PyInstaller Spec Dosyası.
GOST Standartlarında Çelik Konstrüksiyon CAD Tabloları Stüdyosu.
"""
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# QtAwesome font ve harita dosyalarını topla
qtawesome_datas = collect_data_files('qtawesome')

# Proje kaynak dosyaları ve varlıkları
datas = [
    ('src/config/standards_library.json', 'src/config'),
    ('src/ui_v2/assets/chevron_down.svg', 'src/ui_v2/assets'),
    ('src/ui_v2/assets/chevron_down_hover.svg', 'src/ui_v2/assets'),
    ('src/ui_v2/assets/zadax_logo.png', 'src/ui_v2/assets'),
    ('assets/app_icon.ico', 'assets'),
    ('assets/app_icon.png', 'assets'),
    ('assets/zadax_logo.png', 'assets'),
] + qtawesome_datas

# Dinamik yüklenen tüm alt modülleri dahil et
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'ezdxf',
    'qtawesome',
    'PIL',
    'PIL.Image',
] + collect_submodules('src')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'unittest', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 1. Klasör tabanlı dağıtım için EXE (Hızlı açılış)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KM-Layout-Tables',
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
    icon='assets/app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='KM-Layout-Tables-v1.2.0-win64',
)

# 2. Tek parça Standalone EXE (Tek dosya doğrudan çalıştırma)
exe_standalone = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KM-Layout-Tables-v1.2.0-Standalone',
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
    icon='assets/app_icon.ico',
)

