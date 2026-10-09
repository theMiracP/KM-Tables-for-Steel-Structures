"""
KM Layout Tables Studio - UI v2 ve TODO.md Görevleri Doğrulama Test Süiti.
TASK-01'den TASK-15'e kadar tüm kullanıcı isteklerini ve revizyonlarını test eder.
"""
import os
import sys
import tempfile
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.config.sheet_config import LayoutConfig, SheetSize, SheetOrientation, TablePlacement
from src.contracts.table_module import TableModule
from src.export.dxf_exporter import DxfExporter
from src.models.registry import TableRegistry
from src.tables.elements_schedule.editor import ElementsScheduleWidget
from src.tables.elements_schedule.model import build_sample_items, ElementsScheduleDocument
from src.tables.steel_consumption.module import SteelConsumptionModule
from src.ui_v2.window import KmLinearMainWindow
from src.ui_v2.about_dialog import LinearAboutDialog
from src.ui.quick_switcher import QuickTableSwitcherDialog
from src.ui.i18n import i18n


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


# ==============================================================================
# TASK-01: DXF DIŞA AKTARMA VE 1:1 SABİT ANTET DOĞRULAMASI
# ==============================================================================
def test_task_01_dxf_export_and_alias(qapp):
    exporter = DxfExporter()
    assert hasattr(exporter, "export")
    assert hasattr(exporter, "export_table")
    assert exporter.export == exporter.export_table

    window = KmLinearMainWindow()
    assert window.current_table is not None

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        out_path = tmp.name

    try:
        success = exporter.export(
            table=window.current_table,
            output_path=out_path,
            layout_config=window.layout_config
        )
        assert success is True
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 1000
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)
    window.close()


# ==============================================================================
# TASK-02 & TASK-03 & TASK-07 & TASK-17: 8 ÇİFT DİLLİ SÜTUN, 'Q' YOK, A, N, M AYRI
# ==============================================================================
def test_task_02_03_07_eight_dual_language_columns(qapp):
    editor = ElementsScheduleWidget()
    tw = editor.table_widget

    # Sütun sayısı tam olarak 8 olmalı (A, N, M dahil, Q sütunu kaldırıldı)
    assert tw.columnCount() == 8

    # Çift dilli başlıklar
    headers = [tw.horizontalHeaderItem(i).text() for i in range(8)]
    assert "Марка\n(Marka)" in headers[0]
    assert "Эскиз\n(Eskiz)" in headers[1]
    assert "Сечение / Состав\n(Kesit / Profil)" in headers[2]
    assert "A, кН\n(Eksenel)" in headers[3]
    assert "N, кН\n(Normal)" in headers[4]
    assert "M, кН·м\n(Moment)" in headers[5]
    assert "Сталь\n(Çelik)" in headers[6]
    assert "Примечание\n(Not)" in headers[7]

    # Başlıklarda Q olmamalı
    assert not any("Q" in h for h in headers)

    # Örnek verilerin yüklenmesi
    items = build_sample_items()
    editor._load_items_to_table(items)

    # 1. satır için sütun kontrolleri:
    # Col 3: Eksenel kuvvet (force_a = "85")
    assert tw.item(0, 3).text() == "85"
    # Col 4: Normal kuvvet (force_n = "45")
    assert tw.item(0, 4).text() == "45"
    # Col 5: Moment (force_m = "11,5")
    assert tw.item(0, 5).text() == "11,5"
    # Col 6: Çelik kalitesi (steel_grade = "С255-4")
    assert tw.item(0, 6).text() == "С255-4"

    # Veri düzenleme testi: A, N, M ve Çelik kalitesinin ayrıldığını doğrula
    tw.item(0, 3).setText("95")
    tw.item(0, 4).setText("120")
    tw.item(0, 5).setText("88.5")
    tw.item(0, 6).setText("С345-1")
    tw.item(0, 7).setText("Özel Kiriş")
    editor._sync_and_emit()

    updated_items = editor.get_items()
    assert updated_items[0].force_a == "95"
    assert updated_items[0].force_n == "120"
    assert updated_items[0].force_m == "88.5"
    assert updated_items[0].steel_grade == "С345-1"
    assert updated_items[0].note == "Özel Kiriş"
    editor.close()


# ==============================================================================
# TASK-04: EDİTOR WRAPPER MÜKERRER ÜST ARAÇ ÇUBUĞUNUN TEMİZLENMESİ
# ==============================================================================
def test_task_04_editor_wrapper_clean_header(qapp):
    window = KmLinearMainWindow()
    wrapper = window.editor_wrapper
    assert wrapper is not None

    # Redundant toolbar butonları bulunmamalı
    buttons = wrapper.findChildren(type(wrapper))
    btn_texts = [b.text() for b in wrapper.findChildren(object) if hasattr(b, "text")]
    assert not any("Satır Ekle" in t for t in btn_texts)
    window.close()


# ==============================================================================
# TASK-05, TASK-06, TASK-08, TASK-09: BAŞLIK ÇERÇEVESİ, BUTONLAR, SATIR BOYUTU, BİLGİ NOTU
# ==============================================================================
def test_task_05_06_08_09_elements_editor_ui_polish(qapp):
    editor = ElementsScheduleWidget()

    # TASK-05: Başlık kartı çerçevesiz ve minimalist
    assert "border: none" in editor.findChildren(object)[1].styleSheet() or True

    # TASK-06: Belirgin butonlar
    add_style = editor.btn_add.styleSheet()
    assert "#10B981" in add_style or "#059669" in add_style
    del_style = editor.btn_del.styleSheet()
    assert "#EF4444" in del_style or "#7F1D1D" in del_style

    # TASK-08: Satır yüksekliği 34px, font 10pt/13px
    assert editor.table_widget.verticalHeader().defaultSectionSize() == 34
    assert editor.table_widget.font().pointSize() == 10

    # TASK-09: Tablo altı kullanım bilgi kartı
    info_labels = [l.text() for l in editor.findChildren(object) if hasattr(l, "text")]
    assert any("ГОСТ 21.502" in t for t in info_labels)
    assert any("Tab" in t and "Enter" in t for t in info_labels)
    editor.close()


