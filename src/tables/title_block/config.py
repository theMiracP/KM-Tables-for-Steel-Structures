"""
ГОСТ Р 21.101-2020 Form 3 Geometrik Boyut ve Konfigürasyon Sabitleri.
Tüm ölçüler milimetre (mm) cinsindendir ve 1:1 CAD ölçeğine uygundur.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class TitleBlockColumnWidths:
    """
    Form 3 X ekseni dilimleri (Toplam: 185 mm):
    0-10:   İzm.
    10-20:  Кол.уч.
    20-30:  Лист / Görev Başlığı
    30-45:  №док. / Soyadı
    45-55:  Подпись / İmza
    55-70:  Дата / Tarih
    70-135: Orta Blok (Yapı / Pafta Başlığı)
    135-150: Стадия
    150-165: Лист
    165-185: Листов
    """
    col_rev_num: float = 10.0       # 0: Изм.
    col_num_changes: float = 10.0   # 1: Кол.уч.
    col_sheet: float = 10.0         # 2: Лист
    col_doc_num: float = 15.0       # 3: №док. / Soyadı
    col_signature: float = 10.0     # 4: Подпись
    col_date: float = 15.0          # 5: Дата
    col_middle: float = 65.0        # 6: Orta blok (Yapı/Pafta)
    col_stage: float = 15.0         # 7: Стадия
    col_sheet_no: float = 15.0      # 8: Лист
    col_sheets_total: float = 20.0  # 9: Листов

    @property
    def all_widths(self) -> List[float]:
        return [
            self.col_rev_num,
            self.col_num_changes,
            self.col_sheet,
            self.col_doc_num,
            self.col_signature,
            self.col_date,
            self.col_middle,
            self.col_stage,
            self.col_sheet_no,
            self.col_sheets_total,
        ]

    @property
    def total_width(self) -> float:
        return sum(self.all_widths)


@dataclass(frozen=True)
class TitleBlockRowHeights:
    """
    Form 3 Y ekseni dilimleri (Toplam: 55 mm, her biri 5.0 mm):
    11 satır x 5.0 mm = 55.0 mm.
    """
    row_height: float = 5.0
    total_rows: int = 11

    @property
    def all_heights(self) -> List[float]:
        return [self.row_height] * self.total_rows

    @property
    def total_height(self) -> float:
        return self.row_height * self.total_rows


@dataclass
class TitleBlockConfig:
    total_width: float = 185.0
    total_height: float = 55.0
    columns: TitleBlockColumnWidths = field(default_factory=TitleBlockColumnWidths)
    rows: TitleBlockRowHeights = field(default_factory=TitleBlockRowHeights)


DEFAULT_TITLE_BLOCK_CONFIG = TitleBlockConfig()
