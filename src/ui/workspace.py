"""
KM Tablo Oluşturucu - Ana Çalışma Alanı (MainWorkspaceArea).
Tablo Editörü ve CAD Drawing Preview panellerini iki modern bağımsız kart/çalışma alanı olarak sunar.
"""
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QFrame, QLabel
)

from src.ui import theme
from src.ui.i18n import i18n


class ModernWorkspacePanelCard(QFrame):
    """
    Kendi başlığına, rozetine ve aksiyon alanına sahip bağımsız modern çalışma kartı.
    """
    def __init__(self, title: str, subtitle: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernWorkspacePanelCard {{
                background-color: {theme.COLOR_PANEL_BG};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 10px;
            }}
        """)
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(6, 6, 6, 6)
        self.root_layout.setSpacing(6)

        # Kart Başlık Çubuğu (Card Header - 34px)
        self.header_frame = QFrame(self)
        self.header_frame.setFixedHeight(34)
        self.header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.COLOR_PANEL_ALT};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 4px;
            }}
        """)
        h_layout = QHBoxLayout(self.header_frame)
        h_layout.setContentsMargins(8, 0, 8, 0)
        h_layout.setSpacing(8)

        self.lbl_title = QLabel(title, self.header_frame)
        self.lbl_title.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: 0.5px;
        """)
        h_layout.addWidget(self.lbl_title)

        if subtitle:
            self.lbl_sub = QLabel(subtitle, self.header_frame)
            self.lbl_sub.setStyleSheet(f"font-size: 10px; color: {theme.COLOR_TEXT_MUTED};")
            h_layout.addWidget(self.lbl_sub)

        h_layout.addStretch()

        self.header_right_layout = QHBoxLayout()
        self.header_right_layout.setSpacing(4)
        h_layout.addLayout(self.header_right_layout)

        self.header_frame.setVisible(False)
        self.root_layout.addWidget(self.header_frame)

        # İçerik Alanı
        self.content_container = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.root_layout.addWidget(self.content_container, 1)

    def set_content(self, widget: QWidget):
        # Mevcut içeriği temizle
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self.content_layout.addWidget(widget)


class MainWorkspaceArea(QWidget):
    """
    Sol Tablo Editörü ve Sağ CAD Preview çalışma alanlarını birleştiren yatay QSplitter.
    """
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setStyleSheet(f"background-color: {theme.COLOR_BG_DARK};")

        # 1. Editör Kartı
        self.editor_card = ModernWorkspacePanelCard("📋 TABLO EDİTÖRÜ", "Veri Girişi & Hücreler", self.splitter)
        self.splitter.addWidget(self.editor_card)

        # 2. CAD Preview Kartı
        self.cad_card = ModernWorkspacePanelCard("📐 ÇİZİM ÖNİZLEME (CAD)", "1:1 Milimetrik Vektör", self.splitter)
        self.splitter.addWidget(self.cad_card)

        self.splitter.setSizes([550, 600])
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)

        layout.addWidget(self.splitter)
