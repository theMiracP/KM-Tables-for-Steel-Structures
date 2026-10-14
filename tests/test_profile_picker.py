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
    assert dlg.selected_profile is not None
    assert dlg.selected_profile.designation == "20Б1"
    dlg.close()
