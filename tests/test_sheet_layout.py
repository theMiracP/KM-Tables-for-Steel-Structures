"""
Sayfa Düzeni ve ГОСТ Yerleşim Testleri.
"""
import pytest
from src.config.sheet_config import (
    LayoutConfig,
    SheetSize,
    SheetOrientation,
    TablePlacement,
    DEFAULT_LAYOUT_CONFIG,
)
from src.config.table_config import DEFAULT_TABLE_CONFIG
from src.models.elements_schedule import build_sample_items, create_elements_schedule_table
from src.models.sheet import SheetLayoutCalculator

def test_standalone_table_placement():
    """Bağımsız tablo modunda sayfa çerçevesi olmadan orijin (0,0) dönmeli."""
    table = create_elements_schedule_table(build_sample_items(), DEFAULT_TABLE_CONFIG)
    cfg = LayoutConfig(placement=TablePlacement.STANDALONE)

    calc = SheetLayoutCalculator.calculate(table, cfg)
    assert calc.sheet_rect is None
    assert calc.inner_frame_rect is None
    assert calc.title_block_rect is None
    assert calc.table_origin.x == 0.0
    assert calc.table_origin.y == 0.0

def test_sheet_above_titleblock_placement():
    """A3 yatay sayfada tablonun antetin (185x55) hemen üstüne yerleşmesi."""
    table = create_elements_schedule_table(build_sample_items(), DEFAULT_TABLE_CONFIG)
    cfg = LayoutConfig(
        placement=TablePlacement.ABOVE_TITLEBLOCK,
        size=SheetSize.A3,
        orientation=SheetOrientation.LANDSCAPE
    )

    calc = SheetLayoutCalculator.calculate(table, cfg)
    assert calc.sheet_rect is not None
    assert calc.sheet_rect.width == 420.0
    assert calc.sheet_rect.height == 297.0

    # ГОСТ çerçevesi: Sol 20mm, Alt 5mm, Sağ 5mm, Üst 5mm
    assert calc.inner_frame_rect.x == 20.0
    assert calc.inner_frame_rect.y == 5.0
    assert calc.inner_frame_rect.width == 420.0 - 25.0  # 395.0
    assert calc.inner_frame_rect.height == 297.0 - 10.0 # 287.0

    # Antet Form 3 (185 x 55 mm): Sağ alt köşe
    assert calc.title_block_rect.width == 185.0
    assert calc.title_block_rect.height == 55.0
    assert calc.title_block_rect.x_max == calc.inner_frame_rect.x_max
    assert calc.title_block_rect.y_min == calc.inner_frame_rect.y_min

    # Tablo antetin üstüne yerleşmeli (y = 5.0 + 55.0 = 60.0)
    assert calc.table_origin.y == 60.0
    # Sağ kenarı çerçeveye hizalanmalı
    assert calc.table_origin.x + calc.table_width == calc.inner_frame_rect.x_max

def test_sheet_top_right_placement_with_headroom():
    """Sağ üst yerleşimde başlığın üst çerçeveye taşmaması için headroom bırakılmalı."""
    table = create_elements_schedule_table(build_sample_items(), DEFAULT_TABLE_CONFIG)
    cfg = LayoutConfig(
        placement=TablePlacement.TOP_RIGHT,
        size=SheetSize.A3,
        orientation=SheetOrientation.LANDSCAPE
    )

    headroom = 12.0
    calc = SheetLayoutCalculator.calculate(table, cfg, title_clearance=headroom)
    # Üst kenar = inner_frame.y_max
    # Tablo üst çizgisi = tbl_y + calc.table_height
    # Başlık için bırakılan boşluk: inner_frame.y_max - (tbl_y + calc.table_height) == headroom
    table_top = calc.table_origin.y + calc.table_height
    assert round(calc.inner_frame_rect.y_max - table_top, 2) == round(headroom, 2)

def test_sheet_center_placement():
    """Paftayı ortalama seçeneğinde tablo iç çerçevede hem X hem Y olarak ortalanmalı."""
    table = create_elements_schedule_table(build_sample_items(), DEFAULT_TABLE_CONFIG)
    cfg = LayoutConfig(
        placement=TablePlacement.CENTER_SHEET,
        size=SheetSize.A3,
        orientation=SheetOrientation.LANDSCAPE
    )

    calc = SheetLayoutCalculator.calculate(table, cfg)
    # Sol ve sağ boşluk eşit olmalı
    left_gap = calc.table_origin.x - calc.inner_frame_rect.x_min
    right_gap = calc.inner_frame_rect.x_max - (calc.table_origin.x + calc.table_width)
    assert round(left_gap, 2) == round(right_gap, 2)
