"""
'Ведомость элементов' Tablosuna Özel Parametrik Ölçüler (Sütunlar ve Satırlar).
"""
from dataclasses import dataclass, field
from src.config.table_config import TypographyConfig

@dataclass
class ElementsColumnWidths:
    """Ведомость элементов sütun genişlikleri (mm)."""
    mark: float = 20.0          # Марка элемента
    sketch: float = 30.0        # Эскиз
    position: float = 12.0      # Поз.
    section_name: float = 40.0  # Состав
    force_a: float = 15.0       # A, кН
    force_n: float = 15.0       # N, кН
    force_m: float = 15.0       # M, кН*м
    steel_grade: float = 25.0   # Наименование или марка металла
    note: float = 25.0          # Примечание

    @property
    def total_width(self) -> float:
        return (
            self.mark + self.sketch + self.position + self.section_name +
            self.force_a + self.force_n + self.force_m + self.steel_grade + self.note
        )

@dataclass
class ElementsRowHeights:
    """Ведомость элементов satır yükseklikleri (mm)."""
    header_primary: float = 8.0     # 1. seviye başlık
    header_secondary: float = 8.0   # 2. seviye başlık
    data_row_standard: float = 8.0  # Standart veri satırı
    data_row_sub: float = 6.0       # Çok parçalı elemanlarda alt satır
    title_gap: float = 5.0          # Başlık ile tablo arası boşluk

    @property
    def total_header_height(self) -> float:
        return self.header_primary + self.header_secondary

@dataclass
class ElementsScheduleConfig:
    """Ведомость элементов tam konfigürasyonu."""
    columns: ElementsColumnWidths = field(default_factory=ElementsColumnWidths)
    rows: ElementsRowHeights = field(default_factory=ElementsRowHeights)
    typography: TypographyConfig = field(default_factory=TypographyConfig)
    cell_padding_x: float = 1.0
    cell_padding_y: float = 0.8
    table_title: str = "Ведомость элементов"

DEFAULT_ELEMENTS_CONFIG = ElementsScheduleConfig()
