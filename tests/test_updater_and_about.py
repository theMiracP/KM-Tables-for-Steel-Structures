"""
Test Suite: Zadax.net Versiyon Kontrol Servisi ve Hakkında (About) Diyaloğu Testleri.
Manuel web indirme ve güncelleme bildirim mimarisini doğrular.
"""
import json
from unittest.mock import patch, MagicMock
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from src.version import (
    APP_VERSION, COMPANY_WEBSITE, COMPANY_DISPLAY_URL,
    DEFAULT_UPDATE_CHECK_URL
)
from src.services.updater import (
    parse_version, is_version_newer, UpdateInfo,
    UpdateCheckWorker
)
from src.ui_v2.about_dialog import LinearAboutDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_version_metadata():
    """Temel sürüm ve zadax.net firma bilgilerinin doğruluğu."""
    assert APP_VERSION == "1.4.0"
    assert "zadax.net" in COMPANY_WEBSITE
    assert COMPANY_DISPLAY_URL == "www.zadax.net"
    assert "zadax.net" in DEFAULT_UPDATE_CHECK_URL


def test_parse_version_and_comparison():
    """Sürüm ayrıştırma ve semantik karşılaştırma mantığı."""
    assert parse_version("1.3.0") == (1, 3, 0)
    assert parse_version("v1.3.5") == (1, 3, 5)
    assert parse_version("2.0") == (2, 0)
    assert parse_version("") == (0, 0, 0)

    # Karşılaştırmalar
    assert is_version_newer("1.4.0", "1.3.0") is True
    assert is_version_newer("1.3.0", "1.3.0") is False
    assert is_version_newer("1.2.9", "1.3.0") is False
    # String sıralama tuzağı: 1.10.0 > 1.3.0 olmalıdır
    assert is_version_newer("1.10.0", "1.3.0") is True
    assert is_version_newer("2.0.0", "1.99.99") is True


def test_update_check_worker_success():
    """Zadax.net üzerinden güncelleme kontrolü başarılı yanıt senaryosu."""
    payload = {
        "version": "1.4.0",
        "release_date": "2026-10-15",
        "product_url": "https://www.zadax.net/urun/km-layout-tables",
        "changelog": "Yeni çelik profiller eklendi."
    }
    mock_bytes = json.dumps(payload).encode("utf-8")

    worker = UpdateCheckWorker(check_url="https://www.zadax.net/version.json", current_version="1.3.0")

    result_info = []
    worker.check_completed.connect(lambda info: result_info.append(info))

    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_bytes
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        worker.run()

    assert len(result_info) == 1
    info = result_info[0]
    assert info.version == "1.4.0"
    assert info.is_newer is True
    assert info.product_url == "https://www.zadax.net/urun/km-layout-tables"
    assert info.changelog == "Yeni çelik profiller eklendi."


def test_update_check_worker_html_product_page():
    """Zadax.net HTML ürün sayfasından softwareVersion ve link ayrıştırma testi."""
    html_mock = """
    <!DOCTYPE html>
    <html>
    <head>
      <script type="application/ld+json">
      {
        "@type": "SoftwareApplication",
        "softwareVersion": "v1.4.0",
        "offers": { "url": "https://zadax.net/tr/products/km-tables-studio-celik-yap-tablolar-ve-dxf-uretici/" }
      }
      </script>
    </head>
    <body>
       <h1>KM Tables Studio</h1>
    </body>
    </html>
    """
    worker = UpdateCheckWorker(check_url=DEFAULT_UPDATE_CHECK_URL, current_version="1.3.0")
    mock_resp = MagicMock()
    mock_resp.read.return_value = html_mock.encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    result_info = []
    worker.check_completed.connect(lambda info: result_info.append(info))

    with patch("urllib.request.urlopen", return_value=mock_resp):
        worker.run()

    assert len(result_info) == 1
    info = result_info[0]
    assert info.version == "1.4.0"
    assert info.is_newer is True
    assert info.product_url == DEFAULT_UPDATE_CHECK_URL


def test_update_check_worker_failure():
    """Zadax.net sunucusuna ulaşılamadığında hata sinyali üretimi."""
    import urllib.error
    worker = UpdateCheckWorker(check_url="https://www.zadax.net/version.json")

    errors = []
    worker.check_failed.connect(lambda err: errors.append(err))

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        worker.run()

    assert len(errors) == 1
    assert "zadax.net sunucusuna bağlanılamadı" in errors[0]


def test_about_dialog_ui(qapp):
    """About penceresinde www.zadax.net ibaresi ve manuel yönlendirme akışı doğrulaması."""
    dialog = LinearAboutDialog(update_check_url="https://www.zadax.net/version.json")

    # www.zadax.net ibaresi ekranda mevcut mu?
    assert "www.zadax.net" in dialog.btn_web_link.text()

    # Başlangıçta yeni sürüm aksiyon çerçevesi gizli olmalı
    assert dialog.btn_check_update.isEnabled()
    assert not dialog.new_version_frame.isVisible()

    # Sahte yeni sürüm sinyali gönderelim (QMessageBox Yes yanıtı ile mock'layalım)
    fake_update = UpdateInfo(
        version="1.4.0",
        release_date="2026-10-15",
        product_url="https://www.zadax.net/urun/km-layout-tables",
        changelog="Hata düzeltmeleri",
        is_newer=True
    )

    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No):
        dialog._on_check_completed(fake_update)

    dialog.show()
    # Eylem çerçevesinin görünür olduğunu ve zadax.net ürün sayfası butonunun olduğunu doğrula
    assert not dialog.new_version_frame.isHidden()
    assert not dialog.btn_open_product_page.isHidden()
    assert "zadax.net" in dialog.btn_open_product_page.text()
    assert "Yeni sürüm mevcut: v1.4.0" in dialog.lbl_update_status.text()

    # Ürün sayfasına git butonu tıklandığında URL açma çağrısı
    with patch.object(dialog, "_open_external_url") as mock_open:
        dialog._open_update_link()
        mock_open.assert_called_once_with("https://www.zadax.net/urun/km-layout-tables")

    # Kapat butonu ve X pencere kapama davranışı doğrulaması
    dialog.reject()
    assert not dialog.isVisible()
