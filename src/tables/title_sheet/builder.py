"""
ГОСТ Р 21.101-2020 Приложение Р и С (Форма 12) Tablo İnşa Edici (TitleSheetBuilder).
`TitleSheetDocument` nesnesini alıp 185.0 x 287.0 mm milimetrik CAD `Table` modeline dönüştürür.
"""
from typing import Optional, List
from src.models.table import Table, TableRow, TableCell, HAlign, VAlign
from src.models.sketch import SectionSketch, SketchType
from src.tables.title_sheet.model import TitleSheetDocument, TitleSheetSignatory
from src.tables.title_sheet.config import TitleSheetConfig, DEFAULT_TITLE_SHEET_CONFIG


def create_title_sheet_table(
    document: TitleSheetDocument,
    config: Optional[TitleSheetConfig] = None
) -> Table:
    """
    ГОСТ Р 21.101-2020 Форма 12 / Приложение С Başlık Sayfası belgesini
    milimetrik Table nesnesine dönüştürür.
    Toplam Genişlik: 185.0 mm, Net Pafta İçi Yükseklik: 287.0 mm.
    İç hücrelerde gereksiz ızgara çizgileri kapatılır (Р.2 kuralı).
    """
    cfg = config or DEFAULT_TITLE_SHEET_CONFIG

    table = Table(title="")
    table.id = "title_sheet"

    # 3 sütunlu orantılı ızgara:
    # Col 0: 85.0 mm (Unvan / Sol onay alanı)
    # Col 1: 35.0 mm (İmza / Tarih / Orta boşluk)
    # Col 2: 65.0 mm (Ad Soyad / Sağ onay alanı)
    # Toplam: 85 + 35 + 65 = 185.0 mm
    table.add_column("c0", "", 85.0)
    table.add_column("c1", "", 35.0)
    table.add_column("c2", "", 65.0)

    def _full_width_cell(
        text: str,
        font_size: float = 3.5,
        halign: HAlign = HAlign.CENTER,
        valign: VAlign = VAlign.MIDDLE,
        is_bold: bool = False,
        sketch: Optional[SectionSketch] = None
    ) -> List[TableCell]:
        """Tüm sayfayı (185 mm) kaplayan kenarlıksız hücre satırı oluşturur."""
        c0 = TableCell(
            text=text,
            colspan=3,
            halign=halign,
            valign=valign,
            font_size=font_size,
            is_bold=is_bold,
            border_left=False,
            border_right=False,
            border_top=False,
            border_bottom=False,
            sketch=sketch
        )
        return [
            c0,
            TableCell(is_merged_continuation=True, border_left=False, border_right=False, border_top=False, border_bottom=False),
            TableCell(is_merged_continuation=True, border_left=False, border_right=False, border_top=False, border_bottom=False)
        ]

    # -------------------------------------------------------------------------
    # 1. ÜST KURULUŞ & ORGANİZASYON ADI (Поле 1 & 2)
    # -------------------------------------------------------------------------
    if document.higher_org.strip():
        table.add_row(_full_width_cell(document.higher_org.strip(), font_size=2.8, halign=HAlign.CENTER), height=8.0)

    # Logo ve/veya Tasarım Kuruluşu Adı
    logo_sketch = None
    if document.has_logo and document.logo_image_path:
        logo_sketch = SectionSketch(
            sketch_type=SketchType.LOGO_EMBLEM,
            image_path=document.logo_image_path
        )

    org_text = document.organization_name.strip()
    table.add_row(_full_width_cell(org_text, font_size=cfg.font_size_org, is_bold=True, sketch=logo_sketch), height=18.0)

    # -------------------------------------------------------------------------
    # 2. ONAY BLOKLARI (Поле 3 — Гриф согласования / утверждения)
    # -------------------------------------------------------------------------
    if document.approval.has_approval:
        app = document.approval
        app_text = (
            f"{app.approval_title}\n"
            f"{app.role}\n"
            f"{app.organization}\n"
            f"_________________ {app.name}\n"
            f"{app.date}"
        )
        c0 = TableCell(
            text=app_text,
            colspan=2,
            halign=HAlign.LEFT,
            valign=VAlign.TOP,
            font_size=cfg.font_size_approval,
            border_left=False,
            border_right=False,
            border_top=False,
            border_bottom=False
        )
        c2 = TableCell(
            text="",
            colspan=1,
            border_left=False,
            border_right=False,
            border_top=False,
            border_bottom=False
        )
        c1 = TableCell(
            is_merged_continuation=True,
            border_left=False,
            border_right=False,
            border_top=False,
            border_bottom=False
        )
        table.add_row([c0, c1, c2], height=28.0)
    else:
        table.add_row(_full_width_cell("", font_size=2.0), height=10.0)

    # -------------------------------------------------------------------------
    # 3. İNŞAAT NESNESİ / PROJE ADI (Поле 4, BÜYÜK HARFLERLE)
    # -------------------------------------------------------------------------
    table.add_row(_full_width_cell("", font_size=2.0), height=8.0)
    table.add_row(
        _full_width_cell(
            document.object_name.strip(),
            font_size=cfg.font_size_object,
            is_bold=True,
            halign=HAlign.CENTER
        ),
        height=32.0
    )

    # -------------------------------------------------------------------------
    # 4. DOKÜMAN TÜRÜ (Поле 5: ПРОЕКТНАЯ / РАБОЧАЯ ДОКУМЕНТАЦИЯ)
    # -------------------------------------------------------------------------
    table.add_row(_full_width_cell("", font_size=2.0), height=8.0)
    table.add_row(
        _full_width_cell(
            document.doc_type.strip(),
            font_size=cfg.font_size_doc_type,
            is_bold=True,
            halign=HAlign.CENTER
        ),
        height=12.0
    )

    # -------------------------------------------------------------------------
    # 5. DOKÜMAN / BÖLÜM ADI (Поле 6)
    # -------------------------------------------------------------------------
    table.add_row(_full_width_cell("", font_size=2.0), height=8.0)
    table.add_row(
        _full_width_cell(
            document.doc_title.strip(),
            font_size=cfg.font_size_title,
            halign=HAlign.CENTER
        ),
        height=40.0
    )

    # -------------------------------------------------------------------------
    # 6. DOKÜMAN KODU & CİLT NO (Поле 7 & 8)
    # -------------------------------------------------------------------------
    table.add_row(_full_width_cell("", font_size=2.0), height=6.0)
    table.add_row(
        _full_width_cell(
            document.doc_code.strip(),
            font_size=cfg.font_size_code,
            is_bold=True,
            halign=HAlign.CENTER
        ),
        height=12.0
    )
    if document.volume_number.strip():
        table.add_row(
            _full_width_cell(
                document.volume_number.strip(),
                font_size=cfg.font_size_title,
                is_bold=True,
                halign=HAlign.CENTER
            ),
            height=10.0
        )

    # -------------------------------------------------------------------------
    # 7. İMZA BLOKLARI & YIL HESABI İÇİN DİNAMİK DOLGU (287 mm Tamamlama)
    # -------------------------------------------------------------------------
    sigs = document.signatories or []
    sig_height = len(sigs) * 7.5
    year_block_height = 20.0  # Yıl ve alt boşluk

    # Şimdiye kadarki satırların toplam yüksekliği
    cur_h = sum(r.height for r in table.rows)
    target_total_h = cfg.table_height  # 287.0 mm

    remaining_space = target_total_h - cur_h - sig_height - year_block_height
    filler_h = max(10.0, remaining_space)
    table.add_row(_full_width_cell("", font_size=2.0), height=filler_h)

    # -------------------------------------------------------------------------
    # 8. SORUMLU İMZA KADROSU (Поля 9, 10, 11)
    # -------------------------------------------------------------------------
    for s in sigs:
        # Col 0: Unvan (Должность)
        c0 = TableCell(
            text=s.role,
            halign=HAlign.LEFT,
            valign=VAlign.MIDDLE,
            font_size=cfg.font_size_signatory,
            border_left=False,
            border_right=False,
            border_top=False,
            border_bottom=False
        )
        # Col 1: İmza / Tarih
        date_str = f" {s.date}" if s.date else ""
        c1 = TableCell(
            text=f"(подпись{date_str})",
            halign=HAlign.CENTER,
            valign=VAlign.MIDDLE,
            font_size=cfg.font_size_signatory - 0.5,
            border_left=False,
            border_right=False,
            border_top=False,
            border_bottom=False
        )
        # Col 2: Soyadı / İnisiyaller (ФИО)
        c2 = TableCell(
            text=s.surname,
            halign=HAlign.RIGHT,
            valign=VAlign.MIDDLE,
            font_size=cfg.font_size_signatory,
            border_left=False,
            border_right=False,
            border_top=False,
            border_bottom=False
        )
        table.add_row([c0, c1, c2], height=7.5)

    # -------------------------------------------------------------------------
    # 9. YIL (Поле 12, En Altta Ortalı)
    # -------------------------------------------------------------------------
    table.add_row(_full_width_cell("", font_size=2.0), height=6.0)
    table.add_row(
        _full_width_cell(
            document.year.strip(),
            font_size=cfg.font_size_year,
            halign=HAlign.CENTER
        ),
        height=10.0
    )

    # Nihai yükseklik kontrolü: Toplam yüksekliğin tam 287.0 mm olmasını sağla
    final_h = sum(r.height for r in table.rows)
    diff = target_total_h - final_h
    if abs(diff) > 0.001 and len(table.rows) > 0:
        # Son boşluk satırına veya yıla farkı ekle
        table.rows[-1].height += diff

    return table
