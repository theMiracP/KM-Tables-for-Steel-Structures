"""
KM Tablo Oluşturucu - 'Ведомость расхода стали' Tablo Oluşturucu (Builder).
Domain modelini (SteelConsumptionDocument) 2 seviyeli başlık ve İtogo toplamlarına
sahip generic CAD `Table` nesnesine dönüştürür.
"""
from typing import List, Optional, Union
from src.models.table import Table, TableCell, TableRow, TableColumn, HAlign, VAlign
from src.tables.steel_consumption.model import (
    SteelConsumptionItem, SteelConsumptionDocument
)
from src.tables.steel_consumption.config import (
    SteelConsumptionConfig, DEFAULT_STEEL_CONSUMPTION_CONFIG
)


def _format_weight(val: float) -> str:
    """Mühendislik formatında ağırlık (0 ise '-', pozitif ise tek ondalıklı)."""
    if abs(val) < 1e-4:
        return "—"
    # Tam sayı ise tamsayı, ondalıklı ise 1 basamak
    if val == int(val):
        return str(int(val))
    return f"{val:.1f}".replace(".", ",")


def create_steel_consumption_table(
    items_or_doc: Union[List[SteelConsumptionItem], SteelConsumptionDocument],
    config: Optional[SteelConsumptionConfig] = None
) -> Table:
    """
    Çelik sarfiyat verilerinden ГОСТ 21.502 standart 2 kademeli başlığa ve
    toplam satırına sahip Table nesnesi üretir.
    """
    if isinstance(items_or_doc, SteelConsumptionDocument):
        doc = items_or_doc
        items = doc.items
    else:
        items = items_or_doc
        doc = SteelConsumptionDocument(items=items)

    if config is None:
        config = DEFAULT_STEEL_CONSUMPTION_CONFIG

    table = Table(title=config.table_title)

    # 1. Sütun tanımları (7 fiziksel sütun)
    cw = config.columns
    table.add_column("mark", "Марка элемента", cw.mark)
    table.add_column("i_beam", "Двутавры", cw.i_beam)
    table.add_column("channel", "Швеллеры", cw.channel)
    table.add_column("angle", "Уголки", cw.angle)
    table.add_column("tube", "Трубы", cw.tube)
    table.add_column("plate", "Лист", cw.plate)
    table.add_column("total", "Всего, кг", cw.total)

    # 2. Başlık Satırı 1 (Üst seviye)
    h1_cells = [
        TableCell(text="Марка\nэлемента", rowspan=2, is_header=True),
        TableCell(text="Расход стали по профилям, кг", colspan=5, is_header=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(text="Всего,\nкг", rowspan=2, is_header=True),
    ]
    table.add_row(h1_cells, height=config.rows.header_primary, is_header=True)

    # 3. Başlık Satırı 2 (Alt seviye: Profil kategorileri)
    h2_cells = [
        TableCell(is_header=True, is_merged_continuation=True),
        TableCell(text="Двутавры", is_header=True),
        TableCell(text="Швеллеры", is_header=True),
        TableCell(text="Уголки", is_header=True),
        TableCell(text="Трубы", is_header=True),
        TableCell(text="Лист", is_header=True),
        TableCell(is_header=True, is_merged_continuation=True),
    ]
    table.add_row(h2_cells, height=config.rows.header_secondary, is_header=True)

    # 4. Veri Satırları
    for item in items:
        item_total = item.calculate_total()
        row_cells = [
            TableCell(text=item.mark, halign=HAlign.CENTER),
            TableCell(text=_format_weight(item.i_beam), halign=HAlign.RIGHT),
            TableCell(text=_format_weight(item.channel), halign=HAlign.RIGHT),
            TableCell(text=_format_weight(item.angle), halign=HAlign.RIGHT),
            TableCell(text=_format_weight(item.tube), halign=HAlign.RIGHT),
            TableCell(text=_format_weight(item.plate), halign=HAlign.RIGHT),
            TableCell(text=_format_weight(item_total), halign=HAlign.RIGHT),
        ]
        table.add_row(row_cells, height=config.rows.data_row)

    # 5. Toplam (Итого) Satırı
    totals = doc.get_column_totals()
    total_cells = [
        TableCell(text="Итого:", halign=HAlign.CENTER),
        TableCell(text=_format_weight(totals["i_beam"]), halign=HAlign.RIGHT),
        TableCell(text=_format_weight(totals["channel"]), halign=HAlign.RIGHT),
        TableCell(text=_format_weight(totals["angle"]), halign=HAlign.RIGHT),
        TableCell(text=_format_weight(totals["tube"]), halign=HAlign.RIGHT),
        TableCell(text=_format_weight(totals["plate"]), halign=HAlign.RIGHT),
        TableCell(text=_format_weight(totals["total"]), halign=HAlign.RIGHT),
    ]
    table.add_row(total_cells, height=config.rows.total_row)

    return table
