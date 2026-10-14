"""
KM Studio - Vector PDF Exporter (QPdfWriter).
ГОСТ Р 21.101-2020 / ГОСТ 2.301 standartlarına uygun 1:1 ölçekli vektör PDF üretimi.
Tekil paftalar ve çoklu pafta (MultiSheetLayout) için sayfa sayfa vektör PDF çıktısı.
"""
import os
from typing import Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPdfWriter, QPageSize, QPainter
from PySide6.QtCore import QSizeF, QMarginsF, QRectF

from src.config.table_config import TableConfig, DEFAULT_TABLE_CONFIG
from src.config.sheet_config import LayoutConfig, DEFAULT_LAYOUT_CONFIG
from src.models.table import Table
from src.models.multi_sheet import MultiSheetLayout
from src.ui.preview_canvas import CadGraphicsView


class PdfExporter:
    """
    AutoCAD tarzı 1:1 ölçekli, vektörel, aranabilir Kiril metinli PDF dışa aktarıcı.
    """
    def __init__(self, resolution_dpi: int = 300):
        self.resolution_dpi = resolution_dpi
        self._ensure_qapp()

    def _ensure_qapp(self):
        if not QApplication.instance():
            self._app = QApplication([])

    def export(
        self,
        table: Table,
        output_path: str,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None
    ) -> bool:
        """export_sheet için alias metot."""
        return self.export_sheet(table, output_path, table_config, layout_config)

    def export_sheet(
        self,
        table: Table,
        output_path: str,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None
    ) -> bool:
        """
        Tek bir tabloyu seçili pafta ebadı ve Form 3 antetine göre vektör PDF olarak dışa aktarır.
        """
        self._ensure_qapp()
        tbl_cfg = table_config or DEFAULT_TABLE_CONFIG
        lay_cfg = layout_config or DEFAULT_LAYOUT_CONFIG

        # Pafta boyutlarını al (mm)
        sheet_w, sheet_h = lay_cfg.get_sheet_dimensions()

        # Hedef klasörü hazırla
        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        writer = QPdfWriter(output_path)
        writer.setResolution(self.resolution_dpi)
        page_size = QPageSize(QSizeF(sheet_w, sheet_h), QPageSize.Unit.Millimeter)
        writer.setPageSize(page_size)
        writer.setPageMargins(QMarginsF(0, 0, 0, 0))

        # Çizim tuvali (Baskı modunda: beyaz kağıt, siyah teknik çizgiler)
        view = CadGraphicsView()
        view.print_mode = True
        view.set_data(table, tbl_cfg, lay_cfg, auto_fit=False)
        scene = view._scene

        painter = QPainter(writer)
        try:
            scale = self.resolution_dpi / 25.4
            painter.scale(scale, scale)

            # Scene rect: CAD (0,0) -> Scene (0, -sheet_h)
            scene_rect = QRectF(0.0, -sheet_h, sheet_w, sheet_h)
            target_rect = QRectF(0.0, 0.0, sheet_w, sheet_h)
            scene.render(painter, target_rect, scene_rect)
        finally:
            painter.end()

        return os.path.exists(output_path) and os.path.getsize(output_path) > 0

    def export_multi_sheet(
        self,
        multi_sheet_layout: MultiSheetLayout,
        output_path: str,
        table_config: Optional[TableConfig] = None,
        layout_config: Optional[LayoutConfig] = None
    ) -> bool:
        """
        Çoklu pafta yerleşimini (her sayfa ayrı bir pafta olacak şekilde) çok sayfalı vektör PDF olarak dışa aktarır.
        """
        self._ensure_qapp()
        if not multi_sheet_layout or not multi_sheet_layout.pages:
            raise ValueError("Dışa aktarılacak çoklu pafta sayfası bulunamadı.")

        tbl_cfg = table_config or DEFAULT_TABLE_CONFIG
        lay_cfg = layout_config or DEFAULT_LAYOUT_CONFIG

        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        first_page = multi_sheet_layout.pages[0]
        sheet_w = first_page.sheet_rect.width
        sheet_h = first_page.sheet_rect.height

        writer = QPdfWriter(output_path)
        writer.setResolution(self.resolution_dpi)
        page_size = QPageSize(QSizeF(sheet_w, sheet_h), QPageSize.Unit.Millimeter)
        writer.setPageSize(page_size)
        writer.setPageMargins(QMarginsF(0, 0, 0, 0))

        view = CadGraphicsView()
        view.print_mode = True
        view._table_config = tbl_cfg
        view._layout_config = lay_cfg
        scene = view._scene

        painter = QPainter(writer)
        try:
            scale = self.resolution_dpi / 25.4

            for idx, page in enumerate(multi_sheet_layout.pages):
                if idx > 0:
                    writer.newPage()

                p_w = page.sheet_rect.width
                p_h = page.sheet_rect.height

                # Tek sayfayı çiz
                view.render_single_sheet_page(page, auto_fit=False)

                painter.save()
                painter.scale(scale, scale)
                scene_rect = QRectF(0.0, -p_h, p_w, p_h)
                target_rect = QRectF(0.0, 0.0, p_w, p_h)
                scene.render(painter, target_rect, scene_rect)
                painter.restore()
        finally:
            painter.end()

        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
