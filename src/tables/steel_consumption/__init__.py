"""
'Ведомость расхода стали' Tablo Paketi.
"""
from src.tables.steel_consumption.model import (
    SteelConsumptionItem, SteelConsumptionDocument, build_sample_steel_consumption
)
from src.tables.steel_consumption.config import (
    SteelConsumptionConfig, DEFAULT_STEEL_CONSUMPTION_CONFIG
)
from src.tables.steel_consumption.builder import create_steel_consumption_table
from src.tables.steel_consumption.validator import SteelConsumptionValidator
from src.tables.steel_consumption.module import SteelConsumptionModule
from src.models.registry import TableRegistry

# Modülü sistem kayıt defterine otomatik kaydet
_default_instance = SteelConsumptionModule()
TableRegistry.register(_default_instance, is_default=False)

def get_editor_widget_class():
    from src.tables.steel_consumption.editor import SteelConsumptionEditorWidget
    return SteelConsumptionEditorWidget

__all__ = [
    "SteelConsumptionItem",
    "SteelConsumptionDocument",
    "build_sample_steel_consumption",
    "SteelConsumptionConfig",
    "DEFAULT_STEEL_CONSUMPTION_CONFIG",
    "create_steel_consumption_table",
    "SteelConsumptionValidator",
    "SteelConsumptionModule",
    "get_editor_widget_class",
]
