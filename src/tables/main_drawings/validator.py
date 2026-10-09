"""
ГОСТ Р 21.101-2020 Form 2 'Ведомость основных комплектов рабочих чертежей' Doğrulayıcısı.
"""
from src.contracts.table_module import ValidationResult
from src.tables.main_drawings.model import MainDrawingsDocument


class MainDrawingsValidator:
    @staticmethod
    def validate(document: MainDrawingsDocument) -> ValidationResult:
        messages = []

        if not document.items:
            messages.append("Tabloda henüz hiçbir çalışma çizim takımı tanımlanmamış.")

        for idx, item in enumerate(document.items, start=1):
            if not item.designation.strip() and not item.name.strip():
                messages.append(f"Satır #{idx}: Hem takım kodu (Обозначение) hem de adı (Наименование) boş olamaz.")

        is_valid = len(messages) == 0
        return ValidationResult(is_valid=is_valid, messages=messages)
