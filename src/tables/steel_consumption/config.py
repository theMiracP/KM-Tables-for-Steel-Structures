"""
KM Tablo Oluşturucu - 'Ведомость расхода стали' Geometrik ve Tipografik Yapılandırma.
ГОСТ 21.502 standart çizim kolon genişlikleri ve satır yükseklikleri (milimetre cinsinden).
"""
from dataclasses import dataclass, field


@dataclass
class SteelConsumptionColumnWidths:
    """Tablo sütun genişlikleri (mm). Form 3 antet genişliği ile birebir uyumlu (185 mm)."""
    mark: float = 35.0         # Марка элемента
    i_beam: float = 25.0       # Двутавры
    channel: float = 25.0      # Швеллеры
    angle: float = 25.0        # Уголки
    tube: float = 25.0         # Трубы
    plate: float = 25.0        # Листовой прокат
    total: float = 25.0        # Всего, кг

    @property
    def total_width(self) -> float:
        return (
            self.mark + self.i_beam + self.channel +
            self.angle + self.tube + self.plate + self.total
        )


@dataclass
class SteelConsumptionRowHeights:
    """Tablo satır yükseklikleri (mm)."""
    header_primary: float = 10.0     # Üst başlık (Марка / Расход стали / Всего)
    header_secondary: float = 8.0    # Alt başlık (Profil isimleri)
    data_row: float = 8.0            # Veri satırları
    total_row: float = 8.0           # İtogo (Toplam) satırı
    title_gap: float = 5.0           # Tablo üst başlık boşluğu


@dataclass
class SteelConsumptionConfig:
    """Çelik Sarfiyat Çizelgesi tam konfigürasyon paketi."""
    columns: SteelConsumptionColumnWidths = field(default_factory=SteelConsumptionColumnWidths)
    rows: SteelConsumptionRowHeights = field(default_factory=SteelConsumptionRowHeights)
    table_title: str = "Ведомость расхода стали, кг"


DEFAULT_STEEL_CONSUMPTION_CONFIG = SteelConsumptionConfig()
