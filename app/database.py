"""SQLite storage for local laboratory records.

Queries are parameterized. Schema changes go through numbered migrations.
Saved rows are records, not safety approvals.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import date
from pathlib import Path
from typing import Mapping

from app.constants import CHECK_KEYS, CHEMICAL_NOTES, LIBRARY_CATEGORIES, SCHEMA_VERSION
from app.validation import (
    BackupError,
    ValidationError,
    expiry_status,
    parse_expiry,
    parse_timestamp,
    validate_chemical_fields,
    validate_incident_fields,
    validate_inspection,
)

BACKUP_DISCLAIMER = (
    "Local data export from LabGuard AI. This file is not a validated safety "
    "record and does not authorize chemical handling."
)

_TABLES = {
    "chemicals",
    "incidents",
    "inspections",
    "inspection_sessions",
    "inspection_items",
    "calculation_history",
    "library_additions",
    "product_labels",
    "stock_movements",
    "schema_meta",
}

_CHEMICAL_COLUMNS = """
    id, name, quantity, unit, location, expiry, status,
    created_at, updated_at, sds_document, sds_revision, qr_id,
    purpose, hazard_notes, ghs_codes, ppe_notes, glove_notes, storage_notes
"""

CALC_MODULES = ("dilution", "units", "mud", "stock")


def default_db_path() -> Path:
    return Path.home() / "Library" / "Application Support" / "LabGuardAI" / "labguard.db"


def resolve_db_path(db_path: Path | None = None) -> Path:
    if db_path is not None:
        return Path(db_path)
    override = os.environ.get("LABGUARD_DB")
    if override:
        return Path(override)
    return default_db_path()


def local_now() -> str:
    from datetime import datetime

    return datetime.now().astimezone().isoformat(timespec="seconds")


class _Transaction:
    def __init__(self, con: sqlite3.Connection):
        self._con = con

    def __enter__(self) -> sqlite3.Connection:
        self._con.execute("BEGIN")
        return self._con

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None:
            self._con.execute("COMMIT")
        else:
            try:
                self._con.execute("ROLLBACK")
            except sqlite3.OperationalError:
                pass
        return False


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.isolation_level = None
    con.execute("PRAGMA foreign_keys = ON")
    migrate(con)
    return con


def migrate(con: sqlite3.Connection) -> None:
    with _Transaction(con):
        con.execute(
            """CREATE TABLE IF NOT EXISTS schema_meta (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                version INTEGER NOT NULL
            )"""
        )
        _ensure_v1(con)
        version = _version(con)
        if version < 1:
            _set_version(con, 1)
            version = 1
        if version < 2:
            _migrate_to_v2(con)
            _import_legacy_inspections(con)
            _set_version(con, 2)
            version = 2
        if version < 3:
            _migrate_to_v3(con)
            _set_version(con, 3)
        _ensure_library_additions(con)
        _ensure_product_labels(con)
        _ensure_stock_movements(con)
        _ensure_lesson_marks(con)
        if _version(con) != SCHEMA_VERSION:
            raise sqlite3.DatabaseError(f"Unsupported schema version {_version(con)}")


def _ensure_v1(con: sqlite3.Connection) -> None:
    con.execute(
        """CREATE TABLE IF NOT EXISTS chemicals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            location TEXT NOT NULL,
            expiry TEXT DEFAULT '',
            status TEXT DEFAULT 'Review'
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS incidents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS inspections(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            checked INTEGER NOT NULL,
            checked_at TEXT NOT NULL
        )"""
    )


def _migrate_to_v2(con: sqlite3.Connection) -> None:
    columns = {
        "chemicals": (
            ("created_at", "TEXT NOT NULL DEFAULT ''"),
            ("updated_at", "TEXT NOT NULL DEFAULT ''"),
            ("sds_document", "TEXT NOT NULL DEFAULT ''"),
            ("sds_revision", "TEXT NOT NULL DEFAULT ''"),
            ("qr_id", "TEXT NOT NULL DEFAULT ''"),
        ),
        "incidents": (
            ("status", "TEXT NOT NULL DEFAULT 'open'"),
            ("owner", "TEXT NOT NULL DEFAULT ''"),
            ("corrective_action", "TEXT NOT NULL DEFAULT ''"),
            ("updated_at", "TEXT NOT NULL DEFAULT ''"),
        ),
    }
    for table, specs in columns.items():
        existing = _columns(con, table)
        for name, definition in specs:
            if name not in existing:
                con.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
    con.execute(
        """CREATE TABLE IF NOT EXISTS inspection_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspected_on TEXT NOT NULL,
            inspector TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT ''
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS inspection_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            item_key TEXT NOT NULL,
            checked INTEGER NOT NULL CHECK (checked IN (0, 1)),
            FOREIGN KEY (session_id) REFERENCES inspection_sessions(id) ON DELETE CASCADE
        )"""
    )
    con.execute("CREATE INDEX IF NOT EXISTS idx_chemicals_name ON chemicals(name)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents(created_at)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_inspection_items_session ON inspection_items(session_id)")


def _migrate_to_v3(con: sqlite3.Connection) -> None:
    notes = (
        ("purpose", "TEXT NOT NULL DEFAULT ''"),
        ("hazard_notes", "TEXT NOT NULL DEFAULT ''"),
        ("ghs_codes", "TEXT NOT NULL DEFAULT ''"),
        ("ppe_notes", "TEXT NOT NULL DEFAULT ''"),
        ("glove_notes", "TEXT NOT NULL DEFAULT ''"),
        ("storage_notes", "TEXT NOT NULL DEFAULT ''"),
    )
    existing = _columns(con, "chemicals")
    for name, definition in notes:
        if name not in existing:
            con.execute(f"ALTER TABLE chemicals ADD COLUMN {name} {definition}")
    con.execute(
        """CREATE TABLE IF NOT EXISTS calculation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL,
            code TEXT NOT NULL,
            formula TEXT NOT NULL DEFAULT '',
            value REAL,
            unit TEXT NOT NULL DEFAULT '',
            detail TEXT NOT NULL DEFAULT '',
            inputs_json TEXT NOT NULL DEFAULT ''
        )"""
    )


def _ensure_library_additions(con: sqlite3.Connection) -> None:
    """Additive table. Existing chemical, inspection, and incident rows stay."""
    con.execute(
        """CREATE TABLE IF NOT EXISTS library_additions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            formula TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL,
            user_note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )"""
    )


def _ensure_product_labels(con: sqlite3.Connection) -> None:
    con.execute(
        """CREATE TABLE IF NOT EXISTS product_labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            label_concentration TEXT NOT NULL DEFAULT '',
            label_density TEXT NOT NULL DEFAULT '',
            sds_source TEXT NOT NULL DEFAULT '',
            verification TEXT NOT NULL DEFAULT 'unverified',
            created_at TEXT NOT NULL
        )"""
    )


def _ensure_lesson_marks(con: sqlite3.Connection) -> None:
    """Favorites and recent lessons. Existing inventory rows are not touched."""
    con.execute(
        """CREATE TABLE IF NOT EXISTS lesson_recent (
            lesson_id TEXT PRIMARY KEY,
            seen_at TEXT NOT NULL
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS lesson_favorites (
            lesson_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL
        )"""
    )


def remember_lesson(con: sqlite3.Connection, lesson_id: str) -> None:
    if con is None or not str(lesson_id or "").strip():
        return
    from datetime import datetime, timezone

    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    con.execute(
        """INSERT INTO lesson_recent(lesson_id, seen_at) VALUES(?, ?)
           ON CONFLICT(lesson_id) DO UPDATE SET seen_at = excluded.seen_at""",
        (lesson_id, stamp),
    )


def toggle_favorite(con: sqlite3.Connection, lesson_id: str) -> bool:
    if con is None or not str(lesson_id or "").strip():
        return False
    from datetime import datetime, timezone

    row = con.execute(
        "SELECT lesson_id FROM lesson_favorites WHERE lesson_id = ?",
        (lesson_id,),
    ).fetchone()
    if row is not None:
        con.execute("DELETE FROM lesson_favorites WHERE lesson_id = ?", (lesson_id,))
        return False
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    con.execute(
        "INSERT INTO lesson_favorites(lesson_id, created_at) VALUES(?, ?)",
        (lesson_id, stamp),
    )
    return True


def list_recent_lessons(con: sqlite3.Connection, limit: int = 3) -> list[str]:
    if con is None:
        return []
    rows = con.execute(
        "SELECT lesson_id FROM lesson_recent ORDER BY seen_at DESC LIMIT ?",
        (int(limit),),
    ).fetchall()
    return [row["lesson_id"] for row in rows]


def list_favorite_lessons(con: sqlite3.Connection, limit: int = 3) -> list[str]:
    if con is None:
        return []
    rows = con.execute(
        "SELECT lesson_id FROM lesson_favorites ORDER BY created_at DESC LIMIT ?",
        (int(limit),),
    ).fetchall()
    return [row["lesson_id"] for row in rows]


def is_favorite(con: sqlite3.Connection, lesson_id: str) -> bool:
    if con is None or not lesson_id:
        return False
    row = con.execute(
        "SELECT 1 FROM lesson_favorites WHERE lesson_id = ?",
        (lesson_id,),
    ).fetchone()
    return row is not None


def _ensure_stock_movements(con: sqlite3.Connection) -> None:
    con.execute(
        """CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_id INTEGER NOT NULL,
            direction TEXT NOT NULL CHECK (direction IN ('in', 'out')),
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )"""
    )


def _import_legacy_inspections(con: sqlite3.Connection) -> None:
    existing = con.execute("SELECT COUNT(*) FROM inspection_sessions").fetchone()
    if existing and int(existing[0]) > 0:
        return
    rows = con.execute(
        "SELECT item, checked, checked_at FROM inspections ORDER BY checked_at, id"
    ).fetchall()
    grouped: dict[str, list[sqlite3.Row]] = {}
    for row in rows:
        grouped.setdefault(row["checked_at"], []).append(row)
    for checked_at, items in grouped.items():
        cursor = con.execute(
            """INSERT INTO inspection_sessions(inspected_on, inspector, created_at, note)
               VALUES(?,?,?,?)""",
            (checked_at, "", checked_at, ""),
        )
        session_id = int(cursor.lastrowid)
        seen: set[str] = set()
        for item in items:
            key = item["item"]
            if key in seen:
                continue
            seen.add(key)
            con.execute(
                "INSERT INTO inspection_items(session_id, item_key, checked) VALUES(?,?,?)",
                (session_id, key, 1 if item["checked"] else 0),
            )


def _columns(con: sqlite3.Connection, table: str) -> set[str]:
    if table not in _TABLES:
        raise ValueError(table)
    return {row[1] for row in con.execute(f"PRAGMA table_info({table})")}


def _version(con: sqlite3.Connection) -> int:
    row = con.execute("SELECT version FROM schema_meta WHERE id = 1").fetchone()
    return int(row["version"]) if row else 0


def _set_version(con: sqlite3.Connection, version: int) -> None:
    con.execute(
        """INSERT INTO schema_meta(id, version) VALUES(1, ?)
           ON CONFLICT(id) DO UPDATE SET version = excluded.version""",
        (version,),
    )


def _like(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _chemical_from_row(row: sqlite3.Row, today: date | None = None) -> dict:
    expiry = row["expiry"] or ""
    return {
        "id": int(row["id"]),
        "name": row["name"],
        "quantity": float(row["quantity"]),
        "unit": row["unit"],
        "location": row["location"],
        "expiry": expiry,
        "status": expiry_status(expiry, today),
        "created_at": row["created_at"] or "",
        "updated_at": row["updated_at"] or "",
        "sds_document": row["sds_document"] or "",
        "sds_revision": row["sds_revision"] or "",
        "qr_id": row["qr_id"] or "",
        "purpose": row["purpose"] or "",
        "hazard_notes": row["hazard_notes"] or "",
        "ghs_codes": row["ghs_codes"] or "",
        "ppe_notes": row["ppe_notes"] or "",
        "glove_notes": row["glove_notes"] or "",
        "storage_notes": row["storage_notes"] or "",
    }


def list_chemicals(con: sqlite3.Connection, query: str = "", today: date | None = None) -> list[dict]:
    pattern = _like(query.strip().lower())
    rows = con.execute(
        f"""SELECT {_CHEMICAL_COLUMNS}
           FROM chemicals
           WHERE lower(name) LIKE ? ESCAPE '\\'
              OR lower(location) LIKE ? ESCAPE '\\'
              OR lower(qr_id) LIKE ? ESCAPE '\\'
              OR lower(sds_document) LIKE ? ESCAPE '\\'
           ORDER BY id DESC""",
        (pattern, pattern, pattern, pattern),
    ).fetchall()
    return [_chemical_from_row(row, today) for row in rows]


def get_chemical(con: sqlite3.Connection, chem_id: int) -> dict | None:
    row = con.execute(
        f"""SELECT {_CHEMICAL_COLUMNS}
           FROM chemicals WHERE id = ?""",
        (chem_id,),
    ).fetchone()
    if row is None:
        return None
    return _chemical_from_row(row)


def add_chemical(
    con: sqlite3.Connection,
    fields: Mapping,
    created_at: str = "",
    updated_at: str = "",
) -> int:
    checked = validate_chemical_fields(**fields)
    stamp = local_now()
    created = created_at or stamp
    updated = updated_at or stamp
    with _Transaction(con):
        cursor = con.execute(
            """INSERT INTO chemicals(
                   name, quantity, unit, location, expiry, status,
                   created_at, updated_at, sds_document, sds_revision, qr_id,
                   purpose, hazard_notes, ghs_codes, ppe_notes, glove_notes, storage_notes
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                checked["name"],
                checked["quantity"],
                checked["unit"],
                checked["location"],
                checked["expiry"],
                expiry_status(checked["expiry"]),
                created,
                updated,
                checked["sds_document"],
                checked["sds_revision"],
                checked["qr_id"],
                checked["purpose"],
                checked["hazard_notes"],
                checked["ghs_codes"],
                checked["ppe_notes"],
                checked["glove_notes"],
                checked["storage_notes"],
            ),
        )
        return int(cursor.lastrowid)


