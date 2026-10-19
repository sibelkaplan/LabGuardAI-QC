"""Main window. Visible copy comes from app.i18n and is refreshed on language change."""

from __future__ import annotations

import json
import os
from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor, QGuiApplication, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.constants import (
    CHECK_KEYS,
    INCIDENT_KINDS,
    INCIDENT_STATUSES,
    PAGE_KEYS,
    SEVERITIES,
    UNITS,
)
from app.database import (
    add_chemical,
    add_product_label,
    record_stock_movement,
    list_stock_movements,
    add_incident,
    add_inspection,
    connect,
    counts,
    delete_chemical,
    export_backup,
    get_chemical,
    import_backup,
    list_calculations,
    list_favorite_lessons,
    list_recent_lessons,
    list_chemicals,
    list_incidents,
    list_inspection_rows,
    save_calculation,
    resolve_db_path,
    update_chemical,
)
from app.academy_page import AcademyPage
from app.hub import HomePage
from app.card_images import FitImage, caption
from app.i18n import t
from app.media_view import MediaView
from app.library_page import LibraryPage
from app.ppe_page import PpePage
from app.prepare_ui import PrepareWizard
from app.training_center import TrainingCenter
from app.tutor_dock import TutorDock
from app.logo import LogoMark
from app.screens import CalcPage, DetailPage, QuizPanel
from app.styles import SURFACE, stylesheet
from app.validation import STATUS_I18N, BackupError, ValidationError, format_quantity

NAV_ICONS = {
    "home": "⌂",
    "prepare": "⚗",
    "library": "▣",
    "ppe": "◇",
    "studio": "▶",
    "mudacademy": "☰",
    "inventory": "▤",
    "calc": "Σ",
    "inspections": "☑",
    "academy": "♦",
    "incidents": "⚑",
}

STATUS_COLORS = {
    "expired": "#8C2F2F",
    "expiring": "#8A5A00",
    "review": "#3E595D",
    "ok": "#0B5964",
}


