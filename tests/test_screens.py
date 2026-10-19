import os

import pytest

from app.i18n import t
from app.training import QUIZ, score_quiz


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_quiz_answers_are_the_product_limits():
    assert [item["answer"] for item in QUIZ] == [1, 1, 1]
    correct, total = score_quiz([1, 1, 1])
    assert (correct, total) == (3, 3)
    assert score_quiz([0, 0, 0]) == (0, 3)
    assert "does not prove" in t("quiz_q1_b", "en").lower()
    assert "disabled" in t("quiz_q3_b", "en").lower()


def test_new_screens_buttons_and_empty_safety_record(qapp, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from app.main_window import LabGuard

    window = LabGuard(db_path=tmp_path / "lab.db")
    window.c_name.setText("Örnek kap")
    window.c_qty.setText("2")
    window.c_loc.setText("Raf 1")
    window.c_exp.setText("2020-01-01")
    window.editing_id = None
    from PySide6.QtWidgets import QMessageBox

    def accept():
        for widget in qapp.topLevelWidgets():
            if isinstance(widget, QMessageBox):
                widget.accept()

    from PySide6.QtCore import QTimer

    QTimer.singleShot(50, accept)
    window.save_chemical()
    qapp.processEvents()
    accept()
    assert window.chem_table.rowCount() == 1
    assert window.chem_table.item(0, 5).text() == t("status_expired", "tr")

    window.navigate("calc")
    window.calc_page.c1.setText("12")
    window.calc_page.v1.setText("")
    window.calc_page.c2.setText("0.1")
    window.calc_page.v2.setText("1000")
    window.calc_page.basis.setCurrentText("mol/L")
    dilution = window.calc_page.calculate_dilution()
    assert dilution.status == "ok"
    assert dilution.value == pytest.approx(1000 * 0.1 / 12)
    assert "not a mixing" in dilution.detail
    assert t("dilution_ok", "tr") in window.calc_page.dilution_result.text()

    blocked = window.calc_page.calculate_hazardous()
    assert blocked.value is None
    assert blocked.code == "hazardous_dilution_disabled"
    assert "mL" not in window.calc_page.hazard_result.text()
    assert t("hazardous_dilution_disabled", "tr") in window.calc_page.hazard_result.text()

    window.calc_page.mud_weight.setText("10")
    window.calc_page.tvd.setText("1000")
    window.calc_page.pressure_loss.setText("")
    hydrostatic = window.calc_page.calculate_hydrostatic()
    assert hydrostatic.value == pytest.approx(10 * 1000 * 12 / 231)
    missing = window.calc_page.calculate_ecd()
    assert missing.value is None
    assert missing.code == "pressure_loss_required"

    window.calc_page.on_hand.setText("10")
    window.calc_page.on_hand_unit.setText("L")
    window.calc_page.use_per_day.setText("2")
    window.calc_page.use_unit.setText("L")
    stock = window.calc_page.calculate_stock()
    assert stock.value == pytest.approx(5)
    window.calc_page.flow.setText("100")
    window.calc_page.hole_id.setText("8.5")
    window.calc_page.pipe_od.setText("5")
    velocity = window.calc_page.calculate_velocity()
    assert velocity.status == "ok"
    assert velocity.value is not None
    assert window.calc_page.latest.isHidden() is False
    assert "ft/min" in window.calc_page.latest.text()
    assert window.calc_page.history.rowCount() >= 5

    window.set_language("en")
    assert window.nav_buttons["calc"].text().endswith("Calculations")
    assert window.calc_page.tabs.tabText(0)
    window.set_language("tr")

    from PySide6.QtCore import Qt

    window.chem_table.selectRow(0)
    window.editing_id = window.chem_table.item(0, 0).data(Qt.UserRole)
    window.open_detail()
    assert window.detail_page.hazard_notes.text() == ""
    assert window.detail_page.ghs_empty.isHidden() is False
    assert window.detail_page.ghs_marks.text() == ""
    assert "tahmin etmez" in window.detail_page.disclaimer.text()
    window.detail_page.purpose.setText("Laboratuvar kaydı")
    window.detail_page.ghs_boxes["corrosion"].setChecked(True)
    window.save_detail_record()
    assert window.detail_page.purpose.text() == "Laboratuvar kaydı"
    assert "Aşındırıcı" in window.detail_page.ghs_marks.text()
    assert "Alev" not in window.detail_page.ghs_marks.text()

    window.resize(1180, 780)
    window.show()
    qapp.processEvents()
    window.navigate("prepare")
    window.grab().save("/tmp/labguard-prepare.png")
    window.navigate("calc")
    window.grab().save("/tmp/labguard-calc.png")
    window.navigate("detail")
    window.grab().save("/tmp/labguard-detail.png")
    window.close()
