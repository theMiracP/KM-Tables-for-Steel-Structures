"""
ГОСТ Р 21.101-2020 Приложение Л (Форма 9) Veri Modeli.
Разрешение на внесение изменений (Değişiklik İzni).
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import copy


@dataclass
class ChangeSignatoryEntry:
    """Tek bir imza/sorumlu satırı (ГОСТ Р 21.101 Форма 9, Графы 9, 10, 11)."""
    role: str                       # Görev (Изм. внес, Составил, ГИП, Утв.)
    surname: str                    # Soyadı
    signature: str = "✓"            # İmza / Paraf
    date: str = ""                  # Tarih (GG.AA.YY)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChangeSignatoryEntry":
        return cls(
            role=data.get("role", ""),
            surname=data.get("surname", ""),
            signature=data.get("signature", "✓"),
            date=data.get("date", "")
        )


@dataclass
class ChangePermissionItem:
    """Tek bir değişiklik içeriği satırı (ГОСТ Р 21.101 Форма 9, Графы 4, 5, 6, 7, 8)."""
    rev_num: str = "1"              # Графа 4: Изм. (Değişiklik no)
    sheet: str = "1"                # Графа 5: Лист (Değiştirilen pafta no veya Все / Зам. / Нов.)
    content: str = ""               # Графа 6: Содержание изменения (Değişiklik içeriği açıklaması)
    reason_code: str = "1"          # Графа 7: Код (Değişiklik nedeni kodu: 1..5 veya -)
    note: str = ""                  # Графа 8: Примечание (Not)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChangePermissionItem":
        return cls(
            rev_num=str(data.get("rev_num", "1")),
            sheet=str(data.get("sheet", "1")),
            content=str(data.get("content", "")),
            reason_code=str(data.get("reason_code", "")),
            note=str(data.get("note", ""))
        )


def build_default_change_signatories() -> List[ChangeSignatoryEntry]:
    """Standart 4 satırlık GOST Form 9 imza kadrosu (Örnek jenerik isimler)."""
    return [
        ChangeSignatoryEntry(role="Изм. внес", surname="Иванов", signature="✓", date="18.08.26"),
        ChangeSignatoryEntry(role="Составил", surname="Петров", signature="✓", date="18.08.26"),
        ChangeSignatoryEntry(role="ГИП", surname="Сидоров", signature="✓", date="18.08.26"),
        ChangeSignatoryEntry(role="Утв.", surname="Кузнецов", signature="✓", date="18.08.26"),
    ]


def build_empty_change_signatories() -> List[ChangeSignatoryEntry]:
    """Boş 4 satırlık GOST Form 9 imza kadrosu."""
    return [
        ChangeSignatoryEntry(role="Изм. внес", surname="", signature="✓", date=""),
        ChangeSignatoryEntry(role="Составил", surname="", signature="✓", date=""),
        ChangeSignatoryEntry(role="ГИП", surname="", signature="✓", date=""),
        ChangeSignatoryEntry(role="Утв.", surname="", signature="✓", date=""),
    ]


def build_default_change_items() -> List[ChangePermissionItem]:
    """Standart örnek GOST Form 9 jenerik değişiklik kayıtları."""
    return [
        ChangePermissionItem(
            rev_num="1",
            sheet="1",
            content="Внесены изменения в ведомость основных комплектов рабочих чертежей и ведомость чертежей основного комплекта",
            reason_code="1",
            note=""
        ),
        ChangePermissionItem(
            rev_num="1",
            sheet="3",
            content="Скорректирована спецификация металлопроката и примечание",
            reason_code="1",
            note=""
        ),
        ChangePermissionItem(
            rev_num="1",
            sheet="6",
            content="Скорректирован монтажный стык балок и колонн. Скорректировано примечание",
            reason_code="1",
            note=""
        ),
        ChangePermissionItem(
            rev_num="1",
            sheet="7",
            content="Скорректировано примечание к схеме расположения элементов",
            reason_code="4",
            note=""
        ),
    ]


@dataclass
class ChangePermissionDocument:
    """
    ГОСТ Р 21.101-2020 Форма 9 Değişiklik İzni Belgesi.
    """
    resolution_number: str = "001/26"  # Графа 1: Разрешение № (örn: 001/26)
    doc_code: str = "2026-001-КМ"  # Графа 2: Обозначение документа
    object_name: str = (
        "Производственно-складской комплекс в промышленном парке «Северный»,\n"
        "расположенный по адресу: Московская область, г.о. Солнечногорск, тер. Промзона-1,\n"
        "земельный участок с кадастровым номером 50:09:0000000:12345"
    )  # Графа 3: Наименование объекта строительства
    company_name: str = "ООО «ПРОЕКТ-СТРОЙ»"  # Графа 12
    sheet_num: str = "1"  # Графа 17: Лист
    sheet_count: str = "1"  # Графа 18: Листов
    signatories: List[ChangeSignatoryEntry] = field(default_factory=build_default_change_signatories)
    items: List[ChangePermissionItem] = field(default_factory=build_default_change_items)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resolution_number": self.resolution_number,
            "doc_code": self.doc_code,
            "object_name": self.object_name,
            "company_name": self.company_name,
            "sheet_num": self.sheet_num,
            "sheet_count": self.sheet_count,
            "signatories": [s.to_dict() for s in self.signatories],
            "items": [it.to_dict() for it in self.items],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChangePermissionDocument":
        if not data:
            return cls.get_default_sample_document()

        raw_sigs = data.get("signatories", [])
        sigs = [ChangeSignatoryEntry.from_dict(s) for s in raw_sigs] if raw_sigs else build_default_change_signatories()

        raw_items = data.get("items", [])
        items = [ChangePermissionItem.from_dict(it) for it in raw_items] if raw_items else [ChangePermissionItem()]

        return cls(
            resolution_number=str(data.get("resolution_number", "001/26")),
            doc_code=str(data.get("doc_code", "2026-001-КМ")),
            object_name=str(data.get("object_name", "")),
            company_name=str(data.get("company_name", "ООО «ПРОЕКТ-СТРОЙ»")),
            sheet_num=str(data.get("sheet_num", "1")),
            sheet_count=str(data.get("sheet_count", "1")),
            signatories=sigs,
            items=items,
        )

    @classmethod
    def get_default_sample_document(cls) -> "ChangePermissionDocument":
        return cls()

    @classmethod
    def get_empty_document(cls) -> "ChangePermissionDocument":
        return cls(
            resolution_number="",
            doc_code="",
            object_name="",
            company_name="",
            sheet_num="1",
            sheet_count="1",
            signatories=build_empty_change_signatories(),
            items=[ChangePermissionItem(rev_num="1", sheet="1", content="", reason_code="", note="")],
        )
