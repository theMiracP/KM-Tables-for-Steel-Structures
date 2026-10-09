"""
'Ведомость ссылочных и прилагаемых документов' Doğrulayıcısı (Validator).
Mühendislik ve GOST kurallarına göre doküman listesini kontrol eder.
"""
from typing import List
from src.contracts.table_module import ValidationResult
from src.tables.reference_documents.model import ReferenceDocsDocument


class ReferenceDocsValidator:
    @staticmethod
    def validate(document: ReferenceDocsDocument) -> ValidationResult:
        messages: List[str] = []

        if not document.items:
            messages.append("Doküman listesi boş. En az bir standart veya referans doküman ekleyin.")
            return ValidationResult(is_valid=False, messages=messages)

        doc_items = [it for it in document.items if not it.is_section_header]
        if not doc_items:
            messages.append("Listede sadece bölüm başlıkları bulunuyor, geçerli doküman eklenmemiş.")
            return ValidationResult(is_valid=False, messages=messages)

        for idx, item in enumerate(doc_items, start=1):
            if not item.designation.strip() and not item.title.strip():
                messages.append(f"Satır #{idx}: Standart kodu (Обозначение) veya başlığı (Наименование) boş bırakılamaz.")

        is_valid = len(messages) == 0
        return ValidationResult(is_valid=is_valid, messages=messages)
