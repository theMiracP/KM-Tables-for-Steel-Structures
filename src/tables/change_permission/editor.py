"""
ГОСТ Р 21.101-2020 Form 9 'Разрешение на внесение изменений' Veri Giriş Editörü.
Kullanıcının izin bilgilerini, inşaat nesnesi adını, sorumlu mühendisleri ve değişiklik kayıtlarını
(Excel uyumlu kopyala-yapıştır, klavye gezintisi ve seçilebilir ГОСТ Tablo Л.1 neden kodlarıyla)
yönetmesini sağlayan modern Notion/Linear tarzı arayüz.
"""
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel, QAbstractItemView, QFrame,
    QLineEdit, QTextEdit, QScrollArea, QMenu, QMessageBox, QComboBox
)

from src.tables.change_permission.model import (
    ChangePermissionDocument, ChangePermissionItem, ChangeSignatoryEntry,
    build_default_change_signatories, build_empty_change_signatories
)
from src.tables.change_permission.config import REASON_CODES
from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import LinearComboBox, SolidItemDelegate
from src.ui.i18n import i18n


class ChangePermissionTableWidget(QTableWidget):
    """Excel tarzı klavye kısayollarını (Enter -> Alt hücre, Tab -> Yan hücre, Delete) destekleyen grid."""
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
        act_add_row = menu.addAction("＋ Değişiklik Satırı Ekle")
        act_del = menu.addAction("🗑️ Satır Sil")
        menu.addSeparator()
        act_up = menu.addAction("▲ Yukarı Taşı")
        act_down = menu.addAction("▼ Aşağı Taşı")

        action = menu.exec(event.globalPos())
        parent_widget = self.parent()
        while parent_widget and not hasattr(parent_widget, "_copy_to_clipboard"):
            parent_widget = parent_widget.parent()

        if parent_widget:
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


