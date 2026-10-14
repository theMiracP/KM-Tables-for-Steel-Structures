"""
UI v2 Yeni Özellikler Entegrasyon Testleri (Items 2.1, 2.3, 3.2, 4.1, 4.2).
"""
import os
import pytest
from PySide6.QtWidgets import QApplication

from src.ui_v2.window import KmLinearMainWindow
from src.tables.elements_schedule.model import ScheduleItem, ElementsScheduleDocument
from src.tables.title_block.model import TitleBlockDocument
from src.services.profile_database import GostProfileDatabase


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_window_initialization_and_services(qapp):
    win = KmLinearMainWindow()
    assert win.project_manager is not None
    assert win.undo_manager is not None
    assert win.pdf_exporter is not None
    assert len(win.module_documents) >= 5
    assert "vedomost_elementov" in win.module_documents
    assert "title_block" in win.module_documents
    win.close()


def test_title_block_synchronization(qapp):
    """Item 3.2: Title block metadata synchronization across all tables and layout configs."""
    win = KmLinearMainWindow()

    # Title block modülüne geç
    win._switch_to_module("title_block")
    doc: TitleBlockDocument = win.current_document
    doc.company_name = "TEST STEEL CORP"
    doc.project_name = "INDUSTRIAL WAREHOUSE 100x40"

    # Doküman değişikliğini tetikle
    win._on_document_edited(doc)

    # layout_config ve diğer tüm modül layout_config'lerinde güncellendiğini doğrula
    assert win.layout_config.title_block_doc.company_name == "TEST STEEL CORP"
    assert win.layout_config.title_block_doc.project_name == "INDUSTRIAL WAREHOUSE 100x40"

    # elements_schedule modülüne geçildiğinde antetin güncel kaldığını doğrula
    win._switch_to_module("vedomost_elementov")
    assert win.layout_config.title_block_doc.company_name == "TEST STEEL CORP"
    win.close()


def test_undo_redo_in_window(qapp):
    """Item 4.2: Undo / Redo infrastructure."""
    win = KmLinearMainWindow()
    win._switch_to_module("vedomost_elementov")

    doc_orig = win.current_document
    orig_count = len(doc_orig.items)

    # Yeni satır ekle
    win.editor_wrapper.active_editor._add_row()
    assert len(win.current_document.items) == orig_count + 1
    assert win.undo_manager.can_undo()

    # Undo yap (Ctrl+Z)
    win.undo_manager.undo()
    assert len(win.current_document.items) == orig_count
    assert win.undo_manager.can_redo()

    # Redo yap (Ctrl+Y)
    win.undo_manager.redo()
    assert len(win.current_document.items) == orig_count + 1
    win.close()


def test_project_save_load_lifecycle(qapp, tmp_path):
    """Item 4.1: Native project format (.kmproj)."""
    win = KmLinearMainWindow()
    win._switch_to_module("title_block")
    tb_doc: TitleBlockDocument = win.current_document
    tb_doc.company_name = "PROJECT SAVE CORP"
    win._on_document_edited(tb_doc)

    proj_file = str(tmp_path / "test_proj.kmproj")
    win.current_project_path = proj_file
    win._save_project()
    assert os.path.exists(proj_file)
    assert os.path.getsize(proj_file) > 100

    # Yeni proje başlat (sıfırla)
    win._new_project()
    assert win.layout_config.title_block_doc.company_name != "PROJECT SAVE CORP"

    # Projeyi geri yükle
    proj_data = win.project_manager.load_from_file(proj_file)
    win.module_documents = proj_data["module_documents"]
    win.module_layout_configs = proj_data["module_layout_configs"]
    win.current_project_path = proj_file
    win._switch_to_module(proj_data["active_module_id"])

    assert win.module_documents["title_block"].company_name == "PROJECT SAVE CORP"
    win.close()


def test_pdf_export_from_window(qapp, tmp_path):
    """Item 2.3: Vector PDF Export."""
    win = KmLinearMainWindow()
    pdf_out = str(tmp_path / "window_export.pdf")
    success = win.pdf_exporter.export_sheet(
        win.current_table,
        pdf_out,
        win.table_config,
        win.layout_config
    )
    assert success is True
    assert os.path.exists(pdf_out)
    assert os.path.getsize(pdf_out) > 1000
    win.close()


def test_profile_picker_integration(qapp):
    """Item 2.1: Profile picker action in ElementsScheduleWidget."""
    win = KmLinearMainWindow()
    win._switch_to_module("vedomost_elementov")
    editor = win.editor_wrapper.active_editor
    assert hasattr(editor, "btn_profile_picker")
    assert hasattr(editor, "_open_profile_picker")
    win.close()
