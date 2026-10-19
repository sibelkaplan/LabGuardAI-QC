"""Home and sidebar stay mapped to the existing pages."""

import os

import pytest

from app.constants import PAGE_KEYS
from app.i18n import t


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_home_shows_three_actions_and_grouped_navigation(qapp, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication

    from app.main_window import LabGuard

    monkeypatch.setenv("LABGUARD_THEME_FILE", str(tmp_path / "theme.ini"))
    window = LabGuard(db_path=tmp_path / "lab.db")
    window.resize(1200, 780)
    window.show()
    QApplication.processEvents()

    home = window.home_page
    assert window.pages.currentWidget() is home
    assert home.today.text() == "LabGuard AI'ye Hoş Geldiniz"
    assert home.subtitle.text() == "Görsel eğitim ve laboratuvar araçları."
    assert home.quick_label.text() == "Hızlı erişim"
    assert "DEMO" in home.demo_title.text()
    assert home.scroll.horizontalScrollBar().maximum() == 0
    assert window.lang_btn.text() == "English"
    assert window.brand_sub.text() == "Laboratory Safety Intelligence"
    assert window.theme == "laboratory"
    assert window.theme_btn.text() == "Laboratuvar açık"
    for card in (
        home.tutor_card,
        home.studio_card,
        home.calc_card,
        home.tests_card,
        home.rocks_card,
        home.mud_card,
        home.ppe_card,
        home.prepare_card,
        home.inventory_card,
    ):
        assert card.isVisible()
        assert card.button.isVisible()
        assert card.photo.pixmap() is not None
        assert card.photo.pixmap().isNull() is False
    assert home.samples_card.isHidden()
    assert home.library_card.isHidden()
    assert home.banner.pixmap() is not None
    assert home.banner.pixmap().isNull() is False
    assert home.hero_image_key == "hero_lab"
    assert home.banner.image_key == "limestone"
    assert home.hero_image_key != "derrick"
    assert home.banner.image_key != "derrick"
    assert "SDS" in home.safety_note.text() or "SDS" in home.safety_note.text().upper()

    for key in PAGE_KEYS:
        assert window.nav_buttons[key].text().endswith(t(key, "tr"))
    headers = [header.text() for header, _key, _box in window._nav_groups]
    assert headers == ["▾  Öğren", "▾  Laboratuvar", "▾  Kayıtlar ve güvenlik"]

    learn, _key, learn_box = window._nav_groups[0]
    learn.click()
    QApplication.processEvents()
    assert learn_box.isHidden()
    assert window.nav_buttons["studio"].isVisible() is False
    learn.click()
    QApplication.processEvents()
    assert window.nav_buttons["studio"].isVisible()

    home.tutor_card.button.click()
    QApplication.processEvents()
    assert window.pages.currentWidget() is home
    assert window.tutor_dock.panel.isVisible()
    assert "Bağlı bir yapay zekâ" in window.tutor_dock.note.text()
    window.tutor_dock.close_panel()

    window.nav_buttons["home"].click()
    home.calc_card.button.click()
    assert window.pages.currentWidget() is not home
    assert window._current_page == "calc"

    window.nav_buttons["home"].click()
    home.prepare_card.button.click()
    assert window._current_page == "prepare"
    window.nav_buttons["home"].click()
    home.inventory_card.button.click()
    assert window._current_page == "inventory"
    window.nav_buttons["home"].click()
    home.samples_card.button.click()
    assert window.mud_page._category == "samples"
    window.nav_buttons["home"].click()
    home.tests_card.button.click()
    assert window.mud_page._category == "tests"
    window.nav_buttons["home"].click()
    home.rocks_card.button.click()
    assert window.mud_page._category == "rocks"
    window.nav_buttons["home"].click()
    home.mud_card.button.click()
    assert window.mud_page._category == "devices"

    window.lang_btn.click()
    assert home.today.text() == "Welcome to LabGuard AI"
    assert home.subtitle.text() == "Visual training and laboratory tools."
    assert window.nav_buttons["prepare"].text().endswith("Acid preparation")
    assert window.brand_sub.text() == "Laboratory Safety Intelligence"
    assert [header.text() for header, _key, _box in window._nav_groups][0] == "▾  Learn"
    window.close()


def test_theme_switch_changes_the_surface(qapp, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication

    from app.main_window import LabGuard

    monkeypatch.setenv("LABGUARD_THEME_FILE", str(tmp_path / "theme.ini"))
    window = LabGuard(db_path=tmp_path / "lab.db")
    window.resize(1200, 780)
    window.show()
    QApplication.processEvents()

    def canvas():
        view = window.home_page.scroll.viewport()
        return view.grab().toImage().pixelColor(1, 1).name()

    def card():
        return window.home_page.tutor_card.grab().toImage().pixelColor(8, 8).name()

    laboratory_canvas = canvas()
    laboratory_card = card()
    window.theme_btn.click()
    QApplication.processEvents()
    assert window.theme == "white"
    white_canvas = canvas()
    white_card = card()
    window.theme_btn.click()
    QApplication.processEvents()
    assert window.theme == "midnight"
    midnight_canvas = canvas()
    midnight_card = card()
    assert laboratory_canvas == "#ffffff"
    assert white_canvas == "#ffffff"
    assert midnight_canvas == "#000000"
    assert laboratory_card == "#ffffff"
    assert white_card == "#f2f6f6"
    assert midnight_card == "#080d12"
    assert "#000000" in window.styleSheet()
    assert "Bağlı bir yapay zekâ" in window.tutor_dock.note.text()
    window.set_theme("laboratory")
    QApplication.processEvents()
    assert window.theme == "laboratory"
    assert canvas() == laboratory_canvas
    window.close()
