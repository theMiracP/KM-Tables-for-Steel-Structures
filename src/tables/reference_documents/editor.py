"""
'Ведомость ссылочных и прилагаемых документов' Veri Giriş Editörü (ReferenceDocsEditorWidget).
Kullanıcının hazır standartları kütüphaneden seçebileceği, Türkçe ve İngilizce karşılıklarını
görebileceği, yeni standartlar ekleyip düzenleyebileceği ve CAD tuvalini canlı güncelleyebileceği arayüz.
"""
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel, QAbstractItemView, QFrame,
    QMenu, QMessageBox
)

from src.tables.reference_documents.model import (
    ReferenceDocsDocument, ReferenceDocItem, StandardLibraryItem
)
from src.tables.reference_documents.library import standards_library
from src.tables.reference_documents.dialogs import StandardsLibraryDialog
from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import SolidItemDelegate
from src.ui.i18n import i18n


class ReferenceDocsTableWidget(QTableWidget):
    """Excel tarzı klavye kısayollarını (Enter -> Alt hücre, Tab -> Yan hücre, F2 -> Edit) destekleyen grid."""
    def __init__(self, parent=None):
        super().__init__(parent)
        f = self.font()
        f.setPointSize(10)
        self.setFont(f)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        r = self.currentRow()
        c = self.currentColumn()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.state() == QAbstractItemView.State.EditingState:
                super().keyPressEvent(event)
            if r + 1 < self.rowCount():
                self.setCurrentCell(r + 1, c)
            event.accept()
            return
        elif key == Qt.Key.Key_Tab:
            if c + 1 < self.columnCount():
                self.setCurrentCell(r, c + 1)
            elif r + 1 < self.rowCount():
                self.setCurrentCell(r + 1, 0)
            event.accept()
            return
        elif key == Qt.Key.Key_F2:
            item = self.currentItem()
            if item:
                self.editItem(item)
            event.accept()
            return
        elif key == Qt.Key.Key_Escape:
            super().keyPressEvent(event)
            return

        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        act_copy = menu.addAction("Kopyala (Ctrl+C)")
        act_paste = menu.addAction("Yapıştır (Ctrl+V)")
        menu.addSeparator()
        act_lib = menu.addAction("📚 Standart Kütüphanesinden Seç...")
        act_add_doc = menu.addAction("＋ Doküman Ekle")
        act_add_sec = menu.addAction("📑 Bölüm Ekle")
        act_del = menu.addAction("🗑️ Satır Sil")
        menu.addSeparator()
        act_up = menu.addAction("▲ Yukarı Taşı")
        act_down = menu.addAction("▼ Aşağı Taşı")

        action = menu.exec(event.globalPos())
        parent_widget = self.parent()
        if action == act_copy and hasattr(parent_widget, "_copy_to_clipboard"):
            parent_widget._copy_to_clipboard()
        elif action == act_paste and hasattr(parent_widget, "_paste_from_clipboard"):
            parent_widget._paste_from_clipboard()
        elif action == act_lib and hasattr(parent_widget, "_open_library"):
            parent_widget._open_library()
        elif action == act_add_doc and hasattr(parent_widget, "_add_doc_row"):
            parent_widget._add_doc_row()
        elif action == act_add_sec and hasattr(parent_widget, "_add_section_row"):
            parent_widget._add_section_row()
        elif action == act_del and hasattr(parent_widget, "_delete_selected_row"):
            parent_widget._delete_selected_row()
        elif action == act_up and hasattr(parent_widget, "_move_row"):
            parent_widget._move_row(-1)
        elif action == act_down and hasattr(parent_widget, "_move_row"):
            parent_widget._move_row(1)


