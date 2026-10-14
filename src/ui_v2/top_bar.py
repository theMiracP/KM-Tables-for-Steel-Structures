"""
Linear / Notion SaaS Üst Gezinme Çubuğu (TopBar).
Breadcrumbs, Command Palette (Ctrl+K) tetikleyicisi, GOST uyumluluk rozeti ve DXF dışa aktarma eylemi.
"""
import os
from typing import Optional
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QWidget, QSizePolicy
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2 import icons
from src.ui_v2.components import LinearShimmerButton
from src.ui.i18n import i18n


class LinearTopBar(QFrame):
    """
    SaaS tarzı 48px kompakt, minimalist üst navigasyon çubuğu.
    """
    command_palette_requested = Signal()
    export_dxf_requested = Signal()
    export_pdf_requested = Signal()
    new_project_requested = Signal()
    open_project_requested = Signal()
    save_project_requested = Signal()
    save_project_as_requested = Signal()
    toggle_sidebar_requested = Signal()
    toggle_cad_requested = Signal()
    language_changed = Signal(str)
    about_requested = Signal()
    settings_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SIDEBAR};
                border-bottom: 1px solid {theme.BORDER_SUBTLE};
            }}
        """)
        self._build_ui()
        i18n.language_changed.connect(self._update_translations)

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 16, 0)
        layout.setSpacing(12)

        # 1. SOL BÖLÜM: Kenar Çubuğu Aç/Kapa & Logo + KM Studio
        self.btn_toggle_sidebar = QPushButton()
        self.btn_toggle_sidebar.setIcon(icons.get_icon(icons.ICON_MENU, color=icons.COLOR_NEUTRAL))
        self.btn_toggle_sidebar.setIconSize(icons.icon_size(14))
        self.btn_toggle_sidebar.setObjectName("ghostButton")
        self.btn_toggle_sidebar.setToolTip("Kenar Çubuğunu Gizle / Göster (Ctrl+B)")
        self.btn_toggle_sidebar.setFixedSize(28, 28)
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar_requested.emit)
        layout.addWidget(self.btn_toggle_sidebar)

        self.lbl_workspace = QLabel("📐 KM Studio")
        self.lbl_workspace.setStyleSheet(f"font-weight: 600; color: {theme.TEXT_PRIMARY}; font-size: 13px;")
        layout.addWidget(self.lbl_workspace)

        # Proje Menüsü Butonu (Item 4.1)
        self.btn_project = QPushButton("📁 Proje ▾")
        self.btn_project.setObjectName("ghostButton")
        self.btn_project.setFixedHeight(28)
        self.btn_project.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_project.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                border-color: {theme.BORDER_LIGHT};
            }}
        """)
        self._build_project_menu()
        layout.addWidget(self.btn_project)

        # Geriye dönük uyumluluk ve testler için dummy etiketler
        self.lbl_standard = QLabel("")
        self.lbl_standard.hide()
        self.lbl_active_table = QLabel("")
        self.lbl_active_table.hide()

        # 2. ORTA BÖLÜM: Linear Command Palette Tetikleyici Butonu (Ctrl+K)
        layout.addStretch(1)

        self.btn_command_bar = QPushButton(i18n.t("search_command_bar"))
        self.btn_command_bar.setIcon(icons.get_icon(icons.ICON_SEARCH, color=icons.COLOR_MUTED))
        self.btn_command_bar.setIconSize(icons.icon_size(13))
        self.btn_command_bar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_command_bar.setFixedHeight(30)
        self.btn_command_bar.setMinimumWidth(260)
        self.btn_command_bar.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_MUTED};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 0 12px;
                text-align: left;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                color: {theme.TEXT_SECONDARY};
                border-color: {theme.BORDER_LIGHT};
            }}
        """)
        self.btn_command_bar.clicked.connect(self.command_palette_requested.emit)
        layout.addWidget(self.btn_command_bar)

        layout.addStretch(1)

        # 3. SAĞ BÖLÜM: Dil Seçicisi ve Ana Eylem Butonları
        # (GOST badge kaldırıldı, geriye dönük uyumluluk için referans korundu)
        self.badge_gost = QLabel("")
        self.badge_gost.hide()

        # Dil hapları (Pills)
        self._build_language_pills(layout)

        # CAD Ekranı Aç/Kapat Butonu (Ctrl+J)
        self.btn_toggle_cad = QPushButton(f" {i18n.t('btn_cad_panel')}")
        self.btn_toggle_cad.setIcon(icons.get_icon(icons.ICON_DESKTOP, color=icons.COLOR_ACCENT_BLUE))
        self.btn_toggle_cad.setIconSize(icons.icon_size(14))
        self.btn_toggle_cad.setObjectName("ghostButton")
        self.btn_toggle_cad.setFixedHeight(30)
        self.btn_toggle_cad.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_cad.setToolTip(i18n.t("tooltip_toggle_cad"))
        self.btn_toggle_cad.clicked.connect(self.toggle_cad_requested.emit)
        layout.addWidget(self.btn_toggle_cad)
        self.set_cad_visible(True)

        # Hakkında Butonu
        self.btn_about = QPushButton(" Hakkında")
        self.btn_about.setIcon(icons.get_icon(icons.ICON_INFO, color=icons.COLOR_NEUTRAL))
        self.btn_about.setIconSize(icons.icon_size(14))
        self.btn_about.setObjectName("ghostButton")
        self.btn_about.setFixedHeight(30)
        self.btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about.clicked.connect(self.about_requested.emit)
        layout.addWidget(self.btn_about)

        # Ayarlar Butonu
        self.btn_settings = QPushButton(f" {i18n.t('btn_settings')}")
        self.btn_settings.setIcon(icons.get_icon(icons.ICON_SETTINGS, color=icons.COLOR_NEUTRAL))
        self.btn_settings.setIconSize(icons.icon_size(14))
        self.btn_settings.setObjectName("ghostButton")
        self.btn_settings.setFixedHeight(30)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.btn_settings)

        # Vektör PDF Dışa Aktar Butonu (Item 2.3)
        self.btn_export_pdf = QPushButton(" 📄 PDF Aktar")
        self.btn_export_pdf.setObjectName("ghostButton")
        self.btn_export_pdf.setFixedHeight(30)
        self.btn_export_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_pdf.setToolTip("1:1 Ölçekli Vektör PDF Olarak Dışa Aktar (Ctrl+P)")
        self.btn_export_pdf.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: #38BDF8;
                border: 1px solid #0284C7;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #0369A1;
                color: #FFFFFF;
            }}
        """)
        self.btn_export_pdf.clicked.connect(self.export_pdf_requested.emit)
        layout.addWidget(self.btn_export_pdf)

        # Linear Ana Eylem: Export DXF (Sağdan sola jilet parlamalı buton)
        self.btn_export = LinearShimmerButton(" DXF Dışa Aktar")
        self.btn_export.setIcon(icons.get_icon(icons.ICON_BOLT, color=icons.COLOR_WHITE))
        self.btn_export.setIconSize(icons.icon_size(14))
        self.btn_export.setObjectName("primaryButton")
        self.btn_export.setFixedHeight(30)
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_dxf_requested.emit)
        layout.addWidget(self.btn_export)

    def _build_project_menu(self):
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 18px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: #FFFFFF;
            }}
        """)
        act_new = menu.addAction("📄 Yeni Proje (Ctrl+N)")
        act_new.triggered.connect(self.new_project_requested.emit)

        act_open = menu.addAction("📂 Projeyi Aç... (Ctrl+O)")
        act_open.triggered.connect(self.open_project_requested.emit)

        menu.addSeparator()

        act_save = menu.addAction("💾 Projeyi Kaydet (Ctrl+S)")
        act_save.triggered.connect(self.save_project_requested.emit)

        act_save_as = menu.addAction("📋 Farklı Kaydet... (Ctrl+Shift+S)")
        act_save_as.triggered.connect(self.save_project_as_requested.emit)

        self.btn_project.setMenu(menu)

    def _build_language_pills(self, parent_layout: QHBoxLayout):
        lang_container = QWidget()
        lang_layout = QHBoxLayout(lang_container)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setSpacing(2)

        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.lang_btns = {}
        for code, label, svg_name in [("tr", "TR", "flag_tr.svg"), ("ru", "RU", "flag_ru.svg"), ("en", "EN", "flag_en.svg")]:
            btn = QPushButton(f" {label}")
            svg_path = os.path.join(assets_dir, svg_name)
            if os.path.exists(svg_path):
                btn.setIcon(QIcon(svg_path))
                btn.setIconSize(QSize(16, 11))
            btn.setFixedSize(52, 24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, c=code: self._on_lang_clicked(c))
            self.lang_btns[code] = btn
            self.lang_btns[code.upper()] = btn
            lang_layout.addWidget(btn)

        self._update_lang_styles()
        parent_layout.addWidget(lang_container)

    def _on_lang_clicked(self, code: str):
        i18n.set_language(code)
        self.language_changed.emit(code)
        self._update_lang_styles()

    def _update_lang_styles(self):
        curr = i18n.current_language.lower()
        for code, btn in self.lang_btns.items():
            if code.lower() == curr:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {theme.BG_SURFACE_ACTIVE};
                        color: #ffffff;
                        border: 1px solid {theme.BORDER_LIGHT};
                        border-radius: 4px;
                        font-weight: 600;
                        font-size: 11px;
                        padding: 0 4px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {theme.TEXT_MUTED};
                        border: 1px solid transparent;
                        border-radius: 4px;
                        font-size: 11px;
                        padding: 0 4px;
                    }}
                    QPushButton:hover {{
                        color: {theme.TEXT_PRIMARY};
                        background-color: {theme.BG_SURFACE_HOVER};
                    }}
                """)

    def set_active_module_id(self, module_id: str):
        self._active_module_id = module_id
        self._update_active_table_label()

    def set_active_table_title(self, title: str):
        self.lbl_active_table.setText(title)

    def _update_active_table_label(self):
        if hasattr(self, "_active_module_id") and self._active_module_id:
            from src.ui.i18n import get_module_display_title
            self.lbl_active_table.setText(get_module_display_title(self._active_module_id))

    def set_validation_status(self, is_valid: bool, text: Optional[str] = None):
        self._is_valid = is_valid
        status_text = text if text is not None else i18n.t("badge_gost_compliant")
        if is_valid:
            self.badge_gost.setText(f"● {status_text}")
            self.badge_gost.setStyleSheet(f"""
                QLabel {{
                    background-color: {theme.COLOR_SUCCESS_BG};
                    color: {theme.COLOR_SUCCESS};
                    border: 1px solid {theme.COLOR_SUCCESS_BORDER};
                    border-radius: 12px;
                    padding: 0 10px;
                    font-size: 11px;
                    font-weight: 600;
                }}
            """)
        else:
            self.badge_gost.setText(f"▲ {status_text}")
            self.badge_gost.setStyleSheet(f"""
                QLabel {{
                    background-color: {theme.COLOR_WARNING_BG};
                    color: {theme.COLOR_WARNING};
                    border: 1px solid {theme.COLOR_WARNING_BORDER};
                    border-radius: 12px;
                    padding: 0 10px;
                    font-size: 11px;
                    font-weight: 600;
                }}
            """)

    def set_cad_visible(self, is_visible: bool):
        """CAD panelinin görünürlük durumuna göre buton stilini ve durumunu günceller."""
        if not hasattr(self, "btn_toggle_cad"):
            return
        if is_visible:
            self.btn_toggle_cad.setIcon(icons.get_icon(icons.ICON_DESKTOP, color=icons.COLOR_ACCENT_BLUE))
            self.btn_toggle_cad.setToolTip("CAD Ekranını Gizle (Ctrl+J)")
            self.btn_toggle_cad.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.BG_SURFACE_ACTIVE};
                    color: {theme.TEXT_PRIMARY};
                    border: 1px solid {theme.BORDER_LIGHT};
                    border-radius: 6px;
                    padding: 0 10px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme.BG_SURFACE_HOVER};
                    border-color: {theme.ACCENT_PRIMARY};
                }}
            """)
        else:
            self.btn_toggle_cad.setIcon(icons.get_icon(icons.ICON_DESKTOP, color=icons.COLOR_MUTED))
            self.btn_toggle_cad.setToolTip("CAD Ekranını Göster (Ctrl+J)")
            self.btn_toggle_cad.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme.TEXT_MUTED};
                    border: 1px dashed {theme.BORDER_LIGHT};
                    border-radius: 6px;
                    padding: 0 10px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme.BG_SURFACE_HOVER};
                    color: {theme.TEXT_PRIMARY};
                    border-color: {theme.ACCENT_PRIMARY};
                }}
            """)

    def _update_translations(self):
        self._update_lang_styles()
        self.btn_export.setText(f" {i18n.t('action_export_dxf')}")
        if hasattr(self, "btn_command_bar"):
            self.btn_command_bar.setText(i18n.t("search_command_bar"))
        if hasattr(self, "btn_toggle_cad"):
            self.btn_toggle_cad.setText(f" {i18n.t('btn_cad_panel')}")
        if hasattr(self, "btn_about"):
            self.btn_about.setText(f" {i18n.t('action_about')}")
        if hasattr(self, "btn_settings"):
            self.btn_settings.setText(f" {i18n.t('btn_settings')}")
        self.set_validation_status(getattr(self, "_is_valid", True))
        self._update_active_table_label()
