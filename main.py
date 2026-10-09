"""
KM Tablo Oluşturucu - Başlatıcı (Main Entry Point).
Rusya GOST Çelik Konstrüksiyon (KM) Projeleri İçin Mühendislik Tablo Yardımcısı.
"""
import sys
import os
import ctypes

# Proje kök dizinini sys.path'e ekle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from src.ui_v2 import KmLinearMainWindow

def main():
    # Windows Taskbar özel ikon eşlemesi (AppUserModelID)
    try:
        myappid = "zadax.kmlayouttables.studio.1.2.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("KM Layout Tables Studio")
    app.setOrganizationName("Zadax")

    # İkon tanımlaması
    icon_path = os.path.join(BASE_DIR, "assets", "app_icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(BASE_DIR, "assets", "app_icon.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    else:
        app_icon = None

    window = KmLinearMainWindow()
    if app_icon:
        window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
