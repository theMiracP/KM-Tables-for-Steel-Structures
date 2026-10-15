"""
ГОСТ Р 21.101-2020 Приложение Л (Форма 9) Doğrulayıcı (ChangePermissionValidator).
"""
from typing import List
from src.contracts.table_module import ValidationResult
from src.tables.change_permission.model import ChangePermissionDocument


class ChangePermissionValidator:
    @staticmethod
    def validate(document: ChangePermissionDocument) -> ValidationResult:
        messages: List[str] = []

        if not document.resolution_number.strip():
            messages.append("Разрешение № (İzin No) alanı boş bırakılamaz.")

        if not document.doc_code.strip():
            messages.append("Обозначение документа (Doküman Kodu) alanı boş bırakılamaz.")

        if not document.items:
            messages.append("En az bir değişiklik kaydı (satır) bulunmalıdır.")
        else:
            valid_codes = {"", "1", "2", "3", "4", "5", "-"}
            has_valid_item = False
            for idx, it in enumerate(document.items, 1):
                if not it.sheet.strip() and not it.content.strip():
                    continue  # Tamamen boş satır atlanabilir
                has_valid_item = True
                if it.reason_code.strip() and it.reason_code.strip() not in valid_codes:
                    messages.append(
                        f"Satır #{idx}: Geçersiz değişiklik nedeni kodu ('{it.reason_code}'). Standart kodlar: 1, 2, 3, 4, 5."
                    )
            if not has_valid_item:
                messages.append("En az bir geçerli değişiklik satırı girilmelidir.")

        return ValidationResult(is_valid=(len(messages) == 0), messages=messages)
