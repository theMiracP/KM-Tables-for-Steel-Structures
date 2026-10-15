"""
KM Tablo Oluşturucu - Linear / Notion SaaS Ana Penceresi (KmLinearMainWindow).
SaaS tarzı temiz düzen, Notion doküman gezintisi, canlı CAD tuvali ve floating HUD kontrolleri.
"""
import os
import sys
import subprocess
from typing import Optional, Any
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMessageBox, QFileDialog
)

from src.config.sheet_config import LayoutConfig, DEFAULT_LAYOUT_CONFIG
from src.config.table_config import TableConfig, DEFAULT_TABLE_CONFIG
from src.contracts.table_module import TableModule
from src.export.dxf_exporter import DxfExporter
from src.export.pdf_exporter import PdfExporter
from src.services.project_manager import ProjectManager
from src.services.undo_manager import UndoManager
from src.models.registry import TableRegistry
from src.models.table import Table
import src.tables  # Modülleri sisteme kaydet

from src.ui.i18n import i18n
from src.ui_v2 import theme_linear as theme
from src.ui_v2.top_bar import LinearTopBar
from src.ui_v2.sidebar import LinearSidebar
from src.ui_v2.editor_wrapper import TableEditorWrapper
from src.ui_v2.cad_panel import CadViewportPanel
from src.ui_v2.status_bar import LinearStatusBar
from src.ui_v2.about_dialog import LinearAboutDialog


