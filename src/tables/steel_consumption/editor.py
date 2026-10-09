"""
KM Tablo Oluşturucu - 'Ведомость расхода стали' Editörü (SteelConsumptionEditorWidget).
26px kompakt mühendislik satırları, canlı toplam hesaplama ve klavye gezintisi.
"""
from typing import List, Optional, Union
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut, QGuiApplication, QKeyEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel, QAbstractItemView,
    QFrame, QMenu
)

from src.tables.steel_consumption.model import (
    SteelConsumptionItem, SteelConsumptionDocument, build_sample_steel_consumption
)
from src.ui import theme
from src.ui.i18n import i18n
from src.ui.widgets import CyrillicBar, CyrillicKeyboardPanel


class SteelConsumptionTableGrid(QTableWidget):
    """
    Excel tarzı klavye kısayollarını (Enter -> Alt hücre, Tab -> Yan hücre, F2 -> Edit, Esc -> İptal)
    ve sağ tık menüsünü sunan kompakt grid.
    """
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
        act_copy = menu.addAction(f"{i18n.t('action_copy')} (Ctrl+C)")
        act_paste = menu.addAction(f"{i18n.t('action_paste')} (Ctrl+V)")
        menu.addSeparator()
        act_add = menu.addAction(f"+ {i18n.t('add_element')}")
        act_del = menu.addAction(f"🗑 {i18n.t('delete_element')}")
        menu.addSeparator()
        act_up = menu.addAction(f"▲ {i18n.t('move_up')}")
        act_down = menu.addAction(f"▼ {i18n.t('move_down')}")

        action = menu.exec(event.globalPos())
        parent_widget = self.parent()
        if action == act_copy and hasattr(parent_widget, "_copy_to_clipboard"):
            parent_widget._copy_to_clipboard()
        elif action == act_paste and hasattr(parent_widget, "_paste_from_clipboard"):
            parent_widget._paste_from_clipboard()
        elif action == act_add and hasattr(parent_widget, "_add_row"):
            parent_widget._add_row()
        elif action == act_del and hasattr(parent_widget, "_delete_selected_row"):
            parent_widget._delete_selected_row()
        elif action == act_up and hasattr(parent_widget, "_move_row"):
            parent_widget._move_row(-1)
        elif action == act_down and hasattr(parent_widget, "_move_row"):
            parent_widget._move_row(1)


