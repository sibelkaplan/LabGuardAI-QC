from app.constants import (
    CHECK_KEYS,
    INCIDENT_KINDS,
    INCIDENT_STATUSES,
    PAGE_KEYS,
    PPE_KEYS,
    SEVERITIES,
)
from app.i18n import EN, TR, catalog, t
from app.validation import BACKUP_CODES, ERROR_CODES, STATUS_I18N


def test_catalogs_have_the_same_keys():
    assert set(TR) == set(EN)
    assert TR
    for key, value in TR.items():
        assert value.strip()
        assert EN[key].strip()


def test_unknown_key_is_returned():
    assert t("missing-key", "en") == "missing-key"
    assert t("dashboard", "en") == "Overview"
    assert t("dashboard", "tr") == "Genel Bakış"
    assert catalog("fr") is TR


def test_domain_and_error_keys_are_translated():
    required = (
        list(PAGE_KEYS)
        + list(CHECK_KEYS)
        + list(PPE_KEYS)
        + list(INCIDENT_KINDS)
        + list(SEVERITIES)
        + list(INCIDENT_STATUSES)
        + list(ERROR_CODES)
        + list(BACKUP_CODES)
        + list(STATUS_I18N.values())
        + ["file_failed", "checked_yes", "checked_no"]
    )
    for key in required:
        assert key in EN
        assert key in TR


def test_safety_boundaries_are_stated_in_english():
    en = catalog("en")
    assert "placeholder" in en["assistant_note"].lower()
    assert "does not" in en["assistant_note"].lower()
    assert "not proof" in en["inspection_note"].lower()
    assert "does not scan" in en["qr_hint"].lower()
    assert "does not" in en["sds_hint"].lower()
    assert "does not" in en["expiry_note"].lower()
    assert "glove compatibility" in en["ppe_note"].lower()
    assert "do not authorize" in en["demo_banner"].lower()
    assert "validated" in en["demo_banner"].lower()
