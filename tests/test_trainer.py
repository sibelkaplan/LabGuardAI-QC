"""Visual lesson shell, local tutor, speech status, and home search."""

import pytest

from app.learn_routes import search_targets
from app.local_tutor import answer


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_search_opens_named_lessons():
    assert search_targets("Bernard kalsimetresi")[0][1] == "bernard"
    assert search_targets("Otomatik kalsimetre")[0][1] == "auto-calcimeter"
    assert search_targets("Saf su cihazı")[0][1] == "pure-water"
    assert search_targets("Fenolftalein")[0][1] == "phenol"
    assert any(item[1] == "calcite" for item in search_targets("Kalsit ve dolomit"))
    assert any(item[1] == "dolomite" for item in search_targets("Kalsit ve dolomit"))
    assert any(item[1] == "uv" for item in search_targets("UV floresansı"))
    assert any(item[1] == "solvent-cut" for item in search_targets("Solvent cut"))
    assert any(item[1] == "chloride" for item in search_targets("Klorür testi"))
    assert search_targets("Asit seyreltme hesabı")[0] == ("page", "prepare", "Asit hazırlama")
    assert search_targets("Eldiven seçimi")[0][1] == "ppe"
    assert search_targets("Kalsimetre neden sonuç vermiyor?")[0][1] == "trouble-gas"


def test_local_tutor_is_not_a_remote_model():
    result = answer("Gaz hacmi karbonat miktarıyla nasıl ilişkilidir?", "bernard", "tr")
    assert result["remote"] is False
    assert "Bağlı bir yapay zekâ servisi yok" in result["text"]
    assert "22,4" in result["text"]
    simple = answer("Bunu daha basit anlat.", "bernard", "tr")
    assert "uzaktan" not in simple["text"].casefold()
    missing = answer("Bu markanın üçüncü tuşu nedir?", "bernard", "tr")
    assert "kılavuz" in missing["text"].casefold()


def test_lesson_shell_speech_tutor_and_favorite(qapp, tmp_path):
    from PySide6.QtWidgets import QApplication

    from app.database import list_favorite_lessons, list_recent_lessons
    from app.main_window import LabGuard

    window = LabGuard(tmp_path / "labguard.db")
    window.show()
    qapp.processEvents()
    window.home_page.search.setText("Bernard kalsimetresi")
    qapp.processEvents()
    window.home_page.results.itemAt(0).widget().click()
    qapp.processEvents()
    page = window.mud_page
    assert page.stack.currentIndex() == 1
    assert page.player is not None
    assert page.player.see_label.text().startswith("Ne görüyorum?")
    assert "Ölçü borusu" in page.player.does_label.text() or "ölçü" in page.player.does_label.text().casefold()
    assert page.details_host.isHidden()
    page.details_button.click()
    assert page.details_host.isVisible()
    page.player.listen_button.click()
    qapp.processEvents()
    status = page.player.speech_status.text()
    assert status
    assert "sessiz" not in status.casefold()
    page.lesson_question.setText("Otomatik kalsimetreden farkı nedir?")
    page._ask_lesson("bernard")
    assert "Bağlı bir yapay zekâ servisi yok" in page.lesson_answer.text()
    assert page._last_tutor["remote"] is False
    page.favorite_button.click()
    assert list_favorite_lessons(window.con) == ["bernard"]
    assert list_recent_lessons(window.con) == ["bernard"]
    window.home_page.favorite_row.itemAt(0).widget().click()
    qapp.processEvents()
    assert window.mud_page._open_id == "bernard"
    window.close()
    QApplication.instance().processEvents()
