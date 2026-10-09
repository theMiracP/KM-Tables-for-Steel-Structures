"""
KM Tablo Oluşturucu - 'Ведомость расхода стали' Domain Veri Modeli.
ГОСТ 21.502 uyarınca eleman bazında çelik profil türlerine göre sarfiyat (kg) veri yapıları.
"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SteelConsumptionItem:
    """Tek bir elemanın profil kategorilerine göre çelik sarfiyatı (kg)."""
    mark: str = ""              # Eleman markası (örn: "Б1", "К1", "Ф1")
    i_beam: float = 0.0         # Двутавры (I profiller), kg
    channel: float = 0.0        # Швеллеры ([ profiller), kg
    angle: float = 0.0          # Уголки (L profiller), kg
    tube: float = 0.0           # Трубы (□ / ○ boru & kutu profiller), kg
    plate: float = 0.0          # Листовой прокат (- sac/lama), kg
    total: float = 0.0          # Toplam sarfiyat, kg
    note: str = ""              # Not / Açıklama
    raw_values: Dict[str, str] = field(default_factory=dict)  # Sayısal olmayan veya ham girdiler

    def calculate_total(self) -> float:
        """Tüm profil ağırlıklarının toplamını hesaplar."""
        return round(self.i_beam + self.channel + self.angle + self.tube + self.plate, 2)


@dataclass
class SteelConsumptionDocument:
    """Çelik Sarfiyat Çizelgesi çalışma belgesi."""
    items: List[SteelConsumptionItem] = field(default_factory=list)

    def get_column_totals(self) -> Dict[str, float]:
        """Her bir profil sütununun genel toplamını hesaplar."""
        totals = {
            "i_beam": 0.0,
            "channel": 0.0,
            "angle": 0.0,
            "tube": 0.0,
            "plate": 0.0,
            "total": 0.0,
        }
        for it in self.items:
            totals["i_beam"] += it.i_beam
            totals["channel"] += it.channel
            totals["angle"] += it.angle
            totals["tube"] += it.tube
            totals["plate"] += it.plate
            totals["total"] += it.calculate_total()

        for k in totals:
            totals[k] = round(totals[k], 2)
        return totals

    def get_grand_total(self) -> float:
        """Tüm elemanların genel toplam çelik ağırlığını (kg) döndürür."""
        return self.get_column_totals()["total"]


def build_sample_steel_consumption() -> List[SteelConsumptionItem]:
    """Tipik bir ГОСТ 21.502 KM çelik projesi için gerçekçi sarfiyat örnek verileri."""
    return [
        SteelConsumptionItem(
            mark="Б1",
            i_beam=420.5,
            channel=0.0,
            angle=35.2,
            tube=0.0,
            plate=48.0,
            total=503.7,
            note="Ana Kiriş"
        ),
        SteelConsumptionItem(
            mark="Б2",
            i_beam=215.0,
            channel=0.0,
            angle=18.5,
            tube=0.0,
            plate=22.4,
            total=255.9,
            note="İkincil Kiriş"
        ),
        SteelConsumptionItem(
            mark="К1",
            i_beam=680.0,
            channel=0.0,
            angle=0.0,
            tube=0.0,
            plate=95.5,
            total=775.5,
            note="Ana Kolon"
        ),
        SteelConsumptionItem(
            mark="С1",
            i_beam=0.0,
            channel=145.0,
            angle=82.0,
            tube=0.0,
            plate=28.0,
            total=255.0,
            note="Dikey Çapraz"
        ),
        SteelConsumptionItem(
            mark="Ф1",
            i_beam=0.0,
            channel=0.0,
            angle=320.0,
            tube=0.0,
            plate=64.0,
            total=384.0,
            note="Çatı Makası"
        ),
        SteelConsumptionItem(
            mark="П1",
            i_beam=0.0,
            channel=180.5,
            angle=0.0,
            tube=0.0,
            plate=15.0,
            total=195.5,
            note="Çatı Aşığı"
        ),
        SteelConsumptionItem(
            mark="Р1",
            i_beam=0.0,
            channel=0.0,
            angle=0.0,
            tube=112.0,
            plate=14.0,
            total=126.0,
            note="Rüzgar Kolonu"
        ),
    ]
