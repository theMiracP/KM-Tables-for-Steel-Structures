"""
KM Layout Tables Studio - Tablo Şablon / Önayar Yöneticisi (PresetManager).
Kullanıcının her tablo türü için (Eleman Listesi, Antet, Çalışma Çizimleri vb.)
hazırladığı tabloları bağımsız preset (.json) olarak kaydetmesini, listelemesini ve geri yüklemesini sağlar.
"""
import os
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from src.models.sketch import SectionSketch, SketchType
from src.tables.elements_schedule.model import (
    ElementsScheduleDocument, ScheduleItem, ElementPart
)
from src.tables.title_block.model import TitleBlockDocument
from src.tables.working_drawings.model import WorkingDrawingsDocument, WorkingDrawingItem
from src.tables.main_drawings.model import MainDrawingsDocument, DrawingSetItem
from src.tables.reference_documents.model import ReferenceDocItem


@dataclass
class PresetMetadata:
    name: str
    module_id: str
    file_path: str
    created_at: str
    item_count: int = 0
    description: str = ""


class PresetManager:
    """
    Her tablo türü için bağımsız şablon saklama ve geri çağırma servisi.
    """
    _instance: Optional["PresetManager"] = None

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            user_home = os.path.expanduser("~")
            self.base_dir = os.path.join(user_home, ".km_tables_studio", "presets")
        else:
            self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    @classmethod
    def get_instance(cls, base_dir: Optional[str] = None) -> "PresetManager":
        if cls._instance is None:
            cls._instance = PresetManager(base_dir)
        return cls._instance

    def _get_module_dir(self, module_id: str) -> str:
        safe_id = "".join(c for c in module_id if c.isalnum() or c in ("_", "-"))
        path = os.path.join(self.base_dir, safe_id)
        os.makedirs(path, exist_ok=True)
        return path

    # -------------------------------------------------------------------------
    # SERİLEŞTİRME & DESERİLEŞTİRME
    # -------------------------------------------------------------------------
    @staticmethod
    def serialize_document(module_id: str, document: Any) -> Dict[str, Any]:
        """Verilen modülün doküman nesnesini JSON uyumlu bir sözlüğe dönüştürür."""
        # 1. Elements Schedule
        if "elements" in module_id or "elementov" in module_id:
            items = getattr(document, "items", document if isinstance(document, list) else [])
            serialized_items = []
            for it in items:
                sk = it.sketch
                st_val = sk.sketch_type.value if hasattr(sk.sketch_type, "value") else str(sk.sketch_type)
                serialized_items.append({
                    "mark": it.mark,
                    "sketch": {
                        "sketch_type": st_val,
                        "symbol_text": sk.symbol_text,
                        "callout_1": sk.callout_1,
                        "callout_2": sk.callout_2,
                        "callout_3": sk.callout_3,
                        "image_path": getattr(sk, "image_path", ""),
                    },
                    "parts": [{"position_no": p.position_no, "composition": p.composition} for p in it.parts],
                    "force_a": it.force_a,
                    "force_n": it.force_n,
                    "force_m": it.force_m,
                    "steel_grade": it.steel_grade,
                    "note": it.note,
                })
            return {"items": serialized_items}

        # 2. Title Block
        elif "title_block" in module_id or "antet" in module_id:
            if hasattr(document, "to_dict"):
                return document.to_dict()
            return asdict(document)

        # 3. Working Drawings
        elif "working_drawings" in module_id:
            if hasattr(document, "to_dict"):
                return document.to_dict()
            items = getattr(document, "items", document if isinstance(document, list) else [])
            return {"items": [it.to_dict() if hasattr(it, "to_dict") else asdict(it) for it in items]}

        # 4. Main Drawings
        elif "main_drawings" in module_id or "drawings" in module_id:
            if hasattr(document, "to_dict"):
                return document.to_dict()
            items = getattr(document, "items", document if isinstance(document, list) else [])
            return {"items": [it.to_dict() if hasattr(it, "to_dict") else asdict(it) for it in items]}

        # 5. Reference Docs
        elif "reference" in module_id or "doc" in module_id:
            items = getattr(document, "items", document if isinstance(document, list) else [])
            return {"items": [it.to_dict() if hasattr(it, "to_dict") else asdict(it) for it in items]}

        # Genel Dataclass veya List
        if hasattr(document, "to_dict"):
            return document.to_dict()
        try:
            return asdict(document)
        except Exception:
            return {"raw": str(document)}

    @staticmethod
    def deserialize_document(module_id: str, data: Dict[str, Any]) -> Any:
        """JSON sözlüğünü tekrar ilgili modülün doküman nesnesine dönüştürür."""
        # 1. Elements Schedule
        if "elements" in module_id or "elementov" in module_id:
            raw_items = data.get("items", [])
            items = []
            for it_d in raw_items:
                sk_d = it_d.get("sketch", {})
                st_val = sk_d.get("sketch_type", "NONE")
                try:
                    st = SketchType(st_val)
                except Exception:
                    st = SketchType.NONE

                sk = SectionSketch(
                    sketch_type=st,
                    symbol_text=sk_d.get("symbol_text", ""),
                    callout_1=sk_d.get("callout_1", ""),
                    callout_2=sk_d.get("callout_2", ""),
                    callout_3=sk_d.get("callout_3", ""),
                    image_path=sk_d.get("image_path", ""),
                )
                parts = [
                    ElementPart(p.get("position_no", ""), p.get("composition", ""))
                    for p in it_d.get("parts", [])
                ]
                items.append(ScheduleItem(
                    mark=it_d.get("mark", ""),
                    sketch=sk,
                    parts=parts,
                    force_a=it_d.get("force_a", ""),
                    force_n=it_d.get("force_n", ""),
                    force_m=it_d.get("force_m", ""),
                    steel_grade=it_d.get("steel_grade", "С255-4"),
                    note=it_d.get("note", ""),
                ))
            return ElementsScheduleDocument(items=items)

        # 2. Title Block
        elif "title_block" in module_id or "antet" in module_id:
            return TitleBlockDocument.from_dict(data)

        # 3. Working Drawings
        elif "working_drawings" in module_id:
            return WorkingDrawingsDocument.from_dict(data)

        # 4. Main Drawings
        elif "main_drawings" in module_id or "drawings" in module_id:
            return MainDrawingsDocument.from_dict(data)

        # 5. Reference Docs
        elif "reference" in module_id or "doc" in module_id:
            raw_items = data.get("items", [])
            return [ReferenceDocItem.from_dict(it) for it in raw_items]

        return data

    # -------------------------------------------------------------------------
    # DOSYA İŞLEMLERİ (KAYDET / LİSTELE / YÜKLE / SİL)
    # -------------------------------------------------------------------------
    def save_preset(
        self,
        module_id: str,
        preset_name: str,
        document: Any,
        description: str = ""
    ) -> str:
        """
        Kullanıcının tablosunu ilgili modül dizininde .json dosyası olarak saklar.
        """
        clean_name = "".join(c for c in preset_name.strip() if c.isalnum() or c in (" ", "_", "-")).strip()
        if not clean_name:
            clean_name = f"Preset_{int(time.time())}"

        mod_dir = self._get_module_dir(module_id)
        file_path = os.path.join(mod_dir, f"{clean_name}.json")

        payload = {
            "name": clean_name,
            "module_id": module_id,
            "description": description,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": self.serialize_document(module_id, document)
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return file_path

    def list_presets(self, module_id: str) -> List[PresetMetadata]:
        """
        Verilen tablo modülü için kaydedilmiş tüm şablonları listeler.
        """
        mod_dir = self._get_module_dir(module_id)
        results = []
        if not os.path.exists(mod_dir):
            return results

        for fname in sorted(os.listdir(mod_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(mod_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    
                    data_obj = meta.get("data", {})
                    items = data_obj.get("items", []) if isinstance(data_obj, dict) else []
                    count = len(items) if isinstance(items, list) else 0

                    results.append(PresetMetadata(
                        name=meta.get("name", fname.replace(".json", "")),
                        module_id=meta.get("module_id", module_id),
                        file_path=fpath,
                        created_at=meta.get("created_at", ""),
                        item_count=count,
                        description=meta.get("description", "")
                    ))
                except Exception:
                    continue
        return results

    def load_preset(self, module_id: str, preset_name_or_file: str) -> Any:
        """
        Şablonu dosyadan okur ve ilgili doküman nesnesini oluşturur.
        """
        if os.path.isabs(preset_name_or_file) and os.path.exists(preset_name_or_file):
            fpath = preset_name_or_file
        else:
            mod_dir = self._get_module_dir(module_id)
            clean_name = preset_name_or_file.replace(".json", "")
            fpath = os.path.join(mod_dir, f"{clean_name}.json")

        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Şablon dosyası bulunamadı: {fpath}")

        with open(fpath, "r", encoding="utf-8") as f:
            meta = json.load(f)

        data = meta.get("data", {})
        return self.deserialize_document(module_id, data)

    def delete_preset(self, module_id: str, preset_name: str) -> bool:
        """
        Şablon dosyasını siler.
        """
        mod_dir = self._get_module_dir(module_id)
        clean_name = preset_name.replace(".json", "")
        fpath = os.path.join(mod_dir, f"{clean_name}.json")
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
                return True
            except Exception:
                return False
        return False
