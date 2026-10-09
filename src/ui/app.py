"""
KM Tablo Oluşturucu - Eski Ana Uygulama Penceresi (KmMainWindow) [ESKİ / DEPRECATED].
NOT: Kullanıcı kararıyla UI v2 (src.ui_v2.KmLinearMainWindow) aktif hale getirilmiş ve v1 iptal edilmiştir.
Bu modül geriye dönük test uyumluluğu için korunmaktadır.
"""
import os
from typing import Optional, Any
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QComboBox, QMessageBox, QFileDialog, QTabWidget, QDialog
)

from src.config.sheet_config import LayoutConfig, DEFAULT_LAYOUT_CONFIG
from src.config.table_config import TableConfig, DEFAULT_TABLE_CONFIG
from src.contracts.table_module import TableModule
from src.export.dxf_exporter import DxfExporter
from src.models.registry import TableRegistry
from src.models.table import Table
import src.tables  # Modülleri TableRegistry'ye kaydet
from src.ui import theme
from src.ui.cad_workspace import CadWorkspacePanel
from src.ui.header import ModernAppHeader
from src.ui.i18n import i18n
from src.ui.quick_switcher import QuickTableSwitcherDialog
from src.ui.sidebar import ModernNavigationSidebar
from src.ui.workspace import MainWorkspaceArea


