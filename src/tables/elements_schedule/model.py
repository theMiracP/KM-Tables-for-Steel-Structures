"""
'Ведомость элементов' Veri Modelleri (Domain Models).
"""
from dataclasses import dataclass, field
from typing import List
from src.models.sketch import SectionSketch, SketchType

@dataclass
class ElementPart:
    """Tek bir kesit bileşeni (Поз. ve Состав)."""
    position_no: str = ""       # Поз. (örn: "1", "2" veya tek parçalılarda boş)
    composition: str = ""       # Состав (örn: "I 20K1", "-130 x 12", "∅ 70x4.0")

@dataclass
class ScheduleItem:
    """
    Ведомость элементов tablosundaki tek bir eleman satırı.
    Birden fazla parçadan oluşabilir (ör. Б3 ve К1'de 2 levha).
    """
    mark: str                             # Марка элемента (örn: "Б1", "Б2", "Б3", "К1")
    sketch: SectionSketch = field(default_factory=SectionSketch) # Эскиз
    parts: List[ElementPart] = field(default_factory=list)      # Поз. ve Состав parçaları
    force_a: str = ""                     # A, кН
    force_n: str = ""                     # N, кН
    force_m: str = ""                     # M, кН*м
    steel_grade: str = "С255-4"           # Наименование или марка металла
    note: str = ""                        # Примечание

@dataclass
class ElementsScheduleDocument:
    """
    Ведомость элементов tablosunun çalışma belgesi (Document Model).
    Kullanıcının kaydettiği, açtığı veya düzenlediği tüm tablo verisini temsil eder.
    """
    items: List[ScheduleItem] = field(default_factory=list)

def build_sample_items() -> List[ScheduleItem]:
    """Referans görseldeki standart örnek verileri döndürür."""
    return [
        ScheduleItem(
            mark="Б1",
            sketch=SectionSketch(SketchType.I_BEAM, symbol_text="I"),
            parts=[ElementPart("", "I 20K1")],
            force_a="85", force_n="45", force_m="11,5",
            steel_grade="С255-4"
        ),
        ScheduleItem(
            mark="Б2",
            sketch=SectionSketch(SketchType.RECT_TUBE, symbol_text="□"),
            parts=[ElementPart("", "140x100x6.0")],
            force_a="23", force_n="3", force_m="0",
            steel_grade="С255-4"
        ),
        ScheduleItem(
            mark="Б3",
            sketch=SectionSketch(SketchType.COMPOUND_BOX_WELDED, callout_1="1", callout_2="2"),
            parts=[
                ElementPart("1", "-130 x 12"),
                ElementPart("2", "-106 x 12"),
            ],
            force_a="2", force_n="30", force_m="16",
            steel_grade="С255-4"
        ),
        ScheduleItem(
            mark="Б4",
            sketch=SectionSketch(SketchType.ROUND_TUBE, symbol_text="○"),
            parts=[ElementPart("", "∅ 70x4.0")],
            force_a="0", force_n="70", force_m="0",
            steel_grade="С255-4"
        ),
        ScheduleItem(
            mark="Б5",
            sketch=SectionSketch(SketchType.RECT_TUBE, symbol_text="□"),
            parts=[ElementPart("", "200x160x10.0")],
            force_a="", force_n="", force_m="",
            steel_grade="С255-4"
        ),
        ScheduleItem(
            mark="К1",
            sketch=SectionSketch(SketchType.COMPOUND_BOX_WELDED, callout_1="1", callout_2="2"),
            parts=[
                ElementPart("1", "-130 x 12"),
                ElementPart("2", "-106 x 12"),
            ],
            force_a="5", force_n="40", force_m="0",
            steel_grade="С255-4"
        ),
        ScheduleItem(
            mark="К2",
            sketch=SectionSketch(SketchType.RECT_TUBE, symbol_text="□"),
            parts=[ElementPart("", "140x120x6.0")],
            force_a="10", force_n="10", force_m="0",
            steel_grade="С255-4"
        ),
    ]
