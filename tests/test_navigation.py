"""Page history, the local tutor panel, and content search."""

import os

import pytest

from app.learn_routes import search_targets
from app.local_tutor import answer


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_search_reaches_a_chemical_and_a_lesson():
    bernard = search_targets("Bernard kalsimetresi")
    assert bernard[0][1] == "bernard"
    assert "Ders" in bernard[0][2]
    chemicals = search_targets("Hidroklorik asit")
    assert any(item[0] == "chemical" and item[1] == "hcl" for item in chemicals)
    assert search_targets("Asit seyreltme hesabı")[0] == ("page", "prepare", "Asit hazırlama")


def test_example_questions_stay_on_stored_lessons():
    bernard = answer("Bernard kalsimetresi nasıl çalışır?", "", "tr")
    assert bernard["remote"] is False
    assert bernard["open_id"] == "bernard"
    assert "Bağlı bir yapay zekâ servisi yok" in bernard["text"]
    gypsum = answer("Jips ile anhidriti ayırırken nelere dikkat edilir?", "", "tr")
    assert gypsum["open_id"] == "mineral-split"
    assert "Renk" in gypsum["text"]
    sample = answer("Numune nasıl hazırlanır?", "", "tr")
    assert sample["open_id"] == "sample-wash"
    device = answer("Bu laboratuvar cihazı ne işe yarar?", "", "tr")
    assert device["open_id"] == ""
    assert "kılavuz" in device["text"].casefold()


def test_back_returns_through_lesson_library_and_home(qapp, tmp_path):
    from PySide6.QtWidgets import QApplication

    from app.main_window import LabGuard

    window = LabGuard(db_path=tmp_path / "lab.db")
    window.resize(1200, 780)
    window.show()
    QApplication.processEvents()
    assert window.back_button.isHidden()

    window.navigate("library")
    assert window.back_button.isVisible()
    assert window.back_button.text() == "← Geri"
    window.library_page.open_record("hcl")
    assert window.library_page.stack.currentIndex() == 1
    window.library_page.back_button.click()
    assert window.library_page.stack.currentIndex() == 0
    assert window._current_page == "library"
    window.go_back()
    assert window._current_page == "home"
    assert window.back_button.isHidden()

    window.home_page.mud_card.button.click()
    QApplication.processEvents()
    assert window.mud_page._category == "devices"
    window.mud_page.open_lesson("bernard")
    assert window.mud_page.stack.currentIndex() == 1
    window.back_button.click()
    assert window.mud_page.stack.currentIndex() == 0
    assert window.mud_page._category == "devices"
    window.back_button.click()
    assert window._current_page == "home"

    window.tutor_dock.launcher.click()
    QApplication.processEvents()
    assert window.tutor_dock.panel.isVisible()
    assert window._current_page == "home"
    window.tutor_dock.ask("Floresans neyi gösterebilir?")
    assert window.tutor_dock.panel.isVisible()
    assert "kesin kanıt" in window.tutor_dock.answer.text().casefold() or "kanıt" in window.tutor_dock.answer.text().casefold()
    assert window.tutor_dock.link.isVisible()
    window.tutor_dock.link.click()
    QApplication.processEvents()
    assert window.tutor_dock.panel.isHidden()
    assert window.mud_page._open_id == "uv"
    window.back_button.click()
    assert window._current_page == "home"
    window.set_language("en")
    assert window.back_button.text() == "← Back"
    window.close()
