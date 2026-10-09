"""
CAD Vektör Önizleme Tuvali (PySide6 QGraphicsView & QGraphicsScene).
Donanım hızlandırmalı, pürüzsüz anti-aliased CAD çizim motoru.
Milimetrik CAD koordinatları, fare odaklı akıcı zoom, pan ve canlı koordinat takibi.
AutoCAD DXF çıktısıyla %100 birebir görsel ve geometrik eşleşme sağlar.
"""
import os
from typing import Optional, Tuple
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontMetricsF, QWheelEvent,
    QMouseEvent, QPixmap, QTransform
)
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem,
    QGraphicsSimpleTextItem, QGraphicsItemGroup
)

from src.config.table_config import TableConfig, DEFAULT_TABLE_CONFIG
from src.config.sheet_config import LayoutConfig, DEFAULT_LAYOUT_CONFIG, TablePlacement
from src.models.geometry import Rect2D, Point2D
from src.models.sheet import SheetLayoutCalculator, CalculatedLayout
from src.models.sketch import SectionSketch, SketchType
from src.models.table import Table, TableCell, HAlign, VAlign
from src.models.text_layout import wrap_cell_text
from src.ui import theme


class CadGraphicsView(QGraphicsView):
    """
    AutoCAD model uzayı tarzı yüksek performanslı 2D vektör tuvali.
    """
    cursor_pos_changed = Signal(float, float)  # (cad_x_mm, cad_y_mm)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Görünüm ve Donanım Hızlandırma Ayarları
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Arka plan ve fare etkileşimi
        self.setBackgroundBrush(QBrush(QColor(theme.COLOR_CAD_BG)))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setMouseTracking(True)

        self._table: Optional[Table] = None
        self._table_config: TableConfig = DEFAULT_TABLE_CONFIG
        self._layout_config: LayoutConfig = DEFAULT_LAYOUT_CONFIG

    def set_data(
        self,
        table: Table,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None,
        auto_fit: bool = True
    ) -> None:
        """Yeni tablo modelini ve konfigürasyonunu yükler, tuvali yeniden çizer."""
        self._table = table
        if table_config:
            self._table_config = table_config
        if layout_config:
            self._layout_config = layout_config
        self.redraw()
        if auto_fit:
            self.fit_to_view()

    def set_table(
        self,
        table: Table,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None
    ) -> None:
        """Yeni tablo modelini ve konfigürasyonunu yükler, tuvali yeniden çizer."""
        self.set_data(table, table_config=table_config, layout_config=layout_config, auto_fit=True)

    def update_layout_config(self, layout_config: LayoutConfig) -> None:
        """Sadece pafta veya yerleşim ayarlarını günceller."""
        self._layout_config = layout_config
        self.redraw()
        self.fit_to_view()

    def fit_to_view(self) -> None:
        """Tüm paftayı veya tabloyu ekrana tam sığdırır."""
        if self._scene.items():
            rect = self._scene.itemsBoundingRect()
            margin = 25.0
            rect.adjust(-margin, -margin, margin, margin)
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def zoom_in(self) -> None:
        """Yakınlaştır."""
        self.scale(1.2, 1.2)

    def zoom_out(self) -> None:
        """Uzaklaştır."""
        self.scale(0.833, 0.833)

    def zoom_actual(self) -> None:
        """Ölçeği %100 (birebir) seviyesine sıfırlar."""
        self.resetTransform()

    reset_zoom = zoom_actual

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Fare imlecinin olduğu noktaya odaklı pürüzsüz zoom."""
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 0.87
        self.scale(zoom_factor, zoom_factor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        scene_pt = self.mapToScene(event.pos())
        # Scene (X, Y_down) -> CAD mm (X, Y_up)
        cad_x = scene_pt.x()
        cad_y = -scene_pt.y()
        self.cursor_pos_changed.emit(cad_x, cad_y)

    def redraw(self) -> None:
        self._scene.clear()
        if not self._table:
            return

        title_clearance = (
            self._table_config.rows.title_gap + self._table_config.typography.title_height + 3.0
        ) if self._table.title else 0.0

        calc = SheetLayoutCalculator.calculate(
            self._table, self._layout_config, title_clearance=title_clearance
        )
        self._calc_layout = calc

        is_sheet = self._layout_config.placement != TablePlacement.STANDALONE
        is_title_block = (
            getattr(self._table, "id", "") == "title_block" or
            (hasattr(self._table, "columns") and len(self._table.columns) == 10 and abs(self._table.total_width - 185.0) < 0.1)
        )

        # 1. Sayfa Çizimi (Pafta kağıdı, çerçeve ve Form 3 antet)
        if is_sheet and calc.sheet_rect and calc.inner_frame_rect:
            self._draw_sheet(calc, suppress_title_block=is_title_block)

        # 2. Tablo Çizimi (Eğer tablo kendisi antet ise paftada tek kez sağ alta çizilir)
        if is_sheet and is_title_block and calc.title_block_rect:
            self._draw_table_content(Point2D(calc.title_block_rect.x_min, calc.title_block_rect.y_min), is_sheet)
        else:
            self._draw_table_content(calc.table_origin, is_sheet)

    def _cad_to_scene(self, cad_x: float, cad_y: float) -> Tuple[float, float]:
        """CAD koordinatlarını (Y yukarı) QGraphicsScene koordinatlarına (Y aşağı) dönüştürür."""
        return cad_x, -cad_y

    def _draw_sheet(self, calc: CalculatedLayout, suppress_title_block: bool = False) -> None:
        """ГОСТ 2.301 Pafta ve ГОСТ 21.101 Çizim Çerçevesi + Form 3 Antet."""
        s = calc.sheet_rect
        sx, sy = self._cad_to_scene(s.x_min, s.y_max)
        sw = s.width
        sh = s.height

        # Koyu Teknik Pafta Çerçevesi
        paper_brush = QBrush(QColor("#080808"))
        paper_pen = QPen(QColor(theme.COLOR_ACCENT), 0.6)
        self._scene.addRect(sx, sy, sw, sh, paper_pen, paper_brush)

        # ГОСТ 21.101 İç Çizim Çerçevesi (sol 20mm, diğerleri 5mm kalın çizgi)
        f = calc.inner_frame_rect
        fx, fy = self._cad_to_scene(f.x_min, f.y_max)
        frame_pen = QPen(QColor(theme.COLOR_ACCENT), 0.8)
        self._scene.addRect(fx, fy, f.width, f.height, frame_pen, QBrush(Qt.BrushStyle.NoBrush))

        # ГОСТ 2.301-68 / СПДС Pafta Format Etiketi (Sağ alt köşe, alt 5 mm marjininde Form 3 altında ortalı)
        if hasattr(self._layout_config, "get_format_designation"):
            fmt_text = self._layout_config.get_format_designation()
            fmt_cad_x = f.x_max - 25.0
            fmt_cad_y = (s.y_min + f.y_min) / 2.0
            px, py = self._cad_to_scene(fmt_cad_x, fmt_cad_y)
            t_fmt = self._scene.addSimpleText(fmt_text)
            f_fmt = QFont("ISOCPEUR")
            if not f_fmt.exactMatch():
                f_fmt = QFont("Segoe UI")
            f_fmt.setPixelSize(36)
            fm_fmt = QFontMetricsF(f_fmt)
            cap_h = fm_fmt.capHeight() if fm_fmt.capHeight() > 0 else (fm_fmt.ascent() * 0.8)
            font_h = 2.5
            scale_f = font_h / (cap_h if cap_h > 0 else 36.0)
            t_fmt.setFont(f_fmt)
            t_fmt.setBrush(QBrush(QColor(theme.COLOR_TEXT_PRIMARY)))
            t_fmt.setScale(scale_f)
            lw = t_fmt.boundingRect().width() * scale_f
            lh = t_fmt.boundingRect().height() * scale_f
            t_fmt.setPos(px - lw / 2.0, py - lh / 2.0)

        # ГОСТ 2.104 ve ГОСТ Р 21.101 Sol Kenar Boşluğu Ek Tabloları (İnventar & Согласовано)
        self._draw_side_stamps(f)

        # ГОСТ 21.101 Form 3 Ana Antet (185 x 55 mm)
        tb = calc.title_block_rect
        if tb and not suppress_title_block:
            from src.tables.title_block.builder import create_title_block_table
            from src.tables.title_block.model import TitleBlockDocument
            tb_doc = getattr(self._layout_config, "title_block_doc", None) or TitleBlockDocument()
            tb_table = create_title_block_table(tb_doc)
            self._draw_table_content(Point2D(tb.x_min, tb.y_min), is_sheet=True, table=tb_table)

        # ----------------------------------------------------------------------
        # CAD KOORDİNAT EKSENLERİ (X ve Y Okları)
        # ----------------------------------------------------------------------
        ax_x = f.x_min + 12.0
        ax_y = f.y_min + 12.0
        orig_px, orig_py = self._cad_to_scene(ax_x, ax_y)
        axis_pen = QPen(QColor(theme.COLOR_TEXT_PRIMARY), 0.6)

        # X Ekseni (Sağa ok)
        x_end_px, x_end_py = self._cad_to_scene(ax_x + 18.0, ax_y)
        self._scene.addLine(orig_px, orig_py, x_end_px, x_end_py, axis_pen)
        self._scene.addLine(x_end_px, x_end_py, x_end_px - 3, x_end_py - 2, axis_pen)
        self._scene.addLine(x_end_px, x_end_py, x_end_px - 3, x_end_py + 2, axis_pen)
        lbl_x = self._scene.addSimpleText("X")
        lbl_x.setFont(QFont("ISOCPEUR", 4, QFont.Weight.Bold))
        lbl_x.setBrush(QBrush(QColor(theme.COLOR_TEXT_PRIMARY)))
        lbl_x.setPos(x_end_px + 3, x_end_py - 4)

        # Y Ekseni (Yukarı ok)
        y_end_px, y_end_py = self._cad_to_scene(ax_x, ax_y + 18.0)
        self._scene.addLine(orig_px, orig_py, y_end_px, y_end_py, axis_pen)
        self._scene.addLine(y_end_px, y_end_py, y_end_px - 2, y_end_py + 3, axis_pen)
        self._scene.addLine(y_end_px, y_end_py, y_end_px + 2, y_end_py + 3, axis_pen)
        lbl_y = self._scene.addSimpleText("Y")
        lbl_y.setFont(QFont("ISOCPEUR", 4, QFont.Weight.Bold))
        lbl_y.setBrush(QBrush(QColor(theme.COLOR_TEXT_PRIMARY)))
        lbl_y.setPos(y_end_px - 2, y_end_py - 8)

    def _draw_side_stamps(self, f: Rect2D) -> None:
        """ГОСТ 2.104 ve ГОСТ Р 21.101 standart sol kenar boşluğu (20 mm) ek tabloları (İnventar & Согласовано)."""
        x0 = f.x_min
        y0 = f.y_min

        thick_pen = QPen(QColor(theme.COLOR_ACCENT), 0.8)
        thin_pen = QPen(QColor(theme.COLOR_ACCENT), 0.4)
        text_color = QColor(theme.COLOR_TEXT_PRIMARY)

        # 1. Tablo 1: İnventar Bilgileri (85 x 12 mm)
        # Dış Kalın Çerçeve
        p1 = [
            self._cad_to_scene(x0, y0),
            self._cad_to_scene(x0 - 12.0, y0),
            self._cad_to_scene(x0 - 12.0, y0 + 85.0),
            self._cad_to_scene(x0, y0 + 85.0)
        ]
        for i in range(len(p1) - 1):
            self._scene.addLine(p1[i][0], p1[i][1], p1[i + 1][0], p1[i + 1][1], thick_pen)

        # Boyuna İnce Ayırıcı (5 mm metin + 7 mm boş alan)
        x_la, y_la = self._cad_to_scene(x0 - 7.0, y0)
        x_lb, y_lb = self._cad_to_scene(x0 - 7.0, y0 + 85.0)
        self._scene.addLine(x_la, y_la, x_lb, y_lb, thin_pen)

        # Enine İnce Ayırıcılar
        for y_d in [y0 + 25.0, y0 + 60.0]:
            xa, ya = self._cad_to_scene(x0 - 12.0, y_d)
            xb, yb = self._cad_to_scene(x0, y_d)
            self._scene.addLine(xa, ya, xb, yb, thin_pen)

        font = QFont("ISOCPEUR")
        if not font.exactMatch():
            font = QFont("Segoe UI")
        font.setPixelSize(36)
        fm = QFontMetricsF(font)
        cap_h = fm.capHeight() if fm.capHeight() > 0 else 30.0
        font_h = 2.5
        scale_f = font_h / cap_h

        inv_texts = [
            ("Инв. № подл.", y0 + 12.5),
            ("Подп. и дата", y0 + 42.5),
            ("Взам. инв. №", y0 + 72.5),
        ]
        for txt, cad_y in inv_texts:
            item = self._scene.addSimpleText(txt)
            item.setFont(font)
            item.setBrush(QBrush(text_color))
            br = item.boundingRect()
            sc_x, sc_y = self._cad_to_scene(x0 - 9.5, cad_y)
            t = QTransform()
            t.translate(sc_x, sc_y)
            t.rotate(-90.0)
            t.scale(scale_f, scale_f)
            t.translate(-br.width() / 2.0, -br.height() / 2.0)
            item.setTransform(t)

        # 2. Tablo 2: Согласовано (65 x 15 mm)
        # Dış Kalın Çerçeve
        p2 = [
            self._cad_to_scene(x0 - 12.0, y0 + 85.0),
            self._cad_to_scene(x0 - 15.0, y0 + 85.0),
            self._cad_to_scene(x0 - 15.0, y0 + 150.0),
            self._cad_to_scene(x0, y0 + 150.0)
        ]
        for i in range(len(p2) - 1):
            self._scene.addLine(p2[i][0], p2[i][1], p2[i + 1][0], p2[i + 1][1], thick_pen)

        # Boyuna İnce Ayırıcılar
        for x_d in [x0 - 10.0, x0 - 5.0]:
            xa, ya = self._cad_to_scene(x_d, y0 + 85.0)
            xb, yb = self._cad_to_scene(x_d, y0 + 150.0)
            self._scene.addLine(xa, ya, xb, yb, thin_pen)

        # Enine İnce Ayırıcılar
        for dy in [20.0, 40.0, 55.0]:
            xa, ya = self._cad_to_scene(x0 - 10.0, y0 + 85.0 + dy)
            xb, yb = self._cad_to_scene(x0, y0 + 85.0 + dy)
            self._scene.addLine(xa, ya, xb, yb, thin_pen)

        # Başlık Metni
        item_s = self._scene.addSimpleText("Согласовано")
        item_s.setFont(font)
        item_s.setBrush(QBrush(text_color))
        br_s = item_s.boundingRect()
        sc_x, sc_y = self._cad_to_scene(x0 - 12.5, y0 + 117.5)
        t_s = QTransform()
        t_s.translate(sc_x, sc_y)
        t_s.rotate(-90.0)
        t_s.scale(scale_f, scale_f)
        t_s.translate(-br_s.width() / 2.0, -br_s.height() / 2.0)
        item_s.setTransform(t_s)

    def _draw_table_content(
        self,
        origin: Point2D,
        is_sheet: bool,
        table: Optional[Table] = None
    ) -> None:
        """Tablo çizgilerini, metinlerini ve kesit geometrilerini çizer."""
        tbl = table or self._table
        config = self._table_config
        layout_info = tbl.compute_layout()
        t_w = layout_info.total_width
        t_h = layout_info.total_height
        table_top = origin.y + t_h

        border_color = QColor(theme.COLOR_ACCENT)
        grid_color = QColor(theme.COLOR_ACCENT)
        text_color = QColor(theme.COLOR_TEXT_PRIMARY)

        thick_pen = QPen(border_color, 0.7)
        thick_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        thin_pen = QPen(grid_color, 0.35)

        # A. Tablo Başlığı ("Ведомость элементов")
        if tbl.title:
            title_cad_y = table_top + config.rows.title_gap + (config.typography.title_height / 2.0)
            tx, ty = self._cad_to_scene(origin.x + t_w / 2.0, title_cad_y)

            title_item = self._scene.addSimpleText(tbl.title)
            font_title = QFont("ISOCPEUR")
            if not font_title.exactMatch():
                font_title = QFont("Segoe UI")
            font_title.setWeight(QFont.Weight.Bold)
            font_title.setPixelSize(36)
            fm_t = QFontMetricsF(font_title)
            ref_th = fm_t.capHeight() if fm_t.capHeight() > 0 else 30.0
            t_scale = (config.typography.title_height * 0.95) / ref_th
            title_item.setFont(font_title)
            title_item.setScale(t_scale)
            title_item.setBrush(QBrush(QColor(theme.COLOR_TEXT_PRIMARY)))

            # Merkeze hizala
            br = title_item.boundingRect()
            title_item.setPos(tx - (br.width() * t_scale) / 2.0, ty - (br.height() * t_scale) / 2.0)

        # B. Dış Çerçeve
        top_left_x, top_left_y = self._cad_to_scene(origin.x, table_top)
        if not is_sheet:
            bg_brush = QBrush(QColor("#080808"))
            self._scene.addRect(top_left_x, top_left_y, t_w, t_h, thick_pen, bg_brush)
        else:
            self._scene.addRect(top_left_x, top_left_y, t_w, t_h, thick_pen)

        # C. Hücreler, İç Izgara Çizgileri ve Metinler
        for r_idx, row in enumerate(tbl.rows):
            for c_idx, cell in enumerate(row.cells):
                if cell.is_merged_continuation:
                    continue  # Birleştirilmiş hücrelerin devamına iç çizgi/metin çizilmez

                rect = tbl.get_cell_cad_rect(r_idx, c_idx, origin.x, origin.y, layout_info)
                cx1, cy_top = self._cad_to_scene(rect.x_min, rect.y_max)
                cx2, cy_bot = self._cad_to_scene(rect.x_max, rect.y_min)
                cw = rect.width
                ch = rect.height

                # Üst iç çizgi (İnce veya kalın)
                if cell.border_top and rect.y_max < table_top - 0.001:
                    pen_top = thick_pen if getattr(cell, "border_top_thick", False) else thin_pen
                    self._scene.addLine(cx1, cy_top, cx2, cy_top, pen_top)

                # Sağ iç çizgi (İnce veya kalın)
                if cell.border_right and rect.x_max < (origin.x + t_w - 0.001):
                    pen_right = thick_pen if getattr(cell, "border_right_thick", False) else thin_pen
                    self._scene.addLine(cx2, cy_top, cx2, cy_bot, pen_right)

                # Hücre Metni (Auto Word-Wrap & Gerçek CAD Font Oranları)
                if cell.text.strip():
                    pad_x = config.cell_padding_x
                    pad_y = config.cell_padding_y
                    has_logo = bool(cell.sketch and cell.sketch.sketch_type == SketchType.LOGO_EMBLEM)
                    logo_reserved_w = (min(20.0, cw * 0.38) + 4.0) if has_logo else 0.0

                    max_w = max(1.0, cw - logo_reserved_w - 2.0 * pad_x)
                    max_h = max(1.0, ch - 2.0 * pad_y)

                    target_font_h = (
                        cell.font_size if getattr(cell, "font_size", None)
                        else (config.typography.header_text_height if cell.is_header else config.typography.data_text_height)
                    )
                    text_lines, font_h = wrap_cell_text(cell.text, max_w, max_h, target_font_h)

                    if text_lines:
                        cell_font = QFont("ISOCPEUR")
                        if not cell_font.exactMatch():
                            cell_font = QFont("Segoe UI")
                        is_bold = cell.is_header or getattr(cell, "is_bold", False)
                        if is_bold:
                            cell_font.setWeight(QFont.Weight.Bold)

                        ref_size = 36.0
                        cell_font.setPixelSize(int(ref_size))
                        fm = QFontMetricsF(cell_font)
                        cap_h = fm.capHeight() if fm.capHeight() > 0 else (fm.ascent() * 0.8)
                        scale_factor = font_h / (cap_h if cap_h > 0 else ref_size)

                        line_spacing = font_h * 1.25
                        item_h = fm.height() * scale_factor
                        actual_total_h = (len(text_lines) - 1) * line_spacing + item_h

                        if cell.valign == VAlign.TOP:
                            cur_y = cy_top + pad_y
                        elif cell.valign == VAlign.BOTTOM:
                            cur_y = cy_bot - pad_y - actual_total_h
                        else:  # MIDDLE
                            cur_y = cy_top + (ch - actual_total_h) / 2.0

                        for l in text_lines:
                            if not l.strip():
                                cur_y += line_spacing
                                continue
                            t_item = self._scene.addSimpleText(l)
                            t_item.setFont(cell_font)
                            t_item.setBrush(QBrush(text_color))
                            t_item.setScale(scale_factor)

                            line_w = t_item.boundingRect().width() * scale_factor
                            if has_logo:
                                if cell.halign == HAlign.LEFT:
                                    pos_x = cx1 + logo_reserved_w + pad_x
                                elif cell.halign == HAlign.RIGHT:
                                    pos_x = cx2 - pad_x - line_w
                                else:  # CENTER in remaining space
                                    pos_x = cx1 + logo_reserved_w + (cw - logo_reserved_w - line_w) / 2.0
                            else:
                                if cell.halign == HAlign.LEFT:
                                    pos_x = cx1 + pad_x
                                elif cell.halign == HAlign.RIGHT:
                                    pos_x = cx2 - pad_x - line_w
                                else:  # CENTER
                                    pos_x = cx1 + (cw - line_w) / 2.0

                            t_item.setPos(pos_x, cur_y)
                            cur_y += line_spacing

                # Kesit Eskizi / Kurumsal Logo
                if cell.sketch and cell.sketch.sketch_type != SketchType.NONE:
                    self._draw_sketch(cell.sketch, rect, border_color)

    def _draw_sketch(self, sketch: SectionSketch, rect: Rect2D, color: QColor) -> None:
        """Hücre içerisine parametrik kesit eskizini veya logoyu çizer."""
        cx1, cy_top = self._cad_to_scene(rect.x_min, rect.y_max)

        # Kurumsal logo resmi varsa çiz
        if sketch.sketch_type == SketchType.LOGO_EMBLEM and sketch.image_path and os.path.exists(sketch.image_path):
            pixmap = QPixmap(sketch.image_path)
            if not pixmap.isNull():
                avail_w = min(20.0, rect.width * 0.38)
                avail_h = max(2.0, rect.height - 4.0)
                scaled = pixmap.scaled(
                    int(avail_w * 4.0), int(avail_h * 4.0),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                img_item = self._scene.addPixmap(scaled)
                img_scale = avail_h / max(1.0, float(scaled.height()))
                img_item.setScale(img_scale)
                px = cx1 + 3.0
                py = cy_top + (rect.height - scaled.height() * img_scale) / 2.0
                img_item.setPos(px, py)
                return

        pen = QPen(color, 0.4)
        prims = sketch.generate_primitives(rect.x, rect.y, rect.width, rect.height)

        for prim in prims:
            if prim.kind == "line":
                p1 = self._cad_to_scene(prim.coords[0], prim.coords[1])
                p2 = self._cad_to_scene(prim.coords[2], prim.coords[3])
                self._scene.addLine(p1[0], p1[1], p2[0], p2[1], pen)
            elif prim.kind == "rect":
                rx, ry, rw, rh = prim.coords
                px, py = self._cad_to_scene(rx, ry + rh)
                self._scene.addRect(px, py, rw, rh, pen)
            elif prim.kind == "circle":
                cx, cy, r = prim.coords
                px, py = self._cad_to_scene(cx - r, cy + r)
                self._scene.addEllipse(px, py, r * 2.0, r * 2.0, pen)
            elif prim.kind == "leader_text" and prim.text:
                px, py = self._cad_to_scene(prim.coords[0], prim.coords[1])
                t_item = self._scene.addSimpleText(prim.text)
                t_font = QFont("ISOCPEUR")
                t_font.setPixelSize(30)
                t_scale = 1.8 / 24.0
                t_item.setFont(t_font)
                t_item.setScale(t_scale)
                t_item.setBrush(QBrush(color))
                t_item.setPos(px, py)
