"""
KM Tablo Oluşturucu - PySide6 Yeniden Kullanılabilir Mühendislik Arayüz Bileşenleri.
Kompakt Kiril harf şeridi, mini sanal klavye ve durum göstergeleri.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
)
from src.ui import theme

# Rusça KM Projelerinde En Çok Kullanılan Marka Harfleri
POPULAR_CYRILLIC_KM = ["Б", "К", "Ф", "П", "С", "В", "Р", "Ш"]
# Özel CAD / Kesit Sembolleri
SECTION_SYMBOLS = ["±", "∅", "□", "I", "[", "L", "—", "×"]

# Tam Kiril Alfabesi (3 Kompakt Satır)
FULL_CYRILLIC_ROWS = [
    ["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", "Й", "К"],
    ["Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х"],
    ["Ц", "Ч", "Ш", "Щ", "Ъ", "Ы", "Ь", "Э", "Ю", "Я", "∅"],
]

class ChipButton(QPushButton):
    """Kompakt, klavye odağını çalmayan harf/sembol butonu."""
    def __init__(self, text: str, parent=None, tooltip: str = ""):
        super().__init__(text, parent)
        self.setProperty("class", "chip_btn")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Tablo hücresinin odağını korur
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)


class CyrillicBar(QWidget):
    """
    Tablonun hemen üstünde yer alan zarif Kiril ve Sembol Çubuğu.
    Tıklandığında aktif tablo hücresine karakter ekler.
    """
    char_clicked = Signal(str)
    toggle_keyboard = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(3)

        lbl_ru = QLabel("RU:", self)
        lbl_ru.setStyleSheet(f"color: {theme.COLOR_TEXT_DIM}; font-size: 10px; font-weight: bold;")
        layout.addWidget(lbl_ru)

        # En sık kullanılan KM harfleri
        for ch in POPULAR_CYRILLIC_KM:
            btn = ChipButton(ch, self, tooltip=f"Kiril '{ch}' harfini ekle")
            btn.clicked.connect(lambda checked=False, c=ch: self.char_clicked.emit(c))
            layout.addWidget(btn)

        # İnce ayırıcı
        sep1 = QFrame(self)
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet(f"color: {theme.COLOR_BORDER}; margin: 2px 2px;")
        layout.addWidget(sep1)

        # CAD / Kesit sembolleri
        for sym in SECTION_SYMBOLS:
            btn = ChipButton(sym, self, tooltip=f"'{sym}' sembolünü ekle")
            btn.clicked.connect(lambda checked=False, s=sym: self.char_clicked.emit(s))
            layout.addWidget(btn)

        layout.addStretch()

        # Sanal Klavye Aç/Kapa Butonu
        self.btn_kb_toggle = QPushButton("⌨ Tam Klavye", self)
        self.btn_kb_toggle.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_kb_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.COLOR_TEXT_MUTED};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_PRIMARY};
                border-color: {theme.COLOR_BORDER_LIGHT};
            }}
            QPushButton:checked {{
                background-color: {theme.COLOR_ACCENT_MUTED};
                color: #FFFFFF;
                border-color: {theme.COLOR_ACCENT};
            }}
        """)
        self.btn_kb_toggle.setCheckable(True)
        self.btn_kb_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_kb_toggle.clicked.connect(self.toggle_keyboard.emit)
        layout.addWidget(self.btn_kb_toggle)


class CyrillicKeyboardPanel(QWidget):
    """
    İsteğe bağlı açılıp kapanan şık ve kompakt 3 satırlı tam Kiril sanal klavyesi.
    """
    char_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.COLOR_PANEL_ALT};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 4px;
            }}
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(3)

        for row in FULL_CYRILLIC_ROWS:
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(3)
            for ch in row:
                btn = ChipButton(ch, self)
                btn.clicked.connect(lambda checked=False, c=ch: self.char_clicked.emit(c))
                h_layout.addWidget(btn)
            h_layout.addStretch()
            main_layout.addLayout(h_layout)


class SectionHeader(QWidget):
    """Panel bölüm başlığı (örn: 'ELEMANLAR', 'SAYFA & YERLEŞİM')."""
    def __init__(self, title: str, subtitle: str = "", right_widget: QWidget = None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 6)
        layout.setSpacing(6)

        lbl_title = QLabel(title.upper(), self)
        lbl_title.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.COLOR_TEXT_PRIMARY}; letter-spacing: 0.5px;")
        layout.addWidget(lbl_title)

        if subtitle:
            lbl_sub = QLabel(f"·  {subtitle}", self)
            lbl_sub.setStyleSheet(f"font-size: 10px; color: {theme.COLOR_TEXT_MUTED};")
            layout.addWidget(lbl_sub)

        layout.addStretch()

        if right_widget:
            layout.addWidget(right_widget)
