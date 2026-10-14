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
    """
    _instance: Optional["GostProfileDatabase"] = None
    _profiles: List[ProfileRecord] = []
    _lookup: Dict[str, ProfileRecord] = {}

    def __init__(self, json_path: Optional[str] = None):
        if not json_path:
            json_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "gost_profiles.json"
            )
        self.json_path = json_path
        self._load()

    @classmethod
    def instance(cls) -> "GostProfileDatabase":
        if cls._instance is None:
            cls._instance = GostProfileDatabase()
        return cls._instance

    def _load(self):
        self._profiles = []
        self._lookup = {}
        if not os.path.exists(self.json_path):
            return

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