def update_chemical(con: sqlite3.Connection, chem_id: int, fields: Mapping) -> bool:
    provided = dict(fields)
    checked = validate_chemical_fields(**provided)
    current = get_chemical(con, chem_id)
    if current is not None:
        for key in CHEMICAL_NOTES:
            if key not in provided:
                checked[key] = current[key]
    with _Transaction(con):
        cursor = con.execute(
            """UPDATE chemicals
               SET name = ?, quantity = ?, unit = ?, location = ?, expiry = ?, status = ?,
                   updated_at = ?, sds_document = ?, sds_revision = ?, qr_id = ?,
                   purpose = ?, hazard_notes = ?, ghs_codes = ?, ppe_notes = ?,
                   glove_notes = ?, storage_notes = ?
               WHERE id = ?""",
            (
                checked["name"],
                checked["quantity"],
                checked["unit"],
                checked["location"],
                checked["expiry"],
                expiry_status(checked["expiry"]),
                local_now(),
                checked["sds_document"],
                checked["sds_revision"],
                checked["qr_id"],
                checked["purpose"],
                checked["hazard_notes"],
                checked["ghs_codes"],
                checked["ppe_notes"],
                checked["glove_notes"],
                checked["storage_notes"],
                chem_id,
            ),
        )
        return cursor.rowcount > 0


