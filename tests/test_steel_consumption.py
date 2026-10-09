"""
KM Tablo Oluşturucu - İkinci Modül (Ведомость расхода стали) Kapsamlı Test Paketi.
Model, Builder, Validator, Editor, DXF Export ve Mimari Bağımsızlık Testleri.
"""
import os
import sys
import tempfile
import inspect
import pytest
import ezdxf

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from src.contracts.table_module import TableModule, ValidationResult
from src.config.sheet_config import (
    LayoutConfig, SheetSize, SheetOrientation, TablePlacement
)
from src.models.sheet import SheetLayoutCalculator
from src.models.registry import TableRegistry
from src.ui.i18n import i18n
from src.tables.steel_consumption.model import (
    SteelConsumptionItem, SteelConsumptionDocument, build_sample_steel_consumption
)
from src.tables.steel_consumption.config import (
    SteelConsumptionConfig, DEFAULT_STEEL_CONSUMPTION_CONFIG
)
from src.tables.steel_consumption.builder import create_steel_consumption_table
from src.tables.steel_consumption.validator import SteelConsumptionValidator
from src.tables.steel_consumption.editor import SteelConsumptionEditorWidget
from src.tables.steel_consumption.module import SteelConsumptionModule
from src.export.dxf_exporter import DxfExporter
from src.ui.app import KmMainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


# ==============================================================================
# 1. DOMAIN MODEL & SAMPLE DATA TEST
# ==============================================================================
def test_steel_consumption_model_and_samples():
    item = SteelConsumptionItem(
        mark="Б1",
        i_beam=100.5,
        channel=50.0,
        angle=25.5,
        tube=10.0,
        plate=14.0
    )
    assert item.calculate_total() == 200.0

    doc = SteelConsumptionDocument(items=[item])
    totals = doc.get_column_totals()
    assert totals["i_beam"] == 100.5
    assert totals["channel"] == 50.0
    assert totals["angle"] == 25.5
    assert totals["tube"] == 10.0
    assert totals["plate"] == 14.0
    assert totals["total"] == 200.0
    assert doc.get_grand_total() == 200.0

    samples = build_sample_steel_consumption()
    assert len(samples) >= 5
    sample_marks = [s.mark for s in samples]
    assert "Б1" in sample_marks
    assert "К1" in sample_marks


# ==============================================================================
# 2. TABLE BUILDER & GOST MATRIX TEST
# ==============================================================================
def test_steel_consumption_builder_table_structure():
    doc = SteelConsumptionDocument(items=build_sample_steel_consumption())
    table = create_steel_consumption_table(doc)

    assert table.title == "Ведомость расхода стали, кг"
    assert len(table.columns) == 7

    # 2 Seviyeli Başlık Satırı Kontrolleri
    assert len(table.rows) == len(doc.items) + 3  # 2 Header + Data rows + 1 Total row
    r_h1 = table.rows[0]
    r_h2 = table.rows[1]
    assert r_h1.is_header is True
    assert r_h2.is_header is True
    assert r_h1.cells[0].rowspan == 2
    assert r_h1.cells[1].colspan == 5  # Profil sarfiyat grubu

    # Veri satırları
    for r_idx in range(2, 2 + len(doc.items)):
        assert table.rows[r_idx].is_header is False
        assert len(table.rows[r_idx].cells) == 7

    # Toplam (Итого) Satırı
    total_row = table.rows[-1]
    assert total_row.cells[0].text == "Итого:"
    grand_total_cell = total_row.cells[6]
    assert float(grand_total_cell.text.replace(",", ".")) == doc.get_grand_total()


