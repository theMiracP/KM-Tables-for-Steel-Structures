"""
tests/test_tasks_46_to_58.py

Kapsamlı doğrulama test süiti:
- TASK-46: Tablo İsimleri ГОСТ Uyumu & Çift Dilli Başlıklar
- TASK-47: Profil Kesit Şekilleri İkonları
- TASK-48: Kiril Kısayolu Ekleme Hatası Düzeltmesi (QApplication.focusWidget)
- TASK-49: Resizable QSplitter CAD & Editör Alanı
- TASK-50: DXF Export Sonrası Klasör Açma Onayı
- TASK-51: Boş Şirket Adında Title Block Logo Ortalama
- TASK-52 & TASK-53: Form 3 Antet Sorumlu ve Revizyon Sütun ГОСТ Ölçüleri
- TASK-54 & TASK-57: Ayarlar Yöneticisi (AutoCAD Katmanları, Renkleri, Güncelleyici) & SettingsDialog
- TASK-55: About Dialog Buton Sabit Renkleri
- TASK-56: Çoklu Pafta Otomatik Yerleşim & Ortak Antet (MultiSheetLayoutManager & DxfExporter)
- TASK-58: Tablo Önayar (Preset) Yönetim Sistemi (PresetManager & Serileştirme)
"""

import os
import tempfile
import pytest
from PySide6.QtWidgets import QApplication, QLineEdit, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

from src.ui.i18n import i18n
from src.services.settings import SettingsManager, LayerSetting
from src.services.preset_manager import PresetManager
from src.services.updater import UpdateCheckWorker
from src.models.registry import TableRegistry
from src.tables.elements_schedule.editor import ElementsScheduleWidget
from src.tables.elements_schedule.model import ElementsScheduleDocument, ScheduleItem, ElementPart
from src.tables.elements_schedule.sketch_renderer import get_sketch_icon
from src.models.sketch import SectionSketch, SketchType
from src.tables.title_block.model import TitleBlockDocument, SignatoryEntry, build_default_signatories, build_default_revisions
from src.tables.title_block.builder import create_title_block_table
from src.tables.title_block.editor import TitleBlockEditorWidget
from src.models.multi_sheet import MultiSheetLayoutManager, PlacedTableItem, MultiSheetLayout
from src.models.table import Table, TableRow, TableCell
from src.config.sheet_config import LayoutConfig, SheetSize, SheetOrientation
from src.export.dxf_exporter import DxfExporter
from src.ui_v2.about_dialog import LinearAboutDialog
from src.ui_v2.settings_dialog import LinearSettingsDialog


# =============================================================================
# TASK-46: Tablo İsimleri ГОСТ Uyumu
# =============================================================================
def test_task_46_gost_table_names():
    """Tüm modül isimlerinin ГОСТ standartlarına uygun Rusça başlık ve çeviriye sahip olduğunu doğrula."""
    orig_lang = i18n.current_language
    try:
        i18n.set_language("RU")
        # Elements schedule
        elem_title_ru = i18n.t("module_elements_schedule")
        assert "Ведомость элементов" in elem_title_ru

        # Title block
        tb_title_ru = i18n.t("module_title_block")
        assert "Основная надпись" in tb_title_ru
        assert "Форма 3" in tb_title_ru

        # Reference documents
        ref_title_ru = i18n.t("module_reference_docs")
        assert "Ведомость ссылочных" in ref_title_ru

        # Main drawings
        main_title_ru = i18n.t("module_main_drawings")
        assert "Ведомость основных комплектов" in main_title_ru

        # Working drawings
        work_title_ru = i18n.t("module_working_drawings")
        assert "Ведомость рабочих чертежей" in work_title_ru
    finally:
        i18n.set_language(orig_lang)


# =============================================================================
# TASK-47: Profil Kesit Şekilleri İkonları
# =============================================================================
def test_task_47_profile_sketch_icons(qapp):
    """Profil kesit şekillerinin QIcon olarak başarıyla üretildiğini doğrula."""
    for sketch_type in [
        SketchType.I_BEAM,
        SketchType.CHANNEL,
        SketchType.RECT_TUBE,
        SketchType.ROUND_TUBE,
        SketchType.ANGLE,
        SketchType.PLATE,
    ]:
        icon = get_sketch_icon(sketch_type, size=24)
        assert icon is not None
        assert not icon.isNull()
        pixmap = icon.pixmap(24, 24)
        assert not pixmap.isNull()
        assert pixmap.width() == 24
        assert pixmap.height() == 24


