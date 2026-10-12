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


def test_editor_wrapper_language_switch_and_header_layout(qapp):
    """TableEditorWrapper başlıklarının dile göre dinamik değiştiğini ve modern kart yerleşimini doğrula."""
    import src.tables
    from src.ui_v2.editor_wrapper import TableEditorWrapper
    from src.ui.i18n import i18n
    from src.models.registry import TableRegistry

    wrapper = TableEditorWrapper()
    for mod in TableRegistry.all():
        wrapper.register_module(mod)

    # 1. Title Block göster
    wrapper.show_module("title_block")

    # Türkçe
    i18n.set_language("TR")
    assert "Başlık Bloğu" in wrapper.lbl_title.text() or "Form 3" in wrapper.lbl_title.text()
    assert "Form 3" in wrapper.lbl_subtitle.text()
    assert "Şablon Kaydet" in wrapper.btn_save_preset.text()

    # İngilizce
    i18n.set_language("EN")
    assert "Title Block" in wrapper.lbl_title.text()
    assert "Save Preset" in wrapper.btn_save_preset.text()

    # Rusça
    i18n.set_language("RU")
    assert "Основная надпись" in wrapper.lbl_title.text()
    assert "Сохранить шаблон" in wrapper.btn_save_preset.text()

    # 2. Elements Schedule göster (vedomost_elementov)
    wrapper.show_module("vedomost_elementov")
    i18n.set_language("TR")
    assert "Eleman Listesi" in wrapper.lbl_title.text()

    i18n.set_language("EN")
    assert "Elements Schedule" in wrapper.lbl_title.text()

    i18n.set_language("RU")
    assert "Ведомость элементов" in wrapper.lbl_title.text()

    # Sıfırla
    i18n.set_language("TR")
    wrapper.close()


def test_top_bar_language_flags_and_active_highlight(qapp):
    """LinearTopBar dil butonlarında SVG bayrak ikonlarının varlığını ve aktif buton vurgusunu doğrula."""
    from src.ui_v2.top_bar import LinearTopBar
    from src.ui.i18n import i18n

    top_bar = LinearTopBar()

    # 1. Bayrak ikonları doğrulaması
    for code in ["tr", "ru", "en"]:
        btn = top_bar.lang_btns[code]
        assert not btn.icon().isNull(), f"{code} dil butonunda SVG bayrak ikonu yüklü olmalı!"

    # 2. Dil tıklama ve aktif vurgu testi
    top_bar.lang_btns["en"].click()
    assert i18n.current_language == "EN"

    top_bar.lang_btns["tr"].click()
    assert i18n.current_language == "TR"

    top_bar.close()


def test_multi_sheet_excludes_inactive_and_title_block(qapp):
    """Çoklu paftada arayüzde olmayan (çelik sarfiyat) ve içerik tablosu olmayan (antet) tabloların elendiğini doğrula."""
    import src.tables
    from src.ui_v2 import KmLinearMainWindow

    window = KmLinearMainWindow()
    tables = window._get_all_project_tables()

    table_titles = [getattr(t, "title", "") for t in tables]
    for t in tables:
        # 1. Çelik sarfiyat tablosu olmamalı
        assert "расхода стали" not in t.title
        assert "Sarfiyat" not in t.title

        # 2. Antet tablosu içerik tablosu olarak olmamalı
        assert getattr(t, "id", "") != "title_block"
        assert t.total_width != 185.0 or len(t.columns) != 10

    # 3. Yalnızca geçerli aktif tablolar yer almalı
    assert len(tables) >= 1
    window.close()


def test_floating_hud_modernization_styling(qapp):
    """Floating HUD barının modern cam stiline ve temiz dikey çizgi ayırıcılara sahip olduğunu doğrula."""
    from src.ui_v2.cad_panel import FloatingHudToolbar
    from PySide6.QtWidgets import QFrame

    hud = FloatingHudToolbar()
    assert hud.objectName() == "floatingHudToolbar"
    assert hud.btn_multi_sheet.objectName() == "hudMultiSheet"
    assert hud.btn_close.objectName() == "hudClose"

    # Dikey çizgi ayırıcıların varlığı
    dividers = [child for child in hud.findChildren(QFrame) if child is not hud and child.width() == 1]
    assert len(dividers) >= 3, "HUD içinde en az 3 adet ince dikey çizgi ayırıcı olmalı!"

    # Koordinat etiketinin transparan ve çerçevesiz olması
    assert "border: none" in hud.lbl_coords.styleSheet()

    hud.close()
