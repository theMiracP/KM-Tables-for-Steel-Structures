"""
Test Suite: QtAwesome Vektörel İkon Entegrasyonu Testleri.
fa5s (Solid), fa5 / fa5r (Regular) ikonları ve renk standartlarını doğrular.
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from src.ui_v2 import icons


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_qtawesome_availability(qapp):
    """QtAwesome kütüphanesinin yüklü ve aktif olduğunu doğrula."""
    assert icons._QTAWESOME_AVAILABLE is True


def test_solid_icons_generation(qapp):
    """Butonlar ve araç çubuğu için fa5s solid ikonlarının üretimi."""
    ico_sync = icons.get_icon(icons.ICON_SYNC, color=icons.COLOR_WHITE)
    assert isinstance(ico_sync, QIcon)
    assert not ico_sync.isNull()

    ico_close = icons.get_icon(icons.ICON_CLOSE, color=icons.COLOR_WHITE)
    assert not ico_close.isNull()

    ico_plus = icons.get_icon(icons.ICON_PLUS, color=icons.COLOR_SUCCESS)
    assert not ico_plus.isNull()

    ico_trash = icons.get_icon(icons.ICON_TRASH, color=icons.COLOR_DANGER)
    assert not ico_trash.isNull()


def test_regular_icons_generation(qapp):
    """Hafif arayüz öğeleri için fa5 / fa5r regular ikonlarının üretimi."""
    ico_doc = icons.get_icon(icons.ICON_DOC_REGULAR, color=icons.COLOR_NEUTRAL)
    assert isinstance(ico_doc, QIcon)
    assert not ico_doc.isNull()

    # fa5r alias desteği
    ico_alias = icons.get_icon("fa5r.file-alt", color=icons.COLOR_NEUTRAL)
    assert not ico_alias.isNull()

    ico_bookmark = icons.get_icon(icons.ICON_BOOKMARK_REGULAR, color=icons.COLOR_ACCENT_BLUE)
    assert not ico_bookmark.isNull()

    ico_clipboard = icons.get_icon(icons.ICON_CLIPBOARD_REGULAR, color=icons.COLOR_MUTED)
    assert not ico_clipboard.isNull()


def test_icon_size_and_colors():
    """Standart boyut (18-22 px) ve renk tanımları."""
    sz18 = icons.icon_size(18)
    assert sz18.width() == 18
    assert sz18.height() == 18

    assert icons.COLOR_NEUTRAL == "#9ca3af"
    assert icons.COLOR_ACCENT_BLUE == "#3b82f6"