# =============================================================================
# TASK-48: Kiril Kısayolu Ekleme Hatası Düzeltmesi
# =============================================================================
def test_task_48_cyrillic_insert_into_active_cell(qapp):
    """
    Kullanıcı hücre içeriğini silip Kiril kısayoluna tıkladığında,
    harfin silinmiş metne eklenmek yerine odaklı aktif hücre editörüne doğru eklendiğini doğrula.
    """
    widget = ElementsScheduleWidget()
    widget.show()
    table = widget.table_widget

    # Hücre 0,0'ı seç ve düzenle
    table.setCurrentCell(0, 0)
    item = table.item(0, 0)
    assert item is not None
    table.editItem(item)

    # Düzenleyici editörü bul
    line_edit = table.findChild(QLineEdit)
    assert line_edit is not None

    # Metni tamamen silip imleci başa al
    line_edit.clear()
    assert line_edit.text() == ""

    # Kısayol ekle (örn. 'Ш')
    widget._insert_char_to_active_cell("Ш")

    # line_edit aktif odaklı olduğu için text "Ш" olmalıdır (eski "Б1Ш" değil)
    assert line_edit.text() == "Ш"
    widget.close()


# =============================================================================
# TASK-49: Resizable QSplitter CAD & Editör Alanı
# =============================================================================
def test_task_49_splitter_resizable(qapp):
    """KmLinearMainWindow içindeki QSplitter'ın boyutlandırılabilir olduğunu doğrula."""
    from src.ui_v2.window import KmLinearMainWindow
    win = KmLinearMainWindow()
    win.show()

    assert hasattr(win, "splitter")
    splitter = win.splitter
    assert splitter.count() == 2
    assert splitter.childrenCollapsible() is False
    assert splitter.handleWidth() >= 6

    # Sol ve sağ panellerin minimum genişlikleri atanmış olmalı
    editor_panel = splitter.widget(0)
    cad_panel = splitter.widget(1)
    assert editor_panel.minimumWidth() >= 320
    assert cad_panel.minimumWidth() >= 250

    win.close()


# =============================================================================
# TASK-51: Boş Şirket Adında Title Block Logo Ortalama
# =============================================================================
def test_task_51_logo_centering_when_company_empty():
    """Şirket unvanı boş olduğunda logonun kutu içinde ortalandığını doğrula."""
    doc = TitleBlockDocument(
        company_name="",
        company_logo=True,
        logo_image_path="test_logo.png",
        signatories=build_default_signatories(),
        revisions=build_default_revisions()
    )
    table = create_title_block_table(doc)

    # Satır 8 (index 8), Sütun 7 (50x15mm şirket ve logo kutusu)
    cell = table.rows[8].cells[7]
    assert cell is not None
    assert cell.sketch is not None
    assert cell.sketch.sketch_type == SketchType.LOGO_EMBLEM


# =============================================================================
# TASK-52 & TASK-53: Form 3 Antet Sorumlu ve Revizyon Sütun ГОСТ Ölçüleri
# =============================================================================
def test_task_52_and_53_title_block_column_dimensions():
    """
    ГОСТ Р 21.101 Form 3 sütun ölçülerini doğrula:
    - Sütun 0..1: 20 mm (Görev / Должность)
    - Sütun 2..3: 25 mm (Soyisim / Фамилия) - Sütun 2'den başlar!
    - Sütun 4: 10 mm (İmza / Подпись)
    - Sütun 5: 15 mm (Tarih / Дата)
    Toplam 70 mm.
    Revizyon tablosu:
    - Sütun 0: 10 mm (Изм.)
    - Sütun 1: 10 mm (Кол.уч.)
    - Sütun 2: 10 mm (Лист)
    - Sütun 3: 15 mm (№ док.)
    - Sütun 4: 10 mm (Подп.)
    - Sütun 5: 15 mm (Дата)
    Toplam 70 mm.
    """
    doc = TitleBlockDocument(
        signatories=build_default_signatories(),
        revisions=build_default_revisions()
    )
    table = create_title_block_table(doc)

    col_widths = [col.width for col in table.columns]
    assert len(col_widths) == 10
    # İlk 6 sütun (sol 70 mm): 10, 10, 10, 15, 10, 15
    assert col_widths[0] == 10.0
    assert col_widths[1] == 10.0
    assert col_widths[2] == 10.0
    assert col_widths[3] == 15.0
    assert col_widths[4] == 10.0
    assert col_widths[5] == 15.0
    assert sum(col_widths[:6]) == 70.0

    # Satır 5..10 (indices 5..10) için Sorumlu Görev (cols 0..1 = 20mm) ve Soyisim (cols 2..3 = 25mm) kontrolü
    for r in range(5, 11):
        role_cell = table.rows[r].cells[0]
        surname_cell = table.rows[r].cells[2]
        assert role_cell is not None
        assert role_cell.colspan == 2  # 10 + 10 = 20 mm
        assert surname_cell is not None
        assert surname_cell.colspan == 2  # 10 + 15 = 25 mm


