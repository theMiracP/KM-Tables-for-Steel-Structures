"""
KM Tablo Oluşturucu - 'Ведомость элементов' Editörü (ElementsScheduleWidget).
Excel benzeri veri girişi, 26px kompakt mühendislik satırları, klavye gezintisi ve Kiril klavye entegrasyonu.
"""
from typing import List, Optional, Union
from PySide6.QtCore import Qt, Signal, QEvent, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QGuiApplication, QKeyEvent, QAction, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QComboBox, QLabel, QAbstractItemView,
    QFrame, QMenu, QMessageBox, QLineEdit, QApplication
)

from src.models.sketch import SectionSketch, SketchType
from src.tables.elements_schedule.model import (
    ScheduleItem, ElementPart, ElementsScheduleDocument, build_sample_items
)
from src.tables.elements_schedule.sketch_renderer import get_sketch_icon
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

WELDED_SKETCH_TYPES = {
    SketchType.WELDED_I_BEAM,
    SketchType.COMPOUND_BOX_WELDED,
    SketchType.WELDED_T,
    SketchType.WELDED_I_PACKAGE,
    SketchType.WELDED_CRUCIFORM,
}

def sketch_type_to_profile_category(stype: SketchType) -> Optional[str]:
    """Eskiz tipine göre GOST Sortament kütüphanesindeki ilgili kategori adını döndürür."""
    mapping = {
        SketchType.I_BEAM: "Двутавры",
        SketchType.CHANNEL: "Швеллеры",
        SketchType.RECT_TUBE: "Трубы профильные",
        SketchType.ROUND_TUBE: "Трубы круглые",
        SketchType.ANGLE: "Уголки",
    }
    return mapping.get(stype)

def clean_profile_prefix(txt: str) -> str:
    """
    Metinden eski eskiz ön eklerini (örn. 'I ', '[ ', 'L ', 'Гн. □ ', 'Рифл. -', '-') temizler.
    Böylece eskiz tipi değiştirildiğinde eski tipin sembolü kalıntı yapmaz.
    """
    s = txt.strip()
    prefixes = ["Гн. □", "Гн.□", "Рифл. -", "Рифл.-", "Рифл.", "L ", "∟ ", "уг. ", "[ ", "I ", "- ", "— ", "– ", "-"]
    changed = True
    while changed:
        changed = False
        for p in prefixes:
            if s.startswith(p):
                s = s[len(p):].strip()
                changed = True
                break
    return s

def get_profile_full_name(designation: str, sketch_type: SketchType) -> str:
    """
    Profil adını eskiz tipine uygun GOST sembolü / ön ekiyle formatlar.
    Örn:
    - 20Б1 -> I 20Б1
    - 140x100x6.0 -> Гн. □ 140x100x6.0
    - 16П -> [ 16П
    - 75х5 -> L 75х5
    - 70x4.0 -> ○ ⌀ 70x4.0
    """
    clean = clean_profile_prefix(designation)
    if not clean:
        return ""
    if sketch_type == SketchType.I_BEAM:
        return f"I {clean}"
    elif sketch_type == SketchType.RECT_TUBE:
        return f"Гн. □ {clean}"
    elif sketch_type == SketchType.CHANNEL:
        return f"[ {clean}"
    elif sketch_type == SketchType.ANGLE:
        return f"L {clean}"
    elif sketch_type == SketchType.ROUND_TUBE:
        if clean.startswith("⌀") or clean.startswith("ø") or clean.startswith("Ø"):
            return f"○ {clean}"
        return f"○ ⌀ {clean}"
    elif sketch_type == SketchType.CHECKERED_PLATE:
        return f"Рифл. -{clean}"
    elif sketch_type == SketchType.PLATE:
        return f"-{clean}"
    return clean

