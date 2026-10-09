"""
'Ведомость элементов' Tablo Modülü (ElementsScheduleModule).
`TableModule` sözleşmesini uygulayan ilk somut mühendislik tablosu.
"""
from typing import Any, Optional
from PySide6.QtWidgets import QWidget

from src.contracts.table_module import TableModule, ValidationResult
from src.models.table import Table
from src.tables.elements_schedule.model import ElementsScheduleDocument, build_sample_items
from src.tables.elements_schedule.config import ElementsScheduleConfig, DEFAULT_ELEMENTS_CONFIG
from src.tables.elements_schedule.builder import create_elements_schedule_table
from src.tables.elements_schedule.validator import ElementsScheduleValidator

class ElementsScheduleModule(TableModule):
    def __init__(self, config: Optional[ElementsScheduleConfig] = None):
        self.config = config or DEFAULT_ELEMENTS_CONFIG

    @property
    def id(self) -> str:
        return "vedomost_elementov"

    @property
    def name(self) -> str:
        return "Ведомость элементов (ГОСТ 21.502 / КМ)"

    @property
    def category(self) -> str:
        return "КМ — Çelik Yapılar (ГОСТ 21.502)"

    @property
    def description(self) -> str:
        return "ГОСТ 21.502-2007 Çelik yapılar (КМ) eleman listesi tablosu."

    @property
    def supports_preview(self) -> bool:
        return True

    def create_default_document(self) -> ElementsScheduleDocument:
        return ElementsScheduleDocument(items=build_sample_items())

    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        from src.tables.elements_schedule.editor import ElementsScheduleWidget
        return ElementsScheduleWidget(parent=parent)

    def build_table(self, document: Any) -> Table:
        return create_elements_schedule_table(document, self.config)

    def validate(self, document: Any) -> ValidationResult:
        return ElementsScheduleValidator.validate(document)

    def default_export_filename(self, document: Any) -> str:
        return "Vedomost_Elementov.dxf"