class LabGuard(QMainWindow):
    def __init__(self, db_path: Path | None = None):
        super().__init__()
        self.lang = "tr"
        self.db_path = resolve_db_path(db_path)
        self.con = connect(self.db_path)
        self.editing_id: int | None = None
        self._current_page = "home"
        self._history: list[dict] = []
        self._history_ready = False
        self._restoring = False
        self._loading_table = False
        self._bound: list[tuple] = []
        self._combos: list[tuple[QComboBox, tuple[str, ...]]] = []
        self._headers: list[tuple[QTableWidget, tuple[str, ...]]] = []
        self.checkboxes: list[tuple[str, QCheckBox]] = []
        self._pictures: list[tuple[FitImage, QLabel, str]] = []

        self.setWindowTitle("LabGuard AI")
        self.resize(1200, 780)
        self.setMinimumSize(960, 640)
        app = QApplication.instance()
        if app is not None:
            app.setStyle("Fusion")
        self.theme = self._stored_theme()
        self._build()
        self.set_theme(self.theme)
        self.retranslate()
        self.navigate("home")

    def bind_text(self, widget, key: str, prefix: str = ""):
        self._bound.append((widget, "text", key, prefix))
        widget.setText(prefix + t(key, self.lang))
        return widget

    def bind_placeholder(self, widget, key: str):
        self._bound.append((widget, "placeholder", key, ""))
        widget.setPlaceholderText(t(key, self.lang))
        return widget

    def bind_combo(self, combo: QComboBox, keys: tuple[str, ...]) -> QComboBox:
        self._combos.append((combo, keys))
        self._refill_combo(combo, keys)
        return combo

    def _refill_combo(self, combo: QComboBox, keys: tuple[str, ...]) -> None:
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for key in keys:
            combo.addItem(t(key, self.lang), key)
        index = combo.findData(current) if current is not None else 0
        combo.setCurrentIndex(index if index >= 0 else 0)
        combo.blockSignals(False)

    def _title(self, key: str, size: int = 22) -> QLabel:
        label = QLabel()
        label.setObjectName("PageTitle")
        label.setWordWrap(True)
        return self.bind_text(label, key)

    def _card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        return frame

    def _muted(self, key: str, prefix: str = "") -> QLabel:
        label = QLabel()
        label.setObjectName("Muted")
        label.setWordWrap(True)
        return self.bind_text(label, key, prefix)

    def _picture(self, key: str, height: int = 140) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        image = FitImage(key, height)
        note = QLabel()
        note.setObjectName("Muted")
        note.setWordWrap(True)
        layout.addWidget(image)
        layout.addWidget(note)
        self._pictures.append((image, note, key))
        return box

    def _warning(self, key: str) -> QLabel:
        label = QLabel()
        label.setObjectName("Warning")
        label.setWordWrap(True)
        return self.bind_text(label, key)

    def _form_row(self, form: QFormLayout, key: str, field: QWidget) -> QLabel:
        label = QLabel()
        label.setObjectName("Muted")
        self.bind_text(label, key)
        form.addRow(label, field)
        return label

    def _table(self, keys: tuple[str, ...]) -> QTableWidget:
        table = QTableWidget(0, len(keys))
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMinimumHeight(180)
        table.setWordWrap(True)
        self._headers.append((table, keys))
        table.setHorizontalHeaderLabels([t(key, self.lang) for key in keys])
        return table

    def _scroll(self, page: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(page)
        return scroll

    def _page(self) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 2, 12, 12)
        layout.setSpacing(14)
        return page, layout

    def _nav_group(self, layout, title_key: str):
        header = QPushButton()
        header.setObjectName("GroupHeader")
        header.setCheckable(True)
        header.setChecked(True)
        box = QWidget()
        box.setObjectName("SidebarHost")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(6, 0, 0, 4)
        box_layout.setSpacing(2)
        header.toggled.connect(lambda open_, panel=box: panel.setVisible(open_))
        header.toggled.connect(lambda _open: self._sync_groups())
        layout.addWidget(header)
        layout.addWidget(box)
        self._nav_groups.append((header, title_key, box))
        return box_layout

    def _sync_groups(self) -> None:
        for header, key, _box in self._nav_groups:
            mark = "▾" if header.isChecked() else "▸"
            header.setText(f"{mark}  {t(key, self.lang)}")

    def _add_nav(self, layout, key: str) -> None:
        button = QPushButton()
        button.setObjectName("Nav")
        button.clicked.connect(lambda checked=False, page=key: self.navigate(page))
        self.nav_buttons[key] = button
        layout.addWidget(button)

    def _add_action(self, layout, key: str, callback, icon: str = "") -> None:
        button = QPushButton()
        button.setObjectName("Nav")
        button.clicked.connect(lambda checked=False: callback())
        self.bind_text(button, key, f"{icon}   " if icon else "")
        layout.addWidget(button)

    def _build(self) -> None:
        self.pages = QStackedWidget()
        self._page_index = {}
        outer = QWidget()
        outer_layout = QHBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        side = QFrame()
        side.setObjectName("Sidebar")
        side.setFixedWidth(268)
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(12, 16, 12, 12)
        side_layout.setSpacing(6)
        brand_row = QHBoxLayout()
        brand_row.setSpacing(8)
        brand_row.addWidget(LogoMark(), 0, Qt.AlignmentFlag.AlignTop)
        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        brand = QLabel("LabGuard AI")
        brand.setObjectName("Brand")
        self.brand_sub = QLabel()
        self.brand_sub.setObjectName("BrandTag")
        self.brand_sub.setWordWrap(True)
        self.bind_text(self.brand_sub, "brand_sub")
        brand_col.addWidget(brand)
        brand_col.addWidget(self.brand_sub)
        brand_row.addLayout(brand_col, 1)
        side_layout.addLayout(brand_row)

        nav_scroll = QScrollArea()
        nav_scroll.setObjectName("SidebarScroll")
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav_host = QWidget()
        nav_host.setObjectName("SidebarHost")
        nav_layout = QVBoxLayout(nav_host)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)
        self.nav_buttons: dict[str, QPushButton] = {}
        self._nav_groups: list[tuple[QPushButton, QWidget]] = []
        self._add_nav(nav_layout, "home")
        learn = self._nav_group(nav_layout, "nav_group_learn")
        self._add_action(learn, "nav_tutor", self._open_tutor)
        self._add_nav(learn, "studio")
        self._add_nav(learn, "mudacademy")
        self._add_action(learn, "mud_cat_tests", lambda: self._open_academy_category("tests"))
        self._add_action(learn, "mud_cat_rocks", lambda: self._open_academy_category("rocks"))
        lab = self._nav_group(nav_layout, "nav_group_lab")
        self._add_nav(lab, "prepare")
        self._add_nav(lab, "library")
        self._add_action(lab, "mud_cat_devices", lambda: self._open_academy_category("devices"))
        self._add_nav(lab, "ppe")
        self._add_nav(lab, "calc")
        records = self._nav_group(nav_layout, "nav_group_records")
        for key in ("inventory", "inspections", "academy", "incidents"):
            self._add_nav(records, key)
        nav_layout.addStretch()
        nav_scroll.setWidget(nav_host)
        side_layout.addWidget(nav_scroll, 1)
        self.lang_btn = QPushButton()
        self.lang_btn.setObjectName("SideChoice")
        self.lang_btn.clicked.connect(self.toggle_language)
        side_layout.addWidget(self.lang_btn)
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("SideChoice")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.hide()
        side_layout.addWidget(self.theme_btn)
        theme_row = QHBoxLayout()
        theme_row.setSpacing(6)
        self.theme_segments = {}
        for key in ("laboratory", "midnight", "system"):
            button = QPushButton()
            button.setObjectName("SideChoice")
            button.clicked.connect(lambda checked=False, chosen=key: self._choose_theme(chosen))
            self.theme_segments[key] = button
            theme_row.addWidget(button)
        side_layout.addLayout(theme_row)
        self.side_status = QLabel()
        self.side_status.setObjectName("Sub")
        self.side_status.setWordWrap(True)
        self.bind_text(self.side_status, "demo_short", prefix="●  ")
        side_layout.addWidget(self.side_status)

        right = QFrame()
        right.setObjectName("Canvas")
        right.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 14, 20, 16)
        right_layout.setSpacing(8)
        heading = QHBoxLayout()
        self.back_button = QPushButton()
        self.back_button.setObjectName("Back")
        self.back_button.clicked.connect(self.go_back)
        self.bind_text(self.back_button, "nav_back")
        self.breadcrumb = QLabel()
        self.breadcrumb.setObjectName("Sub")
        heading.addWidget(self.back_button)
        heading.addWidget(self.breadcrumb)
        heading.addStretch()
        self.top_search = QLineEdit()
        self.top_search.setObjectName("HomeSearch")
        self.top_search.setClearButtonEnabled(True)
        self.top_search.setMinimumWidth(160)
        self.top_search.setMaximumWidth(280)
        self.bind_placeholder(self.top_search, "home_search_prompt")
        self.top_search.textChanged.connect(self._from_top_search)
        heading.addWidget(self.top_search)
        self.banner = QLabel()
        self.banner.setObjectName("Banner")
        self.banner.setWordWrap(True)
        self.bind_text(self.banner, "demo_banner")
        right_layout.addLayout(heading)
        right_layout.addWidget(self.banner)
        right_layout.addWidget(self.pages, 1)
        self._content = right

        outer_layout.addWidget(side)
        outer_layout.addWidget(right, 1)
        self.setCentralWidget(outer)
        self._build_home()
        self._build_prepare()
        self._build_library()
        self._build_ppe()
        self._build_studio()
        self._build_mudacademy()
        self._build_inventory()
        self._build_calc()
        self._build_detail()
        self._build_inspections()
        self._build_academy()
        self._build_incidents()
        self.library_page._before_move = self._remember
        self.library_page._external_back = self.go_back
        self.mud_page._before_move = self._remember
        self.mud_page._external_back = self.go_back
        self.tutor_dock = TutorDock(self._open_linked_lesson, self._place_tutor)
        self.tutor_dock.setParent(self._content)

    def _build_home(self) -> None:
        self.home_page = HomePage(
            lambda: self.navigate("prepare"),
            lambda: self.navigate("library"),
            lambda: self.navigate("ppe"),
            lambda: self.navigate("studio"),
            self._open_academy_category,
            lambda: self.navigate("calc"),
            self._open_tutor,
            self._open_learn_target,
            lambda: self.navigate("inventory"),
            lambda: self.navigate("academy"),
        )
        self._add_page("home", self.home_page)
        self.home_page.search.textChanged.connect(self._mirror_top_search)

    def _from_top_search(self, text: str) -> None:
        if not hasattr(self, "home_page"):
            return
        if self.home_page.search.text() != text:
            self.home_page.search.setText(text)
        if text.strip() and getattr(self, "_current_page", "home") != "home":
            self.navigate("home")

    def _mirror_top_search(self, text: str) -> None:
        if hasattr(self, "top_search") and self.top_search.text() != text:
            self.top_search.setText(text)

    def _build_library(self) -> None:
        self.library_page = LibraryPage(lambda: self.con)
        self._add_page("library", self.library_page)

    def _build_ppe(self) -> None:
        self.ppe_page = PpePage()
        self._add_page("ppe", self.ppe_page)

    def _build_studio(self) -> None:
        self.studio_page = TrainingCenter()
        self._add_page("studio", self.studio_page)

    def _build_mudacademy(self) -> None:
        self.mud_page = AcademyPage()
        self.mud_page.attach(self.con, self._refresh_home_marks)
        self._add_page("mudacademy", self.mud_page)

    def _build_prepare(self) -> None:
        self.wizard = PrepareWizard()
        self.assistant_note = self.wizard.assistant_note
        self.wizard.set_label_saver(self._save_label_note)
        self._add_page("prepare", self.wizard)

    def _add_page(self, key: str, widget) -> None:
        self._page_index[key] = self.pages.addWidget(widget)

    def _build_inventory(self) -> None:
        page, layout = self._page()
        layout.addWidget(self._title("inventory"))
        layout.addWidget(self._picture("inventory_scene"))
        backup_row = QHBoxLayout()
        export_button = QPushButton()
        export_button.clicked.connect(self.export_backup_file)
        self.bind_text(export_button, "export")
        import_button = QPushButton()
        import_button.clicked.connect(self.import_backup_file)
        self.bind_text(import_button, "import_backup")
        backup_row.addWidget(export_button)
        backup_row.addWidget(import_button)
        backup_row.addStretch()
        layout.addLayout(backup_row)
        form_card = self._card()
        form = QFormLayout(form_card)
        form.setContentsMargins(16, 16, 16, 16)
        form.setSpacing(8)
        self.c_name = QLineEdit()
        self.c_qty = QLineEdit()
        self.bind_placeholder(self.c_qty, "qty_hint")
        self.c_unit = QComboBox()
        self.c_unit.addItems(list(UNITS))
        self.c_loc = QLineEdit()
        self.c_exp = QLineEdit()
        self.bind_placeholder(self.c_exp, "expiry_hint")
        self.c_sds = QLineEdit()
        self.c_rev = QLineEdit()
        self.c_qr = QLineEdit()
        self.c_name_label = self._form_row(form, "name", self.c_name)
        self._form_row(form, "quantity", self.c_qty)
        self._form_row(form, "unit", self.c_unit)
        self._form_row(form, "location", self.c_loc)
        self._form_row(form, "expiry", self.c_exp)
        self._form_row(form, "sds_document", self.c_sds)
        self._form_row(form, "sds_revision", self.c_rev)
        self._form_row(form, "qr_id", self.c_qr)
        self.qr_hint = self._muted("qr_hint")
        self.sds_hint = self._muted("sds_hint")
        self.expiry_note = self._muted("expiry_note")
        form.addRow(self.sds_hint)
        form.addRow(self.qr_hint)
        form.addRow(self.expiry_note)
        button_row = QHBoxLayout()
        self.save_chemical_btn = QPushButton()
        self.save_chemical_btn.setObjectName("Primary")
        self.save_chemical_btn.clicked.connect(self.save_chemical)
        self.clear_chemical_btn = QPushButton()
        self.clear_chemical_btn.clicked.connect(self.clear_chemical_form)
        self.bind_text(self.clear_chemical_btn, "clear")
        self.delete_chemical_btn = QPushButton()
        self.delete_chemical_btn.clicked.connect(self.delete_chemical)
        self.bind_text(self.delete_chemical_btn, "delete")
        button_row.addWidget(self.save_chemical_btn)
        button_row.addWidget(self.clear_chemical_btn)
        button_row.addWidget(self.delete_chemical_btn)
        form.addRow(button_row)
        layout.addWidget(form_card)

        self.search = QLineEdit()
        self.bind_placeholder(self.search, "search")
        self.search.textChanged.connect(self.refresh_chemicals)
        layout.addWidget(self.search)
        self.edit_hint = self._muted("edit_hint")
        layout.addWidget(self.edit_hint)
        self.chem_table = self._table(("name", "quantity", "unit", "location", "expiry", "status", "qr_id"))
        self.chem_table.itemSelectionChanged.connect(self._on_chemical_selected)
        layout.addWidget(self.chem_table, 1)
        self.chem_empty = self._muted("empty")
        layout.addWidget(self.chem_empty)
        move = self._card()
        move_layout = QVBoxLayout(move)
        move_layout.setContentsMargins(16, 14, 16, 14)
        move_layout.addWidget(self._title("stock_move_title", 16))
        move_form = QFormLayout()
        self.move_direction = self.bind_combo(QComboBox(), ("stock_in", "stock_out"))
        self.move_qty = QLineEdit()
        self.move_note = QLineEdit()
        self._form_row(move_form, "type", self.move_direction)
        self._form_row(move_form, "quantity", self.move_qty)
        self._form_row(move_form, "description", self.move_note)
        move_layout.addLayout(move_form)
        move_button = QPushButton()
        move_button.setObjectName("Primary")
        move_button.clicked.connect(self.save_stock_movement)
        self.bind_text(move_button, "stock_move_save")
        move_layout.addWidget(move_button)
        self.move_status = QLabel()
        self.move_status.setWordWrap(True)
        move_layout.addWidget(self.move_status)
        layout.addWidget(move)
        layout.addWidget(self._title("stock_history", 16))
        self.move_table = self._table(("type", "quantity", "unit", "description", "timestamp"))
        layout.addWidget(self.move_table)
        self._sync_chemical_buttons()
        detail_button = QPushButton()
        detail_button.setObjectName("Primary")
        detail_button.clicked.connect(self.open_detail)
        self.bind_text(detail_button, "open_detail")
        layout.addWidget(detail_button)
        self._add_page("inventory", self._scroll(page))

    def _build_calc(self) -> None:
        page, layout = self._page()
        layout.addWidget(self._title("calc_title"))
        self.calc_page = CalcPage()
        self.calc_page.set_callbacks(self._persist_calc, lambda: list_calculations(self.con))
        layout.addWidget(self.calc_page, 1)
        self._add_page("calc", page)

    def _build_detail(self) -> None:
        outer, layout = self._page()
        layout.addWidget(self._title("detail"))
        self.detail_page = DetailPage()
        self.detail_page.save_button.clicked.connect(self.save_detail_record)
        layout.addWidget(self.detail_page, 1)
        self._add_page("detail", self._scroll(outer))

    def _build_inspections(self) -> None:
        page, layout = self._page()
        layout.addWidget(self._title("inspection_title"))
        layout.addWidget(self._picture("inspection_scene"))
        self.inspection_note = self._warning("inspection_note")
        layout.addWidget(self.inspection_note)
        checklist = QWidget()
        checklist_layout = QVBoxLayout(checklist)
        checklist_layout.setContentsMargins(0, 0, 0, 0)
        checklist_layout.setSpacing(8)
        form_card = self._card()
        form = QFormLayout(form_card)
        form.setContentsMargins(16, 16, 16, 16)
        self.inspector = QLineEdit()
        self._form_row(form, "inspector", self.inspector)
        checklist_layout.addWidget(form_card)
        for key in CHECK_KEYS:
            box = QCheckBox()
            self.bind_text(box, key)
            self.checkboxes.append((key, box))
            checklist_layout.addWidget(box)
        save = QPushButton()
        save.setObjectName("Primary")
        save.clicked.connect(self.save_inspection)
        self.bind_text(save, "save_check")
        checklist_layout.addWidget(save)
        layout.addWidget(checklist)
        layout.addWidget(self._title("history", 16))
        self.inspection_table = self._table(("date", "timestamp", "inspector", "item", "mark"))
        layout.addWidget(self.inspection_table, 1)
        self.inspection_empty = self._muted("empty")
        layout.addWidget(self.inspection_empty)
        self._add_page("inspections", self._scroll(page))

    def _build_academy(self) -> None:
        page, layout = self._page()
        layout.addWidget(self._title("academy"))
        layout.addWidget(self._picture("ppe_scene", 120))
        for title_key, body_key in (
            ("lesson_sds_title", "lesson_sds_body"),
            ("lesson_docs_title", "lesson_docs_body"),
            ("lesson_emergency_title", "lesson_emergency_body"),
        ):
            frame = self._card()
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(16, 14, 16, 14)
            frame_layout.addWidget(self._title(title_key, 16))
            frame_layout.addWidget(self._muted(body_key))
            layout.addWidget(frame)
        for key in ("step_1", "step_2", "step_3"):
            layout.addWidget(self._muted(key, prefix="•  "))
        self.quiz = QuizPanel()
        layout.addWidget(self.quiz)
        layout.addStretch()
        self._add_page("academy", self._scroll(page))

    def _build_incidents(self) -> None:
        page, layout = self._page()
        layout.addWidget(self._title("incident_title"))
        self.incident_media = MediaView("spill", image_height=160)
        layout.addWidget(self.incident_media)
        self.incident_note = self._warning("incident_note")
        layout.addWidget(self.incident_note)
        form_card = self._card()
        form = QFormLayout(form_card)
        form.setContentsMargins(16, 16, 16, 16)
        self.i_type = self.bind_combo(QComboBox(), INCIDENT_KINDS)
        self.i_severity = self.bind_combo(QComboBox(), SEVERITIES)
        self.i_status = self.bind_combo(QComboBox(), INCIDENT_STATUSES)
        self.i_owner = QLineEdit()
        self.i_desc = QTextEdit()
        self.i_desc.setMaximumHeight(90)
        self.bind_placeholder(self.i_desc, "desc_hint")
        self.i_action = QTextEdit()
        self.i_action.setMaximumHeight(80)
        self._form_row(form, "type", self.i_type)
        self._form_row(form, "severity", self.i_severity)
        self._form_row(form, "status", self.i_status)
        self._form_row(form, "owner", self.i_owner)
        self._form_row(form, "description", self.i_desc)
        self._form_row(form, "corrective", self.i_action)
        submit = QPushButton()
        submit.setObjectName("Primary")
        submit.clicked.connect(self.save_incident)
        self.bind_text(submit, "submit")
        form.addRow(submit)
        layout.addWidget(form_card)
        layout.addWidget(self._title("history", 16))
        self.incident_table = self._table(
            ("type", "severity", "description", "timestamp", "status", "owner", "corrective")
        )
        layout.addWidget(self.incident_table)
        self.incident_empty = self._muted("empty")
        layout.addWidget(self.incident_empty)
        self._add_page("incidents", self._scroll(page))

    def _open_academy_category(self, category: str) -> None:
        current = self._capture()
        same = (
            current["page"] == "mudacademy"
            and current["academy_index"] == 0
            and current["category"] == category
        )
        if not same:
            self._remember()
        self.navigate("mudacademy", remember=False)
        self.mud_page.set_category(category)
        self.mud_page.show_list()
        self._sync_back()

    def _open_tutor(self) -> None:
        self.tutor_dock.open_panel()
        self._place_tutor()

    def _open_linked_lesson(self, lesson_id: str) -> None:
        self._open_learn_target("lesson", lesson_id)

    def _open_learn_target(self, kind: str, value: str) -> None:
        if kind == "page":
            self.navigate(value)
            return
        if kind == "chemical":
            self.navigate("library")
            self.library_page.open_record(value)
            self._sync_back()
            return
        if kind == "lesson":
            opened_from_academy = self._current_page == "mudacademy"
            if not opened_from_academy:
                self.navigate("mudacademy")
                self.mud_page._before_move = None
            self.mud_page.open_lesson(value)
            self.mud_page._before_move = self._remember
            self._sync_back()

    def _refresh_home_marks(self) -> None:
        if not hasattr(self, "home_page") or self.con is None:
            return
        self.home_page.set_marks(list_recent_lessons(self.con), list_favorite_lessons(self.con))

    def _capture(self) -> dict:
        data = {"page": self._current_page, "editing_id": self.editing_id}
        if hasattr(self, "mud_page"):
            data["category"] = self.mud_page._category
            data["academy_index"] = self.mud_page.stack.currentIndex()
            data["lesson"] = self.mud_page._open_id
        if hasattr(self, "library_page"):
            data["library_index"] = self.library_page.stack.currentIndex()
            data["record"] = self.library_page._open_id
        return data

    def _remember(self) -> None:
        if self._restoring or not self._history_ready:
            return
        snap = self._capture()
        if self._history and self._history[-1] == snap:
            return
        self._history.append(snap)
        if len(self._history) > 30:
            self._history.pop(0)

    def _restore(self, snap: dict) -> None:
        self._restoring = True
        try:
            self.navigate(snap["page"], remember=False)
            if snap["page"] == "mudacademy":
                self.mud_page.set_category(snap.get("category", "all"))
                if snap.get("academy_index") == 1 and snap.get("lesson"):
                    self.mud_page.open_lesson(snap["lesson"])
                elif snap.get("academy_index") == 2:
                    self.mud_page.show_tutor()
                else:
                    self.mud_page.show_list()
            elif snap["page"] == "library":
                if snap.get("library_index") == 1 and snap.get("record"):
                    self.library_page.open_record(snap["record"])
                else:
                    self.library_page.show_list()
            elif snap["page"] == "detail" and snap.get("editing_id") and self.con is not None:
                record = get_chemical(self.con, snap["editing_id"])
                if record is not None:
                    self.detail_page.load(record)
        finally:
            self._restoring = False
        self._sync_back()

    def go_back(self) -> None:
        if not self._history:
            self.navigate("home", remember=False)
            return
        self._restore(self._history.pop())

    def _sync_back(self) -> None:
        if hasattr(self, "back_button"):
            self.back_button.setVisible(self._current_page != "home")

    def _place_tutor(self) -> None:
        if not hasattr(self, "tutor_dock"):
            return
        host = self._content
        dock = self.tutor_dock
        dock.adjustSize()
        if dock.panel.isVisible():
            width = min(360, max(220, host.width() - 24))
            height = min(480, max(220, host.height() - 24))
            dock.setFixedSize(width, height)
        else:
            dock.setFixedSize(48, 48)
        dock.move(max(8, host.width() - dock.width() - 12), max(8, host.height() - dock.height() - 12))
        dock.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._place_tutor()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._place_tutor()

    def navigate(self, key: str, remember: bool = True) -> None:
        if remember and key != self._current_page:
            self._remember()
        self._current_page = key
        self.pages.setCurrentIndex(self._page_index[key])
        self._history_ready = True
        self.breadcrumb.setText("LabGuard AI  /  " + t(key, self.lang))
        self._sync_back()
        for name, button in self.nav_buttons.items():
            button.setObjectName("Active" if name == key else "Nav")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
        if self.con is not None:
            self.refresh_stats()
            if key == "inventory":
                self.refresh_chemicals()
                self.refresh_stock_movements()
            elif key == "inspections":
                self.refresh_inspections()
            elif key == "incidents":
                self.refresh_incidents()
            elif key == "calc":
                self.calc_page.refresh_history()
            elif key == "library":
                self.library_page.rebuild()

    def _theme_store(self) -> QSettings:
        override = os.environ.get("LABGUARD_THEME_FILE")
        if override:
            return QSettings(override, QSettings.Format.IniFormat)
        folder = Path.home() / "Library" / "Application Support" / "LabGuardAI"
        folder.mkdir(parents=True, exist_ok=True)
        return QSettings(str(folder / "theme.ini"), QSettings.Format.IniFormat)

    def _stored_theme(self) -> str:
        value = str(self._theme_store().value("theme", "laboratory") or "laboratory")
        aliases = {"light": "laboratory", "dark": "midnight"}
        value = aliases.get(value, value)
        return value if value in SURFACE else "laboratory"

    def set_theme(self, theme: str) -> None:
        aliases = {"light": "laboratory", "dark": "midnight"}
        theme = aliases.get(theme, theme)
        if theme not in SURFACE:
            theme = "laboratory"
        self.theme = theme
        self.setStyleSheet(stylesheet(theme))
        self._paint_surfaces()
        store = self._theme_store()
        store.setValue("theme", theme)
        store.sync()
        self._sync_theme_button()

    def _choose_theme(self, choice: str) -> None:
        if choice == "system":
            scheme = QGuiApplication.styleHints().colorScheme()
            choice = "midnight" if scheme == Qt.ColorScheme.Dark else "laboratory"
        self.set_theme(choice)

    def _paint_surfaces(self) -> None:
        colors = SURFACE[self.theme if self.theme in SURFACE else "laboratory"]
        for scroll in self.findChildren(QScrollArea):
            color = colors["sidebar"] if scroll.objectName() == "SidebarScroll" else colors["canvas"]
            view = scroll.viewport()
            view.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            view.setAutoFillBackground(True)
            palette = view.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(color))
            palette.setColor(QPalette.ColorRole.Base, QColor(color))
            view.setPalette(palette)
        if hasattr(self, "_content"):
            self._content.setAutoFillBackground(True)
            palette = self._content.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(colors["canvas"]))
            self._content.setPalette(palette)
        side = self.findChild(QFrame, "Sidebar")
        if side is not None:
            side.setAutoFillBackground(True)
            palette = side.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(colors["sidebar"]))
            side.setPalette(palette)

    def toggle_theme(self) -> None:
        order = ("laboratory", "white", "midnight")
        current = self.theme if self.theme in order else "laboratory"
        self.set_theme(order[(order.index(current) + 1) % len(order)])

    def _sync_theme_button(self) -> None:
        if hasattr(self, "theme_btn"):
            self.theme_btn.setText(t(f"theme_{self.theme}", self.lang))
        if hasattr(self, "theme_segments"):
            labels = {
                "laboratory": "theme_seg_light",
                "midnight": "theme_seg_dark",
                "system": "theme_seg_system",
            }
            active = "midnight" if self.theme == "midnight" else "laboratory"
            for key, button in self.theme_segments.items():
                button.setText(t(labels[key], self.lang))
                button.setObjectName("Active" if key == active else "SideChoice")
                button.style().unpolish(button)
                button.style().polish(button)

    def set_language(self, lang: str) -> None:
        if lang not in {"tr", "en"}:
            raise ValueError(lang)
        self.lang = lang
        self.retranslate()

    def toggle_language(self) -> None:
        self.set_language("en" if self.lang == "tr" else "tr")

    def retranslate(self) -> None:
        for widget, kind, key, prefix in self._bound:
            value = prefix + t(key, self.lang)
            if kind == "text":
                widget.setText(value)
            else:
                widget.setPlaceholderText(value)
        for combo, keys in self._combos:
            self._refill_combo(combo, keys)
        for table, keys in self._headers:
            table.setHorizontalHeaderLabels([t(key, self.lang) for key in keys])
        for key, button in self.nav_buttons.items():
            button.setText(f"{NAV_ICONS[key]}   {t(key, self.lang)}")
            button.setObjectName("Active" if key == self._current_page else "Nav")
            button.style().unpolish(button)
            button.style().polish(button)
        self.lang_btn.setText("English" if self.lang == "tr" else "Türkçe")
        self._sync_theme_button()
        self._sync_groups()
        self._sync_back()
        for image, note, key in self._pictures:
            image.set_lang(self.lang)
            note.setText(caption(key, self.lang))
        if hasattr(self, "incident_media"):
            self.incident_media.retranslate(self.lang)
        if hasattr(self, "tutor_dock"):
            self.tutor_dock.retranslate(self.lang)
        self.breadcrumb.setText("LabGuard AI  /  " + t(self._current_page, self.lang))
        self._sync_chemical_buttons()
        if hasattr(self, "home_page"):
            self.home_page.retranslate(self.lang)
            self._refresh_home_marks()
        if hasattr(self, "library_page"):
            self.library_page.retranslate(self.lang)
        if hasattr(self, "ppe_page"):
            self.ppe_page.retranslate(self.lang)
        if hasattr(self, "studio_page"):
            self.studio_page.retranslate(self.lang)
        if hasattr(self, "mud_page"):
            self.mud_page.retranslate(self.lang)
        if hasattr(self, "wizard"):
            self.wizard.retranslate(self.lang)
        if hasattr(self, "quiz"):
            self.quiz.retranslate(self.lang)
        if hasattr(self, "calc_page"):
            self.calc_page.retranslate(self.lang)
        if hasattr(self, "detail_page"):
            self.detail_page.retranslate(self.lang)
        if self.con is not None and hasattr(self, "chem_table"):
            self.refresh_stats()
            self.refresh_chemicals()
            self.refresh_incidents()
            self.refresh_inspections()

    def refresh_stats(self) -> None:
        if self.con is None or not hasattr(self, "stat_values"):
            return
        data = counts(self.con)
        self.stat_values["chemicals"].setText(str(data["chemicals"]))
        self.stat_values["stat_inspections"].setText(str(data["inspections"]))
        self.stat_values["reports"].setText(str(data["incidents"]))

    def _persist_calc(self, module: str, inputs: dict, result) -> None:
        if self.con is None:
            return
        save_calculation(self.con, module, inputs, result)

    def _save_label_note(self, name: str, concentration: str, density: str, source: str) -> None:
        if self.con is None:
            return
        add_product_label(
            self.con,
            name=name or "—",
            label_concentration=concentration,
            label_density=density,
            sds_source=source,
        )

    def save_stock_movement(self) -> None:
        if self.con is None or self.editing_id is None:
            self.move_status.setText(t("no_selection", self.lang))
            return
        try:
            record_stock_movement(
                self.con,
                chemical_id=self.editing_id,
                direction="in" if self.move_direction.currentData() == "stock_in" else "out",
                quantity=self.move_qty.text(),
                note=self.move_note.text(),
            )
        except ValidationError as exc:
            self.move_status.setText(t(exc.code, self.lang))
            return
        self.move_qty.clear()
        self.move_note.clear()
        self.move_status.setText(t("stock_move_saved", self.lang))
        self.refresh_chemicals()
        self.refresh_stock_movements()

    def refresh_stock_movements(self) -> None:
        if self.con is None or not hasattr(self, "move_table"):
            return
        rows = list_stock_movements(self.con)
        names = {row["id"]: row["name"] for row in list_chemicals(self.con, "")}
        self.move_table.setRowCount(len(rows))
        for index, row in enumerate(rows):
            values = [
                t(row["direction"] if row["direction"] in {"stock_in", "stock_out"} else f"stock_{row['direction']}", self.lang),
                format_quantity(row["quantity"]),
                row["unit"],
                row["note"] or names.get(row["chemical_id"], ""),
                row["created_at"],
            ]
            for column, value in enumerate(values):
                self.move_table.setItem(index, column, QTableWidgetItem(value))

    def open_detail(self) -> None:
        chem_id = self.editing_id or self._selected_chemical_id()
        if chem_id is None or self.con is None:
            self._warn("inventory", "no_selection")
            return
        record = get_chemical(self.con, chem_id)
        if record is None:
            self._warn("inventory", "no_selection")
            return
        self.detail_page.load(record)
        self.navigate("detail")

    def save_detail_record(self) -> None:
        if self.con is None or self.detail_page.record_id is None:
            self.detail_page.status.setText(t("no_selection", self.lang))
            return
        record = get_chemical(self.con, self.detail_page.record_id)
        if record is None:
            self.detail_page.status.setText(t("no_selection", self.lang))
            return
        fields = {
            "name": record["name"],
            "quantity": record["quantity"],
            "unit": record["unit"],
            "location": record["location"],
            "expiry": record["expiry"],
            "sds_document": record["sds_document"],
            "sds_revision": record["sds_revision"],
            "qr_id": record["qr_id"],
        }
        fields.update(self.detail_page.notes())
        try:
            update_chemical(self.con, record["id"], fields)
        except ValidationError as exc:
            self.detail_page.status.setText(t(exc.code, self.lang))
            return
        saved = get_chemical(self.con, record["id"])
        if saved is not None:
            self.detail_page.load(saved)
        self.detail_page.status.setText(t("saved", self.lang))

    def _sync_chemical_buttons(self) -> None:
        if not hasattr(self, "save_chemical_btn"):
            return
        if self.editing_id is None:
            self.save_chemical_btn.setText(t("add", self.lang))
            self.delete_chemical_btn.setEnabled(False)
        else:
            self.save_chemical_btn.setText(t("update", self.lang))
            self.delete_chemical_btn.setEnabled(True)

    def _chemical_fields(self) -> dict:
        return {
            "name": self.c_name.text(),
            "quantity": self.c_qty.text(),
            "unit": self.c_unit.currentText(),
            "location": self.c_loc.text(),
            "expiry": self.c_exp.text(),
            "sds_document": self.c_sds.text(),
            "sds_revision": self.c_rev.text(),
            "qr_id": self.c_qr.text(),
        }

    def save_chemical(self) -> None:
        try:
            fields = self._chemical_fields()
            if self.editing_id is None:
                add_chemical(self.con, fields)
                self.clear_chemical_form()
            else:
                if not update_chemical(self.con, self.editing_id, fields):
                    self._warn("inventory", "no_selection")
                    return
        except ValidationError as exc:
            self._warn("inventory", exc.code)
            return
        self.refresh_chemicals()
        self.refresh_stats()
        self._info("inventory", "saved")

    def clear_chemical_form(self) -> None:
        self._loading_table = True
        self.editing_id = None
        self.chem_table.clearSelection()
        self._loading_table = False
        self.c_name.clear()
        self.c_qty.clear()
        self.c_unit.setCurrentIndex(0)
        self.c_loc.clear()
        self.c_exp.clear()
        self.c_sds.clear()
        self.c_rev.clear()
        self.c_qr.clear()
        self._sync_chemical_buttons()

    def delete_chemical(self) -> None:
        if self.editing_id is None:
            self._warn("inventory", "no_selection")
            return
        if not self._confirm("delete", "delete_confirm"):
            return
        if not delete_chemical(self.con, self.editing_id):
            self._warn("inventory", "no_selection")
            return
        self.clear_chemical_form()
        self.refresh_chemicals()
        self.refresh_stats()
        self._info("inventory", "deleted")

    def _selected_chemical_id(self) -> int | None:
        row = self.chem_table.currentRow()
        if row < 0:
            return None
        item = self.chem_table.item(row, 0)
        if item is None:
            return None
        value = item.data(Qt.UserRole)
        return int(value) if value is not None else None

    def _on_chemical_selected(self) -> None:
        if self._loading_table or self.con is None:
            return
        chem_id = self._selected_chemical_id()
        if chem_id is None:
            return
        record = get_chemical(self.con, chem_id)
        if record is None:
            return
        self.editing_id = record["id"]
        self.c_name.setText(record["name"])
        self.c_qty.setText(format_quantity(record["quantity"]))
        unit_index = self.c_unit.findText(record["unit"])
        self.c_unit.setCurrentIndex(unit_index if unit_index >= 0 else 0)
        self.c_loc.setText(record["location"])
        self.c_exp.setText(record["expiry"])
        self.c_sds.setText(record["sds_document"])
        self.c_rev.setText(record["sds_revision"])
        self.c_qr.setText(record["qr_id"])
        self._sync_chemical_buttons()

    def refresh_chemicals(self) -> None:
        if self.con is None or not hasattr(self, "chem_table"):
            return
        self._loading_table = True
        selected = self.editing_id
        rows = list_chemicals(self.con, self.search.text())
        self.chem_table.setRowCount(len(rows))
        for index, row in enumerate(rows):
            values = [
                row["name"],
                format_quantity(row["quantity"]),
                row["unit"],
                row["location"],
                row["expiry"] or "—",
                t(STATUS_I18N[row["status"]], self.lang),
                row["qr_id"] or "—",
            ]
            for column, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if column == 0:
                    cell.setData(Qt.UserRole, row["id"])
                if column == 5:
                    cell.setForeground(QColor(STATUS_COLORS.get(row["status"], "#18353A")))
                self.chem_table.setItem(index, column, cell)
            if selected is not None and row["id"] == selected:
                self.chem_table.selectRow(index)
        self.chem_empty.setVisible(not rows)
        self._loading_table = False

    def save_inspection(self) -> None:
        try:
            add_inspection(
                self.con,
                {
                    "inspector": self.inspector.text(),
                    "items": {key: box.isChecked() for key, box in self.checkboxes},
                },
            )
        except ValidationError as exc:
            self._warn("inspections", exc.code)
            return
        self.refresh_inspections()
        self.refresh_stats()
        self._info("inspections", "saved_inspection")

    def refresh_inspections(self) -> None:
        if self.con is None or not hasattr(self, "inspection_table"):
            return
        rows = list_inspection_rows(self.con)
        self.inspection_table.setRowCount(len(rows))
        for index, row in enumerate(rows):
            values = [
                row["inspected_on"],
                row["created_at"],
                row["inspector"] or "—",
                t(row["item_key"], self.lang),
                t("checked_yes" if row["checked"] else "checked_no", self.lang),
            ]
            for column, value in enumerate(values):
                self.inspection_table.setItem(index, column, QTableWidgetItem(value))
        self.inspection_table.resizeRowsToContents()
        self.inspection_empty.setVisible(not rows)

    def save_incident(self) -> None:
        try:
            add_incident(
                self.con,
                {
                    "kind": self.i_type.currentData(),
                    "severity": self.i_severity.currentData(),
                    "status": self.i_status.currentData(),
                    "owner": self.i_owner.text(),
                    "description": self.i_desc.toPlainText(),
                    "corrective_action": self.i_action.toPlainText(),
                },
            )
        except ValidationError as exc:
            self._warn("incidents", exc.code)
            return
        self.i_desc.clear()
        self.i_owner.clear()
        self.i_action.clear()
        self.refresh_incidents()
        self.refresh_stats()
        self._info("incidents", "saved_incident")

    def refresh_incidents(self) -> None:
        if self.con is None or not hasattr(self, "incident_table"):
            return
        rows = list_incidents(self.con)
        self.incident_table.setRowCount(len(rows))
        for index, row in enumerate(rows):
            values = [
                t(row["kind"], self.lang),
                t(row["severity"], self.lang),
                row["description"],
                row["created_at"],
                t(row["status"], self.lang),
                row["owner"] or "—",
                row["corrective_action"] or "—",
            ]
            for column, value in enumerate(values):
                self.incident_table.setItem(index, column, QTableWidgetItem(value))
        self.incident_table.resizeRowsToContents()
        self.incident_empty.setVisible(not rows)

    def export_backup_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            t("export", self.lang),
            "labguard-backup.json",
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            payload = export_backup(self.con)
            Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError:
            self._warn("backup_title", "file_failed")
            return
        self._info("backup_title", "export_done")

    def import_backup_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            t("import_backup", self.lang),
            "",
            "JSON (*.json)",
        )
        if not path:
            return
        if not self._confirm("backup_title", "import_confirm"):
            return
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            import_backup(self.con, payload)
        except BackupError as exc:
            self._warn("backup_title", exc.code)
            return
        except (OSError, UnicodeError, json.JSONDecodeError):
            self._warn("backup_title", "file_failed")
            return
        self.clear_chemical_form()
        self.refresh_stats()
        self.refresh_chemicals()
        self.refresh_inspections()
        self.refresh_incidents()
        self._info("backup_title", "import_done")

    def _warn(self, title_key: str, message_key: str) -> None:
        QMessageBox.warning(self, t(title_key, self.lang), t(message_key, self.lang))

    def _info(self, title_key: str, message_key: str) -> None:
        QMessageBox.information(self, t(title_key, self.lang), t(message_key, self.lang))

    def _confirm(self, title_key: str, message_key: str) -> bool:
        answer = QMessageBox.question(
            self,
            t(title_key, self.lang),
            t(message_key, self.lang),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return answer == QMessageBox.Yes

    def shutdown(self) -> None:
        if self.con is not None:
            self.con.close()
            self.con = None

    def closeEvent(self, event) -> None:
        self.shutdown()
        super().closeEvent(event)
