"""Drilling-fluid arithmetic used as a mud-logging calculator.

These are unit identities, not operating procedures and not well-control
instructions. Friction loss is never estimated.

Sources for the relations, not for a site procedure:

- Hydrostatic pressure. One US gallon is 231 in³, so
  P (psi) = MW (ppg) × TVD (ft) × 12/231.
  Field handbooks often round 12/231 (0.051948) to 0.052.
  The same relation is the hydrostatic term in API RP 13D and in
  Bourgoyne, Millheim, Chenevert, and Young, Applied Drilling Engineering,
  SPE Textbook Series, Vol. 2.
- Annular velocity. Flow rate is converted with 1728/231 US gallons per
  cubic foot, and area uses π/4 with diameters in inches:
  AV (ft/min) = Q (ft³/min) / area (ft²).
  The familiar field factor 24.51 is this conversion rounded.
- Capacity and pit volume. One barrel is 42 US gallons, so
  1 bbl = 42 × 231/1728 ft³.
- Equivalent circulating density uses a supplied annular pressure loss.
  API RP 13D discusses ECD; this module does not compute the pressure loss.
- Lag time is volume divided by a supplied pump output.
"""

from __future__ import annotations

import math

from app.calc.result import CalcResult, blocked, ok_result
from app.calc.units import finite_number

# 1 US gallon = 231 in³. 1 ft³ = 1728 in³.
US_GALLON_IN3 = 231.0
FT3_IN3 = 1728.0
PSI_PER_FT_PER_PPG = 12.0 / US_GALLON_IN3
US_GAL_PER_FT3 = FT3_IN3 / US_GALLON_IN3
BBL_GAL = 42.0
FT3_PER_BBL = BBL_GAL / US_GAL_PER_FT3


def _positive(value: object) -> float | None:
    number = finite_number(value)
    if number is None or number <= 0:
        return None
    return number


def hydrostatic_pressure(mud_weight_ppg: object, tvd_ft: object) -> CalcResult:
    formula = "P (psi) = MW (ppg) × TVD (ft) × 12/231"
    mw = _positive(mud_weight_ppg)
    tvd = _positive(tvd_ft)
    if mw is None or tvd is None:
        return blocked("number_invalid", formula, "Mud weight and vertical depth must be greater than zero.")
    psi = mw * tvd * PSI_PER_FT_PER_PPG
    rounded = mw * tvd * 0.052
    return ok_result(
        "hydrostatic_ok",
        psi,
        "psi",
        formula,
        f"{mw} ppg × {tvd} ft × 12/231 = {psi:.6g} psi. The rounded field factor 0.052 would give {rounded:.6g} psi.",
    )


def annular_velocity(flow_gpm: object, hole_id_in: object, pipe_od_in: object) -> CalcResult:
    formula = "AV (ft/min) = Q (ft³/min) / (π/4 × (Dh² − Dp²) / 144)"
    flow = _positive(flow_gpm)
    hole = _positive(hole_id_in)
    pipe = _positive(pipe_od_in)
    if flow is None or hole is None or pipe is None:
        return blocked("number_invalid", formula, "Flow and both diameters must be greater than zero.")
    if pipe >= hole:
        return blocked("geometry_invalid", formula, "Pipe outside diameter must be smaller than the hole diameter.")
    area_ft2 = math.pi / 4.0 * (hole ** 2 - pipe ** 2) / 144.0
    q_ft3_min = flow / US_GAL_PER_FT3
    velocity = q_ft3_min / area_ft2
    return ok_result(
        "velocity_ok",
        velocity,
        "ft/min",
        formula,
        f"{flow} gal/min across Dh {hole} in and Dp {pipe} in = {velocity:.6g} ft/min.",
    )


def pipe_capacity(internal_diameter_in: object) -> CalcResult:
    formula = "bbl/ft = (π/4 × ID² / 144) / (42 × 231/1728)"
    diameter = _positive(internal_diameter_in)
    if diameter is None:
        return blocked("number_invalid", formula, "Internal diameter must be greater than zero.")
    ft3_per_ft = math.pi / 4.0 * (diameter ** 2) / 144.0
    bbl_per_ft = ft3_per_ft / FT3_PER_BBL
    return ok_result(
        "capacity_ok",
        bbl_per_ft,
        "bbl/ft",
        formula,
        f"ID {diameter} in = {bbl_per_ft:.6g} bbl/ft. Open-pipe capacity only.",
    )


def annular_capacity(hole_id_in: object, pipe_od_in: object) -> CalcResult:
    formula = "bbl/ft = (π/4 × (Dh² − Dp²) / 144) / (42 × 231/1728)"
    hole = _positive(hole_id_in)
    pipe = _positive(pipe_od_in)
    if hole is None or pipe is None:
        return blocked("number_invalid", formula, "Both diameters must be greater than zero.")
    if pipe >= hole:
        return blocked("geometry_invalid", formula, "Pipe outside diameter must be smaller than the hole diameter.")
    ft3_per_ft = math.pi / 4.0 * (hole ** 2 - pipe ** 2) / 144.0
    bbl_per_ft = ft3_per_ft / FT3_PER_BBL
    return ok_result(
        "annular_capacity_ok",
        bbl_per_ft,
        "bbl/ft",
        formula,
        f"Dh {hole} in, Dp {pipe} in = {bbl_per_ft:.6g} bbl/ft.",
    )


def pit_volume(length_ft: object, width_ft: object, height_ft: object) -> CalcResult:
    formula = "bbl = length × width × height / (42 × 231/1728)"
    length = _positive(length_ft)
    width = _positive(width_ft)
    height = _positive(height_ft)
    if length is None or width is None or height is None:
        return blocked("number_invalid", formula, "Length, width, and height must be greater than zero.")
    bbl = (length * width * height) / FT3_PER_BBL
    return ok_result(
        "pit_ok",
        bbl,
        "bbl",
        formula,
        f"{length} × {width} × {height} ft = {bbl:.6g} bbl for a rectangular pit.",
    )


def ecd(mud_weight_ppg: object, annular_pressure_loss_psi: object, tvd_ft: object) -> CalcResult:
    formula = "ECD (ppg) = MW + annular pressure loss / (TVD × 12/231)"
    mw = _positive(mud_weight_ppg)
    tvd = _positive(tvd_ft)
    loss = finite_number(annular_pressure_loss_psi)
    if mw is None or tvd is None:
        return blocked("number_invalid", formula, "Mud weight and vertical depth must be greater than zero.")
    if loss is None:
        return blocked(
            "pressure_loss_required",
            formula,
            "Annular pressure loss must be entered. It is not estimated.",
        )
    if loss < 0:
        return blocked("number_invalid", formula, "Annular pressure loss cannot be negative.")
    value = mw + loss / (tvd * PSI_PER_FT_PER_PPG)
    return ok_result(
        "ecd_ok",
        value,
        "ppg",
        formula,
        f"MW {mw} ppg and {loss} psi at {tvd} ft = {value:.6g} ppg. Friction was not calculated.",
    )


def lag_time(annular_volume_bbl: object, pump_output_bbl_per_min: object) -> CalcResult:
    formula = "lag (min) = annular volume (bbl) / pump output (bbl/min)"
    volume = _positive(annular_volume_bbl)
    output = _positive(pump_output_bbl_per_min)
    if volume is None or output is None:
        return blocked("number_invalid", formula, "Annular volume and pump output must be greater than zero.")
    minutes = volume / output
    return ok_result(
        "lag_ok",
        minutes,
        "min",
        formula,
        f"{volume} bbl / {output} bbl/min = {minutes:.6g} min. Pump output is an input, not an estimate.",
    )
