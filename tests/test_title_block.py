"""
ГОСТ Р 21.101-2020 Form 3 Başlık Bloğu (Title Block) Kapsamlı Test Süiti.
Model, Builder, Validator, Module, Editor ve DXF Dışa Aktarma doğrulamaları.
"""
import os
import sys
import tempfile
import pytest
from PySide6.QtWidgets import QApplication

from src.contracts.table_module import TableModule, ValidationResult
from src.models.registry import TableRegistry
from src.models.table import Table, HAlign, VAlign
from src.config.sheet_config import LayoutConfig, TablePlacement, SheetSize
from src.config.table_config import DEFAULT_TABLE_CONFIG
from src.export.dxf_exporter import DxfExporter
from src.tables.title_block import (
    TitleBlockDocument, SignatoryEntry, RevisionEntry,
    TitleBlockModule, TitleBlockValidator, create_title_block_table,
    TitleBlockConfig, DEFAULT_TITLE_BLOCK_CONFIG
)
from src.tables.title_block.editor import TitleBlockEditorWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


# -----------------------------------------------------------------------------
# 1. MODEL VE SERİLEŞTİRME TESTLERİ
# -----------------------------------------------------------------------------
def test_title_block_model_defaults():
    doc = TitleBlockDocument()
    assert doc.doc_code == "2026-001-КМ"
    assert "Северный" in doc.project_name
    assert "Главный производственный корпус" in doc.building_name
    assert "Схема расположения колонн" in doc.sheet_title
    assert doc.stage == "Р"
    assert doc.sheet_num == "1"
    assert "ПРОЕКТ-СТРОЙ" in doc.company_name
    assert len(doc.signatories) == 6
    assert doc.signatories[0].surname == "Иванов"
    assert doc.signatories[1].surname == "Петров"
    assert doc.signatories[5].surname == "Попов"
    assert len(doc.revisions) == 4


def test_title_block_model_serialization():
    doc = TitleBlockDocument(
        doc_code="TEST-2026-01",
        stage="П",
        sheet_num="12",
        company_name="ÖZEL ÇELİK A.Ş."
    )
    d = doc.to_dict()
    assert d["doc_code"] == "TEST-2026-01"
    assert d["stage"] == "П"

    restored = TitleBlockDocument.from_dict(d)
    assert restored.doc_code == "TEST-2026-01"
    assert restored.stage == "П"
    assert restored.sheet_num == "12"
    assert restored.company_name == "ÖZEL ÇELİK A.Ş."


# -----------------------------------------------------------------------------
# 2. DOĞRULAYICI (VALIDATOR) TESTLERİ
# -----------------------------------------------------------------------------
def test_title_block_validator():
    # Geçerli varsayılan doküman
    doc = TitleBlockDocument()
    res = TitleBlockValidator.validate(doc)
    assert res.is_valid
    assert len(res.messages) == 0

    # Boş kod
    invalid_doc = TitleBlockDocument(doc_code="")
    res = TitleBlockValidator.validate(invalid_doc)
    assert not res.is_valid
    assert any("обозначение" in m for m in res.messages)

    # Boş aşama
    invalid_doc2 = TitleBlockDocument(stage="")
    res = TitleBlockValidator.validate(invalid_doc2)
    assert not res.is_valid
    assert any("стадия" in m for m in res.messages)


