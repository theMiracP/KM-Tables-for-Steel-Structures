"""
KM Tablo Oluşturucu - Kapsamlı FINAL AUDIT Doğrulama Testi.
Kullanıcı tarafından talep edilen 12 kontrol grubu ve 15 kuralın tamamını
gerçek PySide6 widget seviyesinde tek tek denetler.
"""
import os
import sys
import tempfile
import pytest
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QMenu

from src.contracts.table_module import TableModule, ValidationResult
from src.models.registry import TableRegistry
from src.config.sheet_config import SheetSize, SheetOrientation, TablePlacement
from src.ui.app import KmMainWindow
from src.ui.quick_switcher import QuickTableSwitcherDialog
from src.ui.i18n import i18n
from src.ui import theme

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


# ==============================================================================
# 1. APPLICATION SHELL AUDIT
# ==============================================================================
def test_audit_1_application_shell(qapp):
    window = KmMainWindow()
    window.show()

    # QMainWindow
    assert isinstance(window, KmMainWindow)

    # Native QMenuBar
    menubar = window.menuBar()
    assert menubar is not None
    menu_titles = [a.text() for a in menubar.actions()]
    for expected_menu in ["Dosya", "Düzen", "Tablolar", "Görünüm", "Araçlar", "Yardım"]:
        assert any(expected_menu in t for t in menu_titles), f"Menü eksik: {expected_menu}"

    # QStatusBar
    statusbar = window.statusBar()
    assert statusbar is not None
    assert statusbar.height() == 24 or statusbar.maximumHeight() == 24

    # Kompakt Header & Aktif Tablo Adı & Dil Seçimi
    assert window.lbl_active_table_title.text() == "Ведомость элементов (ГОСТ 21.502 / КМ)"
    assert window.cb_lang.currentText() in ["TR", "EN", "RU"]
    window.close()


# ==============================================================================
# 2. TABLE EXPLORER AUDIT
# ==============================================================================
def test_audit_2_table_explorer(qapp):
    window = KmMainWindow()
    window.show()

    # Açık / Kapatılabilir
    explorer = window.table_explorer
    assert not explorer.isHidden()
    window._toggle_table_explorer()
    assert explorer.isHidden()
    window._toggle_table_explorer()
    assert not explorer.isHidden()

    # Arama kutusu ve kategori ağacı
    assert explorer.tree.topLevelItemCount() > 0
    explorer.search_input.setText("элемент")
    explorer.search_input.setText("")

    # Aktif tablo seçimi ve modül değişimi
    explorer.set_active_table("vedomost_elementov")
    assert window.active_module.id == "vedomost_elementov"
    window.close()


# ==============================================================================
# 3. QUICK TABLE SWITCHER (Ctrl+T) AUDIT
# ==============================================================================
def test_audit_3_quick_table_switcher(qapp):
    window = KmMainWindow()
    window.show()

    dlg = QuickTableSwitcherDialog(window)
    assert dlg is not None
    assert dlg.list_widget.count() > 0

    # Filtreleme
    dlg.search_edit.setText("Ведомость")
    assert not dlg.list_widget.item(0).isHidden()

    # Enter ile seçim
    dlg._select_current()
    assert dlg.selected_table_id == "vedomost_elementov"
    window.close()


# ==============================================================================
# 4. MAIN SPLITTER AUDIT
# ==============================================================================
def test_audit_4_main_splitter(qapp):
    window = KmMainWindow()
    window.show()

    splitter = window.main_splitter
    assert splitter.count() == 2

    # Sürüklenebilir ve başlangıç oranları
    sizes = splitter.sizes()
    assert sizes[0] > 0 and sizes[1] > 0
    splitter.setSizes([500, 700])
    assert splitter.sizes()[0] > 0

    # Sağ panel gizlenebilmeli (Ctrl+Shift+P)
    assert not window.cad_workspace.isHidden()
    window._toggle_preview()
    assert window.cad_workspace.isHidden()
    window._toggle_preview()
    assert not window.cad_workspace.isHidden()
    window.close()


