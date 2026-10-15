"""
'Титульный лист (Форма 12, Приложение С)' Tablo Modülü (TitleSheetModule).
`TableModule` sözleşmesini uygulayan ГОСТ Р 21.101-2020 Form 12 / Приложение С modülü.
"""
from typing import Any, Optional
from PySide6.QtWidgets import QWidget

from src.contracts.table_module import TableModule, ValidationResult
from src.models.table import Table
from src.tables.title_sheet.model import TitleSheetDocument
from src.tables.title_sheet.config import TitleSheetConfig, DEFAULT_TITLE_SHEET_CONFIG
from src.tables.title_sheet.builder import create_title_sheet_table
from src.tables.title_sheet.validator import TitleSheetValidator


class TitleSheetModule(TableModule):
    def __init__(self, config: Optional[TitleSheetConfig] = None):
        self.config = config or DEFAULT_TITLE_SHEET_CONFIG

    @property
    def id(self) -> str:
        return "title_sheet"

    @property
    def name(self) -> str:
        return "Титульный лист (Форма 12, Приложение С)"

    @property
    def category(self) -> str:
        return "Общие данные — Титульный лист (ГОСТ Р 21.101)"

    @property
    def description(self) -> str:
        return "ГОСТ Р 21.101-2020 Форма 12 / Приложение С Başlık Sayfası / Титульный лист (185 x 287 mm, Word & CAD Export)"

    @property
    def supports_preview(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    def create_default_document(self) -> TitleSheetDocument:
        return TitleSheetDocument.get_default_sample_document()

    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        from src.tables.title_sheet.editor import TitleSheetEditorWidget
        return TitleSheetEditorWidget(parent=parent)

    def build_table(self, document: Any) -> Table:
        if not isinstance(document, TitleSheetDocument):
            document = TitleSheetDocument.from_dict(document if isinstance(document, dict) else {})
        return create_title_sheet_table(document, self.config)

    def validate(self, document: Any) -> ValidationResult:
        if not isinstance(document, TitleSheetDocument):
            document = TitleSheetDocument.from_dict(document if isinstance(document, dict) else {})
        return TitleSheetValidator.validate(document)

    def default_export_filename(self, document: Any) -> str:
        code = getattr(document, "doc_code", "2026-001-KM") or "2026-001-KM"
        safe_code = str(code).replace("/", "_").replace("\\", "_").replace(" ", "_")
        return f"Titulny_List_{safe_code}.dxf"

    def default_docx_filename(self, document: Any) -> str:
        code = getattr(document, "doc_code", "2026-001-KM") or "2026-001-KM"
        safe_code = str(code).replace("/", "_").replace("\\", "_").replace(" ", "_")
        return f"Titulny_List_{safe_code}.docx"
