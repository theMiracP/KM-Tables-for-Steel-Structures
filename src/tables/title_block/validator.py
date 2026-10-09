"""
ГОСТ Р 21.101-2020 Form 3 Başlık Bloğu Doğrulayıcısı (Validator).
Mühendislik standartlarına göre zorunlu antet alanlarını denetler.
"""
from typing import Any
from src.contracts.table_module import ValidationResult
from src.tables.title_block.model import TitleBlockDocument


class TitleBlockValidator:
    @staticmethod
    def validate(document: Any) -> ValidationResult:
        if not isinstance(document, TitleBlockDocument):
            return ValidationResult(is_valid=False, messages=["Geçersiz antet veri tipi."])

        messages = []

        # 1. Doküman Kodu (Графа 1)
        if not document.doc_code or not document.doc_code.strip():
            messages.append("Doküman kodu / şifresi (обозначение документа) boş bırakılamaz.")

        # 2. Proje Aşaması (Графа 6)
        if not document.stage or not document.stage.strip():
            messages.append("Proje aşaması (стадия: Р veya П) belirtilmelidir.")

        # 3. Pafta Numarası (Графа 7)
        if not document.sheet_num or not document.sheet_num.strip():
            messages.append("Pafta sıra numarası (лист) boş bırakılamaz.")

        # 4. En az bir imza sorumlusu (Örn: Разраб.)
        has_signer = any(s.surname and s.surname.strip() for s in document.signatories)
        if not has_signer:
            messages.append("En az bir imza sorumlusu (Разраб.) soyadı girilmelidir.")

        is_valid = len(messages) == 0
        return ValidationResult(is_valid=is_valid, messages=messages)
