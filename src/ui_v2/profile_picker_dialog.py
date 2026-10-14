"""
KM Studio - GOST Profil Seçici İletişim Kutusu (GostProfilePickerDialog).
Linear tarzı modern arayüz, anlık arama, kategori sekmeleri ve detaylı profil bilgileri.
"""
from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QAbstractItemView
)
from src.services.profile_database import GostProfileDatabase, ProfileRecord
from src.ui_v2 import theme_linear as theme
from src.ui_v2 import icons
from src.ui.i18n import i18n


class GostProfilePickerDialog(QDialog):
    """
    Standart GOST çelik profil kütüphanesi seçim diyaloğu.
    """
    def __init__(self, parent=None, initial_query: str = ""):
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
        self._current_category = "Hepsi"

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

        # Arama kutusu
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Profil ara... örn. 20Б1, 16П, 100х100, СТО, 40К1")
        self.search_edit.setText(initial_query)
        self.search_edit.setFixedHeight(32)
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {theme.ACCENT_PRIMARY};
            }}
        """)
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
            if cat == "Hepsi":
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
            self.cat_buttons.append(btn)
        cat_row.addStretch()
        search_layout.addLayout(cat_row)

        layout.addWidget(search_card)

        # 3. Profil Tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Profil (Обозначение)",
            "Kategori",
            "Standart (ГОСТ / СТО)",
            "Kesit Boyutları (мм)",
            "Ağırlık (кг/м)",
            "Önerilen Çelik"
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
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

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

            item_stl = QTableWidgetItem(p.default_steel)
            item_stl.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(r_idx, 0, item_desig)
            self.table.setItem(r_idx, 1, item_cat)
            self.table.setItem(r_idx, 2, item_std)
            self.table.setItem(r_idx, 3, item_dim)
            self.table.setItem(r_idx, 4, item_wt)
            self.table.setItem(r_idx, 5, item_stl)

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
                f"{profile.dimensions} • {profile.weight_kg_m} кг/м • {profile.default_steel}"
            )

    def _on_double_clicked(self, item):
        self._on_selection_changed()
        if self.selected_profile:
            self.accept()
