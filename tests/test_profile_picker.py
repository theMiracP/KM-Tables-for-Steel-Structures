"""
GOST Profil Veritabanı ve Seçici Testleri (Item 2.1).
"""
import pytest
from PySide6.QtWidgets import QApplication

from src.services.profile_database import GostProfileDatabase
from src.ui_v2.profile_picker_dialog import GostProfilePickerDialog
from src.models.sketch import SketchType


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_gost_profile_database_loading():
    db = GostProfileDatabase.instance()
    profiles = db.get_all()
    assert len(profiles) >= 40

    # Kategorileri kontrol et
    categories = db.get_categories()
    assert "Двутавры" in categories
    assert "Швеллеры" in categories
    assert "Трубы профильные" in categories
    assert "Трубы круглые" in categories
    assert "Уголки" in categories

    # Belirli profilleri ara
    rec_20b1 = db.lookup_by_designation("20Б1")
    assert rec_20b1 is not None
    assert rec_20b1.category == "Двутавры"
    assert rec_20b1.get_sketch_type_enum() == SketchType.I_BEAM
    assert rec_20b1.weight_kg_m > 20.0

    rec_16p = db.lookup_by_designation("16П")
    assert rec_16p is not None
    assert rec_16p.get_sketch_type_enum() == SketchType.CHANNEL

    rec_sq = db.lookup_by_designation("100х100х4")
    assert rec_sq is not None
    assert rec_sq.get_sketch_type_enum() == SketchType.RECT_TUBE


def test_gost_profile_database_filtering():
    db = GostProfileDatabase.instance()
    results = db.filter_profiles(query="30К1")
    assert len(results) == 1
    assert results[0].designation == "30К1"
    assert results[0].default_steel == "С345"

    channel_results = db.filter_profiles(category="Швеллеры")
    assert all(p.category == "Швеллеры" for p in channel_results)


def test_profile_picker_dialog(qapp):
    dlg = GostProfilePickerDialog(initial_query="20Б1")
    assert dlg.table.rowCount() >= 1
    assert dlg.table.columnCount() == 5
    assert dlg.search_edit.isClearButtonEnabled()
    
    # "Önerilen Çelik" sütununun kaldırıldığını doğrula
    headers = [dlg.table.horizontalHeaderItem(c).text() for c in range(dlg.table.columnCount())]
    assert not any("Çelik" in h for h in headers)
    
    assert dlg.selected_profile is not None
    assert dlg.selected_profile.designation == "20Б1"
    assert "С255" not in dlg.lbl_selected_info.text()
    
    # Arama temizleme testi
    dlg.search_edit.clear()
    assert dlg.search_edit.text() == ""
    assert dlg.table.rowCount() >= 40
    
    dlg.close()


def test_profile_picker_category_filter(qapp):
    """Kategori parametresiyle başlatılan seçicinin doğru filtrelendiğini test eder."""
    dlg = GostProfilePickerDialog(category="Швеллеры")
    assert dlg._current_category == "Швеллеры"
    assert dlg.table.rowCount() >= 5
    for r in range(dlg.table.rowCount()):
        assert dlg.table.item(r, 1).text() == "Швеллеры"
    dlg.close()


def test_welded_section_dialog(qapp):
    """Kaynaklı kesit bileşen düzenleyicisinin (WeldedSectionDialog) davranışını test eder."""
    from src.tables.elements_schedule.welded_dialog import WeldedSectionDialog

    # 1. 2-parçalı I-kiriş
    dlg = WeldedSectionDialog(SketchType.WELDED_I_BEAM, current_composition="-130 x 12, -106 x 12")
    assert len(dlg.part_edits) == 2
    assert "-130 x 12" in dlg.part_edits[0].text()
    assert "-106 x 12" in dlg.part_edits[1].text()
    dlg._update_preview()
    assert dlg.result_composition == "-130 x 12, -106 x 12"

    # Düzenleme testi
    dlg.part_edits[0].setText("-160 x 14")
    dlg._update_preview()
    assert dlg.result_composition == "-160 x 14, -106 x 12"
    dlg.close()

    # 2. 3-parçalı paket flanşlı kiriş
    dlg3 = WeldedSectionDialog(SketchType.WELDED_I_PACKAGE)
    assert len(dlg3.part_edits) == 3
    dlg3._update_preview()
    assert len(dlg3.result_composition.split(",")) == 3
    dlg3.close()


