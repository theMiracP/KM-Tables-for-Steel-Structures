"""
Soyut CAD Dışa Aktarıcı Arayüzü (Base Exporter).
İleride DWG veya diğer formatlar eklendiğinde aynı arayüz kullanılır.
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.config.sheet_config import LayoutConfig
from src.config.table_config import TableConfig
from src.models.table import Table

class BaseExporter(ABC):
    @abstractmethod
    def export(
        self,
        table: Table,
        output_path: str,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None
    ) -> bool:
        """Tabloyu dosyaya aktarır."""
        pass