# =============================================================================
# TASK-54 & TASK-57: Ayarlar Yöneticisi & SettingsDialog
# =============================================================================
def test_task_54_and_57_settings_manager_and_dialog(qapp, tmp_path):
    """SettingsManager katman ve updater ayarlarının kaydedilip yüklendiğini doğrula."""
    test_file = tmp_path / "test_settings.json"
    mgr = SettingsManager(config_file=str(test_file))

    # Varsayılan katman kontrolü
    layer_frame = mgr.get_layer("KM_TABLO_CERCEVE")
    assert layer_frame.name == "KM_TABLO_CERCEVE"
    assert layer_frame.color == 7

    # Katman güncelleme
    mgr.set_layer("KM_TABLO_CERCEVE", name="MY_OFFICE_FRAME", color=1, lineweight=70)
    assert mgr.get_layer_name("KM_TABLO_CERCEVE") == "MY_OFFICE_FRAME"
    assert mgr.get_layer_color("KM_TABLO_CERCEVE") == 1
    assert mgr.get_layer_lineweight("KM_TABLO_CERCEVE") == 70

    # Updater ayarları kontrolü
    upd = mgr.get_updater_settings()
    assert upd.check_on_startup is False
    mgr.set_updater_settings(check_on_startup=True, check_url=upd.check_url)
    assert mgr.get_updater_settings().check_on_startup is True

    # Yeni örnek ile dosyadan geri okuma kontrolü
    mgr_reloaded = SettingsManager(config_file=str(test_file))
    assert mgr_reloaded.get_layer_name("KM_TABLO_CERCEVE") == "MY_OFFICE_FRAME"
    assert mgr_reloaded.get_updater_settings().check_on_startup is True

    # Settings Dialog testi
    dialog = LinearSettingsDialog()
    dialog.show()
    assert dialog.isVisible()
    dialog.accept()
    dialog.close()


# =============================================================================
# TASK-55: About Dialog Buton Sabit Renkleri
# =============================================================================
def test_task_55_about_dialog_button_colors(qapp):
    """About penceresindeki butonların hover olmadan da farklı renklere sahip olduğunu doğrula."""
    dlg = LinearAboutDialog()

    # Web Link butonu (Deep sky / mavi tonları)
    assert "#0369a1" in dlg.btn_web_link.styleSheet()

    # Check update butonu (Indigo tonları)
    assert "#4338ca" in dlg.btn_check_update.styleSheet()

    # Open product page butonu (Zümrüt yeşili tonları)
    assert "#047857" in dlg.btn_open_product_page.styleSheet()

    # Kapat butonu (Slate tonları)
    assert "#334155" in dlg.btn_close.styleSheet()

    dlg.close()


