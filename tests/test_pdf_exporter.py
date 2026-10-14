"""
PdfExporter birim testleri (Item 2.3).
Tekil ve çoklu pafta vektör PDF çıktısının doğrulanması.
"""
import os
import pytest
from PySide6.QtWidgets import QApplication

from src.export.pdf_exporter import PdfExporter
from src.models.registry import TableRegistry
from src.models.multi_sheet import MultiSheetLayoutManager
from src.config.sheet_config import DEFAULT_LAYOUT_CONFIG
from src.config.table_config import DEFAULT_TABLE_CONFIG
import src.tables


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_pdf_exporter_single_sheet(qapp, tmp_path):
    mod = TableRegistry.get("vedomost_elementov")
    assert mod is not None
    doc = mod.create_default_document()
    table = mod.build_table(doc)

    exporter = PdfExporter(resolution_dpi=150)
    pdf_path = str(tmp_path / "single_sheet.pdf")

    success = exporter.export_sheet(table, pdf_path, DEFAULT_TABLE_CONFIG, DEFAULT_LAYOUT_CONFIG)
    assert success is True
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # Vektör PDF içeriği mevcut


def test_pdf_exporter_multi_sheet(qapp, tmp_path):
    mod = TableRegistry.get("vedomost_elementov")
    doc = mod.create_default_document()
    table = mod.build_table(doc)

    # 2 paftaya sığacak şekilde çoklu pafta üret
    layout = MultiSheetLayoutManager.calculate_layout(
        tables=[table, table],
        layout_config=DEFAULT_LAYOUT_CONFIG
    )
    assert layout.total_sheets >= 1

    exporter = PdfExporter(resolution_dpi=150)
    pdf_path = str(tmp_path / "multi_sheet.pdf")

    success = exporter.export_multi_sheet(layout, pdf_path, DEFAULT_TABLE_CONFIG, DEFAULT_LAYOUT_CONFIG)
    assert success is True
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 2000