class SteelConsumptionEditorWidget(QWidget):
    """
    Ведомость расхода стали tablosu için modern, 26px kompakt mühendislik veri editörü.
    """
    items_changed = Signal(list)       # List[SteelConsumptionItem]
    document_changed = Signal(object)  # SteelConsumptionDocument

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.items: List[SteelConsumptionItem] = build_sample_steel_consumption()
        self._block_signals = False
        self._last_copied_text = ""

        self._build_ui()
        self._load_items_to_table(self.items)

        i18n.language_changed.connect(self._update_translations)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # 1. ÜST BAŞLIK VE METRİK KARTI (Header Card - 36px)
        header_card = QFrame(self)
        header_card.setFixedHeight(36)
        header_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.COLOR_PANEL_BG};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 5px;
            }}
        """)
        card_layout = QHBoxLayout(header_card)
        card_layout.setContentsMargins(10, 0, 10, 0)
        card_layout.setSpacing(8)

        self.lbl_title = QLabel(i18n.t("steel_consumption_title"), header_card)
        self.lbl_title.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: 0.5px;
        """)
        card_layout.addWidget(self.lbl_title)

        # Standart Rozeti
        lbl_gost_badge = QLabel("ГОСТ 21.502 / КМ", header_card)
        lbl_gost_badge.setStyleSheet(f"""
            background-color: #1E293B;
            color: #38BDF8;
            border: 1px solid #0284C7;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 9px;
            font-weight: 700;
        """)
        card_layout.addWidget(lbl_gost_badge)

        card_layout.addStretch()

        self.lbl_count = QLabel("", header_card)
        self.lbl_count.setStyleSheet(f"""
            background-color: {theme.COLOR_PANEL_ALT};
            color: {theme.COLOR_TEXT_MUTED};
            border: 1px solid {theme.COLOR_BORDER};
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 600;
        """)
        card_layout.addWidget(self.lbl_count)

        self.lbl_grand_total = QLabel("", header_card)
        self.lbl_grand_total.setStyleSheet(f"""
            background-color: rgba(16, 185, 129, 0.15);
            color: {theme.COLOR_SUCCESS};
            border: 1px solid {theme.COLOR_SUCCESS};
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 700;
        """)
        card_layout.addWidget(self.lbl_grand_total)

        main_layout.addWidget(header_card)

        # 2. AKSİYON ARAÇ ÇUBUĞU (Action Bar - 32px)
        action_bar = QFrame(self)
        action_bar.setFixedHeight(32)
        action_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.COLOR_PANEL_ALT};
                border: 1px solid {theme.COLOR_BORDER};
                border-radius: 5px;
            }}
        """)
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(8, 0, 8, 0)
        action_layout.setSpacing(6)

        self.btn_add = QPushButton(i18n.t("add_element"), action_bar)
        self.btn_add.setObjectName("btn_accent")
        self.btn_add.setFixedHeight(24)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self._add_row)
        action_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton(f"🗑 {i18n.t('delete_element')}", action_bar)
        self.btn_delete.setObjectName("btn_danger")
        self.btn_delete.setFixedHeight(24)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self._delete_selected_row)
        action_layout.addWidget(self.btn_delete)

        self.btn_up = QPushButton(f"▲ {i18n.t('move_up')}", action_bar)
        self.btn_up.setFixedHeight(24)
        self.btn_up.clicked.connect(lambda: self._move_row(-1))
        action_layout.addWidget(self.btn_up)

        self.btn_down = QPushButton(f"▼ {i18n.t('move_down')}", action_bar)
        self.btn_down.setFixedHeight(24)
        self.btn_down.clicked.connect(lambda: self._move_row(1))
        action_layout.addWidget(self.btn_down)

        action_layout.addStretch()

        self.btn_samples = QPushButton(f"⟲ {i18n.t('load_samples')}", action_bar)
        self.btn_samples.setFixedHeight(24)
        self.btn_samples.clicked.connect(self._reset_to_samples)
        action_layout.addWidget(self.btn_samples)

        main_layout.addWidget(action_bar)

        # 2. Kiril Harf Şeridi
        self.cyrillic_bar = CyrillicBar(self)
        self.cyrillic_bar.char_clicked.connect(self._insert_char_to_active_cell)
        self.cyrillic_bar.toggle_keyboard.connect(self._toggle_keyboard)
        main_layout.addWidget(self.cyrillic_bar)

        # 3. Açılır Kiril Klavyesi
        self.keyboard_panel = CyrillicKeyboardPanel(self)
        self.keyboard_panel.char_clicked.connect(self._insert_char_to_active_cell)
        self.keyboard_panel.setVisible(False)
        main_layout.addWidget(self.keyboard_panel)

        # 4. Kompakt Tablo Grid
        self.table_widget = SteelConsumptionTableGrid(self)
        self.table_widget.setColumnCount(7)
        self._apply_table_headers()

        header = self.table_widget.horizontalHeader()
        header.setFixedHeight(36)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)

        self.table_widget.setColumnWidth(0, 80)   # Марка
        self.table_widget.setColumnWidth(1, 85)   # Двутавры
        self.table_widget.setColumnWidth(2, 85)   # Швеллеры
        self.table_widget.setColumnWidth(3, 85)   # Уголки
        self.table_widget.setColumnWidth(4, 85)   # Трубы
        self.table_widget.setColumnWidth(5, 85)   # Лист
        self.table_widget.setColumnWidth(6, 95)   # Всего

        self.table_widget.verticalHeader().setDefaultSectionSize(26)
        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table_widget.setAlternatingRowColors(True)

        self.table_widget.cellChanged.connect(self._on_cell_changed)
        main_layout.addWidget(self.table_widget)

        # Kısayollar: Ctrl+V Yapıştır, Ctrl+C Kopyala
        shortcut_paste = QShortcut(QKeySequence.StandardKey.Paste, self.table_widget)
        shortcut_paste.activated.connect(self._paste_from_clipboard)

        shortcut_copy = QShortcut(QKeySequence.StandardKey.Copy, self.table_widget)
        shortcut_copy.activated.connect(self._copy_to_clipboard)

    def _apply_table_headers(self):
        self.table_widget.setHorizontalHeaderLabels([
            i18n.t("col_sc_mark"),
            i18n.t("col_sc_i_beam"),
            i18n.t("col_sc_channel"),
            i18n.t("col_sc_angle"),
            i18n.t("col_sc_tube"),
            i18n.t("col_sc_plate"),
            i18n.t("col_sc_total"),
        ])

    def _update_translations(self, lang: str):
        self.lbl_title.setText(i18n.t("steel_consumption_title"))
        self.btn_add.setText(i18n.t("add_element"))
        self.btn_delete.setText(f"🗑 {i18n.t('delete_element')}")
        self.btn_up.setText(f"▲ {i18n.t('move_up')}")
        self.btn_down.setText(f"▼ {i18n.t('move_down')}")
        self.btn_samples.setText(f"⟲ {i18n.t('load_samples')}")
        self._apply_table_headers()
        self._update_item_count_label()

    def _load_items_to_table(self, items: List[SteelConsumptionItem]):
        self._block_signals = True
        self.table_widget.setRowCount(0)

        for it in items:
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)

            # 0: Marka
            it_mark = QTableWidgetItem(it.mark)
            it_mark.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row, 0, it_mark)

            # 1..5: Profil ağırlıkları
            weights = [it.i_beam, it.channel, it.angle, it.tube, it.plate]
            for col_idx, w in enumerate(weights, start=1):
                txt = f"{w:.1f}" if w > 0 else ""
                it_w = QTableWidgetItem(txt)
                it_w.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table_widget.setItem(row, col_idx, it_w)

            # 6: Toplam (Otomatik hesaplanan)
            tot_val = it.calculate_total()
            it_tot = QTableWidgetItem(f"{tot_val:.1f}")
            it_tot.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it_tot.setFlags(it_tot.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Salt okunur
            it_tot.setForeground(Qt.GlobalColor.cyan)
            self.table_widget.setItem(row, 6, it_tot)

        self._block_signals = False
        self._update_item_count_label()

    def _parse_float(self, val_str: str) -> float:
        clean = val_str.strip().replace(",", ".")
        if not clean or clean == "—" or clean == "-":
            return 0.0
        try:
            return float(clean)
        except ValueError:
            return 0.0

    def _on_cell_changed(self, row: int, col: int):
        if self._block_signals:
            return

        # Profil ağırlığı değiştiyse ilgili satırın toplamını anında güncelle
        if 1 <= col <= 5:
            self._update_row_total(row)

        self._sync_and_emit()

    def _update_row_total(self, row: int):
        weights_sum = 0.0
        for c in range(1, 6):
            item = self.table_widget.item(row, c)
            if item:
                weights_sum += self._parse_float(item.text())

        self._block_signals = True
        tot_item = self.table_widget.item(row, 6)
        if not tot_item:
            tot_item = QTableWidgetItem("")
            tot_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tot_item.setFlags(tot_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            tot_item.setForeground(Qt.GlobalColor.cyan)
            self.table_widget.setItem(row, 6, tot_item)
        tot_item.setText(f"{weights_sum:.1f}")
        self._block_signals = False

    def _sync_and_emit(self):
        cols_meta = [
            (1, "i_beam", "Двутавры"),
            (2, "channel", "Швеллеры"),
            (3, "angle", "Уголки"),
            (4, "tube", "Трубы"),
            (5, "plate", "Лист"),
        ]
        new_items: List[SteelConsumptionItem] = []
        for r in range(self.table_widget.rowCount()):
            mark_item = self.table_widget.item(r, 0)
            mark = mark_item.text().strip() if mark_item else ""

            w_vals = []
            raw_vals = {}
            for col_idx, fld_key, fld_label in cols_meta:
                it = self.table_widget.item(r, col_idx)
                txt = it.text().strip() if it else ""
                clean = txt.replace(",", ".")
                if not clean or clean in ("—", "-"):
                    w_vals.append(0.0)
                else:
                    try:
                        w_vals.append(float(clean))
                    except ValueError:
                        w_vals.append(0.0)
                        raw_vals[fld_key] = txt

            item = SteelConsumptionItem(
                mark=mark,
                i_beam=w_vals[0],
                channel=w_vals[1],
                angle=w_vals[2],
                tube=w_vals[3],
                plate=w_vals[4],
                raw_values=raw_vals,
            )
            item.total = item.calculate_total()
            new_items.append(item)

        self.items = new_items
        self._update_item_count_label()
        self.items_changed.emit(self.items)
        self.document_changed.emit(SteelConsumptionDocument(items=self.items))

    def _update_item_count_label(self):
        count = self.table_widget.rowCount()
        self.lbl_count.setText(i18n.t("elem_count_fmt", count=count))

        grand_total = 0.0
        for it in self.items:
            grand_total += it.calculate_total()
        self.lbl_grand_total.setText(i18n.t("grand_total_fmt", total=f"{grand_total:.1f}"))

    def _add_row(self):
        new_mark = f"Э{self.table_widget.rowCount() + 1}"
        new_item = SteelConsumptionItem(mark=new_mark)
        self.items.append(new_item)
        self._load_items_to_table(self.items)
        self._sync_and_emit()

        last_row = self.table_widget.rowCount() - 1
        self.table_widget.setCurrentCell(last_row, 0)
        self.table_widget.scrollToItem(self.table_widget.item(last_row, 0))

    def _delete_selected_row(self):
        sel_rows = sorted(set(idx.row() for idx in self.table_widget.selectedIndexes()), reverse=True)
        if not sel_rows:
            curr = self.table_widget.currentRow()
            if curr >= 0:
                sel_rows = [curr]

        if not sel_rows or len(self.items) <= 1:
            return

        for r in sel_rows:
            if 0 <= r < len(self.items):
                self.items.pop(r)

        self._load_items_to_table(self.items)
        self._sync_and_emit()

    def _move_row(self, direction: int):
        curr = self.table_widget.currentRow()
        target = curr + direction
        if curr < 0 or target < 0 or target >= len(self.items):
            return

        self.items[curr], self.items[target] = self.items[target], self.items[curr]
        self._load_items_to_table(self.items)
        self.table_widget.setCurrentCell(target, 0)
        self._sync_and_emit()

    def _reset_to_samples(self):
        self.items = build_sample_steel_consumption()
        self._load_items_to_table(self.items)
        self._sync_and_emit()

    def _insert_char_to_active_cell(self, char: str):
        curr_item = self.table_widget.currentItem()
        if curr_item:
            curr_item.setText(curr_item.text() + char)
        else:
            r = self.table_widget.currentRow()
            c = self.table_widget.currentColumn()
            if r >= 0 and c >= 0:
                item = QTableWidgetItem(char)
                self.table_widget.setItem(r, c, item)

    def _toggle_keyboard(self):
        is_vis = self.keyboard_panel.isVisible()
        self.keyboard_panel.setVisible(not is_vis)

    def _copy_to_clipboard(self):
        selected_ranges = self.table_widget.selectedRanges()
        if not selected_ranges:
            curr_r = self.table_widget.currentRow()
            if curr_r >= 0:
                vals = [self.table_widget.item(curr_r, c).text() if self.table_widget.item(curr_r, c) else ""
                        for c in range(self.table_widget.columnCount())]
                text = "\t".join(vals)
                self._last_copied_text = text
                try:
                    QGuiApplication.clipboard().setText(text)
                except Exception:
                    pass
            return

        r_range = selected_ranges[0]
        lines = []
        for r in range(r_range.topRow(), r_range.bottomRow() + 1):
            row_vals = []
            for c in range(r_range.leftColumn(), r_range.rightColumn() + 1):
                item = self.table_widget.item(r, c)
                row_vals.append(item.text() if item else "")
            lines.append("\t".join(row_vals))

        text = "\n".join(lines)
        self._last_copied_text = text
        try:
            QGuiApplication.clipboard().setText(text)
        except Exception:
            pass

    def _paste_from_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text() or getattr(self, "_last_copied_text", "")
        if not text:
            return

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return

        start_row = self.table_widget.currentRow()
        start_col = self.table_widget.currentColumn()
        if start_row < 0:
            start_row = 0
        if start_col < 0:
            start_col = 0

        self._block_signals = True
        for r_offset, line in enumerate(lines):
            target_r = start_row + r_offset
            if target_r >= self.table_widget.rowCount():
                self._block_signals = False
                self._add_row()
                self._block_signals = True

            cols = line.split("\t") if "\t" in line else line.split(";")
            for c_offset, val in enumerate(cols):
                target_c = start_col + c_offset
                if target_c >= self.table_widget.columnCount() or target_c == 6:
                    break
                item = self.table_widget.item(target_r, target_c)
                if not item:
                    item = QTableWidgetItem("")
                    self.table_widget.setItem(target_r, target_c, item)
                item.setText(val.strip())
            self._update_row_total(target_r)

        self._block_signals = False
        self._sync_and_emit()

    def get_document(self) -> SteelConsumptionDocument:
        return SteelConsumptionDocument(items=self.items)

    def set_document(self, doc: Union[SteelConsumptionDocument, List[SteelConsumptionItem]]):
        if isinstance(doc, SteelConsumptionDocument):
            self.items = doc.items
        else:
            self.items = doc
        self._load_items_to_table(self.items)
        self._sync_and_emit()

    def get_items(self) -> List[SteelConsumptionItem]:
        return self.items
