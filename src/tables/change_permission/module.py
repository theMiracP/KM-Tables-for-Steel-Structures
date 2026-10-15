"""
'Разрешение на внесение изменений (Форма 9)' Tablo Modülü (ChangePermissionModule).
`TableModule` sözleşmesini uygulayan ГОСТ Р 21.101-2020 Form 9 modülü.
"""
from typing import Any, Optional
from PySide6.QtWidgets import QWidget

from src.contracts.table_module import TableModule, ValidationResult
from src.models.table import Table
from src.tables.change_permission.model import ChangePermissionDocument
from src.tables.change_permission.config import ChangePermissionConfig, DEFAULT_CHANGE_PERMISSION_CONFIG
from src.tables.change_permission.builder import create_change_permission_table
from src.tables.change_permission.validator import ChangePermissionValidator


class ChangePermissionModule(TableModule):
    def __init__(self, config: Optional[ChangePermissionConfig] = None):
        self.config = config or DEFAULT_CHANGE_PERMISSION_CONFIG

    @property
    def id(self) -> str:
        return "change_permission"

    @property
    def name(self) -> str:
        return "Разрешение на внесение изменений (Форма 9)"

    @property
    def category(self) -> str:
        return "Общие данные — Разрешение на изменения (ГОСТ Р 21.101)"

    @property
    def description(self) -> str:
        return "ГОСТ Р 21.101-2020 Форма 9 Değişiklik İzni / Разрешение на внесение изменений (185 x 287 mm)"

    @property
    def supports_preview(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    def create_default_document(self) -> ChangePermissionDocument:
        return ChangePermissionDocument.get_default_sample_document()

    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        from src.tables.change_permission.editor import ChangePermissionEditorWidget
        return ChangePermissionEditorWidget(parent=parent)

    def build_table(self, document: Any) -> Table:
        if not isinstance(document, ChangePermissionDocument):
            document = ChangePermissionDocument.from_dict(document if isinstance(document, dict) else {})
        return create_change_permission_table(document, self.config)

    def validate(self, document: Any) -> ValidationResult:
        if not isinstance(document, ChangePermissionDocument):
            document = ChangePermissionDocument.from_dict(document if isinstance(document, dict) else {})
        return ChangePermissionValidator.validate(document)

    def default_export_filename(self, document: Any) -> str:
        res_no = getattr(document, "resolution_number", "Form9") or "Form9"
        safe_no = str(res_no).replace("/", "_").replace("\\", "_").replace(" ", "_")
        return f"Razreshenie_{safe_no}.dxf"
