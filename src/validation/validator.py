"""
Kullanıcı Dostu Veri Doğrulama (Validation).
NOT: 'Ведомость элементов' validatörü `src/tables/elements_schedule/validator.py` altına taşınmıştır.
Bu dosya geriye dönük tam uyumluluk (backward compatibility) için re-export sağlar.
"""
from src.contracts.table_module import ValidationResult
from src.tables.elements_schedule.validator import ElementsScheduleValidator

# Geriye dönük uyumluluk için alias
TableValidator = ElementsScheduleValidator

__all__ = ["ValidationResult", "TableValidator", "ElementsScheduleValidator"]