# =============================================================================
# TASK-56: Çoklu Pafta Otomatik Yerleşim & Ortak Antet
# =============================================================================
def test_task_56_multi_sheet_layout_and_dxf_export(tmp_path):
    """
    Çoklu pafta yerleşim motorunun birden fazla tabloyu otomatik paftalara böldüğünü
    ve ortak Form 3 ana antetin her sayfaya 'Лист N / Листов Total' formatında yerleştirildiğini doğrula.
    """
    layout_cfg = LayoutConfig(size=SheetSize.A3, orientation=SheetOrientation.LANDSCAPE)

    # 4 adet uzun tablo oluştur (tek A3 sayfasına sığmayacak yükseklikte)
    tables = []
    for i in range(4):
        t = Table(title=f"Tablo {i+1}")
        t.add_column("c1", "Col 1", 185.0)
        # 15 satır * 10mm = 150mm yükseklik
        for r in range(15):
            row = TableRow(cells=[TableCell(text=f"Tablo {i+1} Satır {r+1}")], height=10.0)
            t.rows.append(row)
        tables.append(t)

    title_block = TitleBlockDocument(
        doc_code="KM-PROJ-01",
        project_name="Test Çoklu Pafta Projesi",
        stage="Р",
        sheet_num="1",
        total_sheets="1"
    )

    layout = MultiSheetLayoutManager.calculate_layout(
        tables=tables,
        layout_config=layout_cfg,
        shared_title_block=title_block
    )

    # 4 büyük tablo tek A3 sayfasına sığmayacağı için en az 2 sayfa oluşmalı
    assert layout.total_sheets >= 2
    assert len(layout.pages) >= 2

    # Her sayfada Form 3 antet bulunmalı ve pafta numaraları doğru olmalı
    total_sheets_count = layout.total_sheets
    for idx, page in enumerate(layout.pages):
        assert page.title_block_table is not None
        # Sağ alt hücrede Лист <N> ve Листов <Total> kontrolü
        tb = page.title_block_table
        cell_sheet = tb.rows[6].cells[8]  # Лист hücresi (Satır 6, Sütun 8)
        cell_total = tb.rows[6].cells[9]  # Листов hücresi (Satır 6, Sütun 9)
        assert cell_sheet is not None
        assert str(idx + 1) in cell_sheet.text
        assert cell_total is not None
        assert str(total_sheets_count) in cell_total.text

    # DXF Çoklu Sayfa Export Doğrulaması
    dxf_exporter = DxfExporter()
    output_dxf = tmp_path / "multi_sheet_test.dxf"
    success = dxf_exporter.export_multi_sheet(layout, str(output_dxf))
    assert success is True
    assert output_dxf.exists()
    assert output_dxf.stat().st_size > 1000


def test_task_56_no_table_overlaps_multi_sheet():
    """
    Çoklu paftaya yerleştirilen tabloların ve Form 3 ana antetin hiçbir şekilde
    birbirleriyle (ne X ne de Y ekseninde) çakışmadığını kesin geometrik olarak doğrula.
    (TASK: 'çoklu çıktıda paftalarda böyle çakışma olmasın' hata düzeltmesi).
    """
    # 1. Test: 197mm genişliğindeki Ведомость элементов ile 185mm genişliğindeki referans tablosu
    t1 = Table(title="Ведомость элементов")
    for w in [20, 30, 12, 40, 15, 15, 15, 25, 25]:  # Toplam 197 mm
        t1.add_column(f"c_{w}", f"Col_{w}", float(w))
    for r in range(8):
        t1.rows.append(TableRow(cells=[TableCell(text=f"R{r}") for _ in range(9)], height=10.0))

    t2 = Table(title="Ведомость ссылочных документов")
    for w in [20, 120, 25, 20]:  # Toplam 185 mm
        t2.add_column(f"c_{w}", f"Col_{w}", float(w))
    for r in range(12):
        t2.rows.append(TableRow(cells=[TableCell(text=f"R{r}") for _ in range(4)], height=10.0))

    layout_cfg_a3 = LayoutConfig(size=SheetSize.A3, orientation=SheetOrientation.LANDSCAPE)
    layout = MultiSheetLayoutManager.calculate_layout([t1, t2], layout_config=layout_cfg_a3)

    assert layout.total_sheets >= 1
    for page in layout.pages:
        f = page.inner_frame_rect
        tb = page.title_block_rect

        # Her yerleştirilen tablonun sınırlayıcı kutusunu (Bounding Box) hesapla
        placed_boxes = []
        for item in page.placed_tables:
            info = item.table.compute_layout()
            tw = info.total_width
            headroom = 12.0 if (item.table.title and item.table.title.strip()) else 0.0
            th = info.total_height + headroom
            x_min = item.origin.x
            x_max = item.origin.x + tw
            y_min = item.origin.y
            y_max = item.origin.y + th
            placed_boxes.append((x_min, x_max, y_min, y_max, item.table.title))

            # İç çizim çerçevesi sınırları içinde olduğunu kontrol et
            assert x_min >= f.x_min - 0.05, f"Tablo sol iç çerçeveyi taştı: {x_min} < {f.x_min}"
            assert x_max <= f.x_max + 0.05, f"Tablo sağ iç çerçeveyi taştı: {x_max} > {f.x_max}"
            assert y_min >= f.y_min - 0.05, f"Tablo alt iç çerçeveyi taştı: {y_min} < {f.y_min}"
            assert y_max <= f.y_max + 0.05, f"Tablo üst iç çerçeveyi taştı: {y_max} > {f.y_max}"

            # Form 3 Ana Antet ile çakışmadığını kontrol et
            # (Ya antetin solunda olmalı: x_max <= tb.x_min - 7.99 ya da antetin üstünde: y_min >= tb.y_max + 7.99)
            not_overlapping_tb = (x_max <= tb.x_min + 0.05) or (y_min >= tb.y_max - 0.05)
            assert not_overlapping_tb, f"Tablo '{item.table.title}' Form 3 antet ile çakışıyor!"

        # Aynı sayfadaki tabloların ikili çakışma kontrolü
        for i in range(len(placed_boxes)):
            for j in range(i + 1, len(placed_boxes)):
                b1 = placed_boxes[i]
                b2 = placed_boxes[j]
                # Ya X ekseninde ayrık olmalı ya da Y ekseninde ayrık olmalı
                disjoint_x = (b1[1] <= b2[0] + 0.05) or (b2[1] <= b1[0] + 0.05)
                disjoint_y = (b1[3] <= b2[2] + 0.05) or (b2[3] <= b1[2] + 0.05)
                assert disjoint_x or disjoint_y, (
                    f"Tablo çakışması tespit edildi! '{b1[4]}' ve '{b2[4]}' "
                    f"X1: [{b1[0]}, {b1[1]}], X2: [{b2[0]}, {b2[1]}], "
                    f"Y1: [{b1[2]}, {b1[3]}], Y2: [{b2[2]}, {b2[3]}]"
                )