# -----------------------------------------------------------------------------
# 3. BUILDER VE CAD GEOMETRİSİ TESTLERİ
# -----------------------------------------------------------------------------
def test_title_block_table_builder():
    doc = TitleBlockDocument()
    table = create_title_block_table(doc)

    assert isinstance(table, Table)
    # Form 3 Boyutları: 185 x 55 mm
    layout = table.compute_layout()
    assert pytest.approx(layout.total_width, 0.001) == 185.0
    assert pytest.approx(layout.total_height, 0.001) == 55.0

    # 10 Sütun, 11 Satır
    assert len(table.columns) == 10
    assert len(table.rows) == 11

    # Doküman Kodu Hücresi (Row 0, Col 6): 115 x 15 mm
    cell_code = table.rows[0].cells[6]
    assert cell_code.text == "2026-001-КМ"
    assert cell_code.rowspan == 3
    assert cell_code.colspan == 4
    rect_code = table.get_cell_cad_rect(0, 6, 0.0, 0.0, layout)
    assert pytest.approx(rect_code.width, 0.001) == 115.0
    assert pytest.approx(rect_code.height, 0.001) == 15.0

    # Proje Adı Hücresi (Row 3, Col 6): 115 x 10 mm
    cell_proj = table.rows[3].cells[6]
    assert "Северный" in cell_proj.text
    assert cell_proj.rowspan == 2
    assert cell_proj.colspan == 4
    rect_proj = table.get_cell_cad_rect(3, 6, 0.0, 0.0, layout)
    assert pytest.approx(rect_proj.width, 0.001) == 115.0
    assert pytest.approx(rect_proj.height, 0.001) == 10.0

    # Yapı Adı Hücresi (Row 5, Col 6): 65 x 15 mm
    cell_bld = table.rows[5].cells[6]
    assert "Главный производственный корпус" in cell_bld.text
    rect_bld = table.get_cell_cad_rect(5, 6, 0.0, 0.0, layout)
    assert pytest.approx(rect_bld.width, 0.001) == 65.0
    assert pytest.approx(rect_bld.height, 0.001) == 15.0

    # Firma Kutusu (Row 8, Col 7): 50 x 15 mm
    cell_comp = table.rows[8].cells[7]
    assert "ПРОЕКТ-СТРОЙ" in cell_comp.text
    rect_comp = table.get_cell_cad_rect(8, 7, 0.0, 0.0, layout)
    assert pytest.approx(rect_comp.width, 0.001) == 50.0
    assert pytest.approx(rect_comp.height, 0.001) == 15.0

    # Mühendis Kadrosu Satır 5..10
    row_sig0 = table.rows[5]
    assert row_sig0.cells[0].text == "Разраб."
    assert row_sig0.cells[3].text == "Иванов"

    row_sig5 = table.rows[10]
    assert row_sig5.cells[0].text == "ГИП"
    assert row_sig5.cells[3].text == "Попов"


# -----------------------------------------------------------------------------
# 4. TABLEMODULE SÖZLEŞME TESTLERİ
# -----------------------------------------------------------------------------
def test_title_block_module_contract(qapp):
    mod = TitleBlockModule()
    assert mod.id == "title_block"
    assert "Основная надпись" in mod.name
    assert mod.is_active

    doc = mod.create_default_document()
    assert isinstance(doc, TitleBlockDocument)

    tbl = mod.build_table(doc)
    assert isinstance(tbl, Table)

    val = mod.validate(doc)
    assert val.is_valid

    fname = mod.default_export_filename(doc)
    assert fname.endswith(".dxf")


def test_title_block_registered():
    mod = TableRegistry.get("title_block")
    assert mod is not None
    assert isinstance(mod, TitleBlockModule)
    assert any(m.id == "title_block" for m in TableRegistry.all())


