"""
'Ведомость элементов' Tablo Oluşturucu (Table Builder).
Domain modelini (ElementsScheduleDocument / ScheduleItem listesi)
CAD ve önizleme motoru için generic `Table` matrisine dönüştürür.
"""
from typing import List, Optional, Union
from src.models.table import Table, TableCell, TableRow, TableColumn, HAlign, VAlign
from src.models.sketch import SectionSketch, SketchType
from src.tables.elements_schedule.model import ScheduleItem, ElementPart, ElementsScheduleDocument
from src.tables.elements_schedule.config import ElementsScheduleConfig, DEFAULT_ELEMENTS_CONFIG

def create_elements_schedule_table(
    items_or_doc: Union[List[ScheduleItem], ElementsScheduleDocument],
    config: Optional[ElementsScheduleConfig] = None
) -> Table:
    """
    Eleman listesinden veya çalışma belgesinden 2 seviyeli başlık ve
    birleştirilmiş hücrelere sahip tam Table nesnesini üretir.
    """
    if isinstance(items_or_doc, ElementsScheduleDocument):
        items = items_or_doc.items
    else:
        items = items_or_doc

    if config is None:
        config = DEFAULT_ELEMENTS_CONFIG

    table = Table(title=config.table_title)

    # 1. Sütun tanımları (9 fiziksel sütun)
    cw = config.columns
    table.add_column("mark", "Марка элемента", cw.mark)
    table.add_column("sketch", "Эскиз", cw.sketch)
    table.add_column("pos", "Поз.", cw.position)
    table.add_column("composition", "Состав", cw.section_name)
    table.add_column("force_a", "A, кН", cw.force_a)
    table.add_column("force_n", "N, кН", cw.force_n)
    table.add_column("force_m", "M, кН*м", cw.force_m)
    table.add_column("steel_grade", "Наименование или марка металла", cw.steel_grade)
    table.add_column("note", "Примечание", cw.note)

    # 2. Başlık Satırı 1 (Üst seviye)
    h1_cells = [
        TableCell(text="Марка\nэлемента", rowspan=2, is_header=True),
        TableCell(text="Сечение", colspan=3, is_header=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(text="Усилие\nдля прикрепления", colspan=3, is_header=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(text="Наименование\nили марка\nметалла", rowspan=2, is_header=True),
        TableCell(text="Примечание", rowspan=2, is_header=True),
    ]
    table.add_row(h1_cells, height=config.rows.header_primary, is_header=True)

    # 3. Başlık Satırı 2 (Alt seviye)
    h2_cells = [
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(text="Эскиз", is_header=True),
        TableCell(text="Поз.", is_header=True),
        TableCell(text="Состав", is_header=True),
        TableCell(text="A, кН", is_header=True),
        TableCell(text="N, кН", is_header=True),
        TableCell(text="M, кН*м", is_header=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(is_header=True, is_merged_continuation=True),
    ]
    table.add_row(h2_cells, height=config.rows.header_secondary, is_header=True)

    # 4. Veri Satırları
    for item in items:
        part_count = max(1, len(item.parts))
        row_height = config.rows.data_row_standard if part_count == 1 else config.rows.data_row_sub

        for p_idx in range(part_count):
            part = item.parts[p_idx] if p_idx < len(item.parts) else ElementPart()
            comp_text = part.composition
            if part_count == 1 and item.sketch.sketch_type != SketchType.NONE:
                from src.tables.elements_schedule.editor import get_profile_full_name, WELDED_SKETCH_TYPES
                if item.sketch.sketch_type not in WELDED_SKETCH_TYPES:
                    comp_text = get_profile_full_name(comp_text, item.sketch.sketch_type)

            if p_idx == 0:
                row_cells = [
                    TableCell(text=item.mark, rowspan=part_count),
                    TableCell(sketch=item.sketch, rowspan=part_count),
                    TableCell(text=part.position_no),
                    TableCell(text=comp_text, halign=HAlign.LEFT),
                    TableCell(text=item.force_a, rowspan=part_count),
                    TableCell(text=item.force_n, rowspan=part_count),
                    TableCell(text=item.force_m, rowspan=part_count),
                    TableCell(text=item.steel_grade, rowspan=part_count),
                    TableCell(text=item.note if p_idx == 0 else "", rowspan=part_count),
                ]
            else:
                row_cells = [
                    TableCell(is_merged_continuation=True),
                    TableCell(is_merged_continuation=True),
                    TableCell(text=part.position_no),
                    TableCell(text=comp_text, halign=HAlign.LEFT),
                    TableCell(is_merged_continuation=True),
                    TableCell(is_merged_continuation=True),
                    TableCell(is_merged_continuation=True),
                    TableCell(is_merged_continuation=True),
                    TableCell(is_merged_continuation=True),
                ]
            table.add_row(row_cells, height=row_height)

    return table
