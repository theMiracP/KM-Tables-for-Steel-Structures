"""
'Ведомость ссылочных и прилагаемых документов' Veri Modelleri.
ГОСТ Р 21.101-2020 Form 2 standartlarına uygun doküman ve kütüphane modelleri.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class ReferenceDocItem:
    """Tabloda yer alan tek bir doküman satırı veya bölüm başlığı."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    designation: str = ""        # Обозначение (örn: ГОСТ 27751-2014, СП 16.13330.2017)
    title: str = ""              # Наименование (RU - Standart Rusça Başlık)
    title_tr: str = ""           # Türkçe Karşılığı / Açıklaması
    title_en: str = ""           # English Title / Explanation
    section: str = "Ссылочные документы"  # Раздел (Ссылочные документы / Прилагаемые документы)
    note: str = ""               # Примечание (Notlar)
    is_section_header: bool = False       # True ise bu satır bir bölüm ayracı başlığıdır

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReferenceDocItem":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            designation=data.get("designation", ""),
            title=data.get("title", ""),
            title_tr=data.get("title_tr", ""),
            title_en=data.get("title_en", ""),
            section=data.get("section", "Ссылочные документы"),
            note=data.get("note", ""),
            is_section_header=data.get("is_section_header", False),
        )


@dataclass
class StandardLibraryItem:
    """
    Standartlar kütüphanesinde (veritabanında) saklanan hazır standart şablonu.
    Kullanıcının standartları kolay anlaması için Rusça, Türkçe ve İngilizce karşılıkları içerir.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    designation: str = ""        # Обозначение (örn: СП 16.13330.2017)
    title_ru: str = ""           # Rusça Başlık (Наименование)
    title_tr: str = ""           # Türkçe Başlık / Açıklama
    title_en: str = ""           # İngilizce Başlık / Açıklama
    section: str = "Ссылочные документы"  # Varsayılan bölüm (Ссылочные / Прилагаемые)
    category: str = "КМ Çelik Yapılar"    # Mühendislik kategorisi / disiplini
    note: str = ""               # Not

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StandardLibraryItem":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            designation=data.get("designation", ""),
            title_ru=data.get("title_ru", ""),
            title_tr=data.get("title_tr", ""),
            title_en=data.get("title_en", ""),
            section=data.get("section", "Ссылочные документы"),
            category=data.get("category", "КМ Çelik Yapılar"),
            note=data.get("note", ""),
        )

    def to_reference_item(self) -> ReferenceDocItem:
        """Kütüphane kaydından tablo satırı üretir."""
        return ReferenceDocItem(
            designation=self.designation,
            title=self.title_ru,
            title_tr=self.title_tr,
            title_en=self.title_en,
            section=self.section,
            note=self.note,
            is_section_header=False,
        )


@dataclass
class ReferenceDocsDocument:
    """'Ведомость ссылочных и прилагаемых документов' tam doküman veri modeli."""
    title: str = "Ведомость ссылочных и прилагаемых документов"
    items: List[ReferenceDocItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReferenceDocsDocument":
        items_data = data.get("items", [])
        items = [ReferenceDocItem.from_dict(it) for it in items_data]
        return cls(
            title=data.get("title", "Ведомость ссылочных и прилагаемых документов"),
            items=items,
        )
