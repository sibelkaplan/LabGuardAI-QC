"""Local acid-safety storyboard.

The scenes are a lesson. They are not a preparation instruction, and they
contain no measured quantities. Acid is drawn going into water. Water is
never drawn going onto concentrated acid.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.media_catalog import training_video
from app.motion import hit, paint_scene
from app.speech import Narrator

PETROL = QColor("#0B5964")
PALE = QColor("#E5F0F1")
INK = QColor("#18353A")
WATER = QColor("#8EBEB8")
ACID = QColor("#D7E38A")

SCENES = (
    {"id": "label", "visual": "label", "ms": 8000},
    {"id": "risk", "visual": "risk", "ms": 8000},
    {"id": "area", "visual": "area", "ms": 8000},
    {"id": "ppe", "visual": "ppe", "ms": 8000},
    {"id": "order", "visual": "acid_into_water", "ms": 12000},
    {"id": "emergency", "visual": "emergency", "ms": 8000},
    {"id": "waste", "visual": "waste", "ms": 8000},
)

QUESTIONS = (
    {"id": "q1", "correct": 1},
    {"id": "q2", "correct": 1},
    {"id": "q3", "correct": 1},
)


def scene_pours_water_on_acid(visual: str) -> bool:
    """The lesson never uses a visual that pours water onto concentrated acid."""
    return visual == "water_onto_acid"


class Stage(QWidget):
    def __init__(self, center: "TrainingCenter"):
        super().__init__()
        self.center = center
        self.setMinimumSize(380, 240)
        self.setMaximumHeight(420)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.width() > 16 and self.height() > 16:
            frame_w = self.width() - 16
            frame_h = self.height() - 16
            fx = (event.position().x() - 8) / frame_w
            fy = (event.position().y() - 8) / frame_h
            self.center.pick(fx, fy)
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#F7FBFA"))
        painter.setPen(QPen(PETROL, 3))
        painter.setBrush(QColor("#FFFFFF"))
        frame = QRectF(8, 8, self.width() - 16, self.height() - 16)
        painter.drawRoundedRect(frame, 18, 18)
        paint_scene(painter, frame, SCENES[self.center.scene_index]["visual"], self.center.progress(), self.center.lang)
        painter.end()


class TrainingCenter(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "tr"
        self.scene_index = 0
        self.elapsed = 0
        self.playing = False
        self.using_video = False
        self.video_error = ""
        self._seen = {0}
        self._answers: dict[str, int] = {}
        self._quiz_ready = False
        self._summary_ready = False
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._tick)
        self._texts: list[tuple[QWidget, str]] = []
        self._pick_key = ""
        self.narrator = Narrator()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setSpacing(12)
        self.banner = self._note("train_banner")
        layout.addWidget(self.banner)
        self.video_note = self._note("train_no_video", "Muted")
        layout.addWidget(self.video_note)
        row = QHBoxLayout()
        column = QVBoxLayout()
        self.stage = Stage(self)
        self.video_holder = QWidget()
        self.video_holder.setMinimumSize(640, 340)
        self.video_holder.setVisible(False)
        column.addWidget(self.stage)
        column.addWidget(self.video_holder)
        self.subtitle = QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setObjectName("CaptionChip")
        self.subtitle.setStyleSheet("font-size:18px; font-weight:650; padding:2px;")
        column.addWidget(self.subtitle)
        controls = QHBoxLayout()
        self.play_button = QPushButton()
        self.play_button.setObjectName("Primary")
        self.play_button.clicked.connect(self.play)
        self.pause_button = QPushButton()
        self.pause_button.clicked.connect(self.pause)
        self.restart_button = QPushButton()
        self.restart_button.clicked.connect(self.restart)
        self.prev_button = QPushButton()
        self.prev_button.clicked.connect(self.show_previous)
        self.next_button = QPushButton()
        self.next_button.clicked.connect(self.show_next)
        self.subtitles = QCheckBox()
        self.subtitles.setChecked(True)
        self.subtitles.toggled.connect(self._toggle_subtitles)
        self.listen_button = QPushButton()
        self.listen_button.clicked.connect(self.speak_step)
        self._texts.append((self.listen_button, "listen"))
        for button, key in (
            (self.play_button, "train_play"),
            (self.pause_button, "train_pause"),
            (self.restart_button, "train_restart"),
            (self.prev_button, "train_prev"),
            (self.next_button, "train_next"),
            (self.subtitles, "train_subtitles"),
        ):
            self._texts.append((button, key))
            controls.addWidget(button)
        controls.addWidget(self.listen_button)
        controls.addStretch()
        self.speech_status = QLabel()
        self.speech_status.setWordWrap(True)
        self.speech_status.setObjectName("Muted")
        self.progress_label = QLabel()
        self.progress_label.setObjectName("Muted")
        row.addLayout(column, 3)
        side = QFrame()
        side.setObjectName("Card")
        side_layout = QVBoxLayout(side)
        self.step_title = QLabel()
        self.step_title.setWordWrap(True)
        self.step_title.setObjectName("Heading")
        self.step_title.setStyleSheet("font-size:20px; font-weight:750; background:transparent;")
        self.narration = QLabel()
        self.narration.setWordWrap(True)
        self.ppe_label = self._side_label()
        self.eq_label = self._side_label()
        self.hazard_label = self._side_label()
        self.check_label = self._side_label()
        self.pick_label = QLabel()
        self.pick_label.setWordWrap(True)
        self.pick_label.setObjectName("Warning")
        side_layout.addWidget(self.step_title)
        side_layout.addWidget(self.pick_label)
        self.details_button = QPushButton()
        self.details_button.clicked.connect(self._toggle_details)
        self._texts.append((self.details_button, "details_open"))
        side_layout.addWidget(self.details_button)
        self.details_host = QWidget()
        details = QVBoxLayout(self.details_host)
        details.setContentsMargins(0, 0, 0, 0)
        for label in (self.narration, self.ppe_label, self.eq_label, self.hazard_label, self.check_label):
            details.addWidget(label)
        self.details_host.setVisible(False)
        side_layout.addWidget(self.details_host)
        self.quiz_button = QPushButton()
        self.quiz_button.setObjectName("Primary")
        self.quiz_button.clicked.connect(self.show_quiz)
        self._texts.append((self.quiz_button, "train_quiz"))
        side_layout.addWidget(self.quiz_button)
        side_layout.addStretch()
        side.setMinimumWidth(180)
        side.setMaximumWidth(280)
        row.addWidget(side, 2)
        layout.addLayout(row)
        layout.addLayout(controls)
        layout.addWidget(self.speech_status)
        layout.addWidget(self.progress_label)
        self.quiz_box = QFrame()
        self.quiz_box.setObjectName("Card")
        self.quiz_layout = QVBoxLayout(self.quiz_box)
        self.quiz_status = QLabel()
        self.quiz_status.setWordWrap(True)
        self.quiz_layout.addWidget(self.quiz_status)
        self.choice_groups: list[QButtonGroup] = []
        self.choice_buttons: list[list[QRadioButton]] = []
        for question in QUESTIONS:
            prompt = QLabel()
            prompt.setWordWrap(True)
            prompt.setObjectName("Deep")
            prompt.setStyleSheet("font-weight:700; background:transparent;")
            self._texts.append((prompt, f"train_{question['id']}"))
            self.quiz_layout.addWidget(prompt)
            group = QButtonGroup(self)
            buttons = []
            for choice in range(3):
                radio = QRadioButton()
                radio.setStyleSheet("background:transparent;")
                group.addButton(radio, choice)
                self._texts.append((radio, f"train_{question['id']}_{choice}"))
                self.quiz_layout.addWidget(radio)
                buttons.append(radio)
            self.choice_groups.append(group)
            self.choice_buttons.append(buttons)
        self.grade_button = QPushButton()
        self.grade_button.setObjectName("Primary")
        self.grade_button.clicked.connect(self.grade)
        self._texts.append((self.grade_button, "train_grade"))
        self.quiz_layout.addWidget(self.grade_button)
        self.quiz_box.setVisible(False)
        layout.addWidget(self.quiz_box)
        self.summary_box = QFrame()
        self.summary_box.setObjectName("Card")
        summary_layout = QVBoxLayout(self.summary_box)
        self.summary_title = QLabel()
        self.summary_title.setWordWrap(True)
        self.summary_title.setObjectName("Heading")
        self.summary_title.setStyleSheet("font-size:20px; font-weight:750; background:transparent;")
        self.summary_body = QLabel()
        self.summary_body.setWordWrap(True)
        self.summary_note = self._note("train_not_certificate")
        self._texts.append((self.summary_title, "train_summary_title"))
        self._texts.append((self.summary_body, "train_summary_body"))
        summary_layout.addWidget(self.summary_title)
        summary_layout.addWidget(self.summary_body)
        summary_layout.addWidget(self.summary_note)
        self.summary_box.setVisible(False)
        layout.addWidget(self.summary_box)
        scroll.setWidget(host)
        root.addWidget(scroll)
        self._mount_video()
        self.retranslate("tr")

    def _note(self, key: str, object_name: str = "Warning") -> QLabel:
        label = QLabel()
        label.setWordWrap(True)
        label.setObjectName(object_name)
        self._texts.append((label, key))
        return label

    def _side_label(self) -> QLabel:
        label = QLabel()
        label.setWordWrap(True)
        return label

    def _mount_video(self) -> None:
        path = training_video()
        self.using_video = False
        if path is None:
            return
        try:
            from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
            from PySide6.QtMultimediaWidgets import QVideoWidget
        except Exception as exc:
            self.video_error = str(exc)
            return
        self.using_video = True
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 340)
        holder_layout = QVBoxLayout(self.video_holder)
        holder_layout.setContentsMargins(0, 0, 0, 0)
        holder_layout.addWidget(self.video_widget)
        from PySide6.QtCore import QUrl

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.video_holder.setVisible(True)
        self.stage.setVisible(False)

    def progress(self) -> float:
        duration = SCENES[self.scene_index]["ms"]
        if duration <= 0:
            return 0.0
        return max(0.0, min(1.0, self.elapsed / duration))

    def play(self) -> None:
        if self.using_video:
            self.player.play()
        self.playing = True
        self.timer.start()

    def pause(self) -> None:
        self.playing = False
        self.timer.stop()
        if self.using_video:
            self.player.pause()

    def restart(self) -> None:
        self.pause()
        self.scene_index = 0
        self.elapsed = 0
        self._seen = {0}
        self._quiz_ready = False
        self._summary_ready = False
        self._answers = {}
        for group in self.choice_groups:
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)
        self.quiz_box.setVisible(False)
        self.summary_box.setVisible(False)
        self.quiz_status.setText("")
        if self.using_video:
            self.player.setPosition(0)
        self._refresh_scene()
        self.play()

    def show_previous(self) -> None:
        self.pause()
        self.show_scene(self.scene_index - 1)

    def show_next(self) -> None:
        self.pause()
        if self.scene_index >= len(SCENES) - 1:
            self.show_quiz()
            return
        self.show_scene(self.scene_index + 1)

    def show_scene(self, index: int) -> None:
        self.scene_index = max(0, min(index, len(SCENES) - 1))
        self.elapsed = 0
        self._pick_key = ""
        self.narrator.stop()
        self._seen.add(self.scene_index)
        self._refresh_scene()

    def pick(self, fx: float, fy: float) -> None:
        visual = SCENES[self.scene_index]["visual"]
        key = hit(visual, fx, fy)
        self._pick_key = f"train_pick_{key}" if key else ""
        self.pick_label.setText(t(self._pick_key, self.lang) if key else "")

    def speak_step(self) -> None:
        self._spoken = self.subtitle.text()
        self.speech_status.setText(t(self.narrator.speak(self._spoken), self.lang))

    def _toggle_details(self) -> None:
        open_now = not self.details_host.isVisible()
        self.details_host.setVisible(open_now)
        self.details_button.setText(t("details_close" if open_now else "details_open", self.lang))

    def show_quiz(self) -> None:
        self.pause()
        self._quiz_ready = True
        self.quiz_box.setVisible(True)
        self.summary_box.setVisible(False)

    def grade(self) -> None:
        right = 0
        for question, group in zip(QUESTIONS, self.choice_groups):
            chosen = group.checkedId()
            self._answers[question["id"]] = chosen
            if chosen == question["correct"]:
                right += 1
        self.quiz_status.setText(
            t("train_score", self.lang).format(right=right, total=len(QUESTIONS))
        )
        self._summary_ready = True
        self.summary_box.setVisible(True)

    def _tick(self) -> None:
        if not self.playing:
            return
        self.elapsed += self.timer.interval()
        if self.elapsed >= SCENES[self.scene_index]["ms"]:
            if self.scene_index < len(SCENES) - 1:
                self.scene_index += 1
                self.elapsed = 0
                self._pick_key = ""
                self.narrator.stop()
                self._seen.add(self.scene_index)
            else:
                self.pause()
                self.show_quiz()
        self._refresh_scene()

    def _toggle_subtitles(self, checked: bool) -> None:
        self.subtitle.setVisible(checked)

    def _refresh_scene(self) -> None:
        scene = SCENES[self.scene_index]
        scene_id = scene["id"]
        self.step_title.setText(t(f"train_{scene_id}_title", self.lang))
        self.narration.setText(t(f"train_{scene_id}_narration", self.lang))
        self.subtitle.setText(t(f"train_{scene_id}_sub", self.lang))
        self.ppe_label.setText(f"{t('train_ppe', self.lang)} {t(f'train_{scene_id}_ppe', self.lang)}")
        self.eq_label.setText(f"{t('train_eq', self.lang)} {t(f'train_{scene_id}_eq', self.lang)}")
        self.hazard_label.setText(
            f"{t('train_hazard', self.lang)} {t(f'train_{scene_id}_hazard', self.lang)}"
        )
        self.check_label.setText(
            f"{t('train_check', self.lang)} {t(f'train_{scene_id}_check', self.lang)}"
        )
        self.progress_label.setText(
            t("train_step", self.lang).format(n=self.scene_index + 1, total=len(SCENES))
        )
        self.pick_label.setText(t(self._pick_key, self.lang) if self._pick_key else "")
        self.stage.update()

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        for widget, key in self._texts:
            widget.setText(t(key, lang))
        self.video_note.setVisible(not self.using_video)
        self._refresh_scene()
        if self.quiz_status.text():
            self.grade()


def _font(painter: QPainter, size: int, bold: bool = False) -> None:
    font = QFont("Helvetica Neue", size)
    font.setBold(bold)
    painter.setFont(font)


def _draw_label(painter: QPainter, frame: QRectF, _progress: float, lang: str) -> None:
    _bottle(painter, frame.adjusted(40, 40, -frame.width() * 0.55, -40), t("train_word_label", lang))
    _sheet(painter, frame.adjusted(frame.width() * 0.48, 50, -40, -50), t("train_word_sds", lang))


def _draw_risk(painter: QPainter, frame: QRectF, _progress: float, lang: str) -> None:
    words = (t("train_word_risk", lang), t("train_word_procedure", lang), t("train_word_approval", lang))
    top = frame.top() + 50
    for word in words:
        box = QRectF(frame.left() + 70, top, frame.width() - 140, 58)
        painter.setPen(QPen(PETROL, 2))
        painter.setBrush(PALE)
        painter.drawRoundedRect(box, 10, 10)
        painter.setPen(INK)
        _font(painter, 16, True)
        painter.drawText(box, Qt.AlignmentFlag.AlignCenter, word)
        top += 74


def _draw_area(painter: QPainter, frame: QRectF, _progress: float, lang: str) -> None:
    hood = QRectF(frame.left() + 36, frame.top() + 40, frame.width() * 0.46, frame.height() - 80)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(hood, 8, 8)
    painter.drawLine(int(hood.left()), int(hood.center().y()), int(hood.right()), int(hood.center().y()))
    painter.setPen(INK)
    _font(painter, 14, True)
    painter.drawText(hood.adjusted(8, 8, -8, -8), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, t("train_word_hood", lang))
    eye = QRectF(hood.right() + 28, frame.top() + 48, 150, 90)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(PALE)
    painter.drawRoundedRect(eye, 12, 12)
    painter.setPen(INK)
    painter.drawText(eye, Qt.AlignmentFlag.AlignCenter, t("train_word_eyewash", lang))


def _draw_ppe(painter: QPainter, frame: QRectF, _progress: float, lang: str) -> None:
    words = (
        t("train_word_goggles", lang),
        t("train_word_shield", lang),
        t("train_word_glove", lang),
        t("train_word_coat", lang),
        t("train_word_shoes", lang),
    )
    gap = 16
    width = (frame.width() - 80 - gap * (len(words) - 1)) / len(words)
    left = frame.left() + 40
    for word in words:
        box = QRectF(left, frame.center().y() - 70, width, 140)
        painter.setPen(QPen(PETROL, 2))
        painter.setBrush(PALE)
        painter.drawRoundedRect(box, 12, 12)
        painter.setPen(INK)
        _font(painter, 12, True)
        painter.drawText(box.adjusted(6, 6, -6, -6), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, word)
        left += width + gap


def _draw_acid_into_water(painter: QPainter, frame: QRectF, progress: float, lang: str) -> None:
    """Water is in the vessel first. Acid drops then fall into that water."""
    beaker = QRectF(frame.center().x() - 70, frame.top() + 110, 150, 180)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(beaker, 8, 16)
    water_level = 0.15 + 0.55 * min(1.0, progress / 0.35)
    if progress >= 0.35:
        water_level = 0.7
    liquid_height = beaker.height() * water_level
    liquid = QRectF(beaker.left() + 6, beaker.bottom() - liquid_height - 6, beaker.width() - 12, liquid_height)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WATER)
    painter.drawRoundedRect(liquid, 4, 4)
    painter.setPen(INK)
    _font(painter, 14, True)
    painter.drawText(liquid, Qt.AlignmentFlag.AlignCenter, t("train_word_water", lang))
    bottle = QRectF(beaker.right() + 30, frame.top() + 36, 70, 90)
    painter.setPen(QPen(PETROL, 2))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(bottle, 8, 8)
    painter.drawText(bottle, Qt.AlignmentFlag.AlignCenter, t("train_word_acid", lang))
    if progress > 0.4:
        drop_progress = min(1.0, (progress - 0.4) / 0.45)
        start_y = bottle.bottom()
        end_y = liquid.top() + 8
        for offset in (0.0, 0.18, 0.36):
            local = drop_progress - offset
            if local <= 0 or local >= 1:
                continue
            y = start_y + (end_y - start_y) * local
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(ACID)
            painter.drawEllipse(QRectF(beaker.center().x() - 6, y, 12, 16))
    if progress > 0.82:
        painter.setPen(QPen(PETROL, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for index, rise in enumerate((18, 34, 50)):
            arc = QRectF(beaker.left() + 20 + index * 28, beaker.top() - rise, 24, 16)
            painter.drawArc(arc, 20 * 16, 140 * 16)


def _draw_emergency(painter: QPainter, frame: QRectF, _progress: float, lang: str) -> None:
    box = QRectF(frame.left() + 50, frame.center().y() - 60, frame.width() - 100, 120)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(PALE)
    painter.drawRoundedRect(box, 14, 14)
    painter.setPen(INK)
    _font(painter, 18, True)
    painter.drawText(box, Qt.AlignmentFlag.AlignCenter, t("train_word_plan", lang))


def _draw_waste(painter: QPainter, frame: QRectF, _progress: float, lang: str) -> None:
    _bottle(painter, frame.adjusted(frame.width() * 0.28, 40, -frame.width() * 0.28, -40), t("train_word_waste", lang))


def _bottle(painter: QPainter, box: QRectF, word: str) -> None:
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(box, 18, 18)
    neck = QRectF(box.center().x() - 18, box.top() - 16, 36, 24)
    painter.drawRoundedRect(neck, 6, 6)
    painter.setPen(INK)
    _font(painter, 16, True)
    painter.drawText(box, Qt.AlignmentFlag.AlignCenter, word)


def _sheet(painter: QPainter, box: QRectF, word: str) -> None:
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(box, 8, 8)
    painter.setPen(QPen(PALE, 6))
    for step in range(1, 4):
        y = box.top() + step * box.height() / 4
        painter.drawLine(int(box.left() + 16), int(y), int(box.right() - 16), int(y))
    painter.setPen(INK)
    _font(painter, 16, True)
    painter.drawText(box, Qt.AlignmentFlag.AlignCenter, word)
