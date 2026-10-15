"""
ГОСТ Р 21.101-2020 Form 9 (Разрешение на внесение изменений) Test Süiti.
Model, Konfigürasyon, Neden Kodları (Таблица Л.1), CAD Table Builder, Doğrulayıcı,
DXF/PDF Dışa Aktarma, Preset/Proje Yönetimi ve UI Editör Entegrasyonu testleri.
"""
import os
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QApplication

from src.models.registry import TableRegistry
from src.models.table import Table, HAlign, VAlign
from src.config.sheet_config import LayoutConfig, SheetSize, SheetOrientation, TablePlacement
from src.tables.change_permission.config import (
    ChangePermissionConfig, ChangePermissionColumnWidths, REASON_CODES,
    DEFAULT_CHANGE_PERMISSION_CONFIG
)
from src.tables.change_permission.model import (
    ChangePermissionDocument, ChangePermissionItem, ChangeSignatoryEntry,
    build_default_change_signatories, build_empty_change_signatories,
    build_default_change_items
)
from src.tables.change_permission.builder import (
    create_change_permission_table, calculate_change_item_row_height
)
from src.tables.change_permission.validator import ChangePermissionValidator
from src.tables.change_permission.module import ChangePermissionModule
from src.tables.change_permission.editor import ChangePermissionEditorWidget
from src.export.dxf_exporter import DxfExporter
from src.export.pdf_exporter import PdfExporter
from src.services.preset_manager import PresetManager
from src.services.project_manager import ProjectManager
from src.ui.i18n import i18n, get_module_display_title


# =============================================================================
# 1. MODEL TESTLERİ (Görsel 2 Örneği ve Alan Bütünlüğü)
# =============================================================================
def test_change_permission_default_sample():
    """Form 9 kurgusal/jenerik örnek verilerini doğrular."""
    doc = ChangePermissionDocument.get_default_sample_document()

    assert doc.resolution_number == "001/26"
    assert doc.doc_code == "2026-001-КМ"
    assert "Северный" in doc.object_name
    assert doc.company_name == "ООО «ПРОЕКТ-СТРОЙ»"
    assert doc.sheet_num == "1"
    assert doc.sheet_count == "1"

    # 4 değişiklik satırı
    assert len(doc.items) == 4
    assert doc.items[0].rev_num == "1"
    assert doc.items[0].sheet == "1"
    assert "ведомость основных комплектов" in doc.items[0].content
    assert doc.items[0].reason_code == "1"

    assert doc.items[1].sheet == "3"
    assert doc.items[1].reason_code == "1"

    assert doc.items[2].sheet == "6"
    assert doc.items[2].reason_code == "1"

    assert doc.items[3].sheet == "7"
    assert doc.items[3].reason_code == "4"

    # 4 imza satırı
    assert len(doc.signatories) == 4
    roles = [s.role for s in doc.signatories]
    assert roles == ["Изм. внес", "Составил", "ГИП", "Утв."]
    surnames = [s.surname for s in doc.signatories]
    assert surnames == ["Иванов", "Петров", "Сидоров", "Кузнецов"]


def test_change_permission_empty_document():
    """Boş şablon oluşturmayı ve en az 1 satır kuralını test eder."""
    doc = ChangePermissionDocument.get_empty_document()
    assert doc.resolution_number == ""
    assert doc.doc_code == ""
    assert len(doc.items) == 1
    assert len(doc.signatories) == 4


def test_change_permission_serialization():
    """to_dict ve from_dict fonksiyonlarının veri kaybı yaşatmadığını doğrular."""
    doc = ChangePermissionDocument.get_default_sample_document()
    d = doc.to_dict()

    restored = ChangePermissionDocument.from_dict(d)
    assert restored.resolution_number == doc.resolution_number
    assert restored.doc_code == doc.doc_code
    assert restored.object_name == doc.object_name
    assert restored.company_name == doc.company_name
    assert len(restored.items) == len(doc.items)
    for orig_item, rest_item in zip(doc.items, restored.items):
        assert orig_item.rev_num == rest_item.rev_num
        assert orig_item.sheet == rest_item.sheet
        assert orig_item.content == rest_item.content
        assert orig_item.reason_code == rest_item.reason_code