class KmMainWindow(QMainWindow):
    """
    KM CAD Studio Ana Masaüstü Penceresi.
    Tamamen yeniden yapılandırılmış modern application shell, bağımsız kart çalışma alanları
    ve canlı CAD çizim tuvalini yönetir.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KM Tablo Oluşturucu · GOST 21.502 / KM CAD Studio")
        self.resize(1366, 800)
        self.setMinimumSize(1024, 600)

        # Temel Yapılandırma ve Servisler
        self.table_config: TableConfig = DEFAULT_TABLE_CONFIG
        self.layout_config: LayoutConfig = DEFAULT_LAYOUT_CONFIG
        self.dxf_exporter = DxfExporter()
        self._last_cursor_coords = (0.0, 0.0)

        # Aktif Modül
        all_modules = TableRegistry.all()
        if not all_modules:
            raise RuntimeError("Sisteme kayıtlı hiçbir TableModule bulunamadı!")
        self.active_module: TableModule = all_modules[0]
        self.current_document: Any = self.active_module.create_default_document()
        self.current_table: Optional[Table] = None

        # UI Kurulumu
        self._build_ui()
        self._refresh_table_and_preview()

        # Global Dil Değişimi Dinleyicisi
        i18n.language_changed.connect(self._on_language_changed)

    @property
    def canvas(self):
        """Geriye dönük test uyumluluğu için CAD tuval referansı."""
        return self.cad_workspace.canvas

    @property
    def current_items(self):
        """Aktif dokümanın eleman listesi (Geriye dönük test uyumluluğu)."""
        if hasattr(self.current_document, "items"):
            return self.current_document.items
        elif isinstance(self.current_document, (list, tuple)):
            return self.current_document
        return []

    @current_items.setter
    def current_items(self, val):
        if hasattr(self.current_document, "items"):
            self.current_document.items = val
        else:
            self.current_document = val

    # --------------------------------------------------------------------------
    # MODERN ARAYÜZ KURULUMU (RECONSTRUCTED APP SHELL)
    # --------------------------------------------------------------------------
    def _build_ui(self):
        # 1. Native Menü Çubuğu (MenuBar)
        self._build_menu_bar()

        # Ana Zemin
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 2. Modern Stüdyo Başlık Çubuğu (ModernAppHeader)
        self.modern_header = ModernAppHeader(central_widget)
        self.modern_header.quick_switch_requested.connect(self._open_quick_switcher)
        self.modern_header.toggle_sidebar_requested.connect(self._toggle_table_explorer)
        self.modern_header.export_requested.connect(self._on_export_dxf)
        self.modern_header.fit_view_requested.connect(self._on_fit_view)
        self.modern_header.load_samples_requested.connect(self._on_action_load_samples)
        self.modern_header.language_changed.connect(lambda l: i18n.set_language(l))
        root_layout.addWidget(self.modern_header)

        # Geriye dönük uyumluluk referansları
        self.header_frame = self.modern_header
        self.btn_nav_toggle = self.modern_header.btn_toggle_sidebar
        self.btn_quick_switch = self.modern_header.btn_quick_switch
        self.cb_lang = self.modern_header.cb_lang
        self.lbl_active_table_title = QLabel(self.active_module.name, self.modern_header)
        self.lbl_active_table_title.setVisible(False)
        self.cb_table_type = QComboBox(self.modern_header)
        self.cb_table_type.setVisible(False)
        self._populate_table_registry_options()
        self.cb_table_type.currentIndexChanged.connect(self._on_table_combo_changed)

        # 3. Ana Çalışma Alanı: Sol Modern Sidebar + Ana Kart Alanı (Splitter)
        body_container = QWidget(central_widget)
        body_layout = QHBoxLayout(body_container)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.root_splitter = QSplitter(Qt.Orientation.Horizontal, body_container)
        self.root_splitter.setStyleSheet(f"background-color: {theme.COLOR_BG_DARK};")

        # Sol Panel: ModernNavigationSidebar
        self.sidebar = ModernNavigationSidebar(self.root_splitter)
        self.sidebar.table_selected.connect(self._switch_to_table_id)
        self.sidebar.toggle_requested.connect(self._toggle_table_explorer)
        self.sidebar.set_active_table(self.active_module.id)
        self.table_explorer = self.sidebar  # Geriye dönük test uyumluluğu
        self.root_splitter.addWidget(self.sidebar)

        # Orta & Sağ: MainWorkspaceArea
        self.workspace = MainWorkspaceArea(self.root_splitter)
        self.main_splitter = self.workspace.splitter  # Geriye dönük test uyumluluğu

        # Editör Alanı
        self.editor_container = self.workspace.editor_card.content_container
        self.left_tabs = QTabWidget(self.editor_container)
        self.left_tabs.setStyleSheet("QTabWidget::pane { border: none; } QTabBar { height: 0px; }")
        self.editor_widget = self.active_module.create_editor(self.left_tabs)
        self._connect_editor_signals(self.editor_widget)
        self.left_tabs.addTab(self.editor_widget, i18n.t("tab_elements"))
        self.workspace.editor_card.set_content(self.left_tabs)

        # CAD Preview Alanı
        self.cad_workspace = CadWorkspacePanel(self.workspace.cad_card.content_container)
        self.cad_workspace.layout_changed.connect(self._on_layout_changed)
        self.cad_workspace.export_requested.connect(self._on_export_dxf)
        self.cad_workspace.cursor_pos_changed.connect(self._on_cursor_coords_changed)
        self.cad_workspace.zoom_changed.connect(self._on_zoom_changed)
        self.layout_panel = self.cad_workspace  # Geriye dönük test uyumluluğu
        self.workspace.cad_card.set_content(self.cad_workspace)

        # Splitter başlangıç oranları
        self.root_splitter.addWidget(self.workspace)
        self.root_splitter.setSizes([260, 1106])
        self.root_splitter.setCollapsible(0, True)
        self.root_splitter.setCollapsible(1, False)

        body_layout.addWidget(self.root_splitter)
        root_layout.addWidget(body_container, 1)

        # 4. Modern Durum Çubuğu (24px)
        self._build_status_bar()

    def _build_menu_bar(self):
        """Native masaüstü menü çubuğu."""
        menubar = self.menuBar()
        menubar.clear()

        # A) Dosya Menüsü
        self.menu_file = menubar.addMenu(i18n.t("menu_file"))
        act_new = QAction(i18n.t("action_new"), self)
        act_new.setShortcut(QKeySequence.StandardKey.New)
        act_new.triggered.connect(self._on_action_new)
        self.menu_file.addAction(act_new)

        self.menu_file.addSeparator()
        self.act_export = QAction(i18n.t("action_export_dxf"), self)
        self.act_export.setShortcut(QKeySequence("Ctrl+E"))
        self.act_export.triggered.connect(self._on_export_dxf)
        self.menu_file.addAction(self.act_export)

        self.menu_file.addSeparator()
        act_exit = QAction(i18n.t("action_exit"), self)
        act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        act_exit.triggered.connect(self.close)
        self.menu_file.addAction(act_exit)

        # B) Düzen Menüsü
        self.menu_edit = menubar.addMenu(i18n.t("menu_edit"))
        act_add_row = QAction(f"+ {i18n.t('action_add_row')}", self)
        act_add_row.setShortcut(QKeySequence("Ctrl+Ins"))
        act_add_row.triggered.connect(self._on_action_add_row)
        self.menu_edit.addAction(act_add_row)

        act_del_row = QAction(f"🗑 {i18n.t('action_delete_row')}", self)
        act_del_row.setShortcut(QKeySequence("Ctrl+Del"))
        act_del_row.triggered.connect(self._on_action_delete_row)
        self.menu_edit.addAction(act_del_row)

        self.menu_edit.addSeparator()
        act_up = QAction(f"▲ {i18n.t('action_move_up')}", self)
        act_up.setShortcut(QKeySequence("Alt+Up"))
        act_up.triggered.connect(lambda: self._on_action_move_row(-1))
        self.menu_edit.addAction(act_up)

        act_down = QAction(f"▼ {i18n.t('action_move_down')}", self)
        act_down.setShortcut(QKeySequence("Alt+Down"))
        act_down.triggered.connect(lambda: self._on_action_move_row(1))
        self.menu_edit.addAction(act_down)

        # C) Tablolar Menüsü
        self.menu_tables = menubar.addMenu(i18n.t("menu_tables"))
        self.act_quick_switch = QAction(f"🔍 {i18n.t('action_quick_switch')}", self)
        self.act_quick_switch.setShortcut(QKeySequence("Ctrl+T"))
        self.act_quick_switch.triggered.connect(self._open_quick_switcher)
        self.menu_tables.addAction(self.act_quick_switch)
        self.menu_tables.addSeparator()

        for mod in TableRegistry.all():
            act_tbl = QAction(f"{mod.name}", self)
            act_tbl.setData(mod.id)
            act_tbl.triggered.connect(lambda chk=False, mid=mod.id: self._switch_to_table_id(mid))
            self.menu_tables.addAction(act_tbl)

        # D) Görünüm Menüsü
        self.menu_view = menubar.addMenu(i18n.t("menu_view"))
        self.act_toggle_explorer = QAction(i18n.t("action_toggle_explorer"), self)
        self.act_toggle_explorer.setShortcut(QKeySequence("Ctrl+B"))
        self.act_toggle_explorer.triggered.connect(self._toggle_table_explorer)
        self.menu_view.addAction(self.act_toggle_explorer)

        self.act_toggle_preview = QAction(i18n.t("action_toggle_preview"), self)
        self.act_toggle_preview.setShortcut(QKeySequence("Ctrl+Shift+P"))
        self.act_toggle_preview.triggered.connect(self._toggle_preview)
        self.menu_view.addAction(self.act_toggle_preview)

        self.menu_view.addSeparator()
        self.act_fit = QAction(i18n.t("action_fit_view"), self)
        self.act_fit.setShortcut(QKeySequence("F4"))
        self.act_fit.triggered.connect(self._on_fit_view)
        self.menu_view.addAction(self.act_fit)

        self.act_actual = QAction(i18n.t("action_zoom_actual"), self)
        self.act_actual.setShortcut(QKeySequence("Ctrl+0"))
        self.act_actual.triggered.connect(self._on_zoom_actual)
        self.menu_view.addAction(self.act_actual)

        # E) Araçlar Menüsü
        self.menu_tools = menubar.addMenu(i18n.t("menu_tools"))
        act_samples = QAction("⟲ " + i18n.t("load_samples"), self)
        act_samples.triggered.connect(self._on_action_load_samples)
        self.menu_tools.addAction(act_samples)

        # F) Yardım Menüsü
        self.menu_help = menubar.addMenu(i18n.t("menu_help"))
        act_about = QAction(i18n.t("action_about"), self)
        act_about.triggered.connect(self._show_about_dialog)
        self.menu_help.addAction(act_about)

    def _build_status_bar(self):
        """24px Kompakt Durum Çubuğu."""
        status = self.statusBar()
        status.setFixedHeight(24)

        # Sol: Canlı Validasyon Göstergesi
        self.lbl_status = QLabel("", status)
        self.lbl_status.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.COLOR_SUCCESS}; padding-left: 6px;")
        status.addWidget(self.lbl_status)

        # Orta: Pafta Ebat Bilgisi
        self.lbl_sheet_info = QLabel("ГОСТ 2.301 · A3 Yatay", status)
        self.lbl_sheet_info.setStyleSheet(f"font-size: 10px; color: {theme.COLOR_TEXT_MUTED}; padding-left: 20px; font-weight: 600;")
        status.addPermanentWidget(self.lbl_sheet_info)

        # Sağ: CAD İmleç Koordinatları ve Telemetri
        self.lbl_coords = QLabel("GOST 2.301 • X: -111.0 mm | Y: 257.0 mm | Zoom: %100 | 🔒 Snap | ⛶", status)
        self.lbl_coords.setStyleSheet(f"font-size: 10px; color: {theme.COLOR_TEXT_MUTED}; font-family: Consolas, monospace; padding-right: 8px; font-weight: 600;")
        status.addPermanentWidget(self.lbl_coords)

    # --------------------------------------------------------------------------
    # MODÜL VE TABLO GEÇİŞ YÖNETİMİ
    # --------------------------------------------------------------------------
    def _switch_to_table_id(self, table_id: str):
        target_mod = TableRegistry.get(table_id)
        if target_mod:
            self._set_active_module(target_mod)

    def _set_active_module(self, module: TableModule):
        """Aktif tablo modülünü dinamik olarak değiştirir."""
        if self.active_module and self.active_module.id == module.id:
            return

        self.active_module = module
        self.current_document = module.create_default_document()

        # Üst başlığı ve gezgini güncelle
        self.lbl_active_table_title.setText(module.name)
        self.modern_header.set_active_table_title(module.name)
        self.sidebar.set_active_table(module.id)

        # Combobox seçimini senkronize et
        self.cb_table_type.blockSignals(True)
        idx = self.cb_table_type.findData(module.id)
        if idx >= 0:
            self.cb_table_type.setCurrentIndex(idx)
        self.cb_table_type.blockSignals(False)

        # Editör widget'ını yenile
        old_widget = self.editor_widget
        self.editor_widget = module.create_editor(self.left_tabs)
        self._connect_editor_signals(self.editor_widget)

        self.left_tabs.removeTab(0)
        self.left_tabs.insertTab(0, self.editor_widget, i18n.t("tab_elements"))
        self.left_tabs.setCurrentIndex(0)

        if old_widget:
            old_widget.deleteLater()

        # Workspace başlığını güncelle
        self.workspace.editor_card.lbl_title.setText(f"📋 {module.name}")

        # Preview desteğini kontrol et
        supports_prev = getattr(module, "supports_preview", True)
        self.cad_workspace.setVisible(supports_prev)
        self.workspace.cad_card.setVisible(supports_prev)

        self._refresh_table_and_preview()
        if supports_prev:
            self.cad_workspace.fit_to_view()

    def _open_quick_switcher(self):
        """Ctrl+T ile açılan hızlı arama diyaloğu."""
        dlg = QuickTableSwitcherDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.selected_table_id:
                self._switch_to_table_id(dlg.selected_table_id)

    def _toggle_table_explorer(self):
        show = self.sidebar.isHidden()
        self.sidebar.setVisible(show)

    def _toggle_preview(self):
        show = self.cad_workspace.isHidden()
        self.cad_workspace.setVisible(show)
        self.workspace.cad_card.setVisible(show)

    def _populate_table_registry_options(self):
        self.cb_table_type.blockSignals(True)
        self.cb_table_type.clear()
        registered = TableRegistry.all()
        for mod in registered:
            self.cb_table_type.addItem(f"✓ {mod.name}", mod.id)

        known_future = [
            ("steel_spec", "⏳ Техническая спецификация стали (ГОСТ 21.502)"),
            ("steel_consumption", "⏳ Ведомость расхода стали (ГОСТ 21.501)"),
            ("hardware_schedule", "⏳ Ведомость метизов / Болты (ГОСТ 21.502)"),
        ]
        reg_ids = {m.id for m in registered}
        for fid, flabel in known_future:
            if fid not in reg_ids:
                self.cb_table_type.addItem(flabel, fid)

        if self.active_module:
            idx = self.cb_table_type.findData(self.active_module.id)
            if idx >= 0:
                self.cb_table_type.setCurrentIndex(idx)
        self.cb_table_type.blockSignals(False)

    def _on_table_combo_changed(self, idx: int):
        table_id = self.cb_table_type.currentData()
        target_mod = TableRegistry.get(table_id)
        if target_mod:
            self._set_active_module(target_mod)
        else:
            name = self.cb_table_type.currentText().replace("⏳ ", "")
            self.lbl_status.setText(f"Bilgi: '{name}' tablosu geliştirme yol haritasındadır.")

    # --------------------------------------------------------------------------
    # SİNYAL VE EVENT BAĞLANTILARI
    # --------------------------------------------------------------------------
    def _connect_editor_signals(self, editor: QWidget):
        if hasattr(editor, "document_changed"):
            editor.document_changed.connect(self._on_document_changed)
        elif hasattr(editor, "items_changed"):
            editor.items_changed.connect(self._on_items_changed)

    def _on_document_changed(self, doc: Any):
        self.current_document = doc
        self._refresh_table_and_preview()

    def _on_items_changed(self, items: Any):
        if hasattr(self.current_document, "items"):
            self.current_document.items = items
        else:
            self.current_document = items
        self._refresh_table_and_preview()

    def _on_layout_changed(self, new_layout_config: LayoutConfig):
        self.layout_config = new_layout_config
        placement_val = getattr(new_layout_config.placement, "value", str(new_layout_config.placement))
        short_placement = placement_val.split(":")[-1].strip() if ":" in placement_val else placement_val
        orient_val = getattr(new_layout_config.orientation, "value", str(new_layout_config.orientation)).split()[0]
        size_val = getattr(new_layout_config.size, "value", str(new_layout_config.size))
        self.lbl_sheet_info.setText(f"ГОСТ 2.301 · {size_val} {orient_val} · {short_placement}")
        self.sidebar.lbl_doc_info.setText(f"ГОСТ 2.301 · {size_val} {orient_val} · {short_placement}")
        self.cad_workspace.set_data(self.current_table, self.table_config, self.layout_config, auto_fit=True)

    def _on_cursor_coords_changed(self, cad_x: float, cad_y: float):
        self._last_cursor_coords = (cad_x, cad_y)
        pct = getattr(self, "_current_zoom_pct", 100)
        self.lbl_coords.setText(f"GOST 2.301 • X: {cad_x:+.1f} mm | Y: {cad_y:+.1f} mm | ZOOM: {pct}% | 🔒 Snap | ⛶")

    def _on_zoom_changed(self, pct: int):
        self._current_zoom_pct = pct
        cad_x, cad_y = getattr(self, "_last_cursor_coords", (0.0, 0.0))
        self.lbl_coords.setText(f"GOST 2.301 • X: {cad_x:+.1f} mm | Y: {cad_y:+.1f} mm | ZOOM: {pct}% | 🔒 Snap | ⛶")

    def _on_fit_view(self):
        self.cad_workspace.fit_to_view()

    def _on_zoom_actual(self):
        self.cad_workspace.zoom_actual()

    def _on_zoom_in(self):
        self.cad_workspace.zoom_in()

    def _on_zoom_out(self):
        self.cad_workspace.zoom_out()

    def _on_lang_combo_changed(self):
        lang = self.cb_lang.currentData()
        if lang:
            i18n.set_language(lang)

    def _on_language_changed(self, lang_code: str):
        self._build_menu_bar()
        self.left_tabs.setTabText(0, i18n.t("tab_elements"))
        self.modern_header.set_active_table_title(self.active_module.name)
        self.modern_header.update_translations()
        self.lbl_active_table_title.setText(self.active_module.name)
        if hasattr(self, "cb_lang"):
            self.cb_lang.blockSignals(True)
            idx = self.cb_lang.findData(lang_code)
            if idx >= 0:
                self.cb_lang.setCurrentIndex(idx)
            self.cb_lang.blockSignals(False)
        self._refresh_table_and_preview()
        self._on_layout_changed(self.layout_config)

    # --------------------------------------------------------------------------
    # EYLEM VE İŞLEM METOTLARI
    # --------------------------------------------------------------------------
    def _on_action_new(self):
        self.current_document = self.active_module.create_default_document()
        if hasattr(self.editor_widget, "set_document"):
            self.editor_widget.set_document(self.current_document)
        self._refresh_table_and_preview()

    def _on_action_add_row(self):
        if hasattr(self.editor_widget, "_add_row"):
            self.editor_widget._add_row()

    def _on_action_delete_row(self):
        if hasattr(self.editor_widget, "_delete_selected_row"):
            self.editor_widget._delete_selected_row()

    def _on_action_move_row(self, direction: int):
        if hasattr(self.editor_widget, "_move_row"):
            self.editor_widget._move_row(direction)

    def _on_action_load_samples(self):
        if hasattr(self.editor_widget, "_reset_to_samples"):
            self.editor_widget._reset_to_samples()

    def _show_about_dialog(self):
        QMessageBox.about(
            self,
            i18n.t("action_about"),
            "<h3>KM CAD Studio (ГОСТ / КМ)</h3>"
            "<p>Rusya ve BDT standartlarına uygun milimetrik çelik yapı çizelgeleri ve AutoCAD DXF üretici masaüstü yazılımı.</p>"
            "<p><b>Mimari:</b> Modern Shell, Pluggable TableModule & TableRegistry Altyapısı</p>"
        )

    # --------------------------------------------------------------------------
    # ÇİZİM VE DIŞA AKTARMA (REFRESH & EXPORT)
    # --------------------------------------------------------------------------
    def _refresh_table_and_preview(self):
        val_res = self.active_module.validate(self.current_document)
        self.sidebar.update_validation_state(val_res.is_valid, val_res.summary_message)

        if not val_res.is_valid:
            self.lbl_status.setText(i18n.t("status_warning", msg=val_res.summary_message))
            self.lbl_status.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.COLOR_DANGER}; padding-left: 6px;")
        else:
            doc = self.current_document
            if hasattr(doc, "items") and not callable(doc.items):
                count = len(doc.items)
            elif isinstance(doc, (list, tuple)):
                count = len(doc)
            elif isinstance(doc, dict) and "records" in doc:
                count = len(doc["records"])
            else:
                count = 0
            self.lbl_status.setText(i18n.t("status_ready", count=count))
            self.lbl_status.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.COLOR_SUCCESS}; padding-left: 6px;")

        self.current_table = self.active_module.build_table(self.current_document)
        self.cad_workspace.set_data(self.current_table, self.table_config, self.layout_config, auto_fit=False)

    def _on_export_dxf(self):
        val_res = self.active_module.validate(self.current_document)
        if not val_res.is_valid:
            QMessageBox.warning(
                self,
                i18n.t("validation_warn_title"),
                f"{i18n.t('status_warning', msg=val_res.summary_message)}"
            )
            return

        default_filename = self.active_module.default_export_filename(self.current_document)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "AutoCAD DXF",
            default_filename,
            "AutoCAD DXF Dosyası (*.dxf)"
        )
        if not file_path:
            return

        try:
            success = self.dxf_exporter.export(
                table=self.current_table,
                output_path=file_path,
                table_config=self.table_config,
                layout_config=self.layout_config
            )
            if success:
                fname = os.path.basename(file_path)
                self.lbl_status.setText(i18n.t("status_exported", filename=fname))
                self.lbl_status.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.COLOR_SUCCESS}; padding-left: 6px;")
                QMessageBox.information(
                    self,
                    i18n.t("export_success_title"),
                    i18n.t("export_success_msg", path=file_path)
                )
        except Exception as e:
            self.lbl_status.setText(f"Hata: {str(e)}")
            self.lbl_status.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.COLOR_DANGER}; padding-left: 6px;")
            QMessageBox.critical(self, i18n.t("error_title"), f"DXF dosyası kaydedilirken hata oluştu:\n{str(e)}")
