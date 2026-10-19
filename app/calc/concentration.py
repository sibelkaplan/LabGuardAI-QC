"""Mass, volume, and concentration conversions that stay inside one basis.

Molar mass is never looked up from a chemical name. ppm is not treated as
mg/L, because that step assumes a density this module does not invent.
"""

from __future__ import annotations

from app.calc.result import CalcResult, blocked, ok_result
from app.calc.units import MASS_TO_G, MASS_VOLUME_BASES, VOLUME_TO_ML, finite_number, mass_g, volume_ml


def convert_volume(value: object, from_unit: str, to_unit: str) -> CalcResult:
    number = finite_number(value)
    if number is None or number < 0:
        return blocked("number_invalid", "V_to = V_from × factor", "Volume must be zero or greater.")
    if from_unit not in VOLUME_TO_ML or to_unit not in VOLUME_TO_ML:
        return blocked("unit_invalid", "V_to = V_from × factor", "Volume units are mL and L.")
    ml = volume_ml(number, from_unit)
    result = ml / VOLUME_TO_ML[to_unit]
    return ok_result(
        "volume_converted",
        result,
        to_unit,
        "V_to = V_from × (mL factor from / mL factor to)",
        f"{number} {from_unit} = {result:.6g} {to_unit}",
    )


def convert_mass(value: object, from_unit: str, to_unit: str) -> CalcResult:
    number = finite_number(value)
    if number is None or number < 0:
        return blocked("number_invalid", "m_to = m_from × factor", "Mass must be zero or greater.")
    if from_unit not in MASS_TO_G or to_unit not in MASS_TO_G:
        return blocked("unit_invalid", "m_to = m_from × factor", "Mass units are mg, g, and kg.")
    grams = mass_g(number, from_unit)
    result = grams / MASS_TO_G[to_unit]
    return ok_result(
        "mass_converted",
        result,
        to_unit,
        "m_to = m_from × (g factor from / g factor to)",
        f"{number} {from_unit} = {result:.6g} {to_unit}",
    )


def mass_from_solution(
    *,
    concentration: object,
    concentration_basis: str,
    volume: object,
    volume_unit: str,
    mass_unit: str,
) -> CalcResult:
    """mass = concentration × volume, only for a mass/volume basis."""
    formula = "mass = concentration × volume"
    if concentration_basis not in MASS_VOLUME_BASES:
        return blocked(
            "basis_not_mass_volume",
            formula,
            "Mass from solution is available only for g/L, mg/L, mg/mL, or g/mL. Percent bases are not used.",
        )
    conc = finite_number(concentration)
    vol = finite_number(volume)
    if conc is None or vol is None or conc < 0 or vol < 0:
        return blocked("number_invalid", formula, "Concentration and volume must be zero or greater.")
    ml = volume_ml(vol, volume_unit)
    if ml is None or mass_unit not in MASS_TO_G:
        return blocked("unit_invalid", formula, "Use mL or L, and mg, g, or kg.")
    grams = MASS_VOLUME_BASES[concentration_basis] * ml
    # MASS_VOLUME_BASES is g per mL of solution at the stated concentration of 1.
    grams = grams * conc
    result = grams / MASS_TO_G[mass_unit]
    return ok_result(
        "mass_from_solution",
        result,
        mass_unit,
        formula,
        f"{conc} {concentration_basis} × {vol} {volume_unit} = {result:.6g} {mass_unit}",
    )


def mass_from_molarity(
    *,
    molarity_mol_per_l: object,
    volume: object,
    volume_unit: str,
    molar_mass_g_per_mol: object,
    mass_unit: str,
) -> CalcResult:
    """mass = M × V × molar mass. The caller must supply the molar mass."""
    formula = "mass = molarity (mol/L) × volume (L) × molar mass (g/mol)"
    molarity = finite_number(molarity_mol_per_l)
    vol = finite_number(volume)
    molar_mass = finite_number(molar_mass_g_per_mol)
    if molar_mass is None:
        return blocked("molar_mass_required", formula, "Enter the molar mass from the product or a trusted source. It is not looked up.")
    if molarity is None or vol is None or molarity < 0 or vol < 0 or molar_mass <= 0:
        return blocked("number_invalid", formula, "Molarity and volume must be zero or greater, and molar mass must be greater than zero.")
    ml = volume_ml(vol, volume_unit)
    if ml is None or mass_unit not in MASS_TO_G:
        return blocked("unit_invalid", formula, "Use mL or L, and mg, g, or kg.")
    grams = molarity * (ml / 1000.0) * molar_mass
    result = grams / MASS_TO_G[mass_unit]
    return ok_result(
        "mass_from_molarity",
        result,
        mass_unit,
        formula,
        f"{molarity} mol/L × {vol} {volume_unit} × {molar_mass} g/mol = {result:.6g} {mass_unit}",
    )


def ppm_to_mg_per_l(value: object = None, density: object = None) -> CalcResult:
    """ppm is not converted. Density is ignored on purpose."""
    del value, density
    return blocked(
        "ppm_blocked",
        "ppm → mg/L",
        "ppm is not converted to mg/L here, because that step needs a density and a stated definition that this module will not assume.",
    )
