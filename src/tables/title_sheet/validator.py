"""
ГОСТ Р 21.101-2020 Приложение Р и С (Форма 12) Doğrulayıcı (TitleSheetValidator).
"""
from src.contracts.table_module import ValidationResult
from src.tables.title_sheet.model import TitleSheetDocument


class TitleSheetValidator:
    """Başlık Sayfası veri doğruluğunu denetler."""

    @staticmethod
    def validate(document: TitleSheetDocument) -> ValidationResult:
        errors = []
        warnings = []

        if not document.doc_code or not document.doc_code.strip():
            errors.append("Документ обозначенияси (Обозначение документа / Belge Kodu) boş olamaz.")

        if not document.organization_name or not document.organization_name.strip():
            warnings.append("Tasarım kuruluşu / firma adı (Организация) girilmemiş.")

        if not document.object_name or not document.object_name.strip():
            warnings.append("İnşaat nesnesi / proje adı (Наименование объекта) girilmemiş.")

        if not document.doc_title or not document.doc_title.strip():
            warnings.append("Doküman / bölüm adı (Наименование документа) girilmemiş.")

        if not document.year or not document.year.strip():
            warnings.append("Yayım yılı (Год) girilmemiş.")

        valid_sigs = [s for s in (document.signatories or []) if s.surname.strip()]
        if not valid_sigs:
            warnings.append("En az bir yetkili imzacı soyadı girilmesi tavsiye edilir.")

        messages = errors + warnings
        return ValidationResult(
            is_valid=(len(errors) == 0),
            messages=messages
        )
