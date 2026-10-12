"""
KM Tablo Oluşturucu - Profil Kesit Eskiz İkon Üreticisi (Sketch Renderer).
`SketchType` modellerinden PySide6 `QIcon` ve `QPixmap` kesit sembolleri üretir.
"""
from typing import Optional, Dict
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QBrush

from src.models.sketch import SketchType


_ICON_CACHE: Dict[SketchType, QIcon] = {}


def get_sketch_icon(sketch_type: SketchType, size: int = 22, color: Optional[QColor] = None) -> QIcon:
    """
    Belirtilen SketchType için vektörel CAD kesit şekli ikonu üretir.
    Sonuçlar performans için önbelleğe alınır.
    """
    if color is None:
        color = QColor("#38BDF8")  # Vibrant Sky Blue

    cache_key = (sketch_type, size, color.name())
    if sketch_type in _ICON_CACHE and color.name() == "#38bdf8" and size == 22:
        return _ICON_CACHE[sketch_type]

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    if sketch_type == SketchType.NONE:
        return QIcon()

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(color, 1.6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)

    margin = 3.0
    w = float(size) - 2.0 * margin
    h = float(size) - 2.0 * margin
    cx = float(size) / 2.0
    cy = float(size) / 2.0

    if sketch_type in (SketchType.I_BEAM, SketchType.WELDED_I_BEAM, SketchType.WELDED_I_PACKAGE):
        # I-Kiriş (Üst Flanş, Alt Flanş, Gövde)
        flange_w = w * 0.8
        fx1 = cx - flange_w / 2.0
        fx2 = cx + flange_w / 2.0
        y_top = margin + 1.0
        y_bot = size - margin - 1.0
        painter.drawLine(QPointF(fx1, y_top), QPointF(fx2, y_top))
        painter.drawLine(QPointF(fx1, y_bot), QPointF(fx2, y_bot))
        painter.drawLine(QPointF(cx, y_top), QPointF(cx, y_bot))
        if sketch_type == SketchType.WELDED_I_PACKAGE:
            painter.drawLine(QPointF(fx1, y_top + 2.5), QPointF(fx2, y_top + 2.5))
            painter.drawLine(QPointF(fx1, y_bot - 2.5), QPointF(fx2, y_bot - 2.5))

    elif sketch_type == SketchType.RECT_TUBE:
        # Kutu Profil (□)
        rw = w * 0.75
        rh = h * 0.75
        painter.drawRect(QRectF(cx - rw / 2.0, cy - rh / 2.0, rw, rh))

    elif sketch_type == SketchType.ROUND_TUBE:
        # Dairesel Boru (○)
        r = (min(w, h) * 0.8) / 2.0
        painter.drawEllipse(QPointF(cx, cy), r, r)

    elif sketch_type == SketchType.CHANNEL:
        # Şveller / Kanal ([)
        cw = w * 0.65
        x_left = cx - cw / 2.0
        x_right = cx + cw / 2.0
        y_top = margin + 1.0
        y_bot = size - margin - 1.0
        painter.drawLine(QPointF(x_right, y_top), QPointF(x_left, y_top))
        painter.drawLine(QPointF(x_left, y_top), QPointF(x_left, y_bot))
        painter.drawLine(QPointF(x_left, y_bot), QPointF(x_right, y_bot))

    elif sketch_type == SketchType.ANGLE:
        # Köşebent (L)
        aw = w * 0.7
        ah = h * 0.7
        x_left = cx - aw / 2.0
        y_top = cy - ah / 2.0
        y_bot = cy + ah / 2.0
        x_right = cx + aw / 2.0
        painter.drawLine(QPointF(x_left, y_top), QPointF(x_left, y_bot))
        painter.drawLine(QPointF(x_left, y_bot), QPointF(x_right, y_bot))

    elif sketch_type == SketchType.WELDED_T:
        # T-Profil (Тавр)
        tw = w * 0.8
        x1 = cx - tw / 2.0
        x2 = cx + tw / 2.0
        y_top = margin + 1.0
        y_bot = size - margin - 1.0
        painter.drawLine(QPointF(x1, y_top), QPointF(x2, y_top))
        painter.drawLine(QPointF(cx, y_top), QPointF(cx, y_bot))

    elif sketch_type == SketchType.WELDED_CRUCIFORM:
        # Haç Profil (+)
        x1 = cx - w * 0.4
        x2 = cx + w * 0.4
        y1 = cy - h * 0.4
        y2 = cy + h * 0.4
        painter.drawLine(QPointF(x1, cy), QPointF(x2, cy))
        painter.drawLine(QPointF(cx, y1), QPointF(cx, y2))

    elif sketch_type == SketchType.COMPOUND_BOX_WELDED:
        # Kaynaklı Kutu
        bw = w * 0.65
        bh = h * 0.65
        painter.drawRect(QRectF(cx - bw / 2.0, cy - bh / 2.0, bw, bh))
        # Flanş uzantıları
        painter.drawLine(QPointF(cx - bw / 2.0 - 2.0, cy - bh / 2.0), QPointF(cx - bw / 2.0 + bw + 2.0, cy - bh / 2.0))
        painter.drawLine(QPointF(cx - bw / 2.0 - 2.0, cy + bh / 2.0), QPointF(cx - bw / 2.0 + bw + 2.0, cy + bh / 2.0))

    elif sketch_type in (SketchType.PLATE, SketchType.CHECKERED_PLATE):
        # Levha / Lama (-)
        pw = w * 0.85
        ph = 4.0
        painter.drawRect(QRectF(cx - pw / 2.0, cy - ph / 2.0, pw, ph))

    else:
        # Genel Dikdörtgen
        rw = w * 0.6
        rh = h * 0.6
        painter.drawRect(QRectF(cx - rw / 2.0, cy - rh / 2.0, rw, rh))

    painter.end()

    icon = QIcon(pixmap)
    if color.name() == "#38bdf8" and size == 22:
        _ICON_CACHE[sketch_type] = icon
    return icon
