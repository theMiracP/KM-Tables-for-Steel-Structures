"""
ГОСТ Р 21.101-2020 Form 1 'Ведомость рабочих чертежей основного комплекта' Konfigürasyonu.
Tüm ölçüler milimetre (mm) cinsindendir ve 1:1 CAD ölçeğine uygundur.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class WorkingDrawingsColumnWidths:
    """
    ГОСТ Р 21.101-2020 Форма 1 Sütun Genişlikleri:
    - Лист: 15.0 mm (Pafta / Çizim Numarası)
    - Наименование: 140.0 mm (Çizim Adı / Başlık)
    - Примечание: 30.0 mm (Not / Açıklama)
    Toplam Genişlik: 185.0 mm (Form 3 ana antet ile tam aynı genişlikte, antet üstüne kusursuz oturur).
    """
    col_sheet: float = 15.0   # Лист
    col_name: float = 140.0   # Наименование
    col_note: float = 30.0    # Примечание

    @property
    def all_widths(self) -> List[float]:
        return [self.col_sheet, self.col_name, self.col_note]

    @property
    def total_width(self) -> float:
        return self.col_sheet + self.col_name + self.col_note


@dataclass(frozen=True)
class WorkingDrawingsRowHeights:
    """
    Satır Yükseklikleri (mm):
    - Sütun Başlıkları: 15.0 mm (ГОСТ Р 21.101 Форма 1 standardı)
    - Minimum Veri Satırı: 8.0 mm (Tek satırlı veri için standart ГОСТ minimumu)
    - Çok satırlı başlıklarda metin sarımına göre dinamik satır yüksekliği
    """
    header_height: float = 15.0
    min_item_height: float = 8.0
    line_height_pitch: float = 4.0


@dataclass(frozen=True)
class WorkingDrawingsTypography:
    title_font_size: float = 3.5     # mm (Bold, tablonun üstündeki başlık)
    header_font_size: float = 3.0    # mm (Bold, sütun başlıkları)
    data_font_size: float = 2.5      # mm (Normal ISOCPEUR veri fontu)


@dataclass
class WorkingDrawingsConfig:
    columns: WorkingDrawingsColumnWidths = field(default_factory=WorkingDrawingsColumnWidths)
    rows: WorkingDrawingsRowHeights = field(default_factory=WorkingDrawingsRowHeights)
    typography: WorkingDrawingsTypography = field(default_factory=WorkingDrawingsTypography)
    table_title: str = "Ведомость рабочих чертежей основного комплекта"


DEFAULT_WORKING_DRAWINGS_CONFIG = WorkingDrawingsConfig()
