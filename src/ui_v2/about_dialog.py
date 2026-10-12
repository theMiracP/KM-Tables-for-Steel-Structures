"""
KM Tablo Oluşturucu - "Hakkında" (About) İletişim Kutusu (AboutDialog).
GOST standartları, sürüm bilgisi, zadax.net web bağlantısı ve canlı versiyon kontrol bildirim motoru.
"""
import os
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QMessageBox
)
from src.ui_v2 import theme_linear as theme
from src.ui_v2 import icons
from src.version import (
    APP_NAME, APP_VERSION, COMPANY_NAME, COMPANY_WEBSITE, COMPANY_DISPLAY_URL,
    DEFAULT_UPDATE_CHECK_URL
)
from src.services.updater import (
    UpdateCheckWorker, UpdateInfo
)


class LinearAboutDialog(QDialog):
    """
    Linear SaaS tasarım diline uygun 'Hakkında' ve zadax.net Versiyon Kontrol penceresi.
    Otomatik indirme yapmaz; yeni sürüm çıktığında kullanıcıya bilgi verir ve zadax.net ürün sayfasına yönlendirir.
    """
    def __init__(self, parent=None, update_check_url: str = DEFAULT_UPDATE_CHECK_URL):
        super().__init__(parent)
        self.update_check_url = update_check_url
        self.check_worker = None
        self.latest_update_info: UpdateInfo = None

        self.setWindowTitle("KM Layout Tables Studio · Hakkında")
        self.setFixedSize(540, 500)
        # Windows başlık çubuğunda kapatma (X) butonunun kesinlikle aktif ve çalışır olması için flagler
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
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # 1. Başlık & Rozet & zadax.net Kartı
        header_frame = QFrame(self)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        hf_layout = QHBoxLayout(header_frame)
        hf_layout.setContentsMargins(8, 8, 8, 8)
        hf_layout.setSpacing(14)

        # Marka / Şirket Logosu (Zadax Logo)
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "zadax_logo.png")
        logo_loaded = False
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            if not pix.isNull():
                lbl_logo = QLabel()
                lbl_logo.setFixedSize(56, 56)
                lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
                scaled_pix = pix.scaled(
                    48, 48,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                lbl_logo.setPixmap(scaled_pix)
                lbl_logo.setStyleSheet(f"""
                    background-color: #101116;
                    border: 1px solid {theme.BORDER_LIGHT};
                    border-radius: 8px;
                    padding: 2px;
                """)
                hf_layout.addWidget(lbl_logo)
                logo_loaded = True

        if not logo_loaded:
            lbl_icon = QLabel("📐")
            lbl_icon.setStyleSheet("font-size: 36px; background: transparent;")
            hf_layout.addWidget(lbl_icon)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        lbl_title = QLabel(APP_NAME)
        lbl_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {theme.TEXT_PRIMARY};
            background: transparent;
        """)
        text_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel(f"Sürüm {APP_VERSION} · Linear / Notion SaaS CAD Mimarisi")
        lbl_subtitle.setStyleSheet(f"""
            font-size: 11px;
            color: {theme.TEXT_SECONDARY};
            background: transparent;
        """)
        text_layout.addWidget(lbl_subtitle)

        # zadax.net Web Bağlantısı
        web_container = QHBoxLayout()
        web_container.setSpacing(6)
        web_container.setContentsMargins(0, 4, 0, 0)

        lbl_web_prefix = QLabel("Resmi Web Sitesi:")
        lbl_web_prefix.setStyleSheet(f"""
            font-size: 11px;
            color: {theme.TEXT_MUTED};
            background: transparent;
        """)
        web_container.addWidget(lbl_web_prefix)

        self.btn_web_link = QPushButton(f" {COMPANY_DISPLAY_URL}")
        self.btn_web_link.setIcon(icons.get_icon(icons.ICON_GLOBE, color=icons.COLOR_WHITE))
        self.btn_web_link.setIconSize(icons.icon_size(14))
        self.btn_web_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_web_link.setStyleSheet(f"""
            QPushButton {{
                background-color: #0369a1;
                color: #ffffff;
                border: 1px solid #38bdf8;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
                padding: 3px 8px;
            }}
            QPushButton:hover {{
                background-color: #0284c7;
                border-color: #ffffff;
                color: #ffffff;
            }}
        """)
        self.btn_web_link.clicked.connect(lambda: self._open_external_url(COMPANY_WEBSITE))
        web_container.addWidget(self.btn_web_link)
        web_container.addStretch(1)

        text_layout.addLayout(web_container)
        hf_layout.addLayout(text_layout)
        hf_layout.addStretch(1)

        layout.addWidget(header_frame)

        # 2. Canlı Versiyon Kontrol Kartı (zadax.net Entegrasyonu)
        update_frame = QFrame(self)
        update_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        uf_layout = QVBoxLayout(update_frame)
        uf_layout.setContentsMargins(10, 10, 10, 10)
        uf_layout.setSpacing(8)

        # Güncelleme Üst Satırı: Durum Metni ve Denetle Butonu
        update_top_bar = QHBoxLayout()
        update_top_bar.setSpacing(10)

        self.lbl_update_status = QLabel("Versiyon kontrolü zadax.net üzerinden sağlanır.")
        self.lbl_update_status.setWordWrap(True)
        self.lbl_update_status.setStyleSheet(f"""
            font-size: 11px;
            color: {theme.TEXT_SECONDARY};
            background: transparent;
        """)
        update_top_bar.addWidget(self.lbl_update_status, 1)

        self.btn_check_update = QPushButton(" Güncellemeleri Denetle")
        self.btn_check_update.setIcon(icons.get_icon(icons.ICON_SYNC, color=icons.COLOR_WHITE))
        self.btn_check_update.setIconSize(icons.icon_size(14))
        self.btn_check_update.setFixedHeight(30)
        self.btn_check_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_update.setStyleSheet(f"""
            QPushButton {{
                background-color: #4338ca;
                color: #ffffff;
                border: 1px solid #6366f1;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #4f46e5;
                border-color: #a5b4fc;
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background-color: #3730a3;
            }}
            QPushButton:disabled {{
                background-color: #1e1b4b;
                color: #6b7280;
                border-color: #312e81;
            }}
        """)
        self.btn_check_update.clicked.connect(self.check_for_updates)
        update_top_bar.addWidget(self.btn_check_update)

        uf_layout.addLayout(update_top_bar)

        # Yeni Sürüm Tespit Edildiğinde Görünen Eylem Paneli (Başlangıçta Gizli)
        self.new_version_frame = QFrame()
        self.new_version_frame.setVisible(False)
        self.new_version_frame.setStyleSheet("background: transparent; border: none;")
        nv_layout = QVBoxLayout(self.new_version_frame)
        nv_layout.setContentsMargins(0, 4, 0, 0)
        nv_layout.setSpacing(6)

        self.lbl_update_note = QLabel("")
        self.lbl_update_note.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED}; background: transparent;")
        self.lbl_update_note.setWordWrap(True)
        nv_layout.addWidget(self.lbl_update_note)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self.btn_open_product_page = QPushButton(" zadax.net'te Ürün Sayfasını Aç (İndir)")
        self.btn_open_product_page.setIcon(icons.get_icon(icons.ICON_EXTERNAL_LINK, color=icons.COLOR_WHITE))
        self.btn_open_product_page.setIconSize(icons.icon_size(14))
        self.btn_open_product_page.setFixedHeight(28)
        self.btn_open_product_page.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_product_page.setStyleSheet(f"""
            QPushButton {{
                background-color: #047857;
                color: #ffffff;
                border: 1px solid #10b981;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #059669;
                border-color: #6ee7b7;
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background-color: #065f46;
            }}
        """)
        self.btn_open_product_page.clicked.connect(self._open_update_link)
        action_row.addWidget(self.btn_open_product_page)

        action_row.addStretch(1)
        nv_layout.addLayout(action_row)

        uf_layout.addWidget(self.new_version_frame)

        layout.addWidget(update_frame)

        # 3. Standartlar & Teknik Detaylar Kartı
        info_frame = QFrame(self)
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel {{
                background: transparent;
                color: {theme.TEXT_SECONDARY};
                font-size: 11px;
                line-height: 1.4;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(6)

        lbl_info = QLabel(
            "<b>Desteklenen GOST Standartları:</b><br>"
            "• <b>ГОСТ 21.502-2007:</b> Çelik Yapı Eleman Listeleri (Ведомость элементов)<br>"
            "• <b>ГОСТ Р 21.101-2020 / ГОСТ 2.301:</b> Pafta Boyutları ve Form 3 Ana Antet (185 × 55 mm)<br>"
            "• <b>ГОСТ 2.302-68:</b> 1:1 Ölçekli Metrik Çizimler ($INSUNITS = 4)<br><br>"
            "<b>CAD & DXF Çekirdeği:</b><br>"
            "• Bağımsız <b>ezdxf R2010</b> motoru (AutoCAD lisansı gerektirmez)<br>"
            "• Katmanlı DXF çıktısı ve UTF-8 Kiril metin desteği<br>"
            "• Sağ alt köşeye kilitli Form 3 antet yerleşimi<br>"
            "• Donanım hızlandırmalı 2D vektörel önizleme tuvali"
        )
        lbl_info.setWordWrap(True)
        info_layout.addWidget(lbl_info)
        layout.addWidget(info_frame)

        layout.addStretch(1)

        # 4. Alt Kapat Butonu (Belirgin ve Şık Eylem Butonu)
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 0, 0, 0)
        bottom_bar.addStretch(1)

        self.btn_close = QPushButton(" Kapat", self)
        self.btn_close.setIcon(icons.get_icon(icons.ICON_CLOSE, color=icons.COLOR_WHITE))
        self.btn_close.setIconSize(icons.icon_size(14))
        self.btn_close.setFixedHeight(34)
        self.btn_close.setMinimumWidth(130)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: #334155;
                color: #f8fafc;
                border: 1px solid #64748b;
                border-radius: 6px;
                padding: 0 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
                border-color: #ef4444;
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background-color: #b91c1c;
            }}
        """)
        self.btn_close.clicked.connect(self.reject)
        bottom_bar.addWidget(self.btn_close)
        bottom_bar.addStretch(1)
        layout.addLayout(bottom_bar)

    def _open_external_url(self, url: str):
        """Kullanıcının varsayılan tarayıcısında verilen URL'yi açar."""
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def check_for_updates(self):
        """zadax.net üzerinden arka planda versiyon kontrolü başlatır."""
        self.btn_check_update.setEnabled(False)
        self.lbl_update_status.setText("⏳ zadax.net üzerinden versiyon kontrol ediliyor...")
        self.lbl_update_status.setStyleSheet(f"font-size: 11px; color: {theme.COLOR_INFO}; background: transparent;")
        self.new_version_frame.setVisible(False)

        self.check_worker = UpdateCheckWorker(
            check_url=self.update_check_url,
            current_version=APP_VERSION,
            parent=self
        )
        self.check_worker.check_completed.connect(self._on_check_completed)
        self.check_worker.check_failed.connect(self._on_check_failed)
        self.check_worker.start()

    def _on_check_completed(self, info: UpdateInfo):
        self.btn_check_update.setEnabled(True)
        self.latest_update_info = info

        if info.is_newer:
            status_txt = f"🚀 <b>Yeni sürüm mevcut: v{info.version}</b>"
            if info.release_date:
                status_txt += f" ({info.release_date})"
            self.lbl_update_status.setText(status_txt)
            self.lbl_update_status.setStyleSheet(f"font-size: 11px; color: {theme.COLOR_SUCCESS}; background: transparent;")

            note_txt = "Yeni sürümü zadax.net üzerinden manuel olarak indirebilirsiniz."
            if info.changelog:
                note_txt += f"\nSürüm Notu: {info.changelog}"
            self.lbl_update_note.setText(note_txt)
            self.new_version_frame.setVisible(True)

            # Kullanıcıya web sayfasını açmak isteyip istemediğini sor
            reply = QMessageBox.question(
                self,
                "Yeni Sürüm Güncellemesi",
                f"KM Studio için yeni bir sürüm yayınlandı (v{info.version})!\n\n"
                f"Güncellemeyi indirmek için zadax.net ürün sayfasını açmak ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._open_update_link()
        else:
            self.lbl_update_status.setText(f"✓ <b>Yazılımınız güncel!</b> (Mevcut: v{APP_VERSION})")
            self.lbl_update_status.setStyleSheet(f"font-size: 11px; color: {theme.COLOR_SUCCESS}; background: transparent;")
            self.new_version_frame.setVisible(False)

    def _on_check_failed(self, error_message: str):
        self.btn_check_update.setEnabled(True)
        self.lbl_update_status.setText(f"⚠️ Kontrol edilemedi: {error_message}")
        self.lbl_update_status.setStyleSheet(f"font-size: 11px; color: {theme.COLOR_WARNING}; background: transparent;")
        self.new_version_frame.setVisible(False)

    def _open_update_link(self):
        """zadax.net ürün veya indirme sayfasını kullanıcının tarayıcısında açar."""
        target_url = COMPANY_WEBSITE
        if self.latest_update_info and self.latest_update_info.product_url:
            target_url = self.latest_update_info.product_url
        self._open_external_url(target_url)

    def reject(self):
        """Esc veya X butonu ile kapatıldığında temiz çıkış."""
        if self.check_worker and self.check_worker.isRunning():
            self.check_worker.cancel()
            self.check_worker.wait(300)
        super().reject()

    def closeEvent(self, event):
        """Pencere kapatma olayını kabul et ve modal döngüyü sonlandır."""
        if self.check_worker and self.check_worker.isRunning():
            self.check_worker.cancel()
            self.check_worker.wait(300)
        event.accept()
        super().closeEvent(event)
