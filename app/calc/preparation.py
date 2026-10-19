"""Acid-preparation review.

Theoretical same-basis ratios are calculated here. They are not preparation
approvals. A typed density, a tick box, or a label note never verifies a
product and never authorizes a mixture.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.calc.dilution import hazardous_product_dilution
from app.calc.result import CalcResult, blocked
from app.calc.units import CONCENTRATION_BASES, finite_number

VOLUME_UNITS = ("mL", "L")
# These bases already express an amount per volume, so C1×V1 = C2×V2 is a
# volume ratio. Percent by mass is not one of them.
VOLUME_RATIO_BASES = frozenset(
    {"percent_v_v", "percent_w_v", "mol/L", "mmol/L", "g/L", "mg/L", "mg/mL", "g/mL"}
)
EXAMPLE_C1 = 32.0
EXAMPLE_C2 = 18.5
_EXAMPLE_NAMES = {"hcl", "hidroklorik asit", "hydrochloric acid"}
_FORMULA = "C1 × V1 = C2 × V2"


@dataclass(frozen=True)
class PreparationReview:
    approval: CalcResult
    math_value: float | None
    math_unit: str
    math_code: str
    density_required: bool

    @property
    def value(self):
        return self.approval.value

    @property
    def status(self) -> str:
        return self.approval.status

    @property
    def code(self) -> str:
        return self.approval.code

    @property
    def detail(self) -> str:
        return self.approval.detail


def round_sig(value: float, figures: int = 4) -> float:
    """Round half away from zero to a fixed number of significant figures."""
    if value == 0 or not math.isfinite(value):
        return value
    magnitude = math.floor(math.log10(abs(value)))
    factor = 10 ** (figures - 1 - magnitude)
    shifted = value * factor
    rounded = math.floor(abs(shifted) + 0.5)
    if shifted < 0:
        rounded = -rounded
    return rounded / factor


def is_hcl_example(name: object, c1: object, c2: object) -> bool:
    if str(name or "").strip().lower() not in _EXAMPLE_NAMES:
        return False
    start = finite_number(c1)
    target = finite_number(c2)
    if start is None or target is None:
        return False
    return abs(start - EXAMPLE_C1) < 1e-9 and abs(target - EXAMPLE_C2) < 1e-9


def _approval(code: str, detail: str) -> CalcResult:
    gated = hazardous_product_dilution(
        product_concentration=1,
        basis="percent_w_w",
        density=1,
        target_concentration=1,
        target_volume=1,
        expert_approved=True,
        verified_product_data=True,
    )
    if gated.value is not None:
        raise RuntimeError("Hazardous dilution returned a quantity.")
    return blocked(code, _FORMULA, detail)


def review_preparation(
    *,
    name: object,
    c1: object,
    basis: str,
    c2: object,
    volume: object,
    volume_unit: str,
    density: object = None,
    sds_basis_checked: bool = False,
    sds_density_checked: bool = False,
    procedure_checked: bool = False,
) -> PreparationReview:
    """Return a theoretical ratio, when the basis allows it, and always refuse approval.

    Check boxes and a typed density are ignored on purpose. They do not verify
    an SDS and they are not used as product data.
    """
    del sds_basis_checked, sds_density_checked, procedure_checked, density
    start = finite_number(c1)
    target = finite_number(c2)
    final_volume = finite_number(volume)
    invalid = _approval(
        "prepare_invalid",
        "Required preparation answers are missing or invalid.",
    )
    if (
        not str(name or "").strip()
        or start is None
        or start <= 0
        or target is None
        or target <= 0
        or final_volume is None
        or final_volume <= 0
        or basis not in CONCENTRATION_BASES
        or volume_unit not in VOLUME_UNITS
    ):
        return PreparationReview(invalid, None, "", "prepare_invalid", False)
    if target >= start:
        return PreparationReview(
            _approval("prepare_not_lower", "The target is not lower than the start."),
            None,
            "",
            "prepare_not_lower",
            False,
        )
    if basis == "percent_w_w":
        return PreparationReview(
            _approval(
                "prepare_no_quantity",
                "Percent by mass does not yield a stock volume from a final volume. Density was not used.",
            ),
            None,
            "",
            "prep_ww_volume_blocked",
            True,
        )
    if basis not in VOLUME_RATIO_BASES:
        return PreparationReview(
            _approval("prepare_no_quantity", "This basis has no volume ratio in this module."),
            None,
            "",
            "prepare_no_quantity",
            False,
        )
    raw = (target * final_volume) / start
    rounded = round_sig(raw, 4)
    approval = _approval(
        "prepare_no_quantity",
        f"Theoretical stock volume {rounded} {volume_unit} on basis {basis}. Not a preparation approval.",
    )
    return PreparationReview(approval, rounded, volume_unit, "prep_math_ok", False)
