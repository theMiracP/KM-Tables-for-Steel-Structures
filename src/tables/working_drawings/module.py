"""
'Ведомость рабочих чертежей основного комплекта' Tablo Modülü (WorkingDrawingsModule).
`TableModule` sözleşmesini uygulayan ГОСТ Р 21.101-2020 Form 1 modülü.
"""
from typing import Any, Optional
from PySide6.QtWidgets import QWidget

from src.contracts.table_module import TableModule, ValidationResult
from src.models.table import Table
from src.tables.working_drawings.model import WorkingDrawingsDocument
from src.tables.working_drawings.config import WorkingDrawingsConfig, DEFAULT_WORKING_DRAWINGS_CONFIG
from src.tables.working_drawings.builder import create_working_drawings_table
from src.tables.working_drawings.validator import WorkingDrawingsValidator


class WorkingDrawingsModule(TableModule):
    def __init__(self, config: Optional[WorkingDrawingsConfig] = None):
        self.config = config or DEFAULT_WORKING_DRAWINGS_CONFIG

    @property
    def id(self) -> str:
        return "working_drawings"

    @property
    def name(self) -> str:
        return "Ведомость рабочих чертежей основного комплекта"

    @property
    def category(self) -> str:
        return "Общие данные — Рабочие чертежи (ГОСТ Р 21.101)"

    @property
    def description(self) -> str:
        return "ГОСТ Р 21.101-2020 Форма 1 çalışma çizimleri / pafta listesi tablosu (185 mm)"

    @property
    def supports_preview(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    def create_default_document(self) -> WorkingDrawingsDocument:
        return WorkingDrawingsDocument()

    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        from src.tables.working_drawings.editor import WorkingDrawingsEditorWidget
        return WorkingDrawingsEditorWidget(parent=parent)

    def build_table(self, document: Any) -> Table:
        if not isinstance(document, WorkingDrawingsDocument):
            document = WorkingDrawingsDocument.from_dict(document if isinstance(document, dict) else {})
        return create_working_drawings_table(document, self.config)

    def validate(self, document: Any) -> ValidationResult:
        if not isinstance(document, WorkingDrawingsDocument):
            document = WorkingDrawingsDocument.from_dict(document if isinstance(document, dict) else {})
        return WorkingDrawingsValidator.validate(document)

    def default_export_filename(self, document: Any) -> str:
        return "Vedomost_Rabochikh_Chertezhey_Form1.dxf"