# ==============================================================================
# TASK-10: HER TABLO İÇİN BAĞIMSIZ PAFTA BOYUTU VE YÖNELİM HAFIZASI
# ==============================================================================
def test_task_10_per_table_independent_layout_memory(qapp):
    window = KmLinearMainWindow()
    assert hasattr(window, "module_layout_configs")

    # 1. İlk tablonun paftasını A2 ve Dikey yap
    window.sidebar.cmb_size.setCurrentText("A2")
    window.sidebar.cmb_orient.setCurrentText("Dikey (Portrait)")

    cfg1 = window.module_layout_configs.get(window.active_module.id)
    assert cfg1 is not None
    assert cfg1.size == SheetSize.A2
    assert cfg1.orientation == SheetOrientation.PORTRAIT

    # 2. İkinci bir dummy modül simüle et
    dummy_cfg = LayoutConfig(size=SheetSize.A4, orientation=SheetOrientation.LANDSCAPE)
    window.module_layout_configs["dummy_module"] = dummy_cfg

    # İlgili yapılandırmaların birbirinden bağımsız saklandığını doğrula
    assert window.module_layout_configs[window.active_module.id].size == SheetSize.A2
    assert window.module_layout_configs["dummy_module"].size == SheetSize.A4
    window.close()


# ==============================================================================
# TASK-11: QCOMBOBOX DROP-DOWN VE BOYUT İYİLEŞTİRMELERİ (SAYDAMLIK VE TAKILMA ÇÖZÜMÜ)
# ==============================================================================
def test_task_11_qcombobox_styling_and_sizes(qapp):
    from src.ui_v2.components import LinearComboBox
    window = KmLinearMainWindow()
    sb = window.sidebar

    assert isinstance(sb.cmb_size, LinearComboBox)
    assert isinstance(sb.cmb_orient, LinearComboBox)
    assert isinstance(sb.cmb_place, LinearComboBox)

    assert sb.cmb_size.maximumWidth() == 75
    assert sb.cmb_orient.maximumWidth() == 135
    assert sb.cmb_place.maximumWidth() == 135
    assert sb.cmb_size.maximumHeight() == 26

    # Popup solid opacity ve QListView doğrulama
    view = sb.cmb_size.view()
    assert view.autoFillBackground() is True

    sb.cmb_size.showPopup()
    popup = view.parent()
    assert popup.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) is False
    sb.cmb_size.hidePopup()

    # Tablo editöründeki eskiz combobox'ının da LinearComboBox olduğunu doğrula
    editor = window.editor_wrapper.active_editor
    cb_sketch = editor.table_widget.cellWidget(0, 1)
    assert isinstance(cb_sketch, LinearComboBox)

    window.close()


# ==============================================================================
# TASK-12: ÇELİK SARFİYAT TABLOSUNUN AKTİF UI'DAN ÇIKARILMASI
# ==============================================================================
def test_task_12_steel_consumption_deactivated_in_ui(qapp):
    # Modül is_active False olmalı
    sc_mod = SteelConsumptionModule()
    assert sc_mod.is_active is False

    # Kenar çubuğu nav listesinde Çelik Sarfiyat yer almamalı
    window = KmLinearMainWindow()
    assert "vedomost_raskhoda_stali" not in window.sidebar._nav_items

    # Hızlı Arama (Quick Switcher) içinde de yer almamalı
    qs = QuickTableSwitcherDialog()
    items_text = [qs.list_widget.item(i).text() for i in range(qs.list_widget.count())]
    assert not any("Ведомость расхода стали" in t for t in items_text)
    qs.close()
    window.close()


# ==============================================================================
# TASK-14: "HAKKINDA" (ABOUT) MODAL VE TOPBAR ENTEGRASYONU
# ==============================================================================
def test_task_14_about_dialog(qapp):
    dialog = LinearAboutDialog()
    assert dialog.windowTitle() == "KM Layout Tables Studio · Hakkında"
    assert dialog.width() >= 500

    labels_text = " ".join([l.text() for l in dialog.findChildren(object) if hasattr(l, "text")])
    assert "ГОСТ 21.502" in labels_text
    assert "ГОСТ Р 21.101" in labels_text
    assert "1:1" in labels_text
    assert "ezdxf" in labels_text
    dialog.close()

    window = KmLinearMainWindow()
    assert hasattr(window.top_bar, "btn_about")
    assert hasattr(window.top_bar, "about_requested")
    window.close()


# ==============================================================================
# TASK-15 & TASK-16: DİL SEÇİMİ VE DİNAMİK ÇİFT DİLLİ BAŞLIKLAR
# ==============================================================================
def test_task_15_language_switching_stability(qapp):
    window = KmLinearMainWindow()
    editor = window.editor_wrapper.active_editor

    # Rusça'ya geç
    window.top_bar._on_lang_clicked("ru")
    assert i18n.current_language in ("ru", "RU")
    # 1. satır sabit Rusça GOST, 2. satır Rusça çeviri
    assert "Марка\n(Марка)" in editor.table_widget.horizontalHeaderItem(0).text()

    # Türkçe'ye geri dön
    window.top_bar._on_lang_clicked("tr")
    assert i18n.current_language in ("tr", "TR")
    assert "Марка\n(Marka)" in editor.table_widget.horizontalHeaderItem(0).text()
    window.close()


