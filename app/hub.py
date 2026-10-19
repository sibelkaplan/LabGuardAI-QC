"""Laboratory home. Search, real recent lessons, and the existing page actions."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.academy_content import find_lesson, lesson_title
from app.card_images import FitImage, caption
from app.i18n import t
from app.learn_routes import search_targets
from app.logo import LogoMark

_MONTHS_TR = (
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
)
_DAYS_TR = ("Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar")
_MONTHS_EN = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
_DAYS_EN = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def format_now(lang: str) -> str:
    now = datetime.now().astimezone()
    clock = f"{now.hour:02d}:{now.minute:02d}"
    if lang == "en":
        return f"{_DAYS_EN[now.weekday()]}, {now.day} {_MONTHS_EN[now.month - 1]} {now.year}  {clock}"
    return f"{now.day} {_MONTHS_TR[now.month - 1]} {now.year} {_DAYS_TR[now.weekday()]}  {clock}"


def _shadow(widget: QWidget) -> None:
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(16)
    effect.setOffset(0, 2)
    effect.setColor(QColor(11, 89, 100, 28))
    widget.setGraphicsEffect(effect)


class WelcomeHeadline(QLabel):
    """Two-line headline. text() stays the plain catalog sentence."""

    def __init__(self):
        super().__init__()
        self.setObjectName("WelcomeTitle")
        self.setWordWrap(True)
        self.setTextFormat(Qt.TextFormat.RichText)
        self._plain = ""

    def set_headline(self, value: str) -> None:
        self._plain = value
        if value.endswith("Hoş Geldiniz"):
            head = value[: -len("Hoş Geldiniz")].strip()
            tail = "Hoş Geldiniz"
        elif value.startswith("Welcome to "):
            head = "Welcome to"
            tail = value[len("Welcome to ") :]
        else:
            head, tail = value, ""
        if tail:
            super().setText(f"{head}<br><span style='color:#0B5964'>{tail}</span>")
        else:
            super().setText(value)

    def text(self) -> str:
        return self._plain


class FeatureCard(QFrame):
    def __init__(self, tone: str, image_key: str, title_key: str, body_key: str, on_open):
        super().__init__()
        self.setObjectName("FeatureCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)
        self.setMinimumHeight(132)
        self._on_open = on_open
        self.title_key = title_key
        self.body_key = body_key
        self.image_key = image_key
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 10, 12, 10)
        row.setSpacing(10)
        self.photo = FitImage(image_key, 112)
        self.photo.setMinimumWidth(0)
        self.photo.setMaximumWidth(124)
        self.photo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        text = QVBoxLayout()
        text.setSpacing(4)
        self.title = QLabel()
        self.title.setObjectName("HeroTitle")
        self.title.setWordWrap(True)
        self.body = QLabel()
        self.body.setObjectName("Muted")
        self.body.setWordWrap(True)
        self.button = QPushButton()
        self.button.setObjectName("OpenLite")
        self.button.setMinimumHeight(32)
        self.button.setMaximumWidth(96)
        self.button.clicked.connect(on_open)
        text.addWidget(self.title)
        text.addWidget(self.body)
        text.addStretch(1)
        text.addWidget(self.button, 0, Qt.AlignmentFlag.AlignLeft)
        row.addWidget(self.photo, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addLayout(text, 1)
        _shadow(self)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self.button.underMouse():
            self._on_open()
        super().mouseReleaseEvent(event)

    def apply_language(self, lang: str) -> None:
        self.title.setText(t(self.title_key, lang))
        self.body.setText(t(self.body_key, lang))
        self.button.setText("›")
        note = caption(self.image_key, lang)
        self.photo.setToolTip(note)
        self.setToolTip(note)
        self.photo.set_lang(lang)


class QuickCard(QFrame):
    def __init__(self, image_key: str, title_key: str, on_open):
        super().__init__()
        self.setObjectName("QuickCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(64)
        self._on_open = on_open
        self.title_key = title_key
        self.body_key = ""
        self.image_key = image_key
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        self.photo = FitImage(image_key, 48)
        self.photo.setFixedWidth(64)
        text = QVBoxLayout()
        text.setSpacing(2)
        self.title = QLabel()
        self.title.setObjectName("QuietTitle")
        self.title.setWordWrap(True)
        self.body = QLabel()
        self.body.setObjectName("Muted")
        self.body.setWordWrap(True)
        self.body.hide()
        self.button = QPushButton("›")
        self.button.setObjectName("OpenLite")
        self.button.setFixedSize(32, 32)
        self.button.clicked.connect(on_open)
        text.addWidget(self.title)
        text.addWidget(self.body)
        layout.addWidget(self.photo, 0)
        layout.addLayout(text, 1)
        layout.addWidget(self.button, 0, Qt.AlignmentFlag.AlignVCenter)
        _shadow(self)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self.button.underMouse():
            self._on_open()
        super().mouseReleaseEvent(event)

    def apply_language(self, lang: str) -> None:
        self.title.setText(t(self.title_key, lang))
        self.button.setText("›")
        self.button.setToolTip(t("home_open", lang))
        note = caption(self.image_key, lang)
        self.photo.setToolTip(note)
        self.setToolTip(note)
        self.photo.set_lang(lang)


class PhotoCard(QFrame):
    """Equal image card. The picture sits above a short title and an honest line."""

    def __init__(self, image_key: str, title_key: str, body_key: str, on_open):
        super().__init__()
        self.setObjectName("FeatureCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)
        self.setMinimumHeight(248)
        self._on_open = on_open
        self.title_key = title_key
        self.body_key = body_key
        self.image_key = image_key
        column = QVBoxLayout(self)
        column.setContentsMargins(10, 10, 10, 12)
        column.setSpacing(8)
        self.photo = FitImage(image_key, 128)
        self.photo.setMinimumWidth(0)
        self.title = QLabel()
        self.title.setObjectName("HeroTitle")
        self.title.setWordWrap(True)
        self.body = QLabel()
        self.body.setObjectName("Muted")
        self.body.setWordWrap(True)
        self.button = QPushButton("›")
        self.button.setObjectName("OpenLite")
        self.button.setFixedSize(32, 32)
        self.button.clicked.connect(on_open)
        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(self.title, 1)
        head.addWidget(self.button, 0, Qt.AlignmentFlag.AlignTop)
        column.addWidget(self.photo)
        column.addLayout(head)
        column.addWidget(self.body)
        column.addStretch(1)
        _shadow(self)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self.button.underMouse():
            self._on_open()
        super().mouseReleaseEvent(event)

    def apply_language(self, lang: str) -> None:
        self.title.setText(t(self.title_key, lang))
        self.body.setText(t(self.body_key, lang))
        self.button.setText("›")
        note = caption(self.image_key, lang)
        self.photo.setToolTip(note)
        self.setToolTip(note)
        self.photo.set_lang(lang)


class HomePage(QWidget):
    def __init__(
        self,
        open_prepare,
        open_library,
        open_ppe,
        open_studio,
        open_category,
        open_calc,
        open_tutor,
        open_target,
        open_inventory=None,
        open_help=None,
    ):
        super().__init__()
        self.lang = "tr"
        self.hero_image_key = "hero_lab"
        self._open_target = open_target
        self._open_help = open_help or (lambda: None)
        self._recent: list[str] = []
        self._favorites: list[str] = []
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        host = QWidget()
        host.setMinimumWidth(0)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(2, 2, 4, 18)
        layout.setSpacing(16)

        top = QHBoxLayout()
        top.setSpacing(10)
        self.search = QLineEdit()
        self.search.setObjectName("HomeSearch")
        self.search.setMinimumHeight(40)
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._show_results)
        self.search_go = QPushButton("→")
        self.search_go.setObjectName("Primary")
        self.search_go.setFixedSize(40, 40)
        self.search_go.clicked.connect(lambda: self._show_results(self.search.text()))
        self.search_go.hide()
        self.help_button = QPushButton("?")
        self.help_button.setObjectName("HelpLink")
        self.help_button.setFixedSize(36, 36)
        self.help_button.clicked.connect(self._open_help)
        top.addWidget(self.search, 1)
        top.addWidget(self.search_go, 0)
        top.addWidget(self.help_button, 0)
        layout.addLayout(top)

        self.welcome = QFrame()
        self.welcome.setObjectName("HeroShell")
        self.welcome.setMaximumHeight(280)
        shell = QHBoxLayout(self.welcome)
        shell.setContentsMargins(18, 14, 14, 14)
        shell.setSpacing(16)
        text = QVBoxLayout()
        text.setSpacing(8)
        self.logo = LogoMark()
        self.brand_name = QLabel("LabGuard AI")
        self.brand_name.setObjectName("Brand")
        self.brand_line = QLabel()
        self.brand_line.setObjectName("BrandTag")
        self.brand_line.setWordWrap(True)
        self.brand_name.hide()
        self.brand_line.hide()
        self.logo.hide()
        self.kicker = QLabel()
        self.kicker.setObjectName("WelcomeKicker")
        self.today = WelcomeHeadline()
        self.subtitle = QLabel()
        self.subtitle.setObjectName("WelcomeSub")
        self.subtitle.setWordWrap(True)
        text.addWidget(self.kicker)
        text.addWidget(self.today)
        text.addWidget(self.subtitle)
        self.start_button = QPushButton()
        self.start_button.setObjectName("Primary")
        self.start_button.setMinimumHeight(36)
        self.start_button.clicked.connect(open_studio)
        self.ask_button = QPushButton()
        self.ask_button.setObjectName("HelpLink")
        self.ask_button.setMinimumHeight(36)
        self.ask_button.clicked.connect(open_tutor)
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(self.start_button, 0)
        actions.addWidget(self.ask_button, 0)
        actions.addStretch(1)
        text.addLayout(actions)
        text.addStretch(1)
        self.demo_title = QLabel("DEMO")
        self.demo_title.setObjectName("DemoName")
        self.demo_note = QLabel()
        self.demo_note.hide()
        self.demo_date = QLabel()
        self.demo_date.hide()
        self.demo_title.hide()
        shell.addLayout(text, 5)
        picture = QVBoxLayout()
        picture.setSpacing(4)
        self.hero_photo = FitImage(self.hero_image_key, 168)
        self.hero_photo.setMinimumWidth(0)
        self.hero_photo.setMinimumHeight(180)
        self.banner_note = QLabel()
        self.banner_note.hide()
        picture.addWidget(self.hero_photo, 1)
        shell.addLayout(picture, 4)
        _shadow(self.welcome)
        layout.addWidget(self.welcome)

        self.results = QVBoxLayout()
        layout.addLayout(self.results)

        photos = QHBoxLayout()
        photos.setSpacing(12)
        self.prepare_card = PhotoCard("acid_pour", "prepare", "home_acid_body", open_prepare)
        self.rocks_card = PhotoCard("rock_samples", "mud_cat_rocks", "home_rocks_body", lambda: open_category("rocks"))
        self.tests_card = PhotoCard("tube_photo", "mud_cat_tests", "home_tests_body", lambda: open_category("tests"))
        self.mud_card = PhotoCard("instruments_photo", "mud_cat_devices", "home_devices_body", lambda: open_category("devices"))
        for card in (self.prepare_card, self.rocks_card, self.tests_card, self.mud_card):
            photos.addWidget(card, 1)
        layout.addLayout(photos)

        self.ppe_card = QuickCard("ppe_photo", "home_tile_ppe", open_ppe)
        self.calc_card = QuickCard("calc_scene", "calc", open_calc)
        self.inventory_card = QuickCard("inventory_scene", "inventory", open_inventory or (lambda: None))
        self.inspections_card = QuickCard("inspection_scene", "inspections", lambda: open_target("page", "inspections"))
        self.studio_card = QuickCard("studio_scene", "studio", open_studio)
        self.tutor_card = QuickCard("robot", "home_card_tutor", open_tutor)
        self.library_tile = QuickCard("flask", "library", open_library)

        self.samples_card = QuickCard("tray", "mud_cat_samples", lambda: open_category("samples"))
        self.library_card = QuickCard("flask", "library", open_library)
        self.samples_card.setParent(self)
        self.library_card.setParent(self)
        self.samples_card.hide()
        self.library_card.hide()

        lower = QHBoxLayout()
        lower.setSpacing(12)
        recent_box, self.recent_label, self.recent_row = self._column()
        favorite_box, self.favorite_label, self.favorite_row = self._column()
        tools = QFrame()
        tools.setObjectName("HomePanel")
        tools_box = QVBoxLayout(tools)
        tools_box.setContentsMargins(14, 14, 14, 14)
        tools_box.setSpacing(8)
        self.quick_label = QLabel()
        self.quick_label.setObjectName("HomeSection")
        tools_box.addWidget(self.quick_label)
        for card in (
            self.inventory_card,
            self.calc_card,
            self.inspections_card,
            self.ppe_card,
            self.studio_card,
        ):
            tools_box.addWidget(card)
        self.library_tile.setParent(self)
        self.library_tile.hide()
        tools_box.addStretch(1)
        safety = QFrame()
        safety.setObjectName("HomePanel")
        safety.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        safety_box = QVBoxLayout(safety)
        safety_box.setContentsMargins(14, 14, 14, 14)
        safety_box.setSpacing(6)
        self.safety_title = QLabel()
        self.safety_title.hide()
        for _label, _key in ():
            pass
        self.reminder_labels = []
        self.safety_note = QLabel()
        self.safety_note.setObjectName("Muted")
        self.safety_note.setWordWrap(True)
        safety_box.addWidget(self.safety_note)
        safety_box.insertWidget(0, self.tutor_card)
        safety_box.addStretch(1)
        self.safety_photo = FitImage("glove", 1)
        self.safety_photo.hide()
        self.safety_caption = QLabel()
        self.safety_caption.hide()
        _shadow(recent_box)
        _shadow(favorite_box)
        _shadow(tools)
        _shadow(safety)
        left = QVBoxLayout()
        left.setSpacing(12)
        left.addWidget(recent_box)
        favorite_box.setParent(self)
        favorite_box.hide()
        lower.addLayout(left, 1)
        lower.addWidget(tools, 1)
        lower.addWidget(safety, 1)
        layout.addLayout(lower)

        self.banner = FitImage("limestone", 72)
        self.banner_caption = QLabel()
        self.banner_caption.setObjectName("Muted")
        self.banner_caption.setWordWrap(True)
        self.field_line = QLabel()
        self.field_line.setObjectName("Muted")
        self.field_line.setWordWrap(True)
        self.banner.hide()
        self.banner_caption.hide()
        self.field_line.hide()
        layout.addStretch(1)
        self.scroll.setWidget(host)
        outer.addWidget(self.scroll)

        self._cards = (
            self.tutor_card,
            self.studio_card,
            self.calc_card,
            self.tests_card,
            self.samples_card,
            self.rocks_card,
            self.mud_card,
            self.library_card,
            self.library_tile,
            self.ppe_card,
            self.prepare_card,
            self.inventory_card,
            self.inspections_card,
        )
        self.retranslate("tr")

    def _column(self) -> tuple[QFrame, QLabel, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("HomePanel")
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)
        label = QLabel()
        label.setObjectName("HomeSection")
        label.setWordWrap(True)
        rows = QVBoxLayout()
        rows.setSpacing(6)
        layout.addWidget(label)
        layout.addLayout(rows)
        layout.addStretch(1)
        return frame, label, rows

    def set_marks(self, recent: list[str], favorites: list[str]) -> None:
        self._recent = list(recent)
        self._favorites = list(favorites)
        self._fill_marks()

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.search.setPlaceholderText(t("home_search_prompt", lang))
        self.brand_line.setText(t("brand_sub", lang))
        self.today.set_headline(t("home_welcome", lang))
        self.kicker.setText(t("home_kicker", lang))
        self.subtitle.setText(t("home_welcome_sub", lang))
        self.banner_note.setText(t("home_banner_note", lang))
        self.hero_photo.setToolTip(caption(self.hero_image_key, lang))
        self.hero_photo.set_lang(lang)
        self.help_button.setText("?")
        self.start_button.setText(t("home_start", lang))
        self.ask_button.setText(t("home_ask", lang))
        self.tutor_card.body.setWordWrap(True)
        self.tutor_card.body.setText(t("home_ask_body", lang))
        self.tutor_card.body.show()
        self.mud_card.body.setWordWrap(True)
        self.mud_card.body.setText(t("home_devices_body", lang))
        self.mud_card.body.show()
        self.demo_note.setText(t("demo_banner", lang))
        self.demo_date.setText(format_now(lang))
        self.quick_label.setText(t("home_quick", lang))
        self.recent_label.setText(t("home_recent", lang))
        self.favorite_label.setText(t("home_favorites", lang))
        self.safety_title.setText(t("home_safety_title", lang))
        self.safety_note.setText(t("home_safety_note", lang))
        for label, key in self.reminder_labels:
            label.setText("•  " + t(key, lang))
        self.safety_caption.setText(caption("glove", lang))
        self.safety_photo.setToolTip(caption("glove", lang))
        self.safety_photo.set_lang(lang)
        self.banner_caption.setText(caption("limestone", lang))
        self.field_line.setText(t("home_field_line", lang))
        self.banner.setToolTip(caption("limestone", lang))
        self.banner.hide()
        self.banner_caption.hide()
        self.field_line.hide()
        self.banner.set_lang(lang)
        for card in self._cards:
            card.apply_language(lang)
        self._show_results(self.search.text())
        self._fill_marks()

    def _show_results(self, text: str) -> None:
        while self.results.count():
            item = self.results.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        for kind, value, label in search_targets(text, self.lang):
            button = QPushButton(label)
            button.setObjectName("ListRow")
            button.setMinimumHeight(36 if "\n" not in label else 64)
            button.clicked.connect(lambda checked=False, chosen=(kind, value): self._open_target(*chosen))
            self.results.addWidget(button)

    def _fill_marks(self) -> None:
        self._fill_row(self.recent_row, self._recent, "empty")
        self._fill_row(self.favorite_row, self._favorites, "home_favorites_empty")

    def _fill_row(self, row: QVBoxLayout, lesson_ids: list[str], empty_key: str) -> None:
        while row.count():
            item = row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        shown = 0
        for lesson_id in lesson_ids[:3]:
            lesson = find_lesson(lesson_id)
            if lesson is None:
                continue
            button = QPushButton(lesson_title(lesson, self.lang) + "    ›")
            button.setObjectName("ListRow")
            button.clicked.connect(lambda checked=False, chosen=lesson_id: self._open_target("lesson", chosen))
            row.addWidget(button)
            shown += 1
        if shown == 0:
            empty = QLabel(t(empty_key, self.lang))
            empty.setObjectName("Muted")
            empty.setWordWrap(True)
            row.addWidget(empty)
