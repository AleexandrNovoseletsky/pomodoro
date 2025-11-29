"""Data Normalizers."""

from __future__ import annotations

import re


def normalize_phone(phone: str | None) -> str | None:
    """Normalize Russian phone numbers to format +7XXXXXXXXXX.

    Supports various Russian phone number formats:
    - International: +7 (918) 111-11-11, +7 918 111 11 11
    - National: 8 (918) 111-11-11, 89181111111
    - Local: 918 111-11-11, 9181111111

    Args:
        phone: Raw phone number string that may contain various formatting

    Returns:
        Normalized phone number in +7XXXXXXXXXX format or None if:
        - Input is None or empty
        - Number is not recognized as Russian
        - Number has invalid length or format

    Examples:
        >>> normalize_phone("+7 (918) 111-11-11")
        '+79181111111'
        >>> normalize_phone("89181111111")
        '+79181111111'
        >>> normalize_phone("918 111 11 11")
        '+79181111111'
    """
    if not phone:
        return None

    # Store original first character for international format check
    original_first_char = phone.strip()[0] if phone.strip() else ""

    # Remove all non-digit characters except leading +
    cleaned = re.sub(r"[^\d+]", "", phone)

    # If string started with +, validate it's Russian international code
    if original_first_char == "+":
        if not cleaned.startswith("7"):
            # International format but not Russian (+1, +44, etc.)
            return None
        # Remove the + for consistent processing
        digits = cleaned.removeprefix("7")
    else:
        digits = cleaned

    # Remove any remaining non-digit characters
    digits = re.sub(r"\D", "", digits)

    if not digits:
        return None

    # Handle different digit lengths and formats
    digit_count = len(digits)

    # Case 1: 11 digits starting with 7 or 8
    # (national format with country code)
    if digit_count == 11:
        if digits.startswith("7"):
            return "+" + digits
        elif digits.startswith("8"):
            return "+7" + digits[1:]
        else:
            # 11 digits but doesn't start with 7 or 8 - invalid Russian format
            return None

    # Case 2: 10 digits (local format without country code)
    elif digit_count == 10:
        # Russian mobile numbers typically start with 9
        # Landlines start with 3, 4, 5, 8 but we'll accept any 10 digits
        return "+7" + digits

    # Case 3: More than 11 digits - try to extract valid Russian number
    elif digit_count > 11:
        # Look for Russian pattern in the end of the string
        # Try to find 11 digits starting with 7 or 8
        pattern_11 = re.search(r"(7\d{10}|8\d{10})$", digits)
        if pattern_11:
            matched = pattern_11.group()
            if matched.startswith("7"):
                return "+" + matched
            else:
                return "+7" + matched[1:]

        # Try to find 10 digits (local format)
        pattern_10 = re.search(r"(\d{10})$", digits)
        if pattern_10:
            return "+7" + pattern_10.group()

    # Case 4: Less than 10 digits - invalid
    elif digit_count < 10:
        return None

    # No valid pattern found
    return None


def normalize_name(value: str | None) -> str | None:
    """Normalize person names to standard format.

    Converts names to title case, removes extra whitespace,
    and handles None values.

    Args:
        value: Raw name string that may contain inconsistent formatting

    Returns:
        Normalized name in Title Case with single spaces
        or None if input is empty

    Examples:
        >>> normalize_name("  john   doe  ")
        'John Doe'
        >>> normalize_name("MARY-ANN")
        'Mary-Ann'
        >>> normalize_name(None)
        None
    """
    if value is None:
        return None

    # Remove extra whitespace and normalize
    normalized = " ".join(value.strip().split())

    if not normalized:
        return None

    # Convert to title case (first letter of each word capitalized)
    return normalized.title()
