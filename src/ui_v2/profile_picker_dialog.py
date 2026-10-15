"""
KM Studio - GOST Profil Seçici İletişim Kutusu (GostProfilePickerDialog).
Linear tarzı modern arayüz, anlık arama, kategori sekmeleri ve detaylı profil bilgileri.
"""
from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QAbstractItemView, QToolButton, QComboBox
)
from src.services.profile_database import GostProfileDatabase, ProfileRecord
from src.ui_v2 import theme_linear as theme
from src.ui_v2 import icons
from src.ui.i18n import i18n


class GostProfilePickerDialog(QDialog):
    """
    Standart GOST çelik profil kütüphanesi seçim diyaloğu.
    """
    def __init__(self, parent=None, initial_query: str = "", category: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("GOST Rus Çelik Sortament / Profil Kütüphanesi")
        self.resize(780, 520)
        self.setMinimumSize(640, 420)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
            }}
        """)

        self.db = GostProfileDatabase.instance()
        self.selected_profile: Optional[ProfileRecord] = None
        self._current_category = category if (category and category in self.db.get_categories()) else "Hepsi"

        self._build_ui(initial_query)
        self._refresh_list()

    def _build_ui(self, initial_query: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # 1. Başlık ve Açıklama
        header_layout = QHBoxLayout()
        lbl_icon = QLabel("📚")
        lbl_icon.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(lbl_icon)

        title_col = QVBoxLayout()
        lbl_title = QLabel("ГОСТ Profil ve Kesit Kütüphanesi")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        lbl_sub = QLabel("СТО АСЧМ 20-93, ГОСТ 8240-97, ГОСТ 30245-2003, ГОСТ 10704-91, ГОСТ 8509/8510")
        lbl_sub.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        header_layout.addLayout(title_col)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 2. Arama ve Kategori Filtreleri
        search_card = QFrame()
        search_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 6px;
            }}
        """)
        search_layout = QVBoxLayout(search_card)
        search_layout.setContentsMargins(8, 8, 8, 8)
        search_layout.setSpacing(8)

        # Arama kutusu (Temizleme 'X' butonu ve Esc kısayolu destekli)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Profil ara... örn. 20Б1, 16П, 100х100, СТО, 40К1")
        self.search_edit.setText(initial_query)
        self.search_edit.setFixedHeight(32)
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 6px;
                padding: 0 28px 0 10px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {theme.ACCENT_PRIMARY};
            }}
            QLineEdit QToolButton {{
                border: none;
                background: transparent;
                border-radius: 4px;
                margin-right: 4px;
            }}
            QLineEdit QToolButton:hover {{
                background-color: #334155;
            }}
        """)
        # Koyu temada yüksek kontrastlı 'X' ikonu ve imleç ayarı
        for btn in self.search_edit.findChildren(QToolButton):
            btn.setIcon(icons.get_icon(icons.ICON_CLOSE, color="#94A3B8"))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip("Aramayı Temizle (Esc)")

        # Esc tuşu: metin varsa temizler, metin yoksa pencereyi kapatır
        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self.search_edit)
        esc_shortcut.activated.connect(lambda: self.search_edit.clear() if self.search_edit.text() else self.reject())

        self.search_edit.textChanged.connect(self._refresh_list)
        search_layout.addWidget(self.search_edit)

        # Kategori Butonları (Pills)
        cat_row = QHBoxLayout()
        cat_row.setSpacing(6)
        categories = ["Hepsi"] + self.db.get_categories()
        self.cat_buttons = []
        for cat in categories:
            btn = QPushButton(cat)
            btn.setFixedHeight(24)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if cat == self._current_category:
                btn.setChecked(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.BG_APP};
                    color: {theme.TEXT_SECONDARY};
                    border: 1px solid {theme.BORDER_SUBTLE};
                    border-radius: 4px;
                    padding: 0 10px;
                    font-size: 11px;
                }}
                QPushButton:checked {{
                    background-color: {theme.ACCENT_PRIMARY};
                    color: #FFFFFF;
                    border-color: {theme.ACCENT_PRIMARY};
                    font-weight: 600;
                }}
            """)
            btn.clicked.connect(lambda checked, c=cat: self._set_category(c))
            cat_row.addWidget(btn)
        cat_row.addStretch()

        self.btn_add_custom = QPushButton(" ➕ Yeni Profil Ekle")
        self.btn_add_custom.setFixedHeight(24)
        self.btn_add_custom.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_custom.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: #38BDF8;
                border: 1px solid #0369A1;
                border-radius: 4px;
                padding: 0 10px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #0369A1;
                color: #FFFFFF;
            }}
        """)
        self.btn_add_custom.clicked.connect(self._open_add_custom_profile_dialog)
        cat_row.addWidget(self.btn_add_custom)

        search_layout.addLayout(cat_row)

        layout.addWidget(search_card)

        # 3. Profil Tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Profil (Обозначение)",
            "Kategori",
            "Standart (ГОСТ / СТО)",
            "Kesit Boyutları (мм)",
            "Ağırlık (кг/м)"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                gridline-color: {theme.BORDER_SUBTLE};
            }}
            QHeaderView::section {{
                background-color: {theme.BG_SIDEBAR};
                color: {theme.TEXT_MUTED};
                font-weight: 600;
                font-size: 11px;
                border: none;
                border-bottom: 1px solid {theme.BORDER_LIGHT};
                padding: 6px;
            }}
            QTableWidget::item:selected {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: #FFFFFF;
            }}
        """)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemDoubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self.table, 1)

        # 4. Alt Bilgi ve Eylem Butonları
        bottom_layout = QHBoxLayout()
        self.lbl_selected_info = QLabel("Bir profil seçin...")
        self.lbl_selected_info.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px;")
        bottom_layout.addWidget(self.lbl_selected_info)
        bottom_layout.addStretch()

        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.setFixedHeight(30)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
            }}
        """)
        self.btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton("✓ Seç ve Tabloya Ekle")
        self.btn_apply.setFixedHeight(30)
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.setEnabled(False)
        self.btn_apply.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #FFFFFF;
                border: 1px solid {theme.ACCENT_PRIMARY};
                border-radius: 6px;
                padding: 0 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: {theme.TEXT_MUTED};
                border-color: {theme.BORDER_SUBTLE};
            }}
        """)
        self.btn_apply.clicked.connect(self.accept)
        bottom_layout.addWidget(self.btn_apply)

        layout.addLayout(bottom_layout)

    def _set_category(self, cat: str):
        self._current_category = cat
        for btn in self.cat_buttons:
            btn.setChecked(btn.text() == cat)
        self._refresh_list()

    def _refresh_list(self):
        query = self.search_edit.text()
        profiles = self.db.filter_profiles(query=query, category=self._current_category)

        self.table.setRowCount(len(profiles))
        for r_idx, p in enumerate(profiles):
            item_desig = QTableWidgetItem(p.designation)
            item_desig.setData(Qt.ItemDataRole.UserRole, p)
            item_desig.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_cat = QTableWidgetItem(p.category)
            item_cat.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_std = QTableWidgetItem(p.standard)
            item_std.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_dim = QTableWidgetItem(p.dimensions)
            item_dim.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            item_wt = QTableWidgetItem(f"{p.weight_kg_m:.2f}")
            item_wt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self.table.setItem(r_idx, 0, item_desig)
            self.table.setItem(r_idx, 1, item_cat)
            self.table.setItem(r_idx, 2, item_std)
            self.table.setItem(r_idx, 3, item_dim)
            self.table.setItem(r_idx, 4, item_wt)

        if len(profiles) > 0:
            self.table.selectRow(0)
        else:
            self.selected_profile = None
            self.btn_apply.setEnabled(False)
            self.lbl_selected_info.setText("Eşleşen profil bulunamadı.")

    def _on_selection_changed(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            self.selected_profile = None
            self.btn_apply.setEnabled(False)
            self.lbl_selected_info.setText("Bir profil seçin...")
            return

        item = self.table.item(self.table.currentRow(), 0)
        if item:
            profile: ProfileRecord = item.data(Qt.ItemDataRole.UserRole)
            self.selected_profile = profile
            self.btn_apply.setEnabled(True)
            self.lbl_selected_info.setText(
                f"Seçilen: <b>{profile.designation}</b> ({profile.standard}) — "
                f"{profile.dimensions} • {profile.weight_kg_m} кг/м"
            )

    def _on_double_clicked(self, item):
        self._on_selection_changed()
        if self.selected_profile:
            self.accept()

    def _open_add_custom_profile_dialog(self):
        """Kullanıcının kütüphaneye yeni özel profil eklemesi için diyaloğu açar."""
        init_cat = self._current_category if self._current_category != "Hepsi" else "Двутавры"
        dlg = AddCustomProfileDialog(parent=self, initial_category=init_cat)
        if dlg.exec() and dlg.created_profile:
            # Yeni eklenen profili ara ve seç
            self.search_edit.setText(dlg.created_profile.designation)
            self._refresh_list()
            if self.table.rowCount() > 0:
                self.table.selectRow(0)


class AddCustomProfileDialog(QDialog):
    """
    Kullanıcının GOST profil kütüphanesine yeni özel / fabrika profili eklemesini sağlayan modal diyalog.
    """
    def __init__(self, parent=None, initial_category: str = "Двутавры"):
        super().__init__(parent)
        self.setWindowTitle("Yeni Özel Profil Ekle (GOST / Özel)")
        self.resize(460, 380)
        self.created_profile: Optional[ProfileRecord] = None
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
            }}
        """)
        self._build_ui(initial_category)

    def _build_ui(self, initial_category: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        lbl_title = QLabel("Yeni Özel Profil Ekle")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(lbl_title)

        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel {{
                color: {theme.TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 600;
            }}
            QLineEdit, QComboBox {{
                background-color: {theme.BG_APP};
                color: #FFFFFF;
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 5px;
                padding: 0 8px;
                font-size: 12px;
                min-height: 28px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {theme.ACCENT_PRIMARY};
            }}
        """)
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(8)

        # 1. Profil Adı (Designation)
        lbl_desig = QLabel("Profil Tanımı / Kodu (Обозначение)*:")
        self.edit_desig = QLineEdit()
        self.edit_desig.setPlaceholderText("örn: 45Ш2, 150х100х5, Спец-200")
        form_layout.addWidget(lbl_desig)
        form_layout.addWidget(self.edit_desig)

        # 2. Kategori
        lbl_cat = QLabel("Profil Kategorisi:")
        self.cb_category = QComboBox()
        cats = ["Двутавры", "Швеллеры", "Трубы профильные", "Трубы круглые", "Уголки", "Diğer"]
        self.cb_category.addItems(cats)
        if initial_category in cats:
            self.cb_category.setCurrentText(initial_category)
        form_layout.addWidget(lbl_cat)
        form_layout.addWidget(self.cb_category)

        # 3. Standart
        lbl_std = QLabel("Standart / ГОСТ / СТО:")
        self.edit_std = QLineEdit()
        self.edit_std.setText("СТО АСЧМ 20-93")
        self.edit_std.setPlaceholderText("örn: ГОСТ 30245-2003, СТО АСЧМ 20-93, Özel")
        form_layout.addWidget(lbl_std)
        form_layout.addWidget(self.edit_std)

        # 4. Boyutlar ve Ağırlık (Yan yana)
        row_dim = QHBoxLayout()
        col_dim = QVBoxLayout()
        col_dim.addWidget(QLabel("Kesit Boyutları (мм):"))
        self.edit_dim = QLineEdit()
        self.edit_dim.setPlaceholderText("h=..., b=..., s=...")
        col_dim.addWidget(self.edit_dim)
        row_dim.addLayout(col_dim)

        col_w = QVBoxLayout()
        col_w.addWidget(QLabel("Ağırlık (кг/м):"))
        self.edit_weight = QLineEdit()
        self.edit_weight.setPlaceholderText("örn: 35.5")
        col_w.addWidget(self.edit_weight)
        row_dim.addLayout(col_w)
        form_layout.addLayout(row_dim)

        # 5. Varsayılan Çelik
        lbl_steel = QLabel("Varsayılan Çelik Kalitesi:")
        self.edit_steel = QLineEdit()
        self.edit_steel.setText("С255")
        form_layout.addWidget(lbl_steel)
        form_layout.addWidget(self.edit_steel)

        layout.addWidget(form_card)

        # Butonlar
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedHeight(30)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.TEXT_MUTED};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                color: #FFFFFF;
                border-color: {theme.TEXT_SECONDARY};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("✓ Kütüphaneye Kaydet")
        btn_save.setFixedHeight(30)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #FFFFFF;
                border: 1px solid {theme.ACCENT_PRIMARY};
                border-radius: 6px;
                padding: 0 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_PRIMARY_HOVER};
            }}
        """)
        btn_save.clicked.connect(self._on_save)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

    def _on_save(self):
        desig = self.edit_desig.text().strip()
        if not desig:
            self.edit_desig.setFocus()
            return

        cat = self.cb_category.currentText()
        cat_to_sketch = {
            "Двутавры": "I_BEAM",
            "Швеллеры": "CHANNEL",
            "Трубы профильные": "RECT_TUBE",
            "Трубы круглые": "ROUND_TUBE",
            "Уголки": "ANGLE",
        }
        sk_type = cat_to_sketch.get(cat, "NONE")

        weight = 0.0
        try:
            weight = float(self.edit_weight.text().replace(",", ".").strip())
        except ValueError:
            pass

        rec = ProfileRecord(
            designation=desig,
            category=cat,
            standard=self.edit_std.text().strip() or "Özel",
            sketch_type=sk_type,
            dimensions=self.edit_dim.text().strip(),
            weight_kg_m=weight,
            default_steel=self.edit_steel.text().strip() or "С255"
        )
        GostProfileDatabase.instance().add_custom_profile(rec)
        self.created_profile = rec
        self.accept()
