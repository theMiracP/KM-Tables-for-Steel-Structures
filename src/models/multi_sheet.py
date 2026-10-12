"""
KM Layout Tables Studio - Otomatik Çoklu Pafta Yerleşim Sistemi (MultiSheetLayoutManager).
ГОСТ Р 21.101-2020 standartlarına uygun olarak tüm tabloları paftalara otomatik yerleştirir.
Seçilen sayfa boyutu yetmediğinde otomatik olarak yeni paftalar açar ve
tüm paftalarda ortak Form 3 ana antetini (Лист 1, 2... / Листов N) üretir.
"""
import copy
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

from src.models.geometry import Rect2D, Point2D
from src.models.table import Table
from src.config.sheet_config import LayoutConfig, DEFAULT_LAYOUT_CONFIG
from src.tables.title_block.model import TitleBlockDocument
from src.tables.title_block.builder import create_title_block_table


@dataclass
class PlacedTableItem:
    """Tek bir paftaya yerleştirilmiş tablo ve mutlak CAD koordinatları."""
    table: Table
    origin: Point2D
    sheet_index: int  # 1-indexed


@dataclass
class SheetPageLayout:
    """Tek bir paftanın (çizim sayfasının) tam geometrik yerleşimi."""
    sheet_index: int                   # 1, 2, 3...
    offset_x: float                    # AutoCAD Modelspace'te yan yana dizilim X ofseti
    sheet_rect: Rect2D                 # Kağıt dış sınırı
    inner_frame_rect: Rect2D           # ГОСТ iç çizim çerçevesi (sol 20mm, diğerleri 5mm)
    title_block_rect: Rect2D           # Form 3 antet konumu (185 x 55 mm)
    title_block_table: Table           # Bu sayfaya özel dinamik Лист/Листов değerli antet
    placed_tables: List[PlacedTableItem] = field(default_factory=list)


@dataclass
class MultiSheetLayout:
    """Tüm projenin çoklu pafta yerleşim sonucu."""
    total_sheets: int
    pages: List[SheetPageLayout] = field(default_factory=list)


