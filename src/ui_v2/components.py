"""
Linear / Notion SaaS Özel UI Bileşenleri.
Performans optimizasyonlu, Windows DWM saydamlık ve takılma problemlerinden arındırılmış
özel ComboBox ve arayüz elemanları.
"""
from PySide6.QtCore import Qt, QTimer, QVariantAnimation, QEasingCurve, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QBrush
from PySide6.QtWidgets import (
    QComboBox, QListView, QPushButton, QStyledItemDelegate,
    QLineEdit, QStyleOptionViewItem, QAbstractItemView
)
from src.ui_v2 import theme_linear as theme

class LinearComboBox(QComboBox):
    """
    Linear / Notion tarzı, yüksek performanslı ComboBox.
    - Windows DWM saydamlık hatalarını (arkadaki yazıların görünmesi) önler.
    - Açılış takılmalarını (lag/stutter) engelleyerek anında ve akıcı açılır.
    - QListView tabanlı %100 solid opak zemin sağlar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._list_view = QListView(self)
        self.setView(self._list_view)

        # Solid opak arka plan ayarları
        self._list_view.setAutoFillBackground(True)
        if self._list_view.viewport():
            self._list_view.viewport().setAutoFillBackground(True)
        self._list_view.setUniformItemSizes(True)
        self._list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def showPopup(self):
        popup = self.view().parent()
        if popup:
            popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            popup.setAutoFillBackground(True)
            popup.setStyleSheet(f"""
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 6px;
            """)
        super().showPopup()
        if popup:
            popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            popup.setAutoFillBackground(True)


class SolidItemDelegate(QStyledItemDelegate):
    """
    Hücre düzenlenirken altındaki eski metnin şeffaflık veya gecikme yüzünden
    üst üste binmesini (%100) engelleyen ve solid opak editör oluşturan delege.
    """
    def __init__(self, parent=None, font_size: int = 12):
        super().__init__(parent)
        self.font_size = font_size

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {theme.BG_SURFACE_ACTIVE};
                    color: #ffffff;
                    border: 1.5px solid {theme.ACCENT_PRIMARY};
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-size: {self.font_size}px;
                    font-weight: 500;
                    selection-background-color: {theme.ACCENT_PRIMARY};
                    selection-color: #ffffff;
                }}
            """)
        return editor

    def updateEditorGeometry(self, editor, option, index):
        # Varsayılan Qt mekanizması QTableWidget::item padding değerini düşerek editörü 21px'e sıkıştırır.
        # Bu metod, editörün hücrenin tüm dikey ve yatay alanını (1px kenarlık payı ile)
        # rahatça kaplamasını sağlayarak imlecin ve metnin sıkışmasını engeller.
        rect = option.rect
        if rect.isValid():
            editor.setGeometry(rect.adjusted(1, 1, -1, -1))
        else:
            super().updateEditorGeometry(editor, option, index)

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        view = self.parent()
        # Eğer bu hücre şu anda aktif olarak düzenleniyorsa altındaki metni çizme
        if view and hasattr(view, "state") and view.state() == QAbstractItemView.State.EditingState and view.currentIndex() == index:
            option.text = ""

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        view = self.parent()
        # Çift koruma: Düzenleme halindeki hücrenin alt metni asla çizilmez
        if view and hasattr(view, "state") and view.state() == QAbstractItemView.State.EditingState and view.currentIndex() == index:
            opt.text = ""
        super().paint(painter, opt, index)


