"""
'Ведомость рабочих чертежей основного комплекта' (ГОСТ Р 21.101 Form 1) Testleri.
"""
import os
import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from src.models.registry import TableRegistry
from src.export.dxf_exporter import DxfExporter
from src.tables.working_drawings.model import (
    WorkingDrawingItem, WorkingDrawingsDocument, get_default_sample_items
)
from src.tables.working_drawings.config import (
    WorkingDrawingsConfig, WorkingDrawingsColumnWidths, WorkingDrawingsRowHeights
)
from src.tables.working_drawings.builder import (
    create_working_drawings_table, calculate_item_row_height
)
from src.tables.working_drawings.validator import WorkingDrawingsValidator
from src.tables.working_drawings.module import WorkingDrawingsModule
from src.tables.working_drawings.editor import WorkingDrawingsEditorWidget
from src.ui_v2.sidebar import LinearSidebar
from src.ui_v2.editor_wrapper import TableEditorWrapper
from src.ui.i18n import i18n


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_working_drawings_model_default_items():
    doc = WorkingDrawingsDocument()
    assert len(doc.items) == 10
    assert doc.title == "Ведомость рабочих чертежей основного комплекта"
    assert doc.items[0].sheet_number == "1"
    assert doc.items[0].name == "Общие данные"
    assert doc.items[1].sheet_number == "2"
    assert "Схема расположения колонн" in doc.items[1].name
    assert doc.items[2].sheet_number == "3"
    assert "Схема расположения балок" in doc.items[2].name
    assert doc.items[3].sheet_number == "4"
    assert "ферм и прогонов" in doc.items[3].name
    # 8, 9 ve 10. satırların kontrolü
    assert doc.items[7].sheet_number == "8"
    assert "Узлы сопряжения ферм" in doc.items[7].name
    assert doc.items[8].sheet_number == "9"
    assert "Узлы вертикальных и горизонтальных связей" in doc.items[8].name
    assert doc.items[9].sheet_number == "10"
    assert "Спецификация металлопроката" in doc.items[9].name


def test_working_drawings_model_serialization_and_pdf_interface():
    doc = WorkingDrawingsDocument()
    data = doc.to_dict()
    assert "title" in data
    assert len(data["items"]) == 10

    restored = WorkingDrawingsDocument.from_dict(data)
    assert restored.title == doc.title
    assert len(restored.items) == 10
    assert restored.items[0].sheet_number == doc.items[0].sheet_number
    assert restored.items[0].name == doc.items[0].name

    # Gelecekte PDF'ten aktarım için hazırlanan arayüz fonksiyonlarının testi
    doc.clear_items()
    assert len(doc.items) == 0

    new_from_pdf = [
        WorkingDrawingItem(sheet_number="1", name="Общие данные (PDF)"),
        WorkingDrawingItem(sheet_number="2", name="Схема балок (PDF)"),
    ]
    doc.populate_from_items(new_from_pdf)
    assert len(doc.items) == 2
    assert doc.items[1].name == "Схема балок (PDF)"

    doc.append_item(WorkingDrawingItem(sheet_number="3", name="Узлы (PDF)"))
    assert len(doc.items) == 3


def test_working_drawings_config_dimensions():
    cfg = WorkingDrawingsConfig()
    assert cfg.columns.col_sheet == 15.0
    assert cfg.columns.col_name == 140.0
    assert cfg.columns.col_note == 30.0
    assert cfg.columns.total_width == 185.0
    assert cfg.rows.header_height == 15.0
    assert cfg.rows.min_item_height == 8.0


def test_working_drawings_builder_table_structure():
    doc = WorkingDrawingsDocument()
    table = create_working_drawings_table(doc)

    assert table.title == "Ведомость рабочих чертежей основного комплекта"
    assert len(table.columns) == 3
    assert abs(table.total_width - 185.0) < 0.001

    # İlk satır başlık satırıdır
    header_row = table.rows[0]
    assert header_row.is_header is True
    assert header_row.height == 15.0
    assert [c.text for c in header_row.cells] == ["Лист", "Наименование", "Примечание"]

    # 10 veri satırı (toplam 11 satır)
    assert len(table.rows) == 11
    first_data_row = table.rows[1]
    assert first_data_row.is_header is False
    assert first_data_row.cells[0].text == "1"
    assert first_data_row.cells[1].text == "Общие данные"

    # Hücre hizalamaları: Лист ortalı, Наименование sola dayalı, Примечание ortalı
    assert first_data_row.cells[0].halign.name == "CENTER"
    assert first_data_row.cells[1].halign.name == "LEFT"
    assert first_data_row.cells[2].halign.name == "CENTER"

    # 8. pafta başlığı için satır yüksekliği kontrolü
    row_8 = table.rows[8]  # 0: header, 1: sheet 1, ..., 8: sheet 8
    assert row_8.cells[0].text == "8"
    assert row_8.height >= 8.0


