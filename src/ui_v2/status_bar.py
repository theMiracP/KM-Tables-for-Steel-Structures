"""
Linear / SaaS Minimalist Alt Durum Çubuğu (LinearStatusBar).
Kompakt (26px), tek satır, durum bildirimleri ve CAD motor telemetrisi.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from src.ui_v2 import theme_linear as theme


class LinearStatusBar(QFrame):
    """
    26px yüksekliğinde, ultra-minimal Linear durum çubuğu.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(26)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SIDEBAR};
                border-top: 1px solid {theme.BORDER_SUBTLE};
            }}
            QLabel {{
                color: {theme.TEXT_MUTED};
                font-size: 11px;
            }}
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(16)

        # 1. SOL: CAD Canlı Durum ve Aktif Standart
        self.lbl_status = QLabel("● CAD Motoru Hazır")
        self.lbl_status.setStyleSheet(f"color: {theme.COLOR_SUCCESS}; font-weight: 500;")
        layout.addWidget(self.lbl_status)

        self.lbl_standard = QLabel("Standart: ГОСТ 21.502-2007 (КМ)")
        layout.addWidget(self.lbl_standard)

        layout.addStretch(1)

        # 2. SAĞ: Telemetri ve Dışa Aktarma Formatı
        self.lbl_format = QLabel("Export: DXF R2013 / AC1027")
        layout.addWidget(self.lbl_format)

        self.lbl_encoding = QLabel("Kodlama: ANSI_1251 (Cyrillic)")
        layout.addWidget(self.lbl_encoding)

    def set_status(self, text: str, is_success: bool = True):
        color = theme.COLOR_SUCCESS if is_success else theme.COLOR_WARNING
        self.lbl_status.setText(f"● {text}")
        self.lbl_status.setStyleSheet(f"color: {color}; font-weight: 500;")
