"""
KM Tablo Oluşturucu - Spotify CAD Önizleme Paneli (CadWorkspacePanel).
'ÇİZİM ÖNİZLEME (CAD)' başlığı, '1:1 Milimetrik Vektör', pafta/yerleşim hap dropdownları,
teknik neon yeşil CAD çizim alanı ve '▶ AutoCAD DXF Olarak Dışa Aktar' butonu.
"""
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QComboBox, QLabel
)

from src.config.sheet_config import (
    LayoutConfig, SheetSize, SheetOrientation, TablePlacement, DEFAULT_LAYOUT_CONFIG
)
from src.config.table_config import TableConfig, DEFAULT_TABLE_CONFIG
from src.models.table import Table
from src.ui import theme
from src.ui.i18n import i18n
from src.ui.preview_canvas import CadGraphicsView


class CadWorkspacePanel(QWidget):
    """
    Spotify CAD Görünüm ve Pafta Kontrol Paneli.
    """
    layout_changed = Signal(object)      # LayoutConfig
    export_requested = Signal()          # DXF dışa aktarma tıklandı
    cursor_pos_changed = Signal(float, float)
    zoom_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout_config = DEFAULT_LAYOUT_CONFIG
        self.table_config = DEFAULT_TABLE_CONFIG
        self._current_table: Optional[Table] = None
        self.zoom_pct: int = 100

        self._build_ui()
        i18n.language_changed.connect(self._update_translations)

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        # ----------------------------------------------------------------------
        # 1. KART BAŞLIĞI: [ÇİZİM ÖNİZLEME (CAD)] + [1:1 Milimetrik Vektör]
        # ----------------------------------------------------------------------
        title_bar = QFrame(self)
        title_bar.setFixedHeight(28)
        title_bar.setStyleSheet("background: transparent; border: none;")
        t_layout = QHBoxLayout(title_bar)
        t_layout.setContentsMargins(4, 0, 4, 0)
        t_layout.setSpacing(8)

        self.lbl_title = QLabel("ÇİZİM ÖNİZLEME (CAD)", title_bar)
        self.lbl_title.setStyleSheet("font-size: 13px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.5px;")
        t_layout.addWidget(self.lbl_title)

        t_layout.addStretch()

        self.lbl_vector_tag = QLabel("1:1 Milimetrik Vektör", title_bar)
        self.lbl_vector_tag.setStyleSheet(f"font-size: 11px; color: {theme.COLOR_TEXT_MUTED};")
        t_layout.addWidget(self.lbl_vector_tag)

        root_layout.addWidget(title_bar)

        # ----------------------------------------------------------------------
        # 2. İKİNCİL ŞERİT: [CAD ÖNİZLİ] + [A3 ▾] + [Yatay ▾] + [Yerleşim ▾] + [Zoom]
        # ----------------------------------------------------------------------
        top_bar = QFrame(self)
        top_bar.setFixedHeight(34)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.COLOR_PANEL_ALT};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 17px;
            }}
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(8, 0, 8, 0)
        top_layout.setSpacing(6)

        # Viewport Rozeti
        self.lbl_sheet_tag = QLabel("⛶ CAD ÖNİZLİ", top_bar)
        self.lbl_sheet_tag.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 700;
            color: {theme.COLOR_ACCENT};
            padding: 0 4px;
        """)
        top_layout.addWidget(self.lbl_sheet_tag)

        # Pafta Boyutu Dropdown (A3)
        self.cb_size = QComboBox(top_bar)
        self.cb_size.setFixedHeight(24)
        for s in SheetSize:
            self.cb_size.addItem(s.value, s)
        size_val = self.layout_config.size.value if hasattr(self.layout_config.size, "value") else str(self.layout_config.size)
        self.cb_size.setCurrentText(size_val)
        self.cb_size.currentIndexChanged.connect(self._on_layout_controls_changed)
        top_layout.addWidget(self.cb_size)

        # Yönelim Dropdown (Yatay / Dikey)
        self.cb_orient = QComboBox(top_bar)
        self.cb_orient.setFixedHeight(24)
        self._populate_orientation_options()
        self.cb_orient.currentIndexChanged.connect(self._on_layout_controls_changed)
        top_layout.addWidget(self.cb_orient)

        # Yerleşim Dropdown (Bağımsız Tablo / Antet Üstü)
        self.cb_placement = QComboBox(top_bar)
        self.cb_placement.setFixedHeight(24)
        self._populate_placement_options()
        self.cb_placement.currentIndexChanged.connect(self._on_layout_controls_changed)
        top_layout.addWidget(self.cb_placement)

        top_layout.addStretch()

        # Zoom Kontrolleri: [−] [100%] [+] [⛶]
        self.btn_zm_out = QPushButton("−", top_bar)
        self.btn_zm_out.setObjectName("circleButton")
        self.btn_zm_out.setFixedSize(24, 24)
        self.btn_zm_out.clicked.connect(self.canvas_zoom_out)
        top_layout.addWidget(self.btn_zm_out)

        self.btn_zm_100 = QPushButton("100%", top_bar)
        self.btn_zm_100.setFixedHeight(24)
        self.btn_zm_100.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 12px;
                padding: 0 8px;
                font-size: 10px;
                font-weight: bold;
                color: {theme.COLOR_TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
            }}
        """)
        self.btn_zm_100.clicked.connect(self.zoom_actual)
        top_layout.addWidget(self.btn_zm_100)

        self.btn_zm_in = QPushButton("+", top_bar)
        self.btn_zm_in.setObjectName("circleButton")
        self.btn_zm_in.setFixedSize(24, 24)
        self.btn_zm_in.clicked.connect(self.canvas_zoom_in)
        top_layout.addWidget(self.btn_zm_in)

        self.btn_fit_quick = QPushButton("⛶", top_bar)
        self.btn_fit_quick.setObjectName("circleButton")
        self.btn_fit_quick.setFixedSize(24, 24)
        self.btn_fit_quick.clicked.connect(self.fit_to_view)
        top_layout.addWidget(self.btn_fit_quick)

        root_layout.addWidget(top_bar)

        # ----------------------------------------------------------------------
        # 3. CAD ÇİZİM TUVALİ (CadGraphicsView)
        # ----------------------------------------------------------------------
        canvas_container = QFrame(self)
        canvas_container.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 8px;
            }}
        """)
        c_layout = QVBoxLayout(canvas_container)
        c_layout.setContentsMargins(2, 2, 2, 2)

        self.canvas = CadGraphicsView(canvas_container)
        self.canvas.setStyleSheet("border: none; background: #000000;")
        self.canvas.cursor_pos_changed.connect(self.cursor_pos_changed.emit)
        c_layout.addWidget(self.canvas)

        root_layout.addWidget(canvas_container, 1)

        # ----------------------------------------------------------------------
        # 4. ALT ŞERİT: [:: Sığdır] ve [▶ AutoCAD DXF Olarak Dışa Aktar]
        # ----------------------------------------------------------------------
        bot_bar = QFrame(self)
        bot_bar.setFixedHeight(38)
        bot_bar.setStyleSheet("background: transparent; border: none;")
        bot_layout = QHBoxLayout(bot_bar)
        bot_layout.setContentsMargins(4, 0, 4, 0)
        bot_layout.setSpacing(10)

        self.btn_fit = QPushButton(":: Sığdır", bot_bar)
        self.btn_fit.setFixedHeight(32)
        self.btn_fit.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_PRIMARY};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 16px;
                padding: 0 16px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
            }}
        """)
        self.btn_fit.clicked.connect(self.fit_to_view)
        bot_layout.addWidget(self.btn_fit)

        bot_layout.addStretch()

        # SPOTIFY NEON YEŞİL ALT DXF BUTONU
        self.btn_export = QPushButton("AutoCAD DXF Olarak Dışa Aktar", bot_bar)
        self.btn_export.setObjectName("primaryGreenButton")
        self.btn_export.setFixedHeight(34)
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setStyleSheet(f"""
            QPushButton#primaryGreenButton {{
                background-color: {theme.COLOR_ACCENT};
                color: #000000;
                border: none;
                border-radius: 17px;
                padding: 0 20px;
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
        bot_layout.addWidget(self.btn_export)

        root_layout.addWidget(bot_bar)

    def canvas_zoom_in(self):
        self.canvas.zoom_in()
        self.zoom_pct = int(self.zoom_pct * 1.2)
        self.zoom_changed.emit(self.zoom_pct)

    def zoom_in(self):
        self.canvas_zoom_in()

    def canvas_zoom_out(self):
        self.canvas.zoom_out()
        self.zoom_pct = max(10, int(self.zoom_pct * 0.83))
        self.zoom_changed.emit(self.zoom_pct)

    def zoom_out(self):
        self.canvas_zoom_out()

    def zoom_actual(self):
        self.canvas.zoom_actual()
        self.zoom_pct = 100
        self.zoom_changed.emit(self.zoom_pct)

    def fit_to_view(self):
        self.canvas.fit_to_view()
        self.zoom_pct = 100
        self.zoom_changed.emit(self.zoom_pct)

    def _populate_orientation_options(self):
        self.cb_orient.blockSignals(True)
        self.cb_orient.clear()
        self.cb_orient.addItem("Yatay", SheetOrientation.LANDSCAPE)
        self.cb_orient.addItem("Dikey", SheetOrientation.PORTRAIT)
        self.cb_orient.blockSignals(False)

    def _populate_placement_options(self):
        self.cb_placement.blockSignals(True)
        self.cb_placement.clear()
        placement_keys = [
            (TablePlacement.STANDALONE, "Bağımsız Tablo"),
            (TablePlacement.ABOVE_TITLEBLOCK, "Antet Üstü"),
            (TablePlacement.TOP_RIGHT, "Sağ Üst"),
            (TablePlacement.CENTER_SHEET, "Paftayı Ortala"),
        ]
        for p, label in placement_keys:
            self.cb_placement.addItem(label, p)
        self.cb_placement.blockSignals(False)

    def _on_layout_controls_changed(self):
        self.layout_config.size = self.cb_size.currentData()
        self.layout_config.orientation = self.cb_orient.currentData()
        self.layout_config.placement = self.cb_placement.currentData()
        if self._current_table:
            self.canvas.set_data(self._current_table, self.table_config, self.layout_config, auto_fit=True)
        self.layout_changed.emit(self.layout_config)

    def set_data(
        self,
        table: Table,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None,
        auto_fit: bool = True
    ):
        self._current_table = table
        if table_config:
            self.table_config = table_config
        if layout_config:
            self.layout_config = layout_config

        self.canvas.set_data(
            table=table,
            table_config=self.table_config,
            layout_config=self.layout_config,
            auto_fit=auto_fit
        )

    def redraw(self):
        self.canvas.redraw()

    def _update_translations(self, lang_code: str):
        self.btn_fit.setText(":: Sığdır")
        self.btn_export.setText("AutoCAD DXF Olarak Dışa Aktar")
