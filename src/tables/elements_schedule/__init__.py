"""
'Ведомость элементов' Tablo Paketi.
"""
from src.tables.elements_schedule.model import (
    ElementPart, ScheduleItem, ElementsScheduleDocument, build_sample_items
)
from src.tables.elements_schedule.config import (
    ElementsColumnWidths, ElementsRowHeights, ElementsScheduleConfig, DEFAULT_ELEMENTS_CONFIG
)
from src.tables.elements_schedule.builder import create_elements_schedule_table
from src.tables.elements_schedule.validator import ElementsScheduleValidator
from src.tables.elements_schedule.module import ElementsScheduleModule
from src.models.registry import TableRegistry

# Modülü sistem kayıt defterine varsayılan olarak kaydet
_default_instance = ElementsScheduleModule()
TableRegistry.register(_default_instance, is_default=True)

def get_editor_widget_class():
    from src.tables.elements_schedule.editor import ElementsScheduleWidget
    return ElementsScheduleWidget

__all__ = [
    "ElementPart",
    "ScheduleItem",
    "ElementsScheduleDocument",
    "build_sample_items",
    "ElementsColumnWidths",
    "ElementsRowHeights",
    "ElementsScheduleConfig",
    "DEFAULT_ELEMENTS_CONFIG",
    "create_elements_schedule_table",
    "ElementsScheduleValidator",
    "ElementsScheduleModule",
    "get_editor_widget_class",
]
