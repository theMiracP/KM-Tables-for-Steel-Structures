"""
Standartlar Kütüphanesi ve Yönetimi Modalları (Dialogs).
1. StandardsLibraryDialog: Hazır standartları listeleme, arama, seçme, ekleme, düzenleme ve silme.
2. StandardEditDialog: Standart ekleme ve düzenleme formu (Rusça, Türkçe ve İngilizce alanlar).
"""
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QWidget,
    QAbstractItemView, QTextEdit
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import LinearComboBox, SolidItemDelegate
from src.tables.reference_documents.model import StandardLibraryItem
from src.tables.reference_documents.library import standards_library


class StandardEditDialog(QDialog):
    """Kütüphaneye yeni standart ekleme veya mevcut standardı düzenleme diyaloğu."""
    def __init__(self, item: Optional[StandardLibraryItem] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.item = item
        self.is_edit = item is not None
        self.setWindowTitle("Standart Düzenle" if self.is_edit else "Yeni Standart Ekle")
        self.resize(540, 480)
        self.setStyleSheet(theme.get_linear_stylesheet())
        self._build_ui()
        if self.item:
            self._load_item(self.item)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Başlık ve Açıklama
        lbl_title = QLabel("Standart Kartı" if self.is_edit else "Kütüphaneye Standart Ekle")
        lbl_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {theme.TEXT_PRIMARY};")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(
            "Mühendislerin standardı kolay anlayabilmesi için Rusça GOST başlığının yanına "
            "Türkçe ve İngilizce karşılıklarını ekleyin."
        )
        lbl_desc.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_SECONDARY};")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        # 1. Standart Kodu (Обозначение)
        lbl_desig = QLabel("Standart Kodu / Обозначение (örn: СП 16.13330.2017 veya ГОСТ 27751-2014):")
        lbl_desig.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_PRIMARY};")
        self.txt_desig = QLineEdit()
        self.txt_desig.setPlaceholderText("Örn: СП 16.13330.2017")
        self.txt_desig.setFixedHeight(32)
        layout.addWidget(lbl_desig)
        layout.addWidget(self.txt_desig)

        # 2. Rusça Başlık (Наименование - RU)
        lbl_ru = QLabel("Rusça Başlık / Наименование (RU - Teknik çizime yazılacak standart adı):")
        lbl_ru.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_PRIMARY};")
        self.txt_ru = QLineEdit()
        self.txt_ru.setPlaceholderText("Örn: Стальные конструкции")
        self.txt_ru.setFixedHeight(32)
        layout.addWidget(lbl_ru)
        layout.addWidget(self.txt_ru)

        # 3. Türkçe Karşılığı (TR)
        lbl_tr = QLabel("Türkçe Açıklama / Anlamı (TR):")
        lbl_tr.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_PRIMARY};")
        self.txt_tr = QLineEdit()
        self.txt_tr.setPlaceholderText("Örn: Çelik Yapılar (Güncellenmiş SNiP II-23-81*)")
        self.txt_tr.setFixedHeight(32)
        layout.addWidget(lbl_tr)
        layout.addWidget(self.txt_tr)

        # 4. İngilizce Karşılığı (EN)
        lbl_en = QLabel("English Title / Explanation (EN):")
        lbl_en.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_PRIMARY};")
        self.txt_en = QLineEdit()
        self.txt_en.setPlaceholderText("Örn: Steel Structures")
        self.txt_en.setFixedHeight(32)
        layout.addWidget(lbl_en)
        layout.addWidget(self.txt_en)

        # 5. Bölüm ve Kategori Seçimi (Yan Yana)
        row_opts = QHBoxLayout()
        row_opts.setSpacing(12)

        # Bölüm
        v_sec = QVBoxLayout()
        lbl_sec = QLabel("Bölüm (Раздел):")
        lbl_sec.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_PRIMARY};")
        self.cmb_sec = LinearComboBox()
        self.cmb_sec.addItems(["Ссылочные документы", "Прилагаемые документы"])
        self.cmb_sec.setFixedHeight(32)
        v_sec.addWidget(lbl_sec)
        v_sec.addWidget(self.cmb_sec)
        row_opts.addLayout(v_sec)

        # Kategori
        v_cat = QVBoxLayout()
        lbl_cat = QLabel("Kategori / Disiplin:")
        lbl_cat.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_PRIMARY};")
        self.txt_cat = QLineEdit()
        self.txt_cat.setText("КМ Çelik Yapılar")
        self.txt_cat.setFixedHeight(32)
        v_cat.addWidget(lbl_cat)
        v_cat.addWidget(self.txt_cat)
        row_opts.addLayout(v_cat)

        layout.addLayout(row_opts)

        # 6. Not (Примечание)
        lbl_note = QLabel("Not / Примечание (İsteğe bağlı):")
        lbl_note.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_PRIMARY};")
        self.txt_note = QLineEdit()
        self.txt_note.setPlaceholderText("Ek açıklama veya revizyon bilgisi")
        self.txt_note.setFixedHeight(32)
        layout.addWidget(lbl_note)
        layout.addWidget(self.txt_note)

        layout.addStretch(1)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setObjectName("ghostButton")
        btn_cancel.setFixedHeight(32)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_layout.addStretch(1)

        self.btn_save = QPushButton("💾 Değişiklikleri Kaydet" if self.is_edit else "➕ Kütüphaneye Ekle")
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.setFixedHeight(32)
        self.btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def _load_item(self, item: StandardLibraryItem):
        self.txt_desig.setText(item.designation)
        self.txt_ru.setText(item.title_ru)
        self.txt_tr.setText(item.title_tr)
        self.txt_en.setText(item.title_en)
        idx = self.cmb_sec.findText(item.section)
        if idx >= 0:
            self.cmb_sec.setCurrentIndex(idx)
        else:
            self.cmb_sec.addItem(item.section)
            self.cmb_sec.setCurrentText(item.section)
        self.txt_cat.setText(item.category)
        self.txt_note.setText(item.note)

    def _on_save(self):
        desig = self.txt_desig.text().strip()
        ru = self.txt_ru.text().strip()
        if not desig:
            QMessageBox.warning(self, "Eksik Alan", "Standart kodu (Обозначение) boş bırakılamaz.")
            self.txt_desig.setFocus()
            return
        if not ru:
            QMessageBox.warning(self, "Eksik Alan", "Rusça başlık (Наименование) boş bırakılamaz.")
            self.txt_ru.setFocus()
            return

        item_id = self.item.id if self.item else None
        new_item = StandardLibraryItem(
            id=item_id or self.txt_desig.text().strip().lower().replace(" ", "_"),
            designation=desig,
            title_ru=ru,
            title_tr=self.txt_tr.text().strip(),
            title_en=self.txt_en.text().strip(),
            section=self.cmb_sec.currentText(),
            category=self.txt_cat.text().strip() or "КМ Çelik Yapılar",
            note=self.txt_note.text().strip(),
        )

        if self.is_edit:
            standards_library.update(new_item)
        else:
            standards_library.add(new_item)

        self.accept()


