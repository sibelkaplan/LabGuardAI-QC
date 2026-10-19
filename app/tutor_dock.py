"""Corner panel for the local lesson assistant.

The panel searches stored lessons. It is not a connected language model.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

from app.card_images import load_pixmap

from app.academy_content import find_lesson, lesson_title
from app.i18n import t
from app.local_tutor import answer

EXAMPLES = (
    "tutor_ex_bernard",
    "tutor_ex_auto",
    "tutor_ex_sample",
    "tutor_ex_gypsum",
    "tutor_ex_fluor",
    "tutor_ex_limit",
    "tutor_ex_device",
)


class TutorDock(QWidget):
    def __init__(self, open_lesson, on_place=None):
        super().__init__()
        self.setObjectName("TutorDock")
        self._open_lesson = open_lesson
        self._on_place = on_place
        self.lang = "tr"
        self._open_id = ""
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        self.panel = QFrame()
        self.panel.setObjectName("Card")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(8)
        header = QHBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("QuietTitle")
        self.title.setWordWrap(True)
        self.close_button = QPushButton()
        self.close_button.clicked.connect(self.close_panel)
        header.addWidget(self.title, 1)
        header.addWidget(self.close_button)
        panel_layout.addLayout(header)
        self.note = QLabel()
        self.note.setObjectName("Warning")
        self.note.setWordWrap(True)
        panel_layout.addWidget(self.note)
        self.examples_label = QLabel()
        self.examples_label.setObjectName("Muted")
        panel_layout.addWidget(self.examples_label)
        example_scroll = QScrollArea()
        example_scroll.setWidgetResizable(True)
        example_scroll.setFrameShape(QFrame.Shape.NoFrame)
        example_scroll.setMaximumHeight(116)
        self.example_host = QWidget()
        self.example_layout = QVBoxLayout(self.example_host)
        self.example_layout.setContentsMargins(0, 0, 0, 0)
        self.example_layout.setSpacing(4)
        example_scroll.setWidget(self.example_host)
        panel_layout.addWidget(example_scroll)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMinimumHeight(120)
        self.answer = QLabel()
        self.answer.setWordWrap(True)
        self.answer.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.answer)
        panel_layout.addWidget(scroll, 1)
        self.source = QLabel()
        self.source.setObjectName("Muted")
        self.source.setWordWrap(True)
        panel_layout.addWidget(self.source)
        self.link = QPushButton()
        self.link.setObjectName("Primary")
        self.link.clicked.connect(self._open_linked)
        self.link.hide()
        panel_layout.addWidget(self.link)
        row = QHBoxLayout()
        self.question = QLineEdit()
        self.question.returnPressed.connect(self.send)
        self.send_button = QPushButton()
        self.send_button.setObjectName("Primary")
        self.send_button.clicked.connect(self.send)
        row.addWidget(self.question, 1)
        row.addWidget(self.send_button)
        panel_layout.addLayout(row)
        self.panel.hide()
        root.addWidget(self.panel)
        self.launcher = QPushButton()
        self.launcher.setObjectName("RobotButton")
        self.launcher.setFixedSize(48, 48)
        self.launcher.setIcon(QIcon(load_pixmap("robot", 40, 40)))
        self.launcher.setIconSize(QSize(36, 36))
        self.launcher.clicked.connect(self.toggle)
        root.addWidget(self.launcher, 0, Qt.AlignmentFlag.AlignRight)
        self.retranslate("tr")

    def toggle(self) -> None:
        self.panel.setVisible(not self.panel.isVisible())
        if self.panel.isVisible():
            self.question.setFocus()
        self._moved()

    def close_panel(self) -> None:
        self.panel.hide()
        self._moved()

    def open_panel(self) -> None:
        self.panel.show()
        self.question.setFocus()
        self._moved()

    def _moved(self) -> None:
        if self._on_place is not None:
            self._on_place()

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.title.setText(t("tutor_panel", lang))
        self.note.setText(t("tutor_offline", lang))
        self.examples_label.setText(t("tutor_examples", lang))
        self.close_button.setText(t("tutor_close", lang))
        self.send_button.setText(t("tutor_send", lang))
        self.link.setText(t("tutor_open_lesson", lang))
        self.question.setPlaceholderText(t("tutor_prompt", lang))
        self.launcher.setToolTip(t("tutor_offline", lang))
        while self.example_layout.count():
            item = self.example_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        for key in EXAMPLES:
            button = QPushButton(t(key, lang))
            button.setMinimumHeight(30)
            button.clicked.connect(lambda checked=False, chosen=key: self.ask(t(chosen, self.lang)))
            self.example_layout.addWidget(button)

    def ask(self, text: str) -> None:
        self.open_panel()
        self.question.setText(text)
        self.send()

    def send(self) -> None:
        result = answer(self.question.text(), "", self.lang)
        self.answer.setText(result["text"])
        self._open_id = result.get("open_id") or ""
        lesson = find_lesson(self._open_id) if self._open_id else None
        source = ""
        if lesson is not None:
            source = lesson.get("source_en" if self.lang == "en" else "source_tr", "")
            source = " ".join(str(source).split())
            if len(source) > 180:
                source = source[:177] + "…"
            self.link.setText(t("tutor_open_lesson", self.lang) + " · " + lesson_title(lesson, self.lang))
        self.source.setText(source)
        self.source.setVisible(bool(source))
        self.link.setVisible(lesson is not None)

    def _open_linked(self) -> None:
        if not self._open_id:
            return
        self.close_panel()
        self._open_lesson(self._open_id)