class ReferenceDocsEditorWidget(QWidget):
    """
    ГОСТ Р 21.101 Form 2 'Ведомость ссылочных и прилагаемых документов' Editörü.
    """
    document_changed = Signal(object)  # ReferenceDocsDocument

    def __init__(self, parent=None):
        super().__init__(parent)
        self.document = standards_library.build_default_document()
        self._is_loading = False

        self._build_ui()
        self._load_document_to_table(self.document)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 1. HIZLI EYLEM VE ARAÇ ÇUBUĞU (TOOLBAR)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # Kütüphane Butonu (Vurgulu)
        self.btn_library = QPushButton("📚 Standart Kütüphanesi")
        self.btn_library.setObjectName("primaryButton")
        self.btn_library.setFixedHeight(32)
        self.btn_library.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
                font-weight: 700;
                font-size: 11px;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_HOVER};
            }}
        """)
        self.btn_library.clicked.connect(self._open_library)
        toolbar.addWidget(self.btn_library)

        # Doküman Ekle Butonu
        self.btn_add_doc = QPushButton("＋ Doküman Ekle")
        self.btn_add_doc.setFixedHeight(32)
        self.btn_add_doc.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 11px;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_add_doc.clicked.connect(self._add_doc_row)
        toolbar.addWidget(self.btn_add_doc)

        # Bölüm Ekle Butonu
        self.btn_add_sec = QPushButton("📑 Bölüm Ekle")
        self.btn_add_sec.setObjectName("secondaryButton")
        self.btn_add_sec.setFixedHeight(32)
        self.btn_add_sec.clicked.connect(self._add_section_row)
        toolbar.addWidget(self.btn_add_sec)

        # Sil Butonu
        self.btn_delete = QPushButton("🗑️ Sil")
        self.btn_delete.setFixedHeight(32)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #3B1818;
                color: #EF4444;
                font-weight: 600;
                font-size: 11px;
                border: 1px solid #7F1D1D;
                border-radius: 4px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        self.btn_delete.clicked.connect(self._delete_selected_row)
        toolbar.addWidget(self.btn_delete)

        # Yukarı / Aşağı Butonları
        self.btn_up = QPushButton("▲ Yukarı")
        self.btn_up.setObjectName("ghostButton")
        self.btn_up.setFixedHeight(30)
        self.btn_up.clicked.connect(lambda: self._move_row(-1))
        toolbar.addWidget(self.btn_up)

        self.btn_down = QPushButton("▼ Aşağı")
        self.btn_down.setObjectName("ghostButton")
        self.btn_down.setFixedHeight(30)
        self.btn_down.clicked.connect(lambda: self._move_row(1))
        toolbar.addWidget(self.btn_down)

        toolbar.addStretch(1)

        # Hazır KM Şablonu
        self.btn_sample = QPushButton("📋 Hazır KM Standartları")
        self.btn_sample.setObjectName("ghostButton")
        self.btn_sample.setFixedHeight(30)
        self.btn_sample.clicked.connect(self._load_sample_template)
        toolbar.addWidget(self.btn_sample)

        # Temizle Butonu
        self.btn_clear = QPushButton("🗑️ Temizle")
        self.btn_clear.setObjectName("ghostButton")
        self.btn_clear.setFixedHeight(30)
        self.btn_clear.clicked.connect(self._clear_table)
        toolbar.addWidget(self.btn_clear)

        main_layout.addLayout(toolbar)

        # 2. VERİ GİRİŞ TABLOSU (Grid)
        self.table = ReferenceDocsTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setItemDelegate(SolidItemDelegate(self.table))

        # Çift Dilli Sütun Başlıkları
        self._apply_headers()

        # Genişlikler ve Davranış
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.verticalHeader().setVisible(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)

        self.table.itemChanged.connect(self._on_item_changed)
        main_layout.addWidget(self.table, 1)

        # 3. KULLANIM VE GOST BİLGİ KARTI
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        ic_layout = QVBoxLayout(info_card)
        ic_layout.setContentsMargins(10, 8, 10, 8)
        ic_layout.setSpacing(4)

        self.lbl_info_title = QLabel(i18n.t("info_ref_docs_title"))
        self.lbl_info_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {theme.TEXT_PRIMARY};")
        self.lbl_info_desc = QLabel(i18n.t("info_ref_docs_desc"))
        self.lbl_info_desc.setStyleSheet(f"font-size: 10px; color: {theme.TEXT_SECONDARY}; line-height: 1.4;")
        self.lbl_info_desc.setWordWrap(True)

        ic_layout.addWidget(self.lbl_info_title)
        ic_layout.addWidget(self.lbl_info_desc)
        main_layout.addWidget(info_card)

        # Dil değişimini dinle
        i18n.language_changed.connect(self._on_language_changed)

    def _apply_headers(self):
        """Tablo başlıklarını çift dilli formatta uygular."""
        sub_code = i18n.t("col_sub_code") if i18n.t("col_sub_code") != "col_sub_code" else "Kod / Standart No"
        sub_ru = i18n.t("col_sub_ru") if i18n.t("col_sub_ru") != "col_sub_ru" else "Rusça Başlık"
        sub_tr = i18n.t("col_sub_tr") if i18n.t("col_sub_tr") != "col_sub_tr" else "Türkçe Karşılığı"
        sub_en = i18n.t("col_sub_en") if i18n.t("col_sub_en") != "col_sub_en" else "English Title"
        sub_sec = i18n.t("col_sub_sec") if i18n.t("col_sub_sec") != "col_sub_sec" else "Bölüm"
        sub_note = i18n.t("col_sub_note") if i18n.t("col_sub_note") != "col_sub_note" else "Not"

        headers = [
            f"Обозначение\n({sub_code})",
            f"Наименование (RU)\n({sub_ru})",
            f"Türkçe Karşılığı\n({sub_tr})",
            f"English Title\n({sub_en})",
            f"Раздел\n({sub_sec})",
            f"Примечание\n({sub_note})",
        ]
        self.table.setHorizontalHeaderLabels(headers)

    def _on_language_changed(self, lang: Optional[str] = None):
        """Dil değiştiğinde başlıkları, butonları ve bilgi notunu günceller."""
        self._apply_headers()

        # Toolbar butonları
        self.btn_library.setText(f"📚 {i18n.t('btn_standards_lib')}")
        self.btn_add_doc.setText(f"＋ {i18n.t('btn_add_document')}")
        self.btn_add_sec.setText(f"📑 {i18n.t('btn_add_section')}")
        self.btn_delete.setText(f"🗑️ {i18n.t('btn_delete_row')}")
        self.btn_up.setText(f"▲ {i18n.t('btn_move_up')}")
        self.btn_down.setText(f"▼ {i18n.t('btn_move_down')}")
        self.btn_sample.setText(f"📋 {i18n.t('btn_km_samples')}")
        self.btn_clear.setText(f"🗑️ {i18n.t('btn_clear')}")

        # Bilgi kartı
        self.lbl_info_title.setText(i18n.t("info_ref_docs_title"))
        self.lbl_info_desc.setText(i18n.t("info_ref_docs_desc"))

        # Bölüm satırları etiketini güncelle
        tag = i18n.t("tag_section")
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 0)
            if it and any(kw in it.text().upper() for kw in ["[BÖLÜM]", "[SECTION]", "[РАЗДЕЛ]", "BÖLÜM", "SECTION", "РАЗДЕЛ"]):
                it.setText(f"📑 [{tag}]")

    def get_document(self) -> ReferenceDocsDocument:
        return self.document

    def set_document(self, document: ReferenceDocsDocument):
        self.document = document
        self._load_document_to_table(document)

    def _load_document_to_table(self, document: ReferenceDocsDocument):
        self._is_loading = True
        self.table.setRowCount(len(document.items))

        for row_idx, item in enumerate(document.items):
            self._fill_row(row_idx, item)

        self._is_loading = False

    def _fill_row(self, row_idx: int, item: ReferenceDocItem):
        # 0: Обозначение
        it_desig = QTableWidgetItem(item.designation)
        it_desig.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1: Наименование (RU)
        it_ru = QTableWidgetItem(item.title)

        # 2: Türkçe
        it_tr = QTableWidgetItem(item.title_tr)

        # 3: İngilizce
        it_en = QTableWidgetItem(item.title_en)

        # 4: Bölüm (Раздел)
        it_sec = QTableWidgetItem(item.section)
        it_sec.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # 5: Примечание
        it_note = QTableWidgetItem(item.note)
        it_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Eğer bu satır bir bölüm başlığı ise görsel olarak vurgula
        if item.is_section_header:
            it_desig.setFlags(it_desig.flags() & ~Qt.ItemFlag.ItemIsEditable)
            tag = i18n.t("tag_section")
            it_desig.setText(f"📑 [{tag}]")
            font = it_ru.font()
            font.setBold(True)
            it_ru.setFont(font)
            it_ru.setText(item.title or "Ссылочные документы")

        self.table.setItem(row_idx, 0, it_desig)
        self.table.setItem(row_idx, 1, it_ru)
        self.table.setItem(row_idx, 2, it_tr)
        self.table.setItem(row_idx, 3, it_en)
        self.table.setItem(row_idx, 4, it_sec)
        self.table.setItem(row_idx, 5, it_note)

    def _sync_and_emit(self):
        if self._is_loading:
            return

        new_items: List[ReferenceDocItem] = []
        for r in range(self.table.rowCount()):
            it_desig = self.table.item(r, 0)
            it_ru = self.table.item(r, 1)
            it_tr = self.table.item(r, 2)
            it_en = self.table.item(r, 3)
            it_sec = self.table.item(r, 4)
            it_note = self.table.item(r, 5)

            desig_text = it_desig.text().strip() if it_desig else ""
            ru_text = it_ru.text().strip() if it_ru else ""
            tr_text = it_tr.text().strip() if it_tr else ""
            en_text = it_en.text().strip() if it_en else ""
            sec_text = it_sec.text().strip() if it_sec else "Ссылочные документы"
            note_text = it_note.text().strip() if it_note else ""

            is_sec_header = (
                any(tag in desig_text.upper() for tag in ["[BÖLÜM]", "[SECTION]", "[РАЗДЕЛ]", "BÖLÜM", "SECTION", "РАЗДЕЛ"])
                or (not desig_text and r < len(self.document.items) and self.document.items[r].is_section_header)
                or (r < len(self.document.items) and self.document.items[r].is_section_header)
            )

            new_items.append(ReferenceDocItem(
                designation="" if is_sec_header else desig_text,
                title=ru_text,
                title_tr=tr_text,
                title_en=en_text,
                section=sec_text,
                note=note_text,
                is_section_header=is_sec_header,
            ))

        self.document.items = new_items
        self.document_changed.emit(self.document)

    def _on_item_changed(self, item: QTableWidgetItem):
        if self._is_loading:
            return

        col = item.column()
        row = item.row()

        # Otomatik tamamlama: Eğer kullanıcı kod sütununa (0) standart yazdıysa ve kütüphanede varsa
        if col == 0:
            entered_code = item.text().strip()
            if entered_code and not any(tag in entered_code.upper() for tag in ["[BÖLÜM]", "[SECTION]", "[РАЗДЕЛ]", "BÖLÜM", "SECTION", "РАЗДЕЛ"]):
                match = standards_library.get_by_designation(entered_code)
                if match:
                    self._is_loading = True
                    it_ru = self.table.item(row, 1)
                    it_tr = self.table.item(row, 2)
                    it_en = self.table.item(row, 3)
                    it_sec = self.table.item(row, 4)
                    if it_ru and not it_ru.text().strip():
                        it_ru.setText(match.title_ru)
                    if it_tr and not it_tr.text().strip():
                        it_tr.setText(match.title_tr)
                    if it_en and not it_en.text().strip():
                        it_en.setText(match.title_en)
                    if it_sec and not it_sec.text().strip():
                        it_sec.setText(match.section)
                    self._is_loading = False

        self._sync_and_emit()

    def _open_library(self):
        """Standartlar kütüphanesi arama ve seçim modalını açar."""
        dlg = StandardsLibraryDialog(parent=self)
        dlg.standards_selected.connect(self._add_standards_from_library)
        dlg.exec()

    def _add_standards_from_library(self, standards: List[StandardLibraryItem]):
        """Kütüphaneden seçilen standartları mevcut tabloya ekler."""
        if not standards:
            return

        self._is_loading = True
        start_row = self.table.rowCount()
        self.table.setRowCount(start_row + len(standards))

        for idx, std in enumerate(standards):
            row_idx = start_row + idx
            ref_item = std.to_reference_item()
            self._fill_row(row_idx, ref_item)

        self._is_loading = False
        self._sync_and_emit()
        self.table.selectRow(start_row)

    def _add_doc_row(self):
        """Yeni boş bir doküman satırı ekler."""
        row_idx = self.table.rowCount()
        cur_row = self.table.currentRow()
        insert_idx = (cur_row + 1) if cur_row >= 0 else row_idx

        self._is_loading = True
        self.table.insertRow(insert_idx)
        new_item = ReferenceDocItem(
            designation="",
            title="",
            title_tr="",
            title_en="",
            section="Ссылочные документы",
            note="",
            is_section_header=False,
        )
        self._fill_row(insert_idx, new_item)
        self._is_loading = False

        self._sync_and_emit()
        self.table.selectRow(insert_idx)
        self.table.setCurrentCell(insert_idx, 0)

    def _add_section_row(self):
        """Yeni bir bölüm ayraç başlığı (Ссылочные / Прилагаемые) ekler."""
        row_idx = self.table.rowCount()
        cur_row = self.table.currentRow()
        insert_idx = (cur_row + 1) if cur_row >= 0 else row_idx

        self._is_loading = True
        self.table.insertRow(insert_idx)
        sec_item = ReferenceDocItem(
            designation="",
            title="Прилагаемые документы",
            title_tr="Ek Dokümanlar",
            title_en="Attached Documents",
            section="Прилагаемые документы",
            note="",
            is_section_header=True,
        )
        self._fill_row(insert_idx, sec_item)
        self._is_loading = False

        self._sync_and_emit()
        self.table.selectRow(insert_idx)
        self.table.setCurrentCell(insert_idx, 1)

    def _delete_selected_row(self):
        """Seçili satırları siler."""
        selected_rows = sorted(list(set(idx.row() for idx in self.table.selectedIndexes())), reverse=True)
        if not selected_rows:
            return

        self._is_loading = True
        for r in selected_rows:
            self.table.removeRow(r)

        # Eğer tüm satırlar silindiyse en az 1 boş satır bırak
        if self.table.rowCount() == 0:
            self._is_loading = False
            self._add_doc_row()
            return

        self._is_loading = False
        self._sync_and_emit()

    def _move_row(self, delta: int):
        """Satırı yukarı veya aşağı taşır."""
        cur = self.table.currentRow()
        if cur < 0:
            return
        target = cur + delta
        if 0 <= target < self.table.rowCount():
            # Satır verilerini takas et
            self._is_loading = True
            row_items = []
            for c in range(self.table.columnCount()):
                item = self.table.takeItem(cur, c)
                row_items.append(item)

            self.table.removeRow(cur)
            self.table.insertRow(target)
            for c, it in enumerate(row_items):
                self.table.setItem(target, c, it)
            self._is_loading = False

            self.table.selectRow(target)
            self._sync_and_emit()

    def _load_sample_template(self):
        """Referans görseldeki 14 KM standardını sıfırdan yükler."""
        self.document = standards_library.build_default_document()
        self._load_document_to_table(self.document)
        self.document_changed.emit(self.document)

    def _clear_table(self, prompt: bool = True):
        """Tablodaki verileri temizler ve 1 adet boş satır bırakır."""
        if prompt:
            reply = QMessageBox.question(
                self,
                "Tabloyu Temizle",
                "Tablodaki verileri temizlemek istediğinizden emin misiniz? (1 boş satır bırakılacaktır)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._is_loading = True
        self.table.setRowCount(0)
        self._is_loading = False
        self._add_doc_row()

    def _copy_to_clipboard(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return
        r_range = selected_ranges[0]
        lines = []
        for r in range(r_range.topRow(), r_range.bottomRow() + 1):
            row_vals = []
            for c in range(r_range.leftColumn(), r_range.rightColumn() + 1):
                it = self.table.item(r, c)
                row_vals.append(it.text() if it else "")
            lines.append("\t".join(row_vals))
        text = "\n".join(lines)
        QGuiApplication.clipboard().setText(text)

    def _paste_from_clipboard(self):
        text = QGuiApplication.clipboard().text()
        if not text:
            return
        cur_row = self.table.currentRow()
        cur_col = self.table.currentColumn()
        if cur_row < 0:
            cur_row = 0
        if cur_col < 0:
            cur_col = 0

        lines = text.strip().split("\n")
        self._is_loading = True
        for dr, line in enumerate(lines):
            r = cur_row + dr
            if r >= self.table.rowCount():
                self.table.insertRow(r)
            vals = line.split("\t")
            for dc, val in enumerate(vals):
                c = cur_col + dc
                if c < self.table.columnCount():
                    it = self.table.item(r, c)
                    if not it:
                        it = QTableWidgetItem()
                        self.table.setItem(r, c, it)
                    it.setText(val.strip())
        self._is_loading = False
        self._sync_and_emit()
