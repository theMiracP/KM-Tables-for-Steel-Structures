"""
ГОСТ Р 21.101-2020 Приложение Р и С (Форма 12) Veri Modelleri.
Титульный лист (Title Sheet / Başlık Sayfası).
Kurgusal ve jenerik mühendislik verileri içerir (Kural 6).
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import copy


@dataclass
class TitleSheetSignatory:
    """Tek bir sorumlu imza satırı (Поля 9, 10, 11)."""
    role: str                       # Görev / Unvan (Главный инженер, Главный инженер проекта, Начальник отдела...)
    surname: str                    # Soyadı ve İnisiyaller (Иванов И.И. veya И.О. Фамилия)
    signature: str = "✓"            # İmza / Paraf
    date: str = ""                  # Tarih

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TitleSheetSignatory":
        return cls(
            role=str(data.get("role", "")),
            surname=str(data.get("surname", "")),
            signature=str(data.get("signature", "✓")),
            date=str(data.get("date", ""))
        )


@dataclass
class ApprovalBlock:
    """
    Onay Bloğu (Поле 3 — Гриф согласования / утверждения).
    ГОСТ Р 7.0.97 ve ГОСТ Р 21.101 Form 12 standardına göre sol veya sağ tarafta yer alır.
    """
    has_approval: bool = True
    approval_title: str = "СОГЛАСОВАНО"   # СОГЛАСОВАНО veya УТВЕРЖДАЮ
    role: str = "Главный инженер проекта"
    organization: str = "(наименование организации-генпроектировщика)"
    name: str = "И.О. Фамилия"
    date: str = "«___» ____________ 2026 г."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApprovalBlock":
        return cls(
            has_approval=bool(data.get("has_approval", True)),
            approval_title=str(data.get("approval_title", "СОГЛАСОВАНО")),
            role=str(data.get("role", "Главный инженер проекта")),
            organization=str(data.get("organization", "(наименование организации-генпроектировщика)")),
            name=str(data.get("name", "И.О. Фамилия")),
            date=str(data.get("date", "«___» ____________ 2026 г."))
        )


def build_default_title_sheet_signatories() -> List[TitleSheetSignatory]:
    """Standart örnek GOST Form 12 / Приложение С sorumlu kadrosu (Kurgusal)."""
    return [
        TitleSheetSignatory(role="Главный инженер", surname="Иванов И.И.", signature="✓", date=""),
        TitleSheetSignatory(role="Главный инженер проекта", surname="Петров П.П.", signature="✓", date=""),
        TitleSheetSignatory(role="Начальник отдела", surname="Сидоров С.С.", signature="✓", date=""),
    ]


def build_empty_title_sheet_signatories() -> List[TitleSheetSignatory]:
    """Boş sorumlu kadrosu."""
    return [
        TitleSheetSignatory(role="Главный инженер", surname="", signature="✓", date=""),
        TitleSheetSignatory(role="Главный инженер проекта", surname="", signature="✓", date=""),
    ]


@dataclass
class TitleSheetDocument:
    """
    ГОСТ Р 21.101-2020 Форма 12 (Приложение Р ve Приложение С) Başlık Sayfası Belgesi.
    """
    # Поле 1: Сокращенное / полное наименование вышестоящей организации (опционально)
    higher_org: str = ""

    # Поле 2: Логотип и полное наименование организации, подготовившей документ
    organization_name: str = "ООО «ПРОЕКТ-СТРОЙ»"
    has_logo: bool = False
    logo_image_path: Optional[str] = None

    # Поле 3: Гриф согласования / утверждения
    approval: ApprovalBlock = field(default_factory=ApprovalBlock)

    # Поле 4: Наименование объекта капитального строительства (прописными буквами)
    object_name: str = (
        "ПРОИЗВОДСТВЕННО-СКЛАДСКОЙ КОМПЛЕКС В ПРОМЫШЛЕННОМ ПАРКЕ «СЕВЕРНЫЙ»,\n"
        "РАСПОЛОЖЕННЫЙ ПО АДРЕСУ: МОСКОВСКАЯ ОБЛАСТЬ, Г.О. СОЛНЕЧНОГОРСК, ТЕР. ПРОМЗОНА-1,\n"
        "ЗЕМЕЛЬНЫЙ УЧАСТОК С КАДАСТРОВЫМ НОМЕРОМ 50:09:0000000:12345"
    )

    # Поле 5: Вид документации (ПРОЕКТНАЯ ДОКУМЕНТАЦИЯ / РАБОЧАЯ ДОКУМЕНТАЦИЯ)
    doc_type: str = "ПРОЕКТНАЯ ДОКУМЕНТАЦИЯ"

    # Поле 6: Наименование документа (раздел, подраздел, часть, книга...)
    doc_title: str = (
        "Раздел 5. Сведения об инженерном оборудовании, о сетях инженерно-технического обеспечения,\n"
        "перечень инженерно-технических мероприятий, содержание технологических решений\n\n"
        "Подраздел 4. Отопление, вентиляция и кондиционирование воздуха, тепловые сети\n\n"
        "Часть 2. Тепловые сети"
    )

    # Поле 7: Обозначение документа или тома
    doc_code: str = "2026-001-КМ"

    # Поле 8: Номер тома
    volume_number: str = "Том 1"

    # Поля 9, 10, 11: Блок подписей ответственных лиц
    signatories: List[TitleSheetSignatory] = field(default_factory=build_default_title_sheet_signatories)

    # Поле 12: Год выпуска документа
    year: str = "2026"

    # Поле 13: Дополнительные графы 20—22 на поле подшивки слева
    inv_num: str = ""       # Инв. № подл.
    inv_date: str = ""      # Подп. и дата
    inv_repl: str = ""      # Взам. инв. №

    def to_dict(self) -> Dict[str, Any]:
        return {
            "higher_org": self.higher_org,
            "organization_name": self.organization_name,
            "has_logo": self.has_logo,
            "logo_image_path": self.logo_image_path,
            "approval": self.approval.to_dict(),
            "object_name": self.object_name,
            "doc_type": self.doc_type,
            "doc_title": self.doc_title,
            "doc_code": self.doc_code,
            "volume_number": self.volume_number,
            "signatories": [s.to_dict() for s in self.signatories],
            "year": self.year,
            "inv_num": self.inv_num,
            "inv_date": self.inv_date,
            "inv_repl": self.inv_repl,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TitleSheetDocument":
        if not data:
            return cls.get_default_sample_document()

        raw_app = data.get("approval", {})
        approval = ApprovalBlock.from_dict(raw_app) if isinstance(raw_app, dict) else ApprovalBlock()

        raw_sigs = data.get("signatories", [])
        sigs = [TitleSheetSignatory.from_dict(s) for s in raw_sigs] if raw_sigs else build_default_title_sheet_signatories()

        return cls(
            higher_org=str(data.get("higher_org", "")),
            organization_name=str(data.get("organization_name", "ООО «ПРОЕКТ-СТРОЙ»")),
            has_logo=bool(data.get("has_logo", False)),
            logo_image_path=data.get("logo_image_path"),
            approval=approval,
            object_name=str(data.get("object_name", "")),
            doc_type=str(data.get("doc_type", "ПРОЕКТНАЯ ДОКУМЕНТАЦИЯ")),
            doc_title=str(data.get("doc_title", "")),
            doc_code=str(data.get("doc_code", "2026-001-КМ")),
            volume_number=str(data.get("volume_number", "Том 1")),
            signatories=sigs,
            year=str(data.get("year", "2026")),
            inv_num=str(data.get("inv_num", "")),
            inv_date=str(data.get("inv_date", "")),
            inv_repl=str(data.get("inv_repl", "")),
        )

    @classmethod
    def get_default_sample_document(cls) -> "TitleSheetDocument":
        """Приложение С / Рисунок С.1 kurgusal örnek şablonu."""
        return cls()

    @classmethod
    def get_empty_document(cls) -> "TitleSheetDocument":
        """Boş başlık sayfası şablonu."""
        return cls(
            higher_org="",
            organization_name="",
            has_logo=False,
            logo_image_path=None,
            approval=ApprovalBlock(has_approval=False, approval_title="СОГЛАСОВАНО", role="", organization="", name="", date=""),
            object_name="",
            doc_type="ПРОЕКТНАЯ ДОКУМЕНТАЦИЯ",
            doc_title="",
            doc_code="",
            volume_number="Том 1",
            signatories=build_empty_title_sheet_signatories(),
            year="2026",
            inv_num="",
            inv_date="",
            inv_repl="",
        )