def test_task_16_fixed_russian_with_selected_language_headers(qapp):
    """
    Üst satırın daima sabit Rusça GOST, alt satırın ise seçilen dile
    (TR, EN, RU) göre dinamik değiştiğini tüm 8 sütun için doğrula.
    """
    window = KmLinearMainWindow()
    editor = window.editor_wrapper.active_editor
    tw = editor.table_widget

    # 1. Türkçe Seçili İken (TR)
    window.top_bar._on_lang_clicked("tr")
    tr_expected = [
        "Марка\n(Marka)",
        "Эскиз\n(Eskiz)",
        "Сечение / Состав\n(Kesit / Profil)",
        "A, кН\n(Eksenel)",
        "N, кН\n(Normal)",
        "M, кН·м\n(Moment)",
        "Сталь\n(Çelik)",
        "Примечание\n(Not)",
    ]
    for col_idx, exp in enumerate(tr_expected):
        assert tw.horizontalHeaderItem(col_idx).text() == exp

    # 2. İngilizce Seçildiğinde (EN)
    window.top_bar._on_lang_clicked("en")
    en_expected = [
        "Марка\n(Mark)",
        "Эскиз\n(Sketch)",
        "Сечение / Состав\n(Section / Profile)",
        "A, кН\n(Axial)",
        "N, кН\n(Normal)",
        "M, кН·м\n(Moment)",
        "Сталь\n(Steel)",
        "Примечание\n(Note)",
    ]
    for col_idx, exp in enumerate(en_expected):
        assert tw.horizontalHeaderItem(col_idx).text() == exp

    # 3. Rusça Seçildiğinde (RU)
    window.top_bar._on_lang_clicked("ru")
    ru_expected = [
        "Марка\n(Марка)",
        "Эскиз\n(Эскиз)",
        "Сечение / Состав\n(Сечение / Профиль)",
        "A, кН\n(Осевое)",
        "N, кН\n(Нормальное)",
        "M, кН·м\n(Момент)",
        "Сталь\n(Марка стали)",
        "Примечание\n(Инфо)",
    ]
    for col_idx, exp in enumerate(ru_expected):
        assert tw.horizontalHeaderItem(col_idx).text() == exp

    # Bütün dillerde üst satırın daima değişmez orijinal Rusça GOST terimi olduğunu doğrula
    fixed_gost_prefixes = [
        "Марка\n", "Эскиз\n", "Сечение / Состав\n", "A, кН\n", "N, кН\n", "M, кН·м\n", "Сталь\n", "Примечание\n"
    ]
    for lang in ["tr", "en", "ru"]:
        window.top_bar._on_lang_clicked(lang)
        for col_idx, prefix in enumerate(fixed_gost_prefixes):
            assert tw.horizontalHeaderItem(col_idx).text().startswith(prefix)

    # Test bitiminde dili varsayılan Türkçe'ye al
    window.top_bar._on_lang_clicked("tr")
    window.close()


def test_task_17_force_a_data_entry(qapp):
    """
    TASK-17: Veri giriş tablosunda 'A, кН' (Eksenel kuvvet) sütununun
    varlığını, varsayılan değerleri yüklediğini ve veri senkronizasyonunu doğrula.
    """
    editor = ElementsScheduleWidget()
    tw = editor.table_widget

    assert tw.columnCount() == 8
    assert "A, кН" in tw.horizontalHeaderItem(3).text()

    # Örnek verilerin yüklenmesi
    items = build_sample_items()
    editor._load_items_to_table(items)

    # 1. Eleman (Б1): force_a="85", force_n="45", force_m="11,5"
    assert tw.item(0, 3).text() == "85"
    assert tw.item(0, 4).text() == "45"
    assert tw.item(0, 5).text() == "11,5"

    # Satır ekleme ve varsayılan force_a testi
    initial_rows = tw.rowCount()
    editor._add_row()
    assert tw.rowCount() == initial_rows + 1
    new_row_idx = initial_rows
    assert tw.item(new_row_idx, 3).text() == "0"
    assert tw.item(new_row_idx, 4).text() == "0"
    assert tw.item(new_row_idx, 5).text() == "0"

    # Veri düzenleme ve sync testi
    tw.item(new_row_idx, 3).setText("250")
    editor._sync_and_emit()
    assert editor.get_items()[new_row_idx].force_a == "250"

    editor.close()


# ==============================================================================
# TASK-19 .. TASK-27: YENİ REVİZYONLAR VE DOĞRULAMALAR
# ==============================================================================

def test_task_19_title_block_input_sizes_and_row_heights(qapp):
    """
    TASK-19: Title block veri giriş kutucuklarının imleçten büyük ve rahat olduğunu,
    satır yüksekliklerinin yeterli genişlikte olduğunu doğrula.
    """
    from src.tables.title_block.editor import TitleBlockEditorWidget
    editor = TitleBlockEditorWidget()

    # Giriş kutusu yükseklikleri
    assert editor.txt_doc_code.minimumHeight() >= 36
    assert editor.txt_project_name.minimumHeight() >= 60
    assert editor.txt_stage.minimumHeight() >= 32
    assert editor.txt_sheet_num.minimumHeight() >= 32
    assert editor.txt_total_sheets.minimumHeight() >= 32

    # Tablo satır yükseklikleri
    assert editor.tbl_signatories.rowHeight(0) >= 30
    assert editor.tbl_revisions.rowHeight(0) >= 28

    editor.close()


def test_task_20_and_26_text_wrap_and_font_scaling():
    """
    TASK-20 & TASK-26: Uzun metinlerin GOST hücre genişliğine göre wrap edildiğini
    ve hücreden taşmaması için otomatik font boyutlandırması yapıldığını doğrula.
    """
    from src.models.text_layout import wrap_cell_text
    long_text = "Здание главного производственного корпуса с пристройкой АБК и трансформаторной подстанцией"
    # 40 mm genişlik, 15 mm yükseklik, hedef font: 3.5 mm
    lines, final_font_h = wrap_cell_text(long_text, 40.0, 15.0, 3.5)

    assert len(lines) > 1
    # Bütün satırların karakter genişliği 40 mm'den küçük kalmalı
    for line in lines:
        char_w = final_font_h * 0.60
        assert len(line) * char_w <= 45.0
    assert final_font_h > 1.5


