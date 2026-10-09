"""
Ortak Tablo Modülü Sözleşmesi (Table Module Contract).
Yeni eklenecek mühendislik/GOST tablolarının uyması gereken temel arayüz.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, TYPE_CHECKING
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from src.models.table import Table

@dataclass
class ValidationResult:
    """Genel tablo veri doğrulama sonucu."""
    is_valid: bool = True
    messages: List[str] = field(default_factory=list)

    @property
    def summary_message(self) -> str:
        if self.is_valid:
            return "Tüm veriler geçerli."
        return " | ".join(self.messages)


class TableModule(ABC):
    """
    Tüm mühendislik tabloları için temel modül sözleşmesi.
    Her tablo türü bu sınıfı miras alarak kendi özel veri modelini,
    editörünü, doğrulayıcısını ve generic Table dönüştürücüsünü tanımlar.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Tablonun benzersiz sistem kimliği (örn: 'vedomost_elementov')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Kullanıcı arayüzünde görüntülenecek başlık (örn: 'Ведомость элементов')."""
        pass

    @property
    def category(self) -> str:
        """Tablonun ait olduğu mühendislik disiplini/GOST kategorisi."""
        return "КМ — Çelik Yapılar (ГОСТ 21.502)"

    @property
    def description(self) -> str:
        """Tablo hakkında açıklama veya GOST standardı referansı."""
        return ""

    @property
    def supports_preview(self) -> bool:
        """Tablonun 2D CAD çizim önizlemesi destekleyip desteklemediği."""
        return True

    @property
    def is_active(self) -> bool:
        """Modülün aktif kullanıcı arayüzü listelerinde yer alıp almayacağı."""
        return True

    @abstractmethod
    def create_default_document(self) -> Any:
        """Tablo için varsayılan/örnek başlangıç verisini (Document) üretir."""
        pass

    @abstractmethod
    def create_editor(self, parent: Optional[QWidget] = None) -> QWidget:
        """
        Tabloya özel kullanıcı veri giriş arayüzünü (Editor Widget) üretir.
        Dönen widget `document_changed` sinyaline ve
        `get_document()` / `set_document(doc)` metotlarına sahip olmalıdır.
        """
        pass

    @abstractmethod
    def build_table(self, document: Any) -> Any:
        """
        Tablo verisini (Document) alıp CAD önizleme tuvali ve DXF dışa aktarıcısı
        tarafından kullanılan genel `Table` (Render Model) nesnesine dönüştürür.
        """
        pass

    @abstractmethod
    def validate(self, document: Any) -> ValidationResult:
        """Tablo verilerini mühendislik kurallarına göre doğrular."""
        pass

    def default_export_filename(self, document: Any) -> str:
        """Dışa aktarma dosyasının varsayılan adı."""
        return f"{self.id}.dxf"
