"""
ГОСТ Р 21.101-2020 Form 1 'Ведомость рабочих чертежей основного комплекта' Veri Modelleri.
Kullanıcı manuel girişini ve gelecekte PDF'ten otomatik aktarımı destekleyecek esnek yapıda tasarlanmıştır.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class WorkingDrawingItem:
    """Tek bir pafta / çalışma çizimi satırı."""
    sheet_number: str = ""   # Лист (örn: 1, 2.1, 2.2, 3, 4...)
    name: str = ""           # Наименование (örn: Общие данные, Спецификация...)
    note: str = ""           # Примечание

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sheet_number": self.sheet_number,
            "name": self.name,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingDrawingItem":
        return cls(
            sheet_number=str(data.get("sheet_number", "")),
            name=str(data.get("name", "")),
            note=str(data.get("note", "")),
        )


def get_default_sample_items() -> List[WorkingDrawingItem]:
    """Örnek jenerik KM çalışma çizimleri (paftalar) listesi."""
    return [
        WorkingDrawingItem(
            sheet_number="1",
            name="Общие данные",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="2",
            name="Схема расположения колонн и связей на отм. 0.000",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="3",
            name="Схема расположения балок перекрытия на отм. +4.200",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="4",
            name="Схема расположения ферм и прогонов покрытия на отм. +8.400",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="5",
            name="Схема расположения связей по колоннам и покрытию",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="6",
            name="Разрезы 1-1, 2-2, 3-3",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="7",
            name="Узлы опирания и крепления балок перекрытия (узлы 1...8)",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="8",
            name="Узлы сопряжения ферм с колоннами и опирания прогонов (узлы 9...16)",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="9",
            name="Узлы вертикальных и горизонтальных связей (узлы 17...22)",
            note="",
        ),
        WorkingDrawingItem(
            sheet_number="10",
            name="Спецификация металлопроката и ведомость расхода стали",
            note="",
        ),
    ]


@dataclass
class WorkingDrawingsDocument:
    """Çalışma belgesi (tüm pafta listesi tablo durumu)."""
    title: str = "Ведомость рабочих чертежей основного комплекта"
    items: List[WorkingDrawingItem] = field(default_factory=get_default_sample_items)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "items": [it.to_dict() for it in self.items],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingDrawingsDocument":
        if not data:
            return cls()
        items_data = data.get("items", [])
        items = [WorkingDrawingItem.from_dict(it) for it in items_data]
        return cls(
            title=data.get("title", "Ведомость рабочих чертежей основного комплекта"),
            items=items,
        )

    # İleride PDF veya harici kaynaktan otomatik veri yükleme için genişletme arayüzü
    def populate_from_items(self, new_items: List[WorkingDrawingItem]) -> None:
        """PDF okuyucu veya toplu aktarıcı tarafından listeyi yeniler."""
        self.items = list(new_items)

    def append_item(self, item: WorkingDrawingItem) -> None:
        """Yeni bir çizim satırı ekler."""
        self.items.append(item)

    def clear_items(self) -> None:
        """Tüm satırları temizler."""
        self.items.clear()
