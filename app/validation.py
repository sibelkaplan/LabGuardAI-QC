"""Input checks for local records.

These checks reject malformed form data. They do not decide whether a
chemical, PPE item, or activity is safe.
"""

from __future__ import annotations

import math
import re
from datetime import date, datetime

from app.constants import (
    CHECK_KEYS,
    EXPIRING_WITHIN_DAYS,
    GHS_CODES,
    INCIDENT_KINDS,
    INCIDENT_STATUSES,
    SEVERITIES,
    UNITS,
)

ERROR_CODES = frozenset(
    {
        "name_required",
        "quantity_invalid",
        "quantity_negative",
        "location_required",
        "date_invalid",
        "unit_invalid",
        "description_required",
        "inspector_required",
        "qr_invalid",
        "text_too_long",
        "status_invalid",
        "severity_invalid",
        "kind_invalid",
        "timestamp_invalid",
        "inspection_incomplete",
        "ghs_invalid",
        "category_invalid",
    }
)

BACKUP_CODES = frozenset({"backup_invalid", "backup_version"})

_QR_RE = re.compile(r"^[A-Za-z0-9._:-]*$")
_QUANTITY_RE = re.compile(r"\d+(\.\d+)?")

STATUS_I18N = {
    "ok": "status_ok",
    "expiring": "status_expiring",
    "expired": "status_expired",
    "review": "status_review",
}


class ValidationError(Exception):
    def __init__(self, code: str):
        if code not in ERROR_CODES:
            raise RuntimeError(f"Unknown validation code: {code}")
        self.code = code
        super().__init__(code)


class BackupError(Exception):
    def __init__(self, code: str):
        if code not in BACKUP_CODES:
            raise RuntimeError(f"Unknown backup code: {code}")
        self.code = code
        super().__init__(code)


def _text(value: object, *, max_len: int, required_code: str | None = None, newlines: bool = False) -> str:
    if value is None:
        text = ""
    elif isinstance(value, str):
        text = value
    else:
        raise ValidationError("text_too_long")
    if newlines:
        text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    else:
        text = " ".join(text.split())
    if required_code and not text:
        raise ValidationError(required_code)
    if len(text) > max_len:
        raise ValidationError("text_too_long")
    return text


def parse_quantity(value: object) -> float:
    if isinstance(value, bool) or value is None:
        raise ValidationError("quantity_invalid")
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        text = value.strip().replace(",", ".")
        if not text or _QUANTITY_RE.fullmatch(text) is None:
            raise ValidationError("quantity_invalid")
        number = float(text)
    else:
        raise ValidationError("quantity_invalid")
    if not math.isfinite(number) or number > 1_000_000_000:
        raise ValidationError("quantity_invalid")
    if number < 0:
        raise ValidationError("quantity_negative")
    return number


def format_quantity(value: float) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6f}".rstrip("0").rstrip(".")


def parse_expiry(value: object) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValidationError("date_invalid")
    text = value.strip()
    if not text:
        return ""
    if len(text) != 10:
        raise ValidationError("date_invalid")
    try:
        date.fromisoformat(text)
    except ValueError:
        raise ValidationError("date_invalid") from None
    return text


def parse_timestamp(value: object, *, required: bool = False) -> str:
    if value is None:
        text = ""
    elif isinstance(value, str):
        text = value.strip()
    else:
        raise ValidationError("timestamp_invalid")
    if not text:
        if required:
            raise ValidationError("timestamp_invalid")
        return ""
    if len(text) > 40:
        raise ValidationError("timestamp_invalid")
    try:
        if len(text) == 10:
            date.fromisoformat(text)
        else:
            datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise ValidationError("timestamp_invalid") from None
    return text


def parse_qr(value: object) -> str:
    text = _text(value, max_len=64)
    if _QR_RE.fullmatch(text) is None:
        raise ValidationError("qr_invalid")
    return text


