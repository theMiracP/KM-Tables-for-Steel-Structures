"""
'Ведомость ссылочных и прилагаемых документов' Tablo Modülü (ReferenceDocsModule).
`TableModule` sözleşmesini uygulayan ГОСТ Р 21.101-2020 Form 2 modülü.
"""
from typing import Any, Optional
from PySide6.QtWidgets import QWidget

from src.contracts.table_module import TableModule, ValidationResult
from src.models.table import Table
from src.tables.reference_documents.model import ReferenceDocsDocument
from src.tables.reference_documents.config import ReferenceDocsConfig, DEFAULT_REFERENCE_DOCS_CONFIG
from src.tables.reference_documents.builder import create_reference_docs_table
from src.tables.reference_documents.validator import ReferenceDocsValidator
from src.tables.reference_documents.library import standards_library


class ReferenceDocsModule(TableModule):
    def __init__(self, config: Optional[ReferenceDocsConfig] = None):
        self.config = config or DEFAULT_REFERENCE_DOCS_CONFIG

    @property
    def id(self) -> str:
        return "reference_documents"

    @property
    def name(self) -> str:
        return "Ведомость ссылочных и прилагаемых документов"

    @property
    def category(self) -> str:
        return "Общие данные — Dokümanlar (ГОСТ Р 21.101)"

    @property
    def description(self) -> str:
        return "ГОСТ Р 21.101-2020 Форма 2 referans ve ek dokümanlar tablosu (185 mm)"

    @property
    def supports_preview(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    def create_default_document(self) -> ReferenceDocsDocument:
        return standards_library.build_default_document()

    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        from src.tables.reference_documents.editor import ReferenceDocsEditorWidget
        return ReferenceDocsEditorWidget(parent=parent)

    def build_table(self, document: Any) -> Table:
        if not isinstance(document, ReferenceDocsDocument):
            document = ReferenceDocsDocument.from_dict(document if isinstance(document, dict) else {})
        return create_reference_docs_table(document, self.config)

    def validate(self, document: Any) -> ValidationResult:
        if not isinstance(document, ReferenceDocsDocument):
            document = ReferenceDocsDocument.from_dict(document if isinstance(document, dict) else {})
        return ReferenceDocsValidator.validate(document)

    def default_export_filename(self, document: Any) -> str:
        return "Vedomost_Dokumentov_Form2.dxf"
