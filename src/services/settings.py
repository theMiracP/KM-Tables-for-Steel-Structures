"""
KM Layout Tables Studio - Kullanıcı ve Sistem Ayarları Yöneticisi (SettingsManager).
AutoCAD DXF katman isimleri, renkleri (ACI 1-255), çizgi kalınlıkları ve
otomatik güncelleme kontrol yapılandırmasını kalıcı olarak saklar.
"""
import os
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
from src.config.standards import (
    ALL_LAYERS,
    LAYER_BORDER,
    LAYER_GRID,
    LAYER_TEXT,
    LAYER_SKETCH,
    LAYER_SHEET_FRAME,
    LAYER_TITLEBLOCK,
    CadLayer
)
from src.version import DEFAULT_UPDATE_CHECK_URL

# Standart ACI Renk Ön Tanımları
ACI_COLOR_NAMES = {
    1: "1 - Kırmızı (Red)",
    2: "2 - Sarı (Yellow)",
    3: "3 - Yeşil (Green)",
    4: "4 - Cyan (Açık Mavi)",
    5: "5 - Mavi (Blue)",
    6: "6 - Magenta (Mor)",
    7: "7 - Beyaz / Siyah (White)",
    8: "8 - Koyu Gri (Dark Gray)",
    9: "9 - Açık Gri (Light Gray)",
}


@dataclass
class LayerSetting:
    key: str
    name: str
    color: int
    lineweight: int
    linetype: str = "CONTINUOUS"
    description: str = ""

    def to_cad_layer(self) -> CadLayer:
        return CadLayer(
            name=self.name,
            color=self.color,
            lineweight=self.lineweight,
            linetype=self.linetype,
            description=self.description
        )


@dataclass
class UpdaterSetting:
    check_on_startup: bool = False
    check_url: str = "https://zadax.net/tr/products/km-tables-studio-celik-yap-tablolar-ve-dxf-uretici/"


@dataclass
class AppSettings:
    layers: Dict[str, LayerSetting] = field(default_factory=dict)
    updater: UpdaterSetting = field(default_factory=UpdaterSetting)


def get_default_layers() -> Dict[str, LayerSetting]:
    return {
        "KM_TABLO_CERCEVE": LayerSetting(
            key="KM_TABLO_CERCEVE",
            name=LAYER_BORDER.name,
            color=LAYER_BORDER.color,
            lineweight=LAYER_BORDER.lineweight,
            description=LAYER_BORDER.description
        ),
        "KM_TABLO_IZGARA": LayerSetting(
            key="KM_TABLO_IZGARA",
            name=LAYER_GRID.name,
            color=LAYER_GRID.color,
            lineweight=LAYER_GRID.lineweight,
            description=LAYER_GRID.description
        ),
        "KM_TABLO_METIN": LayerSetting(
            key="KM_TABLO_METIN",
            name=LAYER_TEXT.name,
            color=LAYER_TEXT.color,
            lineweight=LAYER_TEXT.lineweight,
            description=LAYER_TEXT.description
        ),
        "KM_TABLO_ESKIZ": LayerSetting(
            key="KM_TABLO_ESKIZ",
            name=LAYER_SKETCH.name,
            color=LAYER_SKETCH.color,
            lineweight=LAYER_SKETCH.lineweight,
            description=LAYER_SKETCH.description
        ),
        "KM_SAYFA_CERCEVE": LayerSetting(
            key="KM_SAYFA_CERCEVE",
            name=LAYER_SHEET_FRAME.name,
            color=LAYER_SHEET_FRAME.color,
            lineweight=LAYER_SHEET_FRAME.lineweight,
            description=LAYER_SHEET_FRAME.description
        ),
        "KM_ANTET": LayerSetting(
            key="KM_ANTET",
            name=LAYER_TITLEBLOCK.name,
            color=LAYER_TITLEBLOCK.color,
            lineweight=LAYER_TITLEBLOCK.lineweight,
            description=LAYER_TITLEBLOCK.description
        ),
    }


class SettingsManager:
    """
    JSON tabanlı ayar yöneticisi tekil örneği (Singleton).
    """
    _instance: Optional["SettingsManager"] = None

    def __init__(self, config_file: Optional[str] = None):
        if config_file is None:
            user_home = os.path.expanduser("~")
            app_dir = os.path.join(user_home, ".km_tables_studio")
            os.makedirs(app_dir, exist_ok=True)
            self.config_file = os.path.join(app_dir, "settings.json")
        else:
            self.config_file = config_file

        self.settings = AppSettings(layers=get_default_layers())
        self.load()

    @classmethod
    def get_instance(cls, config_file: Optional[str] = None) -> "SettingsManager":
        if cls._instance is None:
            cls._instance = SettingsManager(config_file)
        return cls._instance

    def load(self):
        """Ayar dosyasını okur. Dosya yoksa varsayılanları kaydeder."""
        if not os.path.exists(self.config_file):
            self.save()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Katmanlar
            layers_data = data.get("layers", {})
            defaults = get_default_layers()
            merged_layers = {}
            for k, dflt in defaults.items():
                if k in layers_data:
                    merged_layers[k] = LayerSetting(
                        key=k,
                        name=layers_data[k].get("name", dflt.name),
                        color=int(layers_data[k].get("color", dflt.color)),
                        lineweight=int(layers_data[k].get("lineweight", dflt.lineweight)),
                        linetype=layers_data[k].get("linetype", dflt.linetype),
                        description=layers_data[k].get("description", dflt.description),
                    )
                else:
                    merged_layers[k] = dflt
            self.settings.layers = merged_layers

            # Güncelleme ayarları
            upd_data = data.get("updater", {})
            self.settings.updater = UpdaterSetting(
                check_on_startup=bool(upd_data.get("check_on_startup", False)),
                check_url=str(upd_data.get("check_url", "https://zadax.net/tr/products/km-tables-studio-celik-yap-tablolar-ve-dxf-uretici/")),
            )
        except Exception:
            # Okuma hatasında varsayılanları koru
            self.settings = AppSettings(layers=get_default_layers())

    def save(self):
        """Ayarları JSON dosyasına yazar."""
        try:
            data = {
                "layers": {k: asdict(v) for k, v in self.settings.layers.items()},
                "updater": asdict(self.settings.updater)
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_layer(self, key: str) -> LayerSetting:
        return self.settings.layers.get(key, get_default_layers().get(key, LayerSetting(key, key, 7, 25)))

    def get_layer_name(self, key: str) -> str:
        return self.get_layer(key).name

    def get_layer_color(self, key: str) -> int:
        return self.get_layer(key).color

    def get_layer_lineweight(self, key: str) -> int:
        return self.get_layer(key).lineweight

    def get_all_cad_layers(self) -> List[CadLayer]:
        return [l.to_cad_layer() for l in self.settings.layers.values()]

    def set_layer(self, key: str, name: str, color: int, lineweight: int):
        if key in self.settings.layers:
            self.settings.layers[key].name = name
            self.settings.layers[key].color = color
            self.settings.layers[key].lineweight = lineweight
            self.save()

    def reset_layers_to_default(self):
        self.settings.layers = get_default_layers()
        self.save()

    def get_updater_settings(self) -> UpdaterSetting:
        return self.settings.updater

    def set_updater_settings(self, check_on_startup: bool, check_url: str):
        self.settings.updater.check_on_startup = check_on_startup
        self.settings.updater.check_url = check_url
        self.save()
