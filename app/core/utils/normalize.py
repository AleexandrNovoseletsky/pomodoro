"""Нормализаторы данных."""

from __future__ import annotations

import re


def normalize_phone(phone: str | None) -> str | None:
    """Нормализовать номер телефона к формату +7XXXXXXXXXX.

    Поддерживаем российские номера в форматах:
    - 8XXXXXXXXXX
    - +7XXXXXXXXXX
    - XXXXXXXXXX (если 10 цифр — считаем местным и приставляем +7)
    - с разделителями: пробелы, скобки, дефисы и т.д.

    Также поддерживаем входы с международным префиксом '00' (например,
    007918...) — префикс будет удалён и номер обработан дальше.

    Если в строке содержится больше цифр (например, копипаста с лишним
    префиксом), пытаемся взять последние 10 цифр, если они выглядят как
    мобильный российский номер (начинаются с '9').

    Если номер не распознан как российский — возвращаем None.
    """
    if phone is None:
        return None

    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None

    # Удалим международный префикс '00', если есть (например, 007...)
    digits = digits.removeprefix("00")

    # Вариант: 11 цифр, начинается с 8 или 7
    if len(digits) == 11:
        if digits.startswith("8"):
            return "+7" + digits[1:]
        if digits.startswith("7"):
            return "+" + digits

    # Вариант: 10 цифр — считаем местным мобильным номером и добавляем +7
    if len(digits) == 10:
        return "+7" + digits

    # Если в строке больше цифр (копипаста с префиксом), попробуем взять
    # последние 10 цифр — часто это корректный локальный номер.
    if len(digits) > 11:
        last10 = digits[-10:]
        if len(last10) == 10 and last10[0] == "9":
            return "+7" + last10

    # Неподдерживаемые форматы
    return None


def normalize_name(value: str | None) -> str | None:
    """Привести ФИО к виду: первая буква заглавная, остальные — строчные.

    Если вход пустой или None — возвращаем None.
    Удаляем лишние пробелы по краям и сводим множественные к одному.
    """
    if value is None:
        return None
    v = " ".join(value.strip().split())
    if v == "":
        return None
    return v.capitalize()