# =============================================================================
# 2. KONFİGÜRASYON VE NEDEN KODLARI TESTLERİ (Görsel 1: Таблица Л.1)
# =============================================================================
def test_reason_codes_table():
    """Görsel 1'deki Tablo Л.1 değişiklik neden kodlarını doğrular."""
    assert len(REASON_CODES) == 6  # "" (Yok) + 1..5

    codes = [c[0] for c in REASON_CODES]
    assert codes == ["", "1", "2", "3", "4", "5"]

    # Kod 1
    c1 = next(c for c in REASON_CODES if c[0] == "1")
    assert c1[1] == "Введение усовершенствований"
    assert "İyileştirmelerin uygulanması" in c1[2]

    # Kod 2
    c2 = next(c for c in REASON_CODES if c[0] == "2")
    assert c2[1] == "Изменение стандартов и норм"

    # Kod 3
    c3 = next(c for c in REASON_CODES if c[0] == "3")
    assert c3[1] == "Дополнительные требования заказчика"

    # Kod 4
    c4 = next(c for c in REASON_CODES if c[0] == "4")
    assert c4[1] == "Устранение ошибок"

    # Kod 5
    c5 = next(c for c in REASON_CODES if c[0] == "5")
    assert c5[1] == "Другие причины"


def test_change_permission_dimensions():
    """Milimetrik boyutların ГОСТ Р 21.101 Form 9 standartlarına uygunluğunu doğrular."""
    cfg = DEFAULT_CHANGE_PERMISSION_CONFIG
    assert cfg.total_width == 185.0
    assert cfg.total_height == 287.0
    assert cfg.header_height == 45.0
    assert cfg.signatures_height == 20.0
    assert abs(cfg.columns.total_width - 185.0) < 1e-4


# =============================================================================
# 3. CAD TABLO BUILDER TESTLERİ
# =============================================================================
def test_change_permission_builder():
    """Builder'ın 185 x 287 mm Table modelini doğru hücre yapısıyla kurduğunu doğrular."""
    doc = ChangePermissionDocument.get_default_sample_document()
    table = create_change_permission_table(doc)

    assert table.id == "change_permission"
    assert abs(table.total_width - 185.0) < 1e-4
    assert abs(table.total_height - 287.0) < 1e-4

    # Satır sayısı: 3 başlık satırı + 4 veri satırı + 1 dolgu satırı + 4 imza satırı = 12 satır
    assert len(table.rows) == 12

    # Üst Başlık Satırları
    row0 = table.rows[0]
    assert row0.height == 10.0
    assert row0.cells[0].text == "Разрешение"
    assert row0.cells[3].text == "Обозначение"
    assert row0.cells[7].text == doc.doc_code

    row1 = table.rows[1]
    assert row1.height == 20.0
    assert row1.cells[0].text == doc.resolution_number
    assert "Наименование" in row1.cells[3].text
    assert row1.cells[7].text == doc.object_name

    row2 = table.rows[2]
    assert row2.height == 15.0
    assert row2.cells[0].text == "Изм."
    assert row2.cells[1].text == "Лист"
    assert row2.cells[3].text == "Содержание изменения"
    assert row2.cells[8].text == "Код"
    assert row2.cells[9].text == "Примечание"

    # Alt İmza Satırları (Son 4 satır)
    sig_rows = table.rows[-4:]
    assert sig_rows[0].cells[0].text == "Изм. внес"
    assert sig_rows[0].cells[2].text == "Иванов"
    assert sig_rows[0].cells[6].text == doc.company_name
    assert sig_rows[0].cells[10].text == "Лист"
    assert sig_rows[0].cells[11].text == "Листов"

    assert sig_rows[1].cells[0].text == "Составил"
    assert sig_rows[2].cells[0].text == "ГИП"
    assert sig_rows[2].cells[10].text == "1"
    assert sig_rows[2].cells[11].text == "1"

    assert sig_rows[3].cells[0].text == "Утв."


# =============================================================================
# 4. DOĞRULAYICI TESTLERİ
# =============================================================================
def test_change_permission_validator():
    """Doğrulayıcının eksik alanları ve geçersiz neden kodlarını yakaladığını test eder."""
    doc = ChangePermissionDocument.get_default_sample_document()
    res = ChangePermissionValidator.validate(doc)
    assert res.is_valid is True

    # Eksik izin no
    doc.resolution_number = ""
    res = ChangePermissionValidator.validate(doc)
    assert res.is_valid is False
    assert any("Разрешение №" in m for m in res.messages)

    # Geçersiz neden kodu
    doc.resolution_number = "008/26"
    doc.items[0].reason_code = "99"
    res = ChangePermissionValidator.validate(doc)
    assert res.is_valid is False
    assert any("Geçersiz değişiklik nedeni kodu" in m for m in res.messages)


# =============================================================================
# 5. TABLEREGISTRY VE MODÜL TESTLERİ
# =============================================================================
def test_change_permission_registry():
    """TableRegistry'de modülün doğru şekilde kayıtlı olduğunu doğrular."""
    mod = TableRegistry.get("change_permission")
    assert mod is not None
    assert mod.id == "change_permission"
    assert "Форма 9" in mod.name
    assert mod.supports_preview is True
    assert mod.is_active is True

    doc = mod.create_default_document()
    assert isinstance(doc, ChangePermissionDocument)
    tbl = mod.build_table(doc)
    assert isinstance(tbl, Table)
    assert abs(tbl.total_width - 185.0) < 1e-4

    fname = mod.default_export_filename(doc)
    assert "008_26" in fname or "Razreshenie" in fname


