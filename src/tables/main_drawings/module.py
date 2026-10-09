"""
'Ведомость основных комплектов рабочих чертежей' Tablo Modülü (MainDrawingsModule).
`TableModule` sözleşmesini uygulayan ГОСТ Р 21.101-2020 Form 2 modülü.
"""
from typing import Any, Optional
from PySide6.QtWidgets import QWidget

from src.contracts.table_module import TableModule, ValidationResult
from src.models.table import Table
from src.tables.main_drawings.model import MainDrawingsDocument
from src.tables.main_drawings.config import MainDrawingsConfig, DEFAULT_MAIN_DRAWINGS_CONFIG
from src.tables.main_drawings.builder import create_main_drawings_table
from src.tables.main_drawings.validator import MainDrawingsValidator


class MainDrawingsModule(TableModule):
    def __init__(self, config: Optional[MainDrawingsConfig] = None):
        self.config = config or DEFAULT_MAIN_DRAWINGS_CONFIG

    @property
    def id(self) -> str:
        return "main_drawings"

    @property
    def name(self) -> str:
        return "Ведомость основных комплектов рабочих чертежей"

    @property
    def category(self) -> str:
        return "Общие данные — Çizim Takımları (ГОСТ Р 21.101)"

    @property
    def description(self) -> str:
        return "ГОСТ Р 21.101-2020 Форма 2 temel çalışma çizimleri takımları tablosu (185 mm)"

    @property
    def supports_preview(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    def create_default_document(self) -> MainDrawingsDocument:
        return MainDrawingsDocument()

    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        from src.tables.main_drawings.editor import MainDrawingsEditorWidget
        return MainDrawingsEditorWidget(parent=parent)

    def build_table(self, document: Any) -> Table:
        if not isinstance(document, MainDrawingsDocument):
            document = MainDrawingsDocument.from_dict(document if isinstance(document, dict) else {})
        return create_main_drawings_table(document, self.config)

    def validate(self, document: Any) -> ValidationResult:
        if not isinstance(document, MainDrawingsDocument):
            document = MainDrawingsDocument.from_dict(document if isinstance(document, dict) else {})
        return MainDrawingsValidator.validate(document)

    def default_export_filename(self, document: Any) -> str:
        return "Vedomost_Osnovnykh_Komplektov_Form2.dxf"
