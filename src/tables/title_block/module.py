"""
'Основная надпись (Форма 3)' Tablo Modülü (TitleBlockModule).
`TableModule` sözleşmesini uygulayan ГОСТ Р 21.101 ana antet modülü.
"""
from typing import Any, Optional
from PySide6.QtWidgets import QWidget

from src.contracts.table_module import TableModule, ValidationResult
from src.models.table import Table
from src.tables.title_block.model import TitleBlockDocument
from src.tables.title_block.config import TitleBlockConfig, DEFAULT_TITLE_BLOCK_CONFIG
from src.tables.title_block.builder import create_title_block_table
from src.tables.title_block.validator import TitleBlockValidator


class TitleBlockModule(TableModule):
    def __init__(self, config: Optional[TitleBlockConfig] = None):
        self.config = config or DEFAULT_TITLE_BLOCK_CONFIG

    @property
    def id(self) -> str:
        return "title_block"

    @property
    def name(self) -> str:
        return "Основная надпись (Форма 3)"

    @property
    def category(self) -> str:
        return "Общие данные — Antet (ГОСТ Р 21.101)"

    @property
    def description(self) -> str:
        return "ГОСТ Р 21.101-2020 Форма 3 ana antet ve revizyon bloğu (185 x 55 mm)"

    @property
    def supports_preview(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    def create_default_document(self) -> TitleBlockDocument:
        return TitleBlockDocument()

    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        from src.tables.title_block.editor import TitleBlockEditorWidget
        return TitleBlockEditorWidget(parent=parent)

    def build_table(self, document: Any) -> Table:
        if not isinstance(document, TitleBlockDocument):
            document = TitleBlockDocument.from_dict(document if isinstance(document, dict) else {})
        return create_title_block_table(document, self.config)

    def validate(self, document: Any) -> ValidationResult:
        return TitleBlockValidator.validate(document)

    def default_export_filename(self, document: Any) -> str:
        code = getattr(document, "doc_code", "Form3_TitleBlock") or "Form3_TitleBlock"
        safe_code = code.replace("/", "_").replace("\\", "_").replace(" ", "_")
        return f"{safe_code}.dxf"
