import os

import pytest

from app.library_data import STARTERS, filter_records, all_records


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starter_cards_do_not_assign_safety_data():
    assert [item["id"] for item in STARTERS] == [
        "hcl",
        "caco3",
        "acetone",
        "nacl",
        "naoh",
        "kcl",
        "ipa",
    ]
    for item in STARTERS:
        assert "ghs" not in item
        assert "hazard" not in item
        assert "ppe" not in item
        assert "sds" not in item
    acetone = filter_records(list(STARTERS), "aseton", "all")
    assert [item["id"] for item in acetone] == ["acetone"]
    salts = filter_records(list(STARTERS), "", "salt")
    assert {item["id"] for item in salts} == {"nacl", "kcl"}
    assert filter_records(list(STARTERS), "yokboyle", "all") == []
    added = all_records(
        [{"id": 4, "name": "Barit", "formula": "BaSO4", "category": "mineral", "user_note": "not"}]
    )
    assert added[-1]["id"] == "user:4"
    assert filter_records(added, "barit", "mineral")[-1]["formula"] == "BaSO4"


def test_inventory_stock_and_label_notes_survive_reopen(qapp, tmp_path):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QMessageBox

    from app.database import list_product_labels
    from app.main_window import LabGuard

    path = tmp_path / "lab.db"
    window = LabGuard(db_path=path)
    window.c_name.setText("Kap")
    window.c_qty.setText("5")
    window.c_loc.setText("Raf")
    window.c_exp.setText("")

    def accept():
        for widget in qapp.topLevelWidgets():
            if isinstance(widget, QMessageBox):
                widget.accept()

    QTimer.singleShot(50, accept)
    window.save_chemical()
    qapp.processEvents()
    accept()
    window.chem_table.selectRow(0)
    window.editing_id = 1
    window.move_qty.setText("2")
    window.move_direction.setCurrentIndex(window.move_direction.findData("stock_out"))
    window.save_stock_movement()
    window.wizard.set_label_saver(window._save_label_note)
    window._save_label_note("HCl", "%30-33", "1,18 g/mL", "etiket")
    window.close()

    again = LabGuard(db_path=path)
    again.navigate("inventory")
    qapp.processEvents()
    assert again.chem_table.rowCount() == 1
    assert again.chem_table.item(0, 1).text() in {"3", "3.0", "3,0"}
    assert again.move_table.rowCount() == 1
    labels = list_product_labels(again.con)
    assert labels[0]["verification"] == "unverified"
    assert labels[0]["label_density"] == "1,18 g/mL"
    assert "30" in labels[0]["label_concentration"]
    again.close()


def test_library_and_ppe_pages_open(qapp, tmp_path):
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton

    from app.illustrations import Sketch
    from app.main_window import LabGuard

    window = LabGuard(db_path=tmp_path / "lab.db")
    window.resize(1200, 800)
    window.show()
    qapp.processEvents()

    assert window.nav_buttons["library"].text().endswith("Kimyasal Tanıma Kütüphanesi")
    assert window.nav_buttons["ppe"].text().endswith("Görsel KKD Rehberi")
    window.home_page.library_card.button.click()
    qapp.processEvents()
    assert window._current_page == "library"
    assert window.pages.currentWidget() is window.library_page
    assert window.library_page.grid.count() == 7

    window.library_page.search.setText("HCl")
    qapp.processEvents()
    assert window.library_page.grid.count() == 1
    window.library_page.search.clear()
    window.library_page.set_category("solvent")
    assert window.library_page.grid.count() == 2
    window.library_page.set_category("all")

    window.library_page.add_name.setText("Barit")
    window.library_page.add_formula.setText("BaSO4")
    window.library_page.add_note.setText("kullanıcı notu")
    window.library_page.add_category.setCurrentIndex(
        window.library_page.add_category.findData("mineral")
    )
    window.library_page.save_button.click()
    qapp.processEvents()
    assert window.library_page.grid.count() == 8
    window.library_page.search.setText("Barit")
    card = window.library_page.grid.itemAt(0).widget()
    card.findChild(QPushButton).click()
    qapp.processEvents()
    assert window.library_page.stack.currentIndex() == 1
    detail = "\n".join(label.text() for label in window.library_page.detail_host.findChildren(QLabel))
    assert "BaSO4" in detail
    assert "Doğrulanması gerekiyor" in detail
    assert "kullanıcı notu" in detail
    assert "GHS05" not in detail
    assert "GHS06" not in detail
    window.library_page.show_sds_status()
    assert "SDS" in window.library_page.sds_status.text()
    assert "yok" in window.library_page.sds_status.text()
    sketches = window.library_page.detail_host.findChildren(Sketch)
    assert sketches
    assert sketches[0].width() > 40 and sketches[0].height() > 40

    window.home_page.ppe_card.button.click()
    qapp.processEvents()
    assert window._current_page == "ppe"
    assert window.pages.currentWidget() is window.ppe_page
    ppe_text = "\n".join(label.text() for label in window.ppe_page.findChildren(QLabel))
    assert "yerine geçmez" in ppe_text
    assert "otomatik olarak önerilmez" in ppe_text
    assert "uygunluğu kontrol edilmelidir" in ppe_text
    from app.media_view import MediaView

    pictures = window.ppe_page.findChildren(MediaView)
    assert len(pictures) == 9
    assert sum(1 for picture in pictures if picture.loaded == "photo") >= 6
    assert any(picture.loaded == "illustration" for picture in pictures)

    window.set_language("en")
    assert window.nav_buttons["library"].text().endswith("Chemical recognition library")
    assert "Verification required" in "\n".join(
        label.text() for label in window.library_page.findChildren(QLabel)
    )
    assert "does not replace" in "\n".join(label.text() for label in window.ppe_page.findChildren(QLabel))
    window.set_language("tr")

    window.navigate("home")
    window.grab().save("/tmp/labguard-home-hub.png")
    window.navigate("library")
    window.library_page.show_list()
    window.library_page.search.clear()
    window.library_page.set_category("all")
    qapp.processEvents()
    window.grab().save("/tmp/labguard-library.png")
    window.navigate("ppe")
    window.grab().save("/tmp/labguard-ppe.png")
    QApplication.instance().processEvents()
    window.close()
