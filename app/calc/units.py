"""Unit checks for calculator inputs.

Percent bases are labels. They are not converted into each other here.
"""

from __future__ import annotations

import math

VOLUME_TO_ML = {"mL": 1.0, "L": 1000.0}
MASS_TO_G = {"mg": 0.001, "g": 1.0, "kg": 1000.0}

# One concentration basis per calculation. These labels are not interchangeable.
CONCENTRATION_BASES = (
    "mol/L",
    "mmol/L",
    "g/L",
    "mg/L",
    "mg/mL",
    "percent_v_v",
    "percent_w_w",
    "percent_w_v",
)

PERCENT_BASES = frozenset({"percent_v_v", "percent_w_w", "percent_w_v"})
MASS_VOLUME_BASES = {
    "g/L": 1.0 / 1000.0,  # g per mL
    "mg/L": 0.001 / 1000.0,
    "mg/mL": 0.001,
    "g/mL": 1.0,
}


def finite_number(value: object) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        text = value.strip().replace(",", ".")
        if not text:
            return None
        try:
            number = float(text)
        except ValueError:
            return None
    else:
        return None
    if not math.isfinite(number):
        return None
    return number


def volume_ml(value: float, unit: str) -> float | None:
    factor = VOLUME_TO_ML.get(unit)
    if factor is None:
        return None
    return value * factor


def mass_g(value: float, unit: str) -> float | None:
    factor = MASS_TO_G.get(unit)
    if factor is None:
        return None
    return value * factor