class KmLinearMainWindow(QMainWindow):
    """
    Linear & Notion SaaS Mimarisi ile Baştan Tasarlanmış KM CAD Stüdyosu.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KM Studio · GOST 21.502 / Linear CAD Dashboard")
        self.resize(1440, 860)
        self.setMinimumSize(1024, 640)

        # Temel Yapılandırma ve Servisler
        self.table_config: TableConfig = DEFAULT_TABLE_CONFIG
        self.layout_config: LayoutConfig = DEFAULT_LAYOUT_CONFIG
        self.module_layout_configs: dict[str, LayoutConfig] = {}
        self.dxf_exporter = DxfExporter()
        self.pdf_exporter = PdfExporter()
        self.project_manager = ProjectManager()
        self.undo_manager = UndoManager()
        self.current_project_path: Optional[str] = None
        self.module_documents: dict[str, Any] = {}
        self._last_committed_docs: dict[str, Any] = {}

        # Tüm modüllerin dokümanlarını hafızada tut (sekme geçişlerinde veri kaybını önler)
        import copy
        for mod in TableRegistry.all():
            default_doc = mod.create_default_document()
            self.module_documents[mod.id] = default_doc
            self._last_committed_docs[mod.id] = copy.deepcopy(default_doc)

        # Varsayılan Title Block dokümanını pafta antetine bağla (Item 3.2)
        tb_doc = self.module_documents.get("title_block")
        if tb_doc:
            self.layout_config.title_block_doc = tb_doc

        # Aktif Modül ve Doküman
        all_modules = TableRegistry.all()
        if not all_modules:
            raise RuntimeError("Sisteme kayıtlı hiçbir TableModule bulunamadı!")
        self.active_module: TableModule = all_modules[0]
        self.current_document: Any = self.module_documents[self.active_module.id]
        self.current_table: Optional[Table] = None

        # CAD Tuvali Yenileme Debounce Zamanlayıcısı (Kasmayı/takılmayı önler)
        self._cad_debounce_timer = QTimer(self)
        self._cad_debounce_timer.setSingleShot(True)
        self._cad_debounce_timer.setInterval(60)
        self._cad_debounce_timer.timeout.connect(self._do_refresh_table_and_cad)

        # UI Kurulumu
        self._build_ui()
        self._setup_shortcuts()
        self._init_data()

    def _build_ui(self):
        # Global Linear QSS temasını uygula
        self.setStyleSheet(theme.get_linear_stylesheet())

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. ÜST GEZİNME ÇUBUĞU (Linear TopBar)
        self.top_bar = LinearTopBar(central_widget)
        self.top_bar.command_palette_requested.connect(self._open_quick_switcher)
        self.top_bar.export_dxf_requested.connect(self._export_dxf)
        self.top_bar.export_pdf_requested.connect(self._export_pdf)
        self.top_bar.new_project_requested.connect(self._new_project)
        self.top_bar.open_project_requested.connect(self._open_project)
        self.top_bar.save_project_requested.connect(self._save_project)
        self.top_bar.save_project_as_requested.connect(self._save_project_as)
        self.top_bar.toggle_sidebar_requested.connect(self._toggle_sidebar)
        self.top_bar.toggle_cad_requested.connect(self._toggle_cad_panel)
        self.top_bar.about_requested.connect(self._open_about_dialog)
        self.top_bar.settings_requested.connect(self._open_settings_dialog)
        self.top_bar.language_changed.connect(self._on_language_changed)
        root_layout.addWidget(self.top_bar)

        # 2. ANA ÇALIŞMA ALANI (Sidebar + Splitter)
        body_container = QWidget(central_widget)
        body_layout = QHBoxLayout(body_container)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # A) Kenar Çubuğu (Notion Sidebar)
        self.sidebar = LinearSidebar(body_container)
        self.sidebar.table_selected.connect(self._switch_to_module)
        self.sidebar.layout_config_changed.connect(self._on_layout_config_changed)
        body_layout.addWidget(self.sidebar)

        # B) Modern Splitter (Notion Data Grid + CAD Tuvali)
        self.splitter = QSplitter(Qt.Orientation.Horizontal, body_container)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(6)

        # Sol Panel: Veri Tablosu Editörü
        self.editor_wrapper = TableEditorWrapper(self.splitter)
        self.editor_wrapper.setMinimumWidth(320)
        self.editor_wrapper.document_changed.connect(self._on_document_edited)
        self.editor_wrapper.save_preset_requested.connect(self._on_save_preset)
        self.editor_wrapper.load_preset_requested.connect(self._on_load_preset)
        self.editor_wrapper.undo_requested.connect(self.undo_manager.undo)
        self.editor_wrapper.redo_requested.connect(self.undo_manager.redo)
        self.undo_manager.can_undo_changed.connect(self._on_can_undo_changed)
        self.undo_manager.can_redo_changed.connect(self._on_can_redo_changed)
        self.splitter.addWidget(self.editor_wrapper)

        # Sağ Panel: CAD Görünüm Tuvali ve Floating HUD (Varsayılan Açık)
        self.cad_panel = CadViewportPanel(self.splitter)
        self.cad_panel.setMinimumWidth(250)
        self.cad_panel.toggle_requested.connect(self._toggle_cad_panel)
        self.cad_panel.multi_sheet_requested.connect(self._toggle_multi_sheet_layout)
        self.splitter.addWidget(self.cad_panel)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        # Başlangıç bölme oranları (%42 Editör, %58 CAD)
        self._saved_splitter_sizes = [550, 890]
        self.splitter.setSizes(self._saved_splitter_sizes)
        self.top_bar.set_cad_visible(True)
        body_layout.addWidget(self.splitter, 1)

        root_layout.addWidget(body_container, 1)

        # 3. ALT DURUM ÇUBUĞU (Linear StatusBar)
        self.status_bar = LinearStatusBar(central_widget)
        root_layout.addWidget(self.status_bar)

    def _setup_shortcuts(self):
        # Ctrl+K: Quick Table Switcher / Command Palette
        QShortcut(QKeySequence("Ctrl+K"), self, self._open_quick_switcher)
        # Ctrl+B: Toggle Sidebar
        QShortcut(QKeySequence("Ctrl+B"), self, self._toggle_sidebar)
        # Ctrl+J / F10: Toggle CAD Viewport
        QShortcut(QKeySequence("Ctrl+J"), self, self._toggle_cad_panel)
        QShortcut(QKeySequence("F10"), self, self._toggle_cad_panel)
        # Ctrl+E: Export DXF
        QShortcut(QKeySequence("Ctrl+E"), self, self._export_dxf)
        # Ctrl+P: Export PDF (Item 2.3)
        QShortcut(QKeySequence("Ctrl+P"), self, self._export_pdf)
        # Ctrl+N / Ctrl+O / Ctrl+S / Ctrl+Shift+S: Proje Kısayolları (Item 4.1)
        QShortcut(QKeySequence("Ctrl+N"), self, self._new_project)
        QShortcut(QKeySequence("Ctrl+O"), self, self._open_project)
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_project)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self._save_project_as)
        # Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z: Undo/Redo (Item 4.2)
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_manager.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.undo_manager.redo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self.undo_manager.redo)

    def _init_data(self):
        # Tüm modülleri editöre kaydet
        for mod in TableRegistry.all():
            self.editor_wrapper.register_module(mod)

        # İlk modülü yükle
        self._switch_to_module(self.active_module.id)

    def _switch_to_module(self, module_id: str):
        mod = TableRegistry.get(module_id)
        if not mod:
            return

        # Mevcut aktif tablodaki son durumu sakla
        if self.active_module and self.current_document:
            self.module_documents[self.active_module.id] = self.current_document

        self.active_module = mod
        if module_id not in self.module_documents:
            self.module_documents[module_id] = mod.create_default_document()
        self.current_document = self.module_documents[module_id]

        # Her tablo için bağımsız pafta yapılandırması (TASK-10)
        tb_doc = self.module_documents.get("title_block", getattr(self.layout_config, "title_block_doc", None))
        if module_id not in self.module_layout_configs:
            import copy
            from src.config.sheet_config import SheetSize, SheetOrientation, TablePlacement
            cfg = copy.deepcopy(DEFAULT_LAYOUT_CONFIG)
            if module_id in ("change_permission", "title_sheet"):
                cfg.size = SheetSize.A4
                cfg.orientation = SheetOrientation.PORTRAIT
                cfg.placement = TablePlacement.CENTER_SHEET
            cfg.title_block_doc = tb_doc
            self.module_layout_configs[module_id] = cfg
        self.layout_config = self.module_layout_configs[module_id]
        if tb_doc:
            self.layout_config.title_block_doc = tb_doc
        self.sidebar.set_layout_config(self.layout_config)

        # UI bileşenlerini güncelle
        self.top_bar.set_active_module_id(module_id)
        self.sidebar.set_active_module(module_id)
        self.editor_wrapper.show_module(module_id, self.current_document)

        self._refresh_table_and_cad(immediate=True)

    def _on_language_changed(self, lang: str):
        if self.active_module:
            self.top_bar.set_active_module_id(self.active_module.id)

    def _on_document_edited(self, new_doc: Any):
        import copy
        old_doc = self._last_committed_docs.get(self.active_module.id, self.current_document)
        if not self.undo_manager.is_applying:
            self.undo_manager.push_snapshot(
                description=f"Edit {self.active_module.id}",
                module_id=self.active_module.id,
                old_state=old_doc,
                new_state=copy.deepcopy(new_doc),
                apply_fn=self._apply_undone_state
            )

        self._last_committed_docs[self.active_module.id] = copy.deepcopy(new_doc)
        self.current_document = new_doc
        self.module_documents[self.active_module.id] = new_doc

        # Title block metadata synchronization across all tables and multi-sheet layouts (Item 3.2)
        if self.active_module and self.active_module.id == "title_block":
            self.layout_config.title_block_doc = new_doc
            for cfg in self.module_layout_configs.values():
                cfg.title_block_doc = new_doc
        self._refresh_table_and_cad()

    def _apply_undone_state(self, module_id: str, state: Any):
        """Undo / Redo işlemi sonucunda ilgili modülün durumunu geri yükler."""
        import copy
        self._last_committed_docs[module_id] = copy.deepcopy(state)
        self.module_documents[module_id] = copy.deepcopy(state)
        if module_id == "title_block":
            self.layout_config.title_block_doc = state
            for cfg in self.module_layout_configs.values():
                cfg.title_block_doc = state
        if self.active_module and self.active_module.id == module_id:
            self.current_document = state
            self.editor_wrapper.show_module(module_id, state)
            self._refresh_table_and_cad(immediate=True)
        else:
            self._refresh_table_and_cad()

    def _on_can_undo_changed(self, can_undo: bool):
        self.editor_wrapper.set_undo_redo_enabled(can_undo, self.undo_manager.can_redo())

    def _on_can_redo_changed(self, can_redo: bool):
        self.editor_wrapper.set_undo_redo_enabled(self.undo_manager.can_undo(), can_redo)

    def closeEvent(self, event):
        self.undo_manager.clear()
        super().closeEvent(event)

    def _on_layout_config_changed(self, new_config: LayoutConfig):
        self.layout_config = new_config
        if self.active_module:
            self.module_layout_configs[self.active_module.id] = new_config
        self._refresh_table_and_cad(immediate=True)

    def _refresh_table_and_cad(self, immediate: bool = False):
        """CAD tuvali ve tablo yenilemesini yönetir. Sık güncellemelerde debounce uygular."""
        if immediate:
            self._cad_debounce_timer.stop()
            self._do_refresh_table_and_cad()
        else:
            self._cad_debounce_timer.start()

    def _do_refresh_table_and_cad(self):
        """CAD tuvali ve tablo yenilemesini asıl gerçekleştiren metot."""
        if not self.active_module or not self.current_document:
            return

        # 1. Modülün generic Table nesnesini inşa et
        self._current_multi_sheet_layout = None
        self.cad_panel.set_multi_sheet_mode(False)
        try:
            self.current_table = self.active_module.build_table(self.current_document)
        except Exception as e:
            self.status_bar.set_status(f"Tablo oluşturma hatası: {e}", is_success=False)
            return

        # 2. Canlı CAD Tuvalini Güncelle
        if self.current_table and self.active_module.supports_preview:
            self.cad_panel.set_data(
                table=self.current_table,
                layout_config=self.layout_config,
                auto_fit=False
            )

        # 3. Doğrulama (Validation)
        res = self.active_module.validate(self.current_document)
        self.top_bar.set_validation_status(res.is_valid, "GOST Uyumlu" if res.is_valid else "Uyarı")
        self.sidebar.set_status_message(res.is_valid, res.summary_message)
        self.status_bar.set_status("CAD Tuvali Güncellendi", is_success=res.is_valid)

        # 4. Kenar çubuğu eleman sayısını senkronize et
        items_count = 0
        if hasattr(self.current_document, "items"):
            items_count = len(self.current_document.items)
        elif hasattr(self.current_document, "signatories"):
            items_count = len([s for s in self.current_document.signatories if s.surname.strip()])
        elif isinstance(self.current_document, list):
            items_count = len(self.current_document)
        self.sidebar.set_item_count(self.active_module.id, items_count)

    def _open_quick_switcher(self):
        from src.ui.quick_switcher import QuickTableSwitcherDialog
        dialog = QuickTableSwitcherDialog(current_module_id=self.active_module.id, parent=self)
        dialog.module_selected.connect(self._switch_to_module)
        dialog.exec()

    def _open_about_dialog(self):
        from src.ui_v2.about_dialog import LinearAboutDialog
        dlg = LinearAboutDialog(self)
        dlg.exec()

    def _open_settings_dialog(self):
        from src.ui_v2.settings_dialog import LinearSettingsDialog
        dlg = LinearSettingsDialog(self)
        dlg.exec()

    def _on_save_preset(self):
        from src.ui_v2.preset_dialog import SavePresetDialog
        dlg = SavePresetDialog(module_id=self.active_module.id, document=self.current_document, parent=self)
        if dlg.exec():
            self.status_bar.set_status("Tablo Şablon Olarak Kaydedildi", is_success=True)

    def _on_load_preset(self):
        from src.ui_v2.preset_dialog import LoadPresetDialog
        dlg = LoadPresetDialog(module_id=self.active_module.id, parent=self)
        if dlg.exec() and dlg.loaded_document is not None:
            self.current_document = dlg.loaded_document
            self.editor_wrapper.show_module(self.active_module.id, self.current_document)
            self._refresh_table_and_cad()
            self.status_bar.set_status("Şablon Başarıyla Tabloya Uygulandı", is_success=True)

    def _toggle_sidebar(self):
        self.sidebar.setHidden(not self.sidebar.isHidden())

    def _toggle_cad_panel(self):
        """CAD önizleme tuvalini gizler veya gösterir (varsayılan: açık)."""
        is_hidden = self.cad_panel.isHidden()
        if is_hidden:
            # Aç (Show CAD)
            self.cad_panel.setHidden(False)
            if hasattr(self, "_saved_splitter_sizes") and self._saved_splitter_sizes and len(self._saved_splitter_sizes) == 2 and self._saved_splitter_sizes[1] > 50:
                self.splitter.setSizes(self._saved_splitter_sizes)
            else:
                self.splitter.setSizes([550, 890])
            self.cad_panel.fit_view()
            self.status_bar.set_status("CAD Ekranı Açıldı", is_success=True)
        else:
            # Kapat (Hide CAD)
            sizes = self.splitter.sizes()
            if sizes and len(sizes) == 2 and sizes[1] > 50:
                self._saved_splitter_sizes = sizes
            self.cad_panel.setHidden(True)
            self.status_bar.set_status("CAD Ekranı Gizlendi (Genişletilmiş Tablo Modu)", is_success=True)

        self.top_bar.set_cad_visible(not self.cad_panel.isHidden())

    def _export_dxf(self):
        if not self.current_table:
            QMessageBox.warning(self, "Hata", "Dışa aktarılacak aktif bir tablo bulunamadı.")
            return

        default_name = (
            f"KM_Coklu_Pafta_{self.layout_config.size.value}.dxf"
            if getattr(self, "_current_multi_sheet_layout", None)
            else self.active_module.default_export_filename(self.current_document)
        )
        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "DXF Olarak Dışa Aktar (Linear Studio)",
            os.path.join(os.getcwd(), default_name),
            "AutoCAD DXF Dosyası (*.dxf)"
        )
        if not out_path:
            return

        try:
            if getattr(self, "_current_multi_sheet_layout", None):
                self.dxf_exporter.export_multi_sheet(
                    multi_sheet_layout=self._current_multi_sheet_layout,
                    output_path=out_path,
                    table_config=self.table_config,
                    layout_config=self.layout_config
                )
            else:
                self.dxf_exporter.export(
                    table=self.current_table,
                    output_path=out_path,
                    table_config=self.table_config,
                    layout_config=self.layout_config
                )
            self.status_bar.set_status(f"DXF Başarıyla Dışa Aktarıldı: {os.path.basename(out_path)}", is_success=True)

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle(i18n.t("export_success_title"))
            msg_box.setText(f"{i18n.t('export_success_msg', path=out_path)}\n\n{i18n.t('open_folder_prompt')}")
            btn_open = msg_box.addButton(i18n.t("btn_open_folder"), QMessageBox.ButtonRole.AcceptRole)
            btn_close = msg_box.addButton(i18n.t("btn_close"), QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(btn_open)
            msg_box.exec()

            if msg_box.clickedButton() == btn_open:
                self._open_file_in_explorer(out_path)
        except Exception as e:
            self.status_bar.set_status(f"DXF Dışa Aktarma Başarısız: {e}", is_success=False)
            QMessageBox.critical(self, "Hata", f"DXF dışa aktarılırken hata oluştu:\n{e}")

    def _toggle_multi_sheet_layout(self):
        """Çoklu pafta ve tekli pafta görünümü arasında geçiş yapar."""
        if getattr(self, "_current_multi_sheet_layout", None) is not None:
            self._show_single_sheet_layout()
        else:
            self._show_multi_sheet_layout()

    def _show_single_sheet_layout(self):
        """Çoklu pafta görünümünden aktif tablonun tekil paftasına geri döner."""
        self._current_multi_sheet_layout = None
        self.cad_panel.set_multi_sheet_mode(False)
        self._do_refresh_table_and_cad()
        self.cad_panel.fit_view()
        self.status_bar.set_status("Tekli Pafta Görünümüne Geri Dönüldü", is_success=True)

    def _show_multi_sheet_layout(self):
        """Tüm proje tablolarını sayfa boyutuna göre otomatik olarak paftalara yerleştirir."""
        from src.models.multi_sheet import MultiSheetLayoutManager
        tables = self._get_all_project_tables()
        if not tables:
            QMessageBox.information(
                self,
                "Bilgi",
                "Çoklu paftaya yerleştirilecek çizim tablosu bulunamadı.\n"
                "(Form 3, Form 9 ve Form 12 bağımsız tam sayfa formlarıdır)."
            )
            return

        tb_doc = self.module_documents.get("title_block", getattr(self.layout_config, "title_block_doc", None))
        ms_layout = MultiSheetLayoutManager.calculate_layout(
            tables=tables,
            layout_config=self.layout_config,
            shared_title_block=tb_doc
        )
        self._current_multi_sheet_layout = ms_layout
        self.cad_panel.canvas.render_multi_sheet(ms_layout, auto_fit=True)
        self.cad_panel.set_multi_sheet_mode(True, sheet_count=ms_layout.total_sheets)
        self.status_bar.set_status(
            f"Otomatik Çoklu Pafta: {ms_layout.total_sheets} Pafta Oluşturuldu (Antet Ortak)",
            is_success=True
        )

    def _get_all_project_tables(self) -> list:
        """Kayıtlı aktif çizim tablosu modüllerinin tablolarını toplar."""
        tables = []
        for mod in TableRegistry.all():
            # Yalnızca aktif tablolar dahil edilir (pasif / iptal edilen tablolar hariç)
            if not getattr(mod, "is_active", True):
                continue
            # Antet (Form 3), Değişiklik İzni (Form 9) ve Başlık Sayfası (Form 12) bağımsız tam sayfa formlarıdır, çizim içerik tablosu değildir
            if mod.id in ("title_block", "antet", "change_permission", "title_sheet"):
                continue
            # Çelik sarfiyat tablosu henüz standart onaylanmadığı için hariç tutulur
            if "raskhod" in mod.id or "steel_consumption" in mod.id or "sarfiyat" in mod.id:
                continue

            doc = self.module_documents.get(mod.id) or mod.create_default_document()
            tbl = mod.build_table(doc)
            if tbl and len(tbl.rows) > 0:
                tables.append(tbl)
        return tables

    def _export_pdf(self):
        """Aktif tabloyu veya çoklu paftayı 1:1 vektörel PDF olarak dışa aktarır (Item 2.3)."""
        default_name = (
            f"KM_Coklu_Pafta_{self.layout_config.size.value}.pdf"
            if getattr(self, "_current_multi_sheet_layout", None)
            else f"{self.active_module.default_export_filename(self.current_document).replace('.dxf', '')}.pdf"
        )
        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "1:1 Vektör PDF Olarak Dışa Aktar",
            os.path.join(os.getcwd(), default_name),
            "Adobe PDF Belgesi (*.pdf)"
        )
        if not out_path:
            return

        try:
            if getattr(self, "_current_multi_sheet_layout", None):
                self.pdf_exporter.export_multi_sheet(
                    multi_sheet_layout=self._current_multi_sheet_layout,
                    output_path=out_path,
                    table_config=self.table_config,
                    layout_config=self.layout_config
                )
            else:
                if not self.current_table:
                    QMessageBox.warning(self, "Hata", "Dışa aktarılacak aktif bir tablo bulunamadı.")
                    return
                self.pdf_exporter.export_sheet(
                    table=self.current_table,
                    output_path=out_path,
                    table_config=self.table_config,
                    layout_config=self.layout_config
                )
            self.status_bar.set_status(f"PDF Başarıyla Dışa Aktarıldı: {os.path.basename(out_path)}", is_success=True)

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("PDF Dışa Aktarma Başarılı")
            msg_box.setText(f"Vektör PDF başarıyla oluşturuldu:\n{out_path}\n\nKlasörü açmak ister misiniz?")
            btn_open = msg_box.addButton(i18n.t("btn_open_folder"), QMessageBox.ButtonRole.AcceptRole)
            btn_close = msg_box.addButton(i18n.t("btn_close"), QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(btn_open)
            msg_box.exec()

            if msg_box.clickedButton() == btn_open:
                self._open_file_in_explorer(out_path)
        except Exception as e:
            self.status_bar.set_status(f"PDF Dışa Aktarma Başarısız: {e}", is_success=False)
            QMessageBox.critical(self, "Hata", f"PDF dışa aktarılırken hata oluştu:\n{e}")

    def _update_window_title(self):
        base = "KM Studio · GOST 21.502 / Linear CAD Dashboard"
        if self.current_project_path:
            name = os.path.basename(self.current_project_path)
            self.setWindowTitle(f"{name} — {base}")
        else:
            self.setWindowTitle(f"İsimsiz Proje — {base}")

    def _new_project(self):
        """Yeni bir boş proje başlatır (Item 4.1)."""
        self.module_documents = {}
        for mod in TableRegistry.all():
            self.module_documents[mod.id] = mod.create_default_document()
        self.module_layout_configs = {}
        self._last_committed_docs = {}
        self.active_module = None
        self.current_document = None
        self.current_project_path = None
        self.undo_manager.clear()
        self._current_multi_sheet_layout = None
        self.cad_panel.set_multi_sheet_mode(False)
        self._update_window_title()

        first_mod = TableRegistry.all()[0]
        self._switch_to_module(first_mod.id)
        self.status_bar.set_status("Yeni Proje Başlatıldı", is_success=True)

    def _open_project(self):
        """Kaydedilmiş bir .kmproj dosyasını açar ve tüm modülleri geri yükler (Item 4.1)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "KM Proje Dosyasını Aç",
            os.getcwd(),
            "KM Studio Projesi (*.kmproj);;Tüm Dosyalar (*.*)"
        )
        if not file_path:
            return

        try:
            proj_data = self.project_manager.load_from_file(file_path)
            self.module_documents = proj_data.get("module_documents", {})
            self.module_layout_configs = proj_data.get("module_layout_configs", {})
            self._last_committed_docs = {}
            self.active_module = None
            self.current_document = None
            self.current_project_path = file_path
            self._current_multi_sheet_layout = None
            self.cad_panel.set_multi_sheet_mode(False)
            self.undo_manager.clear()
            self._update_window_title()

            active_id = proj_data.get("active_module_id", "elements_schedule")
            target_id = active_id if TableRegistry.get(active_id) else TableRegistry.all()[0].id
            self._switch_to_module(target_id)
            self.status_bar.set_status(f"Proje Yüklendi: {os.path.basename(file_path)}", is_success=True)
        except Exception as e:
            self.status_bar.set_status(f"Proje açılamadı: {e}", is_success=False)
            QMessageBox.critical(self, "Hata", f"Proje dosyası yüklenirken hata oluştu:\n{e}")

    def _save_project(self):
        """Aktif projeyi mevcut dosya yoluna kaydeder (Item 4.1)."""
        if not self.current_project_path:
            self._save_project_as()
            return

        try:
            if self.active_module and self.current_document:
                self.module_documents[self.active_module.id] = self.current_document

            tb_doc = self.module_documents.get("title_block", getattr(self.layout_config, "title_block_doc", None))
            self.project_manager.save_to_file(
                filepath=self.current_project_path,
                documents=self.module_documents,
                layout_configs=self.module_layout_configs,
                active_module_id=self.active_module.id if self.active_module else "elements_schedule",
                title_block_doc=tb_doc
            )
            self._update_window_title()
            self.status_bar.set_status(f"Proje Kaydedildi: {os.path.basename(self.current_project_path)}", is_success=True)
        except Exception as e:
            self.status_bar.set_status(f"Proje kaydedilemedi: {e}", is_success=False)
            QMessageBox.critical(self, "Hata", f"Proje kaydedilirken hata oluştu:\n{e}")

    def _save_project_as(self):
        """Projeyi yeni bir dosya yoluna .kmproj olarak kaydeder (Item 4.1)."""
        default_name = "KM_Projesi.kmproj"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "KM Projesini Farklı Kaydet",
            os.path.join(os.getcwd(), default_name),
            "KM Studio Projesi (*.kmproj)"
        )
        if not file_path:
            return

        if not file_path.endswith(".kmproj"):
            file_path += ".kmproj"

        self.current_project_path = file_path
        self._save_project()

    def _open_file_in_explorer(self, file_path: str):
        """Dışa aktarılan dosyanın klasörünü işletim sistemi dosya yöneticisinde seçili olarak açar."""
        norm_path = os.path.normpath(file_path)
        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", f"/select,{norm_path}"])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", norm_path])
            else:
                folder = os.path.dirname(norm_path)
                subprocess.Popen(["xdg-open", folder])
        except Exception as err:
            self.status_bar.set_status(f"Klasör açılamadı: {err}", is_success=False)
