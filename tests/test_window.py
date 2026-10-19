import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.database import add_chemical
from app.i18n import t

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_language_switch_refreshes_visible_text_and_records(qapp, tmp_path):
    from app.main_window import LabGuard

    window = LabGuard(db_path=tmp_path / "lab.db")
    add_chemical(
        window.con,
        {
            "name": "Sample container",
            "quantity": "1",
            "unit": "L",
            "location": "Cabinet A",
            "expiry": "2020-01-01",
            "qr_id": "QR-1",
        },
    )
    window.show()
    window.navigate("inventory")
    window.refresh_chemicals()

    assert window.nav_buttons["inventory"].text().endswith("Kimyasal Envanteri")
    assert window.c_name_label.text() == "Kimyasal adı"
    assert window.search.placeholderText() == "Kimyasal ara…"
    assert window.chem_table.horizontalHeaderItem(0).text() == "Kimyasal adı"
    assert "doğrulanmış" in window.banner.text()
    assert "QR kod taramaz" in window.qr_hint.text()

    window.set_language("en")
    assert window.nav_buttons["inventory"].text().endswith("Chemical Inventory")
    assert window.c_name_label.text() == "Chemical name"
    assert window.search.placeholderText() == "Search chemicals…"
    assert window.chem_table.horizontalHeaderItem(0).text() == "Chemical name"
    assert window.chem_table.horizontalHeaderItem(5).text() == "Status"
    assert window.chem_table.item(0, 0).text() == "Sample container"
    assert window.chem_table.item(0, 5).text() == t("status_expired", "en")
    assert window.i_type.currentData() == "spill"
    assert window.i_type.itemText(0) == "Chemical spill"
    assert window.checkboxes[0][1].text() == t("eyewash", "en")
    assert "placeholder" in window.assistant_note.text().lower()
    assert "not proof" in window.inspection_note.text().lower()
    assert "DEMO" in window.banner.text()
    assert "not a validated safety system" in window.banner.text().lower()
    assert window.lang_btn.text() == "Türkçe"

    window.set_language("tr")
    assert window.i_type.itemText(0) == "Kimyasal dökülme"
    assert window.i_type.currentData() == "spill"
    assert window.chem_table.item(0, 5).text() == t("status_expired", "tr")
    window.close()


def test_script_entry_point_opens_without_touching_the_home_database(tmp_path):
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["LABGUARD_EXIT_AFTER_SHOW"] = "1"
    env["LABGUARD_DB"] = str(tmp_path / "lab.db")
    result = subprocess.run(
        [sys.executable, "app/main.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=40,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert Path(env["LABGUARD_DB"]).exists()
