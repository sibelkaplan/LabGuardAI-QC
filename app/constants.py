"""Shared domain constants.

Date windows and checklist keys are UI/record fields. They are not chemical
handling rules and they do not authorize work.
"""

PAGE_KEYS = (
    "home",
    "prepare",
    "library",
    "ppe",
    "studio",
    "mudacademy",
    "inventory",
    "calc",
    "inspections",
    "academy",
    "incidents",
)

LIBRARY_CATEGORIES = (
    "acid",
    "base",
    "salt",
    "solvent",
    "mineral",
    "other",
)

# Codes a person may copy from an SDS. The application never assigns them.
GHS_CODES = (
    "explosive",
    "flame",
    "oxidizer",
    "gas",
    "corrosion",
    "skull",
    "exclamation",
    "health",
    "environment",
)

CHEMICAL_NOTES = (
    "purpose",
    "hazard_notes",
    "ghs_codes",
    "ppe_notes",
    "glove_notes",
    "storage_notes",
)

CHECK_KEYS = (
    "eyewash",
    "spillkit",
    "labels",
    "ventilation",
    "emergency",
    "sds",
)

PPE_KEYS = (
    "goggles",
    "gloves",
    "clothing",
    "ventilation",
    "sds",
)

INCIDENT_KINDS = (
    "spill",
    "unlabelled",
    "damaged",
    "missing",
    "near",
)

SEVERITIES = (
    "low",
    "medium",
    "high",
)

INCIDENT_STATUSES = (
    "open",
    "in_progress",
    "closed",
)

UNITS = (
    "L",
    "mL",
    "kg",
    "g",
    "pcs",
)

# Display reminder only: a date inside this window is labelled "expiring soon".
EXPIRING_WITHIN_DAYS = 30

SCHEMA_VERSION = 3
