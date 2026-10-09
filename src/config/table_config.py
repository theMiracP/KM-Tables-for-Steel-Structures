"""
KM Tablo Konfigürasyonu (Parametrik Ölçüler).

DİKKAT: Kullanıcı kuralları gereği, görselde açıkça belirtilmeyen teknik ölçüler
tahmin edilmemiş; Aşama 1 için güvenli geçici oranlar (placeholder) atanmış ve 
[NEEDS USER INPUT] olarak açıkça işaretlenmiştir.
Gerçek GOST ölçüleri Aşama 2'de kullanıcı tarafından verildiğinde yalnızca bu dosya güncellenecektir.
"""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ColumnWidthConfig:
    """
    Sütun genişlikleri (mm cinsinden).
    [NEEDS USER INPUT] - Gerçek GOST milimetre değerleri Aşama 2'de kullanıcıdan alınacaktır.
    """
    mark: float = 20.0          # Марка элемента [NEEDS USER INPUT]
    sketch: float = 30.0        # Эскиз [NEEDS USER INPUT]
    position: float = 12.0      # Поз. [NEEDS USER INPUT]
    section_name: float = 40.0  # Состав [NEEDS USER INPUT]
    force_a: float = 15.0       # A, кН [NEEDS USER INPUT]
    force_n: float = 15.0       # N, кН [NEEDS USER INPUT]
    force_m: float = 15.0       # M, кН*м [NEEDS USER INPUT]
    steel_grade: float = 25.0   # Наименование или марка металла [NEEDS USER INPUT]
    note: float = 25.0          # Примечание [NEEDS USER INPUT]

    @property
    def total_width(self) -> float:
        """Tablonun toplam genişliği (mm)."""
        return (
            self.mark
            + self.sketch
            + self.position
            + self.section_name
            + self.force_a
            + self.force_n
            + self.force_m
            + self.steel_grade
            + self.note
        )

@dataclass
class RowHeightConfig:
    """
    Satır yükseklikleri (mm cinsinden).
    [NEEDS USER INPUT] - Gerçek GOST satır yükseklikleri Aşama 2'de kullanıcıdan alınacaktır.
    """
    header_primary: float = 8.0   # Başlık 1. seviye (Сечение, Усилие...) [NEEDS USER INPUT]
    header_secondary: float = 8.0 # Başlık 2. seviye (Эскиз, Поз., Состав, A, N, M...) [NEEDS USER INPUT]
    data_row_standard: float = 8.0 # Standart tek satırlı veri satırı [NEEDS USER INPUT]
    data_row_sub: float = 6.0      # Çok parçalı (ör. 2 levhalı) elemanlarda alt satır yüksekliği [NEEDS USER INPUT]
    title_gap: float = 5.0         # 'Ведомость элементов' başlığı ile tablo arası boşluk [NEEDS USER INPUT]

    @property
    def total_header_height(self) -> float:
        return self.header_primary + self.header_secondary

@dataclass
class TypographyConfig:
    """
    Yazı tipleri ve yükseklikleri (mm cinsinden).
    [NEEDS USER INPUT] - Gerçek CAD yazı fontu ve boyutları Aşama 2'de kullanıcıdan alınacaktır.
    """
    font_name: str = "ISOCPEUR"             # CAD yazı tipi stili [NEEDS USER INPUT]
    title_height: float = 4.0               # 'Ведомость элементов' başlık metin yüksekliği [NEEDS USER INPUT]
    header_text_height: float = 2.5         # Başlık hücreleri metin yüksekliği [NEEDS USER INPUT]
    data_text_height: float = 2.5           # Veri hücreleri metin yüksekliği [NEEDS USER INPUT]
    sub_text_height: float = 2.0            # İndis veya alt metin yüksekliği [NEEDS USER INPUT]

@dataclass
class TableConfig:
    """
    Merkezi parametrik tablo konfigürasyonu.
    Magic number kullanımını engeller.
    """
    columns: ColumnWidthConfig = field(default_factory=ColumnWidthConfig)
    rows: RowHeightConfig = field(default_factory=RowHeightConfig)
    typography: TypographyConfig = field(default_factory=TypographyConfig)
    cell_padding_x: float = 1.0     # Hücre yatay iç boşluğu (mm) [NEEDS USER INPUT]
    cell_padding_y: float = 0.8     # Hücre dikey iç boşluğu (mm) [NEEDS USER INPUT]
    table_title: str = "Ведомость элементов"

DEFAULT_TABLE_CONFIG = TableConfig()