# ==============================================================================
# 3. STATIK VALIDATOR TESTLERI
# ==============================================================================
def test_steel_consumption_validator():
    # Geçerli veri
    valid_doc = SteelConsumptionDocument(items=build_sample_steel_consumption())
    res_valid = SteelConsumptionValidator.validate(valid_doc)
    assert res_valid.is_valid is True

    # Boş liste
    empty_doc = SteelConsumptionDocument(items=[])
    res_empty = SteelConsumptionValidator.validate(empty_doc)
    assert res_empty.is_valid is False
    assert "henüz eleman tanımlanmamış" in res_empty.summary_message

    # Boş Marka
    invalid_mark = [SteelConsumptionItem(mark="", i_beam=100.0)]
    res_mark = SteelConsumptionValidator.validate(invalid_mark)
    assert res_mark.is_valid is False
    assert "Eleman markası boş" in res_mark.summary_message

    # Yinelenen Marka
    dup_marks = [
        SteelConsumptionItem(mark="Б1", i_beam=100.0),
        SteelConsumptionItem(mark="Б1", i_beam=50.0),
    ]
    res_dup = SteelConsumptionValidator.validate(dup_marks)
    assert res_dup.is_valid is False
    assert "Yinelenen eleman markası" in res_dup.summary_message

    # Negatif Ağırlık
    neg_weight = [SteelConsumptionItem(mark="К1", i_beam=-50.0)]
    res_neg = SteelConsumptionValidator.validate(neg_weight)
    assert res_neg.is_valid is False
    assert "negatif olamaz" in res_neg.summary_message

    # Sıfır Sarfiyat
    zero_weight = [SteelConsumptionItem(mark="К2")]
    res_zero = SteelConsumptionValidator.validate(zero_weight)
    assert res_zero.is_valid is False
    assert "Hiçbir profil ağırlığı girilmemiş" in res_zero.summary_message


# ==============================================================================
# 4. PYSIDE6 EDITOR WIDGET DAVRANIŞ TESTLERİ
# ==============================================================================
def test_steel_consumption_editor_widget_interactions(qapp):
    editor = SteelConsumptionEditorWidget()
    editor.show()
    tw = editor.table_widget

    # Yoğunluk: 26px satır yüksekliği
    assert tw.verticalHeader().defaultSectionSize() == 26

    # Satır ekleme
    initial_rows = tw.rowCount()
    editor._add_row()
    assert tw.rowCount() == initial_rows + 1

    # Satır silme
    tw.selectRow(initial_rows)
    editor._delete_selected_row()
    assert tw.rowCount() == initial_rows

    # Yukarı / Aşağı taşıma
    m0 = editor.items[0].mark
    m1 = editor.items[1].mark
    tw.selectRow(0)
    editor._move_row(1)
    assert editor.items[1].mark == m0
    tw.selectRow(1)
    editor._move_row(-1)
    assert editor.items[0].mark == m0

    # Örnek verileri sıfırlama
    editor._reset_to_samples()
    assert tw.rowCount() == 7

    # Canlı hücre düzenleme ve otomatik toplam
    # 0. satır 1. sütun (Двутавры): 100.0 yap
    tw.item(0, 1).setText("100.0")
    editor._on_cell_changed(0, 1)
    row_total_cell = tw.item(0, 6)
    assert row_total_cell is not None
    assert float(row_total_cell.text().replace(",", ".")) >= 100.0

    # Klavye simülasyonları: Enter -> alt hücre, Tab -> yan hücre
    tw.setCurrentCell(0, 0)
    ev_enter = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    tw.keyPressEvent(ev_enter)
    assert tw.currentRow() == 1

    ev_tab = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier)
    tw.keyPressEvent(ev_tab)
    assert tw.currentColumn() == 1

    # Pano (Clipboard) Kopyalama
    tw.selectRow(0)
    editor._copy_to_clipboard()
    copied = QApplication.clipboard().text() or getattr(editor, "_last_copied_text", "")
    assert len(copied) > 0

    # Kiril Karakter Şeridi
    editor._insert_char_to_active_cell("Б")
    assert tw.currentItem() is not None

    editor.close()


