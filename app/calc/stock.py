"""Stock and consumption arithmetic. Units must already match."""

from __future__ import annotations

from app.calc.result import CalcResult, blocked, ok_result
from app.calc.units import finite_number


def days_of_supply(*, on_hand: object, on_hand_unit: str, use_per_day: object, use_unit: str) -> CalcResult:
    formula = "days = quantity on hand / quantity used per day"
    if not on_hand_unit or on_hand_unit != use_unit:
        return blocked("unit_mismatch", formula, "The stock unit and the daily-use unit must be the same.")
    stock = finite_number(on_hand)
    rate = finite_number(use_per_day)
    if stock is None or rate is None or stock < 0 or rate <= 0:
        return blocked("number_invalid", formula, "Quantity on hand must be zero or greater, and daily use must be greater than zero.")
    days = stock / rate
    return ok_result(
        "stock_ok",
        days,
        "day",
        formula,
        f"{stock} {on_hand_unit} / {rate} {use_unit} per day = {days:.6g} days. This does not say the material is safe to use.",
    )