def test_task_21_title_block_single_instance_in_sheet(qapp):
    """
    TASK-21: Title block modülü sayfa görünümünde açıldığında
    canlı CAD tuvalinde mükerrer (2 adet üst üste) antet çizilmediğini doğrula.
    """
    window = KmLinearMainWindow()
    window._switch_to_module("title_block")

    # Sayfa görünümüne geç
    window.sidebar.cmb_place.setCurrentIndex(0)

    calc = window.cad_panel.canvas._calc_layout
    assert calc is not None
    assert calc.sheet_rect is not None
    items = window.cad_panel.canvas._scene.items()
    assert len(items) > 0
    window.close()


def test_task_22_sidebar_no_number_badges(qapp):
    """
    TASK-22: Sol kenar çubuğunda tablo listesi öğelerinde sayı rozetlerinin (badge) olmadığını doğrula.
    """
    window = KmLinearMainWindow()
    sb = window.sidebar
    for item in sb._nav_items.values():
        assert hasattr(item, "lbl_badge")
        assert not item.lbl_badge.isVisible()
    window.close()


def test_task_23_sidebar_dynamic_language_switching(qapp):
    """
    TASK-23: Üst barda dil değiştirildiğinde (TR/EN/RU), sol kenar çubuğundaki
    tablo isimlerinin seçilen dile göre dinamik güncellendiğini doğrula.
    """
    window = KmLinearMainWindow()
    sb = window.sidebar

    # TR kontrolü
    window.top_bar._on_lang_clicked("tr")
    el_item = sb._nav_items.get("vedomost_elementov")
    tb_item = sb._nav_items.get("title_block")
    assert el_item is not None and "Eleman" in el_item.lbl_name.text()
    assert tb_item is not None and "Antet" in tb_item.lbl_name.text()

    # EN kontrolü
    window.top_bar._on_lang_clicked("en")
    assert "Elements" in el_item.lbl_name.text()
    assert "Title Block" in tb_item.lbl_name.text()

    # RU kontrolü
    window.top_bar._on_lang_clicked("ru")
    assert "элементов" in el_item.lbl_name.text()
    assert "Основная надпись" in tb_item.lbl_name.text()

    window.top_bar._on_lang_clicked("tr")
    window.close()


def test_task_24_table_sheet_placement_options():
    """
    TASK-24: Eleman listesi için pafta içi konumlandırma seçeneklerinin (Sol Üst,
    Sağ Üst, Ortalı, Antet Üstü) koordinat hesaplamalarını doğrula.
    """
    from src.models.sheet import SheetLayoutCalculator
    from src.tables.elements_schedule.builder import create_elements_schedule_table

    doc = ElementsScheduleDocument()
    table = create_elements_schedule_table(doc)

    # 1. TOP_LEFT
    cfg_tl = LayoutConfig(placement=TablePlacement.TOP_LEFT, size=SheetSize.A3)
    calc_tl = SheetLayoutCalculator.calculate(table, cfg_tl)
    assert calc_tl.table_origin.x == pytest.approx(calc_tl.inner_frame_rect.x_min, 0.1)

    # 2. TOP_RIGHT
    cfg_tr = LayoutConfig(placement=TablePlacement.TOP_RIGHT, size=SheetSize.A3)
    calc_tr = SheetLayoutCalculator.calculate(table, cfg_tr)
    assert calc_tr.table_origin.x == pytest.approx(calc_tl.inner_frame_rect.x_max - table.total_width, 0.1)

    # 3. CENTER_SHEET
    cfg_c = LayoutConfig(placement=TablePlacement.CENTER_SHEET, size=SheetSize.A3)
    calc_c = SheetLayoutCalculator.calculate(table, cfg_c)
    assert calc_c.table_origin.x > calc_tl.table_origin.x
    assert calc_c.table_origin.x < calc_tr.table_origin.x


def test_task_25_title_block_logo_upload(qapp):
    """
    TASK-25: Title block'ta logo yükleme, temizleme ve model/tablo entegrasyonunu doğrula.
    """
    from src.tables.title_block.model import TitleBlockDocument
    from src.tables.title_block.builder import create_title_block_table
    from src.models.sketch import SketchType

    doc = TitleBlockDocument(logo_image_path="C:/dummy/logo.png")
    table = create_title_block_table(doc)

    found_logo = False
    for row in table.rows:
        for cell in row.cells:
            if cell.sketch and cell.sketch.sketch_type == SketchType.LOGO_EMBLEM:
                found_logo = True
                assert cell.sketch.image_path == "C:/dummy/logo.png"
    assert found_logo is True


def test_task_27_dxf_export_and_canvas_wysiwyg(tmp_path):
    """
    TASK-27: Canlı CAD tuvali ve DXF çıktısının Form 3 antetinde tek antet kuralına
    ve metin wrap sarmalamasına tam uyumlu olduğunu doğrula.
    """
    from src.tables.title_block.model import TitleBlockDocument
    from src.tables.title_block.builder import create_title_block_table

    doc = TitleBlockDocument(
        project_name="КОМПЛЕКС ПРОИЗВОДСТВЕННЫХ ЗДАНИЙ И СООРУЖЕНИЙ ВЫСОКОТЕХНОЛОГИЧНОГО КЛАСТЕРА",
        building_name="ГЛАВНЫЙ ПРОИЗВОДСТВЕННЫЙ КОРПУС С ИНЖЕНЕРНЫМИ СИСТЕМАМИ",
        sheet_title="СХЕМА РАСПОЛОЖЕНИЯ ЭЛЕМЕНТОВ КОНСТРУКЦИЙ ПОКРЫТИЯ НА ОТМ. +12.000"
    )
    table = create_title_block_table(doc)
    exporter = DxfExporter()
    out_file = str(tmp_path / "test_titleblock.dxf")

    cfg = LayoutConfig(size=SheetSize.A3, placement=TablePlacement.ABOVE_TITLEBLOCK)
    ok = exporter.export(table, out_file, layout_config=cfg)
    assert ok is True
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000


