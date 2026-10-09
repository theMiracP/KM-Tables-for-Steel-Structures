"""
KM Tablo Oluşturucu - Başlatıcı (Main Entry Point).
Rusya GOST Çelik Konstrüksiyon (KM) Projeleri İçin Mühendislik Tablo Yardımcısı.
"""
import sys
import os

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.ui_v2 import KmLinearMainWindow

def main():
    # Windows High-DPI netlik ayarları
    app = QApplication(sys.argv)
    app.setApplicationName("KM Tablo Oluşturucu")
    app.setOrganizationName("KM CAD Tools")

    window = KmLinearMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
