"""
KM Layout Tables Studio - Vektörel İkon Yöneticisi (QtAwesome Entegrasyonu).
Font Awesome 5 Free Solid (fa5s) ve Regular (fa5 / fa5r) vektörel ikon seti.
"""
from typing import Optional
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

try:
    import qtawesome as qta
    _QTAWESOME_AVAILABLE = True
except ImportError:
    qta = None
    _QTAWESOME_AVAILABLE = False


# -----------------------------------------------------------------------------
# STANDART RENKLER & BOYUTLAR (Kullanıcı Standartları)
# -----------------------------------------------------------------------------
COLOR_NEUTRAL = "#9ca3af"       # Normal durumda nötr açık gri
COLOR_MUTED = "#646979"         # Pasif / ikincil gri
COLOR_ACCENT_BLUE = "#3b82f6"   # Vurgu gereken yerlerde mavi
COLOR_PRIMARY = "#5e6ad2"       # Linear moru vurgusu
COLOR_SUCCESS = "#10b981"       # Başarı / GOST uyumlu yeşili
COLOR_DANGER = "#ef4444"        # Silme / tehlike kırmızısı
COLOR_WARNING = "#f59e0b"       # Uyarı sarısı
COLOR_WHITE = "#ffffff"         # Saf beyaz

DEFAULT_SIZE = 18               # Standart ikon boyutu (18-22 px)


# -----------------------------------------------------------------------------
# SIK KULLANILAN İKON ADLARI (Free Solid & Regular)
# -----------------------------------------------------------------------------
# 1. Butonlar ve Araç Çubuğu: Solid İkonlar (fa5s)
ICON_SYNC = "fa5s.sync-alt"
ICON_CLOSE = "fa5s.times"
ICON_MENU = "fa5s.bars"
ICON_SEARCH = "fa5s.search"
ICON_EXPORT = "fa5s.file-export"
ICON_BOLT = "fa5s.bolt"
ICON_INFO = "fa5s.info-circle"
ICON_SETTINGS = "fa5s.cog"
ICON_GLOBE = "fa5s.globe"
ICON_EXTERNAL_LINK = "fa5s.external-link-alt"
ICON_PLUS = "fa5s.plus"
ICON_TRASH = "fa5s.trash-alt"
ICON_UP = "fa5s.arrow-up"
ICON_DOWN = "fa5s.arrow-down"
ICON_TABLE = "fa5s.table"
ICON_IMAGE = "fa5s.image"
ICON_FOLDER = "fa5s.folder-open"
ICON_CHECK = "fa5s.check"
ICON_CHEVRON_DOWN = "fa5s.chevron-down"
ICON_DESKTOP = "fa5s.desktop"
ICON_EYE = "fa5s.eye"

# 2. Daha Hafif Arayüz / Doküman / Pasif Elemanlar: Regular İkonlar (fa5 / fa5r)
ICON_DOC_REGULAR = "fa5.file-alt"
ICON_CLIPBOARD_REGULAR = "fa5.clipboard"
ICON_BOOKMARK_REGULAR = "fa5.bookmark"
ICON_CHECK_CIRCLE_REGULAR = "fa5.check-circle"
ICON_CLOCK_REGULAR = "fa5.clock"
ICON_COPY_REGULAR = "fa5.copy"
ICON_ID_BADGE_REGULAR = "fa5.id-badge"


def get_icon(name: str,
             color: str = COLOR_NEUTRAL,
             color_active: Optional[str] = None,
             color_disabled: Optional[str] = None) -> QIcon:
    """
    QtAwesome üzerinden Font Awesome 5 vektörel QIcon nesnesi üretir.
    fa5s: Solid ikonlar (butonlar/araç çubukları)
    fa5 / fa5r: Regular ikonlar (hafif doküman/arama/liste öğeleri)
    """
    if not _QTAWESOME_AVAILABLE or qta is None:
        return QIcon()

    # fa5r alias desteği (QtAwesome fa5 regular setini 'fa5' olarak adlandırır)
    actual_name = name
    if actual_name.startswith("fa5r."):
        actual_name = "fa5." + actual_name[5:]
    elif actual_name.startswith("fa6r."):
        actual_name = "fa6." + actual_name[5:]

    kwargs = {"color": color}
    if color_active:
        kwargs["color_active"] = color_active
    if color_disabled:
        kwargs["color_disabled"] = color_disabled

    try:
        return qta.icon(actual_name, **kwargs)
    except Exception:
        return QIcon()


def icon_size(size: int = DEFAULT_SIZE) -> QSize:
    """Belirtilen pikselde QSize döner (18-22 px standardı)."""
    return QSize(size, size)
