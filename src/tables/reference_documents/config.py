"""
ГОСТ Р 21.101-2020 Form 2 'Ведомость ссылочных и прилагаемых документов' Konfigürasyonu.
Tüm ölçüler milimetre (mm) cinsindendir ve 1:1 CAD ölçeğine uygundur.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ReferenceDocsColumnWidths:
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
class ReferenceDocsRowHeights:
    """
    Satır Yükseklikleri (mm):
    - Tablo Başlığı: 12.0 mm (Hücre içi birleşik başlık)
    - Sütun Başlıkları: 10.0 mm
    - Bölüm Başlığı (Ссылочные / Прилагаемые): 8.0 mm
    - Veri Satırı (Standart Doküman): 8.0 mm
    """
    title_height: float = 12.0
    header_height: float = 10.0
    section_height: float = 8.0
    item_height: float = 8.0


@dataclass(frozen=True)
class ReferenceDocsTypography:
    title_font_size: float = 3.5     # mm (Bold)
    header_font_size: float = 3.0    # mm (Bold)
    section_font_size: float = 2.8   # mm (Bold)
    data_font_size: float = 2.5      # mm (Normal)


@dataclass
class ReferenceDocsConfig:
    columns: ReferenceDocsColumnWidths = field(default_factory=ReferenceDocsColumnWidths)
    rows: ReferenceDocsRowHeights = field(default_factory=ReferenceDocsRowHeights)
    typography: ReferenceDocsTypography = field(default_factory=ReferenceDocsTypography)


DEFAULT_REFERENCE_DOCS_CONFIG = ReferenceDocsConfig()