class MultiSheetLayoutManager:
    """
    Tüm tabloları verilen pafta ebadı ve kurallarına göre sayfalara otomatik dağıtan motor.
    """
    SHEET_SPACING: float = 50.0  # Paftalar arası Modelspace boşluğu (50 mm)
    TABLE_GAP: float = 8.0       # Tablolar arası dikey/yatay boşluk (mm)

    @classmethod
    def calculate_layout(
        cls,
        tables: List[Table],
        layout_config: Optional[LayoutConfig] = None,
        shared_title_block: Optional[TitleBlockDocument] = None
    ) -> MultiSheetLayout:
        """
        Verilen tablo listesini sayfalara otomatik olarak yerleştirir.
        Gerektiğinde yeni paftalar açar.
        """
        cfg = layout_config or DEFAULT_LAYOUT_CONFIG
        sheet_w, sheet_h = cfg.get_sheet_dimensions()
        m = cfg.margins

        inner_w = sheet_w - (m.left + m.right)
        inner_h = sheet_h - (m.top + m.bottom)

        tb_w = cfg.title_block.width   # 185.0 mm
        tb_h = cfg.title_block.height  # 55.0 mm

        # Ortak antet verisi
        base_tb_doc = shared_title_block or cfg.title_block_doc or TitleBlockDocument()

        # Tabloları filtrele (boş olanları atla, varsa bağımsız anteti mükerrer ekleme)
        valid_tables: List[Table] = []
        for t in tables:
            if not t or len(t.rows) == 0:
                continue
            is_tb = (
                getattr(t, "id", "") == "title_block" or
                (len(t.columns) == 10 and abs(t.total_width - 185.0) < 0.1)
            )
            if not is_tb:
                valid_tables.append(t)

        if not valid_tables:
            # Tablo yoksa bile en az 1 boş pafta ve antet oluştur
            page1 = cls._create_page_skeleton(1, sheet_w, sheet_h, m, tb_w, tb_h, base_tb_doc, 1)
            return MultiSheetLayout(total_sheets=1, pages=[page1])

        # Sayfalara dağıtım algoritması (Dinamik Sütun Paketleme & Kesin Çakışma Önleme)
        class PageState:
            def __init__(self, sheet_index: int):
                self.sheet_index = sheet_index
                self.columns: List[Dict[str, Any]] = []
                self.tables: List[Tuple[Table, Point2D]] = []
                # İlk sütun: Sağ kenar, Form 3 Antet üstü
                self.open_new_column(is_first=True)

            def open_new_column(self, is_first: bool = False) -> Dict[str, Any]:
                if is_first:
                    x_right = inner_w
                    min_y = tb_h + cls.TABLE_GAP
                    max_w = tb_w  # Form 3 antet taban genişliği (185.0 mm)
                else:
                    prev_col = self.columns[-1]
                    x_right = prev_col["x_right"] - prev_col["max_width"] - cls.TABLE_GAP
                    min_y = cls.TABLE_GAP
                    max_w = 0.0

                col = {
                    "x_right": x_right,
                    "curr_top_y": inner_h - 5.0,
                    "min_bottom_y": min_y,
                    "max_width": max_w,
                    "table_count": 0,
                }
                self.columns.append(col)
                return col

            @property
            def active_column(self) -> Dict[str, Any]:
                return self.columns[-1]

        pages_raw: List[PageState] = []
        current_page_idx = 1
        curr_page = PageState(current_page_idx)

        for tbl in valid_tables:
            layout_info = tbl.compute_layout()
            t_w = layout_info.total_width
            headroom = 12.0 if (tbl.title and tbl.title.strip()) else 0.0
            total_block_h = layout_info.total_height + headroom

            placed = False

            # 1. Mevcut sayfadaki aktif sütuna sığıyor mu?
            act_col = curr_page.active_column
            avail_h = act_col["curr_top_y"] - act_col["min_bottom_y"]
            fits_vert = (total_block_h <= avail_h)
            fits_horiz = ((act_col["x_right"] - t_w) >= 0.0)

            if fits_vert and fits_horiz:
                tbl_cad_x = act_col["x_right"] - t_w
                tbl_cad_y = act_col["curr_top_y"] - total_block_h
                curr_page.tables.append((tbl, Point2D(tbl_cad_x, tbl_cad_y)))
                act_col["curr_top_y"] = tbl_cad_y - cls.TABLE_GAP
                act_col["max_width"] = max(act_col["max_width"], t_w)
                act_col["table_count"] += 1
                placed = True
            else:
                # 2. Aktif sütuna sığmadı. Bu sayfada sola yeni bir sütun açılabilir mi?
                cand_x_right = act_col["x_right"] - act_col["max_width"] - cls.TABLE_GAP
                cand_tbl_cad_x = cand_x_right - t_w
                # Sola açılacak sütun antetin solunda kalacağı için min_y = TABLE_GAP
                cand_avail_h = (inner_h - 5.0) - cls.TABLE_GAP

                # Yatayda iç çerçeve sınırları içinde mi? (>= 0.0) ve dikeyde sığıyor mu?
                if cand_tbl_cad_x >= 0.0 and total_block_h <= cand_avail_h:
                    new_col = curr_page.open_new_column(is_first=False)
                    tbl_cad_x = cand_tbl_cad_x
                    tbl_cad_y = new_col["curr_top_y"] - total_block_h
                    curr_page.tables.append((tbl, Point2D(tbl_cad_x, tbl_cad_y)))
                    new_col["curr_top_y"] = tbl_cad_y - cls.TABLE_GAP
                    new_col["max_width"] = max(new_col["max_width"], t_w)
                    new_col["table_count"] += 1
                    placed = True

            # 3. Bu sayfaya sığmadı (ne aktif sütuna ne de yeni sütuna): Yeni pafta aç!
            if not placed:
                if len(curr_page.tables) > 0:
                    pages_raw.append(curr_page)
                    current_page_idx += 1
                    curr_page = PageState(current_page_idx)

                # Yeni sayfada (veya boş sayfada) ilk sütuna zorunlu yerleştir
                col0 = curr_page.columns[0]
                tbl_cad_x = col0["x_right"] - t_w
                tbl_cad_y = col0["curr_top_y"] - total_block_h
                curr_page.tables.append((tbl, Point2D(tbl_cad_x, tbl_cad_y)))
                col0["curr_top_y"] = tbl_cad_y - cls.TABLE_GAP
                col0["max_width"] = max(col0["max_width"], t_w)
                col0["table_count"] += 1

        pages_raw.append(curr_page)
        total_sheet_count = len(pages_raw)

        # Nihai SheetPageLayout nesnelerini ve dinamik Form 3 antetlerini inşa et
        final_pages: List[SheetPageLayout] = []
        for p_data in pages_raw:
            p_idx = p_data.sheet_index
            page_obj = cls._create_page_skeleton(
                p_idx, sheet_w, sheet_h, m, tb_w, tb_h, base_tb_doc, total_sheet_count
            )

            # Tabloların X ofsetlerini mutlak CAD koordinatlarına göre uyarla
            offset_x = page_obj.offset_x
            for tbl, rel_pt in p_data.tables:
                abs_x = offset_x + m.left + rel_pt.x
                abs_y = m.bottom + rel_pt.y
                page_obj.placed_tables.append(PlacedTableItem(tbl, Point2D(abs_x, abs_y), p_idx))

            final_pages.append(page_obj)

        return MultiSheetLayout(total_sheets=total_sheet_count, pages=final_pages)

    @classmethod
    def _create_page_skeleton(
        cls,
        page_index: int,
        sheet_w: float,
        sheet_h: float,
        margins: Any,
        tb_w: float,
        tb_h: float,
        base_title_block_doc: TitleBlockDocument,
        total_sheets: int
    ) -> SheetPageLayout:
        """Belirtilen pafta numarası için iskelet ve dinamik Form 3 antetini üretir."""
        offset_x = (page_index - 1) * (sheet_w + cls.SHEET_SPACING)

        sheet_rect = Rect2D(offset_x, 0.0, sheet_w, sheet_h)

        inner_x = offset_x + margins.left
        inner_y = margins.bottom
        inner_w = sheet_w - (margins.left + margins.right)
        inner_h = sheet_h - (margins.top + margins.bottom)
        inner_frame = Rect2D(inner_x, inner_y, inner_w, inner_h)

        # Form 3 sağ alt köşe
        tb_x = inner_frame.x_max - tb_w
        tb_y = inner_frame.y_min
        title_block_rect = Rect2D(tb_x, tb_y, tb_w, tb_h)

        # Her pafta için ortak proje verilerini koru, sadece pafta numarasını güncelle
        page_tb_doc = copy.deepcopy(base_title_block_doc)
        page_tb_doc.sheet_num = str(page_index)
        page_tb_doc.total_sheets = str(total_sheets)

        tb_table = create_title_block_table(page_tb_doc)

        return SheetPageLayout(
            sheet_index=page_index,
            offset_x=offset_x,
            sheet_rect=sheet_rect,
            inner_frame_rect=inner_frame,
            title_block_rect=title_block_rect,
            title_block_table=tb_table,
            placed_tables=[]
        )
