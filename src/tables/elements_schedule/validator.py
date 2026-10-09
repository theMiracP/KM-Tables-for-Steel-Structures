"""
'Ведомость элементов' Veri Doğrulayıcı (Validator).
Mühendislik kurallarına ve ГОСТ 21.502 standardına uygunluk kontrolü.
"""
from typing import List, Optional, Union
from src.contracts.table_module import ValidationResult
from src.tables.elements_schedule.model import ScheduleItem, ElementsScheduleDocument

class ElementsScheduleValidator:
    @staticmethod
    def validate_number_str(val: str, field_name: str, allow_empty: bool = True) -> Optional[str]:
        """Sayısal alan kontrolü (virgül veya nokta destekli)."""
        val_clean = val.strip().replace(",", ".")
        if not val_clean:
            if not allow_empty:
                return f"{field_name} alanı boş bırakılamaz."
            return None

        # Mühendislik çizimlerinde tire '-' veya uzun tire '—' (kuvvet yok) geçerlidir
        if val_clean in ("-", "—", "–"):
            return None

        try:
            float(val_clean)
            return None
        except ValueError:
            return f"{field_name} alanı sayısal olmalıdır (veya '-') (Girilen: '{val}')."

    @classmethod
    def validate_item(cls, item: ScheduleItem, row_number: int = 1) -> List[str]:
        errors: List[str] = []

        # 1. Marka kontrolü
        if not item.mark.strip():
            errors.append(f"Satır {row_number}: Eleman markası girilmelidir.")

        # 2. Kuvvet değerleri kontrolü (A, N, M)
        err_a = cls.validate_number_str(item.force_a, f"Satır {row_number} (A, кН)")
        if err_a:
            errors.append(err_a)

        err_n = cls.validate_number_str(item.force_n, f"Satır {row_number} (N, кН)")
        if err_n:
            errors.append(err_n)

        err_m = cls.validate_number_str(item.force_m, f"Satır {row_number} (M, кН*м)")
        if err_m:
            errors.append(err_m)

        # 3. Profil tanımı kontrolü
        if not item.parts or not any(p.composition.strip() for p in item.parts):
            errors.append(f"Satır {row_number}: Kesit/profil bileşimi (Состав) girilmelidir.")

        return errors

    @classmethod
    def validate(cls, items_or_doc: Union[List[ScheduleItem], ElementsScheduleDocument]) -> ValidationResult:
        if isinstance(items_or_doc, ElementsScheduleDocument):
            items = items_or_doc.items
        else:
            items = items_or_doc

        if not items:
            return ValidationResult(is_valid=False, messages=["Tabloda en az 1 eleman bulunmalıdır."])

        all_errors: List[str] = []
        for idx, item in enumerate(items, start=1):
            item_errors = cls.validate_item(item, row_number=idx)
            all_errors.extend(item_errors)

        return ValidationResult(is_valid=len(all_errors) == 0, messages=all_errors)

    # Geriye dönük uyumluluk takma adı
    validate_schedule_items = validate