def test_elements_schedule_sketch_sync(qapp):
    """Eskiz değiştiğinde kesit kolonundaki ikon ve ön ekin geri dönmeden güncellendiğini test eder."""
    from src.tables.elements_schedule.editor import (
        ElementsScheduleWidget, clean_profile_prefix, sketch_type_to_profile_category
    )

    w = ElementsScheduleWidget()
    
    # 1. clean_profile_prefix kontrolleri
    assert clean_profile_prefix("I 20K1") == "20K1"
    assert clean_profile_prefix("[ 16P") == "16P"
    assert clean_profile_prefix("Гн. □ 100x100x4") == "100x100x4"
    assert clean_profile_prefix("L 50x5") == "50x5"
    assert clean_profile_prefix("Рифл. -4x1000") == "4x1000"

    # 2. sketch_type_to_profile_category kontrolleri
    assert sketch_type_to_profile_category(SketchType.I_BEAM) == "Двутавры"
    assert sketch_type_to_profile_category(SketchType.CHANNEL) == "Швеллеры"
    assert sketch_type_to_profile_category(SketchType.RECT_TUBE) == "Трубы профильные"
    assert sketch_type_to_profile_category(SketchType.ROUND_TUBE) == "Трубы круглые"
    assert sketch_type_to_profile_category(SketchType.ANGLE) == "Уголки"

    # 3. Satır 0'da eskiz tipini değiştirme (I_BEAM -> CHANNEL)
    cb = w.table_widget.cellWidget(0, 1)
    assert cb is not None
    
    # Eskiz combo'sunda CHANNEL ([) seçeneğini bul ve seç
    channel_idx = -1
    for i in range(cb.count()):
        stype, _ = cb.itemData(i)
        if stype == SketchType.CHANNEL:
            channel_idx = i
            break
    assert channel_idx != -1

    cb.setCurrentIndex(channel_idx)
    # Geri dönme döngüsü olmamalı! ComboBox CHANNEL olarak kalmalı
    curr_stype, _ = cb.currentData()
    assert curr_stype == SketchType.CHANNEL

    # Kesit hücresindeki metin '[' ön ekiyle başlamalı ve eski 'I' kalıntısı olmamalı
    comp_item = w.table_widget.item(0, 2)
    assert comp_item is not None
    assert comp_item.text().startswith("[")
    assert not comp_item.text().startswith("[ I")

    w.close()


def test_elements_schedule_in_cell_editor_action(qapp):
    """Kesit hücresi düzenleyicisinde (LinearComboBox) kütüphane aksiyon butonunun ve dropdown verilerinin bulunduğunu test eder."""
    from src.tables.elements_schedule.editor import ElementsScheduleWidget, ProfileCellDelegate
    from PySide6.QtWidgets import QStyleOptionViewItem, QComboBox

    w = ElementsScheduleWidget()
    delegate = ProfileCellDelegate(w, w.table_widget)
    index = w.table_widget.model().index(0, 2)
    editor = delegate.createEditor(w.table_widget, QStyleOptionViewItem(), index)

    assert isinstance(editor, QComboBox)
    assert editor.lineEdit() is not None
    actions = editor.lineEdit().actions()
    assert len(actions) >= 1  # Trailing action button (browse library)
    assert any("GOST Profil" in a.toolTip() for a in actions)

    # setEditorData testi: Satır 0 (I_BEAM) profilleri ve aksiyon maddeleri yüklenmeli
    delegate.setEditorData(editor, index)
    item_texts = [editor.itemText(i) for i in range(editor.count())]
    assert any("20Б1" in t or "20К1" in t for t in item_texts)
    assert any("GOST Profil Kütüphanesi" in t for t in item_texts)
    assert any("Yeni Özel Profil Ekle" in t for t in item_texts)

    w.close()


