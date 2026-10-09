"""
Modüler Tablo Mimarisi, TableRegistry ve Gelecekteki Tablo Entegrasyonu Testleri.
"""
import sys
import pytest
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from src.contracts.table_module import TableModule, ValidationResult
from src.models.registry import TableRegistry
from src.models.table import Table, TableCell, TableRow
from src.tables.elements_schedule import (
    ElementsScheduleModule,
    ElementsScheduleDocument,
    create_elements_schedule_table,
    ElementsScheduleValidator,
)

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


# ---------------------------------------------------------------------------
# 1. TableRegistry Birim Testleri
# ---------------------------------------------------------------------------
def test_table_registry_basic_operations():
    default_mod = TableRegistry.get_default()
    assert default_mod is not None
    assert default_mod.id == "vedomost_elementov"

    mod = TableRegistry.get("vedomost_elementov")
    assert mod is default_mod

    all_mods = TableRegistry.all()
    assert any(m.id == "vedomost_elementov" for m in all_mods)


# ---------------------------------------------------------------------------
# 2. ElementsScheduleModule Sözleşme Testleri
# ---------------------------------------------------------------------------
def test_elements_schedule_module_contract(qapp):
    module = ElementsScheduleModule()

    # Identity
    assert module.id == "vedomost_elementov"
    assert "Ведомость элементов" in module.name

    # Document
    doc = module.create_default_document()
    assert isinstance(doc, ElementsScheduleDocument)
    assert len(doc.items) > 0

    # Editor
    editor = module.create_editor()
    assert editor is not None
    assert hasattr(editor, "document_changed")
    assert hasattr(editor, "get_document")
    assert hasattr(editor, "set_document")

    # Builder
    table = module.build_table(doc)
    assert isinstance(table, Table)
    assert len(table.rows) > 2  # Başlıklar + veri satırları
    assert len(table.columns) == 9

    # Validator
    val_res = module.validate(doc)
    assert isinstance(val_res, ValidationResult)
    assert val_res.is_valid

    # Export filename
    fname = module.default_export_filename(doc)
    assert fname.endswith(".dxf")


# ---------------------------------------------------------------------------
# 3. Gelecekte İkinci Tablo Ekleme Testi (FUTURE TEST)
# "Yeni tablo eklemek için MainWindow'a dokunmak gerekiyor mu?"
# ---------------------------------------------------------------------------
class DummyTestTableModule(TableModule):
    """
    Test amaçlı ikinci bir mini tablo modülü.
    MainWindow koduna tek bir satır bile eklemeden sisteme dahil olmalıdır.
    """
    @property
    def id(self) -> str:
        return "dummy_test_table"

    @property
    def name(self) -> str:
        return "Тестовая Таблица (Dummy GOST)"

    def create_default_document(self):
        return {"records": ["Item A", "Item B"]}

    def create_editor(self, parent=None):
        w = QWidget(parent)
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Dummy Editor Widget"))
        return w

    def build_table(self, document):
        t = Table(title="Тестовая Таблица")
        t.add_column("col1", "Parametre", 60.0)
        t.add_column("col2", "Değer", 60.0)
        t.add_row([TableCell(text="Kayıt 1"), TableCell(text="100")])
        t.add_row([TableCell(text="Kayıt 2"), TableCell(text="200")])
        return t

    def validate(self, document):
        return ValidationResult(is_valid=True)

    def default_export_filename(self, document):
        return "Dummy_Test.dxf"


def test_add_second_table_without_modifying_mainwindow(qapp):
    """
    Kanıt: MainWindow'a dokunmadan yeni bir TableModule sisteme register edilir,
    ve MainWindow bu yeni tabloyu otomatik olarak yükleyip çalıştırır.
    """
    from src.ui.app import KmMainWindow

    # 1. Yeni modülü Registry'ye kaydet
    dummy_mod = DummyTestTableModule()
    TableRegistry.register(dummy_mod)

    try:
        # 2. MainWindow'u başlat
        window = KmMainWindow()

        # 3. MainWindow'un ComboBox'ında yeni tablonun listelendiğini doğrula
        combo = window.cb_table_type
        found_idx = -1
        for i in range(combo.count()):
            if combo.itemData(i) == "dummy_test_table":
                found_idx = i
                break

        assert found_idx >= 0, "Yeni tablo MainWindow ComboBox'ına otomatik eklenmeli!"

        # 4. Kullanıcı gibi ComboBox'tan yeni tabloyu seç
        combo.setCurrentIndex(found_idx)

        # 5. MainWindow'un aktif modülünün değiştiğini doğrula
        assert window.active_module.id == "dummy_test_table"
        assert window.active_module.name == "Тестовая Таблица (Dummy GOST)"

        # 6. Tablo render nesnesinin yeni modülün tablosu olduğunu doğrula
        assert window.current_table.title == "Тестовая Таблица"
        assert len(window.current_table.columns) == 2

        # 7. CAD tuvalinin yeni tabloyu hatasız çizdiğini doğrula
        assert window.canvas.scene() is not None

        # 8. DXF export adının yeni modülden geldiğini doğrula
        export_name = window.active_module.default_export_filename(window.current_document)
        assert export_name == "Dummy_Test.dxf"

    finally:
        # Test sonrası temizlik
        if "dummy_test_table" in TableRegistry._modules:
            del TableRegistry._modules["dummy_test_table"]