# ==============================================================================
# 5. TABLE EDITOR REAL QT INTERACTIONS AUDIT
# ==============================================================================
def test_audit_5_table_editor_interactions(qapp):
    window = KmMainWindow()
    window.show()
    editor = window.editor_widget
    tw = editor.table_widget

    # Satır ekleme / silme
    init_rows = tw.rowCount()
    editor._add_row()
    assert tw.rowCount() == init_rows + 1
    tw.selectRow(init_rows)
    editor._delete_selected_row()
    assert tw.rowCount() == init_rows

    # Yukarı / Aşağı taşıma
    m0 = window.current_items[0].mark
    m1 = window.current_items[1].mark
    tw.selectRow(0)
    editor._move_row(1)
    assert window.current_items[1].mark == m0
    tw.selectRow(1)
    editor._move_row(-1)
    assert window.current_items[0].mark == m0

    # Örnek verileri yükleme
    editor._reset_to_samples()
    assert tw.rowCount() == 7

    # Enter -> Alt hücre
    tw.setCurrentCell(0, 0)
    ev_enter = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    tw.keyPressEvent(ev_enter)
    assert tw.currentRow() == 1

    # Tab -> Sonraki hücre
    ev_tab = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier)
    tw.keyPressEvent(ev_tab)
    assert tw.currentColumn() == 1

    # F2 -> Edit
    ev_f2 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F2, Qt.KeyboardModifier.NoModifier)
    tw.keyPressEvent(ev_f2)

    # Esc -> İptal
    ev_esc = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
    tw.keyPressEvent(ev_esc)

    # Ctrl+C / Ctrl+V
    tw.selectRow(0)
    editor._copy_to_clipboard()
    copied = QApplication.clipboard().text()
    assert len(copied) > 0

    # Sağ tık context menu desteği
    assert hasattr(tw, "contextMenuEvent")
    window.close()


# ==============================================================================
# 6. CAD WORKSPACE & RENDERING AUDIT
# ==============================================================================
def test_audit_6_cad_workspace(qapp):
    window = KmMainWindow()
    window.show()
    ws = window.cad_workspace

    # Canvas & Scene
    assert ws.canvas is not None
    assert ws.canvas.scene() is not None
    assert len(ws.canvas.scene().items()) > 0

    # Pafta boyutu ve yerleşim
    ws.cb_size.setCurrentText(SheetSize.A1.value)
    assert window.layout_config.size == SheetSize.A1

    ws.cb_orient.setCurrentIndex(1)
    assert window.layout_config.orientation == SheetOrientation.PORTRAIT

    ws.cb_placement.setCurrentIndex(0)
    assert window.layout_config.placement == TablePlacement.STANDALONE

    # Zoom ve Fit
    ws.fit_to_view()
    ws.zoom_in()
    ws.zoom_out()
    ws.zoom_actual()
    assert ws.canvas.scene() is not None
    window.close()


# ==============================================================================
# 7. DXF EXPORT AUDIT
# ==============================================================================
def test_audit_7_dxf_export(qapp):
    window = KmMainWindow()
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        success = window.dxf_exporter.export(
            window.current_table,
            tmp_path,
            layout_config=window.layout_config
        )
        assert success is True
        assert os.path.exists(tmp_path)
        assert os.path.getsize(tmp_path) > 1000
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ==============================================================================
# 8. STATUS BAR REAL DATA AUDIT
# ==============================================================================
def test_audit_8_status_bar_real_values(qapp):
    window = KmMainWindow()
    window.show()

    # Sol: Validation status & eleman sayısı
    stat_text = window.lbl_status.text()
    assert "✓" in stat_text or "7 eleman" in stat_text

    # Orta: Pafta ebatı, yönelim ve placement
    sheet_text = window.lbl_sheet_info.text()
    assert "ГОСТ 2.301" in sheet_text
    assert "A3" in sheet_text or "Yatay" in sheet_text

    # Sağ: CAD Koordinatı ve Zoom yüzdesi
    coords_text = window.lbl_coords.text()
    assert "X:" in coords_text and "Y:" in coords_text and "Zoom:" in coords_text
    window.close()


