"""
ГОСТ ve CAD Standartları Tanımları.
Katmanlar, renkler, çizgi tipleri ve kalınlıkları.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class CadLayer:
    name: str
    color: int          # AutoCAD Color Index (ACI): 1=Red, 2=Yellow, 3=Green, 4=Cyan, 5=Blue, 6=Magenta, 7=White/Black
    lineweight: int     # mm x 100 (ör. 70 = 0.70mm, 25 = 0.25mm)
    linetype: str = "CONTINUOUS"
    description: str = ""

# Standart KM Tablo Katmanları
LAYER_BORDER = CadLayer(
    name="KM_TABLO_CERCEVE",
    color=7,            # Beyaz / Siyah
    lineweight=70,      # 0.70 mm kalın ana çizgi (ГОСТ 2.303)
    description="Tablo dış çerçevesi ve ana ayırıcı kalın çizgiler"
)

LAYER_GRID = CadLayer(
    name="KM_TABLO_IZGARA",
    color=7,            # Beyaz / Siyah
    lineweight=25,      # 0.25 mm ince çizgi (ГОСТ 2.303)
    description="Tablo iç ızgara ve hücre bölüntü çizgileri"
)

LAYER_TEXT = CadLayer(
    name="KM_TABLO_METIN",
    color=7,            # Beyaz / Siyah
    lineweight=25,
    description="Tablo başlıkları ve veri metinleri"
)

LAYER_SKETCH = CadLayer(
    name="KM_TABLO_ESKIZ",
    color=7,
    lineweight=35,      # 0.35 mm orta/belirgin çizgi
    description="Profil kesit eskizleri ve kaynak sembolleri"
)

LAYER_SHEET_FRAME = CadLayer(
    name="KM_SAYFA_CERCEVE",
    color=7,
    lineweight=70,      # 0.70 mm
    description="Çizim paftası dış ve iç çerçeve çizgileri"
)

LAYER_TITLEBLOCK = CadLayer(
    name="KM_ANTET",
    color=7,
    lineweight=25,
    description="ГОСТ Form 3 ana antet çizgileri ve metinleri"
)

ALL_LAYERS = [
    LAYER_BORDER,
    LAYER_GRID,
    LAYER_TEXT,
    LAYER_SKETCH,
    LAYER_SHEET_FRAME,
    LAYER_TITLEBLOCK,
]
