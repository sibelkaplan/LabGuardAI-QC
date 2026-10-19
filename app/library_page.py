"""Chemical recognition library. Safety fields stay unverified."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.constants import LIBRARY_CATEGORIES
from app.database import add_library_chemical, list_library_additions
from app.i18n import t
from app.media_view import MediaView
from app.library_data import (
    all_records,
    filter_records,
    general_field,
    record_identity,
    record_name,
)
from app.validation import ValidationError


class LibraryPage(QWidget):
    def __init__(self, connection_getter):
        super().__init__()
        self.lang = "tr"
        self._connection = connection_getter
        self._category = "all"
        self._open_id = ""
        self._before_move = None
        self._external_back = None
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._list_page())
        self.stack.addWidget(self._detail_page())
        root.addWidget(self.stack)
        self.retranslate("tr")

    def _list_page(self) -> QWidget:
        page = QWidget()
        self.list_inner = page
        page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        self.disclaimer = QLabel()
        self.disclaimer.setObjectName("Warning")
        self.disclaimer.setWordWrap(True)
        layout.addWidget(self.disclaimer)
        self.search = QLineEdit()
        self.search.textChanged.connect(self.rebuild)
        layout.addWidget(self.search)
        filters = QHBoxLayout()
        self.filter_buttons: dict[str, QPushButton] = {}
        for key in ("all",) + LIBRARY_CATEGORIES:
            button = QPushButton()
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, value=key: self.set_category(value))
            self.filter_buttons[key] = button
            filters.addWidget(button)
        filters.addStretch()
        layout.addLayout(filters)
        self.empty = QLabel()
        self.empty.setObjectName("Muted")
        self.empty.setWordWrap(True)
        layout.addWidget(self.empty)
        self.grid_host = QWidget()
        self.grid_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.grid = QGridLayout(self.grid_host)
        self.grid.setSpacing(12)
        layout.addWidget(self.grid_host)
        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        self.add_title = QLabel()
        self.add_title.setObjectName("Heading")
        self.add_title.setStyleSheet("font-size:16px; font-weight:750; background:transparent;")
        self.add_body = QLabel()
        self.add_body.setObjectName("Muted")
        self.add_body.setWordWrap(True)
        form = QFormLayout()
        self.add_name = QLineEdit()
        self.add_formula = QLineEdit()
        self.add_note = QLineEdit()
        self.add_category = QComboBox()
        form.addRow(self._caption("name"), self.add_name)
        form.addRow(self._caption("library_formula"), self.add_formula)
        form.addRow(self._caption("library"), self.add_category)
        form.addRow(self._caption("library_note"), self.add_note)
        self.name_caption, self.formula_caption, self.group_caption, self.note_caption = form.labelForField(self.add_name), form.labelForField(self.add_formula), form.labelForField(self.add_category), form.labelForField(self.add_note)
        self.save_button = QPushButton()
        self.save_button.setObjectName("Primary")
        self.save_button.clicked.connect(self.save_addition)
        self.add_status = QLabel()
        self.add_status.setWordWrap(True)
        form_layout.addWidget(self.add_title)
        form_layout.addWidget(self.add_body)
        form_layout.addLayout(form)
        form_layout.addWidget(self.save_button)
        form_layout.addWidget(self.add_status)
        layout.addWidget(form_card)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(page)
        return scroll

    def _caption(self, key: str) -> QLabel:
        label = QLabel()
        label.setObjectName("Muted")
        label.setProperty("i18n", key)
        return label

    def _detail_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        self.back_button = QPushButton()
        self.back_button.clicked.connect(self._leave_detail)
        outer.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignLeft)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.detail_host = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_host)
        scroll.setWidget(self.detail_host)
        outer.addWidget(scroll, 1)
        return page

    def set_category(self, category: str) -> None:
        self._category = category
        self.rebuild()

    def show_list(self) -> None:
        self._open_id = ""
        self.stack.setCurrentIndex(0)

    def _leave_detail(self) -> None:
        if self._external_back is not None:
            self._external_back()
        else:
            self.show_list()

    def records(self) -> list[dict]:
        con = self._connection()
        additions = list_library_additions(con) if con is not None else []
        return all_records(additions)

    def rebuild(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        rows = filter_records(self.records(), self.search.text(), self._category)
        self.empty.setVisible(not rows)
        for index, record in enumerate(rows):
            self.grid.addWidget(self._card(record), index // 2, index % 2)
        row_count = (len(rows) + 1) // 2 if rows else 0
        self.grid_host.setMinimumHeight(row_count * 560)
        self.list_inner.setMinimumHeight(self.grid_host.minimumHeight() + 560)
        for key, button in self.filter_buttons.items():
            button.setChecked(key == self._category)
            button.setObjectName("Active" if key == self._category else "")
            button.style().unpolish(button)
            button.style().polish(button)
        if self._open_id:
            self._render_detail(self._open_id)

    def _card(self, record: dict) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setMinimumSize(340, 460)
        layout = QVBoxLayout(frame)
        picture = MediaView(record["id"], record["formula"], image_height=220)
        picture.retranslate(self.lang)
        name = QLabel(record_name(record, self.lang))
        name.setObjectName("Heading")
        name.setStyleSheet("font-size:18px; font-weight:750; background:transparent;")
        name.setWordWrap(True)
        formula = QLabel(record["formula"])
        formula.setObjectName("Muted")
        use_line = QLabel(general_field(record, "use", self.lang))
        use_line.setWordWrap(True)
        badge = QLabel(t("library_needs_verification", self.lang))
        badge.setObjectName("Warning")
        badge.setWordWrap(True)
        opener = QPushButton(t("home_open", self.lang))
        opener.setObjectName("Primary")
        record_id = record["id"]
        opener.clicked.connect(lambda checked=False, chosen=record_id: self.open_record(chosen))
        layout.addWidget(picture)
        layout.addWidget(name)
        layout.addWidget(formula)
        if use_line.text():
            layout.addWidget(use_line)
        layout.addWidget(badge)
        layout.addWidget(opener)
        return frame

    def open_record(self, record_id: str) -> None:
        if self._before_move is not None:
            self._before_move()
        self._open_id = record_id
        self._render_detail(record_id)
        self.stack.setCurrentIndex(1)

    def _render_detail(self, record_id: str) -> None:
        while self.detail_layout.count():
            item = self.detail_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        record = next((item for item in self.records() if item["id"] == record_id), None)
        if record is None:
            missing = QLabel(t("library_empty", self.lang))
            self.detail_layout.addWidget(missing)
            return
        card = QFrame()
        card.setObjectName("Card")
        body = QVBoxLayout(card)
        picture = MediaView(record["id"], record["formula"], image_height=360)
        picture.retranslate(self.lang)
        body.addWidget(picture)
        title = QLabel(record_name(record, self.lang))
        title.setObjectName("PageTitle")
        title.setWordWrap(True)
        body.addWidget(title)
        formula = QLabel(f"{t('library_formula', self.lang)}: {record['formula']}")
        body.addWidget(formula)
        body.addWidget(self._section("library_what", record_identity(record, self.lang)))
        use = general_field(record, "use", self.lang) or t("library_use_unverified", self.lang)
        body.addWidget(self._section("library_use", use))
        hazard = general_field(record, "hazard", self.lang)
        product = t("library_needs_verification", self.lang)
        body.addWidget(self._section("library_hazards", "\n".join(part for part in (hazard, product) if part)))
        body.addWidget(self._section("library_ghs", "\n".join((product, t("library_ghs_why", self.lang)))))
        body.addWidget(
            self._section(
                "library_ppe_field",
                "\n".join((t("library_ppe_general", self.lang), t("library_ppe_why", self.lang))),
            )
        )
        storage = general_field(record, "storage", self.lang)
        body.addWidget(
            self._section(
                "library_storage",
                "\n".join(part for part in (storage, t("library_storage_why", self.lang)) if part),
            )
        )
        body.addWidget(self._section("library_emergency", t("library_emergency_general", self.lang)))
        source = general_field(record, "source", self.lang)
        if source:
            body.addWidget(self._section("library_sds", source))
        sds = self._section("library_sds", "")
        self.sds_status = QLabel()
        self.sds_status.setWordWrap(True)
        sds_button = QPushButton(t("library_sds_button", self.lang))
        sds_button.clicked.connect(self.show_sds_status)
        sds.layout().addWidget(sds_button)
        sds.layout().addWidget(self.sds_status)
        body.addWidget(sds)
        if record.get("user_note"):
            body.addWidget(self._section("library_user_note", record["user_note"]))
        self.detail_layout.addWidget(card)
        self.detail_layout.addStretch()

    def _section(self, title_key: str, text: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("IconCard")
        layout = QVBoxLayout(frame)
        title = QLabel(t(title_key, self.lang))
        title.setObjectName("Heading")
        title.setStyleSheet("font-weight:750; background:transparent;")
        title.setWordWrap(True)
        body = QLabel(text)
        body.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(body)
        return frame

    def show_sds_status(self) -> None:
        self.sds_status.setText(t("library_sds_missing", self.lang))

    def save_addition(self) -> None:
        con = self._connection()
        if con is None:
            return
        try:
            add_library_chemical(
                con,
                name=self.add_name.text(),
                formula=self.add_formula.text(),
                category=self.add_category.currentData(),
                user_note=self.add_note.text(),
            )
        except ValidationError as exc:
            self.add_status.setObjectName("ResultBlocked")
            self.add_status.setText(t(exc.code, self.lang))
            self.add_status.style().unpolish(self.add_status)
            self.add_status.style().polish(self.add_status)
            return
        self.add_name.clear()
        self.add_formula.clear()
        self.add_note.clear()
        self.add_status.setObjectName("ResultOk")
        self.add_status.setText(t("library_added", self.lang))
        self.add_status.style().unpolish(self.add_status)
        self.add_status.style().polish(self.add_status)
        self.rebuild()

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.disclaimer.setText(t("library_disclaimer", lang))
        self.search.setPlaceholderText(t("library_search", lang))
        self.empty.setText(t("library_empty", lang))
        self.add_title.setText(t("library_add_title", lang))
        self.add_body.setText(t("library_add_body", lang))
        self.save_button.setText(t("library_save", lang))
        self.back_button.setText(t("library_back", lang))
        self.add_note.setPlaceholderText(t("library_note_hint", lang))
        labels = {
            self.name_caption: "name",
            self.formula_caption: "library_formula",
            self.group_caption: "library_group",
            self.note_caption: "library_note",
        }
        for label, key in labels.items():
            if label is not None:
                label.setText(t(key, lang))
        current = self.add_category.currentData()
        self.add_category.blockSignals(True)
        self.add_category.clear()
        for key in LIBRARY_CATEGORIES:
            self.add_category.addItem(t(f"category_{key}", lang), key)
        index = self.add_category.findData(current)
        self.add_category.setCurrentIndex(index if index >= 0 else 0)
        self.add_category.blockSignals(False)
        for key, button in self.filter_buttons.items():
            label_key = "library_all" if key == "all" else f"category_{key}"
            button.setText(t(label_key, lang))
        self.rebuild()
