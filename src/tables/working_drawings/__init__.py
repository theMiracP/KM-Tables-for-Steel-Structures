"""
'Ведомость рабочих чертежей основного комплекта' Tablo Modül Paketi.
ГОСТ Р 21.101-2020 Form 1 çalışma çizimleri / pafta listesi tablosu (185 mm).
"""
from src.tables.working_drawings.model import (
    WorkingDrawingItem, WorkingDrawingsDocument, get_default_sample_items
)
from src.tables.working_drawings.config import (
    WorkingDrawingsConfig, WorkingDrawingsColumnWidths, WorkingDrawingsRowHeights,
    WorkingDrawingsTypography, DEFAULT_WORKING_DRAWINGS_CONFIG
)
from src.tables.working_drawings.builder import (
    create_working_drawings_table, calculate_item_row_height
)
from src.tables.working_drawings.validator import WorkingDrawingsValidator
from src.tables.working_drawings.module import WorkingDrawingsModule
from src.models.registry import TableRegistry

# Modülü sistem kayıt defterine otomatik kaydet
_default_instance = WorkingDrawingsModule()
TableRegistry.register(_default_instance, is_default=False)


def get_editor_widget_class():
    from src.tables.working_drawings.editor import WorkingDrawingsEditorWidget
    return WorkingDrawingsEditorWidget


__all__ = [
    "WorkingDrawingItem",
    "WorkingDrawingsDocument",
    "get_default_sample_items",
    "WorkingDrawingsConfig",
    "WorkingDrawingsColumnWidths",
    "WorkingDrawingsRowHeights",
    "WorkingDrawingsTypography",
    "DEFAULT_WORKING_DRAWINGS_CONFIG",
    "create_working_drawings_table",
    "calculate_item_row_height",
    "WorkingDrawingsValidator",
    "WorkingDrawingsModule",
    "get_editor_widget_class",
]