class StandardsLibraryDialog(QDialog):
    """
    Kullanıcının hazır standartları inceleyebileceği, arayabileceği,
    Türkçe/İngilizce karşılıklarını görebileceği ve doğrudan çizim tablosuna aktarabileceği
    tam teşekküllü Standartlar Kütüphanesi Yöneticisi.
    """
    standards_selected = Signal(list)  # List[StandardLibraryItem]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("📚 Standartlar ve Doküman Kütüphanesi (Standards Library)")
        self.resize(1020, 620)
        self.setMinimumSize(860, 500)
        self.setStyleSheet(theme.get_linear_stylesheet())
        self._build_ui()
        self._refresh_table()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        # 1. ÜST BAŞLIK VE ARAMA ÇUBUĞU
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        lbl_icon = QLabel("📚")
        lbl_icon.setStyleSheet("font-size: 24px;")
        top_row.addWidget(lbl_icon)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        lbl_title = QLabel("ГОСТ & СП Standartlar ve Referans Doküman Kütüphanesi")
        lbl_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {theme.TEXT_PRIMARY};")
        lbl_sub = QLabel(
            "Tabloya eklemek istediğiniz standartları seçebilir, Türkçe ve İngilizce karşılıklarını inceleyebilir "
            "veya kütüphaneye yeni standartlar ekleyebilirsiniz."
        )
        lbl_sub.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_SECONDARY};")
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_sub)
        top_row.addLayout(title_layout, 1)

        main_layout.addLayout(top_row)

        # 2. ARAMA VE FİLTRELEME ARAÇ ÇUBUĞU
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Standart ara (Kod, Rusça, Türkçe veya İngilizce başlık)...")
        self.txt_search.setFixedHeight(32)
        self.txt_search.textChanged.connect(self._on_search_changed)
        filter_bar.addWidget(self.txt_search, 2)

        self.cmb_category = LinearComboBox()
        self.cmb_category.setFixedHeight(32)
        self.cmb_category.setFixedWidth(180)
        self._populate_categories()
        self.cmb_category.currentTextChanged.connect(self._on_search_changed)
        filter_bar.addWidget(self.cmb_category)

        # Kütüphane Yönetim Butonları
        self.btn_add_new = QPushButton("＋ Yeni Standart Ekle")
        self.btn_add_new.setObjectName("primaryButton")
        self.btn_add_new.setStyleSheet(f"""
            QPushButton {{
                background-color: #10b981;
                color: #ffffff;
                font-weight: 600;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        self.btn_add_new.setFixedHeight(32)
        self.btn_add_new.clicked.connect(self._on_add_new)
        filter_bar.addWidget(self.btn_add_new)

        self.btn_edit = QPushButton("✏️ Düzenle")
        self.btn_edit.setObjectName("secondaryButton")
        self.btn_edit.setFixedHeight(32)
        self.btn_edit.clicked.connect(self._on_edit_selected)
        filter_bar.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑️ Kütüphaneden Sil")
        self.btn_delete.setObjectName("dangerButton")
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: #3b1b1b;
                color: #f87171;
                border: 1px solid #7f1d1d;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: #7f1d1d;
                color: #ffffff;
            }}
        """)
        self.btn_delete.setFixedHeight(32)
        self.btn_delete.clicked.connect(self._on_delete_selected)
        filter_bar.addWidget(self.btn_delete)

        main_layout.addLayout(filter_bar)

        # 3. KÜTÜPHANE STANDARTLARI TABLOSU
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Kod / Обозначение",
            "Rusça Başlık / Наименование (RU)",
            "Türkçe Karşılığı (TR)",
            "English Title (EN)",
            "Bölüm (Раздел)",
            "Kategori / Disiplin"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self._on_row_double_clicked)
        main_layout.addWidget(self.table, 1)

        # 4. ALT AKSİYON ÇUBUĞU
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(12)

        self.btn_reset_defaults = QPushButton("🔄 Varsayılanlara Sıfırla")
        self.btn_reset_defaults.setObjectName("ghostButton")
        self.btn_reset_defaults.setFixedHeight(34)
        self.btn_reset_defaults.clicked.connect(self._on_reset_defaults)
        bottom_bar.addWidget(self.btn_reset_defaults)

        self.lbl_count = QLabel("Toplam 0 standart listelendi.")
        self.lbl_count.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px;")
        bottom_bar.addWidget(self.lbl_count)

        bottom_bar.addStretch(1)

        btn_close = QPushButton("✕ Kapat")
        btn_close.setObjectName("ghostButton")
        btn_close.setFixedHeight(34)
        btn_close.clicked.connect(self.reject)
        bottom_bar.addWidget(btn_close)

        self.btn_add_to_table = QPushButton("➕ Seçilenleri Tabloya Aktar")
        self.btn_add_to_table.setObjectName("primaryButton")
        self.btn_add_to_table.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
                font-weight: 700;
                font-size: 12px;
                border-radius: 6px;
                padding: 6px 18px;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_HOVER};
            }}
        """)
        self.btn_add_to_table.setFixedHeight(34)
        self.btn_add_to_table.clicked.connect(self._on_add_to_table)
        bottom_bar.addWidget(self.btn_add_to_table)

        main_layout.addLayout(bottom_bar)

    def _populate_categories(self):
        self.cmb_category.blockSignals(True)
        self.cmb_category.clear()
        self.cmb_category.addItems(standards_library.get_categories())
        self.cmb_category.blockSignals(False)

    def _refresh_table(self):
        query = self.txt_search.text()
        category = self.cmb_category.currentText()
        items = standards_library.search(query, category)

        self.table.setRowCount(len(items))
        for row_idx, item in enumerate(items):
            # 0: Kod
            it_desig = QTableWidgetItem(item.designation)
            it_desig.setData(Qt.ItemDataRole.UserRole, item)
            it_desig.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_desig.setFlags(it_desig.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 1: Rusça
            it_ru = QTableWidgetItem(item.title_ru)
            it_ru.setToolTip(item.title_ru)
            it_ru.setFlags(it_ru.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 2: Türkçe
            it_tr = QTableWidgetItem(item.title_tr)
            it_tr.setToolTip(item.title_tr)
            it_tr.setFlags(it_tr.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 3: İngilizce
            it_en = QTableWidgetItem(item.title_en)
            it_en.setToolTip(item.title_en)
            it_en.setFlags(it_en.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 4: Bölüm
            it_sec = QTableWidgetItem(item.section)
            it_sec.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_sec.setFlags(it_sec.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 5: Kategori
            it_cat = QTableWidgetItem(item.category)
            it_cat.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_cat.setFlags(it_cat.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.table.setItem(row_idx, 0, it_desig)
            self.table.setItem(row_idx, 1, it_ru)
            self.table.setItem(row_idx, 2, it_tr)
            self.table.setItem(row_idx, 3, it_en)
            self.table.setItem(row_idx, 4, it_sec)
            self.table.setItem(row_idx, 5, it_cat)

        self.lbl_count.setText(f"Toplam {len(items)} standart listelendi.")

    def _on_search_changed(self):
        self._refresh_table()

    def _get_selected_items(self) -> List[StandardLibraryItem]:
        selected_rows = sorted(list(set(index.row() for index in self.table.selectedIndexes())))
        results = []
        for r in selected_rows:
            item_widget = self.table.item(r, 0)
            if item_widget:
                std_item = item_widget.data(Qt.ItemDataRole.UserRole)
                if std_item:
                    results.append(std_item)
        return results

    def _on_row_double_clicked(self, item: QTableWidgetItem):
        # Çift tıklamada doğrudan tabloya ekle
        selected = self._get_selected_items()
        if selected:
            self.standards_selected.emit(selected)
            self.accept()

    def _on_add_to_table(self):
        selected = self._get_selected_items()
        if not selected:
            QMessageBox.information(
                self,
                "Seçim Yapılmadı",
                "Lütfen tabloya aktarmak istediğiniz standartları listeden seçin."
            )
            return
        self.standards_selected.emit(selected)
        self.accept()

    def _on_add_new(self):
        dlg = StandardEditDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._populate_categories()
            self._refresh_table()

    def _on_edit_selected(self):
        selected = self._get_selected_items()
        if not selected:
            QMessageBox.information(self, "Standart Seçin", "Lütfen düzenlemek istediğiniz standardı seçin.")
            return
        item_to_edit = selected[0]
        dlg = StandardEditDialog(item=item_to_edit, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._populate_categories()
            self._refresh_table()

    def _on_delete_selected(self):
        selected = self._get_selected_items()
        if not selected:
            QMessageBox.information(self, "Standart Seçin", "Lütfen silmek istediğiniz standardı seçin.")
            return

        reply = QMessageBox.question(
            self,
            "Silme Onayı",
            f"Seçili {len(selected)} adet standardı kütüphaneden kalıcı olarak silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected:
                standards_library.delete(item.id)
            self._populate_categories()
            self._refresh_table()

    def _on_reset_defaults(self):
        reply = QMessageBox.question(
            self,
            "Sıfırlama Onayı",
            "Standartlar kütüphanesini varsayılan 14 temel KM standardına sıfırlamak istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            standards_library.reset_to_defaults()
            self._populate_categories()
            self._refresh_table()
