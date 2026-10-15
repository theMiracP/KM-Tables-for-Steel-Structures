# -*- mode: python ; coding: utf-8 -*-
"""
KM Layout Tables Studio - PyInstaller Spec Dosyası.
GOST Standartlarında Çelik Konstrüksiyon CAD Tabloları Stüdyosu.
"""
import os
import sys

# Proje dizinini sys.path'e ekle
BASE_DIR = os.path.abspath('.')
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.version import APP_VERSION
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# QtAwesome ve python-docx veri dosyalarını topla
qtawesome_datas = collect_data_files('qtawesome')
docx_datas = collect_data_files('docx')

# Proje kaynak dosyaları ve varlıkları
datas = [
    ('src/config/standards_library.json', 'src/config'),
    ('src/config/gost_profiles.json', 'src/config'),
    ('src/config/custom_profiles.json', 'src/config'),
    ('src/ui_v2/assets/checkmark.svg', 'src/ui_v2/assets'),
    ('src/ui_v2/assets/chevron_down.svg', 'src/ui_v2/assets'),
    ('src/ui_v2/assets/chevron_down_hover.svg', 'src/ui_v2/assets'),
    ('src/ui_v2/assets/flag_en.svg', 'src/ui_v2/assets'),
    ('src/ui_v2/assets/flag_ru.svg', 'src/ui_v2/assets'),
    ('src/ui_v2/assets/flag_tr.svg', 'src/ui_v2/assets'),
    ('src/ui_v2/assets/zadax_logo.png', 'src/ui_v2/assets'),
    ('assets/app_icon.ico', 'assets'),
    ('assets/app_icon.png', 'assets'),
    ('assets/zadax_logo.png', 'assets'),
] + qtawesome_datas + docx_datas

# Dinamik yüklenen tüm alt modülleri dahil et
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    'PySide6.QtPrintSupport',
    'ezdxf',
    'pyparsing',
    'unittest',
    'qtawesome',
    'PIL',
    'PIL.Image',
    'docx',
] + collect_submodules('docx') + collect_submodules('src')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'tkinter'],
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
    name=f'KM-Layout-Tables-v{APP_VERSION}-win64',
)

# 2. Tek parça Standalone EXE (Tek dosya doğrudan çalıştırma)
exe_standalone = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f'KM-Layout-Tables-v{APP_VERSION}-Standalone',
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

