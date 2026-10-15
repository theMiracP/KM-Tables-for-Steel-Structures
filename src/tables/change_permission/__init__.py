"""
'Разрешение на внесение изменений (Форма 9)' Tablo Modül Paketi.
ГОСТ Р 21.101-2020 Form 9 Değişiklik İzni / Разрешение на внесение изменений (185 x 287 mm).
"""
from src.tables.change_permission.model import (
    ChangePermissionItem, ChangeSignatoryEntry, ChangePermissionDocument,
    build_default_change_signatories, build_empty_change_signatories,
    build_default_change_items
)
from src.tables.change_permission.config import (
    ChangePermissionConfig, ChangePermissionColumnWidths, REASON_CODES,
    DEFAULT_CHANGE_PERMISSION_CONFIG
)
from src.tables.change_permission.builder import (
    create_change_permission_table, calculate_change_item_row_height
)
from src.tables.change_permission.validator import ChangePermissionValidator
from src.tables.change_permission.module import ChangePermissionModule
from src.models.registry import TableRegistry

# Modülü sistem kayıt defterine otomatik kaydet
_default_instance = ChangePermissionModule()
TableRegistry.register(_default_instance, is_default=False)


def get_editor_widget_class():
    from src.tables.change_permission.editor import ChangePermissionEditorWidget
    return ChangePermissionEditorWidget


__all__ = [
    "ChangePermissionItem",
    "ChangeSignatoryEntry",
    "ChangePermissionDocument",
    "build_default_change_signatories",
    "build_empty_change_signatories",
    "build_default_change_items",
    "ChangePermissionConfig",
    "ChangePermissionColumnWidths",
    "REASON_CODES",
    "DEFAULT_CHANGE_PERMISSION_CONFIG",
    "create_change_permission_table",
    "calculate_change_item_row_height",
    "ChangePermissionValidator",
    "ChangePermissionModule",
    "get_editor_widget_class",
]
