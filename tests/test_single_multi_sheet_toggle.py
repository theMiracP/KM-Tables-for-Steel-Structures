"""
Çoklu Pafta ve Tekli Pafta Geçişi (Toggle Single / Multi-Sheet) Test Süiti.
HUD Butonu, Rozet, Görünüm ve Dışa Aktarma Eşzamanlaması Testleri.
"""
import pytest
from PySide6.QtCore import Qt

from src.ui_v2 import KmLinearMainWindow
from src.ui_v2.cad_panel import FloatingHudToolbar, CadViewportPanel
from src.ui.i18n import i18n


def test_floating_hud_multi_sheet_toggle(qapp):
    """FloatingHudToolbar butonunun çoklu/tekli pafta modlarına göre metin ve stil değişimini doğrula."""
    i18n.set_language("TR")
    hud = FloatingHudToolbar()

    # Varsayılan: Tekli modda, buton "Çoklu Pafta" olmalı
    assert "Çoklu Pafta" in hud.btn_multi_sheet.text()
    assert hud.btn_multi_sheet.property("active") in ("false", None)

    # Çoklu pafta moduna geçir
    hud.set_multi_sheet_mode(True)
    assert "Tekli Pafta" in hud.btn_multi_sheet.text()
    assert hud.btn_multi_sheet.property("active") == "true"
    assert "Geri Dön" in hud.btn_multi_sheet.toolTip()

    # Tekli pafta moduna geri al
    hud.set_multi_sheet_mode(False)
    assert "Çoklu Pafta" in hud.btn_multi_sheet.text()
    assert hud.btn_multi_sheet.property("active") == "false"

    hud.close()


def test_cad_viewport_panel_badge_and_hud_sync(qapp):
    """CadViewportPanel'in çoklu pafta modunda rozeti ve HUD butonunu senkronize ettiğini doğrula."""
    i18n.set_language("TR")
    panel = CadViewportPanel()

    # Varsayılan
    assert "CANLI CAD" in panel.badge_title.text()
    assert "Çoklu Pafta" in panel.hud.btn_multi_sheet.text()

    # 3 paftalık çoklu moda geç
    panel.set_multi_sheet_mode(True, sheet_count=3)
    assert "ÇOKLU PAFTA" in panel.badge_title.text()
    assert "3 Pafta" in panel.badge_title.text()
    assert "Tekli Pafta" in panel.hud.btn_multi_sheet.text()

    # Tekli moda geri dön
    panel.set_multi_sheet_mode(False)
    assert "CANLI CAD" in panel.badge_title.text()
    assert "Çoklu Pafta" in panel.hud.btn_multi_sheet.text()

    panel.close()


def test_main_window_toggle_single_and_multi_sheet(qapp):
    """Ana pencerede HUD butonuna tıklayarak çoklu paftadan tekli paftaya geçişi doğrula."""
    i18n.set_language("TR")
    window = KmLinearMainWindow()

    # Başlangıç: Tekli pafta görünümü
    assert window._current_multi_sheet_layout is None
    assert "Çoklu Pafta" in window.cad_panel.hud.btn_multi_sheet.text()

    # 1. Butona Tıkla -> Çoklu Paftaya Geç
    window.cad_panel.hud.btn_multi_sheet.click()

    assert window._current_multi_sheet_layout is not None
    assert window._current_multi_sheet_layout.total_sheets >= 1
    assert "Tekli Pafta" in window.cad_panel.hud.btn_multi_sheet.text()
    assert "ÇOKLU PAFTA" in window.cad_panel.badge_title.text()

    # 2. Butona Tekrar Tıkla -> Tekli Paftaya Geri Dön
    window.cad_panel.hud.btn_multi_sheet.click()

    assert window._current_multi_sheet_layout is None
    assert "Çoklu Pafta" in window.cad_panel.hud.btn_multi_sheet.text()
    assert "CANLI CAD" in window.cad_panel.badge_title.text()

    window.close()


def test_multi_sheet_toggle_i18n(qapp):
    """Çoklu/Tekli pafta buton metinlerinin TR, EN, RU dillerinde doğru çevrildiğini doğrula."""
    hud = FloatingHudToolbar()

    # TR
    i18n.set_language("TR")
    hud.set_multi_sheet_mode(False)
    assert "Çoklu Pafta" in hud.btn_multi_sheet.text()
    hud.set_multi_sheet_mode(True)
    assert "Tekli Pafta" in hud.btn_multi_sheet.text()

    # EN
    i18n.set_language("EN")
    hud.set_multi_sheet_mode(False)
    assert "Multi Sheet" in hud.btn_multi_sheet.text()
    hud.set_multi_sheet_mode(True)
    assert "Single Sheet" in hud.btn_multi_sheet.text()

    # RU
    i18n.set_language("RU")
    hud.set_multi_sheet_mode(False)
    assert "Многолистовой" in hud.btn_multi_sheet.text()
    hud.set_multi_sheet_mode(True)
    assert "Один лист" in hud.btn_multi_sheet.text()

    i18n.set_language("TR")
    hud.close()
