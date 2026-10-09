"""
Lisanslama ve Koruma Modülü (Geleceğe Hazır Arayüz).
Pazaryeri (zadax.net) satışı ve lisans anahtarı doğrulaması için altyapı sağlar.
Geliştirme aşamasında bypass modundadır (her zaman aktiftir).
"""
import hashlib
import platform
import uuid
from dataclasses import dataclass
from typing import Optional

@dataclass
class LicenseInfo:
    is_active: bool = True
    licensee: str = "Developer / Unrestricted"
    machine_id: str = ""
    expiration: Optional[str] = None

class LicenseManager:
    _dev_mode: bool = True  # Geliştirme aşamasında her zaman lisanslı

    @classmethod
    def get_machine_id(cls) -> str:
        """Cihaza özgü tekil donanım parmak izi üretir."""
        raw = f"{platform.node()}-{platform.machine()}-{uuid.getnode()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Lisans anahtarını doğrular."""
        if cls._dev_mode:
            return True
        # Gelecekte eklenecek şifreli anahtar kontrolü
        return len(key.strip()) > 0

    @classmethod
    def get_license_info(cls) -> LicenseInfo:
        return LicenseInfo(
            is_active=True,
            licensee="Lisanslı Kullanıcı (Aşama 1 Modu)",
            machine_id=cls.get_machine_id(),
            expiration=None
        )

    @classmethod
    def is_licensed(cls) -> bool:
        return True
