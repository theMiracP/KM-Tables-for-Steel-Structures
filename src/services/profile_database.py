"""
KM Studio - Rus GOST Profil ve Sortament Veritabanı Servisi (ProfileDatabase).
СТО АСЧМ 20-93, ГОСТ 8240-97, ГОСТ 30245-2003, ГОСТ 10704-91, ГОСТ 8509/8510
standartlarındaki çelik profillerin sorgulanması, filtrelemesi ve eskiz eşlemesi.
"""
import os
import json
from dataclasses import dataclass
from typing import List, Optional, Dict
from src.models.sketch import SketchType


@dataclass
class ProfileRecord:
    designation: str
    category: str
    standard: str
    sketch_type: str
    dimensions: str
    weight_kg_m: float
    default_steel: str

    def get_sketch_type_enum(self) -> SketchType:
        try:
            return SketchType[self.sketch_type]
        except KeyError:
            return SketchType.NONE


class GostProfileDatabase:
    """
    GOST profil veritabanı yönetim servisi.
    Standart kütüphaneyi (gost_profiles.json) ve kullanıcı tanımlı profilleri (custom_profiles.json) yönetir.
    """
    _instance: Optional["GostProfileDatabase"] = None
    _profiles: List[ProfileRecord] = []
    _custom_profiles: List[ProfileRecord] = []
    _lookup: Dict[str, ProfileRecord] = {}

    def __init__(self, json_path: Optional[str] = None):
        if not json_path:
            json_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "gost_profiles.json"
            )
        self.json_path = json_path
        self.custom_json_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "custom_profiles.json"
        )
        self._load()

    @classmethod
    def instance(cls) -> "GostProfileDatabase":
        if cls._instance is None:
            cls._instance = GostProfileDatabase()
        return cls._instance

    def _load(self):
        self._profiles = []
        self._custom_profiles = []
        self._lookup = {}

        # 1. Standart GOST kütüphanesini yükle
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    rec = ProfileRecord(
                        designation=item.get("designation", ""),
                        category=item.get("category", ""),
                        standard=item.get("standard", ""),
                        sketch_type=item.get("sketch_type", "NONE"),
                        dimensions=item.get("dimensions", ""),
                        weight_kg_m=float(item.get("weight_kg_m", 0.0)),
                        default_steel=item.get("default_steel", "С255")
                    )
                    self._profiles.append(rec)
                    self._lookup[rec.designation.upper()] = rec
            except Exception:
                pass

        # 2. Varsa kullanıcı tanımlı özel profilleri yükle
        if os.path.exists(self.custom_json_path):
            try:
                with open(self.custom_json_path, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                for citem in cdata:
                    crec = ProfileRecord(
                        designation=citem.get("designation", ""),
                        category=citem.get("category", ""),
                        standard=citem.get("standard", ""),
                        sketch_type=citem.get("sketch_type", "NONE"),
                        dimensions=citem.get("dimensions", ""),
                        weight_kg_m=float(citem.get("weight_kg_m", 0.0)),
                        default_steel=citem.get("default_steel", "С255")
                    )
                    self._custom_profiles.append(crec)
                    key = crec.designation.upper()
                    if key in self._lookup:
                        # Standart profilin üstüne yaz veya güncelle
                        idx = self._profiles.index(self._lookup[key])
                        self._profiles[idx] = crec
                    else:
                        self._profiles.append(crec)
                    self._lookup[key] = crec
            except Exception:
                pass

    def add_custom_profile(self, rec: ProfileRecord) -> bool:
        """Kütüphaneye kullanıcı tanımlı yeni profil ekler ve diske kaydeder."""
        key = rec.designation.strip().upper()
        if not key:
            return False

        if key in self._lookup:
            existing = self._lookup[key]
            existing.category = rec.category
            existing.standard = rec.standard
            existing.sketch_type = rec.sketch_type
            existing.dimensions = rec.dimensions
            existing.weight_kg_m = rec.weight_kg_m
            existing.default_steel = rec.default_steel
            # Custom listesinde de güncelle
            for i, p in enumerate(self._custom_profiles):
                if p.designation.upper() == key:
                    self._custom_profiles[i] = rec
                    break
            else:
                self._custom_profiles.append(rec)
        else:
            self._profiles.append(rec)
            self._custom_profiles.append(rec)
            self._lookup[key] = rec

        self._save_custom_profiles()
        return True

    def delete_custom_profile(self, designation: str) -> bool:
        """Kullanıcı tanımlı profili siler."""
        key = designation.strip().upper()
        found = False
        self._custom_profiles = [p for p in self._custom_profiles if p.designation.upper() != key]
        if key in self._lookup:
            rec = self._lookup.pop(key)
            if rec in self._profiles:
                self._profiles.remove(rec)
            found = True
        if found:
            self._save_custom_profiles()
        return found

    def _save_custom_profiles(self):
        """Özel profilleri JSON dosyasına yazar."""
        try:
            os.makedirs(os.path.dirname(self.custom_json_path), exist_ok=True)
            data = [
                {
                    "designation": p.designation,
                    "category": p.category,
                    "standard": p.standard,
                    "sketch_type": p.sketch_type,
                    "dimensions": p.dimensions,
                    "weight_kg_m": p.weight_kg_m,
                    "default_steel": p.default_steel,
                }
                for p in self._custom_profiles
            ]
            with open(self.custom_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_all(self) -> List[ProfileRecord]:
        return list(self._profiles)

    def get_categories(self) -> List[str]:
        seen = []
        for p in self._profiles:
            if p.category not in seen:
                seen.append(p.category)
        return seen

    def filter_profiles(self, query: str = "", category: str = "") -> List[ProfileRecord]:
        q = query.strip().upper()
        results = []
        for p in self._profiles:
            if category and category != "Hepsi" and p.category != category:
                continue
            if not q:
                results.append(p)
                continue
            # Arama: profil adı, standart, kategori veya boyutlarda eşleşme
            text = f"{p.designation} {p.standard} {p.dimensions} {p.category}".upper()
            if q in text:
                results.append(p)
        return results

    def lookup_by_designation(self, designation: str) -> Optional[ProfileRecord]:
        return self._lookup.get(designation.strip().upper())
