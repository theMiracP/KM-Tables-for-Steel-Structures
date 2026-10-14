"""
KM Layout Tables Studio - Proje Yönetim Servisi (Project Manager).
Tüm aktif tablo modüllerini, Form 3 antet verilerini, pafta yapılandırmalarını ve CAD ayarlarını
tek bir bütüncül '.kmproj' (KM Project) dosyasında kaydeder, doğrular ve geri yükler.
"""
import os
import json
import datetime
from typing import Dict, Any, Optional
from dataclasses import asdict

from src.version import APP_NAME, APP_VERSION
from src.config.sheet_config import (
    LayoutConfig, SheetSize, SheetOrientation,
    TablePlacement, SheetMargins, TitleBlockConfig
)
from src.services.preset_manager import PresetManager
from src.tables.title_block.model import TitleBlockDocument


KMPROJ_FILE_EXT = ".kmproj"
KMPROJ_MAGIC_FORMAT = "KM_STUDIO_PROJECT"
KMPROJ_VERSION = "1.0.0"


class ProjectManager:
    """
    Tüm KM çizim projesini tek bir dosyada saklayan ve açan servis.
    """

    @staticmethod
    def layout_config_to_dict(cfg: LayoutConfig) -> Dict[str, Any]:
        """LayoutConfig nesnesini JSON uyumlu bir sözlüğe dönüştürür."""
        tb_doc_dict = None
        if hasattr(cfg, "title_block_doc") and cfg.title_block_doc:
            tb_doc_dict = PresetManager.serialize_document("title_block", cfg.title_block_doc)

        return {
            "placement": cfg.placement.name if hasattr(cfg.placement, "name") else str(cfg.placement),
            "size": cfg.size.name if hasattr(cfg.size, "name") else str(cfg.size),
            "orientation": cfg.orientation.name if hasattr(cfg.orientation, "name") else str(cfg.orientation),
            "margins": {
                "left": cfg.margins.left,
                "top": cfg.margins.top,
                "right": cfg.margins.right,
                "bottom": cfg.margins.bottom,
            },
            "title_block": {
                "width": cfg.title_block.width,
                "height": cfg.title_block.height,
                "gap_above": cfg.title_block.gap_above,
            },
            "table_gap": getattr(cfg, "table_gap", 8.0),
            "title_block_doc": tb_doc_dict
        }

    @staticmethod
    def layout_config_from_dict(d: Dict[str, Any]) -> LayoutConfig:
        """JSON sözlüğünden LayoutConfig nesnesini geri kurar."""
        place_str = d.get("placement", "STANDALONE")
        try:
            place_enum = TablePlacement[place_str]
        except KeyError:
            try:
                place_enum = TablePlacement(place_str)
            except ValueError:
                place_enum = TablePlacement.STANDALONE

        size_str = d.get("size", "A3")
        try:
            size_enum = SheetSize[size_str]
        except KeyError:
            try:
                size_enum = SheetSize(size_str)
            except ValueError:
                size_enum = SheetSize.A3

        orient_str = d.get("orientation", "LANDSCAPE")
        try:
            orient_enum = SheetOrientation[orient_str]
        except KeyError:
            try:
                orient_enum = SheetOrientation(orient_str)
            except ValueError:
                orient_enum = SheetOrientation.LANDSCAPE

        m_data = d.get("margins", {})
        margins = SheetMargins(
            left=float(m_data.get("left", 20.0)),
            top=float(m_data.get("top", 5.0)),
            right=float(m_data.get("right", 5.0)),
            bottom=float(m_data.get("bottom", 5.0))
        )

        tb_data = d.get("title_block", {})
        title_block = TitleBlockConfig(
            width=float(tb_data.get("width", 185.0)),
            height=float(tb_data.get("height", 55.0)),
            gap_above=float(tb_data.get("gap_above", 0.0))
        )

        cfg = LayoutConfig(
            placement=place_enum,
            size=size_enum,
            orientation=orient_enum,
            margins=margins,
            title_block=title_block
        )

        tb_doc_raw = d.get("title_block_doc")
        if tb_doc_raw:
            cfg.title_block_doc = PresetManager.deserialize_document("title_block", tb_doc_raw)

        return cfg

    @classmethod
    def serialize_project(
        cls,
        project_name: str,
        module_documents: Dict[str, Any],
        module_layout_configs: Dict[str, LayoutConfig],
        active_module_id: str,
        title_block_doc: Optional[TitleBlockDocument] = None,
        layer_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Tüm proje durumunu JSON uyumlu bir veri yapısına dönüştürür."""
        now_iso = datetime.datetime.now().isoformat()

        # 1. Modül Dokümanlarını Serileştir
        serialized_modules = {}
        for mod_id, doc in module_documents.items():
            if doc is not None:
                try:
                    serialized_modules[mod_id] = PresetManager.serialize_document(mod_id, doc)
                except Exception:
                    pass

        # 2. Pafta Konfigürasyonlarını Serileştir
        serialized_configs = {}
        for mod_id, cfg in module_layout_configs.items():
            try:
                serialized_configs[mod_id] = cls.layout_config_to_dict(cfg)
            except Exception:
                pass

        # 3. Ortak Antet Dokümanı
        tb_dict = None
        if title_block_doc:
            tb_dict = PresetManager.serialize_document("title_block", title_block_doc)
        elif "title_block" in serialized_modules:
            tb_dict = serialized_modules["title_block"]

        return {
            "format": KMPROJ_MAGIC_FORMAT,
            "version": KMPROJ_VERSION,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "project_name": project_name,
            "saved_at": now_iso,
            "active_module_id": active_module_id,
            "title_block": tb_dict,
            "modules": serialized_modules,
            "layout_configs": serialized_configs,
            "layer_settings": layer_settings or {}
        }

    @classmethod
    def save_to_file(
        cls,
        file_path: Optional[str] = None,
        project_name: Optional[str] = None,
        module_documents: Optional[Dict[str, Any]] = None,
        module_layout_configs: Optional[Dict[str, LayoutConfig]] = None,
        active_module_id: str = "vedomost_elementov",
        title_block_doc: Optional[TitleBlockDocument] = None,
        layer_settings: Optional[Dict[str, Any]] = None,
        filepath: Optional[str] = None,
        documents: Optional[Dict[str, Any]] = None,
        layout_configs: Optional[Dict[str, LayoutConfig]] = None,
        **kwargs
    ) -> str:
        """Projeyi verilen dosya yoluna '.kmproj' formatında kaydeder."""
        actual_path = file_path or filepath
        if not actual_path:
            raise ValueError("Dosya yolu belirtilmedi.")
        if not actual_path.lower().endswith(KMPROJ_FILE_EXT):
            actual_path += KMPROJ_FILE_EXT

        actual_name = project_name or os.path.splitext(os.path.basename(actual_path))[0]
        actual_docs = module_documents if module_documents is not None else (documents or {})
        actual_cfgs = module_layout_configs if module_layout_configs is not None else (layout_configs or {})

        data = cls.serialize_project(
            project_name=actual_name,
            module_documents=actual_docs,
            module_layout_configs=actual_cfgs,
            active_module_id=active_module_id,
            title_block_doc=title_block_doc,
            layer_settings=layer_settings
        )

        os.makedirs(os.path.dirname(os.path.abspath(actual_path)), exist_ok=True)
        with open(actual_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return actual_path

    @classmethod
    def load_from_file(cls, file_path: str) -> Dict[str, Any]:
        """
        Verilen '.kmproj' dosyasını okur, doğrular ve model nesnelerini içeren
        kullanıma hazır bir proje sözlüğü döndürür.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Proje dosyası bulunamadı: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # Doğrulama (Format ve versiyon)
        fmt = raw.get("format")
        if fmt != KMPROJ_MAGIC_FORMAT and fmt != "KMPROJ":
            raise ValueError(f"Geçersiz proje dosyası formatı: {fmt}. Beklenen: {KMPROJ_MAGIC_FORMAT}")

        project_name = raw.get("project_name", os.path.splitext(os.path.basename(file_path))[0])
        active_module_id = raw.get("active_module_id", "elements_schedule")

        # 1. Ortak Antet Belgesi
        title_block_doc = None
        tb_raw = raw.get("title_block")
        if tb_raw:
            try:
                title_block_doc = PresetManager.deserialize_document("title_block", tb_raw)
            except Exception:
                pass

        # 2. Modül Dokümanlarını Deserilize Et
        module_documents: Dict[str, Any] = {}
        modules_raw = raw.get("modules", {})
        for mod_id, doc_data in modules_raw.items():
            try:
                module_documents[mod_id] = PresetManager.deserialize_document(mod_id, doc_data)
            except Exception:
                pass

        if title_block_doc and "title_block" not in module_documents:
            module_documents["title_block"] = title_block_doc

        # 3. Pafta Yapılandırmalarını Deserilize Et
        module_layout_configs: Dict[str, LayoutConfig] = {}
        configs_raw = raw.get("layout_configs", {})
        for mod_id, cfg_dict in configs_raw.items():
            try:
                cfg = cls.layout_config_from_dict(cfg_dict)
                if title_block_doc and not getattr(cfg, "title_block_doc", None):
                    cfg.title_block_doc = title_block_doc
                module_layout_configs[mod_id] = cfg
            except Exception:
                pass

        return {
            "project_name": project_name,
            "active_module_id": active_module_id,
            "title_block_doc": title_block_doc,
            "module_documents": module_documents,
            "module_layout_configs": module_layout_configs,
            "layer_settings": raw.get("layer_settings", {}),
            "file_path": file_path,
            "saved_at": raw.get("saved_at", "")
        }
