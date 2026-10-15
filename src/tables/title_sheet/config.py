"""
ГОСТ Р 21.101-2020 Приложение Р и С (Форма 12) Yapılandırma Parametreleri.
Титульный лист (Title Sheet / Başlık Sayfası).
"""
from dataclasses import dataclass


@dataclass
class TitleSheetConfig:
    """ГОСТ Р 21.101-2020 Form 12 / Приложение С parametreleri."""
    sheet_width: float = 210.0      # A4 Genişlik (mm)
    sheet_height: float = 297.0     # A4 Yükseklik (mm)
    margin_left: float = 20.0       # Sol cilt payı (mm)
    margin_right: float = 5.0       # Sağ kenar payı (mm)
    margin_top: float = 5.0         # Üst kenar payı (mm)
    margin_bottom: float = 5.0      # Alt kenar payı (mm)

    table_width: float = 185.0      # Çalışma alanı net genişlik (mm)
    table_height: float = 287.0     # Çalışma alanı net yükseklik (mm)

    # Kolon Genişlikleri (85 + 35 + 65 = 185 mm)
    col_role_width: float = 85.0
    col_sign_width: float = 35.0
    col_surname_width: float = 65.0

    @property
    def working_width(self) -> float:
        return self.table_width

    @property
    def working_height(self) -> float:
        return self.table_height

    # Tipografi yükseklikleri (mm)
    font_size_object: float = 4.5       # Nesne adı (Поле 4, BÜYÜK HARFLERLE)
    font_size_doc_type: float = 4.0     # Belge türü (Поле 5, ПРОЕКТНАЯ / РАБОЧАЯ ДОКУМЕНТАЦИЯ)
    font_size_title: float = 3.5        # Bölüm ve doküman başlığı (Поле 6)
    font_size_code: float = 4.5         # Belge şifresi ve Cilt No (Поле 7, 8)
    font_size_org: float = 3.5          # Kuruluş adı (Поле 2)
    font_size_approval: float = 2.8     # Onay bloğu (Поле 3)
    font_size_signatory: float = 2.8    # İmzacı kadrosu (Поля 9, 10, 11)
    font_size_year: float = 3.5         # Yıl (Поле 12)


DEFAULT_TITLE_SHEET_CONFIG = TitleSheetConfig()
