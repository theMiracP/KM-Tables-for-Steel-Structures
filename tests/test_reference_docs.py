"""
'Ведомость ссылочных и прилагаемых документов' Modülü ve Standartlar Kütüphanesi Testleri.
ГОСТ Р 21.101 Form 2, Kütüphane CRUD, Model, Builder, DXF ve Editör Doğrulaması.
"""
import os
import sys
import tempfile
import pytest
from PySide6.QtWidgets import QApplication

from src.models.registry import TableRegistry
from src.models.table import Table, HAlign
from src.contracts.table_module import ValidationResult
from src.export.dxf_exporter import DxfExporter
from src.config.sheet_config import DEFAULT_LAYOUT_CONFIG
from src.tables.reference_documents.model import (
    ReferenceDocItem, ReferenceDocsDocument, StandardLibraryItem
)
from src.tables.reference_documents.config import (
    ReferenceDocsConfig, DEFAULT_REFERENCE_DOCS_CONFIG
)
from src.tables.reference_documents.library import (
    StandardsLibraryManager, standards_library, DEFAULT_STANDARDS_DATA
)
from src.tables.reference_documents.builder import create_reference_docs_table
from src.tables.reference_documents.validator import ReferenceDocsValidator
from src.tables.reference_documents.module import ReferenceDocsModule
from src.tables.reference_documents.editor import ReferenceDocsEditorWidget
from src.tables.reference_documents.dialogs import StandardsLibraryDialog, StandardEditDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_reference_docs_model_serialization():
    """Model serileştirme ve deserileştirme testleri."""
    item = ReferenceDocItem(
        designation="СП 16.13330.2017",
        title="Стальные конструкции",
        title_tr="Çelik Yapılar",
        title_en="Steel Structures",
        section="Ссылочные документы",
        note="Güncel revizyon",
    )
    d = item.to_dict()
    assert d["designation"] == "СП 16.13330.2017"
    assert d["title_tr"] == "Çelik Yapılar"
    assert d["title_en"] == "Steel Structures"

    reconstructed = ReferenceDocItem.from_dict(d)
    assert reconstructed.designation == item.designation
    assert reconstructed.title == item.title
    assert reconstructed.title_tr == item.title_tr
    assert reconstructed.title_en == item.title_en

    doc = ReferenceDocsDocument(items=[item])
    doc_d = doc.to_dict()
    assert len(doc_d["items"]) == 1
    doc_reconstructed = ReferenceDocsDocument.from_dict(doc_d)
    assert len(doc_reconstructed.items) == 1
    assert doc_reconstructed.items[0].designation == "СП 16.13330.2017"


def test_standards_library_default_items_and_image_match():
    """Referans görseldeki 14 standardın kütüphanede eksiksiz var olduğunu doğrula."""
    all_standards = standards_library.get_all()
    assert len(all_standards) >= 14

    expected_codes = [
        "ГОСТ 27751-2014",
        "СП 16.13330.2017",
        "СП 20.13330.2016",
        "СП 28.13330.2017",
        "СП 48.13330.2019",
        "СП 70.13330.2012",
        "СП 72.13330.2016",
        "СТО АРСС 11251254.001-018-5",
        "СП 470.1325800.2019",
        "ГОСТ 23118-2019",
        "СНиП 12-03-2001",
        "СНиП 12-04-2002",
        "СП 112.13330.2011",
        "ФЗ №123-ФЗ",
    ]

    for code in expected_codes:
        match = standards_library.get_by_designation(code)
        assert match is not None, f"Standart {code} kütüphanede bulunamadı!"
        assert bool(match.title_ru.strip()), f"{code} Rusça başlığı boş!"
        assert bool(match.title_tr.strip()), f"{code} Türkçe açıklaması boş!"
        assert bool(match.title_en.strip()), f"{code} İngilizce açıklaması boş!"