# ==============================================================================
# 5. DXF DIŞA AKTARMA TESTİ
# ==============================================================================
def test_steel_consumption_dxf_export():
    mod = SteelConsumptionModule()
    doc = mod.create_default_document()
    table = mod.build_table(doc)

    exporter = DxfExporter()
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        success = exporter.export(table, tmp_path)
        assert success is True
        assert os.path.exists(tmp_path)
        assert os.path.getsize(tmp_path) > 1000

        # ezdxf ile çizim varlıklarını doğrula
        dxf_doc = ezdxf.readfile(tmp_path)
        entities = list(dxf_doc.modelspace())
        assert len(entities) > 50
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ==============================================================================
# 6. TABLE MODULE KONTRAT TESTİ
# ==============================================================================
def test_steel_consumption_module_contract():
    mod = SteelConsumptionModule()
    assert isinstance(mod, TableModule)
    assert mod.id == "vedomost_raskhoda_stali"
    assert "Ведомость расхода стали" in mod.name
    assert "КМ" in mod.category
    assert mod.supports_preview is True

    doc = mod.create_default_document()
    assert isinstance(doc, SteelConsumptionDocument)

    tbl = mod.build_table(doc)
    assert tbl is not None

    val = mod.validate(doc)
    assert val.is_valid is True

    fn = mod.default_export_filename(doc)
    assert fn.endswith(".dxf")


# ==============================================================================
# 7. MİMARİ TEST: app.py DEĞİŞTİRİLMEDEN OTOMATİK KEŞİF
# ==============================================================================
def test_architecture_zero_modification_to_app_py():
    """
    KmMainWindow kaynak kodunda tabloya özel doğrudan import veya
    if/else bulunmadığını ve modülün TableRegistry üzerinden dinamik
    yüklendiğini doğrular.
    """
    from src.ui import app as app_module
    source = inspect.getsource(app_module)

    # KmMainWindow içinde 'SteelConsumption' sınıfı doğrudan import EDİLMEMELİ
    assert "from src.tables.steel_consumption" not in source
    assert "SteelConsumptionModule" not in source
    assert "SteelConsumptionEditorWidget" not in source
    assert "SteelConsumptionDocument" not in source
    assert "SteelConsumptionValidator" not in source

    # TableRegistry üzerinden ikinci modül kayıtlı olmalı
    mod = TableRegistry.get("vedomost_raskhoda_stali")
    assert mod is not None
    assert mod.id == "vedomost_raskhoda_stali"


# ==============================================================================
# 8. ÇİFT TABLO GEÇİŞİ VE CANLI WORKSPACE ADAPTASYONU
# ==============================================================================
def test_switching_between_tables_and_preview_update(qapp):
    """
    Gerçek QApplication ile iki tablo arasında dinamik geçiş,
    editörün ve CAD tuvali varlıklarının güncellenmesi ve
    her iki modülde de DXF export üretimi.
    """
    window = KmMainWindow()
    window.show()

    # 1. Başlangıçta Varsayılan: Elements Schedule
    assert window.active_module.id == "vedomost_elementov"
    init_scene_items = len(window.cad_workspace.canvas.scene().items())
    assert init_scene_items > 0

    # 2. İkinci Tabloya Geçiş: Steel Consumption
    window._switch_to_table_id("vedomost_raskhoda_stali")
    assert window.active_module.id == "vedomost_raskhoda_stali"
    assert type(window.editor_widget).__name__ == "SteelConsumptionEditorWidget"
    assert "Ведомость расхода стали" in window.lbl_active_table_title.text()

    sc_scene_items = len(window.cad_workspace.canvas.scene().items())
    assert sc_scene_items > 0

    # İkinci tabloda DXF export doğrulaması
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        exp_res = window.dxf_exporter.export(
            window.current_table,
            tmp_path,
            layout_config=window.layout_config
        )
        assert exp_res is True
        assert os.path.exists(tmp_path)
        assert os.path.getsize(tmp_path) > 1000
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 3. Tekrar İlk Tabloya Dönüş
    window._switch_to_table_id("vedomost_elementov")
    assert window.active_module.id == "vedomost_elementov"
    assert type(window.editor_widget).__name__ == "ElementsScheduleWidget"
    assert "Ведомость элементов" in window.lbl_active_table_title.text()

    window.close()


