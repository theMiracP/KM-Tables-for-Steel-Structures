"""
Linear / Notion SaaS Yan Gezinme Paneli (Sidebar).
Çalışma alanı seçimi, interaktif tablo listesi, pafta parametreleri ve GOST durum kartı.
"""
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QWidget, QScrollArea, QLineEdit
)
from src.contracts.table_module import TableModule
from src.config.sheet_config import SheetSize, SheetOrientation, TablePlacement, LayoutConfig
from src.models.registry import TableRegistry
from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import LinearComboBox
from src.ui_v2 import icons
from src.ui.i18n import i18n
from src.version import APP_VERSION


def get_module_display_title(module_or_id) -> str:
    """
    Tüm programda (Sidebar, Quick Switcher, Dialoglar) tek tip, standart tablo adını döner.
    Aktif dile (TR/RU/EN) göre yerelleştirilmiştir.
    """
    mod_id = getattr(module_or_id, "id", str(module_or_id))
    raw_name = getattr(module_or_id, "name", "")
    if "elements" in mod_id or "elementov" in mod_id:
        return i18n.t("module_elements_schedule")
    elif "title_block" in mod_id or "antet" in mod_id:
        return i18n.t("module_title_block")
    elif "reference" in mod_id or "doc" in mod_id:
        return i18n.t("module_reference_docs")
    elif "working_drawings" in mod_id:
        return i18n.t("module_working_drawings")
    elif "main_drawings" in mod_id or "drawings" in mod_id or "main_sets" in mod_id:
        return i18n.t("module_main_drawings")
    else:
        return raw_name.split("(")[0].strip() if raw_name else mod_id


def get_module_icon_name(module_or_id) -> str:
    """Modüle ait vektörel ikon adını döner."""
    mod_id = getattr(module_or_id, "id", str(module_or_id))
    if "elements" in mod_id or "elementov" in mod_id:
        return icons.ICON_DOC_REGULAR
    elif "title_block" in mod_id or "antet" in mod_id:
        return "fa5r.id-badge"
    elif "reference" in mod_id or "doc" in mod_id:
        return icons.ICON_BOOKMARK_REGULAR
    elif "working_drawings" in mod_id:
        return icons.ICON_CLIPBOARD_REGULAR
    elif "main_drawings" in mod_id or "drawings" in mod_id or "main_sets" in mod_id:
        return "fa5r.copy"
    return icons.ICON_DOC_REGULAR


class TableNavItem(QPushButton):
    """Notion tarzı doküman navigasyon satırı."""
    def __init__(self, module: TableModule, is_active: bool = False, count: int = 0, parent=None):
        super().__init__(parent)
        self.module = module
        self.count = count
        self.is_active = is_active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        self._build_ui()

    def _build_ui(self):
        self.setText("")  # Text is handled custom via child layout or formatted string
        layout = QHBoxLayout(self)
        # İkon (fa5r Regular hafif vektörel ikonlar)
        self.lbl_icon = QLabel()
        self.lbl_icon.setFixedSize(18, 18)
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_icon)

        # Tablo Adı
        self.lbl_name = QLabel("")
        self.lbl_name.setStyleSheet("font-size: 12px; font-weight: 500;")
        layout.addWidget(self.lbl_name, 1)

        # Sayı Rozeti (Kullanıcı isteği doğrultusunda gizlendi)
        self.lbl_badge = QLabel("")
        self.lbl_badge.setVisible(False)
        layout.addWidget(self.lbl_badge)

        self.update_title()
        self.set_active_state(self.is_active)

    def update_title(self):
        """Aktif dile göre tablo adını günceller."""
        self.lbl_name.setText(get_module_display_title(self.module))

    def _get_icon_name(self) -> str:
        return get_module_icon_name(self.module)

    def _update_icon(self):
        icon_name = self._get_icon_name()
        color = icons.COLOR_ACCENT_BLUE if self.is_active else icons.COLOR_NEUTRAL
        ico = icons.get_icon(icon_name, color=color)
        if not ico.isNull():
            self.lbl_icon.setPixmap(ico.pixmap(16, 16))

    def set_active_state(self, active: bool):
        self.is_active = active
        self._update_icon()
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.BG_SURFACE_HOVER};
                    border: 1px solid {theme.BORDER_LIGHT};
                    border-left: 3px solid {theme.ACCENT_PRIMARY};
                    border-radius: 6px;
                    text-align: left;
                }}
            """)
            self.lbl_name.setStyleSheet(f"color: #ffffff; font-weight: 600; font-size: 12px;")
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {theme.BG_SURFACE};
                    border-color: {theme.BORDER_SUBTLE};
                }}
            """)
            self.lbl_name.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-weight: 500; font-size: 12px;")

    def set_count(self, count: int):
        self.count = count
        # Sayı gösterimi gizli tutulur


