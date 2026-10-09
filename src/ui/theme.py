"""
KM Tablo Oluşturucu - Spotify Dark & Neon Green Tasarım Sistemi (theme.py).
Masaüstü Spotify stili: Pitch Black zemin (#000000), yuvarlatılmış kartlar (#121212),
Spotify Neon Yeşili (#1ed760) vurguları ve hap (pill) butonlar.
"""
import os

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui_v2", "assets")).replace("\\", "/")
CHEVRON_DOWN_SVG = f"{ASSETS_DIR}/chevron_down.svg"

# ==============================================================================
# 1. TEMEL MÜHENDİSLİK PALETİ (Test Uyumluluk Sabitleri)
# ==============================================================================
COLOR_BG_DARK = "#1E1E1E"
COLOR_PANEL_BG = "#252526"
COLOR_PANEL_ALT = "#1F1F1F"
COLOR_PANEL_HOVER = "#2D2D30"
COLOR_BORDER = "#3E3E42"
COLOR_BORDER_LIGHT = "#4E4E52"

COLOR_TEXT_PRIMARY = "#D4D4D4"
COLOR_TEXT_MUTED = "#9D9D9D"
COLOR_TEXT_DIM = "#6E6E6E"

COLOR_ACCENT = "#0E639C"
COLOR_ACCENT_HOVER = "#1177BB"
COLOR_ACCENT_MUTED = "#264F78"
COLOR_CYAN = "#06B6D4"

# UI v2 Uyumluluk sabitleri
BG_SURFACE = "#17181f"
BG_SURFACE_ACTIVE = "#282a36"
BORDER_SUBTLE = "#232530"

COLOR_SUCCESS = "#4EC9B0"
COLOR_SUCCESS_BG = "#143522"
COLOR_SUCCESS_BORDER = "#1B4D3A"
COLOR_WARNING = "#D7BA7D"
COLOR_DANGER = "#F14C4C"
COLOR_DANGER_BG = "#381E1E"
COLOR_DANGER_BORDER = "#722525"

COLOR_CAD_BG = "#141414"
COLOR_CAD_PAPER = "#FFFFFF"
COLOR_CAD_FRAME = "#000000"
COLOR_CAD_GRID = "#1B1F27"

# ==============================================================================
# 2. SPOTIFY DARK & NEON GREEN DESIGN TOKENS
# ==============================================================================
SPOTIFY_BG = "#000000"              # Dış zemin (Pitch Black)
SPOTIFY_PANEL = "#121212"           # Spotify kartları ve paneller
SPOTIFY_SURFACE = "#181818"         # İkincil kartlar, butonlar
SPOTIFY_HOVER = "#242424"           # Hover
SPOTIFY_BORDER = "#222222"          # İnce sınır
SPOTIFY_GREEN = "#1ED760"           # Spotify Neon Yeşili
SPOTIFY_GREEN_HOVER = "#1FDF64"
SPOTIFY_GREEN_DARK = "#143522"
SPOTIFY_WHITE = "#FFFFFF"
SPOTIFY_MUTED = "#B3B3B3"


