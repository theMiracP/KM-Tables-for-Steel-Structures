"""
ГОСТ Р 21.101-2020 Приложение Л (Форма 9) Tablo İnşa Edici (ChangePermissionBuilder).
`ChangePermissionDocument` nesnesini alıp milimetrik CAD `Table` modeline dönüştürür.
"""
from typing import Optional, List
from src.models.table import Table, TableRow, TableCell, HAlign, VAlign
from src.models.text_layout import wrap_cell_text
from src.tables.change_permission.model import (
    ChangePermissionDocument, ChangePermissionItem, ChangeSignatoryEntry
)
from src.tables.change_permission.config import (
    ChangePermissionConfig, DEFAULT_CHANGE_PERMISSION_CONFIG
)


def calculate_change_item_row_height(item: ChangePermissionItem, min_h: float = 10.0) -> float:
    """Metin uzunluğuna göre dinamik satır yüksekliği hesaplar (min 10.0 mm)."""
    text = (item.content or "").strip()
    if not text:
        return min_h
    # 100 mm sütun genişliği, ~92 mm net alan, 2.5 mm yazı yüksekliği
    lines, _ = wrap_cell_text(text, max_width_mm=92.0, max_height_mm=300.0, target_font_size_mm=2.5)
    line_count = max(1, len(lines))
    # Her satır için ~4.5 mm
    calc_h = line_count * 4.5 + 4.0
    return max(min_h, calc_h)