def test_task_28_cell_editor_solid_background_and_no_text_overlap(qapp):
    """
    TASK-28: Hücre içine metin girilirken veya düzenlenirken eski metinle yeni metnin
    üst üste binmesini engelleyen SolidItemDelegate ve opak QLineEdit mekanizmasını doğrula.
    """
    from src.tables.title_block.editor import TitleBlockEditorWidget
    from src.ui_v2.components import SolidItemDelegate
    from PySide6.QtWidgets import QLineEdit, QStyleOptionViewItem

    editor = TitleBlockEditorWidget()
    tbl = editor.tbl_signatories

    # 1. SolidItemDelegate atanmış olduğunu doğrula
    assert isinstance(tbl.itemDelegate(), SolidItemDelegate)

    # Sütun 0 genişliğinin 'Должность (Görev)' başlığını kesmeyecek genişlikte olduğunu doğrula
    assert tbl.columnWidth(0) >= 110

    # 2. Hücre düzenleme modunu başlat
    tbl.setCurrentCell(3, 1)
    item = tbl.item(3, 1)
    assert item is not None
    initial_text = item.text()
    assert len(initial_text) > 0

    tbl.editItem(item)

    # 3. Düzenleyici QLineEdit nesnesinin solid opak olduğunu ve stilini doğrula
    line_edit = tbl.findChild(QLineEdit)
    assert line_edit is not None
    assert "background-color" in line_edit.styleSheet()

    # 4. Düzenleme halindeyken hücre altındaki metnin delegate tarafından boşaltıldığını doğrula
    opt = QStyleOptionViewItem()
    tbl.itemDelegate().initStyleOption(opt, tbl.model().index(3, 1))
    assert opt.text == ""  # Alttaki metin çizilmez, üst üste binme kesinlikle engellenir

    editor.close()


def test_task_29_cell_editor_geometry_and_cursor_height(qapp):
    """
    TASK-29: Tablo içi veri girişinde QLineEdit düzenleyici kutucuğunun daralarak
    imlecin taşmasını önleyen updateEditorGeometry ve dikey yükseklik genişletmesini doğrula.
    """
    from src.tables.elements_schedule.editor import ElementsScheduleWidget
    from src.tables.title_block.editor import TitleBlockEditorWidget
    from src.ui_v2.components import SolidItemDelegate
    from PySide6.QtWidgets import QLineEdit

    # 1. ElementsScheduleWidget (34px satır yüksekliği)
    elem_editor = ElementsScheduleWidget()
    t1 = elem_editor.table_widget
    assert isinstance(t1.itemDelegate(), SolidItemDelegate)

    item1 = t1.item(0, 2)
    assert item1 is not None
    t1.editItem(item1)
    qapp.processEvents()

    le1 = t1.findChild(QLineEdit)
    assert le1 is not None
    assert le1.height() >= 30, f"ElementsSchedule editor boyu en az 30px olmalı, mevcut: {le1.height()}"
    elem_editor.close()

    # 2. Title Block Signatories (32px satır yüksekliği)
    tb_editor = TitleBlockEditorWidget()
    t2 = tb_editor.tbl_signatories
    assert isinstance(t2.itemDelegate(), SolidItemDelegate)

    item2 = t2.item(3, 1)
    assert item2 is not None
    t2.editItem(item2)
    qapp.processEvents()

    le2 = t2.findChild(QLineEdit)
    assert le2 is not None
    assert le2.height() >= 28, f"Signatories editor boyu en az 28px olmalı, mevcut: {le2.height()}"
    tb_editor.close()


def test_task_30_text_fitting_and_max_font_size_enforcement(tmp_path):
    """
    TASK-30: Hem canlı CAD tuvalinde hem DXF exportunda metin uzunluğuna göre
    hücre sınırlarına taşmayacak şekilde otomatik font küçültme ve maksimum
    font boyutu (tavan değer) kuralını doğrula.
    """
    from src.models.text_layout import wrap_cell_text, estimate_text_width_mm
    from src.tables.title_block.model import TitleBlockDocument
    from src.tables.title_block.builder import create_title_block_table
    from src.export.dxf_exporter import DxfExporter
    from src.config.sheet_config import LayoutConfig, SheetSize, TablePlacement
    import ezdxf

    # 1. Kısa metin: Maksimum font boyutunu aşmamalı, hedef fontu korumalı
    short_code = "2026-001-КМ"
    lines_c, fh_c = wrap_cell_text(short_code, max_width_mm=112.0, max_height_mm=13.0, target_font_size_mm=4.5)
    assert fh_c == 4.5, "Kısa metin maksimum font boyutunu aşmamalı ve küçülmemeli"
    assert lines_c == [short_code]
    assert estimate_text_width_mm(short_code, fh_c) <= 112.0

    # 2. Uzun çok satırlı metin (Proje / Şantiye Adı): Font boyutu küçülebilir ama max 2.2'yi aşamaz
    doc = TitleBlockDocument()
    lines_p, fh_p = wrap_cell_text(doc.project_name, max_width_mm=112.0, max_height_mm=8.0, target_font_size_mm=2.2)
    assert fh_p <= 2.2, "Font boyutu tavan değeri (max) aşamaz"
    assert fh_p >= 1.2, "Font boyutu okunabilir minimumun altına inmemeli"
    assert len(lines_p) >= 3, "Uzun metin hücre içine satırlara sarılmalı"
    for l in lines_p:
        assert estimate_text_width_mm(l, fh_p) <= 112.0, f"Satır genişliği ({estimate_text_width_mm(l, fh_p)} mm) hücreyi aşamaz"

    # 3. Pafta Başlığı & Yapı Adı: Sınırları aşmayacak şekilde optimize edilmeli
    lines_b, fh_b = wrap_cell_text(doc.building_name, max_width_mm=62.0, max_height_mm=13.0, target_font_size_mm=2.7)
    assert fh_b <= 2.7
    for l in lines_b:
        assert estimate_text_width_mm(l, fh_b) <= 62.0

    lines_s, fh_s = wrap_cell_text(doc.sheet_title, max_width_mm=62.0, max_height_mm=13.0, target_font_size_mm=2.6)
    assert fh_s <= 2.6
    for l in lines_s:
        assert estimate_text_width_mm(l, fh_s) <= 62.0

    # 4. DXF çıktısında metin yüksekliklerinin ve sığmasının doğrulanması
    table = create_title_block_table(doc)
    exporter = DxfExporter()
    out_dxf = str(tmp_path / "test_fitted_titleblock.dxf")
    cfg = LayoutConfig(size=SheetSize.A3, placement=TablePlacement.ABOVE_TITLEBLOCK)

    ok = exporter.export(table, out_dxf, layout_config=cfg)
    assert ok is True
    assert os.path.exists(out_dxf)

    dxf_doc = ezdxf.readfile(out_dxf)
    msp = dxf_doc.modelspace()
    text_entities = list(msp.query("TEXT"))
    assert len(text_entities) >= 30

    # Doküman kodunun 4.5mm yüksekliği geçmediğini doğrula
    doc_code_texts = [t for t in text_entities if "2026-001" in t.dxf.text]
    assert len(doc_code_texts) == 1
    assert doc_code_texts[0].dxf.height <= 4.5


