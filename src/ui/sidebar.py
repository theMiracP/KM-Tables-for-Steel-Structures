"""
KM Tablo Oluşturucu - Spotify Dark 'Kitaplığın' Kenar Çubuğu (ModernNavigationSidebar).
Kitaplık başlığı (||| Kitaplığın), filtre hapları (+ Yeni Ekle, + Dosya Ekle),
çalınan parça tarzı aktif tablo kartı (equalizer ve play butonu),
dairesel yeşil GOST doğrulama göstergesi ve 'Şimdi oynatılıyor' alt çubuğu.
"""
from typing import Optional, Dict
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QPushButton, QFrame
)

from src.contracts.table_module import TableModule
from src.models.registry import TableRegistry
from src.ui import theme
from src.ui.i18n import i18n


class CircularDonutGauge(QWidget):
    """Spotify tarzı dairesel neon yeşil halka gösterge."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.percentage = 100
        self.is_valid = True

    def set_state(self, is_valid: bool):
        self.is_valid = is_valid
        self.percentage = 100 if is_valid else 45
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(4, 4, 24, 24)

        # Arka plan halkası
        bg_pen = QPen(QColor(theme.COLOR_PANEL_ALT), 3.5)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)

        # Dolu halka
        ring_color = QColor(theme.COLOR_ACCENT) if self.is_valid else QColor(theme.COLOR_WARNING)
        ring_pen = QPen(ring_color, 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(ring_pen)

        span_angle = int(- (self.percentage / 100.0) * 360 * 16)
        painter.drawArc(rect, 90 * 16, span_angle)


class ModernNavigationSidebar(QWidget):
    """
    Spotify 'Kitaplığın' tarzı sol kütüphane ve navigasyon paneli.
    """
    table_selected = Signal(str)  # table_id
    toggle_requested = Signal()   # Çekmece daralt

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)
        self._current_table_id: Optional[str] = None

        self._build_ui()
        self.refresh_list()
        i18n.language_changed.connect(self._update_translations)

    def _build_ui(self):
        self.setStyleSheet(f"""
            ModernNavigationSidebar {{
                background-color: {theme.COLOR_PANEL_BG};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 10px;
            }}
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 12, 10, 10)
        main_layout.setSpacing(10)

        # ----------------------------------------------------------------------
        # 1. KİTAPLIK BAŞLIĞI: ||| Kitaplığın + [+] [→]
        # ----------------------------------------------------------------------
        header = QFrame(self)
        header.setFixedHeight(32)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(2, 0, 2, 0)
        h_layout.setSpacing(8)

        self.lbl_title = QLabel("📚  Kitaplığın", header)
        self.lbl_title.setStyleSheet("""
            font-size: 14px;
            font-weight: 800;
            color: #FFFFFF;
        """)
        h_layout.addWidget(self.lbl_title)
        h_layout.addStretch()

        btn_add = QPushButton("＋", header)
        btn_add.setObjectName("circleButton")
        btn_add.setFixedSize(26, 26)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.COLOR_TEXT_MUTED};
                border: none;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #FFFFFF;
                background-color: {theme.COLOR_PANEL_HOVER};
                border-radius: 13px;
            }}
        """)
        h_layout.addWidget(btn_add)

        self.btn_collapse = QPushButton("→", header)
        self.btn_collapse.setObjectName("circleButton")
        self.btn_collapse.setFixedSize(26, 26)
        self.btn_collapse.setToolTip("Kitaplığı Daralt (Ctrl+B)")
        self.btn_collapse.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.COLOR_TEXT_MUTED};
                border: none;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #FFFFFF;
                background-color: {theme.COLOR_PANEL_HOVER};
                border-radius: 13px;
            }}
        """)
        self.btn_collapse.clicked.connect(self.toggle_requested.emit)
        h_layout.addWidget(self.btn_collapse)

        main_layout.addWidget(header)

        # ----------------------------------------------------------------------
        # 2. FİLTRE HAPLARI: [+ Yeni Ekle] [+ Dosya Ekle]
        # ----------------------------------------------------------------------
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(6)

        btn_new = QPushButton("＋ Yeni Ekle", self)
        btn_new.setFixedHeight(28)
        btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: #FFFFFF;
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 14px;
                padding: 0 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
            }}
        """)
        pills_layout.addWidget(btn_new)

        btn_file = QPushButton("＋ Dosya Ekle", self)
        btn_file.setFixedHeight(28)
        btn_file.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: #FFFFFF;
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 14px;
                padding: 0 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
            }}
        """)
        pills_layout.addWidget(btn_file)
        pills_layout.addStretch()

        main_layout.addLayout(pills_layout)

        # Gizli arama inputu (test uyumluluğu için mevcut tutulur)
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("🔍 Tablolarda ara...")
        self.search_input.setFixedHeight(26)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_PRIMARY};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 13px;
                padding: 2px 10px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.COLOR_ACCENT};
            }}
        """)
        self.search_input.textChanged.connect(self._filter_tree)
        main_layout.addWidget(self.search_input)

        # ----------------------------------------------------------------------
        # 3. SPOTIFY PLAYLIST LİSTESİ (Tree Widget)
        # ----------------------------------------------------------------------
        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(10)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: transparent;
                border: none;
                padding: 0px;
                outline: none;
            }}
            QTreeWidget::item {{
                height: 48px;
                border-radius: 6px;
                padding: 4px;
                margin-bottom: 2px;
                color: {theme.COLOR_TEXT_MUTED};
            }}
            QTreeWidget::item:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
                color: #FFFFFF;
            }}
            QTreeWidget::item:selected {{
                background-color: #14281D;
                color: {theme.COLOR_ACCENT};
                border-left: 3px solid {theme.COLOR_ACCENT};
                font-weight: 700;
            }}
        """)
        self.tree.itemClicked.connect(self._on_item_clicked)
        main_layout.addWidget(self.tree, 1)

        # ----------------------------------------------------------------------
        # 4. DOKÜMAN & PAFTA BİLGİSİ (Açılır Çekmece Hapı)
        # ----------------------------------------------------------------------
        self.btn_doc_accordion = QPushButton("DOKÜMAN & PAFTA BİLGİSİ   ▾", self)
        self.btn_doc_accordion.setFixedHeight(30)
        self.btn_doc_accordion.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.COLOR_PANEL_ALT};
                color: {theme.COLOR_TEXT_MUTED};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 15px;
                padding: 0 12px;
                text-align: left;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_PANEL_HOVER};
                color: #FFFFFF;
            }}
        """)
        self.lbl_doc_info = QLabel("ГОСТ 2.301 · A3 Yatay · Form 3 (185 mm)", self)
        self.lbl_doc_info.setStyleSheet(f"font-size: 10px; color: {theme.COLOR_TEXT_MUTED}; padding-left: 6px;")
        main_layout.addWidget(self.btn_doc_accordion)
        main_layout.addWidget(self.lbl_doc_info)

        # ----------------------------------------------------------------------
        # 5. CANLI DOĞRULAMA (GOST) KARTI
        # ----------------------------------------------------------------------
        val_card = QFrame(self)
        val_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.COLOR_PANEL_ALT};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 8px;
                padding: 6px;
            }}
        """)
        vc_layout = QVBoxLayout(val_card)
        vc_layout.setContentsMargins(10, 8, 10, 8)
        vc_layout.setSpacing(6)

        lbl_val_title = QLabel("CANLI DOĞRULAMA (GOST)", val_card)
        lbl_val_title.setStyleSheet(f"font-size: 10px; font-weight: 800; color: {theme.COLOR_TEXT_MUTED}; letter-spacing: 0.5px;")
        vc_layout.addWidget(lbl_val_title)

        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        self.lbl_val_summary = QLabel("✓ Tüm kurallar geçerli", val_card)
        self.lbl_val_summary.setStyleSheet(f"""
            QLabel {{
                background-color: {theme.COLOR_SUCCESS_BG};
                color: {theme.COLOR_ACCENT};
                border: 1px solid #1B4D3A;
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 700;
            }}
        """)
        status_row.addWidget(self.lbl_val_summary, 1)

        # Dairesel Halka Gösterge
        self.gauge = CircularDonutGauge(val_card)
        status_row.addWidget(self.gauge)

        vc_layout.addLayout(status_row)
        main_layout.addWidget(val_card)

        # ----------------------------------------------------------------------
        # 6. 'ŞİMDİ OYNATILIYOR' MİNİ BAR (Now Playing Widget)
        # ----------------------------------------------------------------------
        now_playing = QFrame(self)
        now_playing.setFixedHeight(46)
        now_playing.setStyleSheet(f"""
            QFrame {{
                background-color: #0A0A0A;
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 6px;
            }}
        """)
        np_layout = QHBoxLayout(now_playing)
        np_layout.setContentsMargins(6, 4, 8, 4)
        np_layout.setSpacing(8)

        # Mini thumbnail
        self.lbl_np_thumb = QLabel("📐", now_playing)
        self.lbl_np_thumb.setFixedSize(30, 30)
        self.lbl_np_thumb.setStyleSheet(f"""
            background-color: {theme.COLOR_PANEL_ALT};
            border-radius: 4px;
            font-size: 14px;
            text-align: center;
        """)
        self.lbl_np_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        np_layout.addWidget(self.lbl_np_thumb)

        # Şarkı / Tablo Başlığı
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(1)

        lbl_np_header = QLabel("Aktif Tablo:", now_playing)
        lbl_np_header.setStyleSheet(f"font-size: 9px; color: {theme.COLOR_TEXT_DIM};")
        info_layout.addWidget(lbl_np_header)

        self.lbl_np_title = QLabel("Ведомость элементов", now_playing)
        self.lbl_np_title.setStyleSheet("font-size: 10px; font-weight: 700; color: #FFFFFF;")
        info_layout.addWidget(self.lbl_np_title)

        np_layout.addLayout(info_layout, 1)

        # Heart & Pip Icons
        btn_heart = QPushButton("♡", now_playing)
        btn_heart.setFixedSize(20, 20)
        btn_heart.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {theme.COLOR_TEXT_MUTED};
                font-size: 14px;
            }}
            QPushButton:hover {{
                color: {theme.COLOR_ACCENT};
            }}
        """)
        np_layout.addWidget(btn_heart)

        main_layout.addWidget(now_playing)

    def refresh_list(self):
        """Modülleri Spotify playlistleri şeklinde yükler."""
        self.tree.clear()
        modules = TableRegistry.all()

        # Ana Kategori Klasörü: KM - ÇELİK YAPILAR (ГОСТ 21.502...)
        cat_item = QTreeWidgetItem(self.tree)
        cat_item.setText(0, "📁  KM - ÇELİK YAPILAR (ГОСТ 21.502)")
        cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        cat_item.setExpanded(True)
        cat_item.setForeground(0, QColor("#FFFFFF"))

        for i, mod in enumerate(modules):
            item = QTreeWidgetItem(cat_item)
            is_active = (mod.id == self._current_table_id) or (i == 0 and not self._current_table_id)

            icon = "📊" if "stal" in mod.id or "stali" in mod.id else "📐"
            item.setText(0, f"{icon}  {mod.name.split('(')[0].strip()}")
            item.setData(0, Qt.ItemDataRole.UserRole, mod.id)
            item.setToolTip(0, mod.description or mod.name)

            if is_active:
                self.tree.setCurrentItem(item)

        # Ek Gösterim Maddeleri (Mockup uyumu için)
        mock_a3_1 = QTreeWidgetItem(self.tree)
        mock_a3_1.setText(0, "📄  GOST 2.301 - A3 Yatay")
        mock_a3_1.setForeground(0, QColor(theme.COLOR_TEXT_MUTED))

        mock_a3_2 = QTreeWidgetItem(self.tree)
        mock_a3_2.setText(0, "📐  GOST 2.301 - A3 Yatay")
        mock_a3_2.setForeground(0, QColor(theme.COLOR_TEXT_MUTED))

    def set_active_table(self, table_id: str):
        self._current_table_id = table_id
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            if top.data(0, Qt.ItemDataRole.UserRole) == table_id:
                self.tree.setCurrentItem(top)
                self._update_now_playing(top.text(0))
                return
            for j in range(top.childCount()):
                child = top.child(j)
                if child.data(0, Qt.ItemDataRole.UserRole) == table_id:
                    self.tree.setCurrentItem(child)
                    self._update_now_playing(child.text(0))
                    return

    def _update_now_playing(self, raw_title: str):
        cleaned = raw_title.replace("📐", "").replace("📊", "").replace("📄", "").strip()
        self.lbl_np_title.setText(cleaned)

    def update_validation_state(self, is_valid: bool, msg: str = ""):
        self.gauge.set_state(is_valid)
        if is_valid:
            self.lbl_val_summary.setText("✓ Tüm kurallar geçerli")
            self.lbl_val_summary.setStyleSheet(f"""
                QLabel {{
                    background-color: {theme.COLOR_SUCCESS_BG};
                    color: {theme.COLOR_ACCENT};
                    border: 1px solid #1B4D3A;
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 10px;
                    font-weight: 700;
                }}
            """)
        else:
            self.lbl_val_summary.setText("⚠ Eksik Parametre")
            self.lbl_val_summary.setStyleSheet(f"""
                QLabel {{
                    background-color: {theme.COLOR_DANGER_BG};
                    color: {theme.COLOR_DANGER};
                    border: 1px solid {theme.COLOR_DANGER_BORDER};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 10px;
                    font-weight: 700;
                }}
            """)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        table_id = item.data(0, Qt.ItemDataRole.UserRole)
        if table_id:
            self._current_table_id = table_id
            self._update_now_playing(item.text(0))
            self.table_selected.emit(table_id)

    def _filter_tree(self, text: str):
        query = text.strip().lower()
        for i in range(self.tree.topLevelItemCount()):
            cat_item = self.tree.topLevelItem(i)
            any_child_visible = False
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                name = child.text(0).lower()
                tooltip = child.toolTip(0).lower()
                match = (query in name) or (query in tooltip)
                child.setHidden(not match)
                if match:
                    any_child_visible = True
            cat_item.setHidden(not any_child_visible and query != "")
            if query != "" and any_child_visible:
                cat_item.setExpanded(True)

    def _update_translations(self, lang_code: str):
        self.lbl_title.setText("📚  Kitaplığın")
        self.refresh_list()
