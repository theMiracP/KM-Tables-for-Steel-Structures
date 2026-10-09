"""
KM Tablo Oluşturucu - UI Paketi.
PEP 562 lazy loading ile dairesel bağımlılıklar önlenir.
"""
from src.ui import theme
from src.ui import widgets
from src.ui.i18n import i18n
from src.ui.preview_canvas import CadGraphicsView

def __getattr__(name: str):
    if name in ("KmMainWindow", "KmTableApp"):
        from src.ui.app import KmMainWindow
        return KmMainWindow
    if name in ("ElementsScheduleWidget", "InputPanel"):
        from src.tables.elements_schedule.editor import ElementsScheduleWidget
        return ElementsScheduleWidget
    if name == "PreviewCanvas":
        return CadGraphicsView
    raise AttributeError(f"module 'src.ui' has no attribute '{name}'")

__all__ = [
    "KmMainWindow",
    "KmTableApp",
    "CadGraphicsView",
    "PreviewCanvas",
    "ElementsScheduleWidget",
    "theme",
    "widgets",
    "i18n",
]