def save_calculation(con: sqlite3.Connection, module: str, inputs: dict, result) -> int:
    if module not in CALC_MODULES:
        raise ValueError(module)
    import json

    with _Transaction(con):
        cursor = con.execute(
            """INSERT INTO calculation_history(
                   module, created_at, status, code, formula, value, unit, detail, inputs_json
               ) VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                module,
                local_now(),
                result.status,
                result.code,
                result.formula,
                result.value,
                result.unit,
                result.detail,
                json.dumps(inputs, ensure_ascii=False),
            ),
        )
        return int(cursor.lastrowid)


def add_library_chemical(
    con: sqlite3.Connection,
    *,
    name: object,
    formula: object = "",
    category: object = "",
    user_note: object = "",
) -> int:
    """Store a library identity the user typed. This does not verify hazards."""
    if not isinstance(name, str) or not isinstance(formula, str) or not isinstance(user_note, str):
        raise ValidationError("text_too_long")
    cleaned = " ".join(name.split())
    if not cleaned:
        raise ValidationError("name_required")
    if len(cleaned) > 120 or len(formula.strip()) > 40 or len(user_note.strip()) > 500:
        raise ValidationError("text_too_long")
    if category not in LIBRARY_CATEGORIES:
        raise ValidationError("category_invalid")
    with _Transaction(con):
        cursor = con.execute(
            """INSERT INTO library_additions(name, formula, category, user_note, created_at)
               VALUES(?,?,?,?,?)""",
            (cleaned, formula.strip(), category, user_note.strip(), local_now()),
        )
        return int(cursor.lastrowid)


def add_product_label(
    con: sqlite3.Connection,
    *,
    name: str,
    label_concentration: str = "",
    label_density: str = "",
    sds_source: str = "",
) -> int:
    """Store label text exactly as typed. Verification stays unverified."""
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("name_required")
    for value in (label_concentration, label_density, sds_source):
        if not isinstance(value, str) or len(value) > 300:
            raise ValidationError("text_too_long")
    with _Transaction(con):
        cursor = con.execute(
            """INSERT INTO product_labels(
                   name, label_concentration, label_density, sds_source, verification, created_at
               ) VALUES(?,?,?,?,?,?)""",
            (name.strip(), label_concentration.strip(), label_density.strip(), sds_source.strip(), "unverified", local_now()),
        )
        return int(cursor.lastrowid)


def list_product_labels(con: sqlite3.Connection) -> list[dict]:
    rows = con.execute(
        """SELECT id, name, label_concentration, label_density, sds_source, verification, created_at
           FROM product_labels ORDER BY id"""
    ).fetchall()
    return [dict(row) for row in rows]


def record_stock_movement(
    con: sqlite3.Connection,
    *,
    chemical_id: int,
    direction: str,
    quantity: object,
    note: str = "",
) -> dict:
    """Adjust an inventory quantity and keep the movement. Does not judge safety."""
    from app.validation import parse_quantity

    if direction not in {"in", "out"}:
        raise ValidationError("status_invalid")
    amount = parse_quantity(quantity)
    if amount <= 0:
        raise ValidationError("quantity_invalid")
    if not isinstance(note, str) or len(note) > 300:
        raise ValidationError("text_too_long")
    current = get_chemical(con, chemical_id)
    if current is None:
        raise ValidationError("name_required")
    updated = current["quantity"] + amount if direction == "in" else current["quantity"] - amount
    if updated < 0:
        raise ValidationError("quantity_negative")
    with _Transaction(con):
        updated_rows = con.execute(
            "UPDATE chemicals SET quantity = ?, updated_at = ? WHERE id = ?",
            (updated, local_now(), chemical_id),
        ).rowcount
        if updated_rows != 1:
            raise ValidationError("name_required")
        cursor = con.execute(
            """INSERT INTO stock_movements(chemical_id, direction, quantity, unit, note, created_at)
               VALUES(?,?,?,?,?,?)""",
            (chemical_id, direction, amount, current["unit"], note.strip(), local_now()),
        )
    return {"id": int(cursor.lastrowid), "quantity": updated, "unit": current["unit"]}


def list_stock_movements(con: sqlite3.Connection, chemical_id: int | None = None) -> list[dict]:
    if chemical_id is None:
        rows = con.execute(
            """SELECT id, chemical_id, direction, quantity, unit, note, created_at
               FROM stock_movements ORDER BY id DESC LIMIT 50"""
        ).fetchall()
    else:
        rows = con.execute(
            """SELECT id, chemical_id, direction, quantity, unit, note, created_at
               FROM stock_movements WHERE chemical_id = ? ORDER BY id DESC LIMIT 50""",
            (chemical_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_library_additions(con: sqlite3.Connection) -> list[dict]:
    rows = con.execute(
        """SELECT id, name, formula, category, user_note, created_at
           FROM library_additions ORDER BY id"""
    ).fetchall()
    return [dict(row) for row in rows]


def list_calculations(con: sqlite3.Connection, module: str = "") -> list[dict]:
    if module:
        rows = con.execute(
            """SELECT id, module, created_at, status, code, formula, value, unit, detail
               FROM calculation_history WHERE module = ? ORDER BY id DESC LIMIT 50""",
            (module,),
        ).fetchall()
    else:
        rows = con.execute(
            """SELECT id, module, created_at, status, code, formula, value, unit, detail
               FROM calculation_history ORDER BY id DESC LIMIT 50"""
        ).fetchall()
    return [dict(row) for row in rows]


def delete_chemical(con: sqlite3.Connection, chem_id: int) -> bool:
    with _Transaction(con):
        cursor = con.execute("DELETE FROM chemicals WHERE id = ?", (chem_id,))
        return cursor.rowcount > 0


def add_incident(con: sqlite3.Connection, fields: Mapping) -> int:
    checked = validate_incident_fields(**fields)
    stamp = local_now()
    created = checked["created_at"] or stamp
    updated = checked["updated_at"] or created
    with _Transaction(con):
        cursor = con.execute(
            """INSERT INTO incidents(
                   kind, severity, description, created_at, status, owner,
                   corrective_action, updated_at
               ) VALUES(?,?,?,?,?,?,?,?)""",
            (
                checked["kind"],
                checked["severity"],
                checked["description"],
                created,
                checked["status"],
                checked["owner"],
                checked["corrective_action"],
                updated,
            ),
        )
        return int(cursor.lastrowid)


def list_incidents(con: sqlite3.Connection) -> list[dict]:
    rows = con.execute(
        """SELECT id, kind, severity, description, created_at, status, owner,
                  corrective_action, updated_at
           FROM incidents ORDER BY id DESC"""
    ).fetchall()
    return [
        {
            "id": int(row["id"]),
            "kind": row["kind"],
            "severity": row["severity"],
            "description": row["description"],
            "created_at": row["created_at"],
            "status": row["status"],
            "owner": row["owner"] or "",
            "corrective_action": row["corrective_action"] or "",
            "updated_at": row["updated_at"] or "",
        }
        for row in rows
    ]


def add_inspection(con: sqlite3.Connection, fields: Mapping) -> int:
    checked = validate_inspection(**fields)
    with _Transaction(con):
        cursor = con.execute(
            """INSERT INTO inspection_sessions(inspected_on, inspector, created_at, note)
               VALUES(?,?,?,?)""",
            (checked["inspected_on"], checked["inspector"], local_now(), ""),
        )
        session_id = int(cursor.lastrowid)
        for key in CHECK_KEYS:
            con.execute(
                "INSERT INTO inspection_items(session_id, item_key, checked) VALUES(?,?,?)",
                (session_id, key, 1 if checked["items"][key] else 0),
            )
        return session_id


def list_inspection_rows(con: sqlite3.Connection) -> list[dict]:
    rows = con.execute(
        """SELECT s.id AS session_id, s.inspected_on, s.inspector, s.created_at,
                  i.item_key, i.checked
           FROM inspection_sessions AS s
           JOIN inspection_items AS i ON i.session_id = s.id"""
    ).fetchall()
    order = {key: index for index, key in enumerate(CHECK_KEYS)}
    parsed = [
        {
            "session_id": int(row["session_id"]),
            "inspected_on": row["inspected_on"],
            "inspector": row["inspector"] or "",
            "created_at": row["created_at"],
            "item_key": row["item_key"],
            "checked": bool(row["checked"]),
        }
        for row in rows
    ]
    parsed.sort(key=lambda row: (-row["session_id"], order.get(row["item_key"], 99), row["item_key"]))
    return parsed


def counts(con: sqlite3.Connection) -> dict[str, int]:
    def one(sql: str) -> int:
        return int(con.execute(sql).fetchone()[0])

    return {
        "chemicals": one("SELECT COUNT(*) FROM chemicals"),
        "inspections": one("SELECT COUNT(*) FROM inspection_sessions"),
        "incidents": one("SELECT COUNT(*) FROM incidents"),
    }


def _rows(con: sqlite3.Connection, sql: str) -> list[dict]:
    return [dict(row) for row in con.execute(sql).fetchall()]


def export_backup(con: sqlite3.Connection) -> dict:
    return {
        "app": "LabGuard AI",
        "schema_version": SCHEMA_VERSION,
        "exported_at": local_now(),
        "disclaimer": BACKUP_DISCLAIMER,
        "chemicals": _rows(
            con,
            """SELECT id, name, quantity, unit, location, expiry, created_at, updated_at,
                      sds_document, sds_revision, qr_id, purpose, hazard_notes, ghs_codes,
                      ppe_notes, glove_notes, storage_notes
               FROM chemicals ORDER BY id""",
        ),
        "incidents": _rows(
            con,
            """SELECT id, kind, severity, description, created_at, status, owner,
                      corrective_action, updated_at
               FROM incidents ORDER BY id""",
        ),
        "inspection_sessions": _rows(
            con,
            """SELECT id, inspected_on, inspector, created_at, note
               FROM inspection_sessions ORDER BY id""",
        ),
        "inspection_items": _rows(
            con,
            """SELECT session_id, item_key, checked
               FROM inspection_items ORDER BY session_id, id""",
        ),
        "calculation_history": _rows(
            con,
            """SELECT module, created_at, status, code, formula, value, unit, detail, inputs_json
               FROM calculation_history ORDER BY id""",
        ),
    }


def _as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise BackupError("backup_invalid")
    return value


def _guard(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ValidationError as exc:
        raise BackupError("backup_invalid") from exc


def _checked_list(payload: dict, key: str) -> list:
    value = payload.get(key)
    if not isinstance(value, list):
        raise BackupError("backup_invalid")
    return value


def import_backup(con: sqlite3.Connection, payload: object) -> dict[str, int]:
    if not isinstance(payload, dict):
        raise BackupError("backup_invalid")
    version = payload.get("schema_version")
    if version not in {2, SCHEMA_VERSION}:
        raise BackupError("backup_version")

    chemical_rows = []
    for row in _checked_list(payload, "chemicals"):
        if not isinstance(row, dict):
            raise BackupError("backup_invalid")
        fields = _guard(
            validate_chemical_fields,
            name=row.get("name"),
            quantity=row.get("quantity"),
            unit=row.get("unit"),
            location=row.get("location"),
            expiry=row.get("expiry") or "",
            sds_document=row.get("sds_document") or "",
            sds_revision=row.get("sds_revision") or "",
            qr_id=row.get("qr_id") or "",
            purpose=row.get("purpose") or "",
            hazard_notes=row.get("hazard_notes") or "",
            ghs_codes=row.get("ghs_codes") or "",
            ppe_notes=row.get("ppe_notes") or "",
            glove_notes=row.get("glove_notes") or "",
            storage_notes=row.get("storage_notes") or "",
        )
        fields["created_at"] = _guard(parse_timestamp, row.get("created_at") or "")
        fields["updated_at"] = _guard(parse_timestamp, row.get("updated_at") or "")
        chemical_rows.append(fields)

    incident_rows = []
    for row in _checked_list(payload, "incidents"):
        if not isinstance(row, dict):
            raise BackupError("backup_invalid")
        incident_rows.append(
            _guard(
                validate_incident_fields,
                kind=row.get("kind"),
                severity=row.get("severity"),
                description=row.get("description"),
                status=row.get("status") or "open",
                owner=row.get("owner") or "",
                corrective_action=row.get("corrective_action") or "",
                created_at=row.get("created_at") or "",
                updated_at=row.get("updated_at") or "",
            )
        )

    session_rows = []
    seen_sessions: set[int] = set()
    for row in _checked_list(payload, "inspection_sessions"):
        if not isinstance(row, dict):
            raise BackupError("backup_invalid")
        session_id = _as_int(row.get("id"))
        if session_id in seen_sessions:
            raise BackupError("backup_invalid")
        seen_sessions.add(session_id)
        day = _guard(parse_expiry, row.get("inspected_on") if isinstance(row.get("inspected_on"), str) else "bad")
        if not day:
            raise BackupError("backup_invalid")
        inspector_raw = row.get("inspector") or ""
        if not isinstance(inspector_raw, str):
            raise BackupError("backup_invalid")
        inspector = " ".join(inspector_raw.split())
        if len(inspector) > 120:
            raise BackupError("backup_invalid")
        note = row.get("note") or ""
        if not isinstance(note, str) or len(note.strip()) > 500:
            raise BackupError("backup_invalid")
        session_rows.append(
            {
                "id": session_id,
                "inspected_on": day,
                "inspector": inspector,
                "created_at": _guard(parse_timestamp, row.get("created_at") or ""),
                "note": note.strip(),
            }
        )

    grouped: dict[int, dict[str, bool]] = {row["id"]: {} for row in session_rows}
    for row in _checked_list(payload, "inspection_items"):
        if not isinstance(row, dict):
            raise BackupError("backup_invalid")
        session_id = _as_int(row.get("session_id"))
        key = row.get("item_key")
        if session_id not in grouped or key not in CHECK_KEYS or key in grouped[session_id]:
            raise BackupError("backup_invalid")
        checked = row.get("checked")
        if isinstance(checked, bool):
            grouped[session_id][key] = checked
        elif isinstance(checked, int) and not isinstance(checked, bool) and checked in (0, 1):
            grouped[session_id][key] = bool(checked)
        else:
            raise BackupError("backup_invalid")
    for session_id, item_map in grouped.items():
        if set(item_map) != set(CHECK_KEYS):
            raise BackupError("backup_invalid")

    if version == 2:
        history_rows = payload.get("calculation_history") or []
    else:
        history_rows = _checked_list(payload, "calculation_history")
    if not isinstance(history_rows, list):
        raise BackupError("backup_invalid")
    parsed_history = []
    for row in history_rows:
        if not isinstance(row, dict) or row.get("module") not in CALC_MODULES:
            raise BackupError("backup_invalid")
        if row.get("status") not in {"ok", "blocked"} or not isinstance(row.get("code"), str):
            raise BackupError("backup_invalid")
        parsed_history.append(row)

    with _Transaction(con):
        con.execute("DELETE FROM calculation_history")
        con.execute("DELETE FROM inspection_items")
        con.execute("DELETE FROM inspection_sessions")
        con.execute("DELETE FROM incidents")
        con.execute("DELETE FROM chemicals")
        for fields in chemical_rows:
            created = fields["created_at"] or local_now()
            updated = fields["updated_at"] or created
            con.execute(
                """INSERT INTO chemicals(
                       name, quantity, unit, location, expiry, status,
                       created_at, updated_at, sds_document, sds_revision, qr_id,
                       purpose, hazard_notes, ghs_codes, ppe_notes, glove_notes, storage_notes
                   ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    fields["name"],
                    fields["quantity"],
                    fields["unit"],
                    fields["location"],
                    fields["expiry"],
                    expiry_status(fields["expiry"]),
                    created,
                    updated,
                    fields["sds_document"],
                    fields["sds_revision"],
                    fields["qr_id"],
                    fields["purpose"],
                    fields["hazard_notes"],
                    fields["ghs_codes"],
                    fields["ppe_notes"],
                    fields["glove_notes"],
                    fields["storage_notes"],
                ),
            )
        for fields in incident_rows:
            created = fields["created_at"] or local_now()
            updated = fields["updated_at"] or created
            con.execute(
                """INSERT INTO incidents(
                       kind, severity, description, created_at, status, owner,
                       corrective_action, updated_at
                   ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    fields["kind"],
                    fields["severity"],
                    fields["description"],
                    created,
                    fields["status"],
                    fields["owner"],
                    fields["corrective_action"],
                    updated,
                ),
            )
        id_map: dict[int, int] = {}
        for fields in session_rows:
            cursor = con.execute(
                """INSERT INTO inspection_sessions(inspected_on, inspector, created_at, note)
                   VALUES(?,?,?,?)""",
                (
                    fields["inspected_on"],
                    fields["inspector"],
                    fields["created_at"] or local_now(),
                    fields["note"],
                ),
            )
            id_map[fields["id"]] = int(cursor.lastrowid)
        for session_id, item_map in grouped.items():
            for key in CHECK_KEYS:
                con.execute(
                    "INSERT INTO inspection_items(session_id, item_key, checked) VALUES(?,?,?)",
                    (id_map[session_id], key, 1 if item_map[key] else 0),
                )
        for row in parsed_history:
            con.execute(
                """INSERT INTO calculation_history(
                       module, created_at, status, code, formula, value, unit, detail, inputs_json
                   ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    row["module"],
                    row.get("created_at") or local_now(),
                    row["status"],
                    row["code"],
                    row.get("formula") or "",
                    row.get("value"),
                    row.get("unit") or "",
                    row.get("detail") or "",
                    row.get("inputs_json") or "",
                ),
            )
    return counts(con)