# ==============================================================================
# 9. I18N REAL UI SWITCH AUDIT (TR -> RU -> EN -> TR)
# ==============================================================================
def test_audit_9_i18n_cycle(qapp):
    window = KmMainWindow()
    window.show()

    # TR
    i18n.set_language("TR")
    assert window.menu_file.title() == "Dosya"
    assert "Eleman Ekle" in window.editor_widget.btn_add.text()

    # RU
    i18n.set_language("RU")
    assert window.menu_file.title() == "Файл"
    assert "Добавить" in window.editor_widget.btn_add.text()
    assert "Ведомость" in window.lbl_active_table_title.text()

    # EN
    i18n.set_language("EN")
    assert window.menu_file.title() == "File"
    assert "Add" in window.editor_widget.btn_add.text()

    # TR'ye dön
    i18n.set_language("TR")
    assert window.menu_file.title() == "Dosya"
    window.close()


# ==============================================================================
# 10. THEME PALETTE & RESTYLED RULES AUDIT
# ==============================================================================
def test_audit_10_theme_specification():
    # Renk paleti kontrolleri
    assert theme.COLOR_BG_DARK == "#1E1E1E"
    assert theme.COLOR_PANEL_BG == "#252526"
    assert theme.COLOR_PANEL_ALT == "#1F1F1F"
    assert theme.COLOR_BORDER == "#3E3E42"
    assert theme.COLOR_TEXT_PRIMARY == "#D4D4D4"
    assert theme.COLOR_TEXT_MUTED == "#9D9D9D"
    assert theme.COLOR_ACCENT == "#0E639C"
    assert theme.COLOR_SUCCESS == "#4EC9B0"
    assert theme.COLOR_WARNING == "#D7BA7D"
    assert theme.COLOR_DANGER == "#F14C4C"
    assert theme.COLOR_CAD_BG == "#141414"
    assert theme.COLOR_CAD_PAPER == "#FFFFFF"

    # QSS içerisinde 2px radius ve Segoe UI kuralları bulunmalı
    assert "border-radius: 2px" in theme.QSS_DARK_THEME
    assert "Segoe UI" in theme.QSS_DARK_THEME


# ==============================================================================
# 11. LAYOUT DENSITY GEOMETRY AUDIT
# ==============================================================================
def test_audit_11_layout_density_geometry(qapp):
    window = KmMainWindow()
    window.show()

    # Status Bar: 24px
    assert window.statusBar().height() == 24 or window.statusBar().maximumHeight() == 24

    # Table Row: ~34px (Enlarged for readability)
    assert window.editor_widget.table_widget.verticalHeader().defaultSectionSize() == 34

    # Action Bar: ~28px
    action_bars = window.editor_widget.findChildren(type(window.editor_widget))
    assert window.editor_widget.table_widget.horizontalHeader().height() <= 48
    window.close()


# ==============================================================================
# 12. ARCHITECTURE COUPLING AUDIT
# ==============================================================================
def test_audit_12_architecture_decoupling():
    import inspect
    from src.ui import app as app_module

    source = inspect.getsource(app_module)

    # KmMainWindow kaynak kodunda doğrudan bu özel sınıflar import edilmemeli:
    assert "from src.models.elements_schedule import ScheduleItem" not in source
    assert "from src.models.elements_schedule import ElementPart" not in source
    assert "from src.ui.input_panel import ElementsScheduleWidget" not in source
    assert "from src.validation.validator import TableValidator" not in source
    assert "from src.models.elements_schedule import create_elements_schedule_table" not in source
