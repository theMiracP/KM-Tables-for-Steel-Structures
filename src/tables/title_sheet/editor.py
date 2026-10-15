"""
ГОСТ Р 21.101-2020 Приложение Р и С (Форма 12) Başlık Sayfası Editörü (TitleSheetEditorWidget).
Linear/Notion koyu temalı SaaS arayüzü, canlı CAD senkronizasyonu ve doğrudan Word (.docx) aktarımı.
"""
import os
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QFrame, QFileDialog, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QComboBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QColor

from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import LinearButton, LinearComboBox, SolidItemDelegate
from src.ui.i18n import i18n
from src.tables.title_sheet.model import (
    TitleSheetDocument, TitleSheetSignatory, ApprovalBlock,
    build_default_title_sheet_signatories, build_empty_title_sheet_signatories
)
from src.export.docx_exporter import DocxExporter


class TitleSheetEditorWidget(QWidget):
    """
    ГОСТ Р 21.101-2020 Form 12 / Приложение С Başlık Sayfası (Титульный лист) Editörü.
    """
    document_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._doc = TitleSheetDocument.get_default_sample_document()
        self._is_updating = False

        self._setup_ui()
        self.set_document(self._doc)

        i18n.language_changed.connect(self._update_translations)

    # -------------------------------------------------------------------------
    # UI KURULUMU
    # -------------------------------------------------------------------------
    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Kaydırılabilir alan (Dar/kısa panellerde layout ezilmesini ve kartların üst üste binmesini kesinlikle önler)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(12, 10, 12, 12)
        self.main_layout.setSpacing(10)

        # 1. ÜST EYLEM ÇUBUĞU (Toolbar: Word Export, Örnek Şablon, Temizle)
        self._build_toolbar()

        # 2. KART 1: KURULUŞ BİLGİLERİ & LOGO (Поля 1 & 2)
        self._build_org_card()

        # 3. KART 2: ONAY GRİFİ (Поле 3)
        self._build_approval_card()

        # 4. KART 3: PROJE VE DOKÜMAN BİLGİLERİ (Поля 4, 5, 6, 7, 8, 12)
        self._build_project_card()

        # 5. KART 4: SORUMLU İMZACI KADROSU (Поля 9, 10, 11)
        self._build_signatories_card()

        self.main_layout.addStretch()

        self.scroll.setWidget(container)
        root_layout.addWidget(self.scroll)

    def _build_toolbar(self):
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_CARD};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 4px;
            }}
        """)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(8)

        # Word'e Aktar Butonu (Belirgin Mavi/Vurgulu Buton)
        self.btn_export_word = QPushButton("📄 Word'e Aktar (.docx)")
        self.btn_export_word.setFixedHeight(30)
        self.btn_export_word.setCursor(Qt.PointingHandCursor)
        self.btn_export_word.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 12px;
                border: none;
                border-radius: 4px;
                padding: 4px 14px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)
        self.btn_export_word.clicked.connect(self._export_to_word)
        lay.addWidget(self.btn_export_word)

        lay.addStretch()

        # Örnek Şablon Butonu
        self.btn_sample = LinearButton(i18n.t("preset_btn_sample"), variant="secondary")
        self.btn_sample.setFixedHeight(30)
        self.btn_sample.clicked.connect(self._load_sample_template)
        lay.addWidget(self.btn_sample)

        # Temizle Butonu
        self.btn_clear = LinearButton(f"🧹 {i18n.t('clear_table')}", variant="danger")
        self.btn_clear.setFixedHeight(30)
        self.btn_clear.clicked.connect(lambda: self._clear_all_fields(prompt=True))
        lay.addWidget(self.btn_clear)

        self.main_layout.addWidget(bar)

    def _build_org_card(self):
        card = QFrame()
        card.setStyleSheet(self._card_style())
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)

        lbl = QLabel("1. KURULUŞ BİLGİLERİ VE LOGO (Организация и Логотип / Поля 1, 2)")
        lbl.setStyleSheet(self._card_header_style())
        lay.addWidget(lbl)

        # Üst Kuruluş Adı (Поле 1)
        r0 = QHBoxLayout()
        r0.setSpacing(6)
        lbl_high = QLabel("Вышестоящая орг. (Üst Kuruluş):")
        lbl_high.setFixedWidth(180)
        lbl_high.setStyleSheet(self._field_label_style())
        self.txt_higher_org = QLineEdit()
        self.txt_higher_org.setPlaceholderText("İsteğe bağlı üst bakanlık / birlik / kamu idaresi...")
        self.txt_higher_org.setStyleSheet(self._input_style())
        self.txt_higher_org.textChanged.connect(self._sync_and_emit)
        r0.addWidget(lbl_high)
        r0.addWidget(self.txt_higher_org)
        lay.addLayout(r0)

        # Tasarım Kuruluşu / Firma Adı (Поле 2)
        r1 = QHBoxLayout()
        r1.setSpacing(6)
        lbl_org = QLabel("Организация (Firma Adı):")
        lbl_org.setFixedWidth(180)
        lbl_org.setStyleSheet(self._field_label_style())
        self.txt_org_name = QLineEdit()
        self.txt_org_name.setPlaceholderText("örn: ООО «ПРОЕКТ-СТРОЙ»")
        self.txt_org_name.setStyleSheet(self._input_style())
        self.txt_org_name.textChanged.connect(self._sync_and_emit)
        r1.addWidget(lbl_org)
        r1.addWidget(self.txt_org_name)
        lay.addLayout(r1)

        # Logo Satırı
        r2 = QHBoxLayout()
        r2.setSpacing(8)
        self.chk_logo = QCheckBox("Kurumsal Logo Ekle")
        self.chk_logo.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 11px; font-weight: 600;")
        self.chk_logo.toggled.connect(self._toggle_logo)
        r2.addWidget(self.chk_logo)

        self.btn_select_logo = LinearButton("Logo Seç...", variant="secondary")
        self.btn_select_logo.setFixedHeight(26)
        self.btn_select_logo.clicked.connect(self._select_logo_file)
        r2.addWidget(self.btn_select_logo)

        self.lbl_logo_path = QLabel("Logo seçilmedi")
        self.lbl_logo_path.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px;")
        r2.addWidget(self.lbl_logo_path, 1)

        self.btn_clear_logo = LinearButton("Kaldır", variant="danger")
        self.btn_clear_logo.setFixedHeight(26)
        self.btn_clear_logo.clicked.connect(self._clear_logo)
        r2.addWidget(self.btn_clear_logo)

        lay.addLayout(r2)
        self.main_layout.addWidget(card)

    def _build_approval_card(self):
        card = QFrame()
        card.setStyleSheet(self._card_style())
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)

        lbl = QLabel("2. ONAY GRİFİ (Гриф согласования / Поле 3)")
        lbl.setStyleSheet(self._card_header_style())
        lay.addWidget(lbl)

        r0 = QHBoxLayout()
        r0.setSpacing(8)
        self.chk_has_approval = QCheckBox("Onay Grifini Göster (СОГЛАСОВАНО / УТВЕРЖДАЮ)")
        self.chk_has_approval.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 11px; font-weight: 600;")
        self.chk_has_approval.toggled.connect(self._sync_and_emit)
        r0.addWidget(self.chk_has_approval)

        self.cmb_app_title = LinearComboBox()
        self.cmb_app_title.setMinimumWidth(280)
        self._populate_approval_combos()
        self.cmb_app_title.currentIndexChanged.connect(self._sync_and_emit)
        r0.addWidget(self.cmb_app_title)
        r0.addStretch()
        lay.addLayout(r0)

        # Onay detay satırları: Unvan + Kuruluş + İsim + Tarih
        r1 = QHBoxLayout()
        r1.setSpacing(6)

        v_role = QVBoxLayout()
        v_role.setSpacing(2)
        lbl_ar = QLabel("Должность (Unvan):")
        lbl_ar.setStyleSheet(self._field_label_style())
        self.txt_app_role = QLineEdit()
        self.txt_app_role.setPlaceholderText("örn: Главный инженер проекта")
        self.txt_app_role.setStyleSheet(self._input_style())
        self.txt_app_role.textChanged.connect(self._sync_and_emit)
        v_role.addWidget(lbl_ar)
        v_role.addWidget(self.txt_app_role)
        r1.addLayout(v_role, 2)

        v_org = QVBoxLayout()
        v_org.setSpacing(2)
        lbl_ao = QLabel("Организация (Onay Kuruluşu):")
        lbl_ao.setStyleSheet(self._field_label_style())
        self.txt_app_org = QLineEdit()
        self.txt_app_org.setPlaceholderText("örn: (наименование организации-генпроектировщика)")
        self.txt_app_org.setStyleSheet(self._input_style())
        self.txt_app_org.textChanged.connect(self._sync_and_emit)
        v_org.addWidget(lbl_ao)
        v_org.addWidget(self.txt_app_org)
        r1.addLayout(v_org, 2)

        v_name = QVBoxLayout()
        v_name.setSpacing(2)
        lbl_an = QLabel("ФИО (Yetkili İsim):")
        lbl_an.setStyleSheet(self._field_label_style())
        self.txt_app_name = QLineEdit()
        self.txt_app_name.setPlaceholderText("örn: И.О. Фамилия")
        self.txt_app_name.setStyleSheet(self._input_style())
        self.txt_app_name.textChanged.connect(self._sync_and_emit)
        v_name.addWidget(lbl_an)
        v_name.addWidget(self.txt_app_name)
        r1.addLayout(v_name, 1)

        v_date = QVBoxLayout()
        v_date.setSpacing(2)
        lbl_ad = QLabel("Дата (Tarih):")
        lbl_ad.setStyleSheet(self._field_label_style())
        self.txt_app_date = QLineEdit()
        self.txt_app_date.setPlaceholderText("«___» _____ 2026 г.")
        self.txt_app_date.setStyleSheet(self._input_style())
        self.txt_app_date.textChanged.connect(self._sync_and_emit)
        v_date.addWidget(lbl_ad)
        v_date.addWidget(self.txt_app_date)
        r1.addLayout(v_date, 1)

        lay.addLayout(r1)
        self.main_layout.addWidget(card)

    def _build_project_card(self):
        card = QFrame()
        card.setStyleSheet(self._card_style())
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)

        lbl = QLabel("3. PROJE VE DOKÜMAN BAŞLIĞI (Объект и Наименование документа / Поля 4, 5, 6, 7, 8)")
        lbl.setStyleSheet(self._card_header_style())
        lay.addWidget(lbl)

        # İnşaat Nesnesi Adı (Поле 4, BÜYÜK HARFLERLE)
        lbl_obj = QLabel("Наименование объекта капитального строительства (İnşaat / Proje Adı — Büyük Harflerle):")
        lbl_obj.setStyleSheet(self._field_label_style())
        self.txt_object_name = QTextEdit()
        self.txt_object_name.setFixedHeight(56)
        self.txt_object_name.setPlaceholderText("PROJE NESNESİ, ŞANTİYE VE TAM ADRESİ...")
        self.txt_object_name.setStyleSheet(self._input_style())
        self.txt_object_name.textChanged.connect(self._sync_and_emit)
        lay.addWidget(lbl_obj)
        lay.addWidget(self.txt_object_name)

        # Doküman Türü (Поле 5)
        r_type = QHBoxLayout()
        r_type.setSpacing(6)
        lbl_type = QLabel("Вид документации (Doküman Türü):")
        lbl_type.setFixedWidth(200)
        lbl_type.setStyleSheet(self._field_label_style())
        self.cmb_doc_type = LinearComboBox()
        self._populate_doc_type_combos()
        self.cmb_doc_type.setFixedHeight(28)
        self.cmb_doc_type.currentIndexChanged.connect(self._sync_and_emit)
        r_type.addWidget(lbl_type)
        r_type.addWidget(self.cmb_doc_type, 1)
        lay.addLayout(r_type)

        # Doküman / Bölüm Başlığı (Поле 6)
        lbl_title = QLabel("Наименование документа (Bölüm, Alt Bölüm, Kısım veya Doküman Adı):")
        lbl_title.setStyleSheet(self._field_label_style())
        self.txt_doc_title = QTextEdit()
        self.txt_doc_title.setFixedHeight(68)
        self.txt_doc_title.setPlaceholderText("Раздел 5. Сведения об инженерном оборудовании...\nПодраздел 4...")
        self.txt_doc_title.setStyleSheet(self._input_style())
        self.txt_doc_title.textChanged.connect(self._sync_and_emit)
        lay.addWidget(lbl_title)
        lay.addWidget(self.txt_doc_title)

        # Belge Kodu + Cilt No + Yıl (Поля 7, 8, 12)
        r_code = QHBoxLayout()
        r_code.setSpacing(8)

        v_c = QVBoxLayout()
        v_c.setSpacing(2)
        lbl_c = QLabel("Обозначение (Belge Kodu):")
        lbl_c.setStyleSheet(self._field_label_style())
        self.txt_doc_code = QLineEdit()
        self.txt_doc_code.setFixedHeight(28)
        self.txt_doc_code.setPlaceholderText("örn: 2026-001-КМ")
        self.txt_doc_code.setStyleSheet(self._input_style())
        self.txt_doc_code.textChanged.connect(self._sync_and_emit)
        v_c.addWidget(lbl_c)
        v_c.addWidget(self.txt_doc_code)
        r_code.addLayout(v_c, 2)

        v_v = QVBoxLayout()
        v_v.setSpacing(2)
        lbl_v = QLabel("Номер тома (Cilt No):")
        lbl_v.setStyleSheet(self._field_label_style())
        self.txt_volume = QLineEdit()
        self.txt_volume.setFixedHeight(28)
        self.txt_volume.setPlaceholderText("örn: Том 1")
        self.txt_volume.setStyleSheet(self._input_style())
        self.txt_volume.textChanged.connect(self._sync_and_emit)
        v_v.addWidget(lbl_v)
        v_v.addWidget(self.txt_volume)
        r_code.addLayout(v_v, 1)

        v_y = QVBoxLayout()
        v_y.setSpacing(2)
        lbl_y = QLabel("Год (Yıl):")
        lbl_y.setStyleSheet(self._field_label_style())
        self.txt_year = QLineEdit()
        self.txt_year.setFixedHeight(28)
        self.txt_year.setPlaceholderText("örn: 2026")
        self.txt_year.setStyleSheet(self._input_style())
        self.txt_year.textChanged.connect(self._sync_and_emit)
        v_y.addWidget(lbl_y)
        v_y.addWidget(self.txt_year)
        r_code.addLayout(v_y, 1)

        lay.addLayout(r_code)
        self.main_layout.addWidget(card)

    def _build_signatories_card(self):
        card = QFrame()
        card.setStyleSheet(self._card_style())
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)

        hdr = QHBoxLayout()
        lbl = QLabel("4. SORUMLU İMZACI KADROSU (Подписи ответственных лиц / Поля 9, 10, 11)")
        lbl.setStyleSheet(self._card_header_style())
        hdr.addWidget(lbl)
        hdr.addStretch()

        # İmzacı Butonları
        self.btn_add_sig = LinearButton("＋ Yetkili Ekle", variant="primary")
        self.btn_add_sig.setFixedHeight(26)
        self.btn_add_sig.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 11px;
                border-radius: 4px;
                padding: 2px 10px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_add_sig.clicked.connect(self._add_signatory)
        hdr.addWidget(self.btn_add_sig)

        self.btn_del_sig = LinearButton("🗑 Sil", variant="danger")
        self.btn_del_sig.setFixedHeight(26)
        self.btn_del_sig.clicked.connect(self._delete_signatory)
        hdr.addWidget(self.btn_del_sig)

        self.btn_up_sig = QPushButton("▲")
        self.btn_up_sig.setFixedSize(28, 26)
        self.btn_up_sig.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_up_sig.setToolTip("Yukarı Taşı")
        self.btn_up_sig.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 11px;
                font-weight: 700;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                border-color: {theme.BORDER_FOCUS};
            }}
        """)
        self.btn_up_sig.clicked.connect(lambda: self._move_signatory(-1))
        hdr.addWidget(self.btn_up_sig)

        self.btn_down_sig = QPushButton("▼")
        self.btn_down_sig.setFixedSize(28, 26)
        self.btn_down_sig.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_down_sig.setToolTip("Aşağı Taşı")
        self.btn_down_sig.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 11px;
                font-weight: 700;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                border-color: {theme.BORDER_FOCUS};
            }}
        """)
        self.btn_down_sig.clicked.connect(lambda: self._move_signatory(1))
        hdr.addWidget(self.btn_down_sig)

        lay.addLayout(hdr)

        # Tablo: Unvan | İmza / Paraf | Ad Soyad
        self.table_sigs = QTableWidget()
        self.table_sigs.setItemDelegate(SolidItemDelegate(self.table_sigs, font_size=12))
        self.table_sigs.setColumnCount(3)
        self.table_sigs.setHorizontalHeaderLabels([
            "Должность\n(Görev / Unvan)",
            "Подпись / Дата\n(İmza / Durum)",
            "Фамилия И.О.\n(Adı Soyadı)"
        ])
        self.table_sigs.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_sigs.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_sigs.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_sigs.verticalHeader().setVisible(False)
        self.table_sigs.setMinimumHeight(140)
        self.table_sigs.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme.BG_SURFACE};
                gridline-color: {theme.BORDER_SUBTLE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {theme.BG_CARD};
                color: {theme.TEXT_SECONDARY};
                font-weight: 700;
                font-size: 11px;
                border: 1px solid {theme.BORDER_SUBTLE};
                padding: 4px;
            }}
        """)
        self.table_sigs.cellChanged.connect(self._on_table_cell_changed)
        lay.addWidget(self.table_sigs)

        self.main_layout.addWidget(card)

    # -------------------------------------------------------------------------
    # VERİ SENKRONİZASYONU
    # -------------------------------------------------------------------------
    def get_document(self) -> TitleSheetDocument:
        """Arayüzdeki güncel verileri TitleSheetDocument olarak döndürür."""
        sigs = []
        for r in range(self.table_sigs.rowCount()):
            role_item = self.table_sigs.item(r, 0)
            sig_item = self.table_sigs.item(r, 1)
            sur_item = self.table_sigs.item(r, 2)
            sigs.append(TitleSheetSignatory(
                role=role_item.text().strip() if role_item else "",
                signature=sig_item.text().strip() if sig_item else "✓",
                surname=sur_item.text().strip() if sur_item else ""
            ))

        app_title_val = self.cmb_app_title.currentData()
        if not app_title_val:
            app_title_val = self.cmb_app_title.currentText().split(" — ")[0].strip()

        app_block = ApprovalBlock(
            has_approval=self.chk_has_approval.isChecked(),
            approval_title=app_title_val or "СОГЛАСОВАНО",
            role=self.txt_app_role.text().strip(),
            organization=self.txt_app_org.text().strip(),
            name=self.txt_app_name.text().strip(),
            date=self.txt_app_date.text().strip()
        )

        doc_type_val = self.cmb_doc_type.currentData()
        if not doc_type_val:
            doc_type_val = self.cmb_doc_type.currentText().split(" — ")[0].strip()

        return TitleSheetDocument(
            higher_org=self.txt_higher_org.text().strip(),
            organization_name=self.txt_org_name.text().strip(),
            has_logo=self.chk_logo.isChecked(),
            logo_image_path=self._doc.logo_image_path,
            approval=app_block,
            object_name=self.txt_object_name.toPlainText().strip(),
            doc_type=doc_type_val or "ПРОЕКТНАЯ ДОКУМЕНТАЦИЯ",
            doc_title=self.txt_doc_title.toPlainText().strip(),
            doc_code=self.txt_doc_code.text().strip(),
            volume_number=self.txt_volume.text().strip(),
            signatories=sigs,
            year=self.txt_year.text().strip(),
            inv_num=self._doc.inv_num,
            inv_date=self._doc.inv_date,
            inv_repl=self._doc.inv_repl,
        )

    def set_document(self, document: TitleSheetDocument):
        """Model verilerini editör bileşenlerine yükler."""
        self._is_updating = True
        self._doc = document

        self.txt_higher_org.setText(document.higher_org)
        self.txt_org_name.setText(document.organization_name)
        self.chk_logo.setChecked(document.has_logo)
        if document.logo_image_path:
            self.lbl_logo_path.setText(os.path.basename(document.logo_image_path))
        else:
            self.lbl_logo_path.setText("Logo seçilmedi")

        # Onay
        app = document.approval
        self.chk_has_approval.setChecked(app.has_approval)
        idx = self.cmb_app_title.findData(app.approval_title)
        if idx < 0:
            for i in range(self.cmb_app_title.count()):
                d = self.cmb_app_title.itemData(i)
                t = self.cmb_app_title.itemText(i)
                if d == app.approval_title or t.startswith(app.approval_title):
                    idx = i
                    break
        if idx >= 0:
            self.cmb_app_title.setCurrentIndex(idx)
        elif app.approval_title:
            self.cmb_app_title.addItem(app.approval_title, app.approval_title)
            self.cmb_app_title.setCurrentIndex(self.cmb_app_title.count() - 1)

        self.txt_app_role.setText(app.role)
        self.txt_app_org.setText(app.organization)
        self.txt_app_name.setText(app.name)
        self.txt_app_date.setText(app.date)

        # Proje
        self.txt_object_name.setPlainText(document.object_name)
        idx_t = self.cmb_doc_type.findData(document.doc_type)
        if idx_t < 0:
            for i in range(self.cmb_doc_type.count()):
                d = self.cmb_doc_type.itemData(i)
                t = self.cmb_doc_type.itemText(i)
                if d == document.doc_type or t.startswith(document.doc_type):
                    idx_t = i
                    break
        if idx_t >= 0:
            self.cmb_doc_type.setCurrentIndex(idx_t)
        elif document.doc_type:
            self.cmb_doc_type.addItem(document.doc_type, document.doc_type)
            self.cmb_doc_type.setCurrentIndex(self.cmb_doc_type.count() - 1)

        self.txt_doc_title.setPlainText(document.doc_title)
        self.txt_doc_code.setText(document.doc_code)
        self.txt_volume.setText(document.volume_number)
        self.txt_year.setText(document.year)

        # İmzacı tablosu
        self._load_signatories_to_table(document.signatories)

        self._is_updating = False

    def _load_signatories_to_table(self, sigs: List[TitleSheetSignatory]):
        self.table_sigs.blockSignals(True)
        self.table_sigs.setRowCount(len(sigs))
        for r, s in enumerate(sigs):
            item_r = QTableWidgetItem(s.role)
            item_s = QTableWidgetItem(s.signature or "✓")
            item_n = QTableWidgetItem(s.surname)

            item_r.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_s.setTextAlignment(Qt.AlignCenter)
            item_n.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            self.table_sigs.setItem(r, 0, item_r)
            self.table_sigs.setItem(r, 1, item_s)
            self.table_sigs.setItem(r, 2, item_n)
            self.table_sigs.setRowHeight(r, 28)
        self.table_sigs.blockSignals(False)
        self._adjust_signatories_table_height()

    def _adjust_signatories_table_height(self):
        """İmzacı tablosunun yüksekliğini satır sayısına göre en az 140px, en fazla 280px olarak ayarlar."""
        header_h = self.table_sigs.horizontalHeader().height() or 34
        rows_h = self.table_sigs.rowCount() * 28
        total_h = max(140, min(header_h + rows_h + 8, 280))
        self.table_sigs.setFixedHeight(total_h)

    def _on_table_cell_changed(self, row: int, col: int):
        if not self._is_updating:
            self._sync_and_emit()

    def _sync_and_emit(self):
        if self._is_updating:
            return
        self._doc = self.get_document()
        self.document_changed.emit()

    # -------------------------------------------------------------------------
    # BUTON AKSİYONLARI
    # -------------------------------------------------------------------------
    def _export_to_word(self):
        """Mevcut başlık sayfasını Word (.docx) olarak kaydeder."""
        doc = self.get_document()
        safe_code = doc.doc_code.replace("/", "_").replace("\\", "_") or "Titul"
        default_name = f"Titulny_List_{safe_code}.docx"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Word (.docx) Olarak Kaydet",
            default_name,
            "Word Dokümanı (*.docx)"
        )
        if not file_path:
            return

        exporter = DocxExporter()
        ok = exporter.export_title_sheet(doc, file_path)
        if ok:
            ans = QMessageBox.information(
                self,
                "Dışa Aktarma Başarılı",
                f"Başlık sayfası başarıyla Word dokümanına aktarıldı:\n\n{file_path}\n\nDosyayı şimdi açmak ister misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            if ans == QMessageBox.Yes:
                try:
                    os.startfile(file_path)
                except Exception as e:
                    print(f"Dosya açılamadı: {e}")
        else:
            QMessageBox.critical(
                self,
                "Hata",
                "Word dosyası dışa aktarılırken bir hata oluştu."
            )

    def _load_sample_template(self):
        """Приложение С / Рисунок С.1 kurgusal jenerik örnek şablonunu yükler."""
        sample_doc = TitleSheetDocument.get_default_sample_document()
        self.set_document(sample_doc)
        self._sync_and_emit()

    def _clear_all_fields(self, prompt: bool = False):
        """Tüm alanları temizler (en az 1 sorumlu satırı korunur)."""
        if prompt:
            ans = QMessageBox.question(
                self,
                "Temizle",
                "Tüm başlık sayfası alanlarını temizlemek istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            if ans != QMessageBox.Yes:
                return

        empty_doc = TitleSheetDocument.get_empty_document()
        self.set_document(empty_doc)
        self._sync_and_emit()

    def _add_signatory(self):
        """Yeni sorumlu satırı ekler."""
        r = self.table_sigs.rowCount()
        self.table_sigs.insertRow(r)
        self.table_sigs.setItem(r, 0, QTableWidgetItem("Инженер"))
        self.table_sigs.setItem(r, 1, QTableWidgetItem("✓"))
        self.table_sigs.setItem(r, 2, QTableWidgetItem(""))
        self.table_sigs.setRowHeight(r, 28)
        self.table_sigs.setCurrentCell(r, 2)
        self._adjust_signatories_table_height()
        self._sync_and_emit()

    def _delete_signatory(self):
        """Seçili sorumlu satırını siler (en az 1 satır korunur)."""
        r = self.table_sigs.currentRow()
        if r < 0:
            r = self.table_sigs.rowCount() - 1
        if self.table_sigs.rowCount() <= 1:
            # Sıfıra indirme, içeriği temizle
            self.table_sigs.item(0, 0).setText("")
            self.table_sigs.item(0, 2).setText("")
            self._adjust_signatories_table_height()
            self._sync_and_emit()
            return
        self.table_sigs.removeRow(r)
        self._adjust_signatories_table_height()
        self._sync_and_emit()

    def _move_signatory(self, direction: int):
        """Seçili sorumlu satırını yukarı/aşağı taşır."""
        r = self.table_sigs.currentRow()
        target = r + direction
        if r < 0 or target < 0 or target >= self.table_sigs.rowCount():
            return

        role_a = self.table_sigs.item(r, 0).text()
        sig_a = self.table_sigs.item(r, 1).text()
        sur_a = self.table_sigs.item(r, 2).text()

        role_b = self.table_sigs.item(target, 0).text()
        sig_b = self.table_sigs.item(target, 1).text()
        sur_b = self.table_sigs.item(target, 2).text()

        self.table_sigs.item(r, 0).setText(role_b)
        self.table_sigs.item(r, 1).setText(sig_b)
        self.table_sigs.item(r, 2).setText(sur_b)

        self.table_sigs.item(target, 0).setText(role_a)
        self.table_sigs.item(target, 1).setText(sig_a)
        self.table_sigs.item(target, 2).setText(sur_a)

        self.table_sigs.setCurrentCell(target, 0)
        self._sync_and_emit()

    def _toggle_logo(self, checked: bool):
        self._doc.has_logo = checked
        self._sync_and_emit()

    def _select_logo_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Logo Resmi Seç",
            "",
            "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self._doc.logo_image_path = path
            self._doc.has_logo = True
            self.chk_logo.setChecked(True)
            self.lbl_logo_path.setText(os.path.basename(path))
            self._sync_and_emit()

    def _clear_logo(self):
        self._doc.logo_image_path = None
        self._doc.has_logo = False
        self.chk_logo.setChecked(False)
        self.lbl_logo_path.setText("Logo seçilmedi")
        self._sync_and_emit()

    # -------------------------------------------------------------------------
    # STİL YARDIMCILARI
    # -------------------------------------------------------------------------
    def _card_style(self) -> str:
        return f"""
            QFrame {{
                background-color: {theme.BG_CARD};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
            }}
        """

    def _card_header_style(self) -> str:
        return f"""
            font-size: 11px;
            font-weight: 700;
            color: {theme.TEXT_SECONDARY};
            letter-spacing: 0.5px;
        """

    def _field_label_style(self) -> str:
        return f"""
            font-size: 10px;
            font-weight: 600;
            color: {theme.TEXT_SECONDARY};
        """

    def _input_style(self) -> str:
        return f"""
            QLineEdit, QTextEdit {{
                background-color: {theme.BG_SURFACE};
                color: #FFFFFF;
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 600;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {theme.ACCENT_PRIMARY};
                background-color: {theme.BG_SURFACE_ACTIVE};
            }}
        """

    def _populate_approval_combos(self):
        """Onay grifi başlık seçeneklerini (СОГЛАСОВАНО / УТВЕРЖДАЮ) aktif dile göre doldurur."""
        curr_val = self.cmb_app_title.currentData() if hasattr(self, "cmb_app_title") and self.cmb_app_title.count() > 0 else "СОГЛАСОВАНО"
        self.cmb_app_title.blockSignals(True)
        self.cmb_app_title.clear()
        self.cmb_app_title.addItem(i18n.t("approval_soglasovano"), "СОГЛАСОВАНО")
        self.cmb_app_title.addItem(i18n.t("approval_utverzhdayu"), "УТВЕРЖДАЮ")
        idx = self.cmb_app_title.findData(curr_val)
        if idx >= 0:
            self.cmb_app_title.setCurrentIndex(idx)
        else:
            self.cmb_app_title.setCurrentIndex(0)
        self.cmb_app_title.blockSignals(False)

    def _populate_doc_type_combos(self):
        """Doküman türü seçeneklerini (ПРОЕКТНАЯ / РАБОЧАЯ) aktif dile göre doldurur."""
        curr_val = self.cmb_doc_type.currentData() if hasattr(self, "cmb_doc_type") and self.cmb_doc_type.count() > 0 else "ПРОЕКТНАЯ ДОКУМЕНТАЦИЯ"
        self.cmb_doc_type.blockSignals(True)
        self.cmb_doc_type.clear()
        self.cmb_doc_type.addItem(i18n.t("doc_type_project"), "ПРОЕКТНАЯ ДОКУМЕНТАЦИЯ")
        self.cmb_doc_type.addItem(i18n.t("doc_type_working"), "РАБОЧАЯ ДОКУМЕНТАЦИЯ")
        idx = self.cmb_doc_type.findData(curr_val)
        if idx >= 0:
            self.cmb_doc_type.setCurrentIndex(idx)
        else:
            self.cmb_doc_type.setCurrentIndex(0)
        self.cmb_doc_type.blockSignals(False)

    def _update_translations(self, lang: Optional[str] = None):
        """Aktif dil değiştiğinde buton metinlerini ve açılır menü etiketlerini dinamik günceller."""
        if hasattr(self, "btn_export_word"):
            self.btn_export_word.setText(i18n.t("btn_export_word"))
        if hasattr(self, "btn_sample"):
            self.btn_sample.setText(i18n.t("preset_btn_sample"))
        if hasattr(self, "btn_clear"):
            self.btn_clear.setText(f"🧹 {i18n.t('clear_table')}")

        if hasattr(self, "cmb_app_title"):
            curr_app = self.cmb_app_title.currentData() or self.cmb_app_title.currentText().split(" — ")[0].strip()
            self._populate_approval_combos()
            idx = self.cmb_app_title.findData(curr_app)
            if idx >= 0:
                self.cmb_app_title.setCurrentIndex(idx)

        if hasattr(self, "cmb_doc_type"):
            curr_type = self.cmb_doc_type.currentData() or self.cmb_doc_type.currentText().split(" — ")[0].strip()
            self._populate_doc_type_combos()
            idx_t = self.cmb_doc_type.findData(curr_type)
            if idx_t >= 0:
                self.cmb_doc_type.setCurrentIndex(idx_t)
