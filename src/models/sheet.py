"""
Sayfa Düzeni, Çerçeve, Antet ve Yerleşim Hesaplayıcı.
ГОСТ Р 21.101-2020 standartlarına uygun olarak paftayı ve tablo koordinatlarını konumlandırır.
"""
from dataclasses import dataclass
from typing import Tuple, Optional
from src.config.sheet_config import LayoutConfig, TablePlacement
from src.models.geometry import Rect2D, Point2D
from src.models.table import Table, TableLayoutInfo

@dataclass
class CalculatedLayout:
    """Sayfa, çerçeve, antet ve tablonun CAD koordinatları (mm)."""
    sheet_rect: Optional[Rect2D]       # Pafta dış sınırı
    inner_frame_rect: Optional[Rect2D] # ГОСТ iç çizim çerçevesi (sol 20, diğerleri 5mm)
    title_block_rect: Optional[Rect2D] # Form 3 ana antet (185x55 mm)
    table_origin: Point2D              # Tablonun sol alt yerleşim noktası
    table_width: float
    table_height: float

class SheetLayoutCalculator:
    @staticmethod
    def calculate(table: Table, layout_cfg: LayoutConfig, title_clearance: float = 12.0) -> CalculatedLayout:
        layout_info = table.compute_layout()
        t_w = layout_info.total_width
        t_h = layout_info.total_height

        # Eğer başlık yoksa başlık payını sıfırla
        headroom = title_clearance if table.title and table.title.strip() else 0.0

        if layout_cfg.placement == TablePlacement.STANDALONE:
            # Sadece tablo (orijin 0,0)
            return CalculatedLayout(
                sheet_rect=None,
                inner_frame_rect=None,
                title_block_rect=None,
                table_origin=Point2D(0.0, 0.0),
                table_width=t_w,
                table_height=t_h,
            )

        # Sayfa boyutlarını al
        sheet_w, sheet_h = layout_cfg.get_sheet_dimensions()
        sheet_rect = Rect2D(0.0, 0.0, sheet_w, sheet_h)

        # İç çizim çerçevesi (ГОСТ Р 21.101-2020 Приложение И)
        # Sol kenar 20 mm, alt/sağ/üst 5 mm
        m = layout_cfg.margins
        inner_x = m.left
        inner_y = m.bottom
        inner_w = sheet_w - (m.left + m.right)
        inner_h = sheet_h - (m.top + m.bottom)
        inner_frame = Rect2D(inner_x, inner_y, inner_w, inner_h)

        # Antet (Form 3: 185 x 55 mm) sağ alt köşede yer alır
        tb_w = layout_cfg.title_block.width
        tb_h = layout_cfg.title_block.height
        tb_x = inner_frame.x_max - tb_w
        tb_y = inner_frame.y_min
        title_block = Rect2D(tb_x, tb_y, tb_w, tb_h)

        # Tablo yerleşimi
        if layout_cfg.placement == TablePlacement.ABOVE_TITLEBLOCK:
            # Antetin hemen üstüne, sağa hizalı
            tbl_x = inner_frame.x_max - t_w
            tbl_y = title_block.y_max + layout_cfg.title_block.gap_above

        elif layout_cfg.placement == TablePlacement.TOP_RIGHT:
            # Sağ üst köşe: Başlığın üst çerçeveye taşmaması için 'headroom' kadar aşağı ötelenir
            tbl_x = inner_frame.x_max - t_w
            tbl_y = inner_frame.y_max - t_h - headroom

        elif layout_cfg.placement == TablePlacement.TOP_LEFT:
            # Sol üst köşe
            tbl_x = inner_frame.x_min
            tbl_y = inner_frame.y_max - t_h - headroom

        elif layout_cfg.placement == TablePlacement.CENTER_SHEET:
            # Paftayı ortala (iç çerçeve içinde yatay ve dikey merkezleme)
            total_block_h = t_h + headroom
            tbl_x = inner_frame.x_min + max(0.0, (inner_frame.width - t_w) / 2.0)
            tbl_y = inner_frame.y_min + max(0.0, (inner_frame.height - total_block_h) / 2.0)

        elif layout_cfg.placement == TablePlacement.CUSTOM:
            tbl_x = layout_cfg.custom_x
            tbl_y = layout_cfg.custom_y
        else:
            tbl_x = 0.0
            tbl_y = 0.0

        return CalculatedLayout(
            sheet_rect=sheet_rect,
            inner_frame_rect=inner_frame,
            title_block_rect=title_block,
            table_origin=Point2D(tbl_x, tbl_y),
            table_width=t_w,
            table_height=t_h,
        )
