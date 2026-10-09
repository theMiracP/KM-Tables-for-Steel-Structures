"""
Giriş Doğrulama (Validation) Testleri.
"""
import pytest
from src.models.elements_schedule import ScheduleItem, ElementPart
from src.validation.validator import TableValidator

def test_validation_with_valid_items():
    """Geçerli elemanlar başarıyla doğrulanmalı."""
    valid_item = ScheduleItem(
        mark="Б1",
        parts=[ElementPart("", "I 20K1")],
        force_a="85.5",
        force_n="45",
        force_m="11,5",
        steel_grade="С255-4"
    )
    result = TableValidator.validate_schedule_items([valid_item])
    assert result.is_valid is True
    assert len(result.messages) == 0

def test_validation_dash_forces():
    """Kuvvet alanlarına tire '-' veya '—' girilmesi geçerli olmalı."""
    dash_item = ScheduleItem(
        mark="Б5",
        parts=[ElementPart("", "140x100x6.0")],
        force_a="-",
        force_n="—",
        force_m="",
        steel_grade="С255-4"
    )
    result = TableValidator.validate_schedule_items([dash_item])
    assert result.is_valid is True
    assert len(result.messages) == 0

def test_validation_empty_mark():
    """Markası boş olan eleman hata vermeli."""
    invalid_item = ScheduleItem(
        mark="",
        parts=[ElementPart("", "I 20K1")],
        force_a="10",
        force_n="20",
        force_m="0"
    )
    result = TableValidator.validate_schedule_items([invalid_item])
    assert result.is_valid is False
    assert any("Eleman markası girilmelidir" in msg for msg in result.messages)

def test_validation_non_numeric_forces():
    """Kuvvet alanlarına harf/geçersiz metin girildiğinde anlaşılır mesaj üretmeli."""
    invalid_item = ScheduleItem(
        mark="Б2",
        parts=[ElementPart("", "140x100x6.0")],
        force_a="abc",
        force_n="20",
        force_m="0"
    )
    result = TableValidator.validate_schedule_items([invalid_item])
    assert result.is_valid is False
    assert any("sayısal olmalıdır" in msg for msg in result.messages)

def test_validation_empty_composition():
    """Profil/kesit bilgisi boş olduğunda hata vermeli."""
    invalid_item = ScheduleItem(
        mark="Б3",
        parts=[ElementPart("", "")],
        force_a="10",
        force_n="20",
        force_m="0"
    )
    result = TableValidator.validate_schedule_items([invalid_item])
    assert result.is_valid is False
    assert any("Kesit/profil bileşimi (Состав) girilmelidir" in msg for msg in result.messages)
