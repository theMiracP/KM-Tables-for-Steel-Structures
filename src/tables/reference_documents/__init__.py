"""
'Ведомость ссылочных и прилагаемых документов' Tablo Modül Paketi.
ГОСТ Р 21.101-2020 Form 2 referans ve ek dokümanlar tablosu (185 mm).
"""
from src.tables.reference_documents.model import (
    ReferenceDocItem, ReferenceDocsDocument, StandardLibraryItem
)
from src.tables.reference_documents.config import (
    ReferenceDocsConfig, ReferenceDocsColumnWidths, ReferenceDocsRowHeights,
    DEFAULT_REFERENCE_DOCS_CONFIG
)
from src.tables.reference_documents.library import StandardsLibraryManager, standards_library
from src.tables.reference_documents.builder import create_reference_docs_table
from src.tables.reference_documents.validator import ReferenceDocsValidator
from src.tables.reference_documents.module import ReferenceDocsModule
from src.models.registry import TableRegistry

# Modülü sistem kayıt defterine otomatik kaydet
_default_instance = ReferenceDocsModule()
TableRegistry.register(_default_instance, is_default=False)

def get_editor_widget_class():
    from src.tables.reference_documents.editor import ReferenceDocsEditorWidget
    return ReferenceDocsEditorWidget

__all__ = [
    "ReferenceDocItem",
    "ReferenceDocsDocument",
    "StandardLibraryItem",
    "ReferenceDocsConfig",
    "ReferenceDocsColumnWidths",
    "ReferenceDocsRowHeights",
    "DEFAULT_REFERENCE_DOCS_CONFIG",
    "StandardsLibraryManager",
    "standards_library",
    "create_reference_docs_table",
    "ReferenceDocsValidator",
    "ReferenceDocsModule",
    "get_editor_widget_class",
]
