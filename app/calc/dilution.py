"""Dilution arithmetic.

Same-basis C1V1 = C2V2 is ordinary proportion. It is not a mixing procedure
and it does not authorize anyone to prepare a solution.

Hazardous product dilution stays blocked. This module will not turn a
concentrated product into an instruction such as "add this many millilitres".
Percent volume, percent mass, and mass/volume percent are never converted
into one another, with or without a density.
"""

from __future__ import annotations

from app.calc.result import CalcResult, blocked, ok_result
from app.calc.units import CONCENTRATION_BASES, finite_number

_FORMULA = "C1 × V1 = C2 × V2"


def convert_percent_basis(
    value: object = None,
    from_basis: str = "",
    to_basis: str = "",
    density: object = None,
) -> CalcResult:
    """Refuse every percent-basis conversion, including when density is supplied."""
    del value, from_basis, to_basis, density
    return blocked(
        "percent_basis_blocked",
        _FORMULA,
        "percent_v_v, percent_w_w, and percent_w_v are different bases and are not converted.",
    )


def hazardous_product_dilution(
    *,
    product_concentration: object = None,
    basis: str = "",
    density: object = None,
    target_concentration: object = None,
    target_volume: object = None,
    expert_approved: bool = False,
    verified_product_data: bool = False,
) -> CalcResult:
    """Operational dilution from a hazardous product is not enabled.

    Flags, density, and concentrations are accepted so callers can see that
    supplying them still does not produce a quantity.
    """
    del product_concentration, basis, density, target_concentration, target_volume
    del expert_approved, verified_product_data
    return blocked(
        "hazardous_dilution_disabled",
        _FORMULA,
        "Hazardous product dilution is disabled until verified product data and an expert-approved procedure are part of the product. This build does not have either.",
    )


def solve_dilution(
    *,
    c1: object,
    v1: object,
    c2: object,
    v2: object,
    basis: str,
) -> CalcResult:
    """Solve the single missing term of C1V1 = C2V2 inside one basis.

    Volumes are in the same unit, chosen by the caller. The result unit is
    that same unnamed volume unit; this function does not tell anyone how
    to mix the liquids.
    """
    if basis not in CONCENTRATION_BASES:
        return blocked("basis_invalid", _FORMULA, "Choose one concentration basis.")
    raw = {"c1": c1, "v1": v1, "c2": c2, "v2": v2}
    parsed: dict[str, float | None] = {}
    missing = []
    for key, value in raw.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            parsed[key] = None
            missing.append(key)
            continue
        number = finite_number(value)
        if number is None:
            return blocked("number_invalid", _FORMULA, f"{key} is not a finite number.")
        parsed[key] = number
    if len(missing) != 1:
        return blocked("one_unknown", _FORMULA, "Leave exactly one of C1, V1, C2, V2 empty.")
    for key, number in parsed.items():
        if number is None:
            continue
        if number <= 0:
            return blocked("not_positive", _FORMULA, f"{key} must be greater than zero.")
    unknown = missing[0]
    c1_value, v1_value = parsed["c1"], parsed["v1"]
    c2_value, v2_value = parsed["c2"], parsed["v2"]
    if unknown == "v1":
        value = (c2_value * v2_value) / c1_value
    elif unknown == "v2":
        value = (c1_value * v1_value) / c2_value
    elif unknown == "c1":
        value = (c2_value * v2_value) / v1_value
    else:
        value = (c1_value * v1_value) / v2_value
    solved = dict(parsed)
    solved[unknown] = value
    if solved["c2"] >= solved["c1"]:
        return blocked(
            "not_dilution",
            _FORMULA,
            "The result is not a dilution because the final concentration is not lower than the starting concentration.",
        )
    detail = (
        f"Basis {basis}. Solved {unknown} = {value:.6g}. "
        "Same basis only. This is not a mixing procedure."
    )
    return ok_result("dilution_ok", value, "volume" if unknown.startswith("v") else basis, _FORMULA, detail)
