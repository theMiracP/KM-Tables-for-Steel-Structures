"""
KM Tablo Oluşturucu - Hızlı Tablo Değiştirici (Quick Table Switcher / Ctrl+K / Ctrl+T).
Merkezde açılan, klavye odaklı, anında filtrelenebilir Notion/Linear tarzı komut ve tablo seçim diyaloğu.
"""
from typing import Optional
from PySide6.QtCore import Qt, QEvent, Signal, QSize
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QLabel, QWidget
)

from src.contracts.table_module import TableModule
from src.models.registry import TableRegistry
from src.ui_v2 import theme_linear as theme
from src.ui_v2 import icons
from src.ui_v2.sidebar import get_module_display_title, get_module_icon_name
from src.ui.i18n import i18n


class QuickTableSwitcherDialog(QDialog):
    """
    Ctrl+K / Ctrl+T ile tetiklenen hızlı tablo arama ve geçiş diyaloğu.
    Tüm programdaki (Sidebar, TopBar vb.) standart tablo adlarıyla %100 senkronize çalışır.
    """
    module_selected = Signal(str)

    def __init__(self, current_module_id: Optional[str] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_module_id = current_module_id
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setFixedSize(560, 360)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 8px;
            }}
            QLineEdit {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                selection-background-color: {theme.ACCENT_PRIMARY};
                selection-color: #ffffff;
            }}
            QLineEdit:focus {{
                border-color: {theme.ACCENT_PRIMARY};
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                color: {theme.TEXT_PRIMARY};
                padding: 6px 10px;
                border-radius: 6px;
                margin: 2px 0;
                font-size: 12px;
            }}
            QListWidget::item:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {theme.BG_SURFACE_ACTIVE};
                border-left: 3px solid {theme.ACCENT_PRIMARY};
                font-weight: 600;
            }}
        """)

        self.selected_table_id: Optional[str] = None
        self._build_ui()
        self._populate_list()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Üst Başlık & İpucu
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        lbl_title = QLabel(i18n.t("quick_switcher_title"))
        lbl_title.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {theme.TEXT_PRIMARY};")
        header_layout.addWidget(lbl_title)

        lbl_hint = QLabel(i18n.t("quick_switcher_hint"))
        lbl_hint.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        header_layout.addWidget(lbl_hint)
        layout.addLayout(header_layout)

        # Arama Girdi Kutusu
        self.search_edit = QLineEdit(self)
        self.search_edit.setPlaceholderText(i18n.t("search_table_placeholder"))
        self.search_edit.setFixedHeight(32)
        self.search_edit.textChanged.connect(self._filter_list)
        layout.addWidget(self.search_edit)

        # Sonuç Listesi
        self.list_widget = QListWidget(self)
        self.list_widget.setIconSize(icons.icon_size(16))
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        # Event filtreleri (Enter / Esc / Up / Down)
        self.search_edit.installEventFilter(self)
        self.list_widget.installEventFilter(self)

    def _populate_list(self):
        self.list_widget.clear()
        modules = [m for m in TableRegistry.all() if getattr(m, "is_active", True)]
        for mod in modules:
            item = QListWidgetItem()
            item.setSizeHint(QSize(520, 44))
            title = get_module_display_title(mod)
            gost_desc = getattr(mod, "name", "")
            
            # Ana başlık sidebar ve tüm programdaki ile birebir aynı isim!
            item.setText(f"{title}\n   {gost_desc}")
            item.setData(Qt.ItemDataRole.UserRole, mod.id)
            
            ico = icons.get_icon(get_module_icon_name(mod.id), color=icons.COLOR_PRIMARY)
            if not ico.isNull():
                item.setIcon(ico)
                
            self.list_widget.addItem(item)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _filter_list(self, query: str):
        query = query.strip().lower()
        visible_count = 0
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            mod_id = str(item.data(Qt.ItemDataRole.UserRole) or "").lower()
            match = not query or query in item.text().lower() or query in mod_id
            item.setHidden(not match)
            if match and visible_count == 0:
                self.list_widget.setCurrentRow(i)
                visible_count += 1

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Escape:
                self.reject()
                return True
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._select_current()
                return True
            elif key == Qt.Key.Key_Down:
                cur = self.list_widget.currentRow()
                for next_r in range(cur + 1, self.list_widget.count()):
                    if not self.list_widget.item(next_r).isHidden():
                        self.list_widget.setCurrentRow(next_r)
                        break
                return True
            elif key == Qt.Key.Key_Up:
                cur = self.list_widget.currentRow()
                for prev_r in range(cur - 1, -1, -1):
                    if not self.list_widget.item(prev_r).isHidden():
                        self.list_widget.setCurrentRow(prev_r)
                        break
                return True
        return super().eventFilter(obj, event)

    def _select_current(self):
        cur_item = self.list_widget.currentItem()
        if cur_item and not cur_item.isHidden():
            self.selected_table_id = cur_item.data(Qt.ItemDataRole.UserRole)
            self.module_selected.emit(self.selected_table_id)
            self.accept()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self.selected_table_id = item.data(Qt.ItemDataRole.UserRole)
        self.module_selected.emit(self.selected_table_id)
        self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.search_edit.setFocus()
        self.search_edit.selectAll()
