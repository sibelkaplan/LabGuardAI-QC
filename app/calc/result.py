"""Shared calculation result. status is ok or blocked."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalcResult:
    status: str
    code: str
    value: float | None = None
    unit: str = ""
    formula: str = ""
    detail: str = ""

    def __post_init__(self) -> None:
        if self.status not in {"ok", "blocked"}:
            raise ValueError(self.status)
        if self.status == "blocked" and self.value is not None:
            raise ValueError("blocked results do not carry a quantity")

    @property
    def blocked(self) -> bool:
        return self.status == "blocked"


def blocked(code: str, formula: str = "", detail: str = "") -> CalcResult:
    return CalcResult(status="blocked", code=code, formula=formula, detail=detail)


def ok_result(code: str, value: float, unit: str, formula: str, detail: str) -> CalcResult:
    return CalcResult(status="ok", code=code, value=value, unit=unit, formula=formula, detail=detail)