def get_profiles_for_sketch(stype: SketchType) -> List[str]:
    """Aktif eskiz tipine uygun tüm profil isimlerini ön ekleriyle birlikte liste olarak döndürür."""
    from src.services.profile_database import GostProfileDatabase
    db = GostProfileDatabase.instance()
    cat = sketch_type_to_profile_category(stype)
    if not cat:
        if stype in WELDED_SKETCH_TYPES:
            if stype in (SketchType.WELDED_I_PACKAGE, SketchType.WELDED_CRUCIFORM):
                return [
                    "-300 x 14, -260 x 12, -500 x 10",
                    "-250 x 12, -200 x 10, -400 x 8",
                    "-350 x 16, -300 x 14, -600 x 12",
                ]
            else:
                return [
                    "-130 x 12, -106 x 12",
                    "-160 x 14, -120 x 10",
                    "-200 x 16, -150 x 12",
                    "-250 x 16, -200 x 14",
                    "-300 x 18, -250 x 14",
                ]
        elif stype == SketchType.CHECKERED_PLATE:
            return ["Рифл. -4x1000", "Рифл. -5x1000", "Рифл. -6x1000", "Рифл. -8x1000"]
        elif stype == SketchType.PLATE:
            return ["-10x200", "-12x250", "-14x300", "-16x350", "-20x400"]
        return []

    recs = db.filter_profiles(category=cat)
    return [get_profile_full_name(r.designation, stype) for r in recs]


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
        elif key == Qt.Key.Key_F4:
            # F4: 2. sütundaysa profil/kesit düzenleyiciyi aç
            if c == 2:
                parent_w = self.parent()
                if parent_w and hasattr(parent_w, "_open_section_editor_for_row"):
                    parent_w._open_section_editor_for_row(r)
                    event.accept()
                    return
        elif key in (Qt.Key.Key_Escape,):
            # Esc: Düzenlemeyi iptal et
            super().keyPressEvent(event)
            return
        elif key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            # Seçili hücrelerin içeriğini temizle (Eskiz combo hariç)
            if self.state() != QAbstractItemView.State.EditingState:
                parent_w = self.parent()
                if parent_w and hasattr(parent_w, "_block_signals"):
                    parent_w._block_signals = True
                try:
                    for item in self.selectedItems():
                        if item.column() != 1:
                            item.setText("")
                            if item.column() == 2:
                                item.setIcon(QIcon())
                finally:
                    if parent_w and hasattr(parent_w, "_block_signals"):
                        parent_w._block_signals = False
                if parent_w and hasattr(parent_w, "_sync_and_emit"):
                    parent_w._sync_and_emit()
                event.accept()
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


