"""
ГОСТ Р 21.101-2020 Form 2 'Ведомость ссылочных и прилагаемых документов' CAD Tablo İnşa Edicisi.
1:1 milimetrik CAD Table nesnesi üretir (Önizleme tuvali ve ezdxf motoru için).
"""
from typing import Optional, List
from src.models.table import Table, TableCell, HAlign, VAlign
from src.tables.reference_documents.model import ReferenceDocsDocument, ReferenceDocItem
from src.tables.reference_documents.config import (
    ReferenceDocsConfig, DEFAULT_REFERENCE_DOCS_CONFIG
)


def create_reference_docs_table(
    document: ReferenceDocsDocument,
    config: Optional[ReferenceDocsConfig] = None,
) -> Table:
    """
    ReferenceDocsDocument nesnesini ГОСТ Р 21.101-2020 Form 2 standartlarında
    185 mm genişliğindeki milimetrik CAD Table modeline dönüştürür.
    """
    cfg = config or DEFAULT_REFERENCE_DOCS_CONFIG

    # Tabloyu oluştur (title="", çünkü başlık görseldeki gibi tablonun en üst hücresinde yer alır)
    table = Table(title="")

    # 1. Sütun Tanımları (Toplam: 185.0 mm)
    # Form 3 antet genişliği (185 mm) ile tam hizalanır
    table.add_column("designation", "Обозначение", cfg.columns.col_designation)  # 60 mm
    table.add_column("name", "Наименование", cfg.columns.col_name)                # 95 mm
    table.add_column("note", "Примечание", cfg.columns.col_note)                  # 30 mm

    # 2. Üst Ana Başlık Satırı (Tüm sütunları birleştiren 185 mm'lik başlık kutusu)
    title_text = document.title or "Ведомость ссылочных и прилагаемых документов"
    table.add_row(
        [
            TableCell(
                text=title_text,
                colspan=3,
                halign=HAlign.CENTER,
                valign=VAlign.MIDDLE,
                font_size=cfg.typography.title_font_size,
                is_bold=True,
                is_header=True,
            ),
            TableCell(is_merged_continuation=True),
            TableCell(is_merged_continuation=True),
        ],
        height=cfg.rows.title_height,
        is_header=True,
    )

    # 3. Sütun Başlıkları Satırı (Обозначение, Наименование, Примечание)
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

    # 4. Satırların Eklenmesi
    has_explicit_headers = any(it.is_section_header for it in document.items)

    if has_explicit_headers or not document.items:
        # Satırlar doğrudan kullanıcı sıralamasına göre eklenir
        for item in document.items:
            _append_item_row(table, item, cfg)
    else:
        # Otomatik bölüm gruplaması (Ссылочные документы / Прилагаемые документы)
        sections_order: List[str] = []
        grouped: dict[str, List[ReferenceDocItem]] = {}
        for item in document.items:
            sec = item.section.strip() or "Ссылочные документы"
            if sec not in grouped:
                grouped[sec] = []
                sections_order.append(sec)
            grouped[sec].append(item)

        for sec_name in sections_order:
            # Bölüm ayraç satırı
            header_item = ReferenceDocItem(
                designation="",
                title=sec_name,
                is_section_header=True,
                section=sec_name,
            )
            _append_item_row(table, header_item, cfg)
            # Bölüme ait elemanlar
            for item in grouped[sec_name]:
                _append_item_row(table, item, cfg)

    return table


def _append_item_row(table: Table, item: ReferenceDocItem, cfg: ReferenceDocsConfig) -> None:
    """Tek bir doküman veya bölüm başlığı satırını CAD tablosuna ekler."""
    if item.is_section_header:
        # Bölüm Başlığı Satırı (Görselde: Sol ve sağ boş, orta sütunda başlık ortalı)
        table.add_row(
            [
                TableCell(text="", is_header=True),
                TableCell(
                    text=item.title,
                    halign=HAlign.CENTER,
                    valign=VAlign.MIDDLE,
                    font_size=cfg.typography.section_font_size,
                    is_bold=True,
                    is_header=True,
                ),
                TableCell(text="", is_header=True),
            ],
            height=cfg.rows.section_height,
            is_header=True,
        )
    else:
        # Standart Doküman Satırı
        # Kod (Обозначение): Hücre içinde daima ortalı (HAlign.CENTER)
        table.add_row(
            [
                TableCell(
                    text=item.designation,
                    halign=HAlign.CENTER,
                    valign=VAlign.MIDDLE,
                    font_size=cfg.typography.data_font_size,
                ),
                TableCell(
                    text=item.title,
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
            height=cfg.rows.item_height,
            is_header=False,
        )
