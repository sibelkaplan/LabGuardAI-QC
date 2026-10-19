import os

import pytest

from app.calc.preparation import is_hcl_example, review_preparation


def test_hcl_example_is_recognized_without_a_stored_density():
    assert is_hcl_example("HCl", "32", "18,5")
    assert is_hcl_example("Hidroklorik asit", 32, 18.5)
    assert not is_hcl_example("HCl", "32", "10")


def test_same_basis_ratio_is_not_an_approval_and_mass_percent_has_no_volume():
    mass = review_preparation(
        name="HCl",
        c1="32",
        basis="percent_w_w",
        c2="18.5",
        volume="1000",
        volume_unit="mL",
        density="1.18",
        sds_basis_checked=True,
        sds_density_checked=True,
        procedure_checked=True,
    )
    assert mass.value is None
    assert mass.math_value is None
    assert mass.density_required is True
    assert mass.math_code == "prep_ww_volume_blocked"
    assert "578" not in mass.detail

    volume = review_preparation(
        name="HCl",
        c1="32",
        basis="percent_v_v",
        c2="18.5",
        volume="1000",
        volume_unit="mL",
        density="1.18",
        sds_basis_checked=True,
        procedure_checked=True,
    )
    assert volume.value is None
    assert volume.code == "prepare_no_quantity"
    assert volume.math_value == pytest.approx(578.1)
    assert volume.math_unit == "mL"
    assert volume.density_required is False
    without_density = review_preparation(
        name="HCl",
        c1="32",
        basis="percent_v_v",
        c2="18.5",
        volume="1000",
        volume_unit="mL",
    )
    assert without_density.math_value == volume.math_value

    mixed = review_preparation(
        name="HCl",
        c1="32",
        basis="",
        c2="18.5",
        volume="1000",
        volume_unit="mL",
    )
    assert mixed.math_value is None
    assert mixed.code == "prepare_invalid"


def test_preparation_review_never_returns_a_quantity():
    blocked = review_preparation(
        name="HCl",
        c1="32",
        basis="percent_w_w",
        c2="18.5",
        volume="1000",
        volume_unit="mL",
        density="1.16",
        sds_basis_checked=True,
        sds_density_checked=True,
        procedure_checked=True,
    )
    assert blocked.value is None
    assert blocked.status == "blocked"
    assert blocked.code == "prepare_no_quantity"
    assert "578" not in blocked.detail

    missing = review_preparation(
        name="HCl",
        c1="32",
        basis="",
        c2="18.5",
        volume="1000",
        volume_unit="mL",
    )
    assert missing.value is None
    assert missing.code == "prepare_invalid"

    not_lower = review_preparation(
        name="HCl",
        c1="10",
        basis="mol/L",
        c2="10",
        volume="1",
        volume_unit="L",
        density="1.0",
    )
    assert not_lower.value is None
    assert not_lower.code == "prepare_not_lower"


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_wizard_navigation_example_and_no_quantity(qapp, tmp_path):
    from PySide6.QtWidgets import QApplication

    from app.main_window import LabGuard

    window = LabGuard(db_path=tmp_path / "lab.db")
    wizard = window.wizard
    assert window.pages.currentWidget() is window.home_page
    window.home_page.prepare_card.button.click()
    assert window.pages.currentWidget() is wizard
    assert wizard.step == 0
    assert wizard.start_button.text() == "Yeni hazırlama başlat"
    assert "placeholder" in wizard.assistant_note.text().lower() or "yer tutucu" in wizard.assistant_note.text().lower()

    wizard.next_button.click()
    assert wizard.step == 0

    wizard.start_button.click()
    assert wizard.step == 1
    wizard.next_button.click()
    assert wizard.step == 1
    assert wizard.step_error.isHidden() is False

    wizard.example_button.click()
    assert wizard.step == 1
    assert wizard.name_edit.text() == "HCl"
    assert wizard.c1_edit.text() == "32"
    assert wizard.c2_edit.text() == "18,5"
    assert wizard.basis_value() == ""

    wizard.go_next()
    assert wizard.step == 2
    assert wizard.example_basis_note.isHidden() is False
    wizard.go_next()
    assert wizard.step == 2

    wizard.basis_buttons["percent_w_w"].setChecked(True)
    wizard.go_back()
    assert wizard.step == 1
    assert wizard.name_edit.text() == "HCl"
    wizard.go_next()
    wizard.go_next()
    assert wizard.step == 3
    assert wizard.c2_edit.text() == "18,5"
    wizard.c2_edit.setText("40")
    wizard.go_next()
    assert wizard.step == 3
    assert "küçük" in wizard.step_error.text()
    wizard.c2_edit.setText("18,5")
    wizard.go_next()
    assert wizard.step == 4
    wizard.volume_edit.setText("1000")
    wizard.volume_unit.setCurrentText("mL")
    wizard.go_next()
    assert wizard.step == 5
    assert "1000 mL" in wizard.summary.text()
    assert "Kütlece" in wizard.summary.text()

    wizard.density_edit.setText("1.16")
    wizard.seen_basis.setChecked(True)
    wizard.seen_density.setChecked(True)
    wizard.seen_procedure.setChecked(True)
    wizard.next_button.click()
    assert wizard.last_result is not None
    assert wizard.last_result.value is None
    text = wizard.result_label.text()
    assert "üretilmedi" in text
    assert "578" not in text
    assert "mL" not in text.split("C1")[0] or "1000" not in text
    assert wizard.result_label.isHidden() is False

    window.set_language("en")
    assert window.nav_buttons["prepare"].text().endswith("Acid preparation")
    assert wizard.start_button.text() == "Start a new preparation"
    assert "No preparation quantity was produced." in wizard.result_label.text()
    assert "578" not in wizard.result_label.text()
    window.set_language("tr")

    wizard.go_back()
    assert wizard.step == 4
    wizard.back_button.click()
    wizard.back_button.click()
    wizard.back_button.click()
    wizard.back_button.click()
    assert wizard.step == 0
    assert window.nav_buttons["inventory"].text().endswith("Kimyasal Envanteri")
    window.resize(1180, 780)
    window.show()
    QApplication.instance().processEvents()
    window.grab().save("/tmp/labguard-home.png")
    wizard.start_example()
    window.grab().save("/tmp/labguard-step1.png")
    wizard.basis_buttons["percent_v_v"].setChecked(True)
    wizard.go_next()
    wizard.go_next()
    wizard.go_next()
    wizard.volume_edit.setText("500")
    wizard.go_next()
    wizard.next_button.click()
    window.grab().save("/tmp/labguard-check.png")
    window.navigate("inventory")
    assert window.pages.currentIndex() == window._page_index["inventory"]
    window.navigate("inspections")
    assert window.inspection_note.text()
    window.navigate("incidents")
    assert window.incident_note.text()
    window.navigate("prepare")
    assert wizard.step == 5
    window.close()