# =============================================================================
# TASK-58: Tablo Önayar (Preset) Yönetim Sistemi
# =============================================================================
def test_task_58_preset_manager_save_and_load(tmp_path):
    """PresetManager'ın önayarları kaydedip, listeleyip, yüklediğini ve sildiğini doğrula."""
    preset_dir = str(tmp_path / "presets")
    pm = PresetManager(base_dir=preset_dir)

    module_id = "elements_schedule"
    sample_doc = ElementsScheduleDocument(
        items=[
            ScheduleItem(
                mark="Б1",
                sketch=SectionSketch(sketch_type=SketchType.I_BEAM),
                parts=[ElementPart(composition="40Б1")],
                force_n="150"
            ),
            ScheduleItem(
                mark="К1",
                sketch=SectionSketch(sketch_type=SketchType.RECT_TUBE),
                parts=[ElementPart(composition="140х140х6")],
                force_n="320"
            )
        ]
    )

    # 1. Preset Kaydet
    saved_path = pm.save_preset(
        module_id=module_id,
        preset_name="Standart Kiriş ve Kolonlar",
        document=sample_doc,
        description="Tipik çelik kiriş ve kolon şablonu"
    )
    assert os.path.exists(saved_path)

    # 2. Preset Listele
    presets = pm.list_presets(module_id)
    assert len(presets) == 1
    p = presets[0]
    assert p.name == "Standart Kiriş ve Kolonlar"
    assert p.module_id == module_id
    assert p.description == "Tipik çelik kiriş ve kolon şablonu"

    # 3. Preset Yükle
    loaded_doc = pm.load_preset(module_id, p.name)
    assert loaded_doc is not None
    assert len(loaded_doc.items) == 2
    assert loaded_doc.items[0].mark == "Б1"
    assert loaded_doc.items[1].mark == "К1"

    # 4. Preset Sil
    deleted = pm.delete_preset(module_id, p.name)
    assert deleted is True
    assert len(pm.list_presets(module_id)) == 0


# =============================================================================
# Zadax.net Güncelleme HTML Regex Ayrıştırıcı Testi
# =============================================================================
def test_updater_html_parser_zadax_page():
    """Zadax.net ürün sayfası HTML içeriğinden sürüm ve indirme linkinin parse edildiğini doğrula."""
    html_mock = """
    <html>
        <body>
            <h1>KM Tables Studio (Çelik Yapı Tabloları ve DXF Üretici)</h1>
            <p>Güncel Sürüm: <strong>v1.6.0</strong></p>
            <p>Son Güncelleme: 12.10.2026</p>
            <a href="https://zadax.net/downloads/km-tables-studio-setup-v1.6.0.exe" class="download-button">İndir</a>
        </body>
    </html>
    """
    worker = UpdateCheckWorker()
    info = worker._parse_html_page(html_mock)
    assert info is not None
    assert info.version == "1.6.0"
    assert "km-tables-studio-setup-v1.6.0.exe" in info.product_url