def create_change_permission_table(
    document: ChangePermissionDocument,
    config: Optional[ChangePermissionConfig] = None
) -> Table:
    """
    ГОСТ Р 21.101-2020 Форма 9 Değişiklik İzni belgesini milimetrik Table nesnesine dönüştürür.
    Toplam Genişlik: 185.0 mm, Standart Pafta İçi Yükseklik: 287.0 mm.
    """
    cfg = config or DEFAULT_CHANGE_PERMISSION_CONFIG
    cols_cfg = cfg.columns

    table = Table(title="")  # Belge içinde kendi başlık bloğu vardır
    table.id = "change_permission"

    # 12 alt dilim sütun tanımları (Toplam 185.0 mm)
    for idx, width in enumerate(cols_cfg.all_widths):
        table.add_column(f"c{idx}", "", width)

    # -------------------------------------------------------------------------
    # 1. ÜST BAŞLIK BLOĞU (Header, Toplam: 45.0 mm)
    # -------------------------------------------------------------------------
    # Row 0 (h = 10.0 mm)
    # - Разрешение (cols 0..2, w=30 mm)
    # - Обозначение (cols 3..6, w=40 mm)
    # - Doküman Kodu (cols 7..11, w=115 mm)
    cells_h0 = [
        TableCell(text="Разрешение", colspan=3, font_size=3.0, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(text="Обозначение", colspan=4, font_size=3.0, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(text=document.doc_code, colspan=5, font_size=3.8, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_bold=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_h0, height=10.0, is_header=True)

    # Row 1 (h = 20.0 mm)
    # - Разрешение № (cols 0..2, w=30 mm)
    # - Наименование объекта строительства (cols 3..6, w=40 mm)
    # - İnşaat Nesnesi Adı (cols 7..11, w=115 mm)
    cells_h1 = [
        TableCell(text=document.resolution_number, colspan=3, font_size=3.5, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_bold=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(text="Наименование\nобъекта\nстроительства", colspan=4, font_size=2.5, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(text=document.object_name, colspan=5, font_size=2.3, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_h1, height=20.0, is_header=True)

    # Row 2 (h = 15.0 mm): Sütun Başlıkları
    # - Изм. (col 0, w=15 mm)
    # - Лист (cols 1..2, w=15 mm)
    # - Содержание изменения (cols 3..7, w=100 mm)
    # - Код (col 8, w=15 mm)
    # - Примечание (cols 9..11, w=40 mm)
    cells_h2 = [
        TableCell(text="Изм.", colspan=1, font_size=2.8, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True),
        TableCell(text="Лист", colspan=2, font_size=2.8, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True),
        TableCell(is_merged_continuation=True),
        TableCell(text="Содержание изменения", colspan=5, font_size=2.8, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(text="Код", colspan=1, font_size=2.8, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True),
        TableCell(text="Примечание", colspan=3, font_size=2.8, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_h2, height=15.0, is_header=True)

    # -------------------------------------------------------------------------
    # 2. DEĞİŞİKLİK SATIRLARI (Items)
    # -------------------------------------------------------------------------
    total_items_height = 0.0
    items = document.items if document.items else [ChangePermissionItem()]

    for item in items:
        row_h = calculate_change_item_row_height(item, cfg.min_row_height)
        total_items_height += row_h

        cells_item = [
            TableCell(text=item.rev_num, colspan=1, font_size=2.5, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
            TableCell(text=item.sheet, colspan=2, font_size=2.5, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
            TableCell(is_merged_continuation=True),
            TableCell(text=item.content, colspan=5, font_size=2.5, halign=HAlign.LEFT, valign=VAlign.MIDDLE),
            TableCell(is_merged_continuation=True),
            TableCell(is_merged_continuation=True),
            TableCell(is_merged_continuation=True),
            TableCell(is_merged_continuation=True),
            TableCell(text=item.reason_code, colspan=1, font_size=2.5, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
            TableCell(text=item.note, colspan=3, font_size=2.5, halign=HAlign.LEFT, valign=VAlign.MIDDLE),
            TableCell(is_merged_continuation=True),
            TableCell(is_merged_continuation=True),
        ]
        table.add_row(cells_item, height=row_h)

    # -------------------------------------------------------------------------
    # 3. BOŞ DOLGU ALANI (Filler Row)
    # -------------------------------------------------------------------------
    # Standart Form 9 (A4 iç çerçevesi 287 mm):
    # Üst blok: 45 mm, Alt imza bloğu: 20 mm.
    # Kalan boşluk: 287 - 45 - items_height - 20 mm.
    remaining_h = cfg.total_height - cfg.header_height - total_items_height - cfg.signatures_height
    if remaining_h > 4.0:
        cells_filler = [
            TableCell(text="", colspan=12, border_left=True, border_right=True, border_top=True, border_bottom=True),
        ] + [TableCell(is_merged_continuation=True) for _ in range(11)]
        table.add_row(cells_filler, height=remaining_h)

    # -------------------------------------------------------------------------
    # 4. ALT İMZA VE PAFTA BLOĞU (Signatures, Toplam: 20.0 mm)
    # -------------------------------------------------------------------------
    # 4 satır x 5.0 mm = 20.0 mm
    sigs = document.signatories
    def get_sig(idx: int, default_role: str) -> ChangeSignatoryEntry:
        if idx < len(sigs):
            return sigs[idx]
        return ChangeSignatoryEntry(role=default_role, surname="")

    sig0 = get_sig(0, "Изм. внес")
    sig1 = get_sig(1, "Составил")
    sig2 = get_sig(2, "ГИП")
    sig3 = get_sig(3, "Утв.")

    # Satır 0 (h = 5.0 mm):
    # - Изм. внес, Soyadı, İmza, Tarih, Kuruluş Adı (rowspan 4), Лист başlığı (rowspan 2), Листов başlığı (rowspan 2)
    cells_s0 = [
        TableCell(text=sig0.role or "Изм. внес", colspan=2, font_size=2.2, halign=HAlign.LEFT, valign=VAlign.MIDDLE, border_top_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(text=sig0.surname, colspan=2, font_size=2.2, halign=HAlign.LEFT, valign=VAlign.MIDDLE, border_top_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(text=sig0.signature, colspan=1, font_size=2.2, halign=HAlign.CENTER, valign=VAlign.MIDDLE, border_top_thick=True),
        TableCell(text=sig0.date, colspan=1, font_size=2.2, halign=HAlign.CENTER, valign=VAlign.MIDDLE, border_top_thick=True),
        # Kuruluş: cols 6..9 (w=95 mm), 4 satır birleşik
        TableCell(text=document.company_name, colspan=4, rowspan=4, font_size=2.7, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_bold=True, border_top_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        # Лист (col 10, w=10 mm), 2 satır birleşik
        TableCell(text="Лист", colspan=1, rowspan=2, font_size=2.5, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True, border_top_thick=True),
        # Листов (col 11, w=15 mm), 2 satır birleşik
        TableCell(text="Листов", colspan=1, rowspan=2, font_size=2.5, halign=HAlign.CENTER, valign=VAlign.MIDDLE, is_header=True, border_top_thick=True),
    ]
    table.add_row(cells_s0, height=5.0)

    # Satır 1 (h = 5.0 mm):
    # - Составил, Soyadı, İmza, Tarih, Kuruluş devamı, Лист/Листов başlık devamı
    cells_s1 = [
        TableCell(text=sig1.role or "Составил", colspan=2, font_size=2.2, halign=HAlign.LEFT, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(text=sig1.surname, colspan=2, font_size=2.2, halign=HAlign.LEFT, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(text=sig1.signature, colspan=1, font_size=2.2, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
        TableCell(text=sig1.date, colspan=1, font_size=2.2, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_s1, height=5.0)

    # Satır 2 (h = 5.0 mm):
    # - ГИП, Soyadı, İmza, Tarih, Kuruluş devamı, Лист değeri (rowspan 2), Листов değeri (rowspan 2)
    cells_s2 = [
        TableCell(text=sig2.role or "ГИП", colspan=2, font_size=2.2, halign=HAlign.LEFT, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(text=sig2.surname, colspan=2, font_size=2.2, halign=HAlign.LEFT, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(text=sig2.signature, colspan=1, font_size=2.2, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
        TableCell(text=sig2.date, colspan=1, font_size=2.2, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        # Лист değeri (cols 10, w=10 mm), 2 satır birleşik
        TableCell(text=document.sheet_num, colspan=1, rowspan=2, font_size=3.0, halign=HAlign.CENTER, valign=VAlign.MIDDLE, border_top=True),
        # Листов değeri (cols 11, w=15 mm), 2 satır birleşik
        TableCell(text=document.sheet_count, colspan=1, rowspan=2, font_size=3.0, halign=HAlign.CENTER, valign=VAlign.MIDDLE, border_top=True),
    ]
    table.add_row(cells_s2, height=5.0)

    # Satır 3 (h = 5.0 mm):
    # - Утв., Soyadı, İmza, Tarih, Kuruluş devamı, Лист/Листов değer devamı
    cells_s3 = [
        TableCell(text=sig3.role or "Утв.", colspan=2, font_size=2.2, halign=HAlign.LEFT, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(text=sig3.surname, colspan=2, font_size=2.2, halign=HAlign.LEFT, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(text=sig3.signature, colspan=1, font_size=2.2, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
        TableCell(text=sig3.date, colspan=1, font_size=2.2, halign=HAlign.CENTER, valign=VAlign.MIDDLE),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_s3, height=5.0)

    return table