class LinearSidebar(QFrame):
    """
    Notion / Linear tarzı dar, şık çalışma alanı kenar çubuğu.
    """
    table_selected = Signal(str)          # module_id
    layout_config_changed = Signal(object) # LayoutConfig

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setObjectName("sidebarFrame")
        self.setStyleSheet(f"""
            QFrame#sidebarFrame {{
                background-color: {theme.BG_SIDEBAR};
                border-right: 1px solid {theme.BORDER_SUBTLE};
            }}
        """)
        self._nav_items = {}
        self._layout_config = LayoutConfig()

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 16, 12, 16)
        main_layout.setSpacing(16)

        # 1. ÇALIŞMA ALANI BAŞLIĞI (Notion Workspace Selector)
        ws_container = QWidget()
        ws_layout = QHBoxLayout(ws_container)
        ws_layout.setContentsMargins(0, 0, 0, 0)
        ws_layout.setSpacing(8)

        lbl_ws_icon = QLabel()
        ico_ws = icons.get_icon("fa5s.drafting-compass", color=icons.COLOR_PRIMARY)
        if not ico_ws.isNull():
            lbl_ws_icon.setPixmap(ico_ws.pixmap(16, 16))
        else:
            lbl_ws_icon.setText("📐")
        ws_layout.addWidget(lbl_ws_icon)

        self.lbl_ws_title = QLabel(i18n.t("sidebar_workspace_title"))
        self.lbl_ws_title.setStyleSheet(f"font-weight: 600; color: {theme.TEXT_PRIMARY}; font-size: 13px;")
        ws_layout.addWidget(self.lbl_ws_title, 1)

        self.btn_more = QPushButton()
        ico_down = icons.get_icon(icons.ICON_CHEVRON_DOWN, color=icons.COLOR_MUTED)
        if not ico_down.isNull():
            self.btn_more.setIcon(ico_down)
            self.btn_more.setIconSize(icons.icon_size(10))
        else:
            self.btn_more.setText("▾")
        self.btn_more.setObjectName("ghostButton")
        self.btn_more.setFixedSize(20, 20)
        self.btn_more.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_more.setToolTip("Çalışma Alanı / Proje Menüsü")
        self.btn_more.clicked.connect(self._show_workspace_menu)
        ws_layout.addWidget(self.btn_more)
        main_layout.addWidget(ws_container)

        # Hızlı Arama Kutusu
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText(i18n.t("sidebar_filter_placeholder"))
        self.txt_filter.setFixedHeight(28)
        self.txt_filter.textChanged.connect(self._filter_items)
        main_layout.addWidget(self.txt_filter)

        # 2. SCROLLABLE BÖLÜM: Tablolar ve Pafta Ayarları
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(18)

        # A) TABLOLAR BÖLÜMÜ
        self.lbl_sec_tables = QLabel(i18n.t("sidebar_tables_header"))
        self.lbl_sec_tables.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_MUTED}; letter-spacing: 0.5px;")
        scroll_layout.addWidget(self.lbl_sec_tables)

        self.tables_container = QWidget()
        self.tables_layout = QVBoxLayout(self.tables_container)
        self.tables_layout.setContentsMargins(0, 0, 0, 0)
        self.tables_layout.setSpacing(4)
        scroll_layout.addWidget(self.tables_container)

        self._populate_tables()

        # B) PAFTA PARAMETRELERİ BÖLÜMÜ (Notion Properties Card)
        self.lbl_sec_sheet = QLabel(i18n.t("sidebar_sheet_header"))
        self.lbl_sec_sheet.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_MUTED}; letter-spacing: 0.5px;")
        scroll_layout.addWidget(self.lbl_sec_sheet)

        sheet_card = QFrame()
        sheet_card.setObjectName("cardFrame")
        sheet_card.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        sc_layout = QVBoxLayout(sheet_card)
        sc_layout.setContentsMargins(8, 8, 8, 8)
        sc_layout.setSpacing(8)

        # Boyut
        row_size = QHBoxLayout()
        self.lbl_size = QLabel(i18n.t("sidebar_size"))
        self.lbl_size.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px;")
        self.cmb_size = LinearComboBox()
        self.cmb_size.addItems(["A3", "A4", "A2", "A1", "A0"])
        self.cmb_size.setCurrentText("A3")
        self.cmb_size.setFixedWidth(75)
        self.cmb_size.setFixedHeight(26)
        self.cmb_size.currentTextChanged.connect(self._on_layout_param_changed)
        row_size.addWidget(self.lbl_size)
        row_size.addStretch(1)
        row_size.addWidget(self.cmb_size)
        sc_layout.addLayout(row_size)

        # Yön
        row_orient = QHBoxLayout()
        self.lbl_orient = QLabel(i18n.t("sidebar_orientation"))
        self.lbl_orient.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px;")
        self.cmb_orient = LinearComboBox()
        self.cmb_orient.setFixedWidth(135)
        self.cmb_orient.setFixedHeight(26)
        self._populate_orientation_options()
        self.cmb_orient.currentIndexChanged.connect(self._on_layout_param_changed)
        row_orient.addWidget(self.lbl_orient)
        row_orient.addStretch(1)
        row_orient.addWidget(self.cmb_orient)
        sc_layout.addLayout(row_orient)

        # Yerleşim
        row_place = QHBoxLayout()
        self.lbl_place = QLabel(i18n.t("sidebar_placement"))
        self.lbl_place.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px;")
        self.cmb_place = LinearComboBox()
        self.cmb_place.setFixedWidth(135)
        self.cmb_place.setFixedHeight(26)
        self._populate_placement_options()
        self.cmb_place.currentIndexChanged.connect(self._on_layout_param_changed)
        row_place.addWidget(self.lbl_place)
        row_place.addStretch(1)
        row_place.addWidget(self.cmb_place)
        sc_layout.addLayout(row_place)

        scroll_layout.addWidget(sheet_card)

        # Dil değişimini dinle
        i18n.language_changed.connect(self._on_language_changed)

        # C) GOST DURUM KARTI (Notion Callout)
        self.status_callout = QFrame()
        self.status_callout.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.COLOR_SUCCESS_BG};
                border: 1px solid {theme.COLOR_SUCCESS_BORDER};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        callout_layout = QVBoxLayout(self.status_callout)
        callout_layout.setContentsMargins(8, 8, 8, 8)
        callout_layout.setSpacing(4)

        self.lbl_callout_title = QLabel(i18n.t("sidebar_status_compliant"))
        self.lbl_callout_title.setStyleSheet(f"font-weight: 600; color: {theme.COLOR_SUCCESS}; font-size: 11px;")
        self.lbl_callout_desc = QLabel(i18n.t("sidebar_status_compliant_desc"))
        self.lbl_callout_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 10px;")
        self.lbl_callout_desc.setWordWrap(True)

        callout_layout.addWidget(self.lbl_callout_title)
        callout_layout.addWidget(self.lbl_callout_desc)
        scroll_layout.addWidget(self.status_callout)

        scroll_layout.addStretch(1)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1)

        # 3. ALT BİLGİ (Footer)
        footer_layout = QHBoxLayout()
        lbl_version = QLabel(f"KM Studio v{APP_VERSION} · Linear Edition")
        lbl_version.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 10px;")
        footer_layout.addWidget(lbl_version)
        main_layout.addLayout(footer_layout)

    def _populate_tables(self):
        modules = [m for m in TableRegistry.all() if getattr(m, "is_active", True)]
        for i, mod in enumerate(modules):
            item = TableNavItem(mod, is_active=(i == 0), count=0)
            item.clicked.connect(lambda checked=False, m_id=mod.id: self._select_module(m_id))
            self._nav_items[mod.id] = item
            self.tables_layout.addWidget(item)

    def _select_module(self, module_id: str):
        for m_id, item in self._nav_items.items():
            item.set_active_state(m_id == module_id)
        self.table_selected.emit(module_id)

    def set_active_module(self, module_id: str):
        for m_id, item in self._nav_items.items():
            item.set_active_state(m_id == module_id)

    def set_item_count(self, module_id: str, count: int):
        if module_id in self._nav_items:
            self._nav_items[module_id].set_count(count)

    def _show_workspace_menu(self):
        """Çalışma alanı / proje açılır menüsünü gösterir."""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtCore import QPoint
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 6px;
                padding: 4px;
                font-size: 12px;
            }}
            QMenu::item {{
                padding: 6px 14px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {theme.BG_SURFACE_HOVER};
                color: {theme.TEXT_PRIMARY};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {theme.BORDER_SUBTLE};
                margin: 4px 6px;
            }}
        """)

        act_header = menu.addAction("📁 KM Proje Çizimleri (Aktif)")
        act_header.setEnabled(False)
        menu.addSeparator()

        parent_win = self.window()
        act_search = menu.addAction(icons.get_icon(icons.ICON_SEARCH, color=icons.COLOR_NEUTRAL), "🔍 Tablo Ara... (Ctrl+K)")
        if parent_win and hasattr(parent_win, "_open_quick_switcher"):
            act_search.triggered.connect(parent_win._open_quick_switcher)

        act_about = menu.addAction(icons.get_icon(icons.ICON_INFO, color=icons.COLOR_NEUTRAL), "ℹ️ Hakkında & Bilgi")
        if parent_win and hasattr(parent_win, "_open_about_dialog"):
            act_about.triggered.connect(parent_win._open_about_dialog)

        menu.exec(self.btn_more.mapToGlobal(QPoint(0, self.btn_more.height() + 2)))

    def _filter_items(self, query: str):
        q = query.strip().lower()
        for item in self._nav_items.values():
            disp_title = item.lbl_name.text().lower()
            raw_title = item.module.name.lower()
            mod_id = item.module.id.lower()
            visible = not q or q in disp_title or q in raw_title or q in mod_id
            item.setVisible(visible)

    def _populate_placement_options(self):
        """Yerleşim seçeneklerini dile uygun doldurur."""
        self.cmb_place.blockSignals(True)
        self.cmb_place.clear()
        options = [
            (TablePlacement.ABOVE_TITLEBLOCK, i18n.t("placement_above_titleblock")),
            (TablePlacement.TOP_RIGHT, i18n.t("placement_top_right")),
            (TablePlacement.TOP_LEFT, i18n.t("placement_top_left")),
            (TablePlacement.CENTER_SHEET, i18n.t("placement_center_sheet")),
            (TablePlacement.STANDALONE, i18n.t("placement_standalone")),
        ]
        for enum_val, label in options:
            self.cmb_place.addItem(label, userData=enum_val)

        # Mevcut seçimi koru
        matched = False
        for idx in range(self.cmb_place.count()):
            if self.cmb_place.itemData(idx) == self._layout_config.placement:
                self.cmb_place.setCurrentIndex(idx)
                matched = True
                break
        if not matched:
            self.cmb_place.setCurrentIndex(0)
        self.cmb_place.blockSignals(False)

    def _populate_orientation_options(self):
        curr_orient = getattr(self, "_layout_config", None).orientation if hasattr(self, "_layout_config") and self._layout_config else SheetOrientation.LANDSCAPE
        self.cmb_orient.blockSignals(True)
        self.cmb_orient.clear()
        self.cmb_orient.addItem(i18n.t("orient_landscape"), SheetOrientation.LANDSCAPE)
        self.cmb_orient.addItem(i18n.t("orient_portrait"), SheetOrientation.PORTRAIT)
        if curr_orient == SheetOrientation.PORTRAIT:
            self.cmb_orient.setCurrentIndex(1)
        else:
            self.cmb_orient.setCurrentIndex(0)
        self.cmb_orient.blockSignals(False)

    def _on_layout_param_changed(self):
        size_str = self.cmb_size.currentText()
        size_map = {
            "A3": SheetSize.A3, "A4": SheetSize.A4, "A2": SheetSize.A2,
            "A1": SheetSize.A1, "A0": SheetSize.A0
        }
        self._layout_config.size = size_map.get(size_str, SheetSize.A3)

        orient_data = self.cmb_orient.currentData()
        if orient_data:
            self._layout_config.orientation = orient_data
        else:
            orient_str = self.cmb_orient.currentText()
            self._layout_config.orientation = (
                SheetOrientation.PORTRAIT if "Dikey" in orient_str or "Portrait" in orient_str or "Книжн" in orient_str else SheetOrientation.LANDSCAPE
            )

        place_val = self.cmb_place.currentData()
        if place_val:
            self._layout_config.placement = place_val
        else:
            place_str = self.cmb_place.currentText()
            if "Yalnızca" in place_str or "Standalone" in place_str or "Только" in place_str:
                self._layout_config.placement = TablePlacement.STANDALONE
            elif "Sol" in place_str or "Left" in place_str or "левый" in place_str:
                self._layout_config.placement = TablePlacement.TOP_LEFT
            elif "Sağ Üst" in place_str or "Top-Right" in place_str or "правый" in place_str:
                self._layout_config.placement = TablePlacement.TOP_RIGHT
            elif "Orta" in place_str or "Center" in place_str or "центр" in place_str:
                self._layout_config.placement = TablePlacement.CENTER_SHEET
            else:
                self._layout_config.placement = TablePlacement.ABOVE_TITLEBLOCK

        self.layout_config_changed.emit(self._layout_config)

    def set_layout_config(self, config: LayoutConfig):
        """Dışarıdan (örneğin tablo değişiminde) pafta ayarlarını günceller."""
        self._layout_config = config
        self.cmb_size.blockSignals(True)
        self.cmb_orient.blockSignals(True)
        self.cmb_place.blockSignals(True)

        size_rev_map = {
            SheetSize.A3: "A3", SheetSize.A4: "A4", SheetSize.A2: "A2",
            SheetSize.A1: "A1", SheetSize.A0: "A0"
        }
        self.cmb_size.setCurrentText(size_rev_map.get(config.size, "A3"))

        if config.orientation == SheetOrientation.PORTRAIT:
            self.cmb_orient.setCurrentIndex(1)
        else:
            self.cmb_orient.setCurrentIndex(0)

        matched = False
        for idx in range(self.cmb_place.count()):
            if self.cmb_place.itemData(idx) == config.placement:
                self.cmb_place.setCurrentIndex(idx)
                matched = True
                break
        if not matched:
            if config.placement == TablePlacement.STANDALONE:
                self.cmb_place.setCurrentIndex(4)
            else:
                self.cmb_place.setCurrentIndex(0)

        self.cmb_size.blockSignals(False)
        self.cmb_orient.blockSignals(False)
        self.cmb_place.blockSignals(False)

    def _on_language_changed(self, lang_code: str):
        """Dil değiştiğinde sol sekmedeki başlıkları ve seçenekleri dinamik günceller."""
        if hasattr(self, "lbl_ws_title"):
            self.lbl_ws_title.setText(i18n.t("sidebar_workspace_title"))
        if hasattr(self, "txt_filter"):
            self.txt_filter.setPlaceholderText(i18n.t("sidebar_filter_placeholder"))
        self.lbl_sec_tables.setText(i18n.t("sidebar_tables_header"))
        self.lbl_sec_sheet.setText(i18n.t("sidebar_sheet_header"))
        self.lbl_size.setText(i18n.t("sidebar_size"))
        self.lbl_orient.setText(i18n.t("sidebar_orientation"))
        self.lbl_place.setText(i18n.t("sidebar_placement"))
        for item in self._nav_items.values():
            item.update_title()
        self._populate_orientation_options()
        self._populate_placement_options()
        if hasattr(self, "lbl_callout_title") and hasattr(self, "lbl_callout_desc"):
            self.lbl_callout_title.setText(i18n.t("sidebar_status_compliant"))
            self.lbl_callout_desc.setText(i18n.t("sidebar_status_compliant_desc"))

    def set_status_message(self, is_valid: bool, msg: str):
        if is_valid:
            self.status_callout.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme.COLOR_SUCCESS_BG};
                    border: 1px solid {theme.COLOR_SUCCESS_BORDER};
                    border-radius: 6px;
                    padding: 6px;
                }}
            """)
            if hasattr(self, "lbl_callout_title"):
                self.lbl_callout_title.setText(i18n.t("sidebar_status_compliant"))
            self.lbl_callout_desc.setText(msg or i18n.t("sidebar_status_compliant_desc"))
        else:
            self.status_callout.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme.COLOR_WARNING_BG};
                    border: 1px solid {theme.COLOR_WARNING_BORDER};
                    border-radius: 6px;
                    padding: 6px;
                }}
            """)
            if hasattr(self, "lbl_callout_title"):
                self.lbl_callout_title.setText(f"▲ {i18n.t('validation_warn_title')}")
            self.lbl_callout_desc.setText(msg or i18n.t("sidebar_status_warning_desc"))
