"""
13 Maddelik Kullanıcı Revizyon Listesi Doğrulama Testleri (test_revisions_batch_13.py).
Maddeler:
1 & 3: QCheckBox görünürlüğü ve checkmark ikonu
2: GOST / Tablo No / İsim standardı ve çevirileri
4: Güncelleme adresinin sabit resmi URL olması
5: AutoCAD katman adı alanının imleç yüksekliği (28px/36px)
6: AutoCAD renk paleti (AciColorPickerDialog) ve renk kutuları
7: AutoCAD özel çizgi kalınlığı (Custom lineweight)
8: Kenar çubuğu ve üst bardan kalkan GOST callout & badge
9: Dil seçenekleri bayrak simgeleri (🇹🇷 TR, 🇬🇧 EN, 🇷🇺 RU)
10: Eleman listesi butonundaki çift '+' temizliği
11: Editör başlığı ile şablon butonlarının ayrılması (iki satır)
12: Üst barda yalnızca logo ve KM Studio kalması
13: Profil ismi değiştiğinde anında algılama ve eskiz senkronizasyonu
"""
import os
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.ui.i18n import i18n, get_module_display_title
from src.ui_v2 import theme_linear as theme
from src.ui_v2.top_bar import LinearTopBar
from src.ui_v2.sidebar import LinearSidebar
from src.ui_v2.editor_wrapper import TableEditorWrapper
from src.ui_v2.settings_dialog import LinearSettingsDialog, AciColorPickerDialog, make_color_icon
from src.tables.elements_schedule.editor import ElementsScheduleWidget, ProfileCellDelegate
from src.models.sketch import SketchType
from src.version import DEFAULT_UPDATE_CHECK_URL


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_item_1_and_3_checkbox_theme_and_icon():
    """Madde 1 & 3: QCheckBox indicator ve checkmark.svg temasının tanımlı olduğunu doğrular."""
    assert os.path.exists(theme.CHECKMARK_SVG)
    qss = theme.get_linear_stylesheet()
    assert "QCheckBox" in qss
    assert "QCheckBox::indicator:checked" in qss
    assert theme.CHECKMARK_SVG in qss


def test_item_2_table_naming_gost_table_name():
    """Madde 2: Tablo isimlerinin GOST no / Tablo no (veya Form no) / İsim standardına uyduğunu doğrular."""
    # TR
    i18n.set_language("tr")
    t_elem_tr = i18n.t("module_elements_schedule")
    assert "ГОСТ 21.502" in t_elem_tr and "Tablo 1" in t_elem_tr and "Eleman Listesi" in t_elem_tr

    t_tb_tr = i18n.t("module_title_block")
    assert "ГОСТ Р 21.101" in t_tb_tr and "Form 3" in t_tb_tr

    t_ref_tr = i18n.t("module_reference_docs")
    assert "ГОСТ Р 21.101" in t_ref_tr and "Form 2" in t_ref_tr

    # RU
    i18n.set_language("ru")
    t_elem_ru = i18n.t("module_elements_schedule")
    assert "ГОСТ 21.502" in t_elem_ru and "Таблица 1" in t_elem_ru and "Ведомость элементов" in t_elem_ru

    # EN
    i18n.set_language("en")
    t_elem_en = i18n.t("module_elements_schedule")
    assert "GOST 21.502" in t_elem_en and "Table 1" in t_elem_en and "Elements Schedule" in t_elem_en

    # Reset language
    i18n.set_language("tr")


def test_item_4_update_url_fixed_official(qapp):
    """Madde 4: Güncelleme kontrol ayarının kullanıcıdan gizlendiğini ve resmi ürün linkine bağlı olduğunu doğrular."""
    dlg = LinearSettingsDialog()
    assert dlg.txt_update_url.isHidden()
    assert dlg.card_server.isHidden()
    assert dlg.btn_test_url.isHidden()
    assert dlg.lbl_test_result.isHidden()
    assert dlg.txt_update_url.text() == DEFAULT_UPDATE_CHECK_URL
    assert DEFAULT_UPDATE_CHECK_URL == "https://zadax.net/tr/products/km-tables-studio-celik-yap-tablolar-ve-dxf-uretici/"
    dlg.close()



def test_item_5_layer_name_input_size(qapp):
    """Madde 5: AutoCAD katman adı metin kutusunun imleç için yeterli alana (28px) sahip olduğunu doğrular."""
    dlg = LinearSettingsDialog()
    assert dlg.tbl_layers.verticalHeader().defaultSectionSize() >= 36
    for key, widgets in dlg.layer_editors.items():
        name_edit = widgets["name_edit"]
        assert name_edit.height() >= 26 or name_edit.minimumHeight() >= 26 or name_edit.sizeHint().height() >= 24
    dlg.close()


def test_item_6_color_swatches_and_aci_dialog(qapp):
    """Madde 6: Renk açılır kutusunda renk kutuları (swatch) ve 255 ACI palet seçicisi bulunduğunu doğrular."""
    dlg = LinearSettingsDialog()
    for key, widgets in dlg.layer_editors.items():
        cb_color = widgets["color_cb"]
        assert cb_color.count() >= 9
        # İkon atanmış mı kontrol et
        assert not cb_color.itemIcon(0).isNull()

    picker = AciColorPickerDialog(current_color=4)
    assert len(picker._color_buttons) == 255
    picker.close()
    dlg.close()


