"""Handbook-grounded lessons stay original and do not copy recipes."""

import pytest

from app.academy_content import find_lesson, lesson_text
from app.local_tutor import answer


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_handbook_notes_do_not_copy_recipes():
    bernard = lesson_text(find_lesson("bernard"), "tr")
    wash = lesson_text(find_lesson("sample-wash"), "tr")
    fluor = lesson_text(find_lesson("fluor-direct"), "tr")
    phenol = lesson_text(find_lesson("phenol"), "tr")
    chloride = lesson_text(find_lesson("chloride"), "tr")
    sulfate = lesson_text(find_lesson("sulfate"), "tr")
    for text in (bernard, wash, fluor):
        assert "17.5" not in text
        assert "0.2" not in text
        assert "mL" not in text
        assert "%" not in text
        assert "dağıtılmaz" in text
        assert "kopyalanmadı" in text
    assert "bir test yöntemi olarak yok" in phenol
    assert "bir test yöntemi olarak yok" in chloride
    assert "yöntemi yazılmamıştır" in sulfate.casefold() or "Yöntem" in sulfate
    assert "kesin kanıt" in fluor
    assert find_lesson("sample-dry")["animation"] == "dry"
    assert find_lesson("mineral-split")["animation"] == "minerals"


def test_tutor_does_not_invent_a_handbook_recipe():
    result = answer("Elek yıkamasını daha basit anlat", "sample-wash", "tr")
    assert result["remote"] is False
    assert "milimetre" in result["text"].casefold()
    missing = answer("Fenolftalein el kitabında var mı?", "phenol", "tr")
    assert "yok" in missing["text"]
    assert "miktar" in missing["text"]


def test_sample_wash_player_and_listen(qapp, tmp_path):
    from PySide6.QtWidgets import QApplication

    from app.main_window import LabGuard

    window = LabGuard(tmp_path / "labguard.db")
    window.show()
    qapp.processEvents()
    window.home_page.search.setText("Numune yıkama")
    qapp.processEvents()
    window.home_page.results.itemAt(0).widget().click()
    qapp.processEvents()
    page = window.mud_page
    assert page._open_id == "sample-wash"
    assert page.player.animation_id == "wash"
    assert page.player.see_label.text().startswith("Ne görüyorum?")
    page.player.click_fraction(0.20, 0.30)
    assert page.player.selected_part == "coarse"
    page.player.listen_button.click()
    qapp.processEvents()
    assert page.player.speech_status.text()
    assert "dağıtılmaz" in page.detail_plain_text()
    page.open_lesson("bernard")
    assert "17.5" not in page.detail_plain_text()
    assert page.player.animation_id == "bernard"
    page.open_lesson("fluor-direct")
    page.player.show_next()
    assert page.player.current()["visual"] == "fluor_cut"
    window.close()
    QApplication.instance().processEvents()
