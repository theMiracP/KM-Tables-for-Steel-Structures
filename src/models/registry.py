"""
Modüler Tablo Kayıt Merkezi (TableRegistry).
Sisteme kayıtlı tüm TableModule örneklerini yönetir.
"""
from typing import Dict, List, Optional, Union, Callable
from src.contracts.table_module import TableModule

class TableRegistry:
    _modules: Dict[str, TableModule] = {}
    _default_id: Optional[str] = None

    @classmethod
    def register(
        cls,
        module_or_id: Union[TableModule, str],
        display_name: str = "",
        builder_func: Optional[Callable] = None,
        description: str = "",
        is_default: bool = False
    ) -> None:
        """
        Yeni bir tablo modülünü sisteme kaydeder.
        Hem `TableModule` nesnelerini hem de eski `(table_id, display_name, builder_func)` imzasını destekler.
        """
        if isinstance(module_or_id, TableModule):
            mod = module_or_id
            cls._modules[mod.id] = mod
            if is_default or cls._default_id is None:
                cls._default_id = mod.id
        else:
            # Eski imza için hafif wrapper
            table_id = str(module_or_id)
            # Eğer zaten bir TableModule olarak kayıtlıysa ezme
            if table_id not in cls._modules:
                class _LegacyModule(TableModule):
                    @property
                    def id(self) -> str:
                        return table_id
                    @property
                    def name(self) -> str:
                        return display_name or table_id
                    @property
                    def description(self) -> str:
                        return description
                    def create_default_document(self):
                        return []
                    def create_editor(self, parent=None):
                        from PySide6.QtWidgets import QWidget
                        return QWidget(parent)
                    def build_table(self, doc):
                        return builder_func(doc) if builder_func else None
                    def validate(self, doc):
                        from src.contracts.table_module import ValidationResult
                        return ValidationResult(is_valid=True)
                cls._modules[table_id] = _LegacyModule()
                if is_default or cls._default_id is None:
                    cls._default_id = table_id

    @classmethod
    def get(cls, module_id: str) -> Optional[TableModule]:
        """Kimliği verilen tablo modülünü döndürür."""
        return cls._modules.get(module_id)

    @classmethod
    def get_default(cls) -> Optional[TableModule]:
        """Varsayılan aktif tablo modülünü döndürür."""
        if cls._default_id and cls._default_id in cls._modules:
            return cls._modules[cls._default_id]
        if cls._modules:
            return next(iter(cls._modules.values()))
        return None

    @classmethod
    def all(cls) -> List[TableModule]:
        """Kayıtlı tüm tablo modüllerini döndürür."""
        return list(cls._modules.values())

    @classmethod
    def clear(cls) -> None:
        cls._modules.clear()
        cls._default_id = None

    # Geriye dönük uyumluluk yardımcıları
    @classmethod
    def get_registered_tables(cls) -> List[Dict[str, any]]:
        return [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "builder": getattr(m, "build_table", None),
            }
            for m in cls._modules.values()
        ]

    @classmethod
    def get_display_names(cls) -> List[str]:
        return [m.name for m in cls._modules.values()]

    @classmethod
    def get_id_by_display_name(cls, name: str) -> Optional[str]:
        for m in cls._modules.values():
            if m.name == name:
                return m.id
        return None
