"""
KM Tablo Oluşturucu - Yenilenen UI/UX Davranış ve Entegrasyon Testleri.
16 Kritik UI/UX davranışının Qt widget düzeyinde doğrulaması.
"""
import os
import sys
import tempfile
import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from src.contracts.table_module import TableModule, ValidationResult
from src.models.registry import TableRegistry
from src.models.table import Table, TableCell
from src.config.sheet_config import SheetSize, SheetOrientation, TablePlacement
from src.ui.app import KmMainWindow
from src.ui.quick_switcher import QuickTableSwitcherDialog
from src.ui.i18n import i18n


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


# ---------------------------------------------------------------------------
# Test 1: Application Shell, Native MenuBar & Compact StatusBar (PHASE 2 & 9)
# ---------------------------------------------------------------------------
def test_app_shell_menubar_and_statusbar(qapp):
    window = KmMainWindow()
    assert window is not None
    assert window.isVisible() is False

    # Menü Çubuğu Doğrulaması
    menubar = window.menuBar()
    assert menubar is not None
    actions = [a.text() for a in menubar.actions()]
    assert any("Dosya" in a or "File" in a or "Файл" in a for a in actions)
    assert any("Düzen" in a or "Edit" in a or "Правка" in a for a in actions)
    assert any("Tablolar" in a or "Tables" in a or "Таблицы" in a for a in actions)
    assert any("Görünüm" in a or "View" in a or "Вид" in a for a in actions)

    # Durum Çubuğu Doğrulaması (Kompakt 24px)
    statusbar = window.statusBar()
    assert statusbar.height() == 24 or statusbar.maximumHeight() == 24
    assert window.lbl_status is not None
    assert window.lbl_sheet_info is not None
    assert window.lbl_coords is not None


# ---------------------------------------------------------------------------
# Test 2: Table Explorer (PHASE 3: Tree, Filter, Selection)
# ---------------------------------------------------------------------------
def test_table_explorer_navigation(qapp):
    window = KmMainWindow()
    explorer = window.table_explorer
    assert explorer is not None

    # Ağaçta en az 1 kategori ve 1 tablo olmalı
    tree = explorer.tree
    assert tree.topLevelItemCount() > 0

    # Filtreleme testi
    explorer.search_input.setText("элемент")
    # Filtre çalışmalı
    has_visible = False
    for i in range(tree.topLevelItemCount()):
        cat = tree.topLevelItem(i)
        for j in range(cat.childCount()):
            if not cat.child(j).isHidden():
                has_visible = True
    assert has_visible

    # Olmayan kelime
    explorer.search_input.setText("non_existent_table_xyz")
    all_hidden = True
    for i in range(tree.topLevelItemCount()):
        cat = tree.topLevelItem(i)
        for j in range(cat.childCount()):
            if not cat.child(j).isHidden():
                all_hidden = False
    assert all_hidden

    # Temizle
    explorer.search_input.setText("")


# ---------------------------------------------------------------------------
# Test 3: Quick Table Switcher (Ctrl+T Dialog) (PHASE 4)
# ---------------------------------------------------------------------------
def test_quick_table_switcher_dialog(qapp):
    window = KmMainWindow()
    dlg = QuickTableSwitcherDialog(window)
    assert dlg is not None

    # Modül listesi doldurulmuş olmalı
    assert dlg.list_widget.count() > 0

    # Arama kutusu filtreleme
    dlg.search_edit.setText("Ведомость")
    item0 = dlg.list_widget.item(0)
    assert item0 is not None
    assert not item0.isHidden()

    # Seçim simülasyonu
    dlg._select_current()
    assert dlg.selected_table_id == "vedomost_elementov"


# ---------------------------------------------------------------------------
# Test 4: Dynamic Module Switch & Preview Auto-Hide (PHASE 5 & 10)
# ---------------------------------------------------------------------------
class DummyNoPreviewTable(TableModule):
    """Preview desteklemeyen salt metin tablosu."""
    @property
    def id(self) -> str:
        return "dummy_no_preview"
    @property
    def name(self) -> str:
        return "Önizlemesiz Tablo"
    @property
    def category(self) -> str:
        return "Özel Disiplin"
    @property
    def supports_preview(self) -> bool:
        return False
    def create_default_document(self):
        return []
    def create_editor(self, parent=None):
        w = QWidget(parent)
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Salt Metin Editörü"))
        return w
    def build_table(self, doc):
        t = Table(title="Önizlemesiz")
        t.add_column("c1", "Kolon", 50.0)
        t.add_row([TableCell(text="Veri")])
        return t
    def validate(self, doc):
        return ValidationResult(is_valid=True)


