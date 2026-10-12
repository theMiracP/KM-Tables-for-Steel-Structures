"""
ГОСТ Р 21.101-2020 Form 3 Başlık Bloğu İnşa Edici (TitleBlockBuilder).
`TitleBlockDocument` nesnesini alıp milimetrik CAD `Table` modeline dönüştürür.
"""
from typing import Optional
from src.models.table import Table, TableRow, TableCell, HAlign, VAlign
from src.models.sketch import SectionSketch, SketchType
from src.tables.title_block.model import TitleBlockDocument, SignatoryEntry, RevisionEntry
from src.tables.title_block.config import TitleBlockConfig, DEFAULT_TITLE_BLOCK_CONFIG


def create_title_block_table(
    document: TitleBlockDocument,
    config: Optional[TitleBlockConfig] = None
) -> Table:
    """
    TitleBlockDocument verisini 185 x 55 mm Form 3 Table modeline dönüştürür.
    """
    cfg = config or DEFAULT_TITLE_BLOCK_CONFIG
    cols_cfg = cfg.columns
    row_h = cfg.rows.row_height  # 5.0 mm

    table = Table(title="")  # Antetin üstünde dış başlık yer almaz
    table.id = "title_block"

    # 1. Sütun Tanımları (Toplam 185 mm)
    table.add_column("rev_num", "Изм.", cols_cfg.col_rev_num)               # 0: 10 mm
    table.add_column("num_changes", "Кол.уч.", cols_cfg.col_num_changes)   # 1: 10 mm
    table.add_column("sheet", "Лист", cols_cfg.col_sheet)                   # 2: 10 mm
    table.add_column("doc_num", "№док.", cols_cfg.col_doc_num)             # 3: 15 mm
    table.add_column("signature", "Подпись", cols_cfg.col_signature)       # 4: 10 mm
    table.add_column("date", "Дата", cols_cfg.col_date)                     # 5: 15 mm
    table.add_column("middle", "Содержание", cols_cfg.col_middle)          # 6: 65 mm
    table.add_column("stage", "Стадия", cols_cfg.col_stage)                # 7: 15 mm
    table.add_column("sheet_no", "Лист", cols_cfg.col_sheet_no)            # 8: 15 mm
    table.add_column("sheets_total", "Листов", cols_cfg.col_sheets_total)  # 9: 20 mm

    # Güvenli erişim yardımcıları
    def get_rev(idx: int) -> RevisionEntry:
        if idx < len(document.revisions):
            return document.revisions[idx]
        return RevisionEntry()

    def get_sig(idx: int, fallback_role: str) -> SignatoryEntry:
        if idx < len(document.signatories):
            return document.signatories[idx]
        return SignatoryEntry(role=fallback_role, surname="")

    # -------------------------------------------------------------------------
    # SATIR 0 (y = 50..55 mm) - Revizyon 0 ve Doküman Şifresi (Başlangıç)
    # -------------------------------------------------------------------------
    r0 = get_rev(0)
    cells_r0 = [
        TableCell(text=r0.rev_num, font_size=2.2),
        TableCell(text=r0.num_changes, font_size=2.2),
        TableCell(text=r0.sheet, font_size=2.2),
        TableCell(text=r0.doc_num, font_size=2.2),
        TableCell(text=r0.signature, font_size=2.2),
        TableCell(text=r0.date, font_size=2.2, border_right_thick=True),
        # Doküman Şifresi / Kodu: 115 x 15 mm (Rowspan: 3 satır, Colspan: 4 sütun)
        TableCell(
            text=document.doc_code,
            rowspan=3,
            colspan=4,
            halign=HAlign.CENTER,
            valign=VAlign.MIDDLE,
            font_size=4.5,
            is_bold=True
        ),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_r0, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 1 (y = 45..50 mm) - Revizyon 1
    # -------------------------------------------------------------------------
    r1 = get_rev(1)
    cells_r1 = [
        TableCell(text=r1.rev_num, font_size=2.2),
        TableCell(text=r1.num_changes, font_size=2.2),
        TableCell(text=r1.sheet, font_size=2.2),
        TableCell(text=r1.doc_num, font_size=2.2),
        TableCell(text=r1.signature, font_size=2.2),
        TableCell(text=r1.date, font_size=2.2, border_right_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_r1, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 2 (y = 40..45 mm) - Revizyon 2
    # -------------------------------------------------------------------------
    r2 = get_rev(2)
    cells_r2 = [
        TableCell(text=r2.rev_num, font_size=2.2),
        TableCell(text=r2.num_changes, font_size=2.2),
        TableCell(text=r2.sheet, font_size=2.2),
        TableCell(text=r2.doc_num, font_size=2.2),
        TableCell(text=r2.signature, font_size=2.2),
        TableCell(text=r2.date, font_size=2.2, border_right_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_r2, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 3 (y = 35..40 mm) - Revizyon 3 ve Proje/Tesis Adı (115 x 10 mm)
    # -------------------------------------------------------------------------
    r3 = get_rev(3)
    cells_r3 = [
        TableCell(text=r3.rev_num, font_size=2.2),
        TableCell(text=r3.num_changes, font_size=2.2),
        TableCell(text=r3.sheet, font_size=2.2),
        TableCell(text=r3.doc_num, font_size=2.2),
        TableCell(text=r3.signature, font_size=2.2),
        TableCell(text=r3.date, font_size=2.2, border_right_thick=True),
        # Proje / Şantiye Adı: 115 x 10 mm (Rowspan: 2 satır, Colspan: 4 sütun)
        TableCell(
            text=document.project_name,
            rowspan=2,
            colspan=4,
            halign=HAlign.CENTER,
            valign=VAlign.MIDDLE,
            font_size=2.2,
            border_top_thick=True  # Doküman kodu altındaki kalın çizgi
        ),
        TableCell(is_merged_continuation=True, border_top_thick=True),
        TableCell(is_merged_continuation=True, border_top_thick=True),
        TableCell(is_merged_continuation=True, border_top_thick=True),
    ]
    table.add_row(cells_r3, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 4 (y = 30..35 mm) - Revizyon Tablosu Sabit Başlıkları
    # -------------------------------------------------------------------------
    cells_r4 = [
        TableCell(text="Изм.", font_size=2.0, is_header=True),
        TableCell(text="Кол.уч.", font_size=2.0, is_header=True),
        TableCell(text="Лист", font_size=2.0, is_header=True),
        TableCell(text="№док.", font_size=2.0, is_header=True),
        TableCell(text="Подпись", font_size=2.0, is_header=True),
        TableCell(text="Дата", font_size=2.0, is_header=True, border_right_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_r4, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 5 (y = 25..30 mm) - Kadro 0 (Разраб.), Yapı Adı ve Стадия Başlıkları
    # -------------------------------------------------------------------------
    s0 = get_sig(0, "Разраб.")
    cells_r5 = [
        TableCell(text=s0.role, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s0.surname, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s0.signature, halign=HAlign.CENTER, font_size=2.5),
        TableCell(text=s0.date, halign=HAlign.CENTER, font_size=2.2, border_right_thick=True),
        # Yapı / Bölüm Adı: 65 x 15 mm (Rowspan: 3 satır, Colspan: 1 sütun)
        TableCell(
            text=document.building_name,
            rowspan=3,
            colspan=1,
            halign=HAlign.CENTER,
            valign=VAlign.MIDDLE,
            font_size=2.7,
            border_right_thick=True
        ),
        # Стадия, Лист, Листов Başlıkları (5 mm yükseklik)
        TableCell(text="Стадия", font_size=2.0, is_header=True),
        TableCell(text="Лист", font_size=2.0, is_header=True),
        TableCell(text="Листов", font_size=2.0, is_header=True),
    ]
    table.add_row(cells_r5, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 6 (y = 20..25 mm) - Kadro 1 (Проверил) ve Стадия Değerleri
    # -------------------------------------------------------------------------
    s1 = get_sig(1, "Проверил")
    cells_r6 = [
        TableCell(text=s1.role, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s1.surname, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s1.signature, halign=HAlign.CENTER, font_size=2.5),
        TableCell(text=s1.date, halign=HAlign.CENTER, font_size=2.2, border_right_thick=True),
        TableCell(is_merged_continuation=True),
        # Стадия (Р)
        TableCell(text=document.stage, rowspan=2, halign=HAlign.CENTER, valign=VAlign.MIDDLE, font_size=3.5, is_bold=True),
        # Лист (8)
        TableCell(text=document.sheet_num, rowspan=2, halign=HAlign.CENTER, valign=VAlign.MIDDLE, font_size=3.5, is_bold=True),
        # Листов
        TableCell(text=document.total_sheets, rowspan=2, halign=HAlign.CENTER, valign=VAlign.MIDDLE, font_size=3.5),
    ]
    table.add_row(cells_r6, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 7 (y = 15..20 mm) - Kadro 2 (Гл. констр.)
    # -------------------------------------------------------------------------
    s2 = get_sig(2, "Гл. констр.")
    cells_r7 = [
        TableCell(text=s2.role, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s2.surname, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s2.signature, halign=HAlign.CENTER, font_size=2.5),
        TableCell(text=s2.date, halign=HAlign.CENTER, font_size=2.2, border_right_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_r7, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 8 (y = 10..15 mm) - Kadro 3 (Н. контр.), Pafta Başlığı ve Firma Kutusu
    # -------------------------------------------------------------------------
    s3 = get_sig(3, "Н. контр.")
    has_logo = bool(document.company_logo or document.logo_image_path)
    logo_sketch = (
        SectionSketch(sketch_type=SketchType.LOGO_EMBLEM, image_path=document.logo_image_path)
        if has_logo else None
    )
    company_halign = HAlign.RIGHT if has_logo else HAlign.CENTER

    cells_r8 = [
        TableCell(text=s3.role, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s3.surname, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s3.signature, halign=HAlign.CENTER, font_size=2.5),
        TableCell(text=s3.date, halign=HAlign.CENTER, font_size=2.2, border_right_thick=True),
        # Pafta Başlığı / İçeriği: 65 x 15 mm (Rowspan: 3 satır)
        TableCell(
            text=document.sheet_title,
            rowspan=3,
            colspan=1,
            halign=HAlign.CENTER,
            valign=VAlign.MIDDLE,
            font_size=2.6,
            border_right_thick=True
        ),
        # Firma / Tasarım Bürosu Kutusu: 50 x 15 mm (Rowspan: 3 satır, Colspan: 3 sütun)
        TableCell(
            text=document.company_name,
            rowspan=3,
            colspan=3,
            halign=company_halign,
            valign=VAlign.MIDDLE,
            font_size=3.0,
            is_bold=True,
            sketch=logo_sketch
        ),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_r8, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 9 (y = 5..10 mm) - Kadro 4 (Нач. отд.)
    # -------------------------------------------------------------------------
    s4 = get_sig(4, "Нач. отд.")
    cells_r9 = [
        TableCell(text=s4.role, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s4.surname, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s4.signature, halign=HAlign.CENTER, font_size=2.5),
        TableCell(text=s4.date, halign=HAlign.CENTER, font_size=2.2, border_right_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_r9, height=row_h)

    # -------------------------------------------------------------------------
    # SATIR 10 (y = 0..5 mm) - Kadro 5 (ГИП)
    # -------------------------------------------------------------------------
    s5 = get_sig(5, "ГИП")
    cells_r10 = [
        TableCell(text=s5.role, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s5.surname, colspan=2, halign=HAlign.LEFT, font_size=2.5),
        TableCell(is_merged_continuation=True),
        TableCell(text=s5.signature, halign=HAlign.CENTER, font_size=2.5),
        TableCell(text=s5.date, halign=HAlign.CENTER, font_size=2.2, border_right_thick=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
        TableCell(is_merged_continuation=True),
    ]
    table.add_row(cells_r10, height=row_h)

    return table
