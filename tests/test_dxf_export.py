"""
AutoCAD DXF Dışa Aktarma Testleri.
Gerçek DXF dosyası oluşturup ezdxf ile okuyarak katman, metin ve geometri bütünlüğünü doğrular.
"""
import os
import tempfile
import pytest
import ezdxf

from src.config.standards import ALL_LAYERS, LAYER_BORDER, LAYER_GRID, LAYER_TEXT
from src.config.table_config import DEFAULT_TABLE_CONFIG
from src.config.sheet_config import LayoutConfig, SheetSize, SheetOrientation, TablePlacement
from src.export.dxf_exporter import DxfExporter
from src.models.elements_schedule import build_sample_items, create_elements_schedule_table

def test_dxf_standalone_export():
    """Bağımsız DXF dosyasının başarıyla oluşturulup okunabilmesi."""
    items = build_sample_items()
    table = create_elements_schedule_table(items, DEFAULT_TABLE_CONFIG)
    exporter = DxfExporter()

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, "test_table.dxf")
        success = exporter.export(table, out_path, DEFAULT_TABLE_CONFIG)
        assert success is True
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0

        # ezdxf ile dosyayı geri oku ve incele
        doc = ezdxf.readfile(out_path)
        msp = doc.modelspace()

        # Katmanların tanımlı olduğunu kontrol et
        for layer_cfg in ALL_LAYERS:
            assert layer_cfg.name in doc.layers

        # Metin varlığını kontrol et
        texts = [e.dxf.text for e in msp.query("TEXT")]
        assert "Ведомость элементов" in texts
        assert any("Б1" in t for t in texts)
        assert any("С255-4" in t for t in texts)

def test_dxf_sheet_layout_export():
    """A3 sayfa düzeni ve Form 3 anteti ile DXF oluşturulması."""
    items = build_sample_items()
    table = create_elements_schedule_table(items, DEFAULT_TABLE_CONFIG)
    layout_cfg = LayoutConfig(
        placement=TablePlacement.ABOVE_TITLEBLOCK,
        size=SheetSize.A3,
        orientation=SheetOrientation.LANDSCAPE
    )
    exporter = DxfExporter()

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, "test_sheet.dxf")
        success = exporter.export(table, out_path, DEFAULT_TABLE_CONFIG, layout_cfg)
        assert success is True

        doc = ezdxf.readfile(out_path)
        msp = doc.modelspace()

        # Sayfa çerçeve çizgileri (LWPOLYLINE) bulunmalı
        polylines = list(msp.query("LWPOLYLINE"))
        assert len(polylines) >= 3  # Sayfa dış, çerçeve iç, tablo dış

        # Antet metinleri bulunmalı
        texts = [e.dxf.text for e in msp.query("TEXT")]
        assert "Изм." in texts
        assert "Стадия" in texts

def test_dxf_merged_headers_have_no_internal_vertical_lines():
    """'Сечение' ve 'Усилие для прикрепления' birleştirilmiş başlıklarının içinden dikey çizgi geçmemeli."""
    items = build_sample_items()
    table = create_elements_schedule_table(items, DEFAULT_TABLE_CONFIG)
    exporter = DxfExporter()

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, "test_clean_headers.dxf")
        exporter.export(table, out_path, DEFAULT_TABLE_CONFIG)

        doc = ezdxf.readfile(out_path)
        msp = doc.modelspace()
        layout = table.compute_layout()

        table_top = layout.total_height
        row0_bottom = table_top - layout.row_heights[0]

        # 0. satırı (üst başlık) kesen dikey çizgileri topla
        vert_lines_row0 = []
        for line in msp.query("LINE"):
            x1, y1 = line.dxf.start.x, line.dxf.start.y
            x2, y2 = line.dxf.end.x, line.dxf.end.y
            if abs(x1 - x2) < 0.001:  # dikey çizgi
                min_y = min(y1, y2)
                max_y = max(y1, y2)
                if max_y > row0_bottom + 0.01 and min_y < table_top - 0.01:
                    vert_lines_row0.append(round(x1, 2))

        col_x = [round(x, 2) for x in layout.col_x_offsets]
        # Сечение sütunları (col 1 ile col 4 arası): iç kısımda çizgi olmamalı
        inside_secheniye = [x for x in vert_lines_row0 if col_x[1] < x < col_x[4]]
        # Усилие sütunları (col 4 ile col 7 arası): iç kısımda çizgi olmamalı
        inside_usiliye = [x for x in vert_lines_row0 if col_x[4] < x < col_x[7]]

        assert len(inside_secheniye) == 0, f"Сечение içinde dikey çizgi bulundu: {inside_secheniye}"
        assert len(inside_usiliye) == 0, f"Усилие içinde dikey çizgi bulundu: {inside_usiliye}"