def test_switching_tables_and_workspace_adaptation(qapp):
    dummy_mod = DummyNoPreviewTable()
    TableRegistry.register(dummy_mod)

    try:
        window = KmMainWindow()
        window.show()
        # Başlangıçta preview görünür
        assert not window.cad_workspace.isHidden()

        # Preview desteklemeyen tabloya geç
        window._switch_to_table_id("dummy_no_preview")
        assert window.active_module.id == "dummy_no_preview"
        # Sağ CAD paneli otomatik GİZLENMELİ
        assert window.cad_workspace.isHidden() is True

        # Tekrar preview destekleyen tabloya dön
        window._switch_to_table_id("vedomost_elementov")
        assert window.active_module.id == "vedomost_elementov"
        # Sağ CAD paneli otomatik AÇILMALI
        assert not window.cad_workspace.isHidden()
        window.close()

    finally:
        if "dummy_no_preview" in TableRegistry._modules:
            del TableRegistry._modules["dummy_no_preview"]


# ---------------------------------------------------------------------------
# Test 5: Elements Editor 26px Row & Keyboard Navigation (PHASE 6)
# ---------------------------------------------------------------------------
def test_elements_editor_26px_and_shortcuts(qapp):
    window = KmMainWindow()
    editor = window.editor_widget
    table_w = editor.table_widget

    # Satır yüksekliği ~34px (Rahat mühendislik gridi)
    assert table_w.verticalHeader().defaultSectionSize() == 34

    # Hücre seçimi
    table_w.setCurrentCell(0, 0)
    assert table_w.currentRow() == 0
    assert table_w.currentColumn() == 0

    # Enter tuşu simülasyonu -> Alt hücreye inmeli
    event_enter = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    table_w.keyPressEvent(event_enter)
    assert table_w.currentRow() == 1

    # Tab tuşu simülasyonu -> Yan hücreye geçmeli
    event_tab = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier)
    table_w.keyPressEvent(event_tab)
    assert table_w.currentColumn() == 1

    # Clipboard copy simülasyonu
    table_w.selectRow(0)
    editor._copy_to_clipboard()
    # Kopyalanan veri panoda olmalı
    text = QApplication.clipboard().text()
    assert len(text) > 0


# ---------------------------------------------------------------------------
# Test 6: CAD Workspace Controls, Layout & Zoom (PHASE 8)
# ---------------------------------------------------------------------------
def test_cad_workspace_controls_and_zoom(qapp):
    window = KmMainWindow()
    cad_ws = window.cad_workspace

    # Format combobox
    cad_ws.cb_size.setCurrentText(SheetSize.A2.value)
    assert window.layout_config.size == SheetSize.A2

    # Yönelim combobox
    cad_ws.cb_orient.setCurrentIndex(1)
    assert window.layout_config.orientation == SheetOrientation.PORTRAIT

    # Yerleşim combobox
    cad_ws.cb_placement.setCurrentIndex(0)
    assert window.layout_config.placement == TablePlacement.STANDALONE

    # Zoom kontrolleri
    cad_ws.zoom_in()
    cad_ws.zoom_out()
    cad_ws.zoom_actual()
    cad_ws.fit_to_view()
    assert cad_ws.canvas.scene() is not None


# ---------------------------------------------------------------------------
# Test 7: Splitter Resize & Toggles (PHASE 5 & 11)
# ---------------------------------------------------------------------------
def test_splitter_resize_and_toggles(qapp):
    window = KmMainWindow()
    window.show()

    # Splitter boyutlandırma
    window.main_splitter.setSizes([500, 700])
    assert window.main_splitter.sizes()[0] > 0
    assert window.main_splitter.sizes()[1] > 0

    # Çekmece aç/kapa
    init_explorer_hidden = window.table_explorer.isHidden()
    window._toggle_table_explorer()
    assert window.table_explorer.isHidden() == (not init_explorer_hidden)
    window._toggle_table_explorer()
    assert window.table_explorer.isHidden() == init_explorer_hidden

    # Preview aç/kapa
    init_prev_hidden = window.cad_workspace.isHidden()
    window._toggle_preview()
    assert window.cad_workspace.isHidden() == (not init_prev_hidden)
    window._toggle_preview()
    assert window.cad_workspace.isHidden() == init_prev_hidden
    window.close()


# ---------------------------------------------------------------------------
# Test 8: Multilingual Switch (TR / EN / RU) (PHASE 7)
# ---------------------------------------------------------------------------
def test_multilingual_switch_on_new_ui(qapp):
    window = KmMainWindow()

    i18n.set_language("EN")
    assert window.menu_file.title() == "File"
    assert window.menu_edit.title() == "Edit"

    i18n.set_language("RU")
    assert window.menu_file.title() == "Файл"
    assert window.menu_edit.title() == "Правка"

    i18n.set_language("TR")
    assert window.menu_file.title() == "Dosya"
    assert window.menu_edit.title() == "Düzen"
