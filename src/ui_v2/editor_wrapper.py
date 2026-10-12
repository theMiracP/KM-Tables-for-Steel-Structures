"""
Notion / Linear Tarzı Veri Editörü Sarmalayıcısı (TableEditorWrapper).
Başlık, açıklama, hızlı eylem butonları ve gömülü tablo editörü içerir.
"""
from typing import Optional, Any
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QStackedWidget
)
from src.contracts.table_module import TableModule
from src.ui_v2 import theme_linear as theme
from src.ui.i18n import i18n, get_module_display_title


class TableEditorWrapper(QWidget):
    """
    Notion veri tabanı sayfası görünümünde modern editör konteyneri.
    """
    document_changed = Signal(object)  # new document
    save_preset_requested = Signal()
    load_preset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {theme.BG_APP};")
        self._editors = {}
        self._active_module_id: Optional[str] = None

        self._build_ui()
        i18n.language_changed.connect(self._update_translations)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. NOTION / LINEAR SAYFA BAŞLIK KARTI (Kutulu, Derli Toplu Modern Görünüm)
        header_widget = QFrame()
        header_widget.setObjectName("editorHeaderCard")
        header_widget.setStyleSheet(f"""
            QFrame#editorHeaderCard {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 8px;
            }}
        """)
        h_layout = QVBoxLayout(header_widget)
        h_layout.setContentsMargins(14, 10, 14, 10)
        h_layout.setSpacing(6)

        # 1. Satır: İkon + Tablo Başlığı (Sol) & Şablon Eylem Butonları (Sağ)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)

        self.lbl_icon = QLabel("📋")
        self.lbl_icon.setStyleSheet("font-size: 18px;")
        title_row.addWidget(self.lbl_icon)

        self.lbl_title = QLabel("Veri Giriş Tablosu")
        self.lbl_title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: #ffffff;
        """)
        title_row.addWidget(self.lbl_title)
        title_row.addStretch(1)

        # Şablon Eylem Butonları (Üst Sağ Köşe)
        self.btn_save_preset = QPushButton(i18n.t("btn_save_preset"))
        self.btn_save_preset.setFixedHeight(26)
        self.btn_save_preset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_preset.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 5px;
                padding: 0 10px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                border-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
            }}
        """)
        self.btn_save_preset.clicked.connect(self.save_preset_requested.emit)
        title_row.addWidget(self.btn_save_preset)

        self.btn_load_preset = QPushButton(i18n.t("btn_load_preset"))
        self.btn_load_preset.setFixedHeight(26)
        self.btn_load_preset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load_preset.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 5px;
                padding: 0 10px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                border-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
            }}
        """)
        self.btn_load_preset.clicked.connect(self.load_preset_requested.emit)
        title_row.addWidget(self.btn_load_preset)

        h_layout.addLayout(title_row)

        # 2. Satır: Alt Başlık / Standart Açıklaması (Sol) & Excel İpucu Rozeti (Sağ)
        sub_row = QHBoxLayout()
        sub_row.setContentsMargins(0, 0, 0, 0)
        sub_row.setSpacing(8)

        self.lbl_subtitle = QLabel("ГОСТ 21.502-2007 • Çelik Yapı Elemanları")
        self.lbl_subtitle.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px;")
        sub_row.addWidget(self.lbl_subtitle)
        sub_row.addStretch(1)

        # Excel Kısayol İpucu Rozeti
        self.lbl_hint = QLabel(f"📋 {i18n.t('hint_excel_paste_short')}")
        self.lbl_hint.setToolTip(i18n.t("hint_excel_paste"))
        self.lbl_hint.setStyleSheet(f"""
            color: {theme.TEXT_MUTED};
            font-size: 10px;
            background-color: {theme.BG_APP};
            border: 1px solid {theme.BORDER_SUBTLE};
            border-radius: 4px;
            padding: 2px 7px;
        """)
        sub_row.addWidget(self.lbl_hint)

        h_layout.addLayout(sub_row)

        layout.addWidget(header_widget)

        # 2. AKTİF EDİTÖR YIĞINI (QStackedWidget)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack, 1)

    def _get_module_title_and_subtitle(self, module_id: str) -> tuple:
        """Seçilen dile göre (icon, title, subtitle) tuple döndürür."""
        title = get_module_display_title(module_id)
        if "elementov" in module_id or "elements" in module_id:
            return "📄", title, i18n.t("wrapper_subtitle_elements_schedule")
        elif "title_block" in module_id or "antet" in module_id:
            return "🏷️", title, i18n.t("wrapper_subtitle_title_block")
        elif "reference" in module_id or "doc" in module_id:
            return "📚", title, i18n.t("wrapper_subtitle_reference_docs")
        elif "working_drawings" in module_id:
            return "📋", title, i18n.t("wrapper_subtitle_working_drawings")
        elif "main_drawings" in module_id or "drawings" in module_id or "main_sets" in module_id:
            return "📑", title, i18n.t("wrapper_subtitle_main_drawings")
        else:
            return "📊", title, i18n.t("wrapper_subtitle_generic")

    def _update_translations(self, lang: Optional[str] = None):
        """Aktif dil değiştiğinde başlık, alt başlık ve ipucunu günceller."""
        if hasattr(self, "lbl_hint"):
            self.lbl_hint.setText(f"📋 {i18n.t('hint_excel_paste_short')}")
            self.lbl_hint.setToolTip(i18n.t("hint_excel_paste"))
        if hasattr(self, "btn_save_preset"):
            self.btn_save_preset.setText(i18n.t("btn_save_preset"))
        if hasattr(self, "btn_load_preset"):
            self.btn_load_preset.setText(i18n.t("btn_load_preset"))
        if self._active_module_id:
            icon, title, subtitle = self._get_module_title_and_subtitle(self._active_module_id)
            self.lbl_icon.setText(icon)
            self.lbl_title.setText(title)
            self.lbl_subtitle.setText(subtitle)

    def register_module(self, module: TableModule):
        if module.id not in self._editors:
            editor = module.create_editor(self)
            # Editör sinyalini yakala
            if hasattr(editor, "document_changed"):
                editor.document_changed.connect(lambda doc, m_id=module.id: self._on_editor_changed(m_id, doc))
            elif hasattr(editor, "items_changed"):
                editor.items_changed.connect(lambda items, m_id=module.id: self._on_editor_items_changed(m_id, items))

            self._editors[module.id] = (module, editor)
            self.stack.addWidget(editor)

    def show_module(self, module_id: str, document: Optional[Any] = None):
        if module_id not in self._editors:
            return

        self._active_module_id = module_id
        module, editor = self._editors[module_id]

        self._update_translations()

        if document is not None and hasattr(editor, "set_document"):
            editor.set_document(document)

        self.stack.setCurrentWidget(editor)

    def get_current_document(self) -> Optional[Any]:
        if not self._active_module_id or self._active_module_id not in self._editors:
            return None
        _, editor = self._editors[self._active_module_id]
        if hasattr(editor, "get_document"):
            return editor.get_document()
        return None

    @property
    def active_editor(self) -> Optional[QWidget]:
        return self.stack.currentWidget()

    def _on_editor_changed(self, module_id: str, doc: Any):
        if module_id == self._active_module_id:
            self.document_changed.emit(doc)

    def _on_editor_items_changed(self, module_id: str, items: Any):
        if module_id == self._active_module_id:
            self.document_changed.emit(items)