def expiry_status(expiry: str, today: date | None = None) -> str:
    """Return a date-reminder label. This is not a use authorization."""
    if not expiry:
        return "review"
    day = date.fromisoformat(expiry)
    current = today or date.today()
    if day < current:
        return "expired"
    if (day - current).days <= EXPIRING_WITHIN_DAYS:
        return "expiring"
    return "ok"


def parse_ghs(value: object) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",") if part.strip()]
    elif isinstance(value, (list, tuple)):
        parts = []
        for part in value:
            if not isinstance(part, str):
                raise ValidationError("ghs_invalid")
            text = part.strip()
            if text:
                parts.append(text)
    else:
        raise ValidationError("ghs_invalid")
    if len(parts) != len(set(parts)) or any(part not in GHS_CODES for part in parts):
        raise ValidationError("ghs_invalid")
    return ",".join(sorted(parts, key=GHS_CODES.index))


def validate_chemical_fields(
    *,
    name: object,
    quantity: object,
    unit: object,
    location: object,
    expiry: object,
    sds_document: object = "",
    sds_revision: object = "",
    qr_id: object = "",
    purpose: object = "",
    hazard_notes: object = "",
    ghs_codes: object = "",
    ppe_notes: object = "",
    glove_notes: object = "",
    storage_notes: object = "",
) -> dict:
    if not isinstance(unit, str) or unit not in UNITS:
        raise ValidationError("unit_invalid")
    return {
        "name": _text(name, max_len=200, required_code="name_required"),
        "quantity": parse_quantity(quantity),
        "unit": unit,
        "location": _text(location, max_len=200, required_code="location_required"),
        "expiry": parse_expiry(expiry if isinstance(expiry, str) or expiry is None else "bad"),
        "sds_document": _text(sds_document, max_len=300),
        "sds_revision": _text(sds_revision, max_len=80),
        "qr_id": parse_qr(qr_id),
        "purpose": _text(purpose, max_len=500, newlines=True),
        "hazard_notes": _text(hazard_notes, max_len=2000, newlines=True),
        "ghs_codes": parse_ghs(ghs_codes),
        "ppe_notes": _text(ppe_notes, max_len=2000, newlines=True),
        "glove_notes": _text(glove_notes, max_len=2000, newlines=True),
        "storage_notes": _text(storage_notes, max_len=2000, newlines=True),
    }


def validate_incident_fields(
    *,
    kind: object,
    severity: object,
    description: object,
    status: object = "open",
    owner: object = "",
    corrective_action: object = "",
    created_at: object = "",
    updated_at: object = "",
) -> dict:
    if kind not in INCIDENT_KINDS:
        raise ValidationError("kind_invalid")
    if severity not in SEVERITIES:
        raise ValidationError("severity_invalid")
    if status not in INCIDENT_STATUSES:
        raise ValidationError("status_invalid")
    return {
        "kind": kind,
        "severity": severity,
        "description": _text(description, max_len=4000, required_code="description_required", newlines=True),
        "status": status,
        "owner": _text(owner, max_len=120),
        "corrective_action": _text(corrective_action, max_len=4000, newlines=True),
        "created_at": parse_timestamp(created_at),
        "updated_at": parse_timestamp(updated_at),
    }


def validate_inspection(*, inspector: object, items: object, inspected_on: object = None) -> dict:
    if not isinstance(items, dict):
        raise ValidationError("inspection_incomplete")
    if set(items) != set(CHECK_KEYS):
        raise ValidationError("inspection_incomplete")
    normalized: dict[str, bool] = {}
    for key in CHECK_KEYS:
        value = items[key]
        if isinstance(value, bool):
            normalized[key] = value
        elif isinstance(value, int) and value in (0, 1):
            normalized[key] = bool(value)
        else:
            raise ValidationError("inspection_incomplete")
    if inspected_on is None or (isinstance(inspected_on, str) and not inspected_on.strip()):
        day = date.today().isoformat()
    else:
        day = parse_expiry(inspected_on if isinstance(inspected_on, str) else "bad")
        if not day:
            raise ValidationError("date_invalid")
    return {
        "inspector": _text(inspector, max_len=120, required_code="inspector_required"),
        "items": normalized,
        "inspected_on": day,
    }
