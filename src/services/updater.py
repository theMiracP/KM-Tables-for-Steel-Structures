"""
KM Layout Tables Studio - Sürüm Güncelleme Bildirim Servisi (Version Checker).
zadax.net üzerinden en son sürüm bilgisini kontrol eder ve kullanıcıya web üzerinden indirme bağlantısını sunar.
"""
import re
import json
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Tuple

from PySide6.QtCore import QThread, Signal
from src.version import APP_VERSION, DEFAULT_UPDATE_CHECK_URL, COMPANY_WEBSITE


def parse_version(version_str: str) -> Tuple[int, ...]:
    """
    Sürüm dizgisini karşılaştırılabilir tamsayı demetine (tuple) dönüştürür.
    Örnek: '1.2.0' -> (1, 2, 0), 'v1.3.5' -> (1, 3, 5)
    """
    if not version_str:
        return (0, 0, 0)
    matches = re.findall(r"\d+", version_str.strip())
    if not matches:
        return (0, 0, 0)
    return tuple(int(x) for x in matches)


def is_version_newer(remote_version: str, local_version: str = APP_VERSION) -> bool:
    """
    Uzak sürümün yerel sürümden daha yeni olup olmadığını belirler.
    """
    return parse_version(remote_version) > parse_version(local_version)


@dataclass
class UpdateInfo:
    """
    zadax.net güncelleme sunucusundan dönen sürüm bilgileri.
    """
    version: str
    release_date: str = ""
    product_url: str = COMPANY_WEBSITE
    changelog: str = ""
    is_newer: bool = False


class UpdateCheckWorker(QThread):
    """
    Arka planda zadax.net güncelleme adresini kontrol eden iş parçacığı.
    Program arayüzünü dondurmadan versiyon kontrolü yapar.
    """
    check_completed = Signal(object)  # UpdateInfo
    check_failed = Signal(str)        # Hata mesajı

    def __init__(self, check_url: str = DEFAULT_UPDATE_CHECK_URL,
                 current_version: str = APP_VERSION,
                 parent=None):
        super().__init__(parent)
        self.check_url = check_url
        self.current_version = current_version
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        if not self.check_url or not self.check_url.strip():
            self.check_failed.emit("Güncelleme bağlantı adresi (URL) belirtilmemiş.")
            return

        try:
            req = urllib.request.Request(
                self.check_url,
                headers={
                    "User-Agent": f"KM-Layout-Tables-Updater/{self.current_version}",
                    "Accept": "application/json"
                }
            )
            # 8 saniye zaman aşımı
            with urllib.request.urlopen(req, timeout=8) as response:
                if self._is_cancelled:
                    return
                data_raw = response.read().decode("utf-8")
                data = json.loads(data_raw)

                remote_ver = str(data.get("version", "")).strip()
                # product_url veya download_url (kullanıcının ürün linki)
                product_url = str(
                    data.get("product_url") or data.get("download_url") or COMPANY_WEBSITE
                ).strip()
                changelog = str(data.get("changelog", "")).strip()
                release_date = str(data.get("release_date", "")).strip()

                newer = is_version_newer(remote_ver, self.current_version)

                info = UpdateInfo(
                    version=remote_ver,
                    release_date=release_date,
                    product_url=product_url,
                    changelog=changelog,
                    is_newer=newer
                )
                self.check_completed.emit(info)

        except urllib.error.HTTPError as he:
            if not self._is_cancelled:
                if he.code == 404:
                    self.check_failed.emit("zadax.net güncelleme servisi henüz yayında değil.")
                else:
                    self.check_failed.emit(f"Sunucu hatası ({he.code}): Güncelleme bilgisi alınamadı.")
        except urllib.error.URLError:
            if not self._is_cancelled:
                self.check_failed.emit("zadax.net sunucusuna bağlanılamadı. İnternet bağlantınızı kontrol edin.")
        except json.JSONDecodeError:
            if not self._is_cancelled:
                self.check_failed.emit("Sunucudan dönen sürüm bilgisi geçerli bir JSON formatında değil.")
        except Exception as e:
            if not self._is_cancelled:
                self.check_failed.emit(f"Güncelleme kontrolü sırasında hata: {str(e)}")