# ==============================================================================
# 9. NON-NUMERIC INPUT & RAW_VALUES VALIDASYON TESTİ
# ==============================================================================
def test_steel_consumption_non_numeric_validation(qapp):
    # 1. raw_values ile validator testi
    item = SteelConsumptionItem(mark="Б1", i_beam=0.0, raw_values={"i_beam": "не число"})
    res = SteelConsumptionValidator.validate([item])
    assert res.is_valid is False
    assert "не число" in res.summary_message

    # 2. Editör üzerinde metin girilmesi ve otomatik raw_values yakalanması
    editor = SteelConsumptionEditorWidget()
    editor.show()
    tw = editor.table_widget

    # 0. satır 1. sütuna geçersiz metin yaz
    tw.item(0, 1).setText("XYZ")
    editor._on_cell_changed(0, 1)

    assert "i_beam" in editor.items[0].raw_values
    assert editor.items[0].raw_values["i_beam"] == "XYZ"

    doc = editor.get_document()
    doc_res = SteelConsumptionValidator.validate(doc)
    assert doc_res.is_valid is False
    assert "XYZ" in doc_res.summary_message

    # Hücreyi geçerli sayıya düzelt
    tw.item(0, 1).setText("125.5")
    editor._on_cell_changed(0, 1)

    assert "i_beam" not in editor.items[0].raw_values
    assert editor.items[0].i_beam == 125.5
    doc_valid = editor.get_document()
    assert SteelConsumptionValidator.validate(doc_valid).is_valid is True

    editor.close()


# ==============================================================================
# 10. 185 MM ГОСТ FORM 3 ANTET VE PAFTA YERLEŞİM UYUMU TESTİ
# ==============================================================================
def test_steel_consumption_185mm_geometry_and_sheet_layout():
    # 1. 185 mm Form 3 antet genişliği uyumluluğu
    cfg = SteelConsumptionConfig()
    assert cfg.columns.total_width == 185.0
    assert cfg.columns.mark == 35.0
    assert cfg.columns.i_beam == 25.0
    assert cfg.columns.channel == 25.0
    assert cfg.columns.angle == 25.0
    assert cfg.columns.tube == 25.0
    assert cfg.columns.plate == 25.0
    assert cfg.columns.total == 25.0

    doc = SteelConsumptionDocument(items=build_sample_steel_consumption())
    table = create_steel_consumption_table(doc, cfg)
    assert table.total_width == 185.0

    # 2. A3 yatay paftada ABOVE_TITLEBLOCK yerleşimi
    layout_cfg = LayoutConfig(
        placement=TablePlacement.ABOVE_TITLEBLOCK,
        size=SheetSize.A3,
        orientation=SheetOrientation.LANDSCAPE
    )
    calc = SheetLayoutCalculator.calculate(table, layout_cfg)

    # Tablo genişliği (185) antet genişliği (185) ile birebir örtüşmeli
    assert calc.title_block_rect.width == 185.0
    assert calc.table_width == 185.0
    assert calc.table_origin.x == calc.title_block_rect.x_min
    assert calc.table_origin.x + calc.table_width == calc.title_block_rect.x_max
    # Antetin hemen üstünde başlamalı (y = 5 + 55 = 60.0)
    assert calc.table_origin.y == 60.0