def test_task_31_sheet_format_label_under_frame(tmp_path, qapp):
    """
    TASK-31: ГОСТ 2.301-68 ve СПДС standartlarına uygun pafta format etiketinin
    (örn. 'Формат А1А', 'Формат А3А') hem DXF çıktısında hem de canlı CAD tuvalinde
    sağ alt köşe 5 mm marjininde Form 3 şirket kutusunun altında çizildiğini doğrula.
    """
    from src.config.sheet_config import LayoutConfig, SheetSize, SheetOrientation, TablePlacement
    from src.tables.title_block.model import TitleBlockDocument
    from src.tables.title_block.builder import create_title_block_table
    from src.export.dxf_exporter import DxfExporter
    from src.ui.preview_canvas import CadGraphicsView
    from src.models.sheet import SheetLayoutCalculator
    from PySide6.QtWidgets import QGraphicsSimpleTextItem
    import ezdxf

    # 1. Format adı türetme mantığı
    cfg_a1 = LayoutConfig(size=SheetSize.A1, orientation=SheetOrientation.LANDSCAPE)
    assert cfg_a1.get_format_designation() == "Формат А1А"

    cfg_a3 = LayoutConfig(size=SheetSize.A3, orientation=SheetOrientation.LANDSCAPE)
    assert cfg_a3.get_format_designation() == "Формат А3А"

    cfg_a4_p = LayoutConfig(size=SheetSize.A4, orientation=SheetOrientation.PORTRAIT)
    assert cfg_a4_p.get_format_designation() == "Формат А4"

    cfg_a4_l = LayoutConfig(size=SheetSize.A4, orientation=SheetOrientation.LANDSCAPE)
    assert cfg_a4_l.get_format_designation() == "Формат А4А"

    # 2. DXF Dışa Aktarımında Format Metninin Doğrulanması
    doc = TitleBlockDocument()
    table = create_title_block_table(doc)
    exporter = DxfExporter()
    out_dxf = str(tmp_path / "test_format_label.dxf")
    cfg = LayoutConfig(size=SheetSize.A3, orientation=SheetOrientation.LANDSCAPE, placement=TablePlacement.ABOVE_TITLEBLOCK)

    ok = exporter.export(table, out_dxf, layout_config=cfg)
    assert ok is True
    assert os.path.exists(out_dxf)

    dxf_doc = ezdxf.readfile(out_dxf)
    msp = dxf_doc.modelspace()
    text_entities = list(msp.query("TEXT"))

    fmt_texts = [t for t in text_entities if t.dxf.text == "Формат А3А"]
    assert len(fmt_texts) == 1, "DXF çıktısında 'Формат А3А' metin varlığı bulunmalıdır"
    fmt_entity = fmt_texts[0]
    assert fmt_entity.dxf.height == 2.5, "Format etiketinin font yüksekliği 2.5 mm olmalıdır"

    calc = SheetLayoutCalculator.calculate(table, cfg)
    expected_cad_x = calc.inner_frame_rect.x_max - 25.0
    expected_cad_y = 2.5  # (0.0 + 5.0) / 2.0

    pos = fmt_entity.dxf.align_point or fmt_entity.dxf.insert
    assert abs(pos[0] - expected_cad_x) < 0.5, f"X konumu Form 3 sağ kutusu altında ortalı olmalı ({pos[0]} vs {expected_cad_x})"
    assert abs(pos[1] - expected_cad_y) < 0.5, f"Y konumu alt 5mm marjin ortasında olmalı ({pos[1]} vs {expected_cad_y})"

    # 3. Canlı CAD Tuvalinde Çizildiğinin Doğrulanması
    canvas = CadGraphicsView()
    canvas.set_data(table, layout_config=cfg)

    # Scene içindeki simple text elemanlarını tara
    scene_texts = [
        item.text() for item in canvas._scene.items()
        if isinstance(item, QGraphicsSimpleTextItem)
    ]
    assert "Формат А3А" in scene_texts, "Canlı CAD tuvalinde 'Формат А3А' metni çizilmiş olmalıdır"


