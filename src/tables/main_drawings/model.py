"""
ГОСТ Р 21.101-2020 Form 2 'Ведомость основных комплектов рабочих чертежей' Veri Modelleri.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class DrawingSetItem:
    """Tek bir ana çalışma çizim takımı satırı."""
    designation: str = ""    # Обозначение (örn: 2026-001-КМ1)
    name: str = ""           # Наименование (örn: Металлические конструкции секции П...)
    note: str = ""           # Примечание

    def to_dict(self) -> Dict[str, Any]:
        return {
            "designation": self.designation,
            "name": self.name,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DrawingSetItem":
        return cls(
            designation=str(data.get("designation", "")),
            name=str(data.get("name", "")),
            note=str(data.get("note", "")),
        )


def get_default_sample_items() -> List[DrawingSetItem]:
    """Örnek jenerik ana çalışma çizim takımları listesi."""
    return [
        DrawingSetItem(
            designation="2026-001-ПЗ",
            name="Пояснительная записка",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-АР",
            name="Архитектурные решения",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-КЖ1",
            name="Конструкции железобетонные. Фундаменты",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-КЖ2",
            name="Конструкции железобетонные. Каркас",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-КМ1",
            name="Конструкции металлические. Каркас главного корпуса",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-КМ2",
            name="Конструкции металлические. Фахверк и связи",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-КМ3",
            name="Конструкции металлические. Эстакада трубопроводов",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-КМД",
            name="Конструкции металлические деталировочные",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-ОВ",
            name="Отопление, вентиляция и кондиционирование",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-ВК",
            name="Водоснабжение и канализация",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-ЭОМ",
            name="Силовое электрооборудование и электроосвещение",
            note="",
        ),
        DrawingSetItem(
            designation="2026-001-АК",
            name="Автоматизация комплексная",
            note="",
        ),
    ]


@dataclass
class MainDrawingsDocument:
    """Çalışma belgesi (tüm tablo durumu)."""
    title: str = "Ведомость основных комплектов рабочих чертежей"
    items: List[DrawingSetItem] = field(default_factory=get_default_sample_items)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "items": [it.to_dict() for it in self.items],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MainDrawingsDocument":
        if not data:
            return cls()
        items_data = data.get("items", [])
        items = [DrawingSetItem.from_dict(it) for it in items_data]
        return cls(
            title=data.get("title", "Ведомость основных комплектов рабочих чертежей"),
            items=items,
        )