class ProfileCellDelegate(SolidItemDelegate):
    """
    Profil/kesit sütunu için açılır dropdown menüden (ComboBox) kolay profil seçimi,
    anında arama/tamamlama ve GOST kütüphane erişimi sunan delege.
    """
    def __init__(self, owner_widget, parent=None, font_size: int = 13):
        super().__init__(parent, font_size)
        self.owner = owner_widget

    def createEditor(self, parent, option, index):
        if index.column() == 2:
            row = index.row()
            cb = LinearComboBox(parent)
            cb.setEditable(True)
            cb.setMaxVisibleItems(15)

            line_edit = cb.lineEdit()
            if line_edit:
                line_edit.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: {theme.BG_SURFACE_ACTIVE};
                        color: #ffffff;
                        border: none;
                        padding: 2px 28px 2px 8px;
                        font-size: {self.font_size}px;
                        font-weight: 500;
                    }}
                """)
                # Hücre içi sağ aksiyon butonu (GOST Profil / Kesit Kütüphanesi - F4)
                browse_act = line_edit.addAction(
                    icons.get_icon(icons.ICON_SEARCH, color=icons.COLOR_PRIMARY),
                    QLineEdit.ActionPosition.TrailingPosition
                )
                browse_act.setToolTip("GOST Profil / Kesit Kütüphanesi (F4)")
                browse_act.triggered.connect(lambda: self.owner._open_section_editor_for_row(row))
                line_edit.textChanged.connect(lambda text, r=row: self.owner._on_profile_text_changed(r, text))

            cb.setStyleSheet(f"""
                QComboBox {{
                    background-color: {theme.BG_SURFACE_ACTIVE};
                    color: #ffffff;
                    border: 1.5px solid {theme.ACCENT_PRIMARY};
                    border-radius: 4px;
                    padding-left: 2px;
                    font-size: {self.font_size}px;
                }}
            """)
            return cb
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() == 2 and isinstance(editor, QComboBox):
            row = index.row()
            current_txt = index.data(Qt.ItemDataRole.DisplayRole) or ""

            # Aktif satırın eskiz tipini al
            cb_sk = self.owner.table_widget.cellWidget(row, 1)
            stype = SketchType.I_BEAM
            if cb_sk:
                stype, _ = cb_sk.currentData()

            # Eskiz tipine uygun profilleri al
            profiles = get_profiles_for_sketch(stype)

            editor.blockSignals(True)
            editor.clear()

            # Eğer mevcut metin listede yoksa en başa ekle
            if current_txt and current_txt not in profiles:
                editor.addItem(current_txt)

            for p in profiles:
                editor.addItem(p)

            editor.insertSeparator(editor.count())
            editor.addItem("📚 GOST Profil Kütüphanesi (F4)...")
            editor.addItem("➕ Yeni Özel Profil Ekle...")

            editor.setEditText(current_txt)
            editor.blockSignals(False)

            # Kullanıcı hücreye tıklar tıklamaz dropdown'ı anında aç (1 tıkla seçim kolaylığı)
            QTimer.singleShot(0, editor.showPopup)
            return

        super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 2 and isinstance(editor, QComboBox):
            row = index.row()
            val = editor.currentText().strip()

            if val == "📚 GOST Profil Kütüphanesi (F4)...":
                QTimer.singleShot(0, lambda: self.owner._open_section_editor_for_row(row))
                return
            elif val == "➕ Yeni Özel Profil Ekle...":
                QTimer.singleShot(0, lambda: self.owner._open_add_custom_profile_dialog(row))
                return

            cb_sk = self.owner.table_widget.cellWidget(row, 1)
            stype = SketchType.I_BEAM
            if cb_sk:
                stype, _ = cb_sk.currentData()

            formatted = self.owner._auto_format_composition(val, stype)
            model.setData(index, formatted, Qt.ItemDataRole.EditRole)
            self.owner._on_cell_changed(row, index.column())
            return

        super().setModelData(editor, model, index)


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

        # GOST Profil Kütüphanesi Butonu (Item 2.1)
        self.btn_profile_picker = QPushButton(" 📚 GOST Profil...", action_bar)
        self.btn_profile_picker.setFixedHeight(30)
        self.btn_profile_picker.setToolTip("GOST Rus Çelik Sortament / Profil Kütüphanesinden Seç")
        self.btn_profile_picker.setStyleSheet("""
            QPushButton {
                background-color: #1E232B;
                color: #38BDF8;
                border: 1px solid #0369A1;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0369A1;
                color: #FFFFFF;
            }
        """)
        self.btn_profile_picker.clicked.connect(lambda: self._open_section_editor_for_row())
        action_layout.addWidget(self.btn_profile_picker)

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
        self.table_widget.setItemDelegate(ProfileCellDelegate(self, self.table_widget, font_size=13))
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
        self.table_widget.setColumnWidth(3, 75)   # A, кН (Kesme)
        self.table_widget.setColumnWidth(4, 75)   # N, кН (Eksenel)
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
        self.table_widget.cellDoubleClicked.connect(self._on_cell_double_clicked)
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
                cb_sketch.addItem(get_sketch_icon(stype), label, (stype, sym))
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
            if len(item.parts) == 1 and item.sketch.sketch_type != SketchType.NONE and item.sketch.sketch_type not in WELDED_SKETCH_TYPES:
                comp_str = get_profile_full_name(comp_str, item.sketch.sketch_type)
            it_comp = QTableWidgetItem(comp_str)
            it_comp.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            it_comp.setIcon(get_sketch_icon(item.sketch.sketch_type))
            self.table_widget.setItem(row_idx, 2, it_comp)

            # 3: A, кН (Kesme)
            it_fa = QTableWidgetItem(item.force_a)
            it_fa.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row_idx, 3, it_fa)

            # 4: N, кН (Eksenel)
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
        # 1. Hücre düzenleyicisi (QLineEdit) açıksa doğrudan imleç konumuna ekle
        focus_w = QApplication.focusWidget()
        if isinstance(focus_w, QLineEdit) and self.table_widget.isAncestorOf(focus_w):
            focus_w.insert(char)
            r = self.table_widget.currentRow()
            c = self.table_widget.currentColumn()
            if c == 2 and r >= 0:
                self._on_profile_text_changed(r, focus_w.text())
            return

        for edit in self.table_widget.findChildren(QLineEdit):
            if edit.isVisible():
                edit.insert(char)
                r = self.table_widget.currentRow()
                c = self.table_widget.currentColumn()
                if c == 2 and r >= 0:
                    self._on_profile_text_changed(r, edit.text())
                return

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
        self._on_cell_changed(r, c)

    def _detect_sketch_type(self, raw_text: str) -> Optional[SketchType]:
        txt = raw_text.strip()
        if not txt:
            return None

        # 1. Açık GOST sembolleri ve anahtar kelimeler
        if txt.startswith("Гн. □") or txt.startswith("□") or txt.startswith("Гн."):
            return SketchType.RECT_TUBE
        if txt.startswith("L ") or txt.startswith("∟") or txt.startswith("уг."):
            return SketchType.ANGLE
        if txt.startswith("[ ") or txt.startswith("Швеллер"):
            return SketchType.CHANNEL
        if txt.startswith("Рифл."):
            return SketchType.CHECKERED_PLATE
        if txt.startswith("I ") or txt.startswith("Двутавр"):
            return SketchType.I_BEAM
        if txt.startswith("○") or txt.startswith("ø") or txt.startswith("Ø") or txt.startswith("Труба"):
            return SketchType.ROUND_TUBE
        if txt.startswith("-") or txt.startswith("—") or txt.startswith("–") or txt.startswith("Полоса") or txt.startswith("Лист"):
            return SketchType.PLATE

        # 2. Tipik Rusça Profil Kodları (Haddelenmiş I-kirişler: 20К1, 25Ш1, 30Б2, 40К1 vb.)
        import re
        if re.search(r"^\d{2,3}[БШКДbshkd]\d?", txt, re.IGNORECASE):
            return SketchType.I_BEAM
        if re.search(r"^\d{1,2}[ПУпу]", txt, re.IGNORECASE):
            return SketchType.CHANNEL
        if re.search(r"^\d+[xX\*хХ]\d+[xX\*хХ]\d+", txt):
            return SketchType.RECT_TUBE

        return None

    def _on_profile_text_changed(self, row: int, text: str):
        """Kullanıcı hücrede profil ismini yazarken yalnızca eskiz açılır menüsünü anında günceller; tuvali kasmaması için arka plan hücresini tetiklemez."""
        cb: Optional[QComboBox] = self.table_widget.cellWidget(row, 1)
        if not cb:
            return
        det = self._detect_sketch_type(text)
        if det is not None:
            self._set_sketch_combo_type(cb, det)

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

        # Kaynaklı tiplerde elle ön ek formatlaması yapma (WeldedSectionDialog yönetir)
        if sketch_type in WELDED_SKETCH_TYPES:
            return txt

        return get_profile_full_name(txt, sketch_type)

    def _on_cell_changed(self, row: int, col: int):
        if self._block_signals:
            return

        self._block_signals = True
        try:
            if col == 2:
                item = self.table_widget.item(row, col)
                if item:
                    txt = item.text().strip()
                    cb: Optional[QComboBox] = self.table_widget.cellWidget(row, 1)
                    if cb:
                        det = self._detect_sketch_type(txt)
                        if det is not None:
                            self._set_sketch_combo_type(cb, det)
                            stype = det
                        else:
                            stype, _ = cb.currentData()

                        formatted = self._auto_format_composition(txt, stype)
                        if formatted != txt:
                            item.setText(formatted)
                        item.setIcon(get_sketch_icon(stype))
        finally:
            self._block_signals = False

        self._sync_and_emit()

    def _on_cell_double_clicked(self, row: int, col: int):
        """Hücreye çift tıklandığında kesit/profil kolonundaysa düzenleyici diyaloğunu açar."""
        if col == 2:
            self._open_section_editor_for_row(row)

    def _on_sketch_changed(self, row: int, opt_idx: int):
        if self._block_signals:
            return

        cb: Optional[QComboBox] = self.table_widget.cellWidget(row, 1)
        if not cb:
            return

        stype, _ = cb.currentData()
        item = self.table_widget.item(row, 2)
        if not item:
            return

        # TÜM DEĞİŞİKLİKLERİ block_signals İÇİNDE YAP!
        # item.setIcon veya item.setText çağrısı cellChanged'i tetikler,
        # o da eski metne bakıp combobox'ı tekrar geriye çevirir!
        self._block_signals = True
        try:
            item.setIcon(get_sketch_icon(stype))
            cur_txt = item.text().strip()
            if cur_txt:
                formatted = self._auto_format_composition(cur_txt, stype)
                if formatted != cur_txt:
                    item.setText(formatted)
        finally:
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

    def _open_section_editor_for_row(self, row: Optional[int] = None):
        """
        Eskiz tipine göre dinamik profil / kesit düzenleyiciyi açar:
        - Kaynaklı kesitler (1-2, 1-2-3 vb.): WeldedSectionDialog açılarak levha bileşenleri girilir.
        - Haddelenmiş / standart profiller (I, [, L, □, ○ vb.): GostProfilePickerDialog ilgili kategori ön-seçili olarak açılır.
        """
        from src.ui_v2.profile_picker_dialog import GostProfilePickerDialog
        from src.tables.elements_schedule.welded_dialog import WeldedSectionDialog

        if row is None or row < 0:
            row = self.table_widget.currentRow()
        if row < 0:
            if self.table_widget.rowCount() == 0:
                self._add_row()
                row = 0
            else:
                row = 0
                self.table_widget.selectRow(0)

        cb: Optional[QComboBox] = self.table_widget.cellWidget(row, 1)
        stype = SketchType.I_BEAM
        if cb:
            stype, _ = cb.currentData()

        current_item = self.table_widget.item(row, 2)
        current_comp = current_item.text().strip() if current_item else ""

        if stype in WELDED_SKETCH_TYPES:
            dlg = WeldedSectionDialog(sketch_type=stype, current_composition=current_comp, parent=self)
            if dlg.exec() and dlg.result_composition:
                res_comp = dlg.result_composition
                self._block_signals = True
                try:
                    if current_item:
                        current_item.setText(res_comp)
                        current_item.setIcon(get_sketch_icon(stype))
                    else:
                        it = QTableWidgetItem(res_comp)
                        it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                        it.setIcon(get_sketch_icon(stype))
                        self.table_widget.setItem(row, 2, it)
                finally:
                    self._block_signals = False
                self._sync_and_emit()
        else:
            # Standart GOST sortament kütüphanesi
            initial_cat = sketch_type_to_profile_category(stype)
            clean_q = clean_profile_prefix(current_comp)
            dlg = GostProfilePickerDialog(parent=self, initial_query=clean_q, category=initial_cat)
            if dlg.exec() and dlg.selected_profile:
                p = dlg.selected_profile
                self._block_signals = True
                try:
                    # Profil adını ata
                    new_stype = p.get_sketch_type_enum()
                    full_name = get_profile_full_name(p.designation, new_stype)
                    if current_item:
                        current_item.setText(full_name)
                    else:
                        it = QTableWidgetItem(full_name)
                        it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                        self.table_widget.setItem(row, 2, it)

                    # Eskiz ComboBox'ını güncelle
                    if cb:
                        self._set_sketch_combo_type(cb, new_stype)
                    it_c = self.table_widget.item(row, 2)
                    if it_c:
                        it_c.setIcon(get_sketch_icon(new_stype))

                    # Çelik kalitesi
                    st_item = self.table_widget.item(row, 6)
                    if st_item and (not st_item.text().strip() or st_item.text() in ("С255-4", "С255")):
                        st_item.setText(p.default_steel)
                finally:
                    self._block_signals = False

                self._sync_and_emit()

    def _open_profile_picker(self):
        """Geriye dönük uyumluluk: aktif satır için kesit düzenleyiciyi açar."""
        self._open_section_editor_for_row()

    def _open_add_custom_profile_dialog(self, row: Optional[int] = None):
        """Kullanıcının kütüphaneye yeni özel profil eklemesi için diyaloğu açar."""
        from src.ui_v2.profile_picker_dialog import AddCustomProfileDialog
        if row is None or row < 0:
            row = self.table_widget.currentRow()
        if row < 0:
            row = 0

        cb_sk = self.table_widget.cellWidget(row, 1)
        init_cat = "Двутавры"
        if cb_sk:
            stype, _ = cb_sk.currentData()
            init_cat = sketch_type_to_profile_category(stype) or "Двутавры"

        dlg = AddCustomProfileDialog(parent=self, initial_category=init_cat)
        if dlg.exec() and dlg.created_profile:
            p = dlg.created_profile
            self._block_signals = True
            try:
                new_stype = p.get_sketch_type_enum()
                full_name = get_profile_full_name(p.designation, new_stype)
                it = self.table_widget.item(row, 2)
                if it:
                    it.setText(full_name)
                    it.setIcon(get_sketch_icon(new_stype))
                else:
                    it = QTableWidgetItem(full_name)
                    it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    it.setIcon(get_sketch_icon(new_stype))
                    self.table_widget.setItem(row, 2, it)

                if cb_sk:
                    self._set_sketch_combo_type(cb_sk, new_stype)

                st_item = self.table_widget.item(row, 6)
                if st_item and (not st_item.text().strip() or st_item.text() in ("С255-4", "С255")):
                    st_item.setText(p.default_steel)
            finally:
                self._block_signals = False

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
        import copy
        if isinstance(doc, ElementsScheduleDocument):
            self.items = copy.deepcopy(doc.items)
        else:
            self.items = copy.deepcopy(doc)
        self._block_signals = True
        try:
            self._load_items_to_table(self.items)
        finally:
            self._block_signals = False
        self._sync_and_emit()

    def get_items(self) -> List[ScheduleItem]:
        return self.items
