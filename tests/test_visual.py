"""Photographs, the training storyboard, and the acid calculator."""

import os

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

from app.main_window import LabGuard
from app.media_catalog import asset_for, training_video
from app.media_view import MediaView
from app.training_center import SCENES, scene_pours_water_on_acid


def test_verified_photos_are_local_and_uncertain_pictures_stay_illustrations():
    hcl = asset_for("hcl")
    assert hcl["kind"] == "photo"
    assert hcl["available"]
    assert hcl["path"].is_file()
    assert "PD-link" in hcl["license"]
    acetone = asset_for("acetone")
    assert acetone["kind"] == "illustration"
    assert acetone["available"] is False
    goggles = asset_for("goggles")
    assert goggles["kind"] == "illustration"
    spill = asset_for("spill")
    assert spill["kind"] == "illustration"
    assert training_video() is None
    for visual in (scene["visual"] for scene in SCENES):
        assert scene_pours_water_on_acid(visual) is False
    assert SCENES[4]["visual"] == "acid_into_water"


def test_training_center_and_calculator(qapp, tmp_path):
    window = LabGuard(tmp_path / "labguard.db")
    window.show()
    qapp.processEvents()
    assert window.home_page.studio_card.button.text()
    window.home_page.studio_card.button.click()
    qapp.processEvents()
    center = window.studio_page
    assert window._current_page == "studio"
    assert center.using_video is False
    assert center.stage.isVisible()
    center.play()
    assert center.playing is True
    center.pause()
    assert center.playing is False
    center.restart()
    assert center.scene_index == 0
    assert center.playing is True
    center.pause()
    center.show_scene(4)
    qapp.processEvents()
    text = center.narration.text() + center.subtitle.text()
    assert not any(character.isdigit() for character in text)
    assert "su" in text.casefold()
    center.subtitles.setChecked(False)
    assert center.subtitle.isHidden()
    center.show_quiz()
    center.choice_buttons[0][1].setChecked(True)
    center.choice_buttons[1][1].setChecked(True)
    center.choice_buttons[2][1].setChecked(True)
    center.grade()
    assert center.summary_box.isHidden() is False
    assert "sertifika" in center.summary_note.text().casefold()

    window.navigate("library")
    window.library_page.search.setText("HCl")
    qapp.processEvents()
    card = window.library_page.grid.itemAt(0).widget()
    picture = card.findChild(MediaView)
    assert picture.loaded == "photo"
    assert picture.image.pixmap() is not None and not picture.image.pixmap().isNull()
    dialog = picture.enlarge()
    qapp.processEvents()
    assert dialog.isVisible()
    dialog.close()

    window.navigate("prepare")
    wizard = window.wizard
    wizard.calc_button.click()
    assert "Başlangıç konsantrasyonu" in wizard.calc_result.text()
    wizard.calc_c1.setText("32")
    wizard.calc_c2.setText("18,5")
    wizard.calc_volume.setText("1000")
    wizard.calc_basis_buttons["percent_w_w"].setChecked(True)
    wizard.calc_button.click()
    assert "578" not in wizard.calc_result.text()
    wizard.calc_basis_buttons["percent_v_v"].setChecked(True)
    wizard.calc_button.click()
    assert "578.1" in wizard.calc_result.text()
    assert "onayı değildir" in wizard.calc_result.text()
    window.set_language("en")
    assert window.nav_buttons["studio"].text().endswith("Visual training center")
    assert "578.1" in wizard.calc_result.text()
    assert "not a preparation approval" in wizard.calc_result.text()
    window.close()
    QApplication.instance().processEvents()
