"""
KM Tablo Oluşturucu - 'Ведомость элементов' Editörü (ElementsScheduleWidget).
Excel benzeri veri girişi, 26px kompakt mühendislik satırları, klavye gezintisi ve Kiril klavye entegrasyonu.
"""
from typing import List, Optional, Union
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QKeySequence, QShortcut, QGuiApplication, QKeyEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QComboBox, QLabel, QAbstractItemView,
    QFrame, QMenu, QMessageBox
)

from src.models.sketch import SectionSketch, SketchType
from src.tables.elements_schedule.model import (
    ScheduleItem, ElementPart, ElementsScheduleDocument, build_sample_items
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import LinearComboBox, SolidItemDelegate
from src.ui_v2 import icons
from src.ui.i18n import i18n
from src.ui.widgets import CyrillicBar, CyrillicKeyboardPanel

SKETCH_OPTIONS = [
    ("I (Haddelenmiş Двутавр)", SketchType.I_BEAM, "I"),
    ("1-2 (Kaynaklı I-Kiriş)", SketchType.WELDED_I_BEAM, "1-2"),
    ("1-2-3 (Paket Flanşlı I-Kiriş)", SketchType.WELDED_I_PACKAGE, "1-2-3"),
    ("1-2-3 (Kaynaklı Haç Kolon)", SketchType.WELDED_CRUCIFORM, "1-2-3"),
    ("1-2 (Kaynaklı T-Profil / Тавр)", SketchType.WELDED_T, "1-2"),
    ("1-2 (Kaynaklı Kutu)", SketchType.COMPOUND_BOX_WELDED, "1-2"),
    ("Гн. □ (Kutu Profil)", SketchType.RECT_TUBE, "Гн. □"),
    ("L (Köşebent / Уголок)", SketchType.ANGLE, "L"),
    ("[ (Şveller / Kanal)", SketchType.CHANNEL, "["),
    ("Рифл. (Baklavalı Sac)", SketchType.CHECKERED_PLATE, "Рифл."),
    ("○ (Boru)", SketchType.ROUND_TUBE, "○"),
    ("- (Levha / Lama)", SketchType.PLATE, "-"),
    ("Yok", SketchType.NONE, ""),
]


class EngineeringTableWidget(QTableWidget):
    """
    Excel tarzı klavye kısayollarını (Enter -> Alt hücre, Tab -> Yan hücre, F2 -> Edit, Esc -> İptal)
    ve sağ tık Context Menu desteğini sunan Grid.
    """
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
            # Enter: Bir alt satıra geç
            if self.state() == QAbstractItemView.State.EditingState:
                super().keyPressEvent(event)
            if r + 1 < self.rowCount():
                self.setCurrentCell(r + 1, c)
            event.accept()
            return
        elif key == Qt.Key.Key_Tab:
            # Tab: Bir sonraki sütuna geç
            if c + 1 < self.columnCount():
                self.setCurrentCell(r, c + 1)
            elif r + 1 < self.rowCount():
                self.setCurrentCell(r + 1, 0)
            event.accept()
            return
        elif key == Qt.Key.Key_F2:
            # F2: Düzenlemeyi başlat
            item = self.currentItem()
            if item:
                self.editItem(item)
            event.accept()
            return
        elif key == Qt.Key.Key_Escape:
            # Esc: Düzenlemeyi iptal et
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


class ElementsScheduleWidget(QWidget):
    """
    Ведомость элементов tablosu için modern, 26px kompakt mühendislik veri editörü.
    """
    items_changed = Signal(list)       # List[ScheduleItem]
    document_changed = Signal(object)  # ElementsScheduleDocument

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: List[ScheduleItem] = build_sample_items()
        self._block_signals = False

        self._build_ui()
        self._load_items_to_table(self.items)

        i18n.language_changed.connect(self._update_translations)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # 1. BİLGİ VE BAŞLIK ŞERİDİ (Çerçevesiz, temiz Linear stili)
        header_card = QFrame(self)
        header_card.setFixedHeight(36)
        header_card.setStyleSheet("background: transparent; border: none;")
        card_layout = QHBoxLayout(header_card)
        card_layout.setContentsMargins(4, 0, 4, 0)
        card_layout.setSpacing(8)

        self.lbl_title = QLabel("Ведомость элементов", header_card)
        self.lbl_title.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #FFFFFF;
            background: transparent;
        """)
        card_layout.addWidget(self.lbl_title)

        lbl_gost_badge = QLabel("ГОСТ 21.502 / КМ", header_card)
        lbl_gost_badge.setStyleSheet(f"""
            background-color: {theme.BG_SURFACE_ACTIVE};
            color: {theme.COLOR_ACCENT};
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 600;
        """)
        card_layout.addWidget(lbl_gost_badge)

        self.lbl_count = QLabel("(0 eleman)", header_card)
        self.lbl_count.setStyleSheet(f"""
            color: {theme.TEXT_MUTED};
            font-size: 11px;
            font-weight: 500;
            background: transparent;
        """)
        card_layout.addWidget(self.lbl_count)
        card_layout.addStretch()

        main_layout.addWidget(header_card)

        # ----------------------------------------------------------------------
        # 2. AKSİYON ARAÇ ÇUBUĞU (Belirgin Vurgulu Butonlar)
        # ----------------------------------------------------------------------
        action_bar = QFrame(self)
        action_bar.setFixedHeight(34)
        action_bar.setStyleSheet("background: transparent; border: none;")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)

        # + Eleman Ekle Butonu (Belirgin Yeşil)
        self.btn_add = QPushButton(" Eleman Ekle", action_bar)
        self.btn_add.setIcon(icons.get_icon(icons.ICON_PLUS, color=icons.COLOR_WHITE))
        self.btn_add.setIconSize(icons.icon_size(14))
        self.btn_add.setFixedHeight(30)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: 1px solid #059669;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_add.clicked.connect(self._add_row)
        action_layout.addWidget(self.btn_add)

        # Sil Butonu (Belirgin Kırmızı Vurgu)
        self.btn_del = QPushButton(" Sil", action_bar)
        self.btn_del.setIcon(icons.get_icon(icons.ICON_TRASH, color=icons.COLOR_DANGER))
        self.btn_del.setIconSize(icons.icon_size(14))
        self.btn_del.setFixedHeight(30)
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.setStyleSheet("""
            QPushButton {
                background-color: #2A1A1A;
                color: #EF4444;
                border: 1px solid #7F1D1D;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
                border-color: #DC2626;
            }
        """)
        self.btn_del.clicked.connect(self._delete_selected_row)
        action_layout.addWidget(self.btn_del)

        # Yukarı Taşı Butonu (Belirgin Kontrast)
        self.btn_up = QPushButton(" Yukarı", action_bar)
        self.btn_up.setIcon(icons.get_icon(icons.ICON_UP, color=icons.COLOR_NEUTRAL))
        self.btn_up.setIconSize(icons.icon_size(14))
        self.btn_up.setFixedHeight(30)
        self.btn_up.setToolTip("Seçili satırı yukarı taşı")
        self.btn_up.setStyleSheet("""
            QPushButton {
                background-color: #1E232B;
                color: #E2E8F0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FFFFFF;
            }
        """)
        self.btn_up.clicked.connect(lambda: self._move_row(-1))
        action_layout.addWidget(self.btn_up)

        # Aşağı Taşı Butonu (Belirgin Kontrast)
        self.btn_down = QPushButton(" Aşağı", action_bar)
        self.btn_down.setIcon(icons.get_icon(icons.ICON_DOWN, color=icons.COLOR_NEUTRAL))
        self.btn_down.setIconSize(icons.icon_size(14))
        self.btn_down.setFixedHeight(30)
        self.btn_down.setToolTip("Seçili satırı aşağı taşı")
        self.btn_down.setStyleSheet("""
            QPushButton {
                background-color: #1E232B;
                color: #E2E8F0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FFFFFF;
            }
        """)
        self.btn_down.clicked.connect(lambda: self._move_row(1))
        action_layout.addWidget(self.btn_down)

        action_layout.addStretch()

        # Örnekleri Yükle Butonu
        self.btn_sample = QPushButton(" Örnekleri Yükle", action_bar)
        self.btn_sample.setIcon(icons.get_icon(icons.ICON_SYNC, color=icons.COLOR_MUTED))
        self.btn_sample.setIconSize(icons.icon_size(13))
        self.btn_sample.setFixedHeight(30)
        self.btn_sample.setToolTip("Standart örnek verileri geri yükle")
        self.btn_sample.setStyleSheet("""
            QPushButton {
                background-color: #1E232B;
                color: #94A3B8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FFFFFF;
            }
        """)
        self.btn_sample.clicked.connect(self._reset_to_samples)
        action_layout.addWidget(self.btn_sample)

        # Temizle Butonu (1 Boş Satır Bırakır)
        self.btn_clear = QPushButton(" Temizle", action_bar)
        self.btn_clear.setIcon(icons.get_icon(icons.ICON_TRASH, color=icons.COLOR_MUTED))
        self.btn_clear.setIconSize(icons.icon_size(13))
        self.btn_clear.setFixedHeight(30)
        self.btn_clear.setToolTip("Tablodaki verileri temizler ve 1 adet boş satır bırakır")
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #1E232B;
                color: #94A3B8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2A1A1A;
                color: #EF4444;
                border-color: #7F1D1D;
            }
        """)
        self.btn_clear.clicked.connect(self._clear_table)
        action_layout.addWidget(self.btn_clear)

        main_layout.addWidget(action_bar)

        # 3. KİRİL VE SEMBOL ÇUBUĞU
        self.cyrillic_bar = CyrillicBar(self)
        self.cyrillic_bar.char_clicked.connect(self._insert_char_to_active_cell)
        self.cyrillic_bar.toggle_keyboard.connect(self._toggle_keyboard)
        main_layout.addWidget(self.cyrillic_bar)

        # 4. AÇILIR KİRİL KLAVYESİ
        self.keyboard_panel = CyrillicKeyboardPanel(self)
        self.keyboard_panel.char_clicked.connect(self._insert_char_to_active_cell)
        self.keyboard_panel.setVisible(False)
        main_layout.addWidget(self.keyboard_panel)

        # 5. KOMPAKT MÜHENDİSLİK VERİ TABLOSU (EngineeringTableWidget)
        self.table_widget = EngineeringTableWidget(self)
        self.table_widget.setItemDelegate(SolidItemDelegate(self.table_widget, font_size=13))
        self.table_widget.setColumnCount(8)
        self._apply_table_headers()

        header = self.table_widget.horizontalHeader()
        header.setFixedHeight(44)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)

        # Standart Sütun Genişlikleri (8 Kolon: A, N, M dahil)
        self.table_widget.setColumnWidth(0, 80)   # Марка (Marka)
        self.table_widget.setColumnWidth(1, 135)  # Эскиз (Eskiz)
        self.table_widget.setColumnWidth(2, 160)  # Сечение / Состав (Kesit / Profil)
        self.table_widget.setColumnWidth(3, 75)   # A, кН (Eksenel)
        self.table_widget.setColumnWidth(4, 75)   # N, кН (Normal)
        self.table_widget.setColumnWidth(5, 75)   # M, кН·м (Moment)
        self.table_widget.setColumnWidth(6, 95)   # Сталь (Çelik)
        self.table_widget.setColumnWidth(7, 110)  # Примечание (Not)

        # Satır Yüksekliği: 34px (Geniş ve rahat mühendislik gridi)
        self.table_widget.verticalHeader().setDefaultSectionSize(34)
        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table_widget.setAlternatingRowColors(True)

        self.table_widget.cellChanged.connect(self._on_cell_changed)
        main_layout.addWidget(self.table_widget)

        # 6. TABLO ALTI KULLANIM VE GOST BİLGİLENDİRME KARTI (UsageInfoCard)
        info_card = QFrame(self)
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
            }}
            QLabel {{
                color: {theme.TEXT_MUTED};
                font-size: 11px;
            }}
        """)
        info_layout = QHBoxLayout(info_card)
        info_layout.setContentsMargins(10, 6, 10, 6)
        info_layout.setSpacing(10)

        lbl_info_icon = QLabel("💡")
        info_layout.addWidget(lbl_info_icon)

        self.lbl_info_text = QLabel(i18n.t("info_elements_schedule"))
        self.lbl_info_text.setWordWrap(True)
        info_layout.addWidget(self.lbl_info_text, 1)

        main_layout.addWidget(info_card)

        # Kısayollar: Ctrl+V Yapıştır, Ctrl+C Kopyala
        shortcut_paste = QShortcut(QKeySequence.StandardKey.Paste, self.table_widget)
        shortcut_paste.activated.connect(self._paste_from_clipboard)

        shortcut_copy = QShortcut(QKeySequence.StandardKey.Copy, self.table_widget)
        shortcut_copy.activated.connect(self._copy_to_clipboard)

    def _apply_table_headers(self):
        # 1. Satır: Orijinal Rusça GOST Terimi (Daima Sabit)
        # 2. Satır: Seçilen dilin çevirisi (Dinamik: TR, EN, RU)
        self.table_widget.setHorizontalHeaderLabels([
            f"Марка\n({i18n.t('col_sub_mark')})",
            f"Эскиз\n({i18n.t('col_sub_sketch')})",
            f"Сечение / Состав\n({i18n.t('col_sub_composition')})",
            f"A, кН\n({i18n.t('col_sub_force_a')})",
            f"N, кН\n({i18n.t('col_sub_force_n')})",
            f"M, кН·м\n({i18n.t('col_sub_force_m')})",
            f"Сталь\n({i18n.t('col_sub_steel')})",
            f"Примечание\n({i18n.t('col_sub_note')})"
        ])

    def _update_translations(self, lang_code: str = ""):
        try:
            self.lbl_title.setText(i18n.t("elements_title"))
            self.btn_add.setText(f" {i18n.t('add_element')}")
            self.btn_del.setText(f" {i18n.t('delete_element')}")
            self.btn_up.setText(f" {i18n.t('move_up')}")
            self.btn_down.setText(f" {i18n.t('move_down')}")
            self.btn_sample.setText(f" {i18n.t('load_samples')}")
            self.btn_clear.setText(f" {i18n.t('clear_table')}")
            if hasattr(self, "lbl_info_text"):
                self.lbl_info_text.setText(i18n.t("info_elements_schedule"))
            self._apply_table_headers()
            self._update_count_label()
        except RuntimeError:
            pass

    def _load_items_to_table(self, items: List[ScheduleItem]):
        self._block_signals = True
        self.table_widget.setRowCount(len(items))

        for row_idx, item in enumerate(items):
            # 0: Marka
            it_mark = QTableWidgetItem(item.mark)
            it_mark.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row_idx, 0, it_mark)

            # 1: Eskiz ComboBox
            cb_sketch = LinearComboBox(self.table_widget)
            cb_sketch.setFixedHeight(26)
            for label, stype, sym in SKETCH_OPTIONS:
                cb_sketch.addItem(label, (stype, sym))
            selected_idx = 0
            for opt_idx, (label, stype, sym) in enumerate(SKETCH_OPTIONS):
                if item.sketch.sketch_type == stype:
                    selected_idx = opt_idx
                    break
            cb_sketch.setCurrentIndex(selected_idx)
            cb_sketch.currentIndexChanged.connect(lambda idx, r=row_idx: self._on_sketch_changed(r, idx))
            self.table_widget.setCellWidget(row_idx, 1, cb_sketch)

            # 2: Kesit (Состав)
            comp_str = ", ".join(p.composition for p in item.parts) if item.parts else ""
            it_comp = QTableWidgetItem(comp_str)
            it_comp.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row_idx, 2, it_comp)

            # 3: A, кН (Eksenel)
            it_fa = QTableWidgetItem(item.force_a)
            it_fa.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row_idx, 3, it_fa)

            # 4: N, кН (Normal)
            it_fn = QTableWidgetItem(item.force_n)
            it_fn.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row_idx, 4, it_fn)

            # 5: M, кН·м (Moment)
            it_fm = QTableWidgetItem(item.force_m)
            it_fm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row_idx, 5, it_fm)

            # 6: Сталь (Çelik Kalitesi)
            it_st = QTableWidgetItem(item.steel_grade)
            it_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row_idx, 6, it_st)

            # 7: Примечание (Not)
            it_nt = QTableWidgetItem(item.note)
            it_nt.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row_idx, 7, it_nt)

        self._block_signals = False
        self._update_count_label()

    def _update_count_label(self):
        self.lbl_count.setText(i18n.t("elem_count_fmt", count=self.table_widget.rowCount()))

    def _toggle_keyboard(self):
        is_vis = self.keyboard_panel.isVisible()
        self.keyboard_panel.setVisible(not is_vis)
        self.cyrillic_bar.btn_kb_toggle.setChecked(not is_vis)

    def _insert_char_to_active_cell(self, char: str):
        r = self.table_widget.currentRow()
        c = self.table_widget.currentColumn()
        if r < 0 or c < 0:
            r = 0
            c = 0

        if c == 1:
            return

        item = self.table_widget.item(r, c)
        if item is None:
            item = QTableWidgetItem("")
            self.table_widget.setItem(r, c, item)

        item.setText(item.text() + char)
        self.table_widget.setCurrentCell(r, c)
        self._sync_and_emit()

    def _set_sketch_combo_type(self, cb: QComboBox, target_type: SketchType):
        for idx in range(cb.count()):
            stype, _ = cb.itemData(idx)
            if stype == target_type:
                if cb.currentIndex() != idx:
                    cb.blockSignals(True)
                    cb.setCurrentIndex(idx)
                    cb.blockSignals(False)
                break

    def _auto_format_composition(self, raw_text: str, sketch_type: SketchType) -> str:
        txt = raw_text.strip()
        if not txt:
            return txt

        if sketch_type == SketchType.RECT_TUBE:
            if not (txt.startswith("Гн. □") or txt.startswith("Гн.□")):
                clean = txt.lstrip("□ ").strip()
                return f"Гн. □ {clean}"

        elif sketch_type == SketchType.ANGLE:
            if not (txt.startswith("L ") or txt.startswith("∟") or txt.startswith("уг.")):
                clean = txt.lstrip("L∟ ").strip()
                return f"L {clean}"

        elif sketch_type == SketchType.CHANNEL:
            if not (txt.startswith("[ ") or txt.startswith("Швеллер")):
                clean = txt.lstrip("[ ").strip()
                return f"[ {clean}"

        elif sketch_type == SketchType.CHECKERED_PLATE:
            if not txt.startswith("Рифл."):
                val = txt.lstrip("- ").strip()
                return f"Рифл. -{val}"

        elif sketch_type == SketchType.PLATE:
            if not (txt.startswith("-") or txt.startswith("—") or txt.startswith("Полоса")):
                return f"-{txt}"

        return txt

    def _on_cell_changed(self, row: int, col: int):
        if self._block_signals:
            return

        if col == 2:
            item = self.table_widget.item(row, col)
            if item:
                txt = item.text().strip()
                cb: Optional[QComboBox] = self.table_widget.cellWidget(row, 1)
                if cb:
                    stype, _ = cb.currentData()
                    if txt.startswith("Гн. □") or txt.startswith("□"):
                        self._set_sketch_combo_type(cb, SketchType.RECT_TUBE)
                        stype = SketchType.RECT_TUBE
                    elif txt.startswith("L ") or txt.startswith("∟"):
                        self._set_sketch_combo_type(cb, SketchType.ANGLE)
                        stype = SketchType.ANGLE
                    elif txt.startswith("[ "):
                        self._set_sketch_combo_type(cb, SketchType.CHANNEL)
                        stype = SketchType.CHANNEL
                    elif txt.startswith("Рифл."):
                        self._set_sketch_combo_type(cb, SketchType.CHECKERED_PLATE)
                        stype = SketchType.CHECKERED_PLATE
                    elif txt.startswith("I "):
                        self._set_sketch_combo_type(cb, SketchType.I_BEAM)
                        stype = SketchType.I_BEAM

                    formatted = self._auto_format_composition(txt, stype)
                    if formatted != txt:
                        self._block_signals = True
                        item.setText(formatted)
                        self._block_signals = False

        self._sync_and_emit()

    def _on_sketch_changed(self, row: int, opt_idx: int):
        if self._block_signals:
            return

        cb: Optional[QComboBox] = self.table_widget.cellWidget(row, 1)
        if cb:
            stype, _ = cb.currentData()
            item = self.table_widget.item(row, 2)
            if item and item.text().strip():
                formatted = self._auto_format_composition(item.text().strip(), stype)
                if formatted != item.text().strip():
                    self._block_signals = True
                    item.setText(formatted)
                    self._block_signals = False

        self._sync_and_emit()

    def _sync_and_emit(self):
        items: List[ScheduleItem] = []
        for r in range(self.table_widget.rowCount()):
            mark = (self.table_widget.item(r, 0).text() if self.table_widget.item(r, 0) else "").strip()

            cb: Optional[QComboBox] = self.table_widget.cellWidget(r, 1)
            if cb:
                stype, sym = cb.currentData()
                if stype in (SketchType.COMPOUND_BOX_WELDED, SketchType.WELDED_I_BEAM, SketchType.WELDED_T):
                    sk = SectionSketch(stype, callout_1="1", callout_2="2")
                elif stype in (SketchType.WELDED_I_PACKAGE, SketchType.WELDED_CRUCIFORM):
                    sk = SectionSketch(stype, callout_1="1", callout_2="2", callout_3="3")
                else:
                    sk = SectionSketch(stype, symbol_text=sym)
            else:
                sk = SectionSketch(SketchType.NONE)

            comp = (self.table_widget.item(r, 2).text() if self.table_widget.item(r, 2) else "").strip()
            fa = (self.table_widget.item(r, 3).text() if self.table_widget.item(r, 3) else "").strip()
            fn = (self.table_widget.item(r, 4).text() if self.table_widget.item(r, 4) else "").strip()
            fm = (self.table_widget.item(r, 5).text() if self.table_widget.item(r, 5) else "").strip()
            st = (self.table_widget.item(r, 6).text() if self.table_widget.item(r, 6) else "").strip() or "С255-4"
            nt = (self.table_widget.item(r, 7).text() if self.table_widget.item(r, 7) else "").strip()

            parts: List[ElementPart] = []
            if comp:
                raw_parts = [p.strip() for p in comp.split(",") if p.strip()]
                if len(raw_parts) > 1:
                    for p_idx, rp in enumerate(raw_parts):
                        parts.append(ElementPart(position_no=str(p_idx + 1), composition=rp))
                else:
                    parts.append(ElementPart(position_no="", composition=comp))
            else:
                parts.append(ElementPart(position_no="", composition=""))

            items.append(ScheduleItem(
                mark=mark,
                sketch=sk,
                parts=parts,
                force_a=fa,
                force_n=fn,
                force_m=fm,
                steel_grade=st,
                note=nt
            ))

        self.items = items
        self._update_count_label()
        self.items_changed.emit(self.items)
        self.document_changed.emit(ElementsScheduleDocument(items=self.items))

    def _add_row(self):
        new_row = self.table_widget.rowCount()
        new_mark = f"Б{new_row + 1}"
        new_item = ScheduleItem(
            mark=new_mark,
            sketch=SectionSketch(SketchType.I_BEAM, symbol_text="I"),
            parts=[ElementPart("", "20K1")],
            force_a="0", force_n="0", force_m="0",
            steel_grade="С255-4"
        )
        self.items.append(new_item)
        self._load_items_to_table(self.items)
        self.table_widget.selectRow(new_row)
        self._sync_and_emit()

    def _delete_selected_row(self):
        r = self.table_widget.currentRow()
        if 0 <= r < len(self.items):
            del self.items[r]
            if not self.items:
                # Tüm satırlar silindiyse 1 adet boş satır bırak
                self.items = [
                    ScheduleItem(
                        mark="Б1",
                        sketch=SectionSketch(SketchType.I_BEAM, symbol_text="I"),
                        parts=[ElementPart("", "")],
                        force_a="", force_n="", force_m="",
                        steel_grade="", note=""
                    )
                ]
            self._load_items_to_table(self.items)
            new_r = min(r, len(self.items) - 1)
            if new_r >= 0:
                self.table_widget.selectRow(new_r)
            self._sync_and_emit()

    def _move_row(self, direction: int):
        r = self.table_widget.currentRow()
        target = r + direction
        if 0 <= r < len(self.items) and 0 <= target < len(self.items):
            self.items[r], self.items[target] = self.items[target], self.items[r]
            self._load_items_to_table(self.items)
            self.table_widget.selectRow(target)
            self._sync_and_emit()

    def _reset_to_samples(self):
        self.items = build_sample_items()
        self._load_items_to_table(self.items)
        self._sync_and_emit()

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

        self.items = [
            ScheduleItem(
                mark="Б1",
                sketch=SectionSketch(SketchType.I_BEAM, symbol_text="I"),
                parts=[ElementPart("", "")],
                force_a="", force_n="", force_m="",
                steel_grade="", note=""
            )
        ]
        self._load_items_to_table(self.items)
        self.table_widget.selectRow(0)
        self._sync_and_emit()

    def _copy_to_clipboard(self):
        selected_ranges = self.table_widget.selectedRanges()
        if not selected_ranges:
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
                if target_c >= self.table_widget.columnCount():
                    break
                if target_c == 1:
                    continue
                item = self.table_widget.item(target_r, target_c)
                if not item:
                    item = QTableWidgetItem("")
                    self.table_widget.setItem(target_r, target_c, item)
                item.setText(val.strip())

        self._block_signals = False
        self._sync_and_emit()

    def get_document(self) -> ElementsScheduleDocument:
        return ElementsScheduleDocument(items=self.items)

    def set_document(self, doc: Union[ElementsScheduleDocument, List[ScheduleItem]]):
        if isinstance(doc, ElementsScheduleDocument):
            self.items = doc.items
        else:
            self.items = doc
        self._load_items_to_table(self.items)
        self._sync_and_emit()

    def get_items(self) -> List[ScheduleItem]:
        return self.items
