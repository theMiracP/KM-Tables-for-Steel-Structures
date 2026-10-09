"""
PySide6 Arayüz Birim ve Entegrasyon Testleri.
"""
import os
import sys
import pytest
from PySide6.QtWidgets import QApplication

# Test ortamında tek bir QApplication örneği
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_pyside_main_window_init(qapp):
    from src.ui.app import KmMainWindow
    window = KmMainWindow()
    assert window is not None
    assert window.editor_widget.table_widget.rowCount() > 0

def test_pyside_cyrillic_insert(qapp):
    from src.ui.app import KmMainWindow
    window = KmMainWindow()
    window.editor_widget.table_widget.setCurrentCell(0, 0)
    init_val = window.editor_widget.table_widget.item(0, 0).text()
    window.editor_widget._insert_char_to_active_cell("К")
    assert window.editor_widget.table_widget.item(0, 0).text() == init_val + "К"

def test_pyside_add_delete_row(qapp):
    from src.ui.app import KmMainWindow
    window = KmMainWindow()
    cnt = window.editor_widget.table_widget.rowCount()
    window.editor_widget._add_row()
    assert window.editor_widget.table_widget.rowCount() == cnt + 1
    window.editor_widget.table_widget.selectRow(cnt)
    window.editor_widget._delete_selected_row()
    assert window.editor_widget.table_widget.rowCount() == cnt

def test_pyside_canvas_operations(qapp):
    from src.ui.app import KmMainWindow
    window = KmMainWindow()
    window.canvas.zoom_in()
    window.canvas.zoom_out()
    window.canvas.zoom_actual()
    window.canvas.fit_to_view()
    assert window.canvas.scene() is not None

def test_pyside_i18n(qapp):
    from src.ui.app import KmMainWindow
    from src.ui.i18n import i18n
    window = KmMainWindow()
    i18n.set_language("EN")
    assert window.left_tabs.tabText(0) == "Elements (Таблица)"
    i18n.set_language("TR")
    assert window.left_tabs.tabText(0) == "Elemanlar (Таблица)"

def test_pyside_smart_auto_formatting(qapp):
    from src.ui.app import KmMainWindow
    from src.models.sketch import SketchType
    window = KmMainWindow()
    editor = window.editor_widget

    assert editor._auto_format_composition("120x8", SketchType.RECT_TUBE) == "Гн. □ 120x8"
    assert editor._auto_format_composition("50x4.0", SketchType.ANGLE) == "L 50x4.0"
    assert editor._auto_format_composition("12П", SketchType.CHANNEL) == "[ 12П"
    assert editor._auto_format_composition("4", SketchType.CHECKERED_PLATE) == "Рифл. -4"