class LinearShimmerButton(QPushButton):
    """
    Linear / Notion SaaS tarzı, sağdan sola parlayan (razor-sharp sheen shimmer)
    animasyonlu eylem butonu.

    - "Jilet gibi" ultra keskin ışık yansıması (kristal odaklı specular hat ve yumuşak aura).
    - Sağdan sola yönelimli (X ekseninde: 1.4 -> -0.4).
    - Açılı jilet geometrisi (22 derece).
    - Periyodik döngü (3.2 saniye bekleme) ve üzerine gelindiğinde (hover / enterEvent) anında parlama.
    - Buton sınırlarına kenetlenmiş (QPainterPath rounded clip, 6px border-radius).
    """
    def __init__(
        self,
        text: str = "",
        parent=None,
        duration_ms: int = 800,
        pause_interval_ms: int = 3200,
        beam_width: float = 34.0,
        shimmer_angle: float = 22.0,
        auto_start: bool = True,
    ):
        super().__init__(text, parent)
        self._shimmer_pos = 1.4
        self._is_animating = False
        self._auto_shimmer = auto_start
        self._shimmer_duration = duration_ms
        self._pause_interval = pause_interval_ms
        self._beam_width = beam_width
        self._shimmer_angle = shimmer_angle

        # Animasyon motoru
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._shimmer_duration)
        self._anim.setStartValue(1.4)
        self._anim.setEndValue(-0.4)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.valueChanged.connect(self._on_anim_step)
        self._anim.finished.connect(self._on_anim_finished)

        # Periyodik bekleme sayacı
        self._pause_timer = QTimer(self)
        self._pause_timer.setSingleShot(True)
        self._pause_timer.setInterval(self._pause_interval)
        self._pause_timer.timeout.connect(self._trigger_loop)

    @property
    def shimmer_position(self) -> float:
        return self._shimmer_pos

    @shimmer_position.setter
    def shimmer_position(self, val: float):
        self._shimmer_pos = float(val)
        self.update()

    @property
    def is_shimmering(self) -> bool:
        return self._is_animating

    def start_shimmer(self, immediate: bool = False):
        """Parıltı animasyonunu başlatır (sağdan sola süpürme)."""
        if not self.isVisible() or not self.isEnabled():
            return
        self._pause_timer.stop()
        if self._anim.state() == QVariantAnimation.State.Running:
            if immediate:
                self._anim.stop()
            else:
                return
        self._shimmer_pos = 1.4
        self._is_animating = True
        self._anim.start()

    def stop_shimmer(self):
        """Parıltı animasyonunu ve döngüsünü durdurur."""
        self._pause_timer.stop()
        self._anim.stop()
        self._is_animating = False
        self._shimmer_pos = 1.4
        self.update()

    def set_auto_shimmer(self, enabled: bool):
        """Otomatik döngüsel parlamayı açar veya kapatır."""
        self._auto_shimmer = enabled
        if not enabled:
            self.stop_shimmer()
        elif self.isVisible() and not self._is_animating:
            self._pause_timer.start(1000)

    def _trigger_loop(self):
        if self._auto_shimmer and self.isVisible() and self.isEnabled():
            self.start_shimmer()

    def _on_anim_step(self, val):
        self._shimmer_pos = float(val)
        self.update()

    def _on_anim_finished(self):
        self._is_animating = False
        self._shimmer_pos = -0.4
        self.update()
        if self._auto_shimmer and self.isVisible() and self.isEnabled():
            self._pause_timer.start(self._pause_interval)

    def enterEvent(self, event):
        try:
            super().enterEvent(event)
        except TypeError:
            pass
        if self.isEnabled():
            self.start_shimmer(immediate=True)

    def showEvent(self, event):
        super().showEvent(event)
        if self._auto_shimmer and not self._is_animating:
            self._pause_timer.start(1200)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.stop_shimmer()

    def paintEvent(self, event):
        # 1. Butonun standart QSS zemin, kenarlık, metin ve ikonunu çiz
        super().paintEvent(event)

        # 2. Animasyon aktif değilse veya alan geçersizse çık
        if not self._is_animating or self.width() <= 0 or self.height() <= 0:
            return

        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Buton sınırlarına kenetlenmiş maske (border-radius: 6px)
            clip_path = QPainterPath()
            clip_path.addRoundedRect(
                QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 6.0, 6.0
            )
            painter.setClipPath(clip_path)

            w = float(self.width())
            h = float(self.height())
            x_center = w * self._shimmer_pos
            y_center = h / 2.0

            painter.save()
            painter.translate(x_center, y_center)
            painter.rotate(self._shimmer_angle)

            bw = self._beam_width
            grad = QLinearGradient(-bw / 2.0, 0, bw / 2.0, 0)
            # Jilet gibi ultra-keskin parıltı profili:
            # Geniş saydam alan -> İnce yarı-saydam aura -> 0.50 merkezinde 255 saf beyaz jilet çizgisi
            grad.setColorAt(0.00, QColor(255, 255, 255, 0))
            grad.setColorAt(0.28, QColor(230, 240, 255, 25))
            grad.setColorAt(0.42, QColor(245, 250, 255, 110))
            grad.setColorAt(0.48, QColor(255, 255, 255, 220))
            grad.setColorAt(0.50, QColor(255, 255, 255, 255))  # Jilet ucu tepe yansıması
            grad.setColorAt(0.52, QColor(255, 255, 255, 220))
            grad.setColorAt(0.58, QColor(245, 250, 255, 110))
            grad.setColorAt(0.72, QColor(230, 240, 255, 25))
            grad.setColorAt(1.00, QColor(255, 255, 255, 0))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRect(QRectF(-bw / 2.0, -h * 3.0, bw, h * 6.0))
            painter.restore()
        finally:
            painter.end()
