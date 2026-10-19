# LabGuard AI — Cursor Starter

A starter desktop application for laboratory safety workflows. It uses PySide6 and SQLite.

## Requirements
- macOS with Python 3.11+ (Python 3.12 is a good choice)
- Cursor editor

## Run locally
Open this folder in Cursor. In Cursor's Terminal, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app/main.py
```

If `python3` is not installed, install Python 3 from python.org first.

## Tests
With the virtual environment active:

```bash
python -m pytest
```

## Data
SQLite database is created at:
`~/Library/Application Support/LabGuardAI/labguard.db`

Set `LABGUARD_DB` to a file path if you want a different database.

## What this version stores
- Chemical records with quantity, unit, location, an expiry reminder, an SDS document reference, and a QR identifier
- Weekly inspection history with the inspector, date, timestamp, and each marked item
- Incident reports with type, severity, description, timestamp, status, owner, and corrective action
- JSON export and import of those local records
- Turkish and English text, switched from the sidebar

## Important limitations
- This is a starter/MVP, not a validated or certified safety system.
- The banner marks the app as DEMO. Records stay on this computer and do not authorize work.
- PPE text, academy modules, and date status are reminders, not chemical-specific advice.
- A saved inspection checkbox is not proof that the laboratory is safe.
- No live AI connection, SDS document retrieval, QR scanning, authentication, role-based access, or audit-grade logging is implemented.
- The Safety Assistant is a placeholder. It does not provide procedures, mixing quantities, or work authorization.
- Same-basis dilution arithmetic and unit conversions are calculators, not mixing instructions. Percent by volume, percent by mass, and mass/volume percent are not converted into each other.
- Hazardous product dilution stays disabled. This version does not produce an acid or product handling quantity.
- Chemical detail fields stay empty until someone types them from the current SDS. The application does not estimate hazards, PPE, glove compatibility, or storage.
- Mud-logging results use published unit identities. They do not estimate friction or pump output, and they are not well-control instructions.
- Do not use the application to authorize chemical handling. Connect approved SDS/SOP documents and have a qualified safety professional validate workflows before operational use.
