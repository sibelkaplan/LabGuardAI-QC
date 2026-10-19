"""Moving schematic scenes keep the training controls and the current sentence."""

import os

import pytest


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_acid_scene_moves_and_speech_follows_the_step(qapp, tmp_path):
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtCore import QRectF

    from app.main_window import LabGuard
    from app.motion import paint_scene

    window = LabGuard(tmp_path / "labguard.db")
    window.show()
    qapp.processEvents()
    window.home_page.studio_card.button.click()
    center = window.studio_page
    assert center.using_video is False
    assert center.details_host.isHidden()
    center.show_scene(4)
    qapp.processEvents()
    assert center.scene_index == 4
    before = center.subtitle.text()
    assert "su" in (center.narration.text() + before).casefold()
    assert not any(character.isdigit() for character in center.narration.text() + before)
    center.elapsed = 6000
    center.stage.update()
    qapp.processEvents()
    shot = center.stage.grab()
    assert not shot.isNull()
    assert shot.width() > 100
    center.pick(0.40, 0.55)
    assert "Su" in center.pick_label.text() or "su" in center.pick_label.text().casefold()
    center.speak_step()
    qapp.processEvents()
    assert center.speech_status.text()
    assert center._spoken == before
    center.show_next()
    qapp.processEvents()
    assert center.subtitle.text() != before
    assert center._pick_key == ""
    center.play()
    assert center.playing is True
    center.pause()
    assert center.playing is False
    center.restart()
    assert center.scene_index == 0
    center.pause()
    center.pick(0.2, 0.4)
    assert "Etiket" in center.pick_label.text()
    center.show_scene(3)
    center.pick(0.10, 0.45)
    assert "gözlü" in center.pick_label.text().casefold()

    page = window.mud_page
    page.open_lesson("sample-wash")
    wash = page.player
    wash.elapsed = 2000
    wash._refresh()
    assert wash.playing is False or wash.elapsed == 2000
    first = wash.step_speech()
    wash.show_next()
    assert wash.step_speech() == first
    page.open_lesson("fluor-direct")
    fluor = page.player
    spoken = fluor.step_speech()
    fluor.show_next()
    assert fluor.step_speech() != spoken
    fluor.speak_step()
    assert fluor.speech_status.text()
    page.open_lesson("bernard")
    bernard = page.player
    bernard.play()
    bernard.elapsed = 1000
    bernard._refresh()
    bernard.pause()
    assert bernard.playing is False
    bernard.restart()
    assert bernard.index == 0
    assert bernard.playing is True
    bernard.pause()
    frame = QRectF(0, 0, 400, 240)
    scratch = QImage(400, 240, QImage.Format.Format_ARGB32)
    painter = QPainter(scratch)
    paint_scene(painter, frame, "acid_into_water", 0.6, "tr")
    paint_scene(painter, frame, "wash_stack", 0.4, "tr")
    paint_scene(painter, frame, "bernard_gas", 0.5, "tr")
    painter.end()
    window.close()
