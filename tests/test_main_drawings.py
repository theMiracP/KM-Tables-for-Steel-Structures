"""
'Ведомость основных комплектов рабочих чертежей' (ГОСТ Р 21.101 Form 2) Testleri.
"""
import os
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.models.registry import TableRegistry
from src.export.dxf_exporter import DxfExporter
from src.tables.main_drawings.model import (
    DrawingSetItem, MainDrawingsDocument, get_default_sample_items
)
from src.tables.main_drawings.config import (
    MainDrawingsConfig, MainDrawingsColumnWidths, MainDrawingsRowHeights
)
from src.tables.main_drawings.builder import (
    create_main_drawings_table, calculate_item_row_height
)
from src.tables.main_drawings.validator import MainDrawingsValidator
from src.tables.main_drawings.module import MainDrawingsModule
from src.tables.main_drawings.editor import MainDrawingsEditorWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_drawings_model_default_items():
    doc = MainDrawingsDocument()
    assert len(doc.items) == 12
    assert doc.title == "Ведомость основных комплектов рабочих чертежей"
    assert doc.items[0].designation == "2026-001-ПЗ"
    assert "Пояснительная записка" in doc.items[0].name
    assert doc.items[11].designation == "2026-001-АК"


def test_main_drawings_model_serialization():
    doc = MainDrawingsDocument()
    data = doc.to_dict()
    assert "title" in data
    assert len(data["items"]) == 12

    restored = MainDrawingsDocument.from_dict(data)
    assert restored.title == doc.title
    assert len(restored.items) == 12
    assert restored.items[0].designation == doc.items[0].designation
    assert restored.items[0].name == doc.items[0].name


def test_main_drawings_config_dimensions():
    cfg = MainDrawingsConfig()
    assert cfg.columns.col_designation == 60.0
    assert cfg.columns.col_name == 95.0
    assert cfg.columns.col_note == 30.0
    assert cfg.columns.total_width == 185.0
    assert cfg.rows.header_height == 15.0
    assert cfg.rows.min_item_height == 8.0


def test_main_drawings_builder_table_structure():
    doc = MainDrawingsDocument()
    table = create_main_drawings_table(doc)

    assert table.title == "Ведомость основных комплектов рабочих чертежей"
    assert len(table.columns) == 3
    assert abs(table.total_width - 185.0) < 0.001

    # İlk satır başlık satırıdır
    header_row = table.rows[0]
    assert header_row.is_header is True
    assert header_row.height == 15.0
    assert [c.text for c in header_row.cells] == ["Обозначение", "Наименование", "Примечание"]

    # 12 veri satırı
    assert len(table.rows) == 13
    first_data_row = table.rows[1]
    assert first_data_row.is_header is False
    assert first_data_row.cells[0].text == "2026-001-ПЗ"
    assert first_data_row.height >= 8.0


def test_main_drawings_dynamic_row_height():
    cfg = MainDrawingsConfig()
    short_item = DrawingSetItem(designation="К1", name="Kısa isim", note="")
    h_short = calculate_item_row_height(short_item, cfg)
    assert h_short == 8.0

    long_item = DrawingSetItem(
        designation="К2",
        name="Металлические конструкции секции П. Стальные базы СТЖБ колонн. Стальные сердечники колонн -3-го этажа",
        note=""
    )
    h_long = calculate_item_row_height(long_item, cfg)
    assert h_long > 12.0


def test_main_drawings_validator():
    doc = MainDrawingsDocument()
    res = MainDrawingsValidator.validate(doc)
    assert res.is_valid is True

    empty_doc = MainDrawingsDocument(items=[])
    res_empty = MainDrawingsValidator.validate(empty_doc)
    assert res_empty.is_valid is False
    assert "tanımlanmamış" in res_empty.summary_message


def test_main_drawings_registry():
    mod = TableRegistry.get("main_drawings")
    assert mod is not None
    assert isinstance(mod, MainDrawingsModule)
    assert mod.id == "main_drawings"
    assert mod.name == "Ведомость основных комплектов рабочих чертежей"
    assert mod.default_export_filename(None).endswith(".dxf")


def test_main_drawings_dxf_export(tmp_path):
    doc = MainDrawingsDocument()
    table = create_main_drawings_table(doc)
    exporter = DxfExporter()
    out_file = str(tmp_path / "test_main_drawings.dxf")

    success = exporter.export(table, out_file)
    assert success is True
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000


def test_main_drawings_editor_widget(qapp):
    editor = MainDrawingsEditorWidget()
    assert editor.table.rowCount() == 12

    # Satır ekleme testi
    editor._add_row()
    assert editor.table.rowCount() == 13

    # Satır silme testi
    editor.table.selectRow(12)
    editor._delete_selected_row()
    assert editor.table.rowCount() == 12

    # Veri alma / verme testi
    doc = editor.get_document()
    assert len(doc.items) == 12

    # Yukarı taşıma testi
    editor.table.selectRow(1)
    editor._move_row(-1)
    new_doc = editor.get_document()
    assert new_doc.items[0].designation == "2026-001-АР"

    editor.close()
