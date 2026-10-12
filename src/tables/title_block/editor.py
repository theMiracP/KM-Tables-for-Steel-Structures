"""
KM Tablo Oluşturucu - ГОСТ Р 21.101-2020 Form 3 Görsel Antet Editörü (TitleBlockEditorWidget).
Form 3'ün (185 x 55 mm) gerçek geometrisini, hücre bölünmelerini ve CAD çizim mantığını
birebir yansıtan interaktif WYSIWYG veri giriş formu.
"""
import os
from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPlainTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QScrollArea, QCheckBox, QPushButton, QFileDialog
)

from src.tables.title_block.model import (
    TitleBlockDocument, SignatoryEntry, RevisionEntry,
    build_default_signatories, build_empty_signatories, build_default_revisions
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2.components import SolidItemDelegate
from src.ui.i18n import i18n


class TitleBlockEditorWidget(QWidget):
    """
    ГОСТ Р 21.101-2020 Form 3 (185 x 55 mm) Görsel CAD Antet Editörü.
    Antetin fiziksel çizim kutucukları üzerinde doğrudan veri girişi sağlar.
    """
    document_changed = Signal(object)  # TitleBlockDocument

    def __init__(self, parent=None):
        super().__init__(parent)
        self._document: TitleBlockDocument = TitleBlockDocument()
        self._is_loading = False
        self._logo_image_path: Optional[str] = None

        self._build_ui()
        self._update_translations()
        i18n.language_changed.connect(self._update_translations)
        self.set_document(self._document)

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Kaydırılabilir alan (Dar panellerde layout bozulmasını önler)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        self.layout_content = QVBoxLayout(scroll_content)
        self.layout_content.setContentsMargins(14, 12, 14, 14)
        self.layout_content.setSpacing(12)

        # 1. ÜST ARAÇ ÇUBUĞU (Toolbar & Hızlı İşlemler)
        self.layout_content.addWidget(self._build_toolbar())

        # 2. GÖRSEL ANTET STAMPI (WYSIWYG Form 3 Çizim Kutusu)
        self.layout_content.addWidget(self._build_visual_title_block())

        # 3. ALT BİLGİLENDİRME ROZETİ
        self.layout_content.addWidget(self._build_footer_info())

        self.layout_content.addStretch(1)
        scroll.setWidget(scroll_content)
        root_layout.addWidget(scroll)

    # -------------------------------------------------------------------------
    # 1. ÜST ARAÇ ÇUBUĞU
    # -------------------------------------------------------------------------
    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Sol: Başlık ve Form 3 Rozeti
        lbl_badge = QLabel("ГОСТ Р 21.101-2020 • Форма 3 (185 × 55 мм)")
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

        # Sağ: Örnek Doldur ve Temizle Butonları
        self.btn_sample = QPushButton("📋 Örnek KM Doldur")
        self.btn_sample.setToolTip("Standart KM projesi antet verilerini örnek olarak yükler")
        self.btn_sample.setFixedHeight(28)
        self.btn_sample.setStyleSheet(f"""
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
                border-color: {theme.ACCENT_PRIMARY};
            }}
        """)
        self.btn_sample.clicked.connect(self.load_sample_km)
        layout.addWidget(self.btn_sample)

        self.btn_clear = QPushButton("🗑️ Temizle")
        self.btn_clear.setToolTip("Tüm antet alanlarını boşaltır")
        self.btn_clear.setFixedHeight(28)
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_MUTED};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_ERROR_BG};
                color: {theme.COLOR_ERROR};
                border-color: {theme.COLOR_ERROR_BORDER};
            }}
        """)
        self.btn_clear.clicked.connect(lambda: self.clear_all(prompt=True))
        layout.addWidget(self.btn_clear)

        return bar

    # -------------------------------------------------------------------------
    # 2. GÖRSEL ANTET STAMPI (Form 3 CAD Kutusu)
    # -------------------------------------------------------------------------
    def _build_visual_title_block(self) -> QFrame:
        stamp_frame = QFrame()
        stamp_frame.setObjectName("stampCard")
        stamp_frame.setMinimumWidth(720)
        stamp_frame.setStyleSheet(f"""
            QFrame#stampCard {{
                background-color: {theme.BG_SURFACE};
                border: 2px solid {theme.BORDER_LIGHT};
                border-radius: 6px;
            }}
        """)

        h_layout = QHBoxLayout(stamp_frame)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)

        # SOL BÖLGE (70 mm: Revizyonlar & İmzalar)
        left_zone = self._build_left_zone()
        h_layout.addWidget(left_zone, 38)

        # SAĞ BÖLGE (115 mm: Doküman Kodu, Proje, Yapı, Aşama, Çizim, Şirket)
        right_zone = self._build_right_zone()
        h_layout.addWidget(right_zone, 62)

        return stamp_frame

    # -------------------------------------------------------------------------
    # SOL BÖLGE: REVİZYONLAR & İMZALAR (70 mm)
    # -------------------------------------------------------------------------
    def _build_left_zone(self) -> QFrame:
        left_frame = QFrame()
        left_frame.setObjectName("leftZone")
        left_frame.setStyleSheet(f"""
            QFrame#leftZone {{
                background-color: {theme.BG_APP};
                border-right: 2px solid {theme.BORDER_LIGHT};
            }}
        """)

        v_layout = QVBoxLayout(left_frame)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)

        # Üst Kısım: Revizyon Tablosu (Таблица изменений)
        rev_box = QFrame()
        rev_box.setStyleSheet(f"border-bottom: 2px solid {theme.BORDER_LIGHT}; padding: 0px;")
        l_rev = QVBoxLayout(rev_box)
        l_rev.setContentsMargins(8, 8, 8, 8)
        l_rev.setSpacing(6)

        hdr_rev = QHBoxLayout()
        self.lbl_rev_t = QLabel(i18n.t("tb_title_changes"))
        self.lbl_rev_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        lbl_rev_g = QLabel("Графы 14..18")
        lbl_rev_g.setStyleSheet(f"font-size: 9px; color: {theme.TEXT_MUTED};")
        hdr_rev.addWidget(self.lbl_rev_t)
        hdr_rev.addStretch(1)
        hdr_rev.addWidget(lbl_rev_g)
        l_rev.addLayout(hdr_rev)

        self.tbl_revisions = QTableWidget(4, 6)
        self.tbl_revisions.setItemDelegate(SolidItemDelegate(self.tbl_revisions, font_size=12))
        self.tbl_revisions.setHorizontalHeaderLabels([
            i18n.t("tb_col_rev_num"), i18n.t("tb_col_rev_count"),
            i18n.t("tb_col_rev_sheet"), i18n.t("tb_col_rev_doc"),
            i18n.t("tb_col_sign"), i18n.t("tb_col_date")
        ])
        self.tbl_revisions.verticalHeader().setVisible(False)
        self.tbl_revisions.setFixedHeight(152)
        self._style_table(self.tbl_revisions)

        hr = self.tbl_revisions.horizontalHeader()
        hr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hr.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hr.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        hr.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.tbl_revisions.setColumnWidth(0, 42)
        self.tbl_revisions.setColumnWidth(1, 48)
        self.tbl_revisions.setColumnWidth(2, 42)
        self.tbl_revisions.setColumnWidth(4, 52)
        self.tbl_revisions.setColumnWidth(5, 62)

        for r in range(4):
            self.tbl_revisions.setRowHeight(r, 29)

        self.tbl_revisions.cellChanged.connect(self._on_table_edited)
        l_rev.addWidget(self.tbl_revisions)
        v_layout.addWidget(rev_box)

        # Alt Kısım: Sorumlu Mühendisler ve İmzalar (Разработчики и подписи)
        sig_box = QFrame()
        l_sig = QVBoxLayout(sig_box)
        l_sig.setContentsMargins(8, 8, 8, 8)
        l_sig.setSpacing(6)

        hdr_sig = QHBoxLayout()
        self.lbl_sig_t = QLabel(i18n.t("tb_title_signatories"))
        self.lbl_sig_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        lbl_sig_g = QLabel("Графы 10..13")
        lbl_sig_g.setStyleSheet(f"font-size: 9px; color: {theme.TEXT_MUTED};")
        hdr_sig.addWidget(self.lbl_sig_t)
        hdr_sig.addStretch(1)
        hdr_sig.addWidget(lbl_sig_g)
        l_sig.addLayout(hdr_sig)

        self.tbl_signatories = QTableWidget(6, 4)
        self.tbl_signatories.setItemDelegate(SolidItemDelegate(self.tbl_signatories, font_size=12))
        self.tbl_signatories.setHorizontalHeaderLabels([
            i18n.t("tb_col_role"), i18n.t("tb_col_name"),
            i18n.t("tb_col_sign"), i18n.t("tb_col_date")
        ])
        self.tbl_signatories.verticalHeader().setVisible(False)
        self.tbl_signatories.setFixedHeight(225)
        self._style_table(self.tbl_signatories)

        hs = self.tbl_signatories.horizontalHeader()
        hs.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hs.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hs.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hs.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tbl_signatories.setColumnWidth(0, 90)
        self.tbl_signatories.setColumnWidth(2, 54)
        self.tbl_signatories.setColumnWidth(3, 75)

        for r in range(6):
            self.tbl_signatories.setRowHeight(r, 32)

        self.tbl_signatories.cellChanged.connect(self._on_table_edited)
        l_sig.addWidget(self.tbl_signatories)
        v_layout.addWidget(sig_box)

        return left_frame

    # -------------------------------------------------------------------------
    # SAĞ BÖLGE: DOKÜMAN, PROJE, YAPI, AŞAMA, ÇİZİM, ŞİRKET (115 mm)
    # -------------------------------------------------------------------------
    def _build_right_zone(self) -> QFrame:
        right_frame = QFrame()
        right_frame.setStyleSheet(f"background-color: {theme.BG_APP};")
        v_layout = QVBoxLayout(right_frame)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)

        # 1. SATIR: DOKÜMAN KODU (Графа 1 - 115 x 15 mm)
        box_code = QFrame()
        box_code.setStyleSheet(f"border-bottom: 2px solid {theme.BORDER_LIGHT}; padding: 0px;")
        l_code = QVBoxLayout(box_code)
        l_code.setContentsMargins(10, 8, 10, 8)
        l_code.setSpacing(4)

        hdr_code = QHBoxLayout()
        self.lbl_code_t = QLabel(i18n.t("tb_field_doc_code"))
        self.lbl_code_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        lbl_code_g = QLabel("115 × 15 mm")
        lbl_code_g.setStyleSheet(f"font-size: 9px; color: {theme.TEXT_MUTED};")
        hdr_code.addWidget(self.lbl_code_t)
        hdr_code.addStretch(1)
        hdr_code.addWidget(lbl_code_g)
        l_code.addLayout(hdr_code)

        self.txt_doc_code = QLineEdit()
        self.txt_doc_code.setPlaceholderText("Örn: 2026-001-КМ")
        self.txt_doc_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_doc_code.setFixedHeight(38)
        self.txt_doc_code.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BG_SURFACE};
                color: #ffffff;
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 0.8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.ACCENT_PRIMARY};
                background-color: {theme.BG_SURFACE_ACTIVE};
            }}
        """)
        self.txt_doc_code.textChanged.connect(self._on_field_edited)
        l_code.addWidget(self.txt_doc_code)
        v_layout.addWidget(box_code)

        # 2. SATIR: PROJE / TESİS ADI (Графа 2 - 115 x 15 mm)
        box_proj = QFrame()
        box_proj.setStyleSheet(f"border-bottom: 2px solid {theme.BORDER_LIGHT}; padding: 0px;")
        l_proj = QVBoxLayout(box_proj)
        l_proj.setContentsMargins(10, 8, 10, 8)
        l_proj.setSpacing(4)

        hdr_proj = QHBoxLayout()
        self.lbl_proj_t = QLabel(i18n.t("tb_field_project_name"))
        self.lbl_proj_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        lbl_proj_g = QLabel("115 × 15 mm")
        lbl_proj_g.setStyleSheet(f"font-size: 9px; color: {theme.TEXT_MUTED};")
        hdr_proj.addWidget(self.lbl_proj_t)
        hdr_proj.addStretch(1)
        hdr_proj.addWidget(lbl_proj_g)
        l_proj.addLayout(hdr_proj)

        self.txt_project_name = QPlainTextEdit()
        self.txt_project_name.setPlaceholderText("Многофункциональный высотный комплекс с подземной автостоянкой...")
        self.txt_project_name.setFixedHeight(66)
        self._style_plain_text(self.txt_project_name)
        self.txt_project_name.textChanged.connect(self._on_field_edited)
        l_proj.addWidget(self.txt_project_name)
        v_layout.addWidget(box_proj)

        # 3. SATIR: YAPI ADI (65 mm) + AŞAMA & PAFTA (50 mm)
        box_row3 = QFrame()
        box_row3.setStyleSheet(f"border-bottom: 2px solid {theme.BORDER_LIGHT}; padding: 0px;")
        l_row3 = QHBoxLayout(box_row3)
        l_row3.setContentsMargins(0, 0, 0, 0)
        l_row3.setSpacing(0)

        # Sol Hücre (65 mm: Yapı / Bölüm Adı - Графа 3)
        sub_bld = QFrame()
        sub_bld.setStyleSheet(f"border-right: 2px solid {theme.BORDER_LIGHT}; padding: 0px;")
        l_bld = QVBoxLayout(sub_bld)
        l_bld.setContentsMargins(10, 8, 10, 8)
        l_bld.setSpacing(4)

        hdr_bld = QHBoxLayout()
        self.lbl_bld_t = QLabel(i18n.t("tb_field_building_name"))
        self.lbl_bld_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        hdr_bld.addWidget(self.lbl_bld_t)
        l_bld.addLayout(hdr_bld)

        self.txt_building_name = QPlainTextEdit()
        self.txt_building_name.setPlaceholderText("Металлические конструкции секции Ф2\nСтальные сердечники...")
        self.txt_building_name.setFixedHeight(66)
        self._style_plain_text(self.txt_building_name)
        self.txt_building_name.textChanged.connect(self._on_field_edited)
        l_bld.addWidget(self.txt_building_name)
        l_row3.addWidget(sub_bld, 65)

        # Sağ Hücre (50 mm: Стадия, Лист, Листов - Графы 6, 7, 8)
        sub_stage = QFrame()
        l_stg = QVBoxLayout(sub_stage)
        l_stg.setContentsMargins(10, 8, 10, 8)
        l_stg.setSpacing(4)

        self.lbl_stg_t = QLabel(i18n.t("tb_field_stage_sheet_total"))
        self.lbl_stg_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        l_stg.addWidget(self.lbl_stg_t)

        grid_stg = QGridLayout()
        grid_stg.setSpacing(6)

        # Başlıklar
        self.lbl_col_stage = QLabel(i18n.t("tb_col_stage"))
        self.lbl_col_stage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_col_stage.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {theme.TEXT_MUTED};")
        grid_stg.addWidget(self.lbl_col_stage, 0, 0)

        self.lbl_col_num = QLabel(i18n.t("tb_col_sheet"))
        self.lbl_col_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_col_num.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {theme.TEXT_MUTED};")
        grid_stg.addWidget(self.lbl_col_num, 0, 1)

        self.lbl_col_tot = QLabel(i18n.t("tb_col_sheets"))
        self.lbl_col_tot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_col_tot.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {theme.TEXT_MUTED};")
        grid_stg.addWidget(self.lbl_col_tot, 0, 2)

        # Giriş kutuları
        self.txt_stage = QLineEdit()
        self.txt_stage.setPlaceholderText("Р")
        self.txt_stage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_stage.setFixedHeight(34)
        self._style_centered_edit(self.txt_stage, is_bold=True)
        self.txt_stage.textChanged.connect(self._on_field_edited)
        grid_stg.addWidget(self.txt_stage, 1, 0)

        self.txt_sheet_num = QLineEdit()
        self.txt_sheet_num.setPlaceholderText("1")
        self.txt_sheet_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_sheet_num.setFixedHeight(34)
        self._style_centered_edit(self.txt_sheet_num, is_bold=True)
        self.txt_sheet_num.textChanged.connect(self._on_field_edited)
        grid_stg.addWidget(self.txt_sheet_num, 1, 1)

        self.txt_total_sheets = QLineEdit()
        self.txt_total_sheets.setPlaceholderText("-")
        self.txt_total_sheets.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_total_sheets.setFixedHeight(34)
        self._style_centered_edit(self.txt_total_sheets)
        self.txt_total_sheets.textChanged.connect(self._on_field_edited)
        grid_stg.addWidget(self.txt_total_sheets, 1, 2)

        l_stg.addLayout(grid_stg)
        l_stg.addStretch(1)
        l_row3.addWidget(sub_stage, 50)

        v_layout.addWidget(box_row3)

        # 4. SATIR: ÇİZİM BAŞLIĞI (65 mm) + ŞİRKET VE LOGO (50 mm)
        box_row4 = QFrame()
        l_row4 = QHBoxLayout(box_row4)
        l_row4.setContentsMargins(0, 0, 0, 0)
        l_row4.setSpacing(0)

        # Sol Hücre (65 mm: Pafta Başlığı - Графа 4)
        sub_title = QFrame()
        sub_title.setStyleSheet(f"border-right: 2px solid {theme.BORDER_LIGHT}; padding: 0px;")
        l_ttl = QVBoxLayout(sub_title)
        l_ttl.setContentsMargins(10, 8, 10, 8)
        l_ttl.setSpacing(4)

        hdr_ttl = QHBoxLayout()
        self.lbl_ttl_t = QLabel(i18n.t("tb_field_sheet_title"))
        self.lbl_ttl_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        hdr_ttl.addWidget(self.lbl_ttl_t)
        l_ttl.addLayout(hdr_ttl)

        self.txt_sheet_title = QPlainTextEdit()
        self.txt_sheet_title.setPlaceholderText("Узлы изменения сечения колонн...")
        self.txt_sheet_title.setFixedHeight(66)
        self._style_plain_text(self.txt_sheet_title)
        self.txt_sheet_title.textChanged.connect(self._on_field_edited)
        l_ttl.addWidget(self.txt_sheet_title)
        l_row4.addWidget(sub_title, 65)

        # Sağ Hücre (50 mm: Şirket & Logo - Графа 9)
        sub_comp = QFrame()
        l_cmp = QVBoxLayout(sub_comp)
        l_cmp.setContentsMargins(10, 8, 10, 8)
        l_cmp.setSpacing(6)

        self.lbl_cmp_t = QLabel(i18n.t("tb_field_company"))
        self.lbl_cmp_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        l_cmp.addWidget(self.lbl_cmp_t)

        self.txt_company_name = QLineEdit()
        self.txt_company_name.setPlaceholderText("стадиа инжиниринг")
        self.txt_company_name.setFixedHeight(32)
        self.txt_company_name.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BG_SURFACE};
                color: #ffffff;
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 600;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.ACCENT_PRIMARY};
                background-color: {theme.BG_SURFACE_ACTIVE};
            }}
        """)
        self.txt_company_name.textChanged.connect(self._on_field_edited)
        l_cmp.addWidget(self.txt_company_name)

        # Logo Amblemi ve Dosya Seçici
        row_logo = QHBoxLayout()
        row_logo.setSpacing(6)
        self.chk_logo = QCheckBox(i18n.t("tb_logo_show"))
        self.chk_logo.setStyleSheet(f"""
            QCheckBox {{
                color: {theme.TEXT_PRIMARY};
                font-size: 11px;
                font-weight: 500;
            }}
        """)
        self.chk_logo.stateChanged.connect(self._on_field_edited)
        row_logo.addWidget(self.chk_logo)

        self.btn_select_logo = QPushButton(i18n.t("tb_logo_select"))
        self.btn_select_logo.setFixedHeight(24)
        self.btn_select_logo.setToolTip("PNG, JPG, BMP veya SVG kurumsal logo yükler")
        self.btn_select_logo.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                border-color: {theme.ACCENT_PRIMARY};
            }}
        """)
        self.btn_select_logo.clicked.connect(self._on_select_logo)
        row_logo.addWidget(self.btn_select_logo)

        self.btn_clear_logo = QPushButton("✕")
        self.btn_clear_logo.setFixedSize(22, 24)
        self.btn_clear_logo.setToolTip("Yüklenen logoyu kaldır")
        self.btn_clear_logo.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_MUTED};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                color: {theme.COLOR_ERROR};
                border-color: {theme.COLOR_ERROR_BORDER};
            }}
        """)
        self.btn_clear_logo.clicked.connect(self._on_clear_logo)
        row_logo.addWidget(self.btn_clear_logo)
        l_cmp.addLayout(row_logo)

        self.lbl_logo_info = QLabel("")
        self.lbl_logo_info.setStyleSheet(f"color: {theme.COLOR_SUCCESS}; font-size: 10px; font-weight: 500;")
        l_cmp.addWidget(self.lbl_logo_info)
        l_cmp.addStretch(1)

        l_row4.addWidget(sub_comp, 50)
        v_layout.addWidget(box_row4)

        return right_frame

    # -------------------------------------------------------------------------
    # 3. ALT BİLGİLENDİRME
    # -------------------------------------------------------------------------
    def _build_footer_info(self) -> QWidget:
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px dashed {theme.BORDER_LIGHT};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        layout = QHBoxLayout(box)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        lbl_icon = QLabel("💡")
        lbl_icon.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_icon)

        self.lbl_footer_text = QLabel(i18n.t("tb_info_footer"))
        self.lbl_footer_text.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px;")
        self.lbl_footer_text.setWordWrap(True)
        layout.addWidget(self.lbl_footer_text, 1)

        return box

    def _update_translations(self, lang_code: str = ""):
        """Dil değiştiğinde Form 3 Antet etiketlerini, butonlarını ve başlıklarını anlık günceller."""
        try:
            if hasattr(self, "btn_sample"):
                self.btn_sample.setText(f"📋 {i18n.t('btn_km_samples')}")
            if hasattr(self, "btn_clear"):
                self.btn_clear.setText(f"🗑️ {i18n.t('btn_clear')}")
            if hasattr(self, "lbl_rev_t"):
                self.lbl_rev_t.setText(i18n.t("tb_title_changes"))
            if hasattr(self, "tbl_revisions"):
                self.tbl_revisions.setHorizontalHeaderLabels([
                    i18n.t("tb_col_rev_num"), i18n.t("tb_col_rev_count"),
                    i18n.t("tb_col_rev_sheet"), i18n.t("tb_col_rev_doc"),
                    i18n.t("tb_col_sign"), i18n.t("tb_col_date")
                ])
            if hasattr(self, "lbl_sig_t"):
                self.lbl_sig_t.setText(i18n.t("tb_title_signatories"))
            if hasattr(self, "tbl_signatories"):
                self.tbl_signatories.setHorizontalHeaderLabels([
                    i18n.t("tb_col_role"), i18n.t("tb_col_name"),
                    i18n.t("tb_col_sign"), i18n.t("tb_col_date")
                ])
            if hasattr(self, "lbl_code_t"):
                self.lbl_code_t.setText(i18n.t("tb_field_doc_code"))
            if hasattr(self, "lbl_proj_t"):
                self.lbl_proj_t.setText(i18n.t("tb_field_project_name"))
            if hasattr(self, "lbl_bld_t"):
                self.lbl_bld_t.setText(i18n.t("tb_field_building_name"))
            if hasattr(self, "lbl_stg_t"):
                self.lbl_stg_t.setText(i18n.t("tb_field_stage_sheet_total"))
            if hasattr(self, "lbl_col_stage"):
                self.lbl_col_stage.setText(i18n.t("tb_col_stage"))
            if hasattr(self, "lbl_col_num"):
                self.lbl_col_num.setText(i18n.t("tb_col_sheet"))
            if hasattr(self, "lbl_col_tot"):
                self.lbl_col_tot.setText(i18n.t("tb_col_sheets"))
            if hasattr(self, "lbl_ttl_t"):
                self.lbl_ttl_t.setText(i18n.t("tb_field_sheet_title"))
            if hasattr(self, "lbl_cmp_t"):
                self.lbl_cmp_t.setText(i18n.t("tb_field_company"))
            if hasattr(self, "chk_logo"):
                self.chk_logo.setText(i18n.t("tb_logo_show"))
            if hasattr(self, "btn_select_logo"):
                self.btn_select_logo.setText(i18n.t("tb_logo_select"))
            if hasattr(self, "lbl_footer_text"):
                self.lbl_footer_text.setText(i18n.t("tb_info_footer"))
        except RuntimeError:
            pass

    # -------------------------------------------------------------------------
    # STİL YARDIMCILARI
    # -------------------------------------------------------------------------
    def _style_table(self, tbl: QTableWidget):
        tbl.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme.BG_APP};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                gridline-color: {theme.BORDER_SUBTLE};
                font-size: 12px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 4px 6px;
                font-size: 12px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: #ffffff;
            }}
            QTableWidget QLineEdit {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: #ffffff;
                font-size: 12px;
                font-weight: 500;
                padding: 2px 8px;
                border: 1.5px solid {theme.ACCENT_PRIMARY};
                border-radius: 4px;
                selection-background-color: {theme.ACCENT_PRIMARY};
                selection-color: #ffffff;
            }}
            QHeaderView::section {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: {theme.TEXT_MUTED};
                font-size: 10px;
                font-weight: 600;
                border: none;
                border-right: 1px solid {theme.BORDER_SUBTLE};
                border-bottom: 1px solid {theme.BORDER_SUBTLE};
                padding: 3px 4px;
            }}
        """)

    def _style_plain_text(self, edit: QPlainTextEdit):
        edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                line-height: 1.25;
            }}
            QPlainTextEdit:focus {{
                border: 1px solid {theme.ACCENT_PRIMARY};
                background-color: {theme.BG_SURFACE_ACTIVE};
            }}
        """)

    def _style_centered_edit(self, edit: QLineEdit, is_bold: bool = False):
        weight = "700" if is_bold else "500"
        edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 13px;
                font-weight: {weight};
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.ACCENT_PRIMARY};
                background-color: {theme.BG_SURFACE_ACTIVE};
            }}
        """)

    # -------------------------------------------------------------------------
    # VERİ YÖNETİMİ & SENKRONİZASYON
    # -------------------------------------------------------------------------
    def get_document(self) -> TitleBlockDocument:
        return self._document

    def set_document(self, doc: TitleBlockDocument):
        self._is_loading = True
        self._document = doc
        self._logo_image_path = doc.logo_image_path

        # Form alanlarını doldur
        self.txt_doc_code.setText(doc.doc_code)
        self.txt_project_name.setPlainText(doc.project_name)
        self.txt_building_name.setPlainText(doc.building_name)
        self.txt_sheet_title.setPlainText(doc.sheet_title)
        self.txt_stage.setText(doc.stage)
        self.txt_sheet_num.setText(doc.sheet_num)
        self.txt_total_sheets.setText(doc.total_sheets)
        self.txt_company_name.setText(doc.company_name)
        self.chk_logo.setChecked(doc.company_logo)

        if doc.logo_image_path and os.path.exists(doc.logo_image_path):
            self.lbl_logo_info.setText(f"✓ {os.path.basename(doc.logo_image_path)}")
        else:
            self.lbl_logo_info.setText("")

        # İmzalar tablosu
        self.tbl_signatories.blockSignals(True)
        for r, sig in enumerate(doc.signatories[:6]):
            self.tbl_signatories.setItem(r, 0, QTableWidgetItem(sig.role))
            self.tbl_signatories.setItem(r, 1, QTableWidgetItem(sig.surname))
            self.tbl_signatories.setItem(r, 2, QTableWidgetItem(sig.signature))
            self.tbl_signatories.setItem(r, 3, QTableWidgetItem(sig.date))
        self.tbl_signatories.blockSignals(False)

        # Revizyon tablosu
        self.tbl_revisions.blockSignals(True)
        for r, rev in enumerate(doc.revisions[:4]):
            self.tbl_revisions.setItem(r, 0, QTableWidgetItem(rev.rev_num))
            self.tbl_revisions.setItem(r, 1, QTableWidgetItem(rev.num_changes))
            self.tbl_revisions.setItem(r, 2, QTableWidgetItem(rev.sheet))
            self.tbl_revisions.setItem(r, 3, QTableWidgetItem(rev.doc_num))
            self.tbl_revisions.setItem(r, 4, QTableWidgetItem(rev.signature))
            self.tbl_revisions.setItem(r, 5, QTableWidgetItem(rev.date))
        self.tbl_revisions.blockSignals(False)

        self._is_loading = False

    def load_sample_km(self):
        """Örnek standart KM antet içeriği yükler."""
        doc = TitleBlockDocument(
            doc_code="2026-001-КМ",
            project_name=(
                "Производственно-складской комплекс в промышленном парке «Северный»,\n"
                "расположенный по адресу: Московская область, г.о. Солнечногорск, тер. Промзона-1,\n"
                "земельный участок с кадастровым номером 50:09:0000000:12345"
            ),
            building_name="Главный производственный корпус\nМеталлический каркас",
            sheet_title="Схема расположения колонн и балок на отм. +4.200",
            stage="Р",
            sheet_num="1",
            total_sheets="12",
            company_name="ООО «ПРОЕКТ-СТРОЙ»",
            company_logo=False,
            logo_image_path=None,
            signatories=build_default_signatories(),
            revisions=build_default_revisions()
        )
        self.set_document(doc)
        self._sync_and_emit()

    def clear_all(self, prompt: bool = False):
        """Tüm antet alanlarını ve sorumlu imza/tarih bilgilerini temizler."""
        if prompt:
            reply = QMessageBox.question(
                self,
                "Anteti Temizle",
                "Tüm antet alanlarını ve sorumlu imza/tarih bilgilerini temizlemek istediğinizden emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        doc = TitleBlockDocument(
            doc_code="",
            project_name="",
            building_name="",
            sheet_title="",
            stage="Р",
            sheet_num="1",
            total_sheets="",
            company_name="",
            company_logo=False,
            logo_image_path=None,
            signatories=build_empty_signatories(),
            revisions=build_default_revisions()
        )
        self.set_document(doc)
        self._sync_and_emit()

    def _on_select_logo(self):
        """Kullanıcının kurumsal logo resmi yüklemesini sağlar."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Kurumsal Logo Dosyası Seç",
            "",
            "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.svg)"
        )
        if file_path:
            self._logo_image_path = file_path
            self.lbl_logo_info.setText(f"✓ {os.path.basename(file_path)}")
            self.chk_logo.setChecked(True)
            self._sync_and_emit()

    def _on_clear_logo(self):
        """Yüklenen logo dosyasını kaldırır."""
        self._logo_image_path = None
        self.lbl_logo_info.setText("")
        self._sync_and_emit()

    def _on_field_edited(self):
        if self._is_loading:
            return
        self._sync_and_emit()

    def _on_table_edited(self, row: int, col: int):
        if self._is_loading:
            return
        self._sync_and_emit()

    def _sync_and_emit(self):
        # Alanlardan güncel TitleBlockDocument nesnesi oluştur
        doc = TitleBlockDocument(
            doc_code=self.txt_doc_code.text().strip(),
            project_name=self.txt_project_name.toPlainText().strip(),
            building_name=self.txt_building_name.toPlainText().strip(),
            sheet_title=self.txt_sheet_title.toPlainText().strip(),
            stage=self.txt_stage.text().strip(),
            sheet_num=self.txt_sheet_num.text().strip(),
            total_sheets=self.txt_total_sheets.text().strip(),
            company_name=self.txt_company_name.text().strip(),
            company_logo=self.chk_logo.isChecked(),
            logo_image_path=self._logo_image_path,
        )

        # İmzaları topla
        sigs: List[SignatoryEntry] = []
        for r in range(self.tbl_signatories.rowCount()):
            role = self._get_cell_text(self.tbl_signatories, r, 0)
            sur = self._get_cell_text(self.tbl_signatories, r, 1)
            sig = self._get_cell_text(self.tbl_signatories, r, 2)
            dat = self._get_cell_text(self.tbl_signatories, r, 3)
            sigs.append(SignatoryEntry(role=role, surname=sur, signature=sig, date=dat))
        doc.signatories = sigs

        # Revizyonları topla
        revs: List[RevisionEntry] = []
        for r in range(self.tbl_revisions.rowCount()):
            r_num = self._get_cell_text(self.tbl_revisions, r, 0)
            r_chg = self._get_cell_text(self.tbl_revisions, r, 1)
            r_sht = self._get_cell_text(self.tbl_revisions, r, 2)
            r_doc = self._get_cell_text(self.tbl_revisions, r, 3)
            r_sig = self._get_cell_text(self.tbl_revisions, r, 4)
            r_dat = self._get_cell_text(self.tbl_revisions, r, 5)
            revs.append(RevisionEntry(
                rev_num=r_num, num_changes=r_chg, sheet=r_sht,
                doc_num=r_doc, signature=r_sig, date=r_dat
            ))
        doc.revisions = revs

        self._document = doc
        self.document_changed.emit(self._document)

    @staticmethod
    def _get_cell_text(tbl: QTableWidget, r: int, c: int) -> str:
        item = tbl.item(r, c)
        return item.text().strip() if item else ""
