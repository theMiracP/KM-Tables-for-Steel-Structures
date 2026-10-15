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
    multi_sheet_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_multi_sheet: bool = False
        self.setObjectName("floatingHudToolbar")
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            QFrame#floatingHudToolbar {{
                background-color: rgba(18, 20, 28, 0.90);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 18px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                color: #e2e8f0;
                font-size: 11px;
                font-weight: 500;
                padding: 3px 8px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.10);
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.16);
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.70);
                font-size: 11px;
            }}
            QPushButton#hudMultiSheet {{
                background-color: rgba(99, 102, 241, 0.18);
                color: #c7d2fe;
                border: 1px solid rgba(99, 102, 241, 0.38);
                border-radius: 12px;
                padding: 2px 10px;
                font-weight: 500;
                font-size: 11px;
            }}
            QPushButton#hudMultiSheet:hover {{
                background-color: rgba(99, 102, 241, 0.35);
                border-color: rgba(99, 102, 241, 0.65);
                color: #ffffff;
            }}
            QPushButton#hudMultiSheet[active="true"] {{
                background-color: rgba(16, 185, 129, 0.24);
                color: #a7f3d0;
                border: 1px solid rgba(16, 185, 129, 0.55);
                border-radius: 12px;
                padding: 2px 10px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton#hudMultiSheet[active="true"]:hover {{
                background-color: rgba(16, 185, 129, 0.40);
                border-color: rgba(16, 185, 129, 0.80);
                color: #ffffff;
            }}
            QPushButton#hudClose {{
                border-radius: 12px;
            }}
            QPushButton#hudClose:hover {{
                background-color: rgba(239, 68, 68, 0.25);
                color: #fca5a5;
            }}
        """)

        # Hafif gölge efekti
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self._build_ui()

    def _create_divider(self) -> QFrame:
        div = QFrame(self)
        div.setFrameShape(QFrame.Shape.VLine)
        div.setFrameShadow(QFrame.Shadow.Plain)
        div.setFixedWidth(1)
        div.setFixedHeight(14)
        div.setStyleSheet("background-color: rgba(255, 255, 255, 0.14); border: none;")
        return div

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

        layout.addWidget(self._create_divider())

        self.lbl_coords = QLabel("X: 0.0 mm · Y: 0.0 mm")
        self.lbl_coords.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', 'JetBrains Mono', 'Segoe UI Mono', monospace;
                font-size: 11px;
                color: rgba(255, 255, 255, 0.75);
                background: transparent;
                border: none;
                padding: 0 4px;
            }
        """)
        self.lbl_coords.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_coords.setMinimumWidth(165)
        layout.addWidget(self.lbl_coords)

        layout.addWidget(self._create_divider())

        self.btn_multi_sheet = QPushButton(f"📑 {i18n.t('btn_multi_sheet')}")
        self.btn_multi_sheet.setObjectName("hudMultiSheet")
        self.btn_multi_sheet.setToolTip(i18n.t("tooltip_multi_sheet"))
        self.btn_multi_sheet.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_multi_sheet.clicked.connect(self.multi_sheet_clicked.emit)
        layout.addWidget(self.btn_multi_sheet)

        layout.addWidget(self._create_divider())

        self.btn_close = QPushButton()
        self.btn_close.setObjectName("hudClose")
        self.btn_close.setIcon(icons.get_icon(icons.ICON_CLOSE, color=icons.COLOR_MUTED))
        self.btn_close.setIconSize(icons.icon_size(12))
        self.btn_close.setToolTip(i18n.t("btn_cad_panel_close_tooltip"))
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.btn_close)

        i18n.language_changed.connect(self._update_translations)

    def set_multi_sheet_mode(self, is_multi: bool):
        self._is_multi_sheet = is_multi
        self._update_multi_sheet_button()

    def _update_multi_sheet_button(self):
        if self._is_multi_sheet:
            self.btn_multi_sheet.setText(f"📄 {i18n.t('btn_single_sheet')}")
            self.btn_multi_sheet.setToolTip(i18n.t("tooltip_single_sheet"))
            self.btn_multi_sheet.setProperty("active", "true")
        else:
            self.btn_multi_sheet.setText(f"📑 {i18n.t('btn_multi_sheet')}")
            self.btn_multi_sheet.setToolTip(i18n.t("tooltip_multi_sheet"))
            self.btn_multi_sheet.setProperty("active", "false")
        self.btn_multi_sheet.style().unpolish(self.btn_multi_sheet)
        self.btn_multi_sheet.style().polish(self.btn_multi_sheet)
        self.btn_multi_sheet.update()

    def _update_translations(self, lang_code: str = ""):
        try:
            self.btn_fit.setText(f"⛶ {i18n.t('zoom_fit')}")
            self._update_multi_sheet_button()
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
    multi_sheet_requested = Signal()

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
        self.hud.multi_sheet_clicked.connect(self.multi_sheet_requested.emit)
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

    def set_multi_sheet_mode(self, is_multi: bool, sheet_count: int = 0):
        self._is_multi_sheet = is_multi
        self._last_sheet_count = sheet_count
        self.hud.set_multi_sheet_mode(is_multi)
        self._update_badge_title()
        self.badge_title.adjustSize()

    def _update_badge_title(self):
        if getattr(self, "_is_multi_sheet", False):
            count = getattr(self, "_last_sheet_count", 0)
            count_str = f" ({count} {i18n.t('sheets_count')})" if count > 0 else ""
            self.badge_title.setText(f"📑 {i18n.t('badge_multi_sheet')}{count_str}")
        else:
            self.badge_title.setText(f"📐 {i18n.t('badge_cad_viewport')}")

    def _on_language_changed(self, lang_code: str = ""):
        try:
            self._update_badge_title()
        except RuntimeError:
            pass

    def _on_cursor_moved(self, x: float, y: float):
        self.hud.set_coords(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # HUD'ı alt merkeze yerleştir (floating, dinamik genişlik)
        req_w = max(self.hud.sizeHint().width() + 16, 520)
        hud_w = min(req_w, max(self.width() - 24, 200))
        hud_h = 36
        x = (self.width() - hud_w) // 2
        y = self.height() - hud_h - 16
        self.hud.setGeometry(x, y, hud_w, hud_h)

        # Başlık rozetini sol üste yerleştir (metne göre genişlik)
        badge_w = max(self.badge_title.sizeHint().width() + 20, 180)
        self.badge_title.setGeometry(16, 16, badge_w, 26)

    def fit_view(self):
        """Tuvali pencereye sığdırır."""
        self.canvas.fit_to_view()

    def set_data(self, table: Table, layout_config: Optional[LayoutConfig] = None, auto_fit: bool = True):
        self.canvas.set_data(table=table, layout_config=layout_config, auto_fit=auto_fit)