def test_elements_schedule_open_section_editor(monkeypatch, qapp):
    """_open_section_editor_for_row'un kaynaklı kesit için WeldedSectionDialog, haddelenmiş kesit için GostProfilePickerDialog açtığını test eder."""
    from src.tables.elements_schedule.editor import ElementsScheduleWidget
    from src.tables.elements_schedule.welded_dialog import WeldedSectionDialog
    from src.ui_v2.profile_picker_dialog import GostProfilePickerDialog
    from src.models.sketch import SketchType

    w = ElementsScheduleWidget()
    
    # 1. Kaynaklı satır testi
    cb0 = w.table_widget.cellWidget(0, 1)
    # Satır 0'ı WELDED_I_BEAM yap
    w._set_sketch_combo_type(cb0, SketchType.WELDED_I_BEAM)
    
    welded_called = []
    def mock_welded_exec(self):
        welded_called.append(self.sketch_type)
        self.result_composition = "-150 x 14, -120 x 10"
        return True
        
    monkeypatch.setattr(WeldedSectionDialog, "exec", mock_welded_exec)
    w._open_section_editor_for_row(0)
    
    assert len(welded_called) == 1
    assert welded_called[0] == SketchType.WELDED_I_BEAM
    assert w.table_widget.item(0, 2).text() == "-150 x 14, -120 x 10"
    
    # 2. Haddelenmiş satır testi (Швеллеры)
    w._set_sketch_combo_type(cb0, SketchType.CHANNEL)
    gost_called = []
    def mock_gost_exec(self):
        gost_called.append(self._current_category)
        return False  # İptal edildi
        
    monkeypatch.setattr(GostProfilePickerDialog, "exec", mock_gost_exec)
    w._open_section_editor_for_row(0)
    
    assert len(gost_called) == 1
    assert gost_called[0] == "Швеллеры"

    w.close()


def test_custom_profile_db_operations():
    """Özel profil ekleme, arama ve silme işlemlerini test eder."""
    from src.services.profile_database import GostProfileDatabase, ProfileRecord

    db = GostProfileDatabase.instance()
    custom_rec = ProfileRecord(
        designation="ÖZEL_100x50x4",
        category="Трубы профильные",
        standard="СТО АСЧМ 20-93",
        sketch_type="RECT_TUBE",
        dimensions="100x50x4",
        weight_kg_m=8.5,
        default_steel="С345"
    )

    # 1. Ekleme
    added = db.add_custom_profile(custom_rec)
    assert added is True

    # 2. Arama / Doğrulama
    found = db.lookup_by_designation("ÖZEL_100x50x4")
    assert found is not None
    assert found.designation == "ÖZEL_100x50x4"
    assert found.weight_kg_m == 8.5
    assert found.category == "Трубы профильные"

    # 3. Temizleme / Silme
    deleted = db.delete_custom_profile("ÖZEL_100x50x4")
    assert deleted is True
    assert db.lookup_by_designation("ÖZEL_100x50x4") is None


def test_add_custom_profile_dialog(qapp):
    """AddCustomProfileDialog penceresinin veri toplama ve kaydetme yeteneğini test eder."""
    from src.ui_v2.profile_picker_dialog import AddCustomProfileDialog
    from src.services.profile_database import GostProfileDatabase

    dlg = AddCustomProfileDialog(initial_category="Двутавры")
    dlg.edit_desig.setText("45Ш1_MOD")
    dlg.edit_dim.setText("440x200x9x14")
    dlg.edit_weight.setText("52.4")
    dlg.edit_std.setText("ГОСТ 26020-83")
    dlg.edit_steel.setText("С355")

    dlg._on_save()
    rec = dlg.created_profile
    assert rec is not None
    assert rec.designation == "45Ш1_MOD"
    assert rec.category == "Двутавры"
    assert rec.dimensions == "440x200x9x14"
    assert rec.weight_kg_m == 52.4
    assert rec.standard == "ГОСТ 26020-83"
    assert rec.default_steel == "С355"
    assert rec.sketch_type == "I_BEAM"

    # Temizle
    GostProfileDatabase.instance().delete_custom_profile("45Ш1_MOD")
    dlg.close()


def test_builder_ensures_profile_prefix():
    """create_elements_schedule_table fonksiyonunun CAD tablosunda 'Состав' kolonuna GOST ön eklerini (I, Гн. □) yerleştirdiğini test eder."""
    from src.tables.elements_schedule.builder import create_elements_schedule_table
    from src.tables.elements_schedule.model import build_sample_items

    items = build_sample_items()
    table = create_elements_schedule_table(items)
    assert table is not None

    # Tablo satırlarındaki metinleri kontrol et (Col 3: Состав)
    compositions = [row.cells[3].text for row in table.rows if not row.is_header]
    
    # I-kiriş için 'I ' ile başlamalı
    assert any("I " in c and "20" in c for c in compositions)
    # Kutu profil için 'Гн. □' ile başlamalı
    assert any("Гн. □" in c and "140" in c for c in compositions)


