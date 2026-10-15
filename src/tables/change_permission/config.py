"""
ГОСТ Р 21.101-2020 Приложение Л (Форма 9) Konfigürasyon ve Boyut Sabitleri.
Разрешение на внесение изменений (Değişiklik İzni).
Tüm ölçüler milimetre (mm) cinsindendir ve 1:1 CAD ölçeğine uygundur.
"""
from dataclasses import dataclass, field
from typing import List, Tuple


# =============================================================================
# ГОСТ Р 21.101-2020 Таблица Л.1 — Коды причин изменения документа
# (Image 1: Document change reason codes)
# =============================================================================
REASON_CODES: List[Tuple[str, str, str, str]] = [
    ("", "-", "-", "-"),
    ("1", "Введение усовершенствований", "İyileştirmelerin uygulanması", "Implementation of improvements"),
    ("2", "Изменение стандартов и норм", "Standart ve yönetmeliklerdeki değişiklikler", "Changes in standards and regulations"),
    ("3", "Дополнительные требования заказчика", "Ek müşteri gereksinimleri", "Additional customer requirements"),
    ("4", "Устранение ошибок", "Hataların giderilmesi", "Correction of mistakes"),
    ("5", "Другие причины", "Diğer nedenler", "Other reasons"),
]


@dataclass(frozen=True)
class ChangePermissionColumnWidths:
    """
    ГОСТ Р 21.101-2020 Форма 9 — 12 Alt Dilim Genişlikleri (Toplam: 185.0 mm):
    Tüm başlık, satır ve alt imza blokları bu 12 dilimin tam sayı katları ile oluşturulur.
    
    Dilimler (mm):
    [0]:  15.0  (0..15 mm:   İzm. / Role sol dilim)
    [1]:  5.0   (15..20 mm:  Лист sol dilim / Role sağ dilim)
    [2]:  10.0  (20..30 mm:  Лист sağ dilim / Soyadı sol dilim)
    [3]:  10.0  (30..40 mm:  Soyadı sağ dilim / Обозначение dilim 1)
    [4]:  15.0  (40..55 mm:  İmza dilimi / Обозначение dilim 2)
    [5]:  10.0  (55..65 mm:  Tarih dilimi / Обозначение dilim 3)
    [6]:  5.0   (65..70 mm:  Обозначение dilim 4 / Kuruluş dilim 1)
    [7]:  60.0  (70..130 mm: Содержание / Kuruluş dilim 2)
    [8]:  15.0  (130..145 mm: Код / Kuruluş dilim 3)
    [9]:  15.0  (145..160 mm: Kuruluş dilim 4 / Примечание dilim 1)
    [10]: 10.0  (160..170 mm: Лист / Примечание dilim 2)
    [11]: 15.0  (170..185 mm: Листов / Примечание dilim 3)
    
    Toplam: 15+5+10+10+15+10+5+60+15+15+10+15 = 185.0 mm
    """
    slice_0: float = 15.0
    slice_1: float = 5.0
    slice_2: float = 10.0
    slice_3: float = 10.0
    slice_4: float = 15.0
    slice_5: float = 10.0
    slice_6: float = 5.0
    slice_7: float = 60.0
    slice_8: float = 15.0
    slice_9: float = 15.0
    slice_10: float = 10.0
    slice_11: float = 15.0

    @property
    def all_widths(self) -> List[float]:
        return [
            self.slice_0, self.slice_1, self.slice_2, self.slice_3,
            self.slice_4, self.slice_5, self.slice_6, self.slice_7,
            self.slice_8, self.slice_9, self.slice_10, self.slice_11
        ]

    @property
    def total_width(self) -> float:
        return sum(self.all_widths)


@dataclass
class ChangePermissionConfig:
    """
    ГОСТ Р 21.101-2020 Форма 9 Konfigürasyonu.
    A4 Dikey pafta (210 x 297 mm), İç Çerçeve: 185 x 287 mm.
    """
    total_width: float = 185.0
    total_height: float = 287.0
    header_height: float = 45.0
    signatures_height: float = 20.0
    min_row_height: float = 10.0
    columns: ChangePermissionColumnWidths = field(default_factory=ChangePermissionColumnWidths)


DEFAULT_CHANGE_PERMISSION_CONFIG = ChangePermissionConfig()
