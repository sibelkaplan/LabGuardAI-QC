from datetime import date

import pytest

from app.constants import CHECK_KEYS
from app.validation import (
    ValidationError,
    expiry_status,
    format_quantity,
    parse_expiry,
    parse_quantity,
    parse_qr,
    validate_chemical_fields,
    validate_incident_fields,
    validate_inspection,
)


def test_quantity_accepts_decimal_comma_and_dot():
    assert parse_quantity("1,5") == 1.5
    assert parse_quantity("2.25") == 2.25
    assert parse_quantity(0) == 0
    assert parse_quantity(3) == 3


@pytest.mark.parametrize(
    "value, code",
    [
        ("", "quantity_invalid"),
        ("abc", "quantity_invalid"),
        ("1e2", "quantity_invalid"),
        (True, "quantity_invalid"),
        (float("nan"), "quantity_invalid"),
        (-1, "quantity_negative"),
        ("-0,5", "quantity_invalid"),
    ],
)
def test_quantity_rejects_bad_values(value, code):
    with pytest.raises(ValidationError) as caught:
        parse_quantity(value)
    assert caught.value.code == code


def test_expiry_and_status_are_date_reminders_only():
    today = date(2026, 10, 17)
    assert parse_expiry("") == ""
    assert parse_expiry("2026-10-17") == "2026-10-17"
    assert expiry_status("", today) == "review"
    assert expiry_status("2026-10-16", today) == "expired"
    assert expiry_status("2026-10-17", today) == "expiring"
    assert expiry_status("2026-11-16", today) == "expiring"
    assert expiry_status("2026-11-17", today) == "ok"
    with pytest.raises(ValidationError) as caught:
        parse_expiry("2026-02-31")
    assert caught.value.code == "date_invalid"


def test_qr_identifier_charset():
    assert parse_qr(" LAB-01_A.2 ") == "LAB-01_A.2"
    assert parse_qr("") == ""
    with pytest.raises(ValidationError) as caught:
        parse_qr("bad id")
    assert caught.value.code == "qr_invalid"


def test_chemical_fields_keep_sds_and_qr_as_metadata():
    fields = validate_chemical_fields(
        name="  Sample container  ",
        quantity="1,0",
        unit="mL",
        location="Cabinet A",
        expiry="",
        sds_document="site-file-ref",
        sds_revision="2026-01",
        qr_id="QR-1",
    )
    assert fields["name"] == "Sample container"
    assert fields["quantity"] == 1
    assert fields["sds_document"] == "site-file-ref"
    assert fields["qr_id"] == "QR-1"
    assert format_quantity(fields["quantity"]) == "1"


def test_chemical_name_and_location_are_required():
    with pytest.raises(ValidationError) as caught:
        validate_chemical_fields(
            name="  ",
            quantity="1",
            unit="L",
            location="Shelf",
            expiry="",
        )
    assert caught.value.code == "name_required"
    with pytest.raises(ValidationError) as caught:
        validate_chemical_fields(
            name="Sample",
            quantity="1",
            unit="bucket",
            location="Shelf",
            expiry="",
        )
    assert caught.value.code == "unit_invalid"


def test_incident_requires_description_and_known_choices():
    fields = validate_incident_fields(
        kind="near",
        severity="low",
        description="Label was unreadable.",
        status="open",
        owner="A. Kara",
        corrective_action="Replaced the label.",
    )
    assert fields["owner"] == "A. Kara"
    with pytest.raises(ValidationError) as caught:
        validate_incident_fields(kind="near", severity="low", description="  ")
    assert caught.value.code == "description_required"
    with pytest.raises(ValidationError) as caught:
        validate_incident_fields(kind="other", severity="low", description="Text")
    assert caught.value.code == "kind_invalid"


def test_inspection_requires_inspector_and_every_item():
    items = {key: False for key in CHECK_KEYS}
    fields = validate_inspection(inspector="  Lab tech  ", items=items, inspected_on="2026-10-17")
    assert fields["inspector"] == "Lab tech"
    assert set(fields["items"]) == set(CHECK_KEYS)
    with pytest.raises(ValidationError) as caught:
        validate_inspection(inspector=" ", items=items)
    assert caught.value.code == "inspector_required"
    incomplete = dict(items)
    incomplete.pop("sds")
    with pytest.raises(ValidationError) as caught:
        validate_inspection(inspector="Lab tech", items=incomplete)
    assert caught.value.code == "inspection_incomplete"