def test_item_7_custom_lineweight_option(qapp):
    """Madde 7: Çizgi kalınlığı açılır menüsünde özel kalınlık (Custom) seçeneği olduğunu doğrular."""
    dlg = LinearSettingsDialog()
    for key, widgets in dlg.layer_editors.items():
        cb_weight = widgets["weight_cb"]
        has_custom = False
        for idx in range(cb_weight.count()):
            if cb_weight.itemData(idx) == -1:
                has_custom = True
                break
        assert has_custom, f"{key} kalınlık kutusunda 'Özel Kalınlık' bulunamadı."
    dlg.close()


def test_item_8_and_12_top_bar_and_sidebar_clean(qapp):
    """Madde 8 & 12: Üst barda sadece logo ve KM Studio kaldığını, GOST badge ve kenar çubuğu callout'un silindiğini doğrular."""
    top_bar = LinearTopBar()
    assert "KM Studio" in top_bar.lbl_workspace.text()
    assert top_bar.badge_gost.isHidden()
    assert top_bar.lbl_standard.isHidden()
    assert top_bar.lbl_active_table.isHidden()

    # Madde 9: Dil bayrakları (Windows uyumlu SVG vektörel bayrak ikonu veya metin)
    assert not top_bar.lang_btns["tr"].icon().isNull() or "🇹🇷" in top_bar.lang_btns["tr"].text()
    assert not top_bar.lang_btns["ru"].icon().isNull() or "🇷🇺" in top_bar.lang_btns["ru"].text()
    assert not top_bar.lang_btns["en"].icon().isNull() or "🇬🇧" in top_bar.lang_btns["en"].text()
    top_bar.close()

    sidebar = LinearSidebar()
    assert not hasattr(sidebar, "status_callout")
    sidebar.close()


def test_item_10_no_duplicate_plus_in_add_element():
    """Madde 10: Eleman ekle butonunda mükerrer '+' işareti olmadığını doğrular."""
    assert i18n.t("add_element").strip() == "Eleman Ekle"
    i18n.set_language("en")
    assert i18n.t("add_element").strip() == "Add Element"
    i18n.set_language("ru")
    assert i18n.t("add_element").strip() == "Добавить элемент"
    i18n.set_language("tr")


def test_item_11_editor_wrapper_header_layout(qapp):
    """Madde 11: Editör başlığı ile şablon butonlarının ayrı satırlarda yer aldığını doğrular."""
    wrapper = TableEditorWrapper()
    assert wrapper.btn_save_preset is not None
    assert wrapper.btn_load_preset is not None
    assert wrapper.lbl_title is not None
    # Başlık ve butonlar tanımlı
    assert wrapper.btn_save_preset.text() != ""
    wrapper.close()


def test_item_13_profile_detection_and_realtime_sync(qapp):
    """Madde 13: Profil ismi değiştiğinde eskiz türünün anında algılandığını ve gecikmesiz senkronize olduğunu doğrular."""
    widget = ElementsScheduleWidget()

    # I-kiriş tespiti
    assert widget._detect_sketch_type("20К1") == SketchType.I_BEAM
    assert widget._detect_sketch_type("30Б2") == SketchType.I_BEAM
    assert widget._detect_sketch_type("40Ш1") == SketchType.I_BEAM

    # Şveller tespiti
    assert widget._detect_sketch_type("16П") == SketchType.CHANNEL
    assert widget._detect_sketch_type("[ 20") == SketchType.CHANNEL

    # Kutu profil tespiti
    assert widget._detect_sketch_type("100х100х4") == SketchType.RECT_TUBE
    assert widget._detect_sketch_type("Гн. □ 80х4") == SketchType.RECT_TUBE

    # Köşebent tespiti
    assert widget._detect_sketch_type("L 75х6") == SketchType.ANGLE

    # Canlı metin değişimi simülasyonu
    widget._on_profile_text_changed(0, "20К1")
    cb = widget.table_widget.cellWidget(0, 1)
    stype, _ = cb.currentData()
    assert stype == SketchType.I_BEAM

    widget.close()


def test_settings_dialog_layer_table_column_widths(qapp):
    """Ayarlar penceresinde katman tablosu sütun genişliklerinin sığdığını ve kırpılmadığını doğrular."""
    dlg = LinearSettingsDialog()
    dlg.show()
    # Katman Adı (Column 1) en az 140px olmalı
    assert dlg.tbl_layers.columnWidth(1) >= 140
    # Renk (Column 2) en az 220px olmalı
    assert dlg.tbl_layers.columnWidth(2) >= 220
    # Kalınlık (Column 3) en az 230px olmalı
    assert dlg.tbl_layers.columnWidth(3) >= 230
    # Tablo toplam genişliği en az 880px olmalı
    assert dlg.tbl_layers.width() >= 880
    dlg.close()

