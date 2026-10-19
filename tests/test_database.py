import sqlite3
from datetime import date

import pytest

from app.constants import CHECK_KEYS, SCHEMA_VERSION
from app.database import (
    add_chemical,
    add_incident,
    add_inspection,
    connect,
    delete_chemical,
    export_backup,
    import_backup,
    list_chemicals,
    list_incidents,
    list_inspection_rows,
    update_chemical,
)
from app.validation import BackupError, ValidationError


def _chemical(**overrides):
    fields = {
        "name": "Sample container",
        "quantity": "1.5",
        "unit": "L",
        "location": "Cabinet A",
        "expiry": "2020-01-01",
        "sds_document": "binder-3",
        "sds_revision": "A",
        "qr_id": "QR-9",
    }
    fields.update(overrides)
    return fields


def test_schema_migration_is_idempotent_and_upgrades_legacy_rows(tmp_path):
    path = tmp_path / "legacy.db"
    raw = sqlite3.connect(path)
    raw.execute(
        """CREATE TABLE chemicals(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, quantity REAL NOT NULL,
            unit TEXT NOT NULL, location TEXT NOT NULL, expiry TEXT DEFAULT '', status TEXT DEFAULT 'Review')"""
    )
    raw.execute(
        """CREATE TABLE incidents(
            id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, severity TEXT NOT NULL,
            description TEXT NOT NULL, created_at TEXT NOT NULL)"""
    )
    raw.execute(
        """CREATE TABLE inspections(
            id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT NOT NULL, checked INTEGER NOT NULL,
            checked_at TEXT NOT NULL)"""
    )
    raw.execute(
        "INSERT INTO chemicals(name, quantity, unit, location, expiry, status) VALUES(?,?,?,?,?,?)",
        ("Legacy bottle", 2, "g", "Shelf", "2024-01-01", "Review"),
    )
    raw.execute(
        "INSERT INTO incidents(kind, severity, description, created_at) VALUES(?,?,?,?)",
        ("spill", "low", "Old report", "2024-05-01"),
    )
    raw.execute(
        "INSERT INTO inspections(item, checked, checked_at) VALUES(?,?,?)",
        ("eyewash", 1, "2024-05-01"),
    )
    raw.commit()
    raw.close()

    con = connect(path)
    again = connect(path)
    chemicals = list_chemicals(con, "", today=date(2026, 10, 17))
    assert chemicals[0]["name"] == "Legacy bottle"
    assert chemicals[0]["qr_id"] == ""
    assert chemicals[0]["status"] == "expired"
    incidents = list_incidents(con)
    assert incidents[0]["description"] == "Old report"
    assert incidents[0]["status"] == "open"
    assert incidents[0]["owner"] == ""
    rows = list_inspection_rows(con)
    assert rows[0]["item_key"] == "eyewash"
    assert rows[0]["checked"] is True
    version = again.execute("SELECT version FROM schema_meta").fetchone()[0]
    assert version == SCHEMA_VERSION
    con.close()
    again.close()


def test_chemical_crud_search_and_literal_quotes(tmp_path):
    con = connect(tmp_path / "lab.db")
    first = add_chemical(con, _chemical(name="Alpha", qr_id="QR-1", location="North"))
    second = add_chemical(con, _chemical(name="O'Brien 50%", qr_id="QR_2", location="South"))
    assert list_chemicals(con, "obrien") == []
    found = list_chemicals(con, "O'Brien")
    assert [row["id"] for row in found] == [second]
    assert [row["name"] for row in list_chemicals(con, "%")] == ["O'Brien 50%"]
    assert [row["qr_id"] for row in list_chemicals(con, "_")] == ["QR_2"]
    assert list_chemicals(con, "QR_2")[0]["name"] == "O'Brien 50%"
    assert update_chemical(con, first, _chemical(name="Alpha updated", expiry="2099-01-01", qr_id="QR-1"))
    updated = list_chemicals(con, "Alpha", today=date(2026, 10, 17))
    assert updated[0]["name"] == "Alpha updated"
    assert updated[0]["status"] == "ok"
    assert delete_chemical(con, first) is True
    assert delete_chemical(con, first) is False
    assert [row["id"] for row in list_chemicals(con, "")] == [second]
    with pytest.raises(ValidationError):
        add_chemical(con, _chemical(quantity="-3"))
    con.close()


