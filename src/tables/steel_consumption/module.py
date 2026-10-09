"""
KM Tablo Oluşturucu - 'Ведомость расхода стали' Modülü (SteelConsumptionModule).
TableModule sözleşmesini tam uygulayan ikinci bağımsız mühendislik tablosu modülü.
"""
from typing import Optional, Any
from PySide6.QtWidgets import QWidget

from src.contracts.table_module import TableModule, ValidationResult
from src.models.table import Table
from src.tables.steel_consumption.model import (
    SteelConsumptionDocument, build_sample_steel_consumption
)
from src.tables.steel_consumption.builder import create_steel_consumption_table
from src.tables.steel_consumption.validator import SteelConsumptionValidator


class SteelConsumptionModule(TableModule):
    """
    Ведомость расхода стали (ГОСТ 21.502) tablo türünün bağımsız modül tanımı.
    """

    @property
    def id(self) -> str:
        return "vedomost_raskhoda_stali"

    @property
    def name(self) -> str:
        return "Ведомость расхода стали (ГОСТ 21.502)"

    @property
    def category(self) -> str:
        return "КМ — Çelik Yapılar (ГОСТ 21.502)"

    @property
    def description(self) -> str:
        return "ГОСТ 21.502 uyarınca eleman bazında çelik profillere göre sarfiyat tablosu"

    @property
    def supports_preview(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        # Kullanıcı kararıyla Çelik Sarfiyat tablosu aktif arayüzden çıkarılmıştır (TASK-12)
        return False

    def create_default_document(self) -> SteelConsumptionDocument:
        return SteelConsumptionDocument(items=build_sample_steel_consumption())

    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        from src.tables.steel_consumption.editor import SteelConsumptionEditorWidget
        return SteelConsumptionEditorWidget(parent)

    def build_table(self, document: Any) -> Table:
        return create_steel_consumption_table(document)

    def validate(self, document: Any) -> ValidationResult:
        return SteelConsumptionValidator.validate(document)

    def default_export_filename(self, document: Any) -> str:
        return "vedomost_raskhoda_stali.dxf"
