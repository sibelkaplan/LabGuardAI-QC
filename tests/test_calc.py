import math

import pytest

from app.calc.concentration import (
    convert_mass,
    convert_volume,
    mass_from_molarity,
    mass_from_solution,
    ppm_to_mg_per_l,
)
from app.calc.dilution import convert_percent_basis, hazardous_product_dilution, solve_dilution
from app.calc.mudlogging import (
    FT3_PER_BBL,
    PSI_PER_FT_PER_PPG,
    US_GAL_PER_FT3,
    annular_capacity,
    annular_velocity,
    ecd,
    hydrostatic_pressure,
    lag_time,
    pipe_capacity,
    pit_volume,
)
from app.calc.stock import days_of_supply


def test_same_basis_dilution_solves_one_volume():
    result = solve_dilution(c1="12", v1="", c2="0,1", v2="1000", basis="mol/L")
    assert result.status == "ok"
    assert result.value == pytest.approx(1000 * 0.1 / 12)
    assert "C1 × V1 = C2 × V2" in result.formula
    assert "not a mixing procedure" in result.detail


def test_percent_bases_are_not_converted_even_with_density():
    blocked = convert_percent_basis(37, "percent_w_w", "percent_v_v", density=1.19)
    assert blocked.status == "blocked"
    assert blocked.value is None
    assert blocked.code == "percent_basis_blocked"


def test_hazardous_product_dilution_stays_disabled_with_complete_inputs():
    blocked = hazardous_product_dilution(
        product_concentration=37,
        basis="percent_w_w",
        density=1.19,
        target_concentration=1,
        target_volume=1000,
        expert_approved=True,
        verified_product_data=True,
    )
    assert blocked.status == "blocked"
    assert blocked.value is None
    assert blocked.code == "hazardous_dilution_disabled"


def test_dilution_rejects_concentration_increase_and_mixed_unknowns():
    stronger = solve_dilution(c1=1, v1=None, c2=2, v2=10, basis="mol/L")
    assert stronger.code == "not_dilution"
    assert stronger.value is None
    both_missing = solve_dilution(c1=1, v1=None, c2=None, v2=10, basis="g/L")
    assert both_missing.code == "one_unknown"


def test_mass_volume_and_molar_conversions_need_explicit_inputs():
    assert convert_volume("1,5", "L", "mL").value == pytest.approx(1500)
    assert convert_mass(2, "kg", "g").value == pytest.approx(2000)
    mass = mass_from_solution(
        concentration=2, concentration_basis="g/L", volume=500, volume_unit="mL", mass_unit="g"
    )
    assert mass.value == pytest.approx(1)
    percent = mass_from_solution(
        concentration=10, concentration_basis="percent_w_v", volume=1, volume_unit="L", mass_unit="g"
    )
    assert percent.code == "basis_not_mass_volume"
    missing = mass_from_molarity(
        molarity_mol_per_l=1, volume=1, volume_unit="L", molar_mass_g_per_mol="", mass_unit="g"
    )
    assert missing.code == "molar_mass_required"
    assert missing.value is None
    supplied = mass_from_molarity(
        molarity_mol_per_l=0.5, volume=2, volume_unit="L", molar_mass_g_per_mol=40, mass_unit="g"
    )
    assert supplied.value == pytest.approx(40)
    assert ppm_to_mg_per_l(10, density=1).value is None


def test_hydrostatic_uses_exact_gallon_factor_and_states_the_rounded_one():
    result = hydrostatic_pressure(10, 1000)
    assert result.value == pytest.approx(10 * 1000 * 12 / 231)
    assert result.value != pytest.approx(10 * 1000 * 0.052)
    assert "0.052" in result.detail
    assert PSI_PER_FT_PER_PPG == pytest.approx(12 / 231)


def test_annular_velocity_matches_the_unit_identity():
    flow, hole, pipe = 400, 12.25, 5
    result = annular_velocity(flow, hole, pipe)
    area = math.pi / 4 * (hole ** 2 - pipe ** 2) / 144
    expected = (flow / US_GAL_PER_FT3) / area
    assert result.value == pytest.approx(expected)
    assert annular_velocity(400, 5, 8).code == "geometry_invalid"


def test_capacity_pit_ecd_and_lag_do_not_invent_missing_inputs():
    diameter = 4
    capacity = pipe_capacity(diameter)
    expected = (math.pi / 4 * diameter ** 2 / 144) / FT3_PER_BBL
    assert capacity.value == pytest.approx(expected)
    annular = annular_capacity(12.25, 5)
    area = math.pi / 4 * (12.25 ** 2 - 25) / 144
    assert annular.value == pytest.approx(area / FT3_PER_BBL)
    pit = pit_volume(20, 10, 5)
    assert pit.value == pytest.approx(1000 / FT3_PER_BBL)
    missing_loss = ecd(10, "", 10000)
    assert missing_loss.code == "pressure_loss_required"
    assert missing_loss.value is None
    with_loss = ecd(10, 200, 10000)
    assert with_loss.value == pytest.approx(10 + 200 / (10000 * 12 / 231))
    assert lag_time(100, 5).value == pytest.approx(20)
    assert lag_time(100, 0).code == "number_invalid"


def test_stock_days_require_the_same_unit():
    assert days_of_supply(on_hand="10", on_hand_unit="L", use_per_day="2,5", use_unit="L").value == pytest.approx(4)
    mismatch = days_of_supply(on_hand=10, on_hand_unit="L", use_per_day=1, use_unit="mL")
    assert mismatch.code == "unit_mismatch"
    assert mismatch.value is None
