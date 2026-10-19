"""Mudlogging Academy lessons and schematic animations."""

import os

import pytest

from app.academy_content import ALL_LESSONS, CATEGORIES, filter_lessons, find_lesson, lesson_text


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_every_category_has_a_lesson_and_tests_do_not_invent_a_recipe():
    assert CATEGORIES == ("devices", "tests", "rocks", "shows", "measure", "safety", "trouble", "samples")
    for category in CATEGORIES:
        assert filter_lessons("", category)
    assert len(filter_lessons("", "devices")) >= 3
    assert find_lesson("bernard")["animation"] == "bernard"
    assert find_lesson("auto-calcimeter")["animation"] == "auto"
    assert find_lesson("pure-water")["animation"] == "water"
    assert find_lesson("safety-ppe")["animation"] == "acid"
    acetone = lesson_text(find_lesson("acetone-test"), "tr")
    chloride = lesson_text(find_lesson("chloride"), "tr")
    for text in (acetone, chloride):
        assert "mL" not in text
        assert "%" not in text
    uv = lesson_text(find_lesson("uv"), "tr")
    assert "kesin kanıtı" in uv
    coal = lesson_text(find_lesson("coal-test"), "tr")
    assert "tek" in coal and "kesin" in coal
    calcite = lesson_text(find_lesson("calcite"), "tr")
    assert "Renk tek başına" in calcite
    auto = lesson_text(find_lesson("auto-calcimeter"), "tr")
    assert "uydurulmaz" in auto
    bernard = lesson_text(find_lesson("bernard"), "tr")
    assert "teorik" in bernard.casefold()
    assert "22,4" in bernard
    assert len(ALL_LESSONS) >= 20


def test_academy_opens_cards_and_animation_controls(qapp, tmp_path):
    from PySide6.QtWidgets import QApplication

    from app.main_window import LabGuard

    window = LabGuard(tmp_path / "labguard.db")
    window.show()
    qapp.processEvents()
    window.home_page.mud_card.button.click()
    qapp.processEvents()
    page = window.mud_page
    assert window._current_page == "mudacademy"
    assert page.visible_lessons()
    page.search.setText("Bernard")
    qapp.processEvents()
    assert any(lesson["id"] == "bernard" for lesson in page.visible_lessons())
    page.set_category("devices")
    page.search.clear()
    qapp.processEvents()
    assert {lesson["id"] for lesson in page.visible_lessons()} >= {"auto-calcimeter", "bernard", "pure-water"}
    page.open_lesson("bernard")
    qapp.processEvents()
    assert page.stack.currentIndex() == 1
    assert page.player is not None
    assert "teorik" in page.detail_plain_text().casefold()
    player = page.player
    player.play()
    assert player.playing is True
    player.pause()
    assert player.playing is False
    player.show_next()
    assert player.index == 1
    player.show_previous()
    assert player.index == 0
    player.restart()
    assert player.index == 0
    assert player.playing is True
    player.pause()
    player.click_fraction(0.10, 0.60)
    assert player.selected_part == "sample"
    assert "katı" in player.part_label.text().casefold()

    page.show_list()
    page.set_category("all")
    page.open_lesson("safety-ppe")
    qapp.processEvents()
    acid = page.player
    assert acid.animation_id == "acid"
    acid.show_next()
    assert acid.current()["visual"] == "acid_order"
    acid.click_fraction(0.25, 0.50)
    assert acid.selected_part == "water"

    page.open_lesson("uv")
    assert page.player is None
    assert "kesin kanıtı" in page.detail_plain_text()

    window.studio_page.show_scene(2)
    window.studio_page.show_previous()
    assert window.studio_page.scene_index == 1
    window.studio_page.show_next()
    assert window.studio_page.scene_index == 2

    window.set_language("en")
    assert window.nav_buttons["mudacademy"].text().endswith("Mudlogging Academy")
    page.open_lesson("bernard")
    assert "theoretical" in page.detail_plain_text().casefold()
    window.close()
    QApplication.instance().processEvents()
