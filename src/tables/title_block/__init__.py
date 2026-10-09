"""
'Основная надпись (Форма 3)' Tablo Modül Paketi.
ГОСТ Р 21.101-2020 Form 3 ana antet ve revizyon bloğu (185 x 55 mm).
"""
from src.tables.title_block.model import (
    SignatoryEntry, RevisionEntry, TitleBlockDocument,
    build_default_signatories, build_default_revisions
)
from src.tables.title_block.config import (
    TitleBlockConfig, TitleBlockColumnWidths, TitleBlockRowHeights, DEFAULT_TITLE_BLOCK_CONFIG
)
from src.tables.title_block.builder import create_title_block_table
from src.tables.title_block.validator import TitleBlockValidator
from src.tables.title_block.module import TitleBlockModule
from src.models.registry import TableRegistry

# Modülü sistem kayıt defterine otomatik kaydet
_default_instance = TitleBlockModule()
TableRegistry.register(_default_instance, is_default=False)

def get_editor_widget_class():
    from src.tables.title_block.editor import TitleBlockEditorWidget
    return TitleBlockEditorWidget

__all__ = [
    "SignatoryEntry",
    "RevisionEntry",
    "TitleBlockDocument",
    "build_default_signatories",
    "build_default_revisions",
    "TitleBlockConfig",
    "TitleBlockColumnWidths",
    "TitleBlockRowHeights",
    "DEFAULT_TITLE_BLOCK_CONFIG",
    "create_title_block_table",
    "TitleBlockValidator",
    "TitleBlockModule",
    "get_editor_widget_class",
]
