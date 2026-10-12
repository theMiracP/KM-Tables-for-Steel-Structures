"""
KM Layout Tables Studio - Şablon Kaydetme ve Yükleme İletişim Kutuları (PresetDialog).
Kullanıcının tabloları preset olarak kaydetmesini, projeler arasında tekrar kullanmasını sağlar.
"""
from typing import Optional, Any
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2 import icons
from src.services.preset_manager import PresetManager, PresetMetadata


class SavePresetDialog(QDialog):
    """
    Mevcut tablo durumunu yeni bir şablon / preset olarak kaydetme penceresi.
    """
    def __init__(self, module_id: str, document: Any, parent=None):
        super().__init__(parent)
        self.module_id = module_id
        self.document = document
        self.mgr = PresetManager.get_instance()

        self.setWindowTitle("Tabloyu Şablon Olarak Kaydet")
        self.setFixedSize(450, 260)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
            }}
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        lbl_title = QLabel("💾 Yeni Tablo Şablonu Kaydet")
        lbl_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {theme.TEXT_PRIMARY};")
        layout.addWidget(lbl_title)

        lbl_info = QLabel("Bu tablonun içeriğini gelecekteki projelerde tekrar kullanmak üzere şablon olarak saklayın:")
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_SECONDARY};")
        layout.addWidget(lbl_info)

        # Şablon Adı
        lbl_name = QLabel("Şablon Adı:")
        lbl_name.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_MUTED};")
        layout.addWidget(lbl_name)

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Örn: Standart Fabrika Kolonları, Tipik Form 3 vb.")
        self.txt_name.setFixedHeight(30)
        self.txt_name.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 0 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {theme.ACCENT_PRIMARY};
            }}
        """)
        layout.addWidget(self.txt_name)

        # Açıklama / Not
        lbl_desc = QLabel("Açıklama (İsteğe bağlı):")
        lbl_desc.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        layout.addWidget(lbl_desc)

        self.txt_desc = QLineEdit()
        self.txt_desc.setPlaceholderText("Örn: 2026 Çelik Atölyesi Projesi temel elemanları")
        self.txt_desc.setFixedHeight(28)
        self.txt_desc.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 0 8px;
                font-size: 11px;
            }}
        """)
        layout.addWidget(self.txt_desc)

        layout.addStretch(1)

        # Butonlar
        btn_bar = QHBoxLayout()
        btn_bar.addStretch(1)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedHeight(30)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_SECONDARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 0 14px;
                font-size: 11px;
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_bar.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Kaydet")
        btn_save.setFixedHeight(30)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
                border: 1px solid {theme.ACCENT_PRIMARY_HOVER};
                border-radius: 4px;
                padding: 0 18px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_PRIMARY_HOVER};
            }}
        """)
        btn_save.clicked.connect(self._save)
        btn_bar.addWidget(btn_save)

        layout.addLayout(btn_bar)

    def _save(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Hata", "Lütfen şablon için bir isim girin.")
            return

        desc = self.txt_desc.text().strip()
        try:
            self.mgr.save_preset(self.module_id, name, self.document, description=desc)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Şablon kaydedilemedi: {e}")


class LoadPresetDialog(QDialog):
    """
    Kayıtlı şablonları listeleme, seçme ve aktif tabloya aktarma penceresi.
    """
    def __init__(self, module_id: str, parent=None):
        super().__init__(parent)
        self.module_id = module_id
        self.mgr = PresetManager.get_instance()
        self.loaded_document: Optional[Any] = None

        self.setWindowTitle("Tablo Şablonu Yükle")
        self.setFixedSize(620, 420)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
            }}
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        lbl_head = QLabel("📂 Kayıtlı Şablonlar / Önayarlar")
        lbl_head.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {theme.TEXT_PRIMARY};")
        layout.addWidget(lbl_head)

        lbl_sub = QLabel("Bu tablo için daha önce kaydettiğiniz şablonlardan birini seçin:")
        lbl_sub.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_SECONDARY};")
        layout.addWidget(lbl_sub)

        # Tablo Listesi
        self.tbl_presets = QTableWidget(0, 4, self)
        self.tbl_presets.setHorizontalHeaderLabels([
            "Şablon Adı", "Kayıt Tarihi", "Öğe Sayısı", "Açıklama"
        ])
        self.tbl_presets.verticalHeader().setVisible(False)
        self.tbl_presets.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_presets.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tbl_presets.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
            }}
        """)
        h = self.tbl_presets.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self._populate_presets()
        layout.addWidget(self.tbl_presets, 1)

        # Butonlar
        btn_bar = QHBoxLayout()

        btn_delete = QPushButton("🗑️ Seçiliyi Sil")
        btn_delete.setFixedHeight(30)
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_APP};
                color: {theme.COLOR_ERROR};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.COLOR_ERROR_BG};
            }}
        """)
        btn_delete.clicked.connect(self._delete_selected)
        btn_bar.addWidget(btn_delete)

        btn_import_file = QPushButton("📁 JSON Dosyasından Yükle...")
        btn_import_file.setFixedHeight(30)
        btn_import_file.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_MUTED};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                color: {theme.TEXT_PRIMARY};
            }}
        """)
        btn_import_file.clicked.connect(self._import_from_file)
        btn_bar.addWidget(btn_import_file)

        btn_bar.addStretch(1)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedHeight(30)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_SECONDARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 0 14px;
                font-size: 11px;
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_bar.addWidget(btn_cancel)

        btn_load = QPushButton("📂 Şablonu Uygula")
        btn_load.setFixedHeight(30)
        btn_load.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
                border: 1px solid {theme.ACCENT_PRIMARY_HOVER};
                border-radius: 4px;
                padding: 0 18px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_PRIMARY_HOVER};
            }}
        """)
        btn_load.clicked.connect(self._load_selected)
        btn_bar.addWidget(btn_load)

        layout.addLayout(btn_bar)

    def _populate_presets(self):
        self.tbl_presets.setRowCount(0)
        presets = self.mgr.list_presets(self.module_id)
        self.preset_list = presets

        self.tbl_presets.setRowCount(len(presets))
        for r, p in enumerate(presets):
            item_name = QTableWidgetItem(f"📄 {p.name}")
            item_date = QTableWidgetItem(p.created_at)
            item_count = QTableWidgetItem(str(p.item_count) if p.item_count > 0 else "-")
            item_desc = QTableWidgetItem(p.description)

            for it in (item_name, item_date, item_count, item_desc):
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.tbl_presets.setItem(r, 0, item_name)
            self.tbl_presets.setItem(r, 1, item_date)
            self.tbl_presets.setItem(r, 2, item_count)
            self.tbl_presets.setItem(r, 3, item_desc)

        if len(presets) > 0:
            self.tbl_presets.selectRow(0)

    def _delete_selected(self):
        row = self.tbl_presets.currentRow()
        if row < 0 or row >= len(self.preset_list):
            return
        preset = self.preset_list[row]
        reply = QMessageBox.question(
            self,
            "Şablonu Sil",
            f"'{preset.name}' şablonunu silmek istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.mgr.delete_preset(self.module_id, preset.name)
            self._populate_presets()

    def _import_from_file(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self,
            "Şablon JSON Dosyası Seç",
            os.getcwd(),
            "JSON Dosyaları (*.json)"
        )
        if not fpath:
            return
        try:
            self.loaded_document = self.mgr.load_preset(self.module_id, fpath)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya yüklenemedi: {e}")

    def _load_selected(self):
        row = self.tbl_presets.currentRow()
        if row < 0 or row >= len(self.preset_list):
            QMessageBox.warning(self, "Seçim Yapılmadı", "Lütfen listeden bir şablon seçin.")
            return

        preset = self.preset_list[row]
        try:
            self.loaded_document = self.mgr.load_preset(self.module_id, preset.name)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Şablon yüklenemedi: {e}")
