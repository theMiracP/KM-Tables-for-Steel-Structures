"""
ГОСТ Р 21.101-2020 Приложение Р и С (Форма 12) Başlık Sayfası Modülü (Title Sheet / Титульный лист).
"""
from src.models.registry import TableRegistry
from src.tables.title_sheet.config import TitleSheetConfig, DEFAULT_TITLE_SHEET_CONFIG
from src.tables.title_sheet.model import (
    TitleSheetDocument, TitleSheetSignatory, ApprovalBlock,
    build_default_title_sheet_signatories, build_empty_title_sheet_signatories
)
from src.tables.title_sheet.builder import create_title_sheet_table
from src.tables.title_sheet.validator import TitleSheetValidator
from src.tables.title_sheet.module import TitleSheetModule
from src.tables.title_sheet.editor import TitleSheetEditorWidget

# Modülü TableRegistry'ye otomatik kaydet
TableRegistry.register(TitleSheetModule())

__all__ = [
    "TitleSheetConfig",
    "DEFAULT_TITLE_SHEET_CONFIG",
    "TitleSheetDocument",
    "TitleSheetSignatory",
    "ApprovalBlock",
    "build_default_title_sheet_signatories",
    "build_empty_title_sheet_signatories",
    "create_title_sheet_table",
    "TitleSheetValidator",
    "TitleSheetModule",
    "TitleSheetEditorWidget",
]
