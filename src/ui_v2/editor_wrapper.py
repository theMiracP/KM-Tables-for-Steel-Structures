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
from src.ui.i18n import i18n


class TableEditorWrapper(QWidget):
    """
    Notion veri tabanı sayfası görünümünde modern editör konteyneri.
    """
    document_changed = Signal(object)  # new document

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

        # 1. NOTION SAYFA BAŞLIĞI
        header_widget = QWidget()
        h_layout = QVBoxLayout(header_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(4)

        # Başlık Satırı
        title_row = QHBoxLayout()
        self.lbl_icon = QLabel("📋")
        self.lbl_icon.setStyleSheet("font-size: 20px;")
        title_row.addWidget(self.lbl_icon)

        self.lbl_title = QLabel("Veri Giriş Tablosu")
        self.lbl_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {theme.TEXT_PRIMARY};
        """)
        title_row.addWidget(self.lbl_title)
        title_row.addStretch(1)

        # Hızlı Yardım İpucu
        self.lbl_hint = QLabel(i18n.t("hint_excel_paste"))
        self.lbl_hint.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px;")
        title_row.addWidget(self.lbl_hint)

        h_layout.addLayout(title_row)

        self.lbl_subtitle = QLabel("ГОСТ 21.502-2007 Mühendislik Çizim Elemanları")
        self.lbl_subtitle.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px;")
        h_layout.addWidget(self.lbl_subtitle)

        layout.addWidget(header_widget)

        # 2. AKTİF EDİTÖR YIĞINI (QStackedWidget)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack, 1)

    def _get_module_title_and_subtitle(self, module_id: str) -> tuple:
        """Seçilen dile göre (icon, title, subtitle) tuple döndürür."""
        if "elementov" in module_id or "elements" in module_id:
            return "📄", i18n.t("wrapper_title_elements_schedule"), i18n.t("wrapper_subtitle_elements_schedule")
        elif "title_block" in module_id or "antet" in module_id:
            return "🏷️", i18n.t("wrapper_title_title_block"), i18n.t("wrapper_subtitle_title_block")
        elif "reference" in module_id or "doc" in module_id:
            return "📚", i18n.t("wrapper_title_reference_docs"), i18n.t("wrapper_subtitle_reference_docs")
        elif "working_drawings" in module_id:
            return "📋", i18n.t("wrapper_title_working_drawings"), i18n.t("wrapper_subtitle_working_drawings")
        elif "main_drawings" in module_id or "drawings" in module_id or "main_sets" in module_id:
            return "📑", i18n.t("wrapper_title_main_drawings"), i18n.t("wrapper_subtitle_main_drawings")
        else:
            return "📊", i18n.t("wrapper_title_generic"), i18n.t("wrapper_subtitle_generic")

    def _update_translations(self, lang: Optional[str] = None):
        """Aktif dil değiştiğinde başlık, alt başlık ve ipucunu günceller."""
        self.lbl_hint.setText(i18n.t("hint_excel_paste"))
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
