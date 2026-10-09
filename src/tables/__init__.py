"""
KM Tablo Modülleri Paketi.
Sisteme kayıtlı tablo modüllerini yükler.
"""
from src.tables.elements_schedule import ElementsScheduleModule
from src.tables.steel_consumption import SteelConsumptionModule
from src.tables.title_block import TitleBlockModule
from src.tables.reference_documents import ReferenceDocsModule
from src.tables.main_drawings import MainDrawingsModule
from src.tables.working_drawings import WorkingDrawingsModule

__all__ = [
    "ElementsScheduleModule",
    "SteelConsumptionModule",
    "TitleBlockModule",
    "ReferenceDocsModule",
    "MainDrawingsModule",
    "WorkingDrawingsModule",
]

