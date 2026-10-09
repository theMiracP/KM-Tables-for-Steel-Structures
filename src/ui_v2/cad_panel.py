"""
Linear / SaaS Tarzı CAD Önizleme Paneli (CadViewportPanel).
Çerçevesiz, minimalist vektör tuvali ve üzerinde yüzen (Floating Glass HUD) şeffaf araç kontrol hapı.
"""
from typing import Optional
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor

from src.config.sheet_config import LayoutConfig
from src.config.table_config import TableConfig
from src.models.table import Table
from src.ui.preview_canvas import CadGraphicsView
from src.ui_v2 import theme_linear as theme
from src.ui_v2 import icons
from src.ui.i18n import i18n


class FloatingHudToolbar(QFrame):
    """
    Tuvalin üzerinde yüzen (Floating Glass HUD) modern hap araç çubuğu.
    """
    close_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(23, 24, 31, 0.88);
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 18px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme.TEXT_PRIMARY};
                font-size: 11px;
                font-weight: 500;
                padding: 4px 8px;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
            }}
            QLabel {{
                color: {theme.TEXT_MUTED};
                font-size: 11px;
            }}
        """)

        # Hafif gölge efekti
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(6)

        self.btn_fit = QPushButton(f"⛶ {i18n.t('zoom_fit')}")
        self.btn_fit.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_fit)

        self.btn_zoom_actual = QPushButton("100%")
        self.btn_zoom_actual.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_zoom_actual)

        self.btn_zoom_in = QPushButton("＋")
        self.btn_zoom_in.setFixedSize(24, 24)
        self.btn_zoom_in.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("－")
        self.btn_zoom_out.setFixedSize(24, 24)
        self.btn_zoom_out.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_zoom_out)

        sep = QLabel("|")
        layout.addWidget(sep)

        self.lbl_coords = QLabel("X: 0.0 mm · Y: 0.0 mm")
        layout.addWidget(self.lbl_coords)

        sep2 = QLabel("|")
        layout.addWidget(sep2)

        self.btn_close = QPushButton()
        self.btn_close.setIcon(icons.get_icon(icons.ICON_CLOSE, color=icons.COLOR_MUTED))
        self.btn_close.setIconSize(icons.icon_size(12))
        self.btn_close.setToolTip(i18n.t("btn_cad_panel_close_tooltip"))
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.btn_close)

        i18n.language_changed.connect(self._update_translations)

    def _update_translations(self, lang_code: str = ""):
        try:
            self.btn_fit.setText(f"⛶ {i18n.t('zoom_fit')}")
            self.btn_close.setToolTip(i18n.t("btn_cad_panel_close_tooltip"))
        except RuntimeError:
            pass

    def set_coords(self, x: float, y: float):
        self.lbl_coords.setText(f"X: {x:+.1f} mm · Y: {y:+.1f} mm")


class CadViewportPanel(QWidget):
    """
    SaaS tarzı CAD çizim görüntüleyici.
    Floating HUD barı tuvalin üstünde konumlandırır ve pencere boyutu değiştikçe ortalar.
    """
    toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {theme.COLOR_CAD_BG};")

        # CAD Tuvali
        self.canvas = CadGraphicsView(self)
        self.canvas.cursor_pos_changed.connect(self._on_cursor_moved)

        # Floating HUD Bar
        self.hud = FloatingHudToolbar(self)
        self.hud.btn_fit.clicked.connect(self.canvas.fit_to_view)
        self.hud.btn_zoom_actual.clicked.connect(self.canvas.zoom_actual)
        self.hud.btn_zoom_in.clicked.connect(self.canvas.zoom_in)
        self.hud.btn_zoom_out.clicked.connect(self.canvas.zoom_out)
        self.hud.close_clicked.connect(self.toggle_requested.emit)

        # Sol Üstteki Başlık Rozeti (Floating Badge)
        self.badge_title = QLabel(f"📐 {i18n.t('badge_cad_viewport')}", self)
        self.badge_title.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(23, 24, 31, 0.75);
                color: {theme.TEXT_SECONDARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }}
        """)
        i18n.language_changed.connect(self._on_language_changed)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def _on_language_changed(self, lang_code: str = ""):
        try:
            self.badge_title.setText(f"📐 {i18n.t('badge_cad_viewport')}")
        except RuntimeError:
            pass

    def _on_cursor_moved(self, x: float, y: float):
        self.hud.set_coords(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # HUD'ı alt merkeze yerleştir (floating)
        hud_w = 370
        hud_h = 36
        x = (self.width() - hud_w) // 2
        y = self.height() - hud_h - 16
        self.hud.setGeometry(x, y, hud_w, hud_h)

        # Başlık rozetini sol üste yerleştir
        self.badge_title.setGeometry(16, 16, 160, 26)

    def fit_view(self):
        """Tuvali pencereye sığdırır."""
        self.canvas.fit_to_view()

    def set_data(self, table: Table, layout_config: Optional[LayoutConfig] = None, auto_fit: bool = True):
        self.canvas.set_data(table=table, layout_config=layout_config, auto_fit=auto_fit)