# =============================================================================
# 6. DXF VE PDF DIŞA AKTARMA TESTLERİ (1:1 Vektörel)
# =============================================================================
def test_change_permission_dxf_export(tmp_path):
    """DXF dışa aktarımında Form 9'un 1:1 ölçekle ve hatasız üretildiğini test eder."""
    mod = TableRegistry.get("change_permission")
    doc = mod.create_default_document()
    table = mod.build_table(doc)

    exporter = DxfExporter()
    out_file = str(tmp_path / "test_form9.dxf")

    cfg = LayoutConfig(size=SheetSize.A4, orientation=SheetOrientation.PORTRAIT, placement=TablePlacement.CENTER_SHEET)
    success = exporter.export(table, out_file, layout_config=cfg)

    assert success is True
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000

    # DXF içeriğini doğrula
    import ezdxf
    dxf_doc = ezdxf.readfile(out_file)
    assert dxf_doc.header["$INSUNITS"] == 4  # Millimeters
    texts = [e.dxf.text for e in dxf_doc.modelspace().query("TEXT")]
    # Başlık ve izin no metinleri bulunmalı
    assert any("001/26" in t for t in texts)
    assert any("2026-001-КМ" in t for t in texts)


def test_change_permission_pdf_export(tmp_path, qapp):
    """PDF dışa aktarımında Form 9'un vektör formatında üretildiğini test eder."""
    mod = TableRegistry.get("change_permission")
    doc = mod.create_default_document()
    table = mod.build_table(doc)

    pdf_exporter = PdfExporter()
    out_pdf = str(tmp_path / "test_form9.pdf")

    cfg = LayoutConfig(size=SheetSize.A4, orientation=SheetOrientation.PORTRAIT, placement=TablePlacement.CENTER_SHEET)
    success = pdf_exporter.export(table, out_pdf, layout_config=cfg)

    assert success is True
    assert os.path.exists(out_pdf)
    assert os.path.getsize(out_pdf) > 100


# =============================================================================
# 7. PRESET VE PROJE YÖNETİCİSİ TESTLERİ
# =============================================================================
def test_change_permission_preset_and_project(tmp_path):
    """Preset ve Proje (.kmproj) serileştirmesinde Form 9'un tam korunduğunu test eder."""
    doc = ChangePermissionDocument.get_default_sample_document()

    # PresetManager
    serialized = PresetManager.serialize_document("change_permission", doc)
    assert "resolution_number" in serialized
    assert serialized["resolution_number"] == "001/26"

    restored = PresetManager.deserialize_document("change_permission", serialized)
    assert isinstance(restored, ChangePermissionDocument)
    assert restored.doc_code == doc.doc_code

    # ProjectManager
    proj_file = str(tmp_path / "test.kmproj")
    ProjectManager.save_to_file(
        file_path=proj_file,
        project_name="TestProject",
        module_documents={"change_permission": doc},
        module_layout_configs={"change_permission": LayoutConfig(size=SheetSize.A4, orientation=SheetOrientation.PORTRAIT)},
        active_module_id="change_permission"
    )
    assert os.path.exists(proj_file)

    loaded_data = ProjectManager.load_from_file(proj_file)
    assert "change_permission" in loaded_data["module_documents"]
    loaded_doc = loaded_data["module_documents"]["change_permission"]
    assert isinstance(loaded_doc, ChangePermissionDocument)
    assert loaded_doc.resolution_number == "001/26"


# =============================================================================
# 8. UI EDİTÖR WİDGET TESTLERİ (Neden Kodları Seçimi & Butonlar)
# =============================================================================
def test_change_permission_editor_widget(qapp):
    """Editör arayüzünü, neden kodları ComboBox seçimini ve satır işlemlerini test eder."""
    editor = ChangePermissionEditorWidget()
    doc = ChangePermissionDocument.get_default_sample_document()
    editor.set_document(doc)

    assert editor.txt_res_num.text() == "001/26"
    assert editor.txt_doc_code.text() == "2026-001-КМ"
    assert editor.table_widget.rowCount() == 4

    # Sütun 3'teki ComboBox (Neden Kodu) testleri
    cb0 = editor.table_widget.cellWidget(0, 3)
    assert isinstance(cb0, QComboBox)
    assert cb0.currentData() == "1"

    cb3 = editor.table_widget.cellWidget(3, 3)
    assert isinstance(cb3, QComboBox)
    assert cb3.currentData() == "4"

    # Hızlı Kod Atama Butonu [2] testi
    editor.table_widget.setCurrentCell(0, 3)
    editor._apply_code_to_selected_row("2")
    assert cb0.currentData() == "2"

    # Satır ekleme
    initial_count = editor.table_widget.rowCount()
    editor._add_row()
    assert editor.table_widget.rowCount() == initial_count + 1

    # Satır silme
    editor.table_widget.setCurrentCell(editor.table_widget.rowCount() - 1, 0)
    editor._delete_selected_row()
    assert editor.table_widget.rowCount() == initial_count

    # Satır taşıma (Swap)
    item0_sheet = editor.table_widget.item(0, 1).text()
    item1_sheet = editor.table_widget.item(1, 1).text()
    editor.table_widget.setCurrentCell(0, 0)
    editor._move_row(1)
    assert editor.table_widget.item(0, 1).text() == item1_sheet
    assert editor.table_widget.item(1, 1).text() == item0_sheet

    # Boş şablon ve örnek şablon butonları
    editor._clear_all_fields()
    assert editor.txt_res_num.text() == ""
    assert editor.table_widget.rowCount() == 1  # TASK-42: En az 1 boş satır korunur

    editor._load_sample_template()
    assert editor.txt_res_num.text() == "001/26"
    assert editor.table_widget.rowCount() == 4


