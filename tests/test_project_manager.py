"""
Test Suite: KM Layout Tables Studio - Proje Dosyası (.kmproj) Testleri.
Tüm modüllerin, Form 3 antetinin ve pafta ayarlarının JSON bütünlüğünü ve geri yüklenmesini doğrular.
"""
import os
import tempfile
import pytest

from src.services.project_manager import ProjectManager, KMPROJ_FILE_EXT
from src.tables.elements_schedule.model import ElementsScheduleDocument, ScheduleItem, ElementPart
from src.models.sketch import SketchType
from src.tables.title_block.model import TitleBlockDocument, SignatoryEntry
from src.config.sheet_config import DEFAULT_LAYOUT_CONFIG, SheetSize, SheetOrientation


def test_project_manager_save_and_load_roundtrip():
    """Tüm proje verilerinin .kmproj dosyasına hatasız yazılıp okunduğunu doğrular."""
    with tempfile.TemporaryDirectory() as tmpdir:
        proj_file = os.path.join(tmpdir, "Fabrika_KM_Test.kmproj")

        # 1. Test verilerini hazırla
        tb_doc = TitleBlockDocument(
            doc_code="2026-999-КМ",
            project_name="Örnek Çelik Depo Binası",
            building_name="A Blok",
            company_name="Zadax Proje Mühendislik",
            signatories=[
                SignatoryEntry(role="Разраб.", surname="Ахмедов", signature="✓", date="14.10.26")
            ]
        )

        item1 = ScheduleItem(
            mark="К1",
            parts=[ElementPart(position_no="1", composition="40К1")],
            force_a="150.0",
            force_n="450.0",
            force_m="85.0",
            steel_grade="С345",
            note="Ana Taşıyıcı Kolon"
        )
        item1.sketch.sketch_type = SketchType.I_BEAM
        elem_doc = ElementsScheduleDocument(items=[item1])

        module_documents = {
            "title_block": tb_doc,
            "elements_schedule": elem_doc
        }

        import copy
        elem_cfg = copy.deepcopy(DEFAULT_LAYOUT_CONFIG)
        elem_cfg.size = SheetSize.A2
        elem_cfg.orientation = SheetOrientation.LANDSCAPE
        elem_cfg.title_block_doc = tb_doc

        module_configs = {
            "elements_schedule": elem_cfg
        }

        # 2. Kaydet
        saved_path = ProjectManager.save_to_file(
            file_path=proj_file,
            project_name="Fabrika_KM_Test",
            module_documents=module_documents,
            module_layout_configs=module_configs,
            active_module_id="elements_schedule",
            title_block_doc=tb_doc
        )
        assert os.path.exists(saved_path)
        assert saved_path.endswith(KMPROJ_FILE_EXT)

        # 3. Yükle
        loaded = ProjectManager.load_from_file(saved_path)
        assert loaded["project_name"] == "Fabrika_KM_Test"
        assert loaded["active_module_id"] == "elements_schedule"

        # Antet kontrolü
        loaded_tb = loaded["title_block_doc"]
        assert loaded_tb is not None
        assert loaded_tb.doc_code == "2026-999-КМ"
        assert loaded_tb.project_name == "Örnek Çelik Depo Binası"
        assert loaded_tb.company_name == "Zadax Proje Mühendislik"
        assert len(loaded_tb.signatories) == 1
        assert loaded_tb.signatories[0].surname == "Ахмедов"

        # Eleman tablosu kontrolü
        loaded_elem_doc = loaded["module_documents"]["elements_schedule"]
        assert len(loaded_elem_doc.items) == 1
        loaded_item = loaded_elem_doc.items[0]
        assert loaded_item.mark == "К1"
        assert loaded_item.parts[0].composition == "40К1"
        assert loaded_item.force_n == "450.0"
        assert loaded_item.steel_grade == "С345"
        assert loaded_item.sketch.sketch_type == SketchType.I_BEAM

        # Pafta ayarları kontrolü
        loaded_cfg = loaded["module_layout_configs"]["elements_schedule"]
        assert loaded_cfg.size == SheetSize.A2
        assert loaded_cfg.orientation == SheetOrientation.LANDSCAPE
