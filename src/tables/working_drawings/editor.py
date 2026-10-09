"""
ГОСТ Р 21.101-2020 Form 1 'Ведомость рабочих чертежей основного комплекта' Veri Giriş Editörü (WorkingDrawingsEditorWidget).
Kullanıcının tüm pafta satırlarını manuel girebileceği, düzenleyebileceği, Excel'den
kopyalayıp yapıştırabileceği ve canlı CAD tuvalini anında güncelleyebileceği modern arayüz.
Gelecekte PDF'ten otomatik aktarım servisini de besleyecek mimariyle donatılmıştır.
"""
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel, QAbstractItemView, QFrame,
    QMenu, QMessageBox
)

from src.tables.working_drawings.model import (
    WorkingDrawingsDocument, WorkingDrawingItem, get_default_sample_items
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import SolidItemDelegate
from src.ui.i18n import i18n


class WorkingDrawingsTableWidget(QTableWidget):
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
        elif key == Qt.Key.Key_Delete:
            # Seçili hücrelerin içeriğini temizle
            selected = self.selectedItems()
            if selected:
                for it in selected:
                    it.setText("")
                event.accept()
                return

        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        act_copy = menu.addAction("Kopyala (Ctrl+C)")
        act_paste = menu.addAction("Yapıştır (Ctrl+V)")
        menu.addSeparator()
        act_add_row = menu.addAction("＋ Pafta Ekle")
        act_del = menu.addAction("🗑️ Satır Sil")
        menu.addSeparator()
        act_up = menu.addAction("▲ Yukarı Taşı")
        act_down = menu.addAction("▼ Aşağı Taşı")
        menu.addSeparator()
        act_clear = menu.addAction("🧹 Tümünü Temizle")

        action = menu.exec(event.globalPos())
        parent_widget = self.parent()
        if action == act_copy and hasattr(parent_widget, "_copy_to_clipboard"):
            parent_widget._copy_to_clipboard()
        elif action == act_paste and hasattr(parent_widget, "_paste_from_clipboard"):
            parent_widget._paste_from_clipboard()
        elif action == act_add_row and hasattr(parent_widget, "_add_row"):
            parent_widget._add_row()
        elif action == act_del and hasattr(parent_widget, "_delete_selected_row"):
            parent_widget._delete_selected_row()
        elif action == act_up and hasattr(parent_widget, "_move_row"):
            parent_widget._move_row(-1)
        elif action == act_down and hasattr(parent_widget, "_move_row"):
            parent_widget._move_row(1)
        elif action == act_clear and hasattr(parent_widget, "_clear_table"):
            parent_widget._clear_table()


class WorkingDrawingsEditorWidget(QWidget):
    """
    ГОСТ Р 21.101 Form 1 'Ведомость рабочих чертежей основного комплекта' Manuel Veri Editörü.
    """
    document_changed = Signal(object)  # WorkingDrawingsDocument

    def __init__(self, parent=None):
        super().__init__(parent)
        self.document = WorkingDrawingsDocument()
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

        # Pafta Ekle Butonu (Zümrüt Yeşili)
        self.btn_add = QPushButton("＋ Pafta Ekle")
        self.btn_add.setFixedHeight(32)
        self.btn_add.setStyleSheet("""
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
        self.btn_add.clicked.connect(self._add_row)
        toolbar.addWidget(self.btn_add)

        # Satır Sil Butonu (Kırmızı)
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

        # Yukarı / Aşağı Taşıma Butonları
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

        # Örnek Verileri Yükle Butonu (Görseldeki 10 satırı yükler)
        self.btn_sample = QPushButton("📋 Örnek KM Doldur")
        self.btn_sample.setObjectName("ghostButton")
        self.btn_sample.setFixedHeight(30)
        self.btn_sample.clicked.connect(self._load_sample_template)
        toolbar.addWidget(self.btn_sample)

        # Gelecek Özellik: PDF'ten Aktar Butonu
        self.btn_pdf = QPushButton("📄 PDF'ten Aktar (Yakında)")
        self.btn_pdf.setObjectName("ghostButton")
        self.btn_pdf.setFixedHeight(30)
        self.btn_pdf.setToolTip("Gelecek sürümde: Proje PDF pafta setinden otomatik çizim listesi çıkarılacaktır.")
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.setStyleSheet("""
            QPushButton:disabled {
                color: #64748B;
                border: 1px dashed #334155;
                background-color: transparent;
            }
        """)
        toolbar.addWidget(self.btn_pdf)

        # Temizle Butonu
        self.btn_clear = QPushButton("🧹 Temizle")
        self.btn_clear.setObjectName("ghostButton")
        self.btn_clear.setFixedHeight(30)
        self.btn_clear.clicked.connect(self._clear_table)
        toolbar.addWidget(self.btn_clear)

        main_layout.addLayout(toolbar)

        # 2. VERİ GİRİŞ TABLOSU (Grid)
        self.table = WorkingDrawingsTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setItemDelegate(SolidItemDelegate(self.table))

        # Çift Dilli Sütun Başlıkları
        self._apply_headers()

        # Sütun Genişlikleri ve Davranışı
        # 0: Лист (Pafta No) -> ~110px
        # 1: Наименование (Adı) -> Stretch
        # 2: Примечание (Not) -> ~130px
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(2, 130)

        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.verticalHeader().setVisible(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)

        self.table.itemChanged.connect(self._on_item_changed)
        main_layout.addWidget(self.table, 1)

        # 3. KULLANIM VE BİLGİ KARTI
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

        self.lbl_info_title = QLabel(i18n.t("info_working_drawings_title"))
        self.lbl_info_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {theme.TEXT_PRIMARY};")
        self.lbl_info_desc = QLabel(i18n.t("info_working_drawings_desc"))
        self.lbl_info_desc.setStyleSheet(f"font-size: 10px; color: {theme.TEXT_SECONDARY}; line-height: 14px;")
        ic_layout.addWidget(self.lbl_info_title)
        ic_layout.addWidget(self.lbl_info_desc)
        main_layout.addWidget(info_card)

        # Dil değişimini dinle
        i18n.language_changed.connect(self._on_language_changed)
        self._on_language_changed()

    def _on_language_changed(self, lang_code: str = ""):
        """Dil değiştiğinde butonları, başlıkları ve bilgi kartını günceller."""
        try:
            if hasattr(self, "btn_add"):
                self.btn_add.setText(f"＋ {i18n.t('btn_add_sheet')}")
            if hasattr(self, "btn_delete"):
                self.btn_delete.setText(f"🗑️ {i18n.t('btn_delete_row')}")
            if hasattr(self, "btn_up"):
                self.btn_up.setText(f"▲ {i18n.t('btn_move_up')}")
            if hasattr(self, "btn_down"):
                self.btn_down.setText(f"▼ {i18n.t('btn_move_down')}")
            if hasattr(self, "btn_sample"):
                self.btn_sample.setText(f"📋 {i18n.t('btn_load_samples')}")
            if hasattr(self, "btn_clear"):
                self.btn_clear.setText(f"🧹 {i18n.t('btn_clear')}")
            if hasattr(self, "lbl_info_title"):
                self.lbl_info_title.setText(i18n.t("info_working_drawings_title"))
            if hasattr(self, "lbl_info_desc"):
                self.lbl_info_desc.setText(i18n.t("info_working_drawings_desc"))
            self._apply_headers()
        except RuntimeError:
            pass

    def _apply_headers(self):
        """Çift dilli (Rusça GOST + Aktif Dil) başlıkları uygular."""
        if i18n.current_language == "RU":
            headers = ["Лист", "Наименование", "Примечание"]
        else:
            sub_sheet = i18n.t("col_sub_sheet_num") if i18n.t("col_sub_sheet_num") != "col_sub_sheet_num" else "Pafta No"
            sub_name = i18n.t("col_sub_drawing_name") if i18n.t("col_sub_drawing_name") != "col_sub_drawing_name" else "Çizim Adı"
            sub_note = i18n.t("col_sub_note") if i18n.t("col_sub_note") != "col_sub_note" else "Not"
            headers = [
                f"Лист\n({sub_sheet})",
                f"Наименование\n({sub_name})",
                f"Примечание\n({sub_note})",
            ]
        self.table.setHorizontalHeaderLabels(headers)

    def _load_document_to_table(self, doc: WorkingDrawingsDocument):
        self._is_loading = True
        self.table.setRowCount(0)

        for item in doc.items:
            r = self.table.rowCount()
            self.table.insertRow(r)

            it_sheet = QTableWidgetItem(item.sheet_number)
            it_sheet.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 0, it_sheet)

            it_name = QTableWidgetItem(item.name)
            it_name.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 1, it_name)

            it_note = QTableWidgetItem(item.note)
            it_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 2, it_note)

        self._is_loading = False
        self._sync_document()

    def _sync_document(self):
        """Tablodaki verileri model nesnesine aktarır ve sinyal fırlatır."""
        items: List[WorkingDrawingItem] = []
        for r in range(self.table.rowCount()):
            it_sheet = self.table.item(r, 0)
            it_name = self.table.item(r, 1)
            it_note = self.table.item(r, 2)

            sheet_val = it_sheet.text().strip() if it_sheet else ""
            name_val = it_name.text().strip() if it_name else ""
            note_val = it_note.text().strip() if it_note else ""

            # Boş satırları atlamadan sırayı koru
            items.append(WorkingDrawingItem(
                sheet_number=sheet_val,
                name=name_val,
                note=note_val,
            ))

        self.document.items = items
        self.document_changed.emit(self.document)

    def _on_item_changed(self, item: QTableWidgetItem):
        if self._is_loading:
            return
        self._sync_document()

    def _add_row(self):
        """Tablo sonuna veya seçili satırın altına yeni boş pafta satırı ekler."""
        selected_rows = self._get_selected_rows()
        r = selected_rows[-1] + 1 if selected_rows else self.table.rowCount()

        self._is_loading = True
        self.table.insertRow(r)

        # Varsayılan pafta no tahmini (önceki satırdan +1)
        next_sheet_num = ""
        if r > 0:
            prev_sheet_item = self.table.item(r - 1, 0)
            if prev_sheet_item and prev_sheet_item.text().strip().isdigit():
                next_sheet_num = str(int(prev_sheet_item.text().strip()) + 1)

        it_sheet = QTableWidgetItem(next_sheet_num)
        it_sheet.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(r, 0, it_sheet)

        it_name = QTableWidgetItem("")
        it_name.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(r, 1, it_name)

        it_note = QTableWidgetItem("")
        it_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(r, 2, it_note)

        self._is_loading = False
        self.table.selectRow(r)
        self.table.setCurrentCell(r, 0)
        self._sync_document()

    def _delete_selected_row(self):
        """Seçili satırları siler."""
        selected_rows = self._get_selected_rows()
        if not selected_rows:
            return

        self._is_loading = True
        for r in reversed(selected_rows):
            self.table.removeRow(r)

        # Eğer tüm satırlar silindiyse en az 1 boş satır bırak
        if self.table.rowCount() == 0:
            self._is_loading = False
            self._add_row()
            return

        self._is_loading = False
        self._sync_document()

    def _move_row(self, direction: int):
        """Seçili satırı yukarı (-1) veya aşağı (+1) taşır."""
        selected_rows = self._get_selected_rows()
        if len(selected_rows) != 1:
            return
        r = selected_rows[0]
        target = r + direction
        if target < 0 or target >= self.table.rowCount():
            return

        self._is_loading = True
        # Hücre içeriklerini al
        sheet_text = self.table.item(r, 0).text() if self.table.item(r, 0) else ""
        name_text = self.table.item(r, 1).text() if self.table.item(r, 1) else ""
        note_text = self.table.item(r, 2).text() if self.table.item(r, 2) else ""

        self.table.removeRow(r)
        self.table.insertRow(target)

        it_s = QTableWidgetItem(sheet_text)
        it_s.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(target, 0, it_s)

        it_n = QTableWidgetItem(name_text)
        it_n.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(target, 1, it_n)

        it_nt = QTableWidgetItem(note_text)
        it_nt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(target, 2, it_nt)

        self._is_loading = False
        self.table.selectRow(target)
        self._sync_document()

    def _load_sample_template(self):
        """Kullanıcının gönderdiği referans görseldeki 10 satırı yükler."""
        self.document = WorkingDrawingsDocument(items=get_default_sample_items())
        self._load_document_to_table(self.document)

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
        self._add_row()

    def _get_selected_rows(self) -> List[int]:
        selected = set()
        for idx in self.table.selectedIndexes():
            selected.add(idx.row())
        return sorted(list(selected))

    def _copy_to_clipboard(self):
        """Seçili hücreleri panoya tab-ayrımlı formatta kopyalar."""
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

        QGuiApplication.clipboard().setText("\n".join(lines))

    def _paste_from_clipboard(self):
        """Panodaki Excel veya metin verilerini imleçten itibaren yapıştırır."""
        clip_text = QGuiApplication.clipboard().text()
        if not clip_text:
            return

        lines = [line for line in clip_text.splitlines() if line]
        if not lines:
            return

        start_row = self.table.currentRow()
        start_col = self.table.currentColumn()
        if start_row < 0:
            start_row = self.table.rowCount()
        if start_col < 0:
            start_col = 0

        self._is_loading = True
        for r_offset, line in enumerate(lines):
            target_row = start_row + r_offset
            if target_row >= self.table.rowCount():
                self.table.insertRow(self.table.rowCount())

            cols = line.split("\t")
            for c_offset, val in enumerate(cols):
                target_col = start_col + c_offset
                if target_col >= 3:
                    break
                it = self.table.item(target_row, target_col)
                if not it:
                    it = QTableWidgetItem()
                    if target_col in (0, 2):
                        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    else:
                        it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(target_row, target_col, it)
                it.setText(val.strip())

        self._is_loading = False
        self._sync_document()

    def set_document(self, document: WorkingDrawingsDocument):
        self.document = document
        self._load_document_to_table(document)

    def get_document(self) -> WorkingDrawingsDocument:
        return self.document
