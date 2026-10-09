"""
Kullanıcı Davranış ve Fonksiyonel Doğrulama Testleri (12 Çekirdek Davranış).
Mevcut tablonun davranışsal regresyona uğramadığını garanti eder.
"""
import os
import tempfile
import pytest
from PySide6.QtWidgets import QApplication

from src.config.sheet_config import SheetSize, SheetOrientation, TablePlacement
from src.ui.app import KmMainWindow
from src.ui.i18n import i18n
from src.tables.elements_schedule.model import build_sample_items, ElementsScheduleDocument

@pytest.fixture(scope="session")
def qapp():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_full_application_lifecycle_and_features(qapp):
    # 1. Application starts
    window = KmMainWindow()
    assert window is not None

    # 2. Current table is available
    assert window.active_module.id == "vedomost_elementov"
    assert len(window.current_items) == 7

    # 3. Existing elements can be edited
    editor = window.editor_widget
    editor.table_widget.setCurrentCell(0, 0)
    editor.table_widget.item(0, 0).setText("Б_TEST")
    assert window.current_items[0].mark == "Б_TEST"

    # 4. Add/remove works
    initial_count = editor.table_widget.rowCount()
    editor._add_row()
    assert editor.table_widget.rowCount() == initial_count + 1
    assert len(window.current_items) == initial_count + 1
    editor.table_widget.selectRow(initial_count)
    editor._delete_selected_row()
    assert editor.table_widget.rowCount() == initial_count

    # 5. Reordering works
    first_mark = window.current_items[0].mark
    second_mark = window.current_items[1].mark
    editor.table_widget.selectRow(0)
    editor._move_row(1)
    assert window.current_items[1].mark == first_mark
    assert window.current_items[0].mark == second_mark
    # Geri al
    editor.table_widget.selectRow(1)
    editor._move_row(-1)

    # 6. Example data reset works
    editor._reset_to_samples()
    assert len(window.current_items) == 7

    # 7. Validation works
    val_res = window.active_module.validate(window.current_document)
    assert val_res.is_valid

    # 8. Preview works
    assert window.canvas.scene() is not None
    assert len(window.canvas.scene().items()) > 0
    window.canvas.fit_to_view()

    # 9. Sheet/layout configuration works
    window.layout_panel.cb_size.setCurrentText(SheetSize.A1.value)
    assert window.layout_config.size == SheetSize.A1

    # 10. DXF export works
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        success = window.dxf_exporter.export(
            window.current_table,
            tmp_path,
            layout_config=window.layout_config
        )
        assert success
        assert os.path.exists(tmp_path)
        assert os.path.getsize(tmp_path) > 2000
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 11. Language behavior works
    i18n.set_language("RU")
    assert window.left_tabs.tabText(0) == "Ведомость элементов"
    i18n.set_language("EN")
    assert window.left_tabs.tabText(0) == "Elements (Таблица)"
    i18n.set_language("TR")
    assert window.left_tabs.tabText(0) == "Elemanlar (Таблица)"

    # 12. Keyboard interactions work
    editor.table_widget.setCurrentCell(0, 0)
    cur_text = editor.table_widget.item(0, 0).text()
    editor._insert_char_to_active_cell("Ф")
    assert editor.table_widget.item(0, 0).text() == cur_text + "Ф"
