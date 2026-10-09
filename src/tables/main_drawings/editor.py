"""
ГОСТ Р 21.101-2020 Form 2 'Ведомость основных комплектов рабочих чертежей' Veri Giriş Editörü (MainDrawingsEditorWidget).
Kullanıcının tüm çizim takımı satırlarını manuel girebileceği, düzenleyebileceği, Excel'den
kopyalayıp yapıştırabileceği ve canlı CAD tuvalini anında güncelleyebileceği modern arayüz.
"""
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel, QAbstractItemView, QFrame,
    QMenu, QMessageBox
)

from src.tables.main_drawings.model import (
    MainDrawingsDocument, DrawingSetItem, get_default_sample_items
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import SolidItemDelegate
from src.ui.i18n import i18n


class MainDrawingsTableWidget(QTableWidget):
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
        act_add_row = menu.addAction("＋ Takım Ekle")
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


class MainDrawingsEditorWidget(QWidget):
    """
    ГОСТ Р 21.101 Form 2 'Ведомость основных комплектов рабочих чертежей' Manuel Veri Editörü.
    """
    document_changed = Signal(object)  # MainDrawingsDocument

    def __init__(self, parent=None):
        super().__init__(parent)
        self.document = MainDrawingsDocument()
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

        # Takım Ekle Butonu (Zümrüt Yeşili)
        self.btn_add = QPushButton("＋ Çizim Takımı Ekle")
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

        # Örnek Verileri Yükle Butonu
        self.btn_sample = QPushButton("📋 Örnek Verileri Yükle")
        self.btn_sample.setObjectName("ghostButton")
        self.btn_sample.setFixedHeight(30)
        self.btn_sample.clicked.connect(self._load_sample_template)
        toolbar.addWidget(self.btn_sample)

        # Temizle Butonu
        self.btn_clear = QPushButton("🧹 Temizle")
        self.btn_clear.setObjectName("ghostButton")
        self.btn_clear.setFixedHeight(30)
        self.btn_clear.clicked.connect(self._clear_table)
        toolbar.addWidget(self.btn_clear)

        main_layout.addLayout(toolbar)

        # 2. VERİ GİRİŞ TABLOSU (Grid)
        self.table = MainDrawingsTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setItemDelegate(SolidItemDelegate(self.table))

        # Çift Dilli Sütun Başlıkları
        self._apply_headers()

        # Sütun Genişlikleri ve Davranışı
        # 0: Обозначение (Kod) -> ~180px
        # 1: Наименование (Adı) -> Stretch
        # 2: Примечание (Not) -> ~120px
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(2, 120)

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

        self.lbl_info_title = QLabel(i18n.t("info_main_drawings_title"))
        self.lbl_info_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {theme.TEXT_PRIMARY};")
        self.lbl_info_desc = QLabel(i18n.t("info_main_drawings_desc"))
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
                self.btn_add.setText(f"＋ {i18n.t('btn_add_drawing_set')}")
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
                self.lbl_info_title.setText(i18n.t("info_main_drawings_title"))
            if hasattr(self, "lbl_info_desc"):
                self.lbl_info_desc.setText(i18n.t("info_main_drawings_desc"))
            self._apply_headers()
        except RuntimeError:
            pass

    def _apply_headers(self):
        """Çift dilli (Rusça GOST + Aktif Dil) başlıkları uygular."""
        if i18n.current_language == "RU":
            headers = ["Обозначение", "Наименование", "Примечание"]
        else:
            sub_code = i18n.t("col_sub_code") if i18n.t("col_sub_code") != "col_sub_code" else "Kod"
            sub_name = i18n.t("col_sub_drawing_name") if i18n.t("col_sub_drawing_name") != "col_sub_drawing_name" else "Adı / Açıklama"
            sub_note = i18n.t("col_sub_note") if i18n.t("col_sub_note") != "col_sub_note" else "Not"
            headers = [
                f"Обозначение\n({sub_code})",
                f"Наименование\n({sub_name})",
                f"Примечание\n({sub_note})",
            ]
        self.table.setHorizontalHeaderLabels(headers)

    def _load_document_to_table(self, doc: MainDrawingsDocument):
        self._is_loading = True
        self.table.setRowCount(0)

        for item in doc.items:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self._fill_row(r, item)

        self._is_loading = False

    def _fill_row(self, row_idx: int, item: DrawingSetItem):
        # 0: Обозначение
        it_desig = QTableWidgetItem(item.designation)
        it_desig.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row_idx, 0, it_desig)

        # 1: Наименование
        it_name = QTableWidgetItem(item.name)
        it_name.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row_idx, 1, it_name)

        # 2: Примечание
        it_note = QTableWidgetItem(item.note)
        it_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row_idx, 2, it_note)

    def _on_item_changed(self, item: QTableWidgetItem):
        if self._is_loading:
            return
        self._sync_and_emit()

    def _sync_and_emit(self):
        """Griddeki güncel verileri MainDrawingsDocument modeline aktarır ve sinyali yayar."""
        items: List[DrawingSetItem] = []
        for r in range(self.table.rowCount()):
            desig_it = self.table.item(r, 0)
            name_it = self.table.item(r, 1)
            note_it = self.table.item(r, 2)

            desig = desig_it.text().strip() if desig_it else ""
            name = name_it.text().strip() if name_it else ""
            note = note_it.text().strip() if note_it else ""

            items.append(DrawingSetItem(
                designation=desig,
                name=name,
                note=note,
            ))

        self.document.items = items
        self.document_changed.emit(self.document)

    def _add_row(self):
        """Yeni bir çizim takımı satırı ekler."""
        row_idx = self.table.rowCount()
        cur_row = self.table.currentRow()
        insert_idx = (cur_row + 1) if cur_row >= 0 else row_idx

        self._is_loading = True
        self.table.insertRow(insert_idx)
        new_item = DrawingSetItem(
            designation="",
            name="",
            note="",
        )
        self._fill_row(insert_idx, new_item)
        self._is_loading = False

        self._sync_and_emit()
        self.table.selectRow(insert_idx)
        self.table.setCurrentCell(insert_idx, 0)

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
            self.table.insertRow(0)
            self._fill_row(0, DrawingSetItem(designation="", name="", note=""))

        self._is_loading = False
        self.table.selectRow(0)
        self.table.setCurrentCell(0, 0)
        self._sync_and_emit()

    def _move_row(self, delta: int):
        """Satırı yukarı veya aşağı taşır."""
        cur = self.table.currentRow()
        if cur < 0:
            return
        target = cur + delta
        if 0 <= target < self.table.rowCount():
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
        """Kullanıcının ilettiği referans görseldeki 12 satırlık gerçek KM verilerini yükler."""
        self.document = MainDrawingsDocument(items=get_default_sample_items())
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
        self.table.insertRow(0)
        self._fill_row(0, DrawingSetItem(designation="", name="", note=""))
        self._is_loading = False
        self.table.selectRow(0)
        self.table.setCurrentCell(0, 0)
        self._sync_and_emit()

    def _copy_to_clipboard(self):
        """Seçili hücreleri panoya TSV (Excel/Google Sheets uyumlu) formatında kopyalar."""
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
        """Panodaki TSV verilerini (Excel / Sheets) mevcut konuma yapıştırır."""
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

    def get_document(self) -> MainDrawingsDocument:
        return self.document

    def set_document(self, doc: MainDrawingsDocument):
        self.document = doc
        self._load_document_to_table(doc)