class ChangePermissionEditorWidget(QWidget):
    """
    ГОСТ Р 21.101-2020 Form 9 Editör Bileşeni.
    """
    document_changed = Signal(object)  # ChangePermissionDocument

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._doc = ChangePermissionDocument.get_default_sample_document()
        self._block_sync = False

        self._build_ui()
        self.set_document(self._doc)

        i18n.language_changed.connect(self._update_translations)

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(16, 12, 16, 16)
        self.container_layout.setSpacing(14)

        # 1. ÜST ARAÇ ÇUBUĞU & FORM 9 ROZETİ
        self._build_top_bar()

        # 2. DOKÜMAN BAŞLIK KARTI (Разрешение, Обозначение, Объект, Организация, Листы)
        self._build_header_card()

        # 3. SORUMLU İMZA KARTI (Изм. внес, Составил, ГИП, Утв.)
        self._build_signatories_card()

        # 4. DEĞİŞİKLİK TABLOSU VE ARAÇ ÇUBUĞU (İzm, Лист, Содержание, Код, Примечание)
        self._build_table_section()

        # 5. GOST TABLO Л.1 NEDEN KODLARI KARTI (Hızlı Seçici & Referans)
        self._build_reason_codes_card()

        # 6. BİLGİLENDİRME / STANDART NOTU
        self._build_info_card()

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

    # -------------------------------------------------------------------------
    # 1. ÜST ARAÇ ÇUBUĞU
    # -------------------------------------------------------------------------
    def _build_top_bar(self):
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        lbl_badge = QLabel("ГОСТ Р 21.101-2020 • Форма 9 (Разрешение на внесение изменений)")
        lbl_badge.setStyleSheet(f"""
            background-color: {theme.BG_SURFACE_ACTIVE};
            color: {theme.ACCENT_TEXT};
            font-size: 11px;
            font-weight: 600;
            padding: 5px 12px;
            border-radius: 4px;
            border: 1px solid {theme.BORDER_LIGHT};
        """)
        layout.addWidget(lbl_badge)

        layout.addStretch(1)

        self.btn_load_sample = QPushButton(i18n.t("preset_btn_sample"))
        self.btn_load_sample.setToolTip(i18n.t("tooltip_sample_form9"))
        self.btn_load_sample.setFixedHeight(28)
        self.btn_load_sample.setStyleSheet(self._btn_secondary_style())
        self.btn_load_sample.clicked.connect(self._load_sample_template)
        layout.addWidget(self.btn_load_sample)

        self.btn_clear_all = QPushButton(f"🧹 {i18n.t('btn_clear')}")
        self.btn_clear_all.setToolTip(i18n.t("tooltip_clear_form9"))
        self.btn_clear_all.setFixedHeight(28)
        self.btn_clear_all.setStyleSheet(self._btn_secondary_style())
        self.btn_clear_all.clicked.connect(self._clear_all_fields)
        layout.addWidget(self.btn_clear_all)

        self.container_layout.addWidget(bar)

    # -------------------------------------------------------------------------
    # 2. DOKÜMAN BAŞLIK KARTI
    # -------------------------------------------------------------------------
    def _build_header_card(self):
        card = QFrame()
        card.setObjectName("headerCard")
        card.setStyleSheet(self._card_style())
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        # Kart Başlığı
        lbl_card_title = QLabel("📄 DOKÜMAN VE PROJE BİLGİLERİ (ВЕРХНИЙ БЛОК)")
        lbl_card_title.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_MUTED}; letter-spacing: 0.5px;")
        layout.addWidget(lbl_card_title)

        # Satır 1: Разрешение №, Обозначение, Лист, Листов
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        # Разрешение №
        col_res = QVBoxLayout()
        col_res.setSpacing(3)
        self.lbl_res_num = QLabel("Разрешение № (İzin No):")
        self.lbl_res_num.setStyleSheet(self._field_label_style())
        self.txt_res_num = QLineEdit()
        self.txt_res_num.setPlaceholderText("örn: 008/26")
        self.txt_res_num.setStyleSheet(self._input_style())
        self.txt_res_num.textChanged.connect(self._sync_and_emit)
        col_res.addWidget(self.lbl_res_num)
        col_res.addWidget(self.txt_res_num)
        row1.addLayout(col_res, 1)

        # Обозначение документа
        col_doc = QVBoxLayout()
        col_doc.setSpacing(3)
        self.lbl_doc_code = QLabel("Обозначение документа (Doküman Kodu):")
        self.lbl_doc_code.setStyleSheet(self._field_label_style())
        self.txt_doc_code = QLineEdit()
        self.txt_doc_code.setPlaceholderText("örn: РД-2026-Ф1-КМ1-02")
        self.txt_doc_code.setStyleSheet(self._input_style())
        self.txt_doc_code.textChanged.connect(self._sync_and_emit)
        col_doc.addWidget(self.lbl_doc_code)
        col_doc.addWidget(self.txt_doc_code)
        row1.addLayout(col_doc, 2)

        # Лист
        col_sheet = QVBoxLayout()
        col_sheet.setSpacing(3)
        self.lbl_sheet_num = QLabel("Лист (Pafta):")
        self.lbl_sheet_num.setStyleSheet(self._field_label_style())
        self.txt_sheet_num = QLineEdit()
        self.txt_sheet_num.setFixedWidth(65)
        self.txt_sheet_num.setStyleSheet(self._input_style())
        self.txt_sheet_num.textChanged.connect(self._sync_and_emit)
        col_sheet.addWidget(self.lbl_sheet_num)
        col_sheet.addWidget(self.txt_sheet_num)
        row1.addLayout(col_sheet)

        # Листов
        col_sheets = QVBoxLayout()
        col_sheets.setSpacing(3)
        self.lbl_sheet_count = QLabel("Листов (Toplam):")
        self.lbl_sheet_count.setStyleSheet(self._field_label_style())
        self.txt_sheet_count = QLineEdit()
        self.txt_sheet_count.setFixedWidth(65)
        self.txt_sheet_count.setStyleSheet(self._input_style())
        self.txt_sheet_count.textChanged.connect(self._sync_and_emit)
        col_sheets.addWidget(self.lbl_sheet_count)
        col_sheets.addWidget(self.txt_sheet_count)
        row1.addLayout(col_sheets)

        layout.addLayout(row1)

        # Satır 2: Наименование объекта строительства
        col_obj = QVBoxLayout()
        col_obj.setSpacing(3)
        self.lbl_obj_name = QLabel("Наименование объекта строительства (İnşaat / Tesis Adı):")
        self.lbl_obj_name.setStyleSheet(self._field_label_style())
        self.txt_obj_name = QTextEdit()
        self.txt_obj_name.setFixedHeight(54)
        self.txt_obj_name.setPlaceholderText("Proje nesnesi, şantiye adı ve tam adresi...")
        self.txt_obj_name.setStyleSheet(self._input_style())
        self.txt_obj_name.textChanged.connect(self._sync_and_emit)
        col_obj.addWidget(self.lbl_obj_name)
        col_obj.addWidget(self.txt_obj_name)
        layout.addLayout(col_obj)

        # Satır 3: Организация
        col_comp = QVBoxLayout()
        col_comp.setSpacing(3)
        self.lbl_comp_name = QLabel("Организация (Tasarım Kuruluşu / Şirket Adı):")
        self.lbl_comp_name.setStyleSheet(self._field_label_style())
        self.txt_comp_name = QLineEdit()
        self.txt_comp_name.setPlaceholderText("örn: ООО «ПРОЕКТ-СТРОЙ»")
        self.txt_comp_name.setStyleSheet(self._input_style())
        self.txt_comp_name.textChanged.connect(self._sync_and_emit)
        col_comp.addWidget(self.lbl_comp_name)
        col_comp.addWidget(self.txt_comp_name)
        layout.addLayout(col_comp)

        self.container_layout.addWidget(card)

    # -------------------------------------------------------------------------
    # 3. SORUMLU İMZA KARTI
    # -------------------------------------------------------------------------
    def _build_signatories_card(self):
        card = QFrame()
        card.setObjectName("sigCard")
        card.setStyleSheet(self._card_style())
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        lbl_card_title = QLabel("✍️ SORUMLU VE ONAY MAKAMI İMZALARI (ПОДПИСИ)")
        lbl_card_title.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_MUTED}; letter-spacing: 0.5px;")
        layout.addWidget(lbl_card_title)

        self.sig_rows = []
        role_keys = ["perm_role_chg", "perm_role_prep", "perm_role_gip", "perm_role_appr"]

        for idx, key in enumerate(role_keys):
            row_box = QHBoxLayout()
            row_box.setSpacing(8)

            lbl_role = QLabel(i18n.t(key))
            lbl_role.setFixedWidth(175)
            lbl_role.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
            row_box.addWidget(lbl_role)

            txt_surname = QLineEdit()
            txt_surname.setPlaceholderText(i18n.t("ph_surname"))
            txt_surname.setStyleSheet(self._input_style())
            txt_surname.textChanged.connect(self._sync_and_emit)
            row_box.addWidget(txt_surname, 2)

            txt_sig = QLineEdit("✓")
            txt_sig.setFixedWidth(40)
            txt_sig.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt_sig.setStyleSheet(self._input_style())
            txt_sig.textChanged.connect(self._sync_and_emit)
            row_box.addWidget(txt_sig)

            txt_date = QLineEdit()
            txt_date.setFixedWidth(85)
            txt_date.setPlaceholderText(i18n.t("ph_date"))
            txt_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt_date.setStyleSheet(self._input_style())
            txt_date.textChanged.connect(self._sync_and_emit)
            row_box.addWidget(txt_date)

            layout.addLayout(row_box)
            self.sig_rows.append((lbl_role, txt_surname, txt_sig, txt_date))

        self.container_layout.addWidget(card)

    # -------------------------------------------------------------------------
    # 4. DEĞİŞİKLİK TABLOSU
    # -------------------------------------------------------------------------
    def _build_table_section(self):
        sec = QWidget()
        layout = QVBoxLayout(sec)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Tablo Üst Araç Çubuğu
        tb_bar = QHBoxLayout()
        tb_bar.setSpacing(8)

        lbl_sec_title = QLabel("📝 DEĞİŞİKLİK KAYITLARI (СОДЕРЖАНИЕ ИЗМЕНЕНИЙ)")
        lbl_sec_title.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_MUTED}; letter-spacing: 0.5px;")
        tb_bar.addWidget(lbl_sec_title)

        tb_bar.addStretch(1)

        self.btn_add_row = QPushButton(i18n.t("btn_add_change"))
        self.btn_add_row.setStyleSheet(self._btn_primary_style())
        self.btn_add_row.clicked.connect(self._add_row)
        tb_bar.addWidget(self.btn_add_row)

        self.btn_del_row = QPushButton(f"🗑️ {i18n.t('btn_delete_row')}")
        self.btn_del_row.setStyleSheet(self._btn_secondary_style())
        self.btn_del_row.clicked.connect(self._delete_selected_row)
        tb_bar.addWidget(self.btn_del_row)

        self.btn_up = QPushButton("▲")
        self.btn_up.setFixedWidth(28)
        self.btn_up.setStyleSheet(self._btn_secondary_style())
        self.btn_up.clicked.connect(lambda: self._move_row(-1))
        tb_bar.addWidget(self.btn_up)

        self.btn_down = QPushButton("▼")
        self.btn_down.setFixedWidth(28)
        self.btn_down.setStyleSheet(self._btn_secondary_style())
        self.btn_down.clicked.connect(lambda: self._move_row(1))
        tb_bar.addWidget(self.btn_down)

        layout.addLayout(tb_bar)

        # Tablo Grid
        self.table_widget = ChangePermissionTableWidget(self)
        self.table_widget.setItemDelegate(SolidItemDelegate(self.table_widget, font_size=11))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels([
            "Изм.\n(Rev)",
            "Лист\n(Pafta)",
            "Содержание изменения\n(Değişiklik İçeriği Açıklaması)",
            "Код\n(Neden Kodu)",
            "Примечание\n(Not)"
        ])
        header = self.table_widget.horizontalHeader()
        header.setFixedHeight(38)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table_widget.setColumnWidth(0, 65)
        self.table_widget.setColumnWidth(1, 75)
        self.table_widget.setColumnWidth(3, 210)  # Neden kodu açılır menüsü için ferah alan
        self.table_widget.setColumnWidth(4, 120)

        self.table_widget.verticalHeader().setDefaultSectionSize(34)
        self.table_widget.setStyleSheet(self._table_style())
        self.table_widget.itemChanged.connect(self._on_table_item_changed)
        layout.addWidget(self.table_widget)

        self.container_layout.addWidget(sec)

    # -------------------------------------------------------------------------
    # 5. GOST TABLO Л.1 NEDEN KODLARI KARTI (Image 1 Entegrasyonu)
    # -------------------------------------------------------------------------
    def _build_reason_codes_card(self):
        card = QFrame()
        card.setObjectName("codesCard")
        card.setStyleSheet(f"""
            QFrame#codesCard {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # Kart Başlığı
        header_row = QHBoxLayout()
        lbl_title = QLabel("📌 ГОСТ Р 21.101-2020 Таблица Л.1 — Коды причин изменения документа")
        lbl_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {theme.ACCENT_TEXT};")
        header_row.addWidget(lbl_title)
        header_row.addStretch(1)

        lbl_quick_hint = QLabel("Seçili Satıra Ata:")
        lbl_quick_hint.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px;")
        header_row.addWidget(lbl_quick_hint)

        # Hızlı kod atama butonları [1] [2] [3] [4] [5] [—]
        for code_str in ["1", "2", "3", "4", "5", "—"]:
            val_to_apply = "" if code_str == "—" else code_str
            btn_quick = QPushButton(code_str)
            btn_quick.setFixedSize(28, 24)
            btn_quick.setCursor(Qt.CursorShape.PointingHandCursor)
            tip = "Seçili satırın kodunu temizle (—)" if code_str == "—" else f"Seçili satıra Kod {code_str} ata"
            btn_quick.setToolTip(tip)
            btn_quick.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.BG_SURFACE_ACTIVE};
                    color: #FFFFFF;
                    border: 1px solid {theme.BORDER_LIGHT};
                    border-radius: 4px;
                    padding: 0px;
                    font-size: 11px;
                    font-weight: 700;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {theme.ACCENT_PRIMARY};
                    border-color: {theme.ACCENT_PRIMARY};
                    color: #FFFFFF;
                }}
            """)
            btn_quick.clicked.connect(lambda _, c=val_to_apply: self._apply_code_to_selected_row(c))
            header_row.addWidget(btn_quick)

        layout.addLayout(header_row)

        # Açıklama Satırları (Image 1 tablosu birebir)
        grid_desc = QVBoxLayout()
        grid_desc.setSpacing(3)
        code_descriptions = [
            ("1", "Введение усовершенствований", "İyileştirmelerin uygulanması", "Implementation of improvements"),
            ("2", "Изменение стандартов и норм", "Standart ve yönetmeliklerdeki değişiklikler", "Changes in standards and regulations"),
            ("3", "Дополнительные требования заказчика", "Ek müşteri gereksinimleri", "Additional customer requirements"),
            ("4", "Устранение ошибок", "Hataların giderilmesi", "Correction of mistakes"),
            ("5", "Другие причины", "Diğer nedenler", "Other reasons"),
        ]
        for c_num, ru_desc, tr_desc, en_desc in code_descriptions:
            lbl_line = QLabel(f"• <b>Код {c_num}:</b> {ru_desc} — <i>{tr_desc} ({en_desc})</i>")
            lbl_line.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px;")
            grid_desc.addWidget(lbl_line)
        layout.addLayout(grid_desc)

        self.container_layout.addWidget(card)

    # -------------------------------------------------------------------------
    # 6. BİLGİLENDİRME NOTU
    # -------------------------------------------------------------------------
    def _build_info_card(self):
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(info_frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        self.lbl_info_title = QLabel("💡 ГОСТ Р 21.101-2020 Приложение Л — Разрешение на внесение изменений (Форма 9)")
        self.lbl_info_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {theme.ACCENT_TEXT};")
        layout.addWidget(self.lbl_info_title)

        self.lbl_info_desc = QLabel(
            "• Form 9, teknik çizimlerdeki revizyon izinlerini ve değişiklik kayıtlarını standartlaştıran A4 dikey (210 × 297 mm) resmi belgedir.\n"
            "• Toplam genişlik 185 mm olup pafta iç çerçevesiyle (20 mm sol подшивка, 5 mm diğerleri) birebir örtüşür.\n"
            "• 'Код' sütunundan Tablo Л.1'e uygun değişiklik nedeni açılır menüden seçilebilir veya Excel'den yapıştırılabilir (Ctrl+V).\n"
            "• Klavye Kısayolları: Enter sonraki satıra geçer, Tab yan hücreye atlar, Delete seçili hücreleri temizler."
        )
        self.lbl_info_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px; line-height: 1.4;")
        self.lbl_info_desc.setWordWrap(True)
        layout.addWidget(self.lbl_info_desc)

        self.container_layout.addWidget(info_frame)

    # -------------------------------------------------------------------------
    # DOKÜMAN YÜKLEME VE SENKRONİZASYON
    # -------------------------------------------------------------------------
    def set_document(self, doc: ChangePermissionDocument):
        self._doc = doc
        self._block_sync = True

        # 1. Başlık alanlarını doldur
        self.txt_res_num.setText(doc.resolution_number)
        self.txt_doc_code.setText(doc.doc_code)
        self.txt_obj_name.setPlainText(doc.object_name)
        self.txt_comp_name.setText(doc.company_name)
        self.txt_sheet_num.setText(doc.sheet_num)
        self.txt_sheet_count.setText(doc.sheet_count)

        # 2. İmzaları doldur
        for idx, (_, txt_surname, txt_sig, txt_date) in enumerate(self.sig_rows):
            if idx < len(doc.signatories):
                s = doc.signatories[idx]
                txt_surname.setText(s.surname)
                txt_sig.setText(s.signature)
                txt_date.setText(s.date)
            else:
                txt_surname.setText("")
                txt_sig.setText("✓")
                txt_date.setText("")

        # 3. Tabloyu doldur
        self._load_items_to_table(doc.items)

        self._block_sync = False

    def get_document(self) -> ChangePermissionDocument:
        return self._build_document_from_ui()

    def _load_items_to_table(self, items: List[ChangePermissionItem]):
        self.table_widget.blockSignals(True)
        self.table_widget.setRowCount(len(items))

        for row_idx, item in enumerate(items):
            # 0: Изм.
            it_rev = QTableWidgetItem(item.rev_num)
            it_rev.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row_idx, 0, it_rev)

            # 1: Лист
            it_sheet = QTableWidgetItem(item.sheet)
            it_sheet.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row_idx, 1, it_sheet)

            # 2: Содержание изменения
            it_content = QTableWidgetItem(item.content)
            it_content.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row_idx, 2, it_content)

            # 3: Код (Açılır Menü / ComboBox)
            cb_code = LinearComboBox(self.table_widget)
            cb_code.setFixedHeight(26)
            self._populate_code_combobox(cb_code, item.reason_code)
            cb_code.currentIndexChanged.connect(lambda _, r=row_idx: self._on_code_combo_changed(r))
            self.table_widget.setCellWidget(row_idx, 3, cb_code)

            # 4: Примечание
            it_note = QTableWidgetItem(item.note)
            it_note.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row_idx, 4, it_note)

        self.table_widget.blockSignals(False)

    def _on_code_combo_changed(self, row: int):
        if self._block_sync:
            return
        self._sync_and_emit()

    def _apply_code_to_selected_row(self, code_str: str):
        curr_row = self.table_widget.currentRow()
        if curr_row < 0:
            if self.table_widget.rowCount() > 0:
                curr_row = 0
            else:
                return
        cb = self.table_widget.cellWidget(curr_row, 3)
        if isinstance(cb, QComboBox):
            target_val = "" if code_str in ("-", "—") else code_str
            for idx in range(cb.count()):
                if cb.itemData(idx) == target_val:
                    cb.setCurrentIndex(idx)
                    break

    def _on_table_item_changed(self, item: QTableWidgetItem):
        if self._block_sync:
            return
        self._sync_and_emit()

    def _build_document_from_ui(self) -> ChangePermissionDocument:
        # İmzalar
        sigs: List[ChangeSignatoryEntry] = []
        standard_roles = ["Изм. внес", "Составил", "ГИП", "Утв."]
        for idx, (lbl_role, txt_surname, txt_sig, txt_date) in enumerate(self.sig_rows):
            role_key = standard_roles[idx] if idx < len(standard_roles) else "Изм. внес"
            sigs.append(ChangeSignatoryEntry(
                role=role_key,
                surname=txt_surname.text().strip(),
                signature=txt_sig.text().strip() or "✓",
                date=txt_date.text().strip()
            ))

        # Satırlar
        items: List[ChangePermissionItem] = []
        for r in range(self.table_widget.rowCount()):
            it_rev = self.table_widget.item(r, 0)
            it_sheet = self.table_widget.item(r, 1)
            it_content = self.table_widget.item(r, 2)
            cb_code = self.table_widget.cellWidget(r, 3)
            it_note = self.table_widget.item(r, 4)

            rev_val = it_rev.text().strip() if it_rev else "1"
            sheet_val = it_sheet.text().strip() if it_sheet else "1"
            content_val = it_content.text().strip() if it_content else ""
            code_val = cb_code.currentData() if isinstance(cb_code, QComboBox) else ""
            note_val = it_note.text().strip() if it_note else ""

            items.append(ChangePermissionItem(
                rev_num=rev_val,
                sheet=sheet_val,
                content=content_val,
                reason_code=code_val or "",
                note=note_val
            ))

        if not items:
            items = [ChangePermissionItem()]

        return ChangePermissionDocument(
            resolution_number=self.txt_res_num.text().strip(),
            doc_code=self.txt_doc_code.text().strip(),
            object_name=self.txt_obj_name.toPlainText().strip(),
            company_name=self.txt_comp_name.text().strip(),
            sheet_num=self.txt_sheet_num.text().strip() or "1",
            sheet_count=self.txt_sheet_count.text().strip() or "1",
            signatories=sigs,
            items=items
        )

    def _sync_and_emit(self):
        if self._block_sync:
            return
        self._doc = self._build_document_from_ui()
        self.document_changed.emit(self._doc)

    # -------------------------------------------------------------------------
    # TABLO İŞLEMLERİ (Satır Ekle, Sil, Taşı, Temizle, Excel)
    # -------------------------------------------------------------------------
    def _add_row(self):
        doc = self._build_document_from_ui()
        # Bir önceki satırın revizyon numarasını devral
        last_rev = doc.items[-1].rev_num if doc.items else "1"
        doc.items.append(ChangePermissionItem(rev_num=last_rev, sheet="", content="", reason_code="1", note=""))
        self.set_document(doc)
        self.table_widget.setCurrentCell(self.table_widget.rowCount() - 1, 2)
        self._sync_and_emit()

    def _delete_selected_row(self):
        r = self.table_widget.currentRow()
        if r < 0:
            return
        doc = self._build_document_from_ui()
        if len(doc.items) <= 1:
            # TASK-42 Kuralı: En az 1 boş satır korunur
            doc.items = [ChangePermissionItem(rev_num="1", sheet="", content="", reason_code="", note="")]
        else:
            doc.items.pop(r)
        self.set_document(doc)
        new_row = min(r, self.table_widget.rowCount() - 1)
        self.table_widget.setCurrentCell(new_row, 0)
        self._sync_and_emit()

    def _move_row(self, direction: int):
        r = self.table_widget.currentRow()
        if r < 0:
            return
        target = r + direction
        if target < 0 or target >= self.table_widget.rowCount():
            return
        doc = self._build_document_from_ui()
        doc.items[r], doc.items[target] = doc.items[target], doc.items[r]
        self.set_document(doc)
        self.table_widget.setCurrentCell(target, 0)
        self._sync_and_emit()

    def _clear_all_fields(self):
        empty_doc = ChangePermissionDocument.get_empty_document()
        self.set_document(empty_doc)
        self._sync_and_emit()

    def _load_sample_template(self):
        sample_doc = ChangePermissionDocument.get_default_sample_document()
        self.set_document(sample_doc)
        self._sync_and_emit()

    def _copy_to_clipboard(self):
        selected = self.table_widget.selectedRanges()
        if not selected:
            return
        lines = []
        for rng in selected:
            for r in range(rng.topRow(), rng.bottomRow() + 1):
                row_vals = []
                for c in range(rng.leftColumn(), rng.rightColumn() + 1):
                    if c == 3:
                        cb = self.table_widget.cellWidget(r, 3)
                        val = cb.currentData() if isinstance(cb, QComboBox) else ""
                    else:
                        it = self.table_widget.item(r, c)
                        val = it.text() if it else ""
                    row_vals.append(val)
                lines.append("\t".join(row_vals))
        clipboard = QGuiApplication.clipboard()
        clipboard.setText("\n".join(lines))

    def _paste_from_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text().strip()
        if not text:
            return
        lines = text.split("\n")
        start_row = self.table_widget.currentRow()
        if start_row < 0:
            start_row = 0

        doc = self._build_document_from_ui()
        for idx, line in enumerate(lines):
            cols = [c.strip() for c in line.split("\t")]
            if not any(cols):
                continue
            target_idx = start_row + idx
            item = ChangePermissionItem()
            if len(cols) >= 1:
                item.rev_num = cols[0]
            if len(cols) >= 2:
                item.sheet = cols[1]
            if len(cols) >= 3:
                item.content = cols[2]
            if len(cols) >= 4:
                # Kod parse et (1..5)
                raw_c = cols[3]
                c_clean = "".join(ch for ch in raw_c if ch.isdigit())
                item.reason_code = c_clean if c_clean in {"1", "2", "3", "4", "5"} else raw_c
            if len(cols) >= 5:
                item.note = cols[4]

            if target_idx < len(doc.items):
                doc.items[target_idx] = item
            else:
                doc.items.append(item)

        self.set_document(doc)
        self._sync_and_emit()

    @staticmethod
    def _format_reason_code_label(c_val: str, ru_t: str, tr_t: str, en_t: str, lang_code: str) -> str:
        lang = (lang_code or "").lower()
        if not c_val:
            if lang == "tr":
                return "- (Yok / Belirtilmemiş)"
            elif lang == "en":
                return "- (None / Unspecified)"
            return "- (Прочерк)"
        if lang == "tr":
            return f"{c_val} — {tr_t}"
        elif lang == "en":
            return f"{c_val} — {en_t}"
        else:
            return f"{c_val} — {ru_t}"

    def _populate_code_combobox(self, cb: QComboBox, current_val: str, lang_code: Optional[str] = None):
        cb.blockSignals(True)
        cb.clear()
        lang = ((lang_code or i18n.current_language) or "TR").lower()
        for c_val, ru_t, tr_t, en_t in REASON_CODES:
            label = self._format_reason_code_label(c_val, ru_t, tr_t, en_t, lang)
            cb.addItem(label, userData=c_val)

        # Seçimi koru
        matched = False
        target = str(current_val).strip() if current_val is not None else ""
        for c_idx in range(cb.count()):
            if cb.itemData(c_idx) == target:
                cb.setCurrentIndex(c_idx)
                matched = True
                break
        if not matched and cb.count() > 0:
            cb.setCurrentIndex(0)
        cb.blockSignals(False)

    def _update_translations(self, lang: Optional[str] = None):
        """Aktif dil değiştiğinde butonları, imza etiketlerini ve açılır menü metinlerini günceller."""
        # Üst araç çubuğu butonları
        if hasattr(self, "btn_load_sample"):
            self.btn_load_sample.setText(i18n.t("preset_btn_sample"))
            self.btn_load_sample.setToolTip(i18n.t("tooltip_sample_form9"))
        if hasattr(self, "btn_clear_all"):
            self.btn_clear_all.setText(f"🧹 {i18n.t('btn_clear')}")
            self.btn_clear_all.setToolTip(i18n.t("tooltip_clear_form9"))
        if hasattr(self, "btn_add_row"):
            self.btn_add_row.setText(i18n.t("btn_add_change"))
        if hasattr(self, "btn_del_row"):
            self.btn_del_row.setText(f"🗑️ {i18n.t('btn_delete_row')}")

        # Sorumlu imza kadrosu rolleri ve yer tutucuları (Dile göre dinamik güncelleme)
        role_keys = ["perm_role_chg", "perm_role_prep", "perm_role_gip", "perm_role_appr"]
        if hasattr(self, "sig_rows"):
            for idx, (lbl_role, txt_surname, txt_sig, txt_date) in enumerate(self.sig_rows):
                if idx < len(role_keys):
                    lbl_role.setText(i18n.t(role_keys[idx]))
                txt_surname.setPlaceholderText(i18n.t("ph_surname"))
                txt_date.setPlaceholderText(i18n.t("ph_date"))

        # ComboBox'lardaki dil metinlerini güncelle (Aktif dile duyarlı)
        for r in range(self.table_widget.rowCount()):
            cb = self.table_widget.cellWidget(r, 3)
            if isinstance(cb, QComboBox):
                curr_data = cb.currentData()
                self._populate_code_combobox(cb, curr_data, lang_code=lang)

    # -------------------------------------------------------------------------
    # STİL ŞABLONLARI
    # -------------------------------------------------------------------------
    def _card_style(self) -> str:
        return f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
            }}
        """

    def _input_style(self) -> str:
        return f"""
            QLineEdit, QTextEdit {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {theme.ACCENT_PRIMARY};
            }}
        """

    def _field_label_style(self) -> str:
        return f"color: {theme.TEXT_SECONDARY}; font-size: 11px; font-weight: 500;"

    def _btn_primary_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
                border: 1px solid {theme.ACCENT_PRIMARY};
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_HOVER};
            }}
        """

    def _btn_secondary_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                border-color: {theme.BORDER_LIGHT};
            }}
        """

    def _table_style(self) -> str:
        return f"""
            QTableWidget {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
                gridline-color: {theme.BORDER_SUBTLE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 600;
                border: none;
                border-right: 1px solid {theme.BORDER_SUBTLE};
                border-bottom: 1px solid {theme.BORDER_SUBTLE};
                padding: 4px;
            }}
            QTableWidget::item:selected {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: #ffffff;
            }}
        """
