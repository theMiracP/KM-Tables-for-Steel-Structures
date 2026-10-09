"""
Linear / Notion SaaS Tasarımı (UI v2) Testleri.
Pencere açılışı, modül geçişleri, CAD tuval güncellemesi ve kısayol davranışlarını doğrular.
"""
import pytest
from PySide6.QtWidgets import QApplication
from src.ui_v2 import KmLinearMainWindow
from src.models.registry import TableRegistry
from src.config.sheet_config import SheetSize


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_ui_v2_initialization(qapp):
    """Linear/Notion arayüzünün hatasız başlatıldığını doğrula."""
    window = KmLinearMainWindow()
    assert window is not None
    assert window.top_bar is not None
    assert window.sidebar is not None
    assert window.cad_panel is not None
    assert window.status_bar is not None
    assert window.active_module is not None
    assert window.current_table is not None
    window.close()


def test_ui_v2_module_switching(qapp):
    """Yan panelden modül değişiminin sorunsuz çalıştığını doğrula."""
    window = KmLinearMainWindow()
    all_mods = TableRegistry.all()

    if len(all_mods) > 1:
        target_mod = all_mods[1]
        window._switch_to_module(target_mod.id)
        assert window.active_module.id == target_mod.id
        from src.ui.i18n import get_module_display_title
        assert get_module_display_title(target_mod.id) in window.top_bar.lbl_active_table.text()

    window.close()


def test_ui_v2_sidebar_toggle(qapp):
    """Kenar çubuğunun (Ctrl+B / Toggle) görünürlük kontrolünü doğrula."""
    window = KmLinearMainWindow()
    initial_hidden = window.sidebar.isHidden()
    window._toggle_sidebar()
    assert window.sidebar.isHidden() != initial_hidden
    window._toggle_sidebar()
    assert window.sidebar.isHidden() == initial_hidden
    window.close()


def test_ui_v2_layout_config_change(qapp):
    """Pafta ayarları değiştiğinde CAD tuvalinin güncellendiğini doğrula."""
    window = KmLinearMainWindow()
    window.sidebar.cmb_size.setCurrentText("A1")
    assert window.layout_config.size == SheetSize.A1
    window.close()


def test_ui_v2_hud_actions(qapp):
    """Floating HUD kontrollerinin çalıştığını doğrula."""
    window = KmLinearMainWindow()
    hud = window.cad_panel.hud
    assert hud is not None
    hud.btn_zoom_in.click()
    hud.btn_zoom_out.click()
    hud.btn_fit.click()
    hud.btn_zoom_actual.click()
    hud.set_coords(125.5, -45.0)
    assert "125.5" in hud.lbl_coords.text()
    window.close()


def test_main_entry_uses_ui_v2():
    """main.py dosyasının birincil arayüz olarak KmLinearMainWindow (v2) kullandığını doğrula."""
    import inspect
    import main as main_module
    source = inspect.getsource(main_module)
    assert "from src.ui_v2 import KmLinearMainWindow" in source
    assert "KmLinearMainWindow()" in source
    assert "from src.ui.app import KmMainWindow" not in source


def test_linear_shimmer_button_properties_and_direction(qapp):
    """LinearShimmerButton'ın sağdan sola jilet parıltısı mantığını ve çizimini doğrula."""
    from src.ui_v2.components import LinearShimmerButton
    from PySide6.QtGui import QPixmap, QPainter
    from PySide6.QtCore import QEvent

    btn = LinearShimmerButton("DXF Dışa Aktar")
    btn.resize(130, 30)

    # 1. Başlangıç ve yönelim değerleri (Sağdan sola: 1.4 -> -0.4)
    assert btn._anim.startValue() == 1.4
    assert btn._anim.endValue() == -0.4
    assert btn._anim.startValue() > btn._anim.endValue(), "Animasyon sağdan sola (büyük X'ten küçük X'e) olmalı!"
    assert btn._shimmer_angle == 22.0, "Jilet kesim açısı 22 derece olmalı"

    # 2. Manuel pozisyonlama ve özellikler
    btn.shimmer_position = 0.5
    assert btn.shimmer_position == 0.5

    # 3. Boyama testi (paintEvent) - animasyon yokken ve varken
    pix = QPixmap(130, 30)
    btn.render(pix)  # Animasyon kapalıyken normal çizim

    btn._is_animating = True
    btn.shimmer_position = 0.5
    btn.render(pix)  # Animasyon aktifken jilet ışıltısı çizimi

    # 4. Tetikleme ve durdurma
    btn.show()
    btn.start_shimmer(immediate=True)
    assert btn.is_shimmering is True
    btn.stop_shimmer()
    assert btn.is_shimmering is False

    # 5. Hover simülasyonu
    from PySide6.QtGui import QEnterEvent
    from PySide6.QtCore import QPointF
    enter_ev = QEnterEvent(QPointF(10, 10), QPointF(10, 10), QPointF(10, 10))
    btn.enterEvent(enter_ev)
    assert btn.is_shimmering is True
    btn.stop_shimmer()
    btn.close()


def test_top_bar_uses_shimmer_button(qapp):
    """LinearTopBar'ın dışa aktar butonunun LinearShimmerButton olduğunu doğrula."""
    from src.ui_v2.top_bar import LinearTopBar
    from src.ui_v2.components import LinearShimmerButton

    top_bar = LinearTopBar()
    assert isinstance(top_bar.btn_export, LinearShimmerButton)
    assert top_bar.btn_export.objectName() == "primaryButton"
    assert not top_bar.btn_export.icon().isNull()

    # Tıklama sinyali testi
    called = []
    top_bar.export_dxf_requested.connect(lambda: called.append(True))
    top_bar.btn_export.click()
    assert len(called) == 1
    top_bar.close()


def test_ui_v2_cad_panel_toggle_and_default_state(qapp):
    """CAD ekranının varsayılan olarak açık olduğunu ve açılıp kapatılabildiğini doğrula."""
    from src.ui_v2 import KmLinearMainWindow

    window = KmLinearMainWindow()

    # 1. Varsayılan olarak açık olmalı (default açık)
    assert window.cad_panel.isHidden() is False, "CAD ekranı varsayılan olarak açık olmalı!"
    assert "CAD Ekranı" in window.top_bar.btn_toggle_cad.text()

    # 2. TopBar butonuyla kapatma
    window.top_bar.btn_toggle_cad.click()
    assert window.cad_panel.isHidden() is True, "CAD ekranı kapanmalı!"
    assert "Göster" in window.top_bar.btn_toggle_cad.toolTip()

    # 3. TopBar butonuyla tekrar açma
    window.top_bar.btn_toggle_cad.click()
    assert window.cad_panel.isHidden() is False, "CAD ekranı tekrar açılmalı!"
    assert "Gizle" in window.top_bar.btn_toggle_cad.toolTip()

    # 4. HUD üzerindeki kapat butonu ile kapatma
    window.cad_panel.hud.btn_close.click()
    assert window.cad_panel.isHidden() is True, "HUD kapat butonu ile CAD ekranı kapanmalı!"

    # 5. Kısayol metodu doğrudan çağrıldığında açılma
    window._toggle_cad_panel()
    assert window.cad_panel.isHidden() is False

    window.close()