def test_standards_library_crud_operations():
    """Kütüphaneye standart ekleme, düzenleme, silme ve arama CRUD testleri."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    try:
        mgr = StandardsLibraryManager(file_path=temp_path)
        initial_count = len(mgr.get_all())

        # 1. Add
        custom_item = StandardLibraryItem(
            id="test_custom_std",
            designation="ГОСТ 12345-2026",
            title_ru="Специальные металлические конструкции",
            title_tr="Özel Metal Konstrüksiyonlar",
            title_en="Special Metal Structures",
            section="Ссылочные документы",
            category="КМ Çelik Yapılar",
        )
        assert mgr.add(custom_item)
        assert len(mgr.get_all()) == initial_count + 1

        # 2. Get & Search
        found = mgr.get_by_designation("ГОСТ 12345-2026")
        assert found is not None
        assert found.title_tr == "Özel Metal Konstrüksiyonlar"

        # Türkçe ile ara
        results_tr = mgr.search("Özel Metal")
        assert len(results_tr) >= 1
        assert any(r.designation == "ГОСТ 12345-2026" for r in results_tr)

        # İngilizce ile ara
        results_en = mgr.search("Special Metal")
        assert len(results_en) >= 1
        assert any(r.designation == "ГОСТ 12345-2026" for r in results_en)

        # 3. Update
        custom_item.title_tr = "Güncellenmiş Özel Çelik Yapılar"
        assert mgr.update(custom_item)
        updated = mgr.get_by_designation("ГОСТ 12345-2026")
        assert updated.title_tr == "Güncellenmiş Özel Çelik Yapılar"

        # 4. Delete
        assert mgr.delete("test_custom_std")
        assert mgr.get_by_designation("ГОСТ 12345-2026") is None
        assert len(mgr.get_all()) == initial_count

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_reference_docs_builder_table_dimensions():
    """ГОСТ Р 21.101 Form 2 tablo ölçülerinin (185 mm) ve başlık yapısının doğrulanması."""
    doc = standards_library.build_default_document()
    table = create_reference_docs_table(doc)

    assert isinstance(table, Table)
    assert round(table.total_width, 1) == 185.0

    # Sütun genişlikleri: 60, 95, 30
    assert len(table.columns) == 3
    assert table.columns[0].width == 60.0
    assert table.columns[1].width == 95.0
    assert table.columns[2].width == 30.0

    # Satır 0: Tablo Başlığı (185 mm birleşik)
    row_title = table.rows[0]
    assert row_title.height == 12.0
    assert row_title.cells[0].colspan == 3
    assert row_title.cells[0].text == "Ведомость ссылочных и прилагаемых документов"
    assert row_title.cells[0].halign == HAlign.CENTER

    # Satır 1: Sütun Başlıkları
    row_headers = table.rows[1]
    assert row_headers.cells[0].text == "Обозначение"
    assert row_headers.cells[1].text == "Наименование"
    assert row_headers.cells[2].text == "Примечание"

    # Satır 2: Bölüm Ayraç Satırı
    row_sec = table.rows[2]
    assert row_sec.cells[0].text == ""
    assert row_sec.cells[1].text == "Ссылочные документы"
    assert row_sec.cells[2].text == ""

    # Kalan satırlar: Standart verileri
    assert len(table.rows) >= 16  # Başlık + Sütunlar + Bölüm + 14 standart
    row_first_std = table.rows[3]
    assert row_first_std.cells[0].text == "ГОСТ 27751-2014"
    assert "Надёжность строительных конструкций" in row_first_std.cells[1].text


def test_reference_docs_validator():
    """Doğrulayıcı (Validator) kuralları."""
    doc = standards_library.build_default_document()
    res = ReferenceDocsValidator.validate(doc)
    assert res.is_valid

    # Boş doküman
    empty_doc = ReferenceDocsDocument(items=[])
    res_empty = ReferenceDocsValidator.validate(empty_doc)
    assert not res_empty.is_valid

    # Sadece bölüm başlığı olan doküman
    sec_only_doc = ReferenceDocsDocument(items=[
        ReferenceDocItem(title="Ссылочные документы", is_section_header=True)
    ])
    res_sec_only = ReferenceDocsValidator.validate(sec_only_doc)
    assert not res_sec_only.is_valid


def test_reference_docs_module_in_registry():
    """TableRegistry entegrasyonu ve TableModule sözleşmesi."""
    mod = TableRegistry.get("reference_documents")
    assert mod is not None
    assert isinstance(mod, ReferenceDocsModule)
    assert "Ведомость ссылочных" in mod.name
    assert mod.is_active
    assert mod.supports_preview

    doc = mod.create_default_document()
    table = mod.build_table(doc)
    assert isinstance(table, Table)
    assert round(table.total_width, 1) == 185.0


def test_reference_docs_editor_widget(qapp):
    """ReferenceDocsEditorWidget arayüzü, çok dilli sütunlar ve düzenleme sinyalleri."""
    editor = ReferenceDocsEditorWidget()
    assert editor.table.columnCount() == 6
    assert editor.table.rowCount() >= 15

    # Başlıkların çift dilli olduğunu doğrula
    h0 = editor.table.horizontalHeaderItem(0).text()
    h2 = editor.table.horizontalHeaderItem(2).text()
    h3 = editor.table.horizontalHeaderItem(3).text()
    assert "Обозначение" in h0
    assert "Türkçe" in h2
    assert "English" in h3

    # Yeni doküman satırı ekleme
    initial_rows = editor.table.rowCount()
    editor._add_doc_row()
    assert editor.table.rowCount() == initial_rows + 1

    # Düzenleme sinyali
    emitted = []
    editor.document_changed.connect(lambda d: emitted.append(d))
    editor.table.item(editor.table.rowCount() - 1, 0).setText("СП 999.13330")
    assert len(emitted) >= 1
    assert any(it.designation == "СП 999.13330" for it in editor.get_document().items)

    editor.close()


def test_reference_docs_dxf_export(tmp_path):
    """Form 2 tablosunun 1:1 ölçekle DXF dışa aktarımı."""
    doc = standards_library.build_default_document()
    table = create_reference_docs_table(doc)
    exporter = DxfExporter()

    out_file = str(tmp_path / "test_form2_ref_docs.dxf")
    res = exporter.export(
        table=table,
        output_path=out_file,
        layout_config=DEFAULT_LAYOUT_CONFIG,
    )
    assert res is True
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000


def test_all_designations_centered_and_long_name_font_scaling():
    """
    Kullanıcı talebi doğrulaması:
    1. Tüm standart kodları (Обозначение) istisnasız HAlign.CENTER ile ortalanmalı.
    2. Uzun standart adları alt satıra geçmeli ve font küçülmeli.
    3. Maksimum yazı boyutu standartlardan alınmalı (2.5 mm tavan).
    """
    from src.models.text_layout import wrap_cell_text, estimate_block_height

    doc = standards_library.build_default_document()
    table = create_reference_docs_table(doc)

    # 1. Tüm standart kodları (Обозначение) ortalı olmalı
    # Satır 0: Başlık, Satır 1: Sütun başlıkları, Satır 2: Bölüm başlığı
    # Satır 3+: Dokümanlar
    for r_idx in range(3, len(table.rows)):
        cell_desig = table.rows[r_idx].cells[0]
        if cell_desig.text.strip():
            assert cell_desig.halign == HAlign.CENTER, (
                f"Satır #{r_idx} ({cell_desig.text}) HAlign.CENTER olmalı!"
            )

    # Özellikle uzun kodlar da ortalanmalı
    sto_arss_row = next(r for r in table.rows if "СТО АРСС" in r.cells[0].text)
    assert sto_arss_row.cells[0].halign == HAlign.CENTER

    sp_470_row = next(r for r in table.rows if "СП 470" in r.cells[0].text)
    assert sp_470_row.cells[0].halign == HAlign.CENTER

    # 2. Kısa isim: Standart maksimum yazı boyutunu (2.5 mm) korumalı
    short_title = "Стальные конструкции"
    lines_s, fh_s = wrap_cell_text(
        short_title,
        max_width_mm=93.0,
        max_height_mm=6.4,
        target_font_size_mm=2.5
    )
    assert fh_s == 2.5, "Kısa isim standart tavan yazı boyutu olan 2.5 mm'yi korumalı"
    assert len(lines_s) == 1

    # 3. Uzun isim: Alt satıra geçmeli ve font boyutu tavanın altına inmeli
    long_title = "Надёжность строительных конструкций и оснований. Основные положения"
    lines_l, fh_l = wrap_cell_text(
        long_title,
        max_width_mm=93.0,
        max_height_mm=6.4,
        target_font_size_mm=2.5
    )
    assert len(lines_l) >= 2, "Uzun isim alt satıra geçmeli"
    assert fh_l <= 2.5, "Maksimum yazı boyutu tavanı (2.5 mm) aşamaz"
    assert fh_l < 2.5, "Uzun isim hücreye rahat sığması için fontu küçültmeli"
    tot_h = estimate_block_height(lines_l, fh_l)
    assert tot_h <= 6.4, "Toplam blok yüksekliği hücre kullanılabilir yüksekliğini aşamaz"