# ==============================================================================
# 3. SPOTIFY DARK QSS STİL SAYFASI
# ==============================================================================
QSS_DARK_THEME = f"""
/* Genel Pencere ve Zemin */
QMainWindow, QDialog {{
    background-color: {SPOTIFY_BG};
    color: {SPOTIFY_WHITE};
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Circular", sans-serif;
    font-size: 11px;
}}

QWidget {{
    color: {SPOTIFY_WHITE};
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Circular", sans-serif;
}}

/* Native Menü Çubuğu (QMenuBar & QMenu) */
QMenuBar {{
    background-color: {SPOTIFY_BG};
    color: {SPOTIFY_MUTED};
    border-bottom: 1px solid {SPOTIFY_BORDER};
    padding: 3px 6px;
    font-size: 11px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 3px 8px;
    border-radius: 2px;
}}

QMenuBar::item:selected {{
    background-color: {SPOTIFY_SURFACE};
    color: #FFFFFF;
}}

QMenuBar::item:pressed {{
    background-color: {SPOTIFY_GREEN_DARK};
    color: {SPOTIFY_GREEN};
}}

QMenu {{
    background-color: {SPOTIFY_PANEL};
    color: {SPOTIFY_WHITE};
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 6px 0px;
    font-size: 11px;
}}

QMenu::item {{
    padding: 6px 24px 6px 16px;
    border-radius: 2px;
    margin: 1px 4px;
}}

QMenu::item:selected {{
    background-color: {SPOTIFY_HOVER};
    color: {SPOTIFY_GREEN};
}}

QMenu::separator {{
    height: 1px;
    background-color: {SPOTIFY_BORDER};
    margin: 4px 8px;
}}

/* Paneller ve Ayırıcılar (QSplitter) */
QSplitter::handle {{
    background-color: {SPOTIFY_BG};
    width: 6px;
    height: 6px;
}}
QSplitter::handle:hover {{
    background-color: {SPOTIFY_GREEN};
}}

/* Kartlar ve Çerçeveler */
QFrame#panelCard {{
    background-color: {SPOTIFY_PANEL};
    border: 1px solid {SPOTIFY_BORDER};
    border-radius: 10px;
}}

/* Butonlar: Spotify Hap (Pill) Stili */
QPushButton {{
    background-color: {SPOTIFY_SURFACE};
    color: {SPOTIFY_WHITE};
    border: 1px solid {SPOTIFY_BORDER};
    border-radius: 14px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {SPOTIFY_HOVER};
    border-color: #333333;
    color: #FFFFFF;
}}

QPushButton:pressed {{
    background-color: #2a2a2a;
}}

QPushButton:disabled {{
    background-color: {SPOTIFY_PANEL};
    color: #555555;
    border-color: transparent;
}}

/* Spotify Neon Yeşil Birincil Buton (Primary Action) */
QPushButton#primaryGreenButton, QPushButton#btn_accent, QPushButton[primary="true"] {{
    background-color: {SPOTIFY_GREEN};
    color: #000000;
    border: none;
    border-radius: 16px;
    padding: 6px 18px;
    font-weight: 700;
    font-size: 12px;
}}

QPushButton#primaryGreenButton:hover, QPushButton#btn_accent:hover, QPushButton[primary="true"]:hover {{
    background-color: {SPOTIFY_GREEN_HOVER};
    color: #000000;
}}

QPushButton#primaryGreenButton:pressed, QPushButton#btn_accent:pressed, QPushButton[primary="true"]:pressed {{
    background-color: #169C46;
}}

/* Yuvarlak İkon Butonları (Circle Icon Button) */
QPushButton#circleButton {{
    background-color: {SPOTIFY_SURFACE};
    color: {SPOTIFY_MUTED};
    border: 1px solid {SPOTIFY_BORDER};
    border-radius: 14px;
    padding: 0px;
}}
QPushButton#circleButton:hover {{
    background-color: {SPOTIFY_HOVER};
    color: #FFFFFF;
}}

/* Metin Girdileri & Dropdownlar (Pill Search & Inputs) */
QLineEdit {{
    background-color: {SPOTIFY_SURFACE};
    color: {SPOTIFY_WHITE};
    border: 1px solid {SPOTIFY_BORDER};
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 11px;
}}

QLineEdit:focus {{
    border: 1px solid {SPOTIFY_GREEN};
    background-color: {SPOTIFY_PANEL};
}}

QComboBox {{
    background-color: {SPOTIFY_SURFACE};
    color: {SPOTIFY_WHITE};
    border: 1px solid {SPOTIFY_BORDER};
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    min-height: 20px;
}}

QComboBox:hover {{
    background-color: {SPOTIFY_HOVER};
}}

QComboBox::drop-down {{
    border: none;
    width: 18px;
}}

QComboBox::down-arrow {{
    image: url({CHEVRON_DOWN_SVG});
    width: 10px;
    height: 10px;
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {SPOTIFY_PANEL};
    color: {SPOTIFY_WHITE};
    border: 1px solid #333333;
    selection-background-color: {SPOTIFY_HOVER};
    selection-color: {SPOTIFY_GREEN};
    border-radius: 6px;
    padding: 4px;
}}

/* Spotify Tracklist Tablo Stili */
QTableWidget, QTableView {{
    background-color: {SPOTIFY_PANEL};
    color: {SPOTIFY_WHITE};
    gridline-color: {SPOTIFY_BORDER};
    border: 1px solid {SPOTIFY_BORDER};
    border-radius: 8px;
    font-size: 11px;
    outline: none;
}}

QTableWidget::item {{
    padding: 6px 8px;
    border: none;
}}

QTableWidget::item:hover {{
    background-color: {SPOTIFY_HOVER};
}}

QTableWidget::item:selected {{
    background-color: #242424;
    color: #FFFFFF;
}}

/* Tablo Başlıkları (Spotify Yeşil Sütun Başlıkları) */
QHeaderView::section {{
    background-color: {SPOTIFY_PANEL};
    color: {SPOTIFY_GREEN};
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.5px;
    padding: 6px 8px;
    border: none;
    border-bottom: 2px solid {SPOTIFY_GREEN};
    border-right: 1px solid {SPOTIFY_BORDER};
}}

/* Kaydırma Çubukları (Slim Minimalist) */
QScrollBar:vertical {{
    background-color: transparent;
    width: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: #333333;
    min-height: 20px;
    border-radius: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {SPOTIFY_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 6px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: #333333;
    min-width: 20px;
    border-radius: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {SPOTIFY_MUTED};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Durum Çubuğu (QStatusBar) */
QStatusBar {{
    background-color: {SPOTIFY_BG};
    color: {SPOTIFY_MUTED};
    border-top: 1px solid {SPOTIFY_BORDER};
    font-size: 11px;
}}

/* Araç İpuçları (QToolTip) */
QToolTip {{
    background-color: {SPOTIFY_SURFACE};
    color: #FFFFFF;
    border: 1px solid #333333;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
}}
"""