# ==============================================================================
# 11. CANLI EDİTÖR -> CAD TUVALİ VE STATÜ SENKRONİZASYON TESTİ
# ==============================================================================
def test_steel_consumption_live_editor_to_cad_sync(qapp):
    window = KmMainWindow()
    window.show()
    window._switch_to_table_id("vedomost_raskhoda_stali")
    assert window.active_module.id == "vedomost_raskhoda_stali"

    # Hücre değerini değiştir: Satır 0, Sütun 2 (channel) -> "350.0"
    tw = window.editor_widget.table_widget
    tw.item(0, 2).setText("350.0")
    window.editor_widget._on_cell_changed(0, 2)

    # Model ve CAD Table nesnesinin anında güncellendiğini doğrula
    assert window.editor_widget.items[0].channel == 350.0
    # CAD Table: Satır index 2 (0 ve 1 başlık), Sütun index 2 (channel)
    assert window.current_table.rows[2].cells[2].text == "350"
    # İtogo satırı güncellenmeli
    total_row = window.current_table.rows[-1]
    assert float(total_row.cells[6].text.replace(",", ".")) == window.current_document.get_grand_total()

    # StatusBar kontrolü: Yeşil hazır durumu
    status_text = window.lbl_status.text()
    assert ("Hazır" in status_text or "Ready" in status_text or "Готово" in status_text)

    # Hata durumu: Hücreye geçersiz değer gir
    tw.item(0, 2).setText("hata_degeri")
    window.editor_widget._on_cell_changed(0, 2)

    status_err = window.lbl_status.text()
    assert ("Uyarı" in status_err or "Warning" in status_err or "Внимание" in status_err)
    assert "hata_degeri" in status_err

    # Düzelt
    tw.item(0, 2).setText("50.0")
    window.editor_widget._on_cell_changed(0, 2)
    status_fixed = window.lbl_status.text()
    assert ("Hazır" in status_fixed or "Ready" in status_fixed or "Готово" in status_fixed)

    window.close()


# ==============================================================================
# 12. DİNAMİK ÇOK DİLLİ (TR / RU / EN) DEĞİŞİM TESTİ
# ==============================================================================
def test_steel_consumption_dynamic_i18n_cycle(qapp):
    window = KmMainWindow()
    window.show()
    window._switch_to_table_id("vedomost_raskhoda_stali")
    ed = window.editor_widget

    # TR Testi
    i18n.set_language("TR")
    assert ed.lbl_title.text() == i18n.t("steel_consumption_title")
    assert ed.btn_add.text() == i18n.t("add_element")
    assert "eleman" in ed.lbl_count.text()

    # RU Testi
    i18n.set_language("RU")
    assert ed.lbl_title.text() == i18n.t("steel_consumption_title")
    assert ed.btn_add.text() == i18n.t("add_element")
    assert "элем" in ed.lbl_count.text()

    # EN Testi
    i18n.set_language("EN")
    assert ed.lbl_title.text() == i18n.t("steel_consumption_title")
    assert ed.btn_add.text() == i18n.t("add_element")
    assert "elements" in ed.lbl_count.text()

    # TR'ye geri dön
    i18n.set_language("TR")
    window.close()


# ==============================================================================
# 13. DXF KATMANLARI VE MODELSPACE ÇİZİM VARLIKLARI TESTİ
# ==============================================================================
def test_steel_consumption_dxf_layers_and_entities():
    mod = SteelConsumptionModule()
    doc = mod.create_default_document()
    table = mod.build_table(doc)

    exporter = DxfExporter()
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        layout_cfg = LayoutConfig(
            placement=TablePlacement.ABOVE_TITLEBLOCK,
            size=SheetSize.A3,
            orientation=SheetOrientation.LANDSCAPE
        )
        success = exporter.export(table, tmp_path, layout_config=layout_cfg)
        assert success is True

        dxf_doc = ezdxf.readfile(tmp_path)
        layers = {l.dxf.name for l in dxf_doc.layers}
        assert "KM_TABLO_CERCEVE" in layers
        assert "KM_TABLO_IZGARA" in layers
        assert "KM_TABLO_METIN" in layers
        assert "KM_SAYFA_CERCEVE" in layers
        assert "KM_ANTET" in layers

        # Modelspace varlıklarını denetle
        msp = dxf_doc.modelspace()
        texts = [e.dxf.text for e in msp if e.dxftype() == "TEXT"]
        assert any("Ведомость расхода стали" in t for t in texts)
        assert any("Итого" in t for t in texts)
        assert any("Б1" in t for t in texts)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