# -----------------------------------------------------------------------------
# 5. EDITÖR ARAYÜZ TESTLERİ
# -----------------------------------------------------------------------------
def test_title_block_editor_widget(qapp):
    editor = TitleBlockEditorWidget()
    doc = editor.get_document()
    assert doc.doc_code == "2026-001-КМ"

    # Sinyal dinle
    emitted = []
    editor.document_changed.connect(lambda d: emitted.append(d))

    # Alan güncelle
    editor.txt_doc_code.setText("YENI-KOD-001")
    assert len(emitted) > 0
    assert emitted[-1].doc_code == "YENI-KOD-001"

    # Soyadı güncelle
    editor.tbl_signatories.item(0, 1).setText("Demir")
    assert emitted[-1].signatories[0].surname == "Demir"

    # Diğer alanların güncellenmesi
    editor.txt_project_name.setPlainText("Test Proje Adresi")
    assert emitted[-1].project_name == "Test Proje Adresi"

    editor.txt_building_name.setPlainText("Test Bölüm")
    assert emitted[-1].building_name == "Test Bölüm"

    editor.txt_stage.setText("П")
    assert emitted[-1].stage == "П"

    editor.txt_sheet_num.setText("12")
    assert emitted[-1].sheet_num == "12"

    editor.tbl_revisions.item(0, 0).setText("1")
    assert emitted[-1].revisions[0].rev_num == "1"

    # Örnek ve temizleme butonları
    editor.clear_all()
    assert editor.get_document().doc_code == ""
    assert editor.get_document().project_name == ""
    # Sorumlular tablosu: Görevler korunmalı, soyad, imza ve tarih boş olmalıdır
    assert editor.get_document().signatories[0].role == "Разраб."
    assert editor.get_document().signatories[0].surname == ""
    assert editor.get_document().signatories[0].signature == ""
    assert editor.get_document().signatories[0].date == ""
    assert editor.tbl_signatories.item(0, 0).text() == "Разраб."
    assert editor.tbl_signatories.item(0, 1).text() == ""
    assert editor.tbl_signatories.item(0, 2).text() == ""
    assert editor.tbl_signatories.item(0, 3).text() == ""

    editor.load_sample_km()
    assert editor.get_document().doc_code == "2026-001-КМ"
    assert "Северный" in editor.get_document().project_name

    editor.close()


# -----------------------------------------------------------------------------
# 6. DXF DIŞA AKTARMA VE 1:1 ENTEGRASYON TESTLERİ
# -----------------------------------------------------------------------------
def test_title_block_dxf_export():
    import ezdxf

    exporter = DxfExporter()
    mod = TitleBlockModule()
    doc = mod.create_default_document()
    table = mod.build_table(doc)

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tf:
        out_path = tf.name

    try:
        success = exporter.export(
            table=table,
            output_path=out_path,
            table_config=DEFAULT_TABLE_CONFIG,
            layout_config=LayoutConfig(placement=TablePlacement.STANDALONE)
        )
        assert success
        assert os.path.exists(out_path)

        # ezdxf ile içeriği doğrula
        dxf_doc = ezdxf.readfile(out_path)
        msp = dxf_doc.modelspace()

        # Metin varlıklarını topla
        texts = [e.dxf.text for e in msp.query("TEXT")]
        assert any("2026-001-КМ" in t for t in texts)
        assert any("Иванов" in t for t in texts)
        assert any("Попов" in t for t in texts)
        assert any("Разраб." in t for t in texts)
        assert any("Стадия" in t for t in texts)

    finally:
        if os.path.exists(out_path):
            os.remove(out_path)


def test_sheet_layout_title_block_dxf_export():
    """Çizim paftası (ABOVE_TITLEBLOCK) üzerinde Form 3 ana antetin zengin olarak üretildiğini doğrular."""
    import ezdxf
    from src.tables.elements_schedule import ElementsScheduleModule

    exporter = DxfExporter()
    el_mod = ElementsScheduleModule()
    el_doc = el_mod.create_default_document()
    el_table = el_mod.build_table(el_doc)

    tb_doc = TitleBlockDocument(doc_code="ÖZEL-PROJE-07")
    cfg = LayoutConfig(
        placement=TablePlacement.ABOVE_TITLEBLOCK,
        size=SheetSize.A3,
        title_block_doc=tb_doc
    )

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tf:
        out_path = tf.name

    try:
        success = exporter.export(
            table=el_table,
            output_path=out_path,
            table_config=DEFAULT_TABLE_CONFIG,
            layout_config=cfg
        )
        assert success
        dxf_doc = ezdxf.readfile(out_path)
        msp = dxf_doc.modelspace()

        texts = [e.dxf.text for e in msp.query("TEXT")]
        # Hem eleman tablosu hem de antet metinleri paftada mevcut olmalı
        assert any("Ведомость элементов" in t for t in texts)
        assert any("ÖZEL-PROJE-07" in t for t in texts)
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)