def test_expiry_status_is_recomputed_on_read(tmp_path):
    con = connect(tmp_path / "lab.db")
    add_chemical(con, _chemical(expiry="2026-10-20"))
    assert list_chemicals(con, "", today=date(2026, 10, 17))[0]["status"] == "expiring"
    assert list_chemicals(con, "", today=date(2026, 10, 21))[0]["status"] == "expired"
    con.close()


def test_inspection_history_keeps_same_day_sessions(tmp_path):
    con = connect(tmp_path / "lab.db")
    items = {key: key == "labels" for key in CHECK_KEYS}
    add_inspection(con, {"inspector": "Ada", "items": items, "inspected_on": "2026-10-17"})
    items["labels"] = False
    add_inspection(con, {"inspector": "Ada", "items": items, "inspected_on": "2026-10-17"})
    rows = list_inspection_rows(con)
    sessions = {row["session_id"] for row in rows}
    assert len(sessions) == 2
    assert len(rows) == len(CHECK_KEYS) * 2
    latest = [row for row in rows if row["session_id"] == max(sessions)]
    labels = next(row for row in latest if row["item_key"] == "labels")
    assert labels["checked"] is False
    assert labels["inspector"] == "Ada"
    con.close()


def test_incident_history_stores_owner_status_and_action(tmp_path):
    con = connect(tmp_path / "lab.db")
    add_incident(
        con,
        {
            "kind": "unlabelled",
            "severity": "medium",
            "description": "A container had no readable label.",
            "status": "in_progress",
            "owner": "Safety lead",
            "corrective_action": "Quarantined the container.",
            "created_at": "2026-10-17T09:00:00+03:00",
        },
    )
    rows = list_incidents(con)
    assert rows[0]["status"] == "in_progress"
    assert rows[0]["owner"] == "Safety lead"
    assert rows[0]["corrective_action"] == "Quarantined the container."
    assert rows[0]["created_at"] == "2026-10-17T09:00:00+03:00"
    con.close()


def test_backup_roundtrip_replaces_records_and_bad_file_keeps_them(tmp_path):
    original = connect(tmp_path / "original.db")
    add_chemical(original, _chemical(name="Keep me"))
    add_incident(
        original,
        {"kind": "near", "severity": "low", "description": "Door was blocked.", "owner": "Sam"},
    )
    add_inspection(
        original,
        {"inspector": "Sam", "items": {key: True for key in CHECK_KEYS}, "inspected_on": "2026-10-01"},
    )
    payload = export_backup(original)
    assert payload["schema_version"] == SCHEMA_VERSION
    assert "does not authorize" in payload["disclaimer"]

    other = connect(tmp_path / "other.db")
    add_chemical(other, _chemical(name="Replace me", qr_id="OLD"))
    imported = import_backup(other, payload)
    assert imported["chemicals"] == 1
    assert list_chemicals(other, "")[0]["name"] == "Keep me"
    assert list_incidents(other)[0]["description"] == "Door was blocked."
    assert len({row["session_id"] for row in list_inspection_rows(other)}) == 1

    bad = export_backup(other)
    bad["schema_version"] = 1
    with pytest.raises(BackupError) as caught:
        import_backup(other, bad)
    assert caught.value.code == "backup_version"
    assert list_chemicals(other, "")[0]["name"] == "Keep me"

    broken = export_backup(other)
    broken["chemicals"][0]["name"] = ""
    with pytest.raises(BackupError) as caught:
        import_backup(other, broken)
    assert caught.value.code == "backup_invalid"
    assert list_chemicals(other, "")[0]["name"] == "Keep me"
    original.close()
    other.close()
