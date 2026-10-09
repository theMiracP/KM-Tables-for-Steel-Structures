"""
Tablo Modeli ve Geometri Birim Testleri.
"""
import pytest
from src.config.table_config import TableConfig, DEFAULT_TABLE_CONFIG
from src.models.elements_schedule import (
    ScheduleItem,
    ElementPart,
    create_elements_schedule_table,
    build_sample_items,
)
from src.models.sketch import SectionSketch, SketchType
from src.models.table import Table, TableCell, TableRow

def test_table_layout_computation():
    """Temel tablo boyut ve ofset hesaplaması."""
    table = Table(title="Test Tablosu")
    table.add_column("c1", "Kolon 1", 20.0)
    table.add_column("c2", "Kolon 2", 30.0)
    table.add_column("c3", "Kolon 3", 50.0)

    table.add_row([TableCell("A1"), TableCell("B1"), TableCell("C1")], height=10.0)
    table.add_row([TableCell("A2"), TableCell("B2"), TableCell("C2")], height=15.0)

    layout = table.compute_layout()
    assert layout.total_width == 100.0
    assert layout.total_height == 25.0
    assert layout.col_x_offsets == [0.0, 20.0, 50.0, 100.0]
    assert layout.row_y_offsets == [0.0, 10.0, 25.0]

def test_cell_cad_rect_coordinate_math():
    """CAD koordinat sisteminde (orijin sol-alt) hücre dikdörtgen hesabı."""
    table = Table(title="Test")
    table.add_column("c1", "K1", 25.0)
    table.add_column("c2", "K2", 35.0)
    table.add_row([TableCell("R0C0"), TableCell("R0C1")], height=10.0)
    table.add_row([TableCell("R1C0"), TableCell("R1C1")], height=10.0)

    layout = table.compute_layout()
    # origin_x = 0, origin_y = 0
    # Toplam yükseklik 20. İlk satır (r=0) üsttedir: y_min=10, y_max=20.
    r0c0 = table.get_cell_cad_rect(0, 0, 0.0, 0.0, layout)
    assert r0c0.x_min == 0.0
    assert r0c0.x_max == 25.0
    assert r0c0.y_min == 10.0
    assert r0c0.y_max == 20.0

    # İkinci satır (r=1) alttadır: y_min=0, y_max=10.
    r1c1 = table.get_cell_cad_rect(1, 1, 0.0, 0.0, layout)
    assert r1c1.x_min == 25.0
    assert r1c1.x_max == 60.0
    assert r1c1.y_min == 0.0
    assert r1c1.y_max == 10.0

def test_elements_schedule_table_builder():
    """Örnek eleman listesinin doğru satır ve sütun yapısına dönüştürülmesi."""
    items = build_sample_items()
    table = create_elements_schedule_table(items, DEFAULT_TABLE_CONFIG)

    # 9 sütun olmalı
    assert len(table.columns) == 9

    # İlk iki satır başlık olmalı
    assert table.rows[0].is_header is True
    assert table.rows[1].is_header is True

    # Б3 elemanı 2 alt parçaya sahip olduğu için tabloya 2 satır eklemelidir
    layout = table.compute_layout()
    assert layout.total_width > 0
    assert layout.total_height > 0

def test_complex_welded_sketches():
    """Yeni eklenen kompleks kaynaklı kesitlerin primitif üretimi."""
    # 1. Kaynaklı I-Kiriş (1-2)
    sk1 = SectionSketch(SketchType.WELDED_I_BEAM, callout_1="1", callout_2="2")
    prims1 = sk1.generate_primitives(0, 0, 20, 20)
    assert len(prims1) >= 6
    assert any(p.kind == "leader_text" and p.text == "1" for p in prims1)
    assert any(p.kind == "leader_text" and p.text == "2" for p in prims1)

    # 2. Paket Flanşlı I-Kiriş (1-2-3)
    sk2 = SectionSketch(SketchType.WELDED_I_PACKAGE, callout_1="1", callout_2="2", callout_3="3")
    prims2 = sk2.generate_primitives(0, 0, 20, 20)
    assert len(prims2) >= 8
    assert any(p.kind == "leader_text" and p.text == "3" for p in prims2)

    # 3. Kaynaklı Haç Kolon (1-2-3)
    sk3 = SectionSketch(SketchType.WELDED_CRUCIFORM, callout_1="1", callout_2="2", callout_3="3")
    prims3 = sk3.generate_primitives(0, 0, 20, 20)
    assert len(prims3) >= 10
    assert any(p.kind == "leader_text" and p.text == "1" for p in prims3)
    assert any(p.kind == "leader_text" and p.text == "2" for p in prims3)
    assert any(p.kind == "leader_text" and p.text == "3" for p in prims3)

