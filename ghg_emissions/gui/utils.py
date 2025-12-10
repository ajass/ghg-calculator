"""Utility functions for GHG Emissions Calculator GUI."""

import re
from typing import Optional

from ..models import Unit, Scope
from .models import GUIActivity


def validate_activity_input(activity_type: str, quantity: str, unit: str,
                          scope: str, description: str) -> GUIActivity:
    """Validate and parse activity input from GUI forms.

    Args:
        activity_type: The type of activity
        quantity: Quantity as string
        unit: Unit as string
        scope: Scope as string
        description: Optional description

    Returns:
        Validated GUIActivity object

    Raises:
        ValueError: If input validation fails
    """
    # Validate activity type
    if not activity_type or not activity_type.strip():
        raise ValueError("Activity type is required")

    activity_type = activity_type.strip()

    # Validate quantity
    if not quantity or not quantity.strip():
        raise ValueError("Quantity is required")

    try:
        quantity_val = float(quantity.strip())
        if quantity_val < 0:
            raise ValueError("Quantity must be non-negative")
    except ValueError:
        raise ValueError("Quantity must be a valid number")

    # Validate unit
    try:
        unit_val = Unit(unit)
    except ValueError:
        raise ValueError(f"Invalid unit: {unit}. Must be one of {[u.value for u in Unit]}")

    # Validate scope
    try:
        scope_val = Scope(scope)
    except ValueError:
        raise ValueError(f"Invalid scope: {scope}. Must be one of {[s.value for s in Scope]}")

    # Validate description (optional)
    description_val = description.strip() if description else None

    return GUIActivity(
        activity_type=activity_type,
        quantity=quantity_val,
        unit=unit_val,
        scope=scope_val,
        description=description_val
    )


def format_emission_result(total_co2e: float, unit: str = "kg") -> str:
    """Format emission result for display.

    Args:
        total_co2e: Total CO2 equivalent emissions
        unit: Unit for display

    Returns:
        Formatted string
    """
    if total_co2e >= 1000:
        return f"{total_co2e/1000:.2f} tonnes CO2e"
    else:
        return f"{total_co2e:.2f} {unit} CO2e"


def validate_file_path(file_path: str) -> bool:
    """Validate file path for export.

    Args:
        file_path: File path to validate

    Returns:
        True if valid, False otherwise
    """
    if not file_path:
        return False

    # Basic validation - check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    if any(char in file_path for char in invalid_chars):
        return False

    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    # Ensure not empty
    if not sanitized:
        sanitized = "export"

    return sanitized