def test_dxf_cell_text_centering():
    """Hücre metinlerinin CAD hücresinde tam ortalı (center_x, center_y) yerleştiğini doğrular."""
    items = build_sample_items()
    table = create_elements_schedule_table(items, DEFAULT_TABLE_CONFIG)
    exporter = DxfExporter()

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, "test_centering.dxf")
        exporter.export(table, out_path, DEFAULT_TABLE_CONFIG)

        doc = ezdxf.readfile(out_path)
        msp = doc.modelspace()
        layout = table.compute_layout()

        # 1. Tek satırlı veri hücresi (Б1: Row 2, Col 0)
        rect_b1 = table.get_cell_cad_rect(2, 0, 0, 0, layout)
        b1_texts = [e for e in msp.query("TEXT") if e.dxf.text == "Б1"]
        assert len(b1_texts) == 1
        t_b1 = b1_texts[0]
        assert abs(t_b1.dxf.align_point[0] - rect_b1.center_x) < 0.001
        assert abs(t_b1.dxf.align_point[1] - rect_b1.center_y) < 0.001
        assert t_b1.dxf.halign == 1  # Center
        assert t_b1.dxf.valign == 2  # Middle

        # 2. Sola dayalı veri hücresi (I 20K1: Row 2, Col 3)
        rect_comp = table.get_cell_cad_rect(2, 3, 0, 0, layout)
        comp_texts = [e for e in msp.query("TEXT") if e.dxf.text == "I 20K1"]
        assert len(comp_texts) == 1
        t_comp = comp_texts[0]
        expected_x = rect_comp.x_min + DEFAULT_TABLE_CONFIG.cell_padding_x
        assert abs(t_comp.dxf.align_point[0] - expected_x) < 0.001
        assert abs(t_comp.dxf.align_point[1] - rect_comp.center_y) < 0.001
        assert t_comp.dxf.halign == 0  # Left
        assert t_comp.dxf.valign == 2  # Middle

        # 3. Birleştirilmiş tek satırlı başlık hücresi (Сечение: Row 0, Col 1)
        rect_sec = table.get_cell_cad_rect(0, 1, 0, 0, layout)
        sec_texts = [e for e in msp.query("TEXT") if e.dxf.text == "Сечение"]
        assert len(sec_texts) == 1
        t_sec = sec_texts[0]
        assert abs(t_sec.dxf.align_point[0] - rect_sec.center_x) < 0.001
        assert abs(t_sec.dxf.align_point[1] - rect_sec.center_y) < 0.001

        # 4. İki satırlı başlık hücresi (Марка \n элемента: Row 0, Col 0)
        rect_marka = table.get_cell_cad_rect(0, 0, 0, 0, layout)
        marka_lines = [e for e in msp.query("TEXT") if e.dxf.text in ("Марка", "элемента")]
        assert len(marka_lines) == 2
        # İki satırın düşey merkezlerinin ortalaması hücrenin center_y değerine eşit olmalı
        avg_y = sum(e.dxf.align_point[1] for e in marka_lines) / 2.0
        assert abs(avg_y - rect_marka.center_y) < 0.001
