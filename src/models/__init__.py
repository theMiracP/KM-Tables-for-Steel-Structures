from src.models.geometry import Point2D, Rect2D
from src.models.sketch import SketchType, SectionSketch, SketchPrimitive
from src.models.table import Table, TableCell, TableRow, TableColumn, TableLayoutInfo, HAlign, VAlign
from src.models.sheet import CalculatedLayout, SheetLayoutCalculator
from src.models.registry import TableRegistry

_LAZY_EXPORTS = {
    "ElementPart",
    "ScheduleItem",
    "ElementsScheduleDocument",
    "build_sample_items",
    "create_elements_schedule_table",
}

def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        import src.models.elements_schedule as _es
        return getattr(_es, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "Point2D",
    "Rect2D",
    "SketchType",
    "SectionSketch",
    "SketchPrimitive",
    "Table",
    "TableCell",
    "TableRow",
    "TableColumn",
    "TableLayoutInfo",
    "HAlign",
    "VAlign",
    "ElementPart",
    "ScheduleItem",
    "ElementsScheduleDocument",
    "build_sample_items",
    "create_elements_schedule_table",
    "CalculatedLayout",
    "SheetLayoutCalculator",
    "TableRegistry",
]
