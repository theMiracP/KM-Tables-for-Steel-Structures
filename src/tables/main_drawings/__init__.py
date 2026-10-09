"""
'Ведомость основных комплектов рабочих чертежей' Tablo Modül Paketi.
ГОСТ Р 21.101-2020 Form 2 temel çalışma çizimleri takımları tablosu (185 mm).
"""
from src.tables.main_drawings.model import (
    DrawingSetItem, MainDrawingsDocument, get_default_sample_items
)
from src.tables.main_drawings.config import (
    MainDrawingsConfig, MainDrawingsColumnWidths, MainDrawingsRowHeights,
    MainDrawingsTypography, DEFAULT_MAIN_DRAWINGS_CONFIG
)
from src.tables.main_drawings.builder import create_main_drawings_table, calculate_item_row_height
from src.tables.main_drawings.validator import MainDrawingsValidator
from src.tables.main_drawings.module import MainDrawingsModule
from src.models.registry import TableRegistry

# Modülü sistem kayıt defterine otomatik kaydet
_default_instance = MainDrawingsModule()
TableRegistry.register(_default_instance, is_default=False)

def get_editor_widget_class():
    from src.tables.main_drawings.editor import MainDrawingsEditorWidget
    return MainDrawingsEditorWidget

__all__ = [
    "DrawingSetItem",
    "MainDrawingsDocument",
    "get_default_sample_items",
    "MainDrawingsConfig",
    "MainDrawingsColumnWidths",
    "MainDrawingsRowHeights",
    "MainDrawingsTypography",
    "DEFAULT_MAIN_DRAWINGS_CONFIG",
    "create_main_drawings_table",
    "calculate_item_row_height",
    "MainDrawingsValidator",
    "MainDrawingsModule",
    "get_editor_widget_class",
]
