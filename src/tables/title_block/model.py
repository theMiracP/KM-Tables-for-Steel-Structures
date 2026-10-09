"""
ГОСТ Р 21.101-2020 Form 3 Başlık Bloğu (Title Block / Основная надпись) Veri Modeli.
Proje kodu, şantiye adı, yapı adı, pafta başlığı, aşama, pafta numaraları,
sorumlu mühendis imzaları ve revizyon kayıtlarını yönetir.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import copy


@dataclass
class SignatoryEntry:
    """Tek bir sorumlu mühendis / onay makamı satırı (Графы 10, 11, 12, 13)."""
    role: str                       # Görev (Разраб., Проверил, Гл. констр., Н. контр., Нач. отд., ГИП)
    surname: str                    # Soyadı (Иванов, Петров, Сидоров...)
    signature: str = "✓"            # İmza / Paraf simgesi
    date: str = "23.09.26"          # İmza tarihi (GG.AA.YY)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignatoryEntry":
        return cls(
            role=data.get("role", ""),
            surname=data.get("surname", ""),
            signature=data.get("signature", ""),
            date=data.get("date", "")
        )


@dataclass
class RevisionEntry:
    """Tek bir revizyon kayıt satırı (Таблица регистрации изменений)."""
    rev_num: str = ""               # Изм. (Değişiklik no: 1, 2...)
    num_changes: str = ""           # Кол.уч. (Değiştirilen alan/bölüm sayısı)
    sheet: str = ""                 # Лист (Sayfa no veya Зам.)
    doc_num: str = ""               # №док. (Revizyon izin/emir belgesi no)
    signature: str = ""             # Подпись (İmza/Paraf)
    date: str = ""                  # Дата (Revizyon tarihi)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RevisionEntry":
        return cls(
            rev_num=data.get("rev_num", ""),
            num_changes=data.get("num_changes", ""),
            sheet=data.get("sheet", ""),
            doc_num=data.get("doc_num", ""),
            signature=data.get("signature", ""),
            date=data.get("date", "")
        )


def build_default_signatories() -> List[SignatoryEntry]:
    """Standart örnek GOST mühendis kadrosu (Örnek isimler)."""
    return [
        SignatoryEntry(role="Разраб.", surname="Иванов", signature="✓", date="15.03.26"),
        SignatoryEntry(role="Проверил", surname="Петров", signature="✓", date="16.03.26"),
        SignatoryEntry(role="Гл. констр.", surname="Сидоров", signature="✓", date="17.03.26"),
        SignatoryEntry(role="Н. контр.", surname="Кузнецов", signature="✓", date="18.03.26"),
        SignatoryEntry(role="Нач. отд.", surname="Смирнов", signature="✓", date="18.03.26"),
        SignatoryEntry(role="ГИП", surname="Попов", signature="✓", date="19.03.26"),
    ]


def build_empty_signatories() -> List[SignatoryEntry]:
    """6 standart GOST mühendis satırı (Görevler korunur; soyadı, imza ve tarih alanları temizlenir)."""
    return [
        SignatoryEntry(role="Разраб.", surname="", signature="", date=""),
        SignatoryEntry(role="Проверил", surname="", signature="", date=""),
        SignatoryEntry(role="Гл. констр.", surname="", signature="", date=""),
        SignatoryEntry(role="Н. контр.", surname="", signature="", date=""),
        SignatoryEntry(role="Нач. отд.", surname="", signature="", date=""),
        SignatoryEntry(role="ГИП", surname="", signature="", date=""),
    ]


def build_default_revisions() -> List[RevisionEntry]:
    """Form 3 üstündeki 4 revizyon satırı (başlangıçta boş)."""
    return [
        RevisionEntry(),
        RevisionEntry(),
        RevisionEntry(),
        RevisionEntry(),
    ]


@dataclass
class TitleBlockDocument:
    """
    ГОСТ Р 21.101-2020 Форма 3 Ana Antet Belgesi (185 x 55 mm).
    Örnek mühendislik verileri içerir.
    """
    # 1. Doküman Kodu / Şifresi (Графа 1, 115x15mm)
    doc_code: str = "2026-001-КМ"

    # 2. Şantiye / Tesis / Proje Adı ve Adresi (Графа 2, 115x10mm)
    project_name: str = (
        "Производственно-складской комплекс в промышленном парке «Северный»,\n"
        "расположенный по адресу: Московская область, г.о. Солнечногорск, тер. Промзона-1,\n"
        "земельный участок с кадастровым номером 50:09:0000000:12345"
    )

    # 3. Yapı / Bölüm / Etap Adı (Графа 3, 65x15mm)
    building_name: str = "Главный производственный корпус\nМеталлический каркас"

    # 4. Pafta Başlığı / Çizim İçeriği (Графа 4, 65x15mm)
    sheet_title: str = "Схема расположения колонн и балок на отм. +4.200"

    # 5. Pafta Statüsü ve Numaralandırma (Графы 6, 7, 8)
    stage: str = "Р"                    # Стадия (Р = Рабочая документация, П = Проект)
    sheet_num: str = "1"                # Лист (Bu paftanın sıra numarası)
    total_sheets: str = "12"            # Листов (Toplam pafta adedi)

    # 6. Tasarım Bürosu / Firma Adı & Logo (Графа 9, 50x15mm)
    company_name: str = "ООО «ПРОЕКТ-СТРОЙ»"
    company_logo: bool = False
    logo_image_path: Optional[str] = None

    # 7. Kadro ve Revizyon Tabloları
    signatories: List[SignatoryEntry] = field(default_factory=build_default_signatories)
    revisions: List[RevisionEntry] = field(default_factory=build_default_revisions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_code": self.doc_code,
            "project_name": self.project_name,
            "building_name": self.building_name,
            "sheet_title": self.sheet_title,
            "stage": self.stage,
            "sheet_num": self.sheet_num,
            "total_sheets": self.total_sheets,
            "company_name": self.company_name,
            "company_logo": self.company_logo,
            "logo_image_path": self.logo_image_path,
            "signatories": [s.to_dict() for s in self.signatories],
            "revisions": [r.to_dict() for r in self.revisions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TitleBlockDocument":
        doc = cls(
            doc_code=data.get("doc_code", "2026-001-КМ"),
            project_name=data.get("project_name", ""),
            building_name=data.get("building_name", ""),
            sheet_title=data.get("sheet_title", ""),
            stage=data.get("stage", "Р"),
            sheet_num=data.get("sheet_num", "1"),
            total_sheets=data.get("total_sheets", ""),
            company_name=data.get("company_name", "ООО «ПРОЕКТ-СТРОЙ»"),
            company_logo=data.get("company_logo", False),
            logo_image_path=data.get("logo_image_path"),
        )
        if "signatories" in data and isinstance(data["signatories"], list):
            doc.signatories = [SignatoryEntry.from_dict(s) for s in data["signatories"]]
        if "revisions" in data and isinstance(data["revisions"], list):
            doc.revisions = [RevisionEntry.from_dict(r) for r in data["revisions"]]
        return doc

    def clone(self) -> "TitleBlockDocument":
        return copy.deepcopy(self)
