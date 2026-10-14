"""
KM Layout Tables Studio - Sistem ve AutoCAD Ayarları İletişim Kutusu (SettingsDialog).
AutoCAD DXF katman isimleri, ACI renkleri (1-255), çizgi kalınlıkları ve
zadax.net canlı güncelleme kontrol tercihlerini düzenleme arayüzü.
"""
from typing import Dict, Optional
import ezdxf.colors

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap, QIcon, QPainter
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QLineEdit,
    QCheckBox, QTabWidget, QMessageBox, QInputDialog, QScrollArea
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2 import icons
from src.services.settings import SettingsManager, ACI_COLOR_NAMES
from src.services.updater import UpdateCheckWorker, UpdateInfo
from src.version import APP_VERSION, DEFAULT_UPDATE_CHECK_URL

LINEWEIGHT_OPTIONS = [
    (15, "0.15 mm (İnce ızgara)"),
    (25, "0.25 mm (Standart metin/çizgi)"),
    (35, "0.35 mm (Eskiz / belirgin)"),
    (50, "0.50 mm (Kalın çerçeve)"),
    (70, "0.70 mm (Ana dış çerçeve)"),
]


def make_color_icon(r: int, g: int, b: int, size: int = 14) -> QIcon:
    """Belirtilen RGB renk değerine sahip kare renk önizleme ikonu üretir."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(r, g, b))
    painter = QPainter(pixmap)
    painter.setPen(QColor(60, 60, 60))
    painter.drawRect(0, 0, size - 1, size - 1)
    painter.end()
    return QIcon(pixmap)


class AciColorPickerDialog(QDialog):
    """
    AutoCAD Color Index (ACI 1-255) Renk Paleti Seçici İletişim Kutusu.
    1-9 Standart renkler, 10-249 renk matrisi ve 250-255 gri tonları.
    """
    def __init__(self, current_color: int = 7, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoCAD Renk Paleti (ACI 1-255)")
        self.setFixedSize(560, 490)
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
        self.selected_color = max(1, min(255, current_color))
        self._color_buttons = {}
        self._build_ui()
        self._update_preview()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 1. Standart Renkler (1-9)
        lbl_std = QLabel("Standart Renkler (1 - 9):")
        lbl_std.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_MUTED};")
        layout.addWidget(lbl_std)

        std_row = QHBoxLayout()
        std_row.setSpacing(6)
        for aci in range(1, 10):
            btn = self._create_color_button(aci, width=52, height=26, show_num=True)
            std_row.addWidget(btn)
        layout.addLayout(std_row)

        # 2. Tam ACI Renk Matrisi (10 - 249)
        lbl_matrix = QLabel("Tam AutoCAD Renk Matrisi (ACI 10 - 249):")
        lbl_matrix.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_MUTED}; margin-top: 4px;")
        layout.addWidget(lbl_matrix)

        matrix_widget = QWidget()
        matrix_grid = QGridLayout(matrix_widget)
        matrix_grid.setContentsMargins(0, 0, 0, 0)
        matrix_grid.setSpacing(2)

        # 24 sütun x 10 satır = 240 renk (10 .. 249)
        for idx in range(10, 250):
            r_idx = (idx - 10) // 24
            c_idx = (idx - 10) % 24
            btn = self._create_color_button(idx, width=19, height=15, show_num=False)
            matrix_grid.addWidget(btn, r_idx, c_idx)
        layout.addWidget(matrix_widget)

        # 3. Gri Tonları (250 - 255)
        lbl_gray = QLabel("Gri Tonları (250 - 255):")
        lbl_gray.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.TEXT_MUTED}; margin-top: 2px;")
        layout.addWidget(lbl_gray)

        gray_row = QHBoxLayout()
        gray_row.setSpacing(6)
        for aci in range(250, 256):
            btn = self._create_color_button(aci, width=78, height=20, show_num=True)
            gray_row.addWidget(btn)
        layout.addLayout(gray_row)

        # 4. Alt Önizleme ve Eylem Çubuğu
        preview_frame = QFrame()
        preview_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        pf_layout = QHBoxLayout(preview_frame)
        pf_layout.setContentsMargins(8, 6, 8, 6)
        pf_layout.setSpacing(10)

        self.box_swatch = QLabel()
        self.box_swatch.setFixedSize(48, 28)
        self.box_swatch.setStyleSheet("border: 1px solid #ffffff; border-radius: 3px;")
        pf_layout.addWidget(self.box_swatch)

        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 12px; font-weight: 600;")
        pf_layout.addWidget(self.lbl_info, 1)

        btn_ok = QPushButton("Seç")
        btn_ok.setFixedSize(70, 28)
        btn_ok.setObjectName("primaryButton")
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
                border-radius: 4px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_PRIMARY_HOVER};
            }}
        """)
        btn_ok.clicked.connect(self.accept)
        pf_layout.addWidget(btn_ok)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedSize(70, 28)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_SECONDARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        pf_layout.addWidget(btn_cancel)

        layout.addWidget(preview_frame)

    def _create_color_button(self, aci: int, width: int, height: int, show_num: bool = False) -> QPushButton:
        rgb = ezdxf.colors.aci2rgb(aci)
        hex_color = f"#{rgb.r:02x}{rgb.g:02x}{rgb.b:02x}"
        lum = 0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b
        text_color = "#000000" if lum > 130 else "#ffffff"

        btn = QPushButton(str(aci) if show_num else "")
        btn.setFixedSize(width, height)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(f"ACI {aci} · RGB({rgb.r}, {rgb.g}, {rgb.b})")
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {hex_color};
                color: {text_color};
                border: 1px solid rgba(0, 0, 0, 0.4);
                border-radius: 2px;
                font-size: 10px;
                font-weight: 600;
                padding: 0;
            }}
            QPushButton:hover {{
                border: 1.5px solid #ffffff;
            }}
        """)
        btn.clicked.connect(lambda checked=False, c=aci: self._select_color(c))
        self._color_buttons[aci] = btn
        return btn

    def _select_color(self, aci: int):
        self.selected_color = aci
        self._update_preview()

    def _update_preview(self):
        aci = self.selected_color
        rgb = ezdxf.colors.aci2rgb(aci)
        hex_color = f"#{rgb.r:02x}{rgb.g:02x}{rgb.b:02x}"
        self.box_swatch.setStyleSheet(f"background-color: {hex_color}; border: 1.5px solid #ffffff; border-radius: 3px;")

        name_part = f" - {ACI_COLOR_NAMES[aci].split('-')[1].strip()}" if aci in ACI_COLOR_NAMES else ""
        self.lbl_info.setText(f"Renk No: {aci}{name_part} · RGB({rgb.r}, {rgb.g}, {rgb.b})")


class LinearSettingsDialog(QDialog):
    """
    Linear SaaS tasarım dilinde Ayarlar İletişim Kutusu.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KM Layout Tables Studio · Ayarlar")
        self.setMinimumSize(960, 520)
        self.resize(1020, 570)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                background-color: {theme.BG_SURFACE};
            }}
            QTabBar::tab {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_SECONDARY};
                padding: 8px 16px;
                border: 1px solid {theme.BORDER_SUBTLE};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 4px;
                font-size: 11px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: {theme.BG_SURFACE};
                color: #ffffff;
                border-color: {theme.BORDER_LIGHT};
            }}
        """)

        self.mgr = SettingsManager.get_instance()
        self.layer_editors: Dict[str, dict] = {}
        self.test_worker: Optional[UpdateCheckWorker] = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        # Üst Başlık
        lbl_head = QLabel("⚙️ Uygulama & CAD Çıktı Ayarları")
        lbl_head.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {theme.TEXT_PRIMARY};")
        root.addWidget(lbl_head)

        tabs = QTabWidget(self)

        # TAB 1: AutoCAD (DXF) Katmanları
        tab_layers = QWidget()
        l_layout = QVBoxLayout(tab_layers)
        l_layout.setContentsMargins(14, 14, 14, 14)
        l_layout.setSpacing(10)

        lbl_layers_info = QLabel(
            "Dışa aktarılan DXF çizimlerinde kullanılacak AutoCAD katman isimlerini, "
            "ACI renk kodlarını ve çizgi kalınlıklarını özelleştirin:"
        )
        lbl_layers_info.setWordWrap(True)
        lbl_layers_info.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px;")
        l_layout.addWidget(lbl_layers_info)

        self.tbl_layers = QTableWidget(6, 4, tab_layers)
        self.tbl_layers.setHorizontalHeaderLabels([
            "İşlev (Açıklama)", "Katman Adı (AutoCAD)", "Renk (ACI)", "Kalınlık"
        ])
        self.tbl_layers.verticalHeader().setVisible(False)
        self.tbl_layers.verticalHeader().setDefaultSectionSize(36)
        self.tbl_layers.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tbl_layers.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme.BG_APP};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
            }}
        """)
        h = self.tbl_layers.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tbl_layers.setColumnWidth(0, 265)
        self.tbl_layers.setColumnWidth(1, 155)
        self.tbl_layers.setColumnWidth(2, 260)
        self.tbl_layers.setColumnWidth(3, 250)

        self._populate_layers_table()
        l_layout.addWidget(self.tbl_layers)

        # Katman butonları alt satır
        layer_btn_box = QHBoxLayout()
        btn_reset_layers = QPushButton("⟲ Varsayılan GOST Katmanlarına Sıfırla")
        btn_reset_layers.setFixedHeight(28)
        btn_reset_layers.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_MUTED};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 4px;
                padding: 0 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                color: {theme.TEXT_PRIMARY};
            }}
        """)
        btn_reset_layers.clicked.connect(self._reset_layers)
        layer_btn_box.addWidget(btn_reset_layers)
        layer_btn_box.addStretch(1)
        l_layout.addLayout(layer_btn_box)

        tabs.addTab(tab_layers, "AutoCAD Katmanları")

        # TAB 2: Güncelleme & Canlı Servisler
        tab_update = QWidget()
        u_layout = QVBoxLayout(tab_update)
        u_layout.setContentsMargins(16, 16, 16, 16)
        u_layout.setSpacing(14)

        lbl_upd_info = QLabel(
            "Yazılımın yeni sürümlerini resmi Zadax platformu üzerinden otomatik denetleme tercihleri:"
        )
        lbl_upd_info.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px;")
        u_layout.addWidget(lbl_upd_info)

        self.chk_startup_update = QCheckBox("Uygulama her açıldığında arka planda otomatik güncelleme denetle")
        self.chk_startup_update.setChecked(self.mgr.get_updater_settings().check_on_startup)
        u_layout.addWidget(self.chk_startup_update)

        # Sabit Resmi Güncelleme Adresi Kartı (Kullanıcı arayüzünden gizlendi)
        self.card_server = QFrame()
        self.card_server.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        cs_layout = QVBoxLayout(self.card_server)
        cs_layout.setContentsMargins(12, 10, 12, 10)
        cs_layout.setSpacing(4)

        lbl_srv_head = QLabel("🌐 Resmi Güncelleme ve Doğrulama Adresi:")
        lbl_srv_head.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px; font-weight: 600;")
        cs_layout.addWidget(lbl_srv_head)

        lbl_srv_url = QLabel(DEFAULT_UPDATE_CHECK_URL)
        lbl_srv_url.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 12px; font-weight: 500;")
        lbl_srv_url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cs_layout.addWidget(lbl_srv_url)

        u_layout.addWidget(self.card_server)
        self.card_server.hide()

        # Geriye dönük uyumluluk ve testler için gizli QLineEdit
        self.txt_update_url = QLineEdit(DEFAULT_UPDATE_CHECK_URL)
        self.txt_update_url.hide()

        # Test Butonu ve Sonuç Rozeti (Kullanıcı arayüzünden gizlendi)
        test_row = QHBoxLayout()
        test_row.setSpacing(10)
        self.btn_test_url = QPushButton("🔗 Bağlantıyı Test Et")
        self.btn_test_url.setFixedHeight(30)
        self.btn_test_url.setStyleSheet(f"""
            QPushButton {{
                background-color: #0369a1;
                color: #ffffff;
                border: 1px solid #38bdf8;
                border-radius: 4px;
                padding: 0 14px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #0284c7;
            }}
        """)
        self.btn_test_url.clicked.connect(self._test_connection)
        test_row.addWidget(self.btn_test_url)

        self.lbl_test_result = QLabel("")
        self.lbl_test_result.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        test_row.addWidget(self.lbl_test_result, 1)
        u_layout.addLayout(test_row)

        self.btn_test_url.hide()
        self.lbl_test_result.hide()

        u_layout.addStretch(1)
        tabs.addTab(tab_update, "Güncelleme Ayarları")

        root.addWidget(tabs, 1)

        # Alt Eylem Butonları (Kaydet / İptal)
        action_bar = QHBoxLayout()
        action_bar.addStretch(1)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedHeight(32)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_SECONDARY};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_SURFACE_HOVER};
                color: {theme.TEXT_PRIMARY};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        action_bar.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Kaydet")
        btn_save.setFixedHeight(32)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #ffffff;
                border: 1px solid {theme.ACCENT_PRIMARY_HOVER};
                border-radius: 6px;
                padding: 0 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_PRIMARY_HOVER};
            }}
        """)
        btn_save.clicked.connect(self._save_settings)
        action_bar.addWidget(btn_save)

        root.addLayout(action_bar)

    def _populate_layers_table(self):
        self.tbl_layers.clearContents()
        self.layer_editors.clear()

        layer_keys = [
            ("KM_TABLO_CERCEVE", "Dış Çerçeve Çizgileri"),
            ("KM_TABLO_IZGARA", "İç Izgara Çizgileri"),
            ("KM_TABLO_METIN", "Metin ve Başlıklar"),
            ("KM_TABLO_ESKIZ", "Kesit Geometrileri"),
            ("KM_SAYFA_CERCEVE", "Pafta Dış/İç Çerçeveleri"),
            ("KM_ANTET", "Form 3 Başlık Bloğu"),
        ]

        for row, (k, desc) in enumerate(layer_keys):
            self.tbl_layers.setRowHeight(row, 36)
            cfg = self.mgr.get_layer(k)

            # 0: Açıklama
            item_desc = QTableWidgetItem(f"{desc} ({k})")
            item_desc.setFlags(item_desc.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tbl_layers.setItem(row, 0, item_desc)

            # 1: Katman Adı (QLineEdit - Geniş ve rahat imleç)
            edit_name = QLineEdit(cfg.name)
            edit_name.setFixedHeight(28)
            edit_name.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {theme.BG_SURFACE};
                    color: {theme.TEXT_PRIMARY};
                    border: 1px solid {theme.BORDER_SUBTLE};
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                }}
                QLineEdit:focus {{
                    border: 1px solid {theme.BORDER_FOCUS};
                }}
            """)
            self.tbl_layers.setCellWidget(row, 1, edit_name)

            # 2: Renk Seçici (ComboBox + Renk Swatch + 255 Renk Palet Butonu)
            w_color = QWidget()
            wc_layout = QHBoxLayout(w_color)
            wc_layout.setContentsMargins(0, 4, 0, 4)
            wc_layout.setSpacing(6)

            cb_color = QComboBox()
            cb_color.setFixedHeight(28)
            cb_color.setStyleSheet(f"""
                QComboBox {{
                    background-color: {theme.BG_SURFACE};
                    color: {theme.TEXT_PRIMARY};
                    border: 1px solid {theme.BORDER_SUBTLE};
                    border-radius: 4px;
                    padding: 2px 20px 2px 6px;
                    font-size: 11px;
                }}
            """)

            # Standart ACI renkleri ekle
            for aci, cname in ACI_COLOR_NAMES.items():
                rgb = ezdxf.colors.aci2rgb(aci)
                cb_color.addItem(make_color_icon(rgb.r, rgb.g, rgb.b), cname, aci)

            # Eğer seçili renk standart 1-9 dışında ise listeye ekle
            idx = cb_color.findData(cfg.color)
            if idx >= 0:
                cb_color.setCurrentIndex(idx)
            else:
                rgb = ezdxf.colors.aci2rgb(cfg.color)
                cb_color.addItem(make_color_icon(rgb.r, rgb.g, rgb.b), f"{cfg.color} - Özel Palet", cfg.color)
                cb_color.setCurrentIndex(cb_color.count() - 1)

            wc_layout.addWidget(cb_color, 1)

            btn_palette = QPushButton()
            btn_palette.setFixedSize(28, 28)
            btn_palette.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_palette.setToolTip("AutoCAD 255 Renk Paletinden Seç...")
            btn_palette.setIcon(icons.get_icon("fa5s.palette", color="#ffffff"))
            btn_palette.setIconSize(icons.icon_size(14))
            btn_palette.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.BG_SURFACE};
                    border: 1px solid {theme.BORDER_SUBTLE};
                    border-radius: 4px;
                    padding: 0;
                }}
                QPushButton:hover {{
                    background-color: {theme.BG_SURFACE_HOVER};
                    border-color: {theme.ACCENT_PRIMARY};
                }}
            """)
            btn_palette.clicked.connect(lambda checked=False, cb=cb_color: self._open_palette(cb))
            wc_layout.addWidget(btn_palette, 0)

            self.tbl_layers.setCellWidget(row, 2, w_color)

            # 3: Çizgi Kalınlığı (ComboBox + Özel Kalınlık Seçeneği)
            cb_weight = QComboBox()
            cb_weight.setFixedHeight(28)
            cb_weight.setStyleSheet(f"""
                QComboBox {{
                    background-color: {theme.BG_SURFACE};
                    color: {theme.TEXT_PRIMARY};
                    border: 1px solid {theme.BORDER_SUBTLE};
                    border-radius: 4px;
                    padding: 2px 20px 2px 6px;
                    font-size: 11px;
                }}
            """)
            for val, wtext in LINEWEIGHT_OPTIONS:
                cb_weight.addItem(wtext, val)

            # Özel kalınlık öğesini ekle
            cb_weight.addItem("📐 Özel Kalınlık...", -1)

            w_idx = cb_weight.findData(cfg.lineweight)
            if w_idx >= 0:
                cb_weight.setCurrentIndex(w_idx)
            else:
                custom_label = f"{cfg.lineweight / 100:.2f} mm (Özel)"
                cb_weight.insertItem(cb_weight.count() - 1, custom_label, cfg.lineweight)
                cb_weight.setCurrentIndex(cb_weight.count() - 2)

            cb_weight._prev_index = cb_weight.currentIndex()
            cb_weight.currentIndexChanged.connect(lambda idx, cb=cb_weight: self._on_lineweight_changed(cb))
            self.tbl_layers.setCellWidget(row, 3, cb_weight)

            self.layer_editors[k] = {
                "name_edit": edit_name,
                "color_cb": cb_color,
                "weight_cb": cb_weight
            }

    def _open_palette(self, cb_color: QComboBox):
        curr_color = cb_color.currentData() or 7
        dlg = AciColorPickerDialog(current_color=curr_color, parent=self)
        if dlg.exec():
            chosen = dlg.selected_color
            idx = cb_color.findData(chosen)
            if idx >= 0:
                cb_color.setCurrentIndex(idx)
            else:
                rgb = ezdxf.colors.aci2rgb(chosen)
                icon = make_color_icon(rgb.r, rgb.g, rgb.b)
                cb_color.addItem(icon, f"{chosen} - ACI Renk", chosen)
                cb_color.setCurrentIndex(cb_color.count() - 1)

    def _on_lineweight_changed(self, cb_weight: QComboBox):
        data = cb_weight.currentData()
        if data == -1:
            val, ok = QInputDialog.getDouble(
                self,
                "Özel Çizgi Kalınlığı",
                "AutoCAD Çizgi Kalınlığı (mm):",
                0.40, 0.05, 5.0, 2
            )
            if ok:
                val_int = int(round(val * 100))
                label = f"{val:.2f} mm (Özel)"
                idx = cb_weight.findData(val_int)
                if idx >= 0:
                    cb_weight.setCurrentIndex(idx)
                else:
                    insert_idx = max(0, cb_weight.count() - 1)
                    cb_weight.insertItem(insert_idx, label, val_int)
                    cb_weight.setCurrentIndex(insert_idx)
                cb_weight._prev_index = cb_weight.currentIndex()
            else:
                prev_idx = getattr(cb_weight, "_prev_index", 0)
                cb_weight.blockSignals(True)
                cb_weight.setCurrentIndex(prev_idx)
                cb_weight.blockSignals(False)
        else:
            cb_weight._prev_index = cb_weight.currentIndex()

    def _reset_layers(self):
        reply = QMessageBox.question(
            self,
            "Katmanları Sıfırla",
            "Tüm AutoCAD katman adları ve renkleri standart ГОСТ değerlerine sıfırlansın mı?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.mgr.reset_layers_to_default()
            self._populate_layers_table()

    def _test_connection(self):
        url = DEFAULT_UPDATE_CHECK_URL
        self.btn_test_url.setEnabled(False)
        self.lbl_test_result.setText("⏳ Resmi sunucu kontrol ediliyor...")
        self.lbl_test_result.setStyleSheet(f"color: {theme.COLOR_INFO};")

        self.test_worker = UpdateCheckWorker(check_url=url, current_version=APP_VERSION, parent=self)
        self.test_worker.check_completed.connect(self._on_test_success)
        self.test_worker.check_failed.connect(self._on_test_failed)
        self.test_worker.start()

    def _on_test_success(self, info: UpdateInfo):
        self.btn_test_url.setEnabled(True)
        self.lbl_test_result.setText(f"✓ Başarılı: Sürüm v{info.version} tespit edildi.")
        self.lbl_test_result.setStyleSheet(f"color: {theme.COLOR_SUCCESS}; font-weight: 600;")

    def _on_test_failed(self, error: str):
        self.btn_test_url.setEnabled(True)
        self.lbl_test_result.setText(f"⚠️ Hata: {error}")
        self.lbl_test_result.setStyleSheet(f"color: {theme.COLOR_WARNING};")

    def _save_settings(self):
        # 1. Katmanları kaydet
        for k, widgets in self.layer_editors.items():
            name = widgets["name_edit"].text().strip()
            color = int(widgets["color_cb"].currentData())
            weight = int(widgets["weight_cb"].currentData())
            if not name:
                name = k
            self.mgr.set_layer(k, name, color, weight)

        # 2. Güncelleme tercihlerini kaydet (URL daima sabit resmi adrestir)
        chk = self.chk_startup_update.isChecked()
        self.mgr.set_updater_settings(chk, DEFAULT_UPDATE_CHECK_URL)

        self.accept()
