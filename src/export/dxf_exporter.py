"""
AutoCAD Bağımsız DXF Dışa Aktarıcı (DxfExporter).
ezdxf kütüphanesini kullanarak milimetrik, katmanlı ve standartlara tam uyumlu
DXF R2010 dosyası üretir.
"""
import os
from typing import Optional
import ezdxf
from ezdxf.enums import TextEntityAlignment

try:
    from PIL import Image as PilImage
except ImportError:
    PilImage = None

from src.config.standards import (
    ALL_LAYERS,
    LAYER_BORDER,
    LAYER_GRID,
    LAYER_TEXT,
    LAYER_SKETCH,
    LAYER_SHEET_FRAME,
    LAYER_TITLEBLOCK,
)
from src.config.table_config import TableConfig, DEFAULT_TABLE_CONFIG
from src.config.sheet_config import LayoutConfig, DEFAULT_LAYOUT_CONFIG, TablePlacement
from src.export.base_exporter import BaseExporter
from src.models.geometry import Rect2D, Point2D
from src.models.sheet import SheetLayoutCalculator, CalculatedLayout
from src.models.sketch import SectionSketch, SketchType
from src.models.table import Table, TableCell, HAlign, VAlign
from src.models.text_layout import wrap_cell_text

class DxfExporter(BaseExporter):
    def export(
        self,
        table: Table,
        output_path: str,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None
    ) -> bool:
        if table_config is None:
            table_config = DEFAULT_TABLE_CONFIG
        if layout_config is None:
            layout_config = DEFAULT_LAYOUT_CONFIG

        # 1. Yeni DXF Belgesi (R2010 formatı - tüm AutoCAD sürümlerinde sorunsuz açılır)
        doc = ezdxf.new("R2010", setup=True)
        # Çizim birimi: Milimetre (INSUNITS = 4)
        doc.header["$INSUNITS"] = 4
        doc.header["$MEASUREMENT"] = 1  # Metrik

        # 2. Katmanları tanımla
        self._setup_layers(doc)

        # 3. Yazı stilini tanımla
        doc.styles.new("GOST_STYLE", dxfattribs={"font": "isocpeur.ttf"})

        # 4. Yerleşim hesapla (Sayfa, Antet ve Tablo koordinatları)
        title_clearance = (table_config.rows.title_gap + table_config.typography.title_height + 3.0) if table.title else 0.0
        calc_layout = SheetLayoutCalculator.calculate(table, layout_config, title_clearance=title_clearance)
        msp = doc.modelspace()

        # Tablonun kendisi bağımsız özel form mu (Form 3 Antet, Form 9 Değişiklik İzni veya Form 12 Başlık Sayfası)?
        is_special_form = (
            getattr(table, "id", "") in ("title_block", "change_permission", "title_sheet") or
            (hasattr(table, "columns") and len(table.columns) == 10 and abs(table.total_width - 185.0) < 0.1)
        )

        # 5. Sayfa ve Antet Çizimi (Eğer Sayfa Düzeni modu seçildiyse)
        if calc_layout.sheet_rect and calc_layout.inner_frame_rect:
            if is_special_form:
                # Sadece sayfa çerçevelerini çiz, standart Form 3 antetini mükerrer çizme
                self._draw_sheet_frames_only(msp, calc_layout, layout_cfg=layout_config)
            else:
                self._draw_sheet_and_titleblock(msp, calc_layout, layout_config, table_config, doc=doc)

        # 6. Tabloyu Çiz
        if is_special_form and calc_layout.sheet_rect:
            if getattr(table, "id", "") in ("change_permission", "title_sheet"):
                origin = Point2D(calc_layout.inner_frame_rect.x_min, calc_layout.inner_frame_rect.y_min)
            else:
                tb_rect = calc_layout.title_block_rect
                origin = Point2D(tb_rect.x_min, tb_rect.y_min)
            self._draw_table(msp, table, origin, table_config, doc=doc)
        else:
            self._draw_table(msp, table, calc_layout.table_origin, table_config, doc=doc)

        # 7. Kaydet
        doc.saveas(output_path, encoding="utf-8")
        return True

    def export_multi_sheet(
        self,
        multi_sheet_layout,
        output_path: str,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None
    ) -> bool:
        """
        Otomatik olarak oluşturulmuş çoklu pafta yerleşimini tek bir DXF belgesinde Modelspace'e dışa aktarır.
        """
        if table_config is None:
            table_config = DEFAULT_TABLE_CONFIG
        if layout_config is None:
            layout_config = DEFAULT_LAYOUT_CONFIG

        doc = ezdxf.new("R2010", setup=True)
        doc.header["$INSUNITS"] = 4
        doc.header["$MEASUREMENT"] = 1

        self._setup_layers(doc)
        doc.styles.new("GOST_STYLE", dxfattribs={"font": "isocpeur.ttf"})
        msp = doc.modelspace()

        layer_grid = self._get_layer_name("KM_TABLO_IZGARA", LAYER_GRID.name)
        layer_sheet = self._get_layer_name("KM_SAYFA_CERCEVE", LAYER_SHEET_FRAME.name)
        layer_text = self._get_layer_name("KM_TABLO_METIN", LAYER_TEXT.name)

        for page in multi_sheet_layout.pages:
            s = page.sheet_rect
            f = page.inner_frame_rect

            # 1. Kağıt Dış Sınırı (İnce Çizgi)
            msp.add_lwpolyline(
                [(s.x_min, s.y_min), (s.x_max, s.y_min), (s.x_max, s.y_max), (s.x_min, s.y_max)],
                close=True,
                dxfattribs={"layer": layer_grid}
            )

            # 2. İç Çizim Çerçevesi (Kalın Çizgi)
            msp.add_lwpolyline(
                [(f.x_min, f.y_min), (f.x_max, f.y_min), (f.x_max, f.y_max), (f.x_min, f.y_max)],
                close=True,
                dxfattribs={"layer": layer_sheet}
            )

            # 3. Sayfa Format Etiketi
            if layout_config and hasattr(layout_config, "get_format_designation"):
                fmt_text = layout_config.get_format_designation()
                fmt_cad_x = f.x_max - 25.0
                fmt_cad_y = (s.y_min + f.y_min) / 2.0
                msp.add_text(
                    fmt_text,
                    dxfattribs={"layer": layer_text, "height": 2.5, "style": "GOST_STYLE"}
                ).set_placement((fmt_cad_x, fmt_cad_y), align=TextEntityAlignment.MIDDLE_CENTER)

            # 4. Sol Kenar Boşluğu Ek Tabloları
            self._draw_side_stamps(msp, f)

            # 5. Form 3 Antet (Ortak proje bilgisi + dinamik pafta no)
            tb = page.title_block_rect
            self._draw_table(msp, page.title_block_table, Point2D(tb.x_min, tb.y_min), table_config, doc=doc)

            # 6. Bu sayfaya yerleştirilmiş tüm tabloları çiz
            for item in page.placed_tables:
                self._draw_table(msp, item.table, item.origin, table_config, doc=doc)

        doc.saveas(output_path, encoding="utf-8")
        return True

    # Geriye dönük ve arayüz uyumluluğu için takma ad (alias)
    export_table = export

    def _get_layer_name(self, key: str, fallback: str) -> str:
        try:
            from src.services.settings import SettingsManager
            return SettingsManager.get_instance().get_layer_name(key)
        except Exception:
            return fallback

    def _setup_layers(self, doc) -> None:
        """Standart KM katmanlarını DXF belgesine ekler (SettingsManager ile senkronize)."""
        try:
            from src.services.settings import SettingsManager
            layers = SettingsManager.get_instance().get_all_cad_layers()
        except Exception:
            layers = ALL_LAYERS

        for layer_cfg in layers:
            if layer_cfg.name not in doc.layers:
                doc.layers.add(
                    name=layer_cfg.name,
                    color=layer_cfg.color,
                    linetype=layer_cfg.linetype,
                    dxfattribs={"lineweight": layer_cfg.lineweight}
                )

    def _draw_table(
        self,
        msp,
        table: Table,
        origin: Point2D,
        config: TableConfig,
        doc=None
    ) -> None:
        """Tablonun dış sınırlarını, iç ızgarasını, metinlerini ve eskizlerini çizer."""
        layout_info = table.compute_layout()
        t_w = layout_info.total_width
        t_h = layout_info.total_height
        table_top = origin.y + t_h

        layer_text = self._get_layer_name("KM_TABLO_METIN", LAYER_TEXT.name)
        layer_border = self._get_layer_name("KM_TABLO_CERCEVE", LAYER_BORDER.name)
        layer_grid = self._get_layer_name("KM_TABLO_IZGARA", LAYER_GRID.name)

        # A. Tablo Başlığı (örn: "Ведомость элементов")
        if table.title:
            title_x = origin.x + t_w / 2.0
            title_y = table_top + config.rows.title_gap
            msp.add_text(
                table.title,
                dxfattribs={
                    "layer": layer_text,
                    "height": config.typography.title_height,
                    "style": "GOST_STYLE"
                }
            ).set_placement((title_x, title_y), align=TextEntityAlignment.BOTTOM_CENTER)

        # B. Tablo Dış Çerçevesi (Kalın Çizgi)
        msp.add_lwpolyline(
            [
                (origin.x, origin.y),
                (origin.x + t_w, origin.y),
                (origin.x + t_w, table_top),
                (origin.x, table_top),
                (origin.x, origin.y),
            ],
            close=True,
            dxfattribs={"layer": layer_border}
        )

        # C. Hücreleri, İç Çizgileri ve Metinleri Çiz
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                if cell.is_merged_continuation:
                    continue  # Birleştirilmiş hücrenin devamı: İç çizgi ve metin çizilmez

                rect = table.get_cell_cad_rect(r_idx, c_idx, origin.x, origin.y, layout_info)

                # 1. İç ızgara çizgileri (İnce veya kalın çizgi)
                # Üst çizgi (dış çerçeveye denk gelmiyorsa ve cell.border_top ise)
                if cell.border_top and rect.y_max < table_top - 0.001:
                    top_layer = layer_border if getattr(cell, "border_top_thick", False) else layer_grid
                    msp.add_line(
                        (rect.x_min, rect.y_max),
                        (rect.x_max, rect.y_max),
                        dxfattribs={"layer": top_layer}
                    )
                # Sağ dikey çizgi (dış çerçeveye denk gelmiyorsa ve cell.border_right ise)
                if cell.border_right and rect.x_max < (origin.x + t_w - 0.001):
                    right_layer = layer_border if getattr(cell, "border_right_thick", False) else layer_grid
                    msp.add_line(
                        (rect.x_max, rect.y_min),
                        (rect.x_max, rect.y_max),
                        dxfattribs={"layer": right_layer}
                    )

                # 2. Hücre Metni
                if cell.text.strip():
                    self._draw_cell_text(msp, cell, rect, config)

                # 3. Kesit Eskizi / Kurumsal Logo
                if cell.sketch and cell.sketch.sketch_type != SketchType.NONE:
                    has_text = bool(cell.text and cell.text.strip())
                    self._draw_cell_sketch(msp, cell.sketch, rect, doc=doc, has_text=has_text)

    def _draw_cell_text(self, msp, cell: TableCell, rect: Rect2D, config: TableConfig) -> None:
        """Hücre metnini hizalama ve GOST kelime kaydırma (wrap) kurallarına göre çizer."""
        if not cell.text.strip():
            return

        pad_x = config.cell_padding_x
        pad_y = config.cell_padding_y
        has_logo = bool(cell.sketch and cell.sketch.sketch_type == SketchType.LOGO_EMBLEM)
        logo_reserved_w = (min(20.0, rect.width * 0.38) + 4.0) if has_logo else 0.0

        max_w = max(1.0, rect.width - logo_reserved_w - 2.0 * pad_x)
        max_h = max(1.0, rect.height - 2.0 * pad_y)

        target_font_h = (
            cell.font_size if getattr(cell, "font_size", None)
            else (config.typography.header_text_height if cell.is_header else config.typography.data_text_height)
        )
        text_lines, font_h = wrap_cell_text(cell.text, max_w, max_h, target_font_h)

        if not text_lines:
            return

        line_count = len(text_lines)
        line_spacing = font_h * 1.25

        # X Pozisyonu ve Yatay Hizalama
        if has_logo:
            if cell.halign == HAlign.LEFT:
                base_x = rect.x_min + logo_reserved_w + pad_x
                align_code = TextEntityAlignment.MIDDLE_LEFT
            elif cell.halign == HAlign.RIGHT:
                base_x = rect.x_max - pad_x
                align_code = TextEntityAlignment.MIDDLE_RIGHT
            else:
                base_x = rect.x_min + logo_reserved_w + (rect.width - logo_reserved_w) / 2.0
                align_code = TextEntityAlignment.MIDDLE_CENTER
        else:
            if cell.halign == HAlign.LEFT:
                base_x = rect.x_min + pad_x
                align_code = TextEntityAlignment.MIDDLE_LEFT
            elif cell.halign == HAlign.RIGHT:
                base_x = rect.x_max - pad_x
                align_code = TextEntityAlignment.MIDDLE_RIGHT
            else:
                base_x = rect.center_x
                align_code = TextEntityAlignment.MIDDLE_CENTER

        # Y Pozisyonu (Her satırın düşey merkez / MIDDLE Y koordinatı)
        # AutoCAD TextEntityAlignment.MIDDLE_* kullandığı için curr_y her satırın düşey orta noktasıdır.
        if cell.valign == VAlign.TOP:
            # En üst satırın üst kenarı = rect.y_max - pad_y
            start_y = rect.y_max - pad_y - (font_h / 2.0)
        elif cell.valign == VAlign.BOTTOM:
            # En alt satırın alt kenarı = rect.y_min + pad_y
            start_y = rect.y_min + pad_y + (font_h / 2.0) + (line_count - 1) * line_spacing
        else:
            # MIDDLE: Çok satırlı bloğun dikey merkezi tam olarak rect.center_y noktasına denk gelir
            start_y = rect.center_y + ((line_count - 1) * line_spacing / 2.0)

        curr_y = start_y
        layer_text = self._get_layer_name("KM_TABLO_METIN", LAYER_TEXT.name)
        for line in text_lines:
            if line.strip():
                msp.add_text(
                    line,
                    dxfattribs={
                        "layer": layer_text,
                        "height": font_h,
                        "style": "GOST_STYLE"
                    }
                ).set_placement((base_x, curr_y), align=align_code)
            curr_y -= line_spacing

    def _draw_cell_sketch(self, msp, sketch: SectionSketch, rect: Rect2D, doc=None, has_text: bool = False) -> None:
        """Hücre içindeki profil kesit eskizini veya kurumsal logoyu çizer."""
        layer_sketch = self._get_layer_name("KM_TABLO_ESKIZ", LAYER_SKETCH.name)
        # Eğer kurumsal logo resmi varsa ve doc sağlanmışsa DXF raster image olarak ekle
        if sketch.sketch_type == SketchType.LOGO_EMBLEM and sketch.image_path and os.path.exists(sketch.image_path) and doc and PilImage:
            try:
                with PilImage.open(sketch.image_path) as img:
                    img_w_px, img_h_px = img.size
                if img_w_px > 0 and img_h_px > 0:
                    if has_text:
                        avail_w = min(20.0, rect.width * 0.38)
                        avail_h = max(2.0, rect.height - 4.0)
                    else:
                        avail_w = max(2.0, rect.width - 6.0)
                        avail_h = max(2.0, rect.height - 4.0)

                    aspect = img_w_px / img_h_px
                    if (avail_w / avail_h) > aspect:
                        cad_h = avail_h
                        cad_w = avail_h * aspect
                    else:
                        cad_w = avail_w
                        cad_h = avail_w / aspect

                    if has_text:
                        insert_x = rect.x_min + 3.0
                    else:
                        insert_x = rect.x_min + (rect.width - cad_w) / 2.0

                    insert_y = rect.y_min + (rect.height - cad_h) / 2.0
                    img_def = doc.add_image_def(sketch.image_path, (img_w_px, img_h_px))
                    msp.add_image(
                        img_def,
                        insert=(insert_x, insert_y),
                        size_in_units=(cad_w, cad_h),
                        dxfattribs={"layer": layer_sketch}
                    )
                    return
            except Exception:
                pass

        prims = sketch.generate_primitives(rect.x, rect.y, rect.width, rect.height)
        for prim in prims:
            if prim.kind == "line":
                x1, y1, x2, y2 = prim.coords
                msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer_sketch})
            elif prim.kind == "rect":
                rx, ry, rw, rh = prim.coords
                msp.add_lwpolyline(
                    [(rx, ry), (rx + rw, ry), (rx + rw, ry + rh), (rx, ry + rh)],
                    close=True,
                    dxfattribs={"layer": layer_sketch}
                )
            elif prim.kind == "circle":
                cx, cy, r = prim.coords
                msp.add_circle((cx, cy), r, dxfattribs={"layer": layer_sketch})
            elif prim.kind == "leader_text" and prim.text:
                tx, ty, _, _ = prim.coords
                msp.add_text(
                    prim.text,
                    dxfattribs={"layer": layer_sketch, "height": 1.8, "style": "GOST_STYLE"}
                ).set_placement((tx, ty), align=TextEntityAlignment.BOTTOM_LEFT)

    def _draw_sheet_frames_only(
        self,
        msp,
        calc: CalculatedLayout,
        layout_cfg: Optional[LayoutConfig] = None
    ) -> None:
        """Sadece ГОСТ Р 21.101-2020 standart dış ve iç sayfa çerçevelerini çizer (antet hariç)."""
        s = calc.sheet_rect
        f = calc.inner_frame_rect
        if not s or not f:
            return

        layer_grid = self._get_layer_name("KM_TABLO_IZGARA", LAYER_GRID.name)
        layer_sheet = self._get_layer_name("KM_SAYFA_CERCEVE", LAYER_SHEET_FRAME.name)
        layer_text = self._get_layer_name("KM_TABLO_METIN", LAYER_TEXT.name)

        # 1. Sayfa Dış Sınırı (İnce Çizgi)
        msp.add_lwpolyline(
            [(s.x_min, s.y_min), (s.x_max, s.y_min), (s.x_max, s.y_max), (s.x_min, s.y_max)],
            close=True,
            dxfattribs={"layer": layer_grid}
        )

        # 2. İç Çizim Çerçevesi (Kalın Çizgi: sol 20 mm, diğerleri 5 mm)
        msp.add_lwpolyline(
            [(f.x_min, f.y_min), (f.x_max, f.y_min), (f.x_max, f.y_max), (f.x_min, f.y_max)],
            close=True,
            dxfattribs={"layer": layer_sheet}
        )

        # 3. Sayfa Format Etiketi (ГОСТ 2.301-68 / СПДС: alt 5 mm marjinde, sağ köşe Form 3 altında ortalı)
        if layout_cfg and hasattr(layout_cfg, "get_format_designation"):
            fmt_text = layout_cfg.get_format_designation()
            fmt_cad_x = f.x_max - 25.0
            fmt_cad_y = (s.y_min + f.y_min) / 2.0
            msp.add_text(
                fmt_text,
                dxfattribs={"layer": layer_text, "height": 2.5, "style": "GOST_STYLE"}
            ).set_placement((fmt_cad_x, fmt_cad_y), align=TextEntityAlignment.MIDDLE_CENTER)

        # 4. Sol Kenar Boşluğu Ek Tabloları / Yan Şerit (ГОСТ 2.104 / ГОСТ Р 21.101: İnventar & Согласовано)
        self._draw_side_stamps(msp, f)

    def _draw_side_stamps(self, msp, f: Rect2D) -> None:
        """ГОСТ 2.104 ve ГОСТ Р 21.101 standart sol kenar boşluğu (20 mm) ek tabloları (İnventar & Согласовано)."""
        x0 = f.x_min
        y0 = f.y_min

        layer_sheet = self._get_layer_name("KM_SAYFA_CERCEVE", LAYER_SHEET_FRAME.name)
        layer_grid = self._get_layer_name("KM_TABLO_IZGARA", LAYER_GRID.name)
        layer_text = self._get_layer_name("KM_TABLO_METIN", LAYER_TEXT.name)

        # 1. Tablo 1: İnventar Bilgileri (85 x 12 mm)
        # Dış Kalın Çerçeve
        msp.add_lwpolyline(
            [(x0, y0), (x0 - 12.0, y0), (x0 - 12.0, y0 + 85.0), (x0, y0 + 85.0)],
            close=False,
            dxfattribs={"layer": layer_sheet}
        )
        # Boyuna İnce Ayırıcı (5 mm metin + 7 mm boş alan)
        msp.add_line((x0 - 7.0, y0), (x0 - 7.0, y0 + 85.0), dxfattribs={"layer": layer_grid})
        # Enine İnce Ayırıcılar
        msp.add_line((x0 - 12.0, y0 + 25.0), (x0, y0 + 25.0), dxfattribs={"layer": layer_grid})
        msp.add_line((x0 - 12.0, y0 + 60.0), (x0, y0 + 60.0), dxfattribs={"layer": layer_grid})

        # Metinler (90 derece saat yönünün tersine döndürülmüş)
        inv_texts = [
            ("Инв. № подл.", y0 + 12.5),
            ("Подп. и дата", y0 + 42.5),
            ("Взам. инв. №", y0 + 72.5),
        ]
        for txt, cad_y in inv_texts:
            msp.add_text(
                txt,
                dxfattribs={"layer": layer_text, "height": 2.5, "style": "GOST_STYLE", "rotation": 90.0}
            ).set_placement((x0 - 9.5, cad_y), align=TextEntityAlignment.MIDDLE_CENTER)

        # 2. Tablo 2: Согласовано (65 x 15 mm)
        # Dış Kalın Çerçeve
        msp.add_lwpolyline(
            [(x0 - 12.0, y0 + 85.0), (x0 - 15.0, y0 + 85.0), (x0 - 15.0, y0 + 150.0), (x0, y0 + 150.0)],
            close=False,
            dxfattribs={"layer": layer_sheet}
        )
        # Boyuna İnce Ayırıcılar (5 mm başlık + 5 mm satır 1 + 5 mm satır 2)
        msp.add_line((x0 - 10.0, y0 + 85.0), (x0 - 10.0, y0 + 150.0), dxfattribs={"layer": layer_grid})
        msp.add_line((x0 - 5.0, y0 + 85.0), (x0 - 5.0, y0 + 150.0), dxfattribs={"layer": layer_grid})
        # Enine İnce Ayırıcılar (İç 10 mm ızgara: 20 mm, 20 mm, 15 mm, 10 mm)
        for dy in [20.0, 40.0, 55.0]:
            msp.add_line((x0 - 10.0, y0 + 85.0 + dy), (x0, y0 + 85.0 + dy), dxfattribs={"layer": layer_grid})

        # Başlık Metni
        msp.add_text(
            "Согласовано",
            dxfattribs={"layer": layer_text, "height": 2.5, "style": "GOST_STYLE", "rotation": 90.0}
        ).set_placement((x0 - 12.5, y0 + 117.5), align=TextEntityAlignment.MIDDLE_CENTER)

    def _draw_sheet_and_titleblock(
        self,
        msp,
        calc: CalculatedLayout,
        layout_cfg: LayoutConfig,
        table_config: TableConfig,
        doc=None
    ) -> None:
        """ГОСТ Р 21.101-2020 standart sayfa çerçevesi ve Form 3 ana antetini çizer."""
        self._draw_sheet_frames_only(msp, calc, layout_cfg=layout_cfg)

        # 3. Form 3 Ana Antet Detayları (185 x 55 mm)
        self._draw_form3_titleblock_details(msp, calc.title_block_rect, layout_cfg, table_config, doc=doc)

    def _draw_form3_titleblock_details(
        self,
        msp,
        tb: Rect2D,
        layout_cfg: Optional[LayoutConfig] = None,
        table_config: Optional[TableConfig] = None,
        doc=None
    ) -> None:
        """ГОСТ Form 3 ana antetinin tam detaylı iç çizgilerini, metinlerini ve etiketlerini çizer."""
        from src.tables.title_block.builder import create_title_block_table
        from src.tables.title_block.model import TitleBlockDocument

        tb_doc = getattr(layout_cfg, "title_block_doc", None) if layout_cfg else None
        if not tb_doc:
            tb_doc = TitleBlockDocument()

        tb_table = create_title_block_table(tb_doc)
        cfg = table_config or DEFAULT_TABLE_CONFIG
        self._draw_table(msp, tb_table, Point2D(tb.x_min, tb.y_min), cfg, doc=doc)
