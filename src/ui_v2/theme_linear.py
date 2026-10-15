"""
Linear / Notion SaaS Tasarım Sistemi & QSS Teması.
Karanlık mod (Obsidian Dark), Linear mor vurgusu (#5e6ad2), Notion temiz tipografi düzeni
ve ultra-ince 1px sınır çizgileri.
"""

import os

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets")).replace("\\", "/")
CHEVRON_DOWN_SVG = f"{ASSETS_DIR}/chevron_down.svg"
CHEVRON_DOWN_HOVER_SVG = f"{ASSETS_DIR}/chevron_down_hover.svg"
CHECKMARK_SVG = f"{ASSETS_DIR}/checkmark.svg"

# -----------------------------------------------------------------------------
# RENK PALETİ (DESIGN TOKENS - LINEAR OBSIDIAN THEME)
# -----------------------------------------------------------------------------
BG_APP = "#0e0f12"              # En alt katman zemin rengi
BG_SIDEBAR = "#121318"          # Notion / Linear sol navigasyon paneli
BG_SURFACE = "#17181f"          # Kartlar, paneller, veri kutuları
BG_CARD = BG_SURFACE            # Kart zemin rengi (alias)
BG_SURFACE_HOVER = "#20222b"    # Fare üzerine gelme zemin rengi
BG_SURFACE_ACTIVE = "#282a36"   # Seçili öğe zemini

BORDER_SUBTLE = "#232530"       # 1px ultra-ince sınır çizgisi
BORDER_LIGHT = "#2f3242"        # Ayrıştırıcı çizgiler
BORDER_FOCUS = "#5e6ad2"        # Odaklanılan girdi kutusu sınırı (Linear Moru)

# Vurgular (Accents)
ACCENT_PRIMARY = "#5e6ad2"      # Linear ana buton ve eylem moru
ACCENT_PRIMARY_HOVER = "#6e79d6"
ACCENT_HOVER = ACCENT_PRIMARY_HOVER
ACCENT_PRIMARY_PRESSED = "#4f5bb8"
ACCENT_ACTIVE = ACCENT_PRIMARY_PRESSED
ACCENT_TEXT = "#ffffff"
COLOR_ACCENT = "#5e6ad2"        # Geriye dönük uyumluluk vurgusu

# Durum Renkleri (Badges & Status)
COLOR_SUCCESS = "#10b981"       # Yeşil (Geçerli / GOST Uyumlu)
COLOR_SUCCESS_BG = "#0d2b20"
COLOR_SUCCESS_BORDER = "#1b4d3a"

COLOR_WARNING = "#f59e0b"       # Sarı / Turuncu (Eksik Veri)
COLOR_WARNING_BG = "#2c1e0a"
COLOR_WARNING_BORDER = "#5c3e12"

COLOR_ERROR = "#ef4444"         # Kırmızı (Hata)
COLOR_ERROR_BG = "#2b1111"
COLOR_ERROR_BORDER = "#521d1d"

COLOR_INFO = "#3b82f6"          # Mavi (Bilgi / Bildirim)
COLOR_INFO_BG = "#0f2038"

# Metin Hiyerarşisi
TEXT_PRIMARY = "#f3f4f6"        # Ana başlıklar ve birincil metinler
TEXT_SECONDARY = "#9ca3af"      # İkincil etiketler, açıklamalar
TEXT_MUTED = "#646979"          # Pasif durumdaki kısayollar, ipuçları
TEXT_ACCENT = "#818cf8"         # Mor linkler ve vurgular

# CAD Çizim Alanı
COLOR_CAD_BG = "#0a0b0e"        # CAD sonsuz uzay zemin rengi
COLOR_CAD_GRID = "#1a1c24"      # CAD arka plan grid çizgileri
COLOR_CAD_PAPER = "#f8fafc"     # Beyaz mühendislik pafta kağıdı