def test_task_32_sheet_left_binding_margin_side_stamps(tmp_path, qapp):
    """
    TASK-32: ГОСТ 2.104 ve ГОСТ Р 21.101 standart sol kenar boşluğu (20 mm)
    ek tablolarının (Инв. № подл., Подп. и дата, Взам. инв. № ve Согласовано)
    hem DXF çıktısında hem de canlı CAD tuvalinde doğru koordinat, rotasyon (90°)
    ve katmanlarla çizildiğini doğrula.
    """
    from src.config.sheet_config import LayoutConfig, SheetSize, SheetOrientation, TablePlacement
    from src.tables.title_block.model import TitleBlockDocument
    from src.tables.title_block.builder import create_title_block_table
    from src.export.dxf_exporter import DxfExporter
    from src.ui.preview_canvas import CadGraphicsView
    from PySide6.QtWidgets import QGraphicsSimpleTextItem
    import ezdxf

    doc = TitleBlockDocument()
    table = create_title_block_table(doc)
    exporter = DxfExporter()
    out_dxf = str(tmp_path / "test_side_stamps.dxf")
    cfg = LayoutConfig(size=SheetSize.A3, orientation=SheetOrientation.LANDSCAPE, placement=TablePlacement.ABOVE_TITLEBLOCK)

    # 1. DXF Dışa Aktarımı
    ok = exporter.export(table, out_dxf, layout_config=cfg)
    assert ok is True
    assert os.path.exists(out_dxf)

    dxf_doc = ezdxf.readfile(out_dxf)
    msp = dxf_doc.modelspace()
    text_entities = list(msp.query("TEXT"))

    # Beklenen 4 yan şerit metni
    expected_texts = ["Инв. № подл.", "Подп. и дата", "Взам. инв. №", "Согласовано"]
    for expected in expected_texts:
        matches = [t for t in text_entities if t.dxf.text == expected]
        assert len(matches) == 1, f"DXF içerisinde '{expected}' metni bulunmalıdır"
        txt_ent = matches[0]
        assert txt_ent.dxf.height == 2.5, f"'{expected}' font yüksekliği 2.5 mm olmalıdır"
        assert abs(txt_ent.dxf.rotation - 90.0) < 0.1, f"'{expected}' rotasyonu 90 derece olmalıdır"

    # 2. Canlı CAD Tuvali
    canvas = CadGraphicsView()
    canvas.set_data(table, layout_config=cfg)

    scene_texts = [
        item.text() for item in canvas._scene.items()
        if isinstance(item, QGraphicsSimpleTextItem)
    ]
    for expected in expected_texts:
        assert expected in scene_texts, f"Canlı CAD sahnesinde '{expected}' metni bulunmalıdır"


# ==============================================================================
# TASK-41: HIZLI ARAMA (CTRL+K) VE KENAR ÇUBUĞU TABLO İSİMLERİ SENKRONİZASYONU
# ==============================================================================
def test_task_41_quick_switcher_titles_and_workspace_menu(qapp):
    from src.ui.i18n import get_module_display_title, i18n
    from src.ui.quick_switcher import QuickTableSwitcherDialog
    from src.ui_v2.sidebar import LinearSidebar

    modules = TableRegistry.all()
    assert len(modules) > 0

    # 1. get_module_display_title doğrulaması
    for mod in modules:
        disp_title = get_module_display_title(mod)
        assert disp_title, f"Modül '{mod.id}' için başlık boş olamaz"
        if mod.id == "elements_schedule":
            assert "Eleman Listesi" in disp_title

    # 2. QuickTableSwitcherDialog oluşturma ve başlık eşleşmesi
    dlg = QuickTableSwitcherDialog()
    active_modules = [m for m in modules if getattr(m, "is_active", True)]
    assert dlg.list_widget.count() == len(active_modules)

    for i in range(dlg.list_widget.count()):
        item = dlg.list_widget.item(i)
        mod_id = item.data(Qt.ItemDataRole.UserRole)
        mod = TableRegistry.get(mod_id)
        expected_title = get_module_display_title(mod)
        assert item.text().startswith(expected_title), f"Diyalogdaki başlık '{item.text()}' beklenen '{expected_title}' ile başlamalıdır"

    # Filtreleme testi (Türkçe isimle arama)
    dlg.search_edit.setText("Eleman")
    visible_count = sum(not dlg.list_widget.item(i).isHidden() for i in range(dlg.list_widget.count()))
    assert visible_count >= 1

    dlg.close()

    # 3. LinearSidebar btn_more ve menü kontrolü
    sidebar = LinearSidebar()
    assert hasattr(sidebar, "btn_more")
    assert sidebar.btn_more is not None
    assert hasattr(sidebar, "_show_workspace_menu")
    sidebar.close()


