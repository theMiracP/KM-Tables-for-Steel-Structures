"""
Sayfa Boyutları, Kenarlıklar ve Antet Konfigürasyonu.
ГОСТ 2.301 ve ГОСТ Р 21.101-2020 standartlarına uygundur.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple, Optional, Any

class SheetSize(str, Enum):
    A4 = "A4"
    A3 = "A3"
    A2 = "A2"
    A1 = "A1"
    A0 = "A0"

class SheetOrientation(str, Enum):
    PORTRAIT = "Dikey (Книжная)"
    LANDSCAPE = "Yatay (Альбомная)"

class TablePlacement(str, Enum):
    STANDALONE = "Yalnızca Tablo (Orijin 0,0)"
    ABOVE_TITLEBLOCK = "Sayfa Düzeni: Antet Üstü (Sağ Alt)"
    TOP_RIGHT = "Sayfa Düzeni: Sağ Üst Köşe"
    TOP_LEFT = "Sayfa Düzeni: Sol Üst Köşe"
    CENTER_SHEET = "Sayfa Düzeni: Paftayı Ortala"
    CUSTOM = "Özel Koordinat"

# Standart sayfa boyutları (Genişlik x Yükseklik, mm)
SHEET_DIMENSIONS: Dict[SheetSize, Tuple[float, float]] = {
    SheetSize.A4: (210.0, 297.0),
    SheetSize.A3: (420.0, 297.0),
    SheetSize.A2: (594.0, 420.0),
    SheetSize.A1: (841.0, 594.0),
    SheetSize.A0: (1189.0, 841.0),
}

@dataclass
class SheetMargins:
    """ГОСТ Р 21.101-2020 Приложение И kenar boşlukları (mm)."""
    left: float = 20.0    # Ciltleme payı (поле для подшивки)
    top: float = 5.0      # Üst kenar
    right: float = 5.0    # Sağ kenar
    bottom: float = 5.0   # Alt kenar

@dataclass
class TitleBlockConfig:
    """ГОСТ Р 21.101-2020 Форма 3 ana antet boyutları (mm)."""
    width: float = 185.0
    height: float = 55.0
    gap_above: float = 0.0  # Tablo ile antet arasındaki boşluk (varsayılan 0: antet üstüne oturur)

@dataclass
class LayoutConfig:
    """Sayfa ve yerleşim ayarları."""
    placement: TablePlacement = TablePlacement.STANDALONE
    size: SheetSize = SheetSize.A3
    orientation: SheetOrientation = SheetOrientation.LANDSCAPE
    margins: SheetMargins = field(default_factory=SheetMargins)
    title_block: TitleBlockConfig = field(default_factory=TitleBlockConfig)
    title_block_doc: Optional[Any] = None  # Form 3 veri modeli (TitleBlockDocument)
    custom_x: float = 0.0
    custom_y: float = 0.0

    def get_sheet_dimensions(self) -> Tuple[float, float]:
        """Yönelime göre genişlik ve yükseklik döner."""
        w, h = SHEET_DIMENSIONS[self.size]
        if self.orientation == SheetOrientation.PORTRAIT:
            return (min(w, h), max(w, h))
        return (max(w, h), min(w, h))

    def get_format_designation(self) -> str:
        """
        ГОСТ 2.301-68 ve СПДС (nanoCAD/AutoCAD СПДС) standartlarına uygun pafta format etiketi.
        Örn: 'Формат А1А' (Yatay A1), 'Формат А3А' (Yatay A3), 'Формат А4' (Dikey A4).
        """
        # Kiril 'А' harfi (U+0410)
        size_str = self.size.value if hasattr(self.size, "value") else str(self.size)
        base = f"А{size_str[1:]}" if len(size_str) > 1 else size_str
        # СПДС standardında yatay (альбомная) paftalarda sonuna Kiril 'А' eklenir
        is_landscape = (
            self.orientation == SheetOrientation.LANDSCAPE or
            "Yatay" in str(self.orientation) or
            "Альбомная" in str(self.orientation) or
            "LANDSCAPE" in str(self.orientation).upper()
        )
        suffix = "А" if is_landscape else ""
        return f"Формат {base}{suffix}"

DEFAULT_LAYOUT_CONFIG = LayoutConfig()