def get_linear_stylesheet() -> str:
    """
    Tüm uygulamaya uygulanan Linear / Notion SaaS global QSS stil sayfası.
    """
    return f"""
    /* --- GENEL PENCERE VE WIDGET YAPISI --- */
    QMainWindow, QWidget {{
        background-color: {BG_APP};
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', Roboto, sans-serif;
        font-size: 13px;
        selection-background-color: {ACCENT_PRIMARY};
        selection-color: #ffffff;
    }}

    /* --- SPLITTER (PANEL AYIRICILAR) --- */
    QSplitter::handle {{
        background-color: {BG_SURFACE};
    }}
    QSplitter::handle:horizontal {{
        width: 6px;
        background-color: {BG_SURFACE};
        border-left: 1px solid {BORDER_SUBTLE};
        border-right: 1px solid {BORDER_SUBTLE};
    }}
    QSplitter::handle:vertical {{
        height: 6px;
        background-color: {BG_SURFACE};
        border-top: 1px solid {BORDER_SUBTLE};
        border-bottom: 1px solid {BORDER_SUBTLE};
    }}
    QSplitter::handle:horizontal:hover, QSplitter::handle:vertical:hover {{
        background-color: {ACCENT_PRIMARY};
        border-color: {ACCENT_PRIMARY_HOVER};
    }}

    /* --- BUTONLAR (LINEAR STİLİ) --- */
    QPushButton {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 6px;
        padding: 5px 12px;
        font-weight: 500;
        font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: {BG_SURFACE_HOVER};
        border-color: {BORDER_LIGHT};
    }}
    QPushButton:pressed {{
        background-color: {BG_SURFACE_ACTIVE};
    }}
    QPushButton:disabled {{
        background-color: transparent;
        color: {TEXT_MUTED};
        border-color: transparent;
    }}

    /* Birincil Eylem Butonu (Primary Action) */
    QPushButton#primaryButton {{
        background-color: {ACCENT_PRIMARY};
        color: #ffffff;
        border: 1px solid {ACCENT_PRIMARY};
        font-weight: 600;
    }}
    QPushButton#primaryButton:hover {{
        background-color: {ACCENT_PRIMARY_HOVER};
        border-color: {ACCENT_PRIMARY_HOVER};
    }}
    QPushButton#primaryButton:pressed {{
        background-color: {ACCENT_PRIMARY_PRESSED};
    }}

    /* Ghost / İkon Butonu */
    QPushButton#ghostButton {{
        background-color: transparent;
        border: none;
        color: {TEXT_SECONDARY};
        padding: 4px 8px;
    }}
    QPushButton#ghostButton:hover {{
        background-color: {BG_SURFACE_HOVER};
        color: {TEXT_PRIMARY};
    }}

    /* --- ONAY KUTULARI (QCHECKBOX) --- */
    QCheckBox {{
        color: {TEXT_PRIMARY};
        spacing: 8px;
        font-size: 12px;
    }}
    QCheckBox:hover {{
        color: #ffffff;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid {BORDER_LIGHT};
        background-color: {BG_SURFACE};
    }}
    QCheckBox::indicator:hover {{
        border-color: {ACCENT_PRIMARY};
        background-color: {BG_SURFACE_HOVER};
    }}
    QCheckBox::indicator:checked {{
        border-color: {ACCENT_PRIMARY};
        background-color: {ACCENT_PRIMARY};
        image: url({CHECKMARK_SVG});
    }}
    QCheckBox::indicator:checked:hover {{
        border-color: {ACCENT_PRIMARY_HOVER};
        background-color: {ACCENT_PRIMARY_HOVER};
    }}
    QCheckBox::indicator:disabled {{
        border-color: {BORDER_SUBTLE};
        background-color: {BG_APP};
    }}

    /* --- METİN GİRDİLERİ (QLINEEDIT & QCOMBOBOX) --- */
    QLineEdit {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 12px;
    }}
    QLineEdit:focus {{
        border: 1px solid {BORDER_FOCUS};
        background-color: {BG_APP};
    }}
    QComboBox {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 6px;
        padding: 4px 26px 4px 10px;
        min-height: 22px;
        font-size: 12px;
    }}
    QComboBox:hover {{
        background-color: {BG_SURFACE_HOVER};
        border-color: {BORDER_LIGHT};
    }}
    QComboBox:focus, QComboBox:on {{
        border: 1px solid {BORDER_FOCUS};
        background-color: {BG_SURFACE_HOVER};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 22px;
        border-left: none;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }}
    QComboBox::down-arrow {{
        image: url({CHEVRON_DOWN_SVG});
        width: 10px;
        height: 10px;
        margin-right: 6px;
    }}
    QComboBox::down-arrow:hover {{
        image: url({CHEVRON_DOWN_HOVER_SVG});
    }}
    QComboBox QAbstractItemView,
    QComboBox QListView {{
        background-color: {BG_SURFACE};
        border: 1px solid {BORDER_LIGHT};
        selection-background-color: {BG_SURFACE_ACTIVE};
        selection-color: #ffffff;
        color: {TEXT_PRIMARY};
        padding: 4px;
        border-radius: 6px;
        outline: 0px;
    }}
    QComboBox QAbstractItemView::item,
    QComboBox QListView::item {{
        min-height: 26px;
        padding: 4px 8px;
        border-radius: 4px;
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
    }}
    QComboBox QAbstractItemView::item:hover,
    QComboBox QListView::item:hover {{
        background-color: {BG_SURFACE_HOVER};
        color: #ffffff;
    }}
    QComboBox QAbstractItemView::item:selected,
    QComboBox QListView::item:selected {{
        background-color: {BG_SURFACE_ACTIVE};
        color: #ffffff;
    }}

    /* --- TABLOLAR (NOTION DATABASE GRİD STİLİ) --- */
    QTableWidget, QTableView {{
        background-color: {BG_APP};
        color: {TEXT_PRIMARY};
        gridline-color: {BORDER_SUBTLE};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 6px;
        font-size: 13px;
        outline: none;
    }}
    QTableWidget::item {{
        padding: 6px 8px;
        border: none;
        font-size: 13px;
    }}
    QTableWidget::item:hover {{
        background-color: {BG_SURFACE_HOVER};
    }}
    QTableWidget::item:selected {{
        background-color: {BG_SURFACE_ACTIVE};
        color: #ffffff;
    }}
    QTableWidget QLineEdit {{
        background-color: {BG_SURFACE_ACTIVE};
        color: #ffffff;
        font-size: 13px;
        font-weight: 500;
        padding: 2px 8px;
        border: 1.5px solid {ACCENT_PRIMARY};
        border-radius: 4px;
        selection-background-color: {ACCENT_PRIMARY};
        selection-color: #ffffff;
    }}
    QTableWidget QComboBox {{
        font-size: 12px;
        padding: 2px 6px;
        border-radius: 4px;
    }}

    /* Tablo Başlıkları (Notion Column Headers) */
    QHeaderView::section {{
        background-color: {BG_SIDEBAR};
        color: {TEXT_MUTED};
        padding: 6px 8px;
        border: none;
        border-bottom: 1px solid {BORDER_SUBTLE};
        border-right: 1px solid {BORDER_SUBTLE};
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}

    /* --- KAYDIRMA ÇUBUKLARI (ULTRA-SLIM MINIMALIST SCROLLBARS) --- */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER_LIGHT};
        min-height: 24px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        border: none;
        background: transparent;
        height: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER_LIGHT};
        min-width: 24px;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {TEXT_MUTED};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* --- ETİKETLER VE ÇERÇEVELER --- */
    QLabel {{
        background: transparent;
        color: {TEXT_PRIMARY};
    }}
    QFrame#cardFrame {{
        background-color: {BG_SURFACE};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 8px;
    }}
    QFrame#sidebarFrame {{
        background-color: {BG_SIDEBAR};
        border-right: 1px solid {BORDER_SUBTLE};
    }}

    /* --- TOOLTIP & POPUP MENÜ --- */
    QToolTip {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_LIGHT};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 11px;
    }}
    QMenu {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_LIGHT};
        border-radius: 6px;
        padding: 4px 0px;
    }}
    QMenu::item {{
        padding: 6px 16px;
        border-radius: 4px;
        margin: 1px 4px;
    }}
    QMenu::item:selected {{
        background-color: {BG_SURFACE_ACTIVE};
        color: #ffffff;
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {BORDER_SUBTLE};
        margin: 4px 8px;
    }}
    """
