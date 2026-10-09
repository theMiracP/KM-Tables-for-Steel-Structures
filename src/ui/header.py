"""
KM Tablo Oluşturucu - Spotify Dark Üst Komut ve Navigasyon Başlığı (ModernAppHeader).
Spotify logosu, geçmiş butonları (< >), 'Dilediğini Ara (Ctrl+T)' kapsülü ve
'▶ AutoCAD DXF Olarak Dışa Aktar' neon yeşil pill butonu.
"""
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame, QMenu
)

from src.ui import theme
from src.ui.i18n import i18n


class ModernAppHeader(QWidget):
    """
    Spotify masaüstü tarzı üst navigasyon ve komut başlığı.
    """
    quick_switch_requested = Signal()
    toggle_sidebar_requested = Signal()
    export_requested = Signal()
    fit_view_requested = Signal()
    load_samples_requested = Signal()
    language_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(54)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"""
            ModernAppHeader {{
                background-color: {theme.COLOR_BG_DARK};
                border-bottom: 1px solid {theme.COLOR_BORDER};
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        # 1. SOL: Spotify İkonu + 'KM CAD STUDIO'
        self.btn_toggle_sidebar = QPushButton("☰", self)
        self.btn_toggle_sidebar.setObjectName("circleButton")
        self.btn_toggle_sidebar.setFixedSize(30, 30)
        self.btn_toggle_sidebar.setToolTip("Kitaplığı Göster / Gizle (Ctrl+B)")
        self.btn_toggle_sidebar.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: #FFFFFF;
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 15px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
                color: {theme.COLOR_ACCENT};
            }}
        """)
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar_requested.emit)
        layout.addWidget(self.btn_toggle_sidebar)

        # Spotify Dalgası & Marka
        self.lbl_logo = QLabel("🌀 KM CAD STUDIO", self)
        self.lbl_logo.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 900;
            color: {theme.COLOR_ACCENT};
            letter-spacing: 0.8px;
            padding-right: 6px;
        """)
        layout.addWidget(self.lbl_logo)

        # Geri / İleri Dairesel Butonlar (< >)
        self.btn_prev = QPushButton("〈", self)
        self.btn_prev.setObjectName("circleButton")
        self.btn_prev.setFixedSize(28, 28)
        self.btn_prev.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_MUTED};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
                color: #FFFFFF;
            }}
        """)
        layout.addWidget(self.btn_prev)

        self.btn_next = QPushButton("〉", self)
        self.btn_next.setObjectName("circleButton")
        self.btn_next.setFixedSize(28, 28)
        self.btn_next.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_MUTED};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
                color: #FFFFFF;
            }}
        """)
        layout.addWidget(self.btn_next)

        # 2. ORTA: '🔍 Dilediğini Ara (Ctrl+T)' Pill Kapsülü
        self.btn_quick_switch = QPushButton("🔍  Dilediğini Ara (Ctrl+T)", self)
        self.btn_quick_switch.setFixedHeight(34)
        self.btn_quick_switch.setMinimumWidth(280)
        self.btn_quick_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quick_switch.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_MUTED};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 17px;
                padding: 0 16px;
                text-align: left;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {theme.COLOR_BORDER_LIGHT};
                color: #FFFFFF;
                background-color: {theme.COLOR_PANEL_HOVER};
            }}
        """)
        self.btn_quick_switch.clicked.connect(self.quick_switch_requested.emit)
        layout.addWidget(self.btn_quick_switch)

        layout.addStretch()

        # 3. SAĞ: Hızlı Pill Aksiyonları
        # Görünümü Sığdır Butonu
        self.btn_fit = QPushButton("⛶ Görünümü Sığdır", self)
        self.btn_fit.setFixedHeight(32)
        self.btn_fit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fit.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_PRIMARY};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 16px;
                padding: 0 14px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
                color: #FFFFFF;
            }}
        """)
        self.btn_fit.clicked.connect(self.fit_view_requested.emit)
        layout.addWidget(self.btn_fit)

        # Örnekleri Yükle Butonu
        self.btn_samples = QPushButton("± Örnekleri Yükle", self)
        self.btn_samples.setFixedHeight(32)
        self.btn_samples.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_samples.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_PRIMARY};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 16px;
                padding: 0 14px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
                color: #FFFFFF;
            }}
        """)
        self.btn_samples.clicked.connect(self.load_samples_requested.emit)
        layout.addWidget(self.btn_samples)

        # SPOTIFY NEON YEŞİL BÜYÜK PILL EYLEM BUTONU
        self.btn_export = QPushButton("AutoCAD DXF Olarak Dışa Aktar", self)
        self.btn_export.setObjectName("primaryGreenButton")
        self.btn_export.setFixedHeight(34)
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setStyleSheet(f"""
            QPushButton#primaryGreenButton {{
                background-color: {theme.COLOR_ACCENT};
                color: #000000;
                border: none;
                border-radius: 17px;
                padding: 0 18px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton#primaryGreenButton:hover {{
                background-color: {theme.COLOR_ACCENT_HOVER};
            }}
            QPushButton#primaryGreenButton:pressed {{
                background-color: #169C46;
            }}
        """)
        self.btn_export.clicked.connect(self.export_requested.emit)
        layout.addWidget(self.btn_export)

        # Üç Nokta Seçenek Butonu (...)
        self.btn_more = QPushButton("•••", self)
        self.btn_more.setFixedSize(32, 32)
        self.btn_more.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_MUTED};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
                color: #FFFFFF;
            }}
        """)
        layout.addWidget(self.btn_more)

        # Dil Seçici (Pill QComboBox)
        self.cb_lang = QComboBox(self)
        self.cb_lang.setFixedWidth(56)
        self.cb_lang.setFixedHeight(30)
        for code in ["TR", "RU", "EN"]:
            self.cb_lang.addItem(code, code)
        self.cb_lang.setCurrentIndex(0)
        self.cb_lang.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: #FFFFFF;
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 15px;
                padding: 2px 8px;
                font-weight: 700;
                font-size: 11px;
            }}
            QComboBox:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
            }}
        """)
        self.cb_lang.currentIndexChanged.connect(self._on_lang_changed)
        layout.addWidget(self.cb_lang)

    def set_active_table_title(self, title: str):
        self.btn_quick_switch.setText(f"🔍  {title} (Ctrl+T)")

    def _on_lang_changed(self):
        lang = self.cb_lang.currentData()
        if lang:
            self.language_changed.emit(lang)

    def update_translations(self):
        self.btn_fit.setText("⛶ Görünümü Sığdır")
        self.btn_samples.setText("± Örnekleri Yükle")
        self.btn_export.setText("AutoCAD DXF Olarak Dışa Aktar")