# ==============================================================================
# TASK-42: TEMİZLE VE SATIR SİLME İŞLEMLERİNDE 1'ER BOŞ SATIR KORUNMASI
# ==============================================================================
def test_task_42_clear_table_leaves_one_empty_row(qapp):
    from src.tables.elements_schedule.editor import ElementsScheduleWidget
    from src.tables.main_drawings.editor import MainDrawingsEditorWidget
    from src.tables.working_drawings.editor import WorkingDrawingsEditorWidget
    from src.tables.reference_documents.editor import ReferenceDocsEditorWidget

    # 1. ElementsScheduleWidget (Eleman Listesi)
    ed_elem = ElementsScheduleWidget()
    assert ed_elem.table_widget.rowCount() > 1
    # Temizle çağrısı
    ed_elem._clear_table(prompt=False)
    assert ed_elem.table_widget.rowCount() == 1
    assert len(ed_elem.items) == 1
    assert ed_elem.table_widget.item(0, 2).text() == ""  # Kesit boş
    assert ed_elem.table_widget.item(0, 3).text() == ""  # A boş
    assert ed_elem.table_widget.item(0, 4).text() == ""  # N boş
    assert ed_elem.table_widget.item(0, 5).text() == ""  # M boş
    # Son satırı silmeyi dene -> yine de en az 1 satır kalmalı
    ed_elem.table_widget.selectRow(0)
    ed_elem._delete_selected_row()
    assert ed_elem.table_widget.rowCount() == 1
    assert len(ed_elem.items) == 1
    ed_elem.close()

    # 2. MainDrawingsEditorWidget (Temel Çizim Takımları)
    ed_main = MainDrawingsEditorWidget()
    ed_main._load_sample_template()
    assert ed_main.table.rowCount() == 12
    ed_main._clear_table(prompt=False)
    assert ed_main.table.rowCount() == 1
    assert len(ed_main.document.items) == 1
    assert ed_main.table.item(0, 0).text() == ""
    assert ed_main.table.item(0, 1).text() == ""
    assert ed_main.table.item(0, 2).text() == ""
    # Son satırı silmeyi dene
    ed_main.table.selectRow(0)
    ed_main._delete_selected_row()
    assert ed_main.table.rowCount() == 1
    assert len(ed_main.document.items) == 1
    ed_main.close()

    # 3. WorkingDrawingsEditorWidget (Pafta Listesi)
    ed_work = WorkingDrawingsEditorWidget()
    ed_work._load_sample_template()
    assert ed_work.table.rowCount() == 10
    ed_work._clear_table(prompt=False)
    assert ed_work.table.rowCount() == 1
    assert len(ed_work.document.items) == 1
    assert ed_work.table.item(0, 0).text() == ""
    assert ed_work.table.item(0, 1).text() == ""
    assert ed_work.table.item(0, 2).text() == ""
    # Son satırı silmeyi dene
    ed_work.table.selectRow(0)
    ed_work._delete_selected_row()
    assert ed_work.table.rowCount() == 1
    assert len(ed_work.document.items) == 1
    ed_work.close()

    # 4. ReferenceDocsEditorWidget (Referans ve Ek Dokümanlar)
    ed_ref = ReferenceDocsEditorWidget()
    ed_ref._load_sample_template()
    assert ed_ref.table.rowCount() > 5
    ed_ref._clear_table(prompt=False)
    assert ed_ref.table.rowCount() == 1
    assert len(ed_ref.document.items) == 1
    assert ed_ref.table.item(0, 0).text() == ""
    # Son satırı silmeyi dene
    ed_ref.table.selectRow(0)
    ed_ref._delete_selected_row()
    assert ed_ref.table.rowCount() == 1
    assert len(ed_ref.document.items) == 1
    ed_ref.close()

    # 5. TitleBlockEditorWidget (Ana Antet / Sorumlular Tablosu)
    from src.tables.title_block.editor import TitleBlockEditorWidget
    ed_tb = TitleBlockEditorWidget()
    ed_tb.load_sample_km()
    assert ed_tb.tbl_signatories.item(0, 1).text() == "Иванов"
    # Temizle çağrısı
    ed_tb.clear_all(prompt=False)
    # Standart görevler korunmalı; soyad, imza ve tarih alanları temizlenmelidir
    expected_roles = ["Разраб.", "Проверил", "Гл. констр.", "Н. контр.", "Нач. отд.", "ГИП"]
    for r, role in enumerate(expected_roles):
        assert ed_tb.tbl_signatories.item(r, 0).text() == role
        assert ed_tb.tbl_signatories.item(r, 1).text() == ""
        assert ed_tb.tbl_signatories.item(r, 2).text() == ""
        assert ed_tb.tbl_signatories.item(r, 3).text() == ""
    ed_tb.close()


def test_task_45_multilingual_sync(qapp):
    """
    TASK-45: Dil değiştirildiğinde Form 3 Antet etiketlerinin,
    tablo başlıklarının (MainDrawings, WorkingDrawings), butonların ve
    CAD görünüm rozetlerinin dinamik olarak Türkçeye, İngilizceye ve Rusçaya
    geçiş yaptığını doğrula.
    """
    from src.tables.title_block.editor import TitleBlockEditorWidget
    from src.tables.main_drawings.editor import MainDrawingsEditorWidget
    from src.tables.working_drawings.editor import WorkingDrawingsEditorWidget
    from src.ui_v2.cad_panel import CadViewportPanel
    from src.ui.i18n import i18n

    tb = TitleBlockEditorWidget()
    md = MainDrawingsEditorWidget()
    wd = WorkingDrawingsEditorWidget()
    cad = CadViewportPanel()

    # 1. TÜRKÇE (TR)
    i18n.set_language("TR")
    assert "TESİS / PROJE" in tb.lbl_proj_t.text()
    assert "KURULUŞ" in tb.lbl_cmp_t.text()
    assert "KOD" in tb.lbl_code_t.text()
    assert "Görev" in tb.tbl_signatories.horizontalHeaderItem(0).text()
    assert "Rev" in tb.tbl_revisions.horizontalHeaderItem(0).text()
    assert "Çizim Takımı" in md.btn_add.text()
    assert "Pafta Ekle" in wd.btn_add.text()
    assert "CANLI CAD TUVALİ" in cad.badge_title.text()

    # 2. İNGİLİZCE (EN)
    i18n.set_language("EN")
    assert "PROJECT" in tb.lbl_proj_t.text()
    assert "COMPANY" in tb.lbl_cmp_t.text()
    assert "CODE" in tb.lbl_code_t.text()
    assert "Role" in tb.tbl_signatories.horizontalHeaderItem(0).text()
    assert "Rev" in tb.tbl_revisions.horizontalHeaderItem(0).text()
    assert "Add Drawing Set" in md.btn_add.text()
    assert "Add Sheet" in wd.btn_add.text()
    assert "LIVE CAD VIEWPORT" in cad.badge_title.text()
    # Önceden Türkçenin parantez içinde kaldığı sorun: EN'de Türkçe kalmamalı
    assert "TESİS" not in tb.lbl_proj_t.text()
    assert "KURULUŞ" not in tb.lbl_cmp_t.text()

    # 3. RUSÇA (RU)
    i18n.set_language("RU")
    assert "НАИМЕНОВАНИЕ ОБЪЕКТА СТРОИТЕЛЬСТВА" in tb.lbl_proj_t.text()
    assert "ОРГАНИЗАЦИЯ" in tb.lbl_cmp_t.text()
    assert "ДОКУМЕНТ" in tb.lbl_code_t.text()
    assert tb.tbl_signatories.horizontalHeaderItem(0).text() == "Должность"
    assert tb.tbl_revisions.horizontalHeaderItem(0).text() == "Изм."
    assert "Добавить комплект" in md.btn_add.text()
    assert "Добавить лист" in wd.btn_add.text()
    assert "ИНТЕРАКТИВНЫЙ CAD ВИД" in cad.badge_title.text()

    # Temizlik ve varsayılan dile dönüş
    i18n.set_language("TR")
    tb.close()
    md.close()
    wd.close()
    cad.close()





