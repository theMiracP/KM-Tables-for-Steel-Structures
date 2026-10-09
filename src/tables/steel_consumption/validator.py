"""
KM Tablo Oluşturucu - 'Ведомость расхода стали' Doğrulayıcı (Validator).
Mühendislik ve GOST standartlarına göre çelik sarfiyat verilerini denetler.
"""
from typing import List, Union, Set
from src.contracts.table_module import ValidationResult
from src.tables.steel_consumption.model import (
    SteelConsumptionItem, SteelConsumptionDocument
)
from src.ui.i18n import i18n


class SteelConsumptionValidator:
    """Çelik sarfiyat tablosu için statik kural denetleyicisi."""

    @classmethod
    def validate(
        cls,
        items_or_doc: Union[List[SteelConsumptionItem], SteelConsumptionDocument]
    ) -> ValidationResult:
        if isinstance(items_or_doc, SteelConsumptionDocument):
            items = items_or_doc.items
        else:
            items = items_or_doc

        messages: List[str] = []

        # 1. Boş tablo kontrolü
        if not items:
            return ValidationResult(
                is_valid=False,
                messages=[i18n.t("val_sc_empty_table")]
            )

        seen_marks: Set[str] = set()

        for idx, it in enumerate(items, start=1):
            mark = it.mark.strip() if it.mark else ""

            # 2. Marka boşluk kontrolü
            if not mark:
                messages.append(i18n.t("val_sc_empty_mark", idx=idx))
            else:
                # 3. Yinelenen marka kontrolü
                if mark in seen_marks:
                    messages.append(i18n.t("val_sc_dup_mark", idx=idx, mark=mark))
                seen_marks.add(mark)

            # 4. Geçersiz sayısal metin kontrolleri (raw_values)
            if hasattr(it, "raw_values") and it.raw_values:
                for fld, raw_val in it.raw_values.items():
                    messages.append(i18n.t("val_sc_invalid_num", idx=idx, mark=mark or str(idx), field=fld, val=raw_val))

            # 5. Negatif ağırlık kontrolleri
            weights = [it.i_beam, it.channel, it.angle, it.tube, it.plate]
            has_negative = any(w < 0.0 for w in weights)
            if has_negative:
                messages.append(i18n.t("val_sc_neg_weight", idx=idx, mark=mark or str(idx)))

            # 6. Sıfır sarfiyat kontrolü (Tüm profiller 0 ise ve geçersiz metin yoksa)
            if sum(weights) <= 0.0 and not has_negative and not (hasattr(it, "raw_values") and it.raw_values):
                messages.append(i18n.t("val_sc_zero_weight", idx=idx, mark=mark or str(idx)))

        is_valid = len(messages) == 0
        return ValidationResult(is_valid=is_valid, messages=messages)
