"""
ГОСТ Р 21.101-2020 Form 1 'Ведомость рабочих чертежей основного комплекта' Doğrulayıcısı.
"""
from typing import List
from src.contracts.table_module import ValidationResult
from src.tables.working_drawings.model import WorkingDrawingsDocument


class WorkingDrawingsValidator:
    """Pafta listesi verilerini doğrular."""

    @classmethod
    def validate(cls, doc: WorkingDrawingsDocument) -> ValidationResult:
        messages: List[str] = []

        if not doc.items:
            messages.append("Tabloda henüz hiçbir pafta / çalışma çizimi tanımlanmamış.")
            return ValidationResult(is_valid=False, messages=messages)

        seen_sheets = set()
        has_any_content = False

        for idx, item in enumerate(doc.items, start=1):
            s_num = item.sheet_number.strip()
            name = item.name.strip()

            if not s_num and not name:
                messages.append(f"Satır #{idx}: Hem pafta no (Лист) hem de çizim adı (Наименование) boş olamaz.")
                continue

            has_any_content = True

            if not s_num:
                messages.append(f"Satır #{idx}: Pafta numarası belirtilmemiş ('{name[:25]}...').")
            elif s_num in seen_sheets:
                messages.append(f"Satır #{idx}: Yinelenen pafta numarası tespit edildi ('{s_num}').")
            else:
                seen_sheets.add(s_num)

            if not name:
                messages.append(f"Satır #{idx}: Pafta #{s_num} için çizim adı boş bırakılmış.")

        if not has_any_content:
            messages.append("Tablodaki tüm satırlar boş. En az bir geçerli pafta girilmelidir.")

        is_valid = len(messages) == 0
        return ValidationResult(is_valid=is_valid, messages=messages)
