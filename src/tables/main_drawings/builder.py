"""
ГОСТ Р 21.101-2020 Form 2 'Ведомость основных комплектов рабочих чертежей' CAD Tablo İnşa Edicisi.
1:1 milimetrik CAD Table nesnesi üretir (Önizleme tuvali ve ezdxf motoru için).
"""
from typing import Optional, List
from src.models.table import Table, TableCell, HAlign, VAlign
from src.models.text_layout import wrap_paragraph_to_width
from src.tables.main_drawings.model import MainDrawingsDocument, DrawingSetItem
from src.tables.main_drawings.config import (
    MainDrawingsConfig, DEFAULT_MAIN_DRAWINGS_CONFIG
)


def calculate_item_row_height(item: DrawingSetItem, cfg: MainDrawingsConfig) -> float:
    """
    Наименование sütunundaki metnin kelime sarımına göre satırın
    milimetrik yüksekliğini dinamik olarak hesaplar.
    Minimum satır yüksekliği GOST standardı gereği 8.0 mm'dir.
    Çok satırlı metinlerde harflerin sıkışmaması için satır yüksekliği genişletilir.
    """
    avail_w = max(10.0, cfg.columns.col_name - 4.0)
    clean_text = item.name.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not clean_text:
        return cfg.rows.min_item_height

    lines: List[str] = []
    for p in clean_text.split("\n"):
        p_str = p.strip()
        if p_str:
            lines.extend(wrap_paragraph_to_width(p_str, avail_w, cfg.typography.data_font_size))

    line_count = max(1, len(lines))
    if line_count <= 1:
        return cfg.rows.min_item_height

    # Her ek satır için ~4.0 mm yükseklik ve dikey pay
    needed_h = line_count * cfg.rows.line_height_pitch + 3.0
    return max(cfg.rows.min_item_height, needed_h)


def create_main_drawings_table(
    document: MainDrawingsDocument,
    config: Optional[MainDrawingsConfig] = None,
) -> Table:
    """
    MainDrawingsDocument nesnesini ГОСТ Р 21.101-2020 Form 2 standartlarında
    185 mm genişliğindeki milimetrik CAD Table modeline dönüştürür.
    """
    cfg = config or DEFAULT_MAIN_DRAWINGS_CONFIG

    # Tablo başlığı: Tablonun üst sınırının üzerinde yer alır (CAD önizleme tuvali ve DXF dışa aktarıcısı çizer)
    title_text = document.title or cfg.table_title
    table = Table(title=title_text)

    # 1. Sütun Tanımları (Toplam: 185.0 mm)
    # Form 3 antet genişliği (185 mm) ile tam hizalanır
    table.add_column("designation", "Обозначение", cfg.columns.col_designation)  # 60 mm
    table.add_column("name", "Наименование", cfg.columns.col_name)                # 95 mm
    table.add_column("note", "Примечание", cfg.columns.col_note)                  # 30 mm

    # 2. Sütun Başlıkları Satırı (Обозначение, Наименование, Примечание)
    # GOST Form 2 standart başlık yüksekliği: 15.0 mm
    table.add_row(
        [
            TableCell(
                text="Обозначение",
                halign=HAlign.CENTER,
                valign=VAlign.MIDDLE,
                font_size=cfg.typography.header_font_size,
                is_bold=True,
                is_header=True,
            ),
            TableCell(
                text="Наименование",
                halign=HAlign.CENTER,
                valign=VAlign.MIDDLE,
                font_size=cfg.typography.header_font_size,
                is_bold=True,
                is_header=True,
            ),
            TableCell(
                text="Примечание",
                halign=HAlign.CENTER,
                valign=VAlign.MIDDLE,
                font_size=cfg.typography.header_font_size,
                is_bold=True,
                is_header=True,
            ),
        ],
        height=cfg.rows.header_height,
        is_header=True,
    )

    # 3. Veri Satırları
    for item in document.items:
        row_h = calculate_item_row_height(item, cfg)
        table.add_row(
            [
                TableCell(
                    text=item.designation,
                    halign=HAlign.CENTER,
                    valign=VAlign.MIDDLE,
                    font_size=cfg.typography.data_font_size,
                ),
                TableCell(
                    text=item.name,
                    halign=HAlign.LEFT,
                    valign=VAlign.MIDDLE,
                    font_size=cfg.typography.data_font_size,
                ),
                TableCell(
                    text=item.note,
                    halign=HAlign.CENTER,
                    valign=VAlign.MIDDLE,
                    font_size=cfg.typography.data_font_size,
                ),
            ],
            height=row_h,
            is_header=False,
        )

    return table
