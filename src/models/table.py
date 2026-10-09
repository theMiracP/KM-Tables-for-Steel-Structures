"""
Genel Parametrik Tablo Modeli.
Hücreler (Cell), Satırlar (Row), Sütunlar (Column) ve Hücre Birleştirme (Rowspan/Colspan) yapısı.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Dict
from src.models.geometry import Rect2D, Point2D
from src.models.sketch import SectionSketch

class HAlign(str, Enum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"

class VAlign(str, Enum):
    MIDDLE = "middle"
    TOP = "top"
    BOTTOM = "bottom"

@dataclass
class TableCell:
    text: str = ""
    rowspan: int = 1
    colspan: int = 1
    halign: HAlign = HAlign.CENTER
    valign: VAlign = VAlign.MIDDLE
    sketch: Optional[SectionSketch] = None
    is_header: bool = False
    # Çizgi görünürlüğü ve hücre birleştirme (rowspan/colspan)
    is_merged_continuation: bool = False  # Birleştirilmiş hücrenin devamı ise çizgi ve metin çizilmez
    border_left: bool = True
    border_right: bool = True
    border_top: bool = True
    border_bottom: bool = True
    # Özel tipografi ve kalın çizgi nitelikleri (Form 3 ve kompleks tablolar için)
    font_size: Optional[float] = None       # mm cinsinden özel yazı boyutu
    is_bold: Optional[bool] = None          # Kalın yazı tipi
    border_top_thick: bool = False          # Üst sınır kalın ana çizgi (0.7mm)
    border_right_thick: bool = False        # Sağ sınır kalın ana çizgi (0.7mm)
    border_left_thick: bool = False         # Sol sınır kalın ana çizgi (0.7mm)
    border_bottom_thick: bool = False       # Alt sınır kalın ana çizgi (0.7mm)

@dataclass
class TableRow:
    cells: List[TableCell] = field(default_factory=list)
    height: float = 8.0
    is_header: bool = False

@dataclass
class TableColumn:
    key: str
    title: str
    width: float

@dataclass
class TableLayoutInfo:
    """Hesaplanan tablo yerleşim koordinatları."""
    total_width: float
    total_height: float
    col_x_offsets: List[float]       # Her sütunun başlangıç X mesafesi
    row_y_offsets: List[float]       # Tablo üstünden itibaren her satırın Y mesafesi
    row_heights: List[float]
    col_widths: List[float]

class Table:
    """
    Parametrik CAD ve Önizleme Tablosu.
    Gelecekte yeni tablo tipleri bu sınıfı kullanarak türetilebilir.
    """
    def __init__(self, title: str = "Ведомость элементов"):
        self.title = title
        self.columns: List[TableColumn] = []
        self.rows: List[TableRow] = []

    def add_column(self, key: str, title: str, width: float) -> None:
        self.columns.append(TableColumn(key=key, title=title, width=width))

    def add_row(self, cells: List[TableCell], height: float = 8.0, is_header: bool = False) -> None:
        self.rows.append(TableRow(cells=cells, height=height, is_header=is_header))

    @property
    def total_width(self) -> float:
        """Tablonun toplam genişliği (mm)."""
        return sum(col.width for col in self.columns)

    @property
    def total_height(self) -> float:
        """Tablonun toplam yüksekliği (mm)."""
        return sum(row.height for row in self.rows)

    def compute_layout(self) -> TableLayoutInfo:
        """Sütun ve satırların toplam boyutlarını ve ofsetlerini hesaplar."""
        col_widths = [col.width for col in self.columns]
        row_heights = [row.height for row in self.rows]

        col_x = [0.0]
        acc_x = 0.0
        for w in col_widths:
            acc_x += w
            col_x.append(acc_x)

        row_y = [0.0]
        acc_y = 0.0
        for h in row_heights:
            acc_y += h
            row_y.append(acc_y)

        total_width = acc_x
        total_height = acc_y

        return TableLayoutInfo(
            total_width=total_width,
            total_height=total_height,
            col_x_offsets=col_x,
            row_y_offsets=row_y,
            row_heights=row_heights,
            col_widths=col_widths,
        )

    def get_cell_cad_rect(
        self,
        row_idx: int,
        col_idx: int,
        origin_x: float,
        origin_y: float,
        layout: Optional[TableLayoutInfo] = None
    ) -> Rect2D:
        """
        CAD koordinat sisteminde (orijin sol alt köşe, Y yukarı pozitif)
        verilen hücrenin dikdörtgen sınırlarını hesaplar.
        """
        if layout is None:
            layout = self.compute_layout()

        row = self.rows[row_idx]
        cell = row.cells[col_idx]

        # X koordinatları (sol -> sağ)
        x0 = origin_x + layout.col_x_offsets[col_idx]
        span_cols = cell.colspan
        end_col = min(col_idx + span_cols, len(layout.col_widths))
        x1 = origin_x + layout.col_x_offsets[end_col]
        w = x1 - x0

        # Y koordinatları (üstten alta mesafe layout.row_y_offsets içindedir)
        # CAD'de origin_y alt kenarsa:
        # Tablonun üst kenarı = origin_y + layout.total_height
        table_top = origin_y + layout.total_height
        top_y = table_top - layout.row_y_offsets[row_idx]
        span_rows = cell.rowspan
        end_row = min(row_idx + span_rows, len(layout.row_heights))
        bottom_y = table_top - layout.row_y_offsets[end_row]
        h = top_y - bottom_y

        return Rect2D(x=x0, y=bottom_y, width=w, height=h)