# =============================================================================
# 9. ÇOK DİLLİ SENKRONİZASYON (i18n) TESTLERİ
# =============================================================================
def test_change_permission_i18n(qapp):
    """TR, EN ve RU dillerinde Form 9 başlıklarının, butonlarının ve imzacı rollerinin doğruluğunu test eder."""
    editor = ChangePermissionEditorWidget()
    editor.show()

    # TR
    i18n.set_language("tr")
    title_tr = get_module_display_title("change_permission")
    assert "Form 9" in title_tr
    assert "Değişiklik İzni" in title_tr
    assert editor.btn_load_sample.text() == "📋 Örnek Şablon"
    assert "Görsel 2" not in editor.btn_load_sample.text()
    assert "Görsel 2" not in editor.btn_load_sample.toolTip()
    assert editor.sig_rows[0][0].text() == "Изм. внес (Rev. Yapan)"
    assert editor.sig_rows[1][0].text() == "Составил (Hazırlayan)"
    assert editor.sig_rows[2][0].text() == "ГИП (Proje Baş Müh.)"
    assert editor.sig_rows[3][0].text() == "Утв. (Onaylayan)"
    cb0 = editor.table_widget.cellWidget(0, 3)
    cb3 = editor.table_widget.cellWidget(3, 3)
    assert cb0.currentData() == "1"
    assert "İyileştirmelerin uygulanması" in cb0.currentText()
    assert cb3.currentData() == "4"
    assert "Hataların giderilmesi" in cb3.currentText()

    # EN
    i18n.set_language("en")
    title_en = get_module_display_title("change_permission")
    assert "Form 9" in title_en
    assert "Change Permission" in title_en
    assert editor.btn_load_sample.text() == "📋 Sample Template"
    assert editor.sig_rows[0][0].text() == "Изм. внес (Revised by)"
    assert editor.sig_rows[1][0].text() == "Составил (Prepared by)"
    assert editor.sig_rows[2][0].text() == "ГИП (Chief Project Eng.)"
    assert editor.sig_rows[3][0].text() == "Утв. (Approved by)"
    assert cb0.currentData() == "1"
    assert "Implementation of improvements" in cb0.currentText()
    assert cb3.currentData() == "4"
    assert "Correction of mistakes" in cb3.currentText()

    # RU
    i18n.set_language("ru")
    title_ru = get_module_display_title("change_permission")
    assert "Форма 9" in title_ru
    assert "Разрешение на внесение изменений" in title_ru
    assert editor.btn_load_sample.text() == "📋 Пример шаблона"
    assert editor.sig_rows[0][0].text() == "Изм. внес (Изменение внес)"
    assert editor.sig_rows[1][0].text() == "Составил (Разработал)"
    assert editor.sig_rows[2][0].text() == "ГИП (Главный инженер)"
    assert editor.sig_rows[3][0].text() == "Утв. (Утвердил)"
    assert cb0.currentData() == "1"
    assert "Введение усовершенствований" in cb0.currentText()
    assert cb3.currentData() == "4"
    assert "Устранение ошибок" in cb3.currentText()

    # Standart GOST Model Uyumluluğu: Modeldeki roller daima saf ГОСТ formatını korur
    doc = editor.get_document()
    assert doc.signatories[0].role == "Изм. внес"
    assert doc.signatories[1].role == "Составил"
    assert doc.signatories[2].role == "ГИП"
    assert doc.signatories[3].role == "Утв."
    assert doc.items[0].reason_code == "1"
    assert doc.items[3].reason_code == "4"

    # Geri TR'ye al
    i18n.set_language("tr")
    assert "İyileştirmelerin uygulanması" in cb0.currentText()
    assert "Hataların giderilmesi" in cb3.currentText()
    editor.close()