def test_working_drawings_dynamic_row_height():
    cfg = WorkingDrawingsConfig()
    short_item = WorkingDrawingItem(sheet_number="1", name="Kısa isim", note="")
    h_short = calculate_item_row_height(short_item, cfg)
    assert h_short == 8.0

    long_item = WorkingDrawingItem(
        sheet_number="8",
        name="Узлы изменения сечения колонн типов 4, 5 в тип 3 и типа 3 в типы 7, 10 (2АК), изменения наклона колонн типов 4, 3 (2АК)",
        note=""
    )
    h_long = calculate_item_row_height(long_item, cfg)
    assert h_long > 8.0


def test_working_drawings_validator():
    doc = WorkingDrawingsDocument()
    res = WorkingDrawingsValidator.validate(doc)
    assert res.is_valid is True

    # Tamamen boş doküman
    empty_doc = WorkingDrawingsDocument(items=[])
    res_empty_doc = WorkingDrawingsValidator.validate(empty_doc)
    assert res_empty_doc.is_valid is False
    assert "tanımlanmamış" in res_empty_doc.summary_message

    # Tamamen boş satırlardan oluşan doküman
    empty_items_doc = WorkingDrawingsDocument(items=[WorkingDrawingItem(), WorkingDrawingItem()])
    res_empty = WorkingDrawingsValidator.validate(empty_items_doc)
    assert res_empty.is_valid is False
    assert any("boş olamaz" in msg for msg in res_empty.messages)

    # Yinelenen pafta numarası uyarısı
    dup_doc = WorkingDrawingsDocument(items=[
        WorkingDrawingItem(sheet_number="1", name="Sayfa 1"),
        WorkingDrawingItem(sheet_number="1", name="Mükerrer Sayfa 1"),
    ])
    res_dup = WorkingDrawingsValidator.validate(dup_doc)
    assert res_dup.is_valid is False
    assert any("Yinelenen pafta" in msg for msg in res_dup.messages)


def test_working_drawings_registry():
    mod = TableRegistry.get("working_drawings")
    assert mod is not None
    assert isinstance(mod, WorkingDrawingsModule)
    assert mod.id == "working_drawings"
    assert mod.name == "Ведомость рабочих чертежей основного комплекта"
    assert mod.default_export_filename(None).endswith(".dxf")


def test_working_drawings_dxf_export(tmp_path):
    doc = WorkingDrawingsDocument()
    table = create_working_drawings_table(doc)
    exporter = DxfExporter()
    out_file = str(tmp_path / "test_working_drawings.dxf")

    success = exporter.export(table, out_file)
    assert success is True
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000


def test_working_drawings_editor_widget(qapp):
    editor = WorkingDrawingsEditorWidget()
    assert editor.table.rowCount() == 10

    # Satır ekleme testi
    editor._add_row()
    assert editor.table.rowCount() == 11
    # Eklenen satırın otomatik tahmini: önceki '10' olduğu için '11' olmalı
    assert editor.table.item(10, 0).text() == "11"

    # Satır silme testi
    editor.table.selectRow(10)
    editor._delete_selected_row()
    assert editor.table.rowCount() == 10

    # Yukarı taşıma testi
    editor.table.selectRow(1)
    editor._move_row(-1)
    new_doc = editor.get_document()
    assert new_doc.items[0].sheet_number == "2"

    # Temizle ve örnek yükle testi (1 adet boş satır bırakmalıdır)
    editor._clear_table(prompt=False)
    assert editor.table.rowCount() == 1
    assert len(editor.get_document().items) == 1
    assert editor.table.item(0, 0).text() == ""
    assert editor.table.item(0, 1).text() == ""
    assert editor.table.item(0, 2).text() == ""

    editor._load_sample_template()
    assert editor.table.rowCount() == 10
    assert editor.table.item(0, 0).text() == "1"

    # Excel Panodan yapıştırma simülasyonu
    QGuiApplication.clipboard().setText("15\tÇatı Planı\tİmalat\n16\tAşık Detayları\t")
    editor.table.setCurrentCell(9, 0)
    editor._paste_from_clipboard()
    assert editor.table.rowCount() >= 11
    assert editor.table.item(9, 0).text() == "15"
    assert editor.table.item(9, 1).text() == "Çatı Planı"
    assert editor.table.item(10, 0).text() == "16"

    editor.close()


def test_working_drawings_ui_integration(qapp):
    sidebar = LinearSidebar()
    nav_item = sidebar._nav_items.get("working_drawings")
    assert nav_item is not None
    assert nav_item.lbl_icon.text() == "📋" or (nav_item.lbl_icon.pixmap() and not nav_item.lbl_icon.pixmap().isNull())
    assert "Çalışma Çizimleri" in nav_item.lbl_name.text() or "Ведомость рабочих" in nav_item.lbl_name.text()

    wrapper = TableEditorWrapper()
    mod = TableRegistry.get("working_drawings")
    assert mod is not None
    wrapper.register_module(mod)
    wrapper.show_module("working_drawings")
    assert wrapper.lbl_icon.text() == "📋"
    assert "Form 1" in wrapper.lbl_subtitle.text()

    sidebar.close()
    wrapper.close()
