"""
ГОСТ Р 21.101-2020 Form 2 'Ведомость основных комплектов рабочих чертежей' Konfigürasyonu.
Tüm ölçüler milimetre (mm) cinsindendir ve 1:1 CAD ölçeğine uygundur.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class MainDrawingsColumnWidths:
    """
    ГОСТ Р 21.101-2020 Форма 2 Sütun Genişlikleri:
    - Обозначение: 60.0 mm
    - Наименование: 95.0 mm
    - Примечание: 30.0 mm
    Toplam Genişlik: 185.0 mm (Form 3 ana antet ile tam aynı genişlikte, antet üstüne kusursuz oturur).
    """
    col_designation: float = 60.0   # Обозначение
    col_name: float = 95.0          # Наименование
    col_note: float = 30.0          # Примечание

    @property
    def all_widths(self) -> List[float]:
        return [self.col_designation, self.col_name, self.col_note]

    @property
    def total_width(self) -> float:
        return self.col_designation + self.col_name + self.col_note


@dataclass(frozen=True)
class MainDrawingsRowHeights:
    """
    Satır Yükseklikleri (mm):
    - Sütun Başlıkları: 15.0 mm (ГОСТ Р 21.101 Форма 2 standardı)
    - Minimum Veri Satırı: 8.0 mm (Tek satırlı veri için standart ГОСТ minimumu)
    - Çok satırlı verilerde metin sarımına göre dinamik satır yüksekliği
    """
    header_height: float = 15.0
    min_item_height: float = 8.0
    line_height_pitch: float = 4.0


@dataclass(frozen=True)
class MainDrawingsTypography:
    title_font_size: float = 3.5     # mm (Bold, tablonun üstündeki başlık)
    header_font_size: float = 3.0    # mm (Bold)
    data_font_size: float = 2.5      # mm (Normal)


@dataclass
class MainDrawingsConfig:
    columns: MainDrawingsColumnWidths = field(default_factory=MainDrawingsColumnWidths)
    rows: MainDrawingsRowHeights = field(default_factory=MainDrawingsRowHeights)
    typography: MainDrawingsTypography = field(default_factory=MainDrawingsTypography)
    table_title: str = "Ведомость основных комплектов рабочих чертежей"


DEFAULT_MAIN_DRAWINGS_CONFIG = MainDrawingsConfig()
