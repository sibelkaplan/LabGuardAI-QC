"""Mudlogging Academy. Lessons open from category cards and from search."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.academy_anim import ScenePlayer
from app.card_images import FitImage, caption, lesson_image_key
from app.academy_content import CATEGORIES, filter_lessons, find_lesson, lesson_summary, lesson_text, lesson_title
from app.database import is_favorite, remember_lesson, toggle_favorite
from app.i18n import t
from app.local_tutor import answer
from app.speech import Narrator


def _clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child = item.layout()
        if widget is not None:
            narrator = getattr(widget, "narrator", None)
            if narrator is not None:
                narrator.stop()
            widget.setParent(None)
            widget.deleteLater()
        elif child is not None:
            _clear_layout(child)


class AcademyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "tr"
        self._category = "all"
        self._open_id = ""
        self._con = None
        self._on_change = None
        self._before_move = None
        self._external_back = None
        self.player: ScenePlayer | None = None
        self.narrator = Narrator()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._list_page())
        self.stack.addWidget(self._detail_page())
        self.stack.addWidget(self._tutor_page())
        root.addWidget(self.stack)
        self.retranslate("tr")

    def _list_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.banner = QLabel()
        self.banner.setWordWrap(True)
        self.banner.setObjectName("Warning")
        layout.addWidget(self.banner)
        self.search = QLineEdit()
        self.search.textChanged.connect(self.rebuild)
        layout.addWidget(self.search)
        filters = QGridLayout()
        filters.setSpacing(8)
        self.filter_buttons: dict[str, QPushButton] = {}
        for index, key in enumerate(("all",) + CATEGORIES):
            button = QPushButton()
            button.setCheckable(True)
            button.setMinimumHeight(36)
            button.clicked.connect(lambda checked=False, chosen=key: self.set_category(chosen))
            self.filter_buttons[key] = button
            filters.addWidget(button, index // 4, index % 4)
        layout.addLayout(filters)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setSpacing(12)
        scroll.setWidget(self.grid_host)
        layout.addWidget(scroll, 1)
        self.empty = QLabel()
        self.empty.setWordWrap(True)
        layout.addWidget(self.empty)
        return page

    def _detail_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.back_button = QPushButton()
        self.back_button.clicked.connect(self._leave_detail)
        layout.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignLeft)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.detail_host = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_host)
        scroll.setWidget(self.detail_host)
        layout.addWidget(scroll, 1)
        return page

    def _tutor_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.tutor_back = QPushButton()
        self.tutor_back.clicked.connect(self.show_list)
        layout.addWidget(self.tutor_back, 0, Qt.AlignmentFlag.AlignLeft)
        self.tutor_heading = QLabel()
        self.tutor_heading.setObjectName("PageTitle")
        self.tutor_note = QLabel()
        self.tutor_note.setWordWrap(True)
        self.tutor_note.setObjectName("Warning")
        self.tutor_question = QLineEdit()
        self.tutor_submit = QPushButton()
        self.tutor_submit.setObjectName("Primary")
        self.tutor_submit.clicked.connect(self._ask_tutor)
        self.tutor_answer = QLabel()
        self.tutor_answer.setWordWrap(True)
        self.tutor_answer.setObjectName("IconCard")
        layout.addWidget(self.tutor_heading)
        layout.addWidget(self.tutor_note)
        layout.addWidget(self.tutor_question)
        layout.addWidget(self.tutor_submit, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.tutor_answer)
        layout.addStretch()
        return page

    def attach(self, con, on_change) -> None:
        self._con = con
        self._on_change = on_change

    def set_category(self, category: str) -> None:
        self._category = category
        self.rebuild()

    def show_list(self) -> None:
        self._open_id = ""
        self.player = None
        self.stack.setCurrentIndex(0)
        self.rebuild()

    def _leave_detail(self) -> None:
        if self._external_back is not None:
            self._external_back()
        else:
            self.show_list()

    def open_lesson(self, lesson_id: str) -> None:
        lesson = find_lesson(lesson_id)
        if lesson is None:
            return
        if self._before_move is not None:
            self._before_move()
        self._open_id = lesson_id
        if self._con is not None:
            remember_lesson(self._con, lesson_id)
        if self._on_change is not None:
            self._on_change()
        self._render_detail(lesson)
        self.stack.setCurrentIndex(1)

    def show_tutor(self, question: str = "") -> None:
        self.tutor_question.setText(question)
        self.tutor_answer.setText("")
        self.stack.setCurrentIndex(2)
        if question.strip():
            self._ask_tutor()

    def visible_lessons(self) -> list[dict]:
        return filter_lessons(self.search.text(), self._category)

    def detail_plain_text(self) -> str:
        lesson = find_lesson(self._open_id)
        if lesson is None:
            return ""
        return lesson_text(lesson, self.lang)

    def rebuild(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        rows = self.visible_lessons()
        self.empty.setVisible(not rows)
        for index, lesson in enumerate(rows):
            self.grid.addWidget(self._card(lesson), index // 2, index % 2)
        self.grid_host.setMinimumHeight(((len(rows) + 1) // 2) * 320)
        for key, button in self.filter_buttons.items():
            button.setChecked(key == self._category)
            button.setObjectName("Active" if key == self._category else "Nav")
            button.style().unpolish(button)
            button.style().polish(button)

    def _card(self, lesson: dict) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setMinimumHeight(150)
        layout = QVBoxLayout(frame)
        title = QLabel(lesson_title(lesson, self.lang))
        title.setWordWrap(True)
        title.setObjectName("Heading")
        title.setStyleSheet("font-size:18px; font-weight:750; background:transparent;")
        image_key = lesson_image_key(lesson["id"])
        photo = FitImage(image_key, 96, self.lang)
        image_note = QLabel(caption(image_key, self.lang))
        image_note.setWordWrap(True)
        image_note.setObjectName("Muted")
        body = QLabel(lesson_summary(lesson, self.lang))
        body.setWordWrap(True)
        button = QPushButton(t("home_open", self.lang))
        button.setObjectName("Primary")
        lesson_id = lesson["id"]
        button.clicked.connect(lambda checked=False, chosen=lesson_id: self.open_lesson(chosen))
        layout.addWidget(title)
        layout.addWidget(photo)
        layout.addWidget(image_note)
        layout.addWidget(body)
        layout.addWidget(button, 0, Qt.AlignmentFlag.AlignLeft)
        return frame

    def _render_detail(self, lesson: dict) -> None:
        _clear_layout(self.detail_layout)
        self.player = None
        title = QLabel(lesson_title(lesson, self.lang))
        title.setWordWrap(True)
        title.setObjectName("PageTitle")
        self.detail_layout.addWidget(title)
        note = QLabel(t("mud_banner", self.lang))
        note.setWordWrap(True)
        note.setObjectName("Warning")
        self.detail_layout.addWidget(note)
        summary = QLabel(lesson_summary(lesson, self.lang))
        summary.setWordWrap(True)
        summary.setObjectName("Deep")
        summary.setStyleSheet("font-size:16px;")
        self.detail_layout.addWidget(summary)
        image_key = lesson_image_key(lesson["id"])
        if image_key:
            self.detail_layout.addWidget(FitImage(image_key, 180, self.lang))
            image_note = QLabel(caption(image_key, self.lang))
            image_note.setWordWrap(True)
            image_note.setObjectName("Muted")
            self.detail_layout.addWidget(image_note)
        if lesson["animation"]:
            self.player = ScenePlayer(lesson["animation"])
            self.player.retranslate(self.lang)
            self.detail_layout.addWidget(self.player)
        else:
            schematic = QLabel(t("mud_schematic", self.lang))
            schematic.setWordWrap(True)
            schematic.setObjectName("Warning")
            self.detail_layout.addWidget(schematic)
            self.see_label = QLabel(t("see_q", self.lang) + " " + lesson_summary(lesson, self.lang))
            self.see_label.setWordWrap(True)
            self.detail_layout.addWidget(self.see_label)
            listen_row = QHBoxLayout()
            self.listen_button = QPushButton(t("listen", self.lang))
            self.listen_button.clicked.connect(lambda checked=False, text=lesson_summary(lesson, self.lang): self._speak(text))
            self.speech_status = QLabel()
            self.speech_status.setWordWrap(True)
            self.speech_status.setObjectName("Muted")
            listen_row.addWidget(self.listen_button)
            listen_row.addWidget(self.speech_status, 1)
            self.detail_layout.addLayout(listen_row)
        source = lesson.get("source_en") if self.lang == "en" else lesson.get("source_tr")
        if source:
            short = source if len(source) <= 240 else source[:240].rsplit(" ", 1)[0] + "…"
            source_label = QLabel(short)
            source_label.setWordWrap(True)
            source_label.setObjectName("Muted")
            self.detail_layout.addWidget(source_label)
        self.details_button = QPushButton(t("details_open", self.lang))
        self.details_button.clicked.connect(self._toggle_details)
        self.detail_layout.addWidget(self.details_button, 0, Qt.AlignmentFlag.AlignLeft)
        self.details_host = QWidget()
        details = QVBoxLayout(self.details_host)
        details.setContentsMargins(0, 0, 0, 0)
        for section in lesson["sections"]:
            card = QFrame()
            card.setObjectName("IconCard")
            body = QVBoxLayout(card)
            heading = QLabel(section["title_en"] if self.lang == "en" else section["title_tr"])
            heading.setObjectName("Heading")
            heading.setStyleSheet("font-weight:750; background:transparent;")
            heading.setWordWrap(True)
            text = QLabel(section["body_en"] if self.lang == "en" else section["body_tr"])
            text.setWordWrap(True)
            body.addWidget(heading)
            body.addWidget(text)
            details.addWidget(card)
        self.details_host.setVisible(False)
        self.detail_layout.addWidget(self.details_host)
        self._add_tutor(lesson["id"])
        self._add_favorite(lesson["id"])
        self.detail_layout.addStretch()

    def _toggle_details(self) -> None:
        open_now = not self.details_host.isVisible()
        self.details_host.setVisible(open_now)
        self.details_button.setText(t("details_close" if open_now else "details_open", self.lang))

    def _speak(self, text: str) -> None:
        self.speech_status.setText(t(self.narrator.speak(text), self.lang))

    def _add_tutor(self, lesson_id: str) -> None:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        title = QLabel(t("tutor_title", self.lang))
        title.setObjectName("Heading")
        title.setStyleSheet("font-weight:750; background:transparent;")
        note = QLabel(t("tutor_offline", self.lang))
        note.setWordWrap(True)
        note.setObjectName("Warning")
        self.lesson_question = QLineEdit()
        self.lesson_question.setPlaceholderText(t("tutor_prompt", self.lang))
        ask = QPushButton(t("tutor_ask", self.lang))
        ask.setObjectName("Primary")
        ask.clicked.connect(lambda checked=False, chosen=lesson_id: self._ask_lesson(chosen))
        self.lesson_answer = QLabel()
        self.lesson_answer.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(note)
        layout.addWidget(self.lesson_question)
        layout.addWidget(ask, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.lesson_answer)
        self.detail_layout.addWidget(card)

    def _ask_lesson(self, lesson_id: str) -> None:
        result = answer(self.lesson_question.text(), lesson_id, self.lang)
        self.lesson_answer.setText(result["text"])
        self._last_tutor = result

    def _ask_tutor(self) -> None:
        result = answer(self.tutor_question.text(), "", self.lang)
        self.tutor_answer.setText(result["text"])
        self._last_tutor = result
        if result["open_id"]:
            self.open_lesson(result["open_id"])
            self.lesson_question.setText(self.tutor_question.text())
            self.lesson_answer.setText(result["text"])

    def _add_favorite(self, lesson_id: str) -> None:
        self.favorite_button = QPushButton(self._favorite_label(lesson_id))
        self.favorite_button.clicked.connect(lambda checked=False, chosen=lesson_id: self._toggle_favorite(chosen))
        self.detail_layout.addWidget(self.favorite_button, 0, Qt.AlignmentFlag.AlignLeft)

    def _favorite_label(self, lesson_id: str) -> str:
        marked = is_favorite(self._con, lesson_id) if self._con is not None else False
        return t("favorite_on" if marked else "favorite_add", self.lang)

    def _toggle_favorite(self, lesson_id: str) -> None:
        if self._con is None:
            return
        toggle_favorite(self._con, lesson_id)
        self.favorite_button.setText(self._favorite_label(lesson_id))
        if self._on_change is not None:
            self._on_change()

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.banner.setText(t("mud_banner", lang))
        self.search.setPlaceholderText(t("mud_search", lang))
        self.empty.setText(t("mud_empty", lang))
        self.back_button.setText(t("mud_back", lang))
        self.tutor_back.setText(t("mud_back", lang))
        self.tutor_heading.setText(t("tutor_title", lang))
        self.tutor_note.setText(t("tutor_offline", lang))
        self.tutor_question.setPlaceholderText(t("tutor_prompt", lang))
        self.tutor_submit.setText(t("tutor_ask", lang))
        for key, button in self.filter_buttons.items():
            label = "mud_all" if key == "all" else f"mud_cat_{key}"
            button.setText(t(label, lang))
        self.rebuild()
        if self._open_id:
            lesson = find_lesson(self._open_id)
            if lesson is not None:
                self._render_detail(lesson)
