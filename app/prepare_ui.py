"""Step-by-step acid preparation interview.

The pages collect answers and explain the limits. They do not produce a
volume or mass of acid to add.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.calc.preparation import is_hcl_example, review_preparation
from app.card_images import FitImage, caption as image_caption
from app.calc.result import CalcResult
from app.calc.units import finite_number
from app.i18n import t

BASIS_CHOICES = (
    ("basis_ww", "percent_w_w"),
    ("basis_vv", "percent_v_v"),
    ("basis_wv", "percent_w_v"),
    ("basis_mol", "mol/L"),
)
STEP_KEYS = (
    "prep_step_chemical",
    "prep_step_basis",
    "prep_step_target",
    "prep_step_volume",
    "prep_step_check",
)


def _polish(widget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


class PrepareWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "tr"
        self.step = 0
        self._label_saver = None
        self.example_mode = False
        self.last_result: CalcResult | None = None
        self._texts: list[tuple[QWidget, str]] = []
        self._photos: list[tuple[FitImage, QLabel, str]] = []
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 4, 8, 4)
        root.setSpacing(12)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._scroll(self._home_page()))
        self.stack.addWidget(self._chemical_page())
        self.stack.addWidget(self._basis_page())
        self.stack.addWidget(self._target_page())
        self.stack.addWidget(self._volume_page())
        self.stack.addWidget(self._check_page())
        root.addWidget(self.stack, 1)
        self.progress = QHBoxLayout()
        self.progress.setSpacing(8)
        self.step_labels: list[QLabel] = []
        for key in STEP_KEYS:
            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._bind(label, key)
            self.step_labels.append(label)
            self.progress.addWidget(label, 1)
        self.progress_host = QWidget()
        self.progress_host.setLayout(self.progress)
        root.insertWidget(0, self.progress_host)
        footer = QHBoxLayout()
        self.back_button = QPushButton()
        self.back_button.clicked.connect(self.go_back)
        self._bind(self.back_button, "prep_back")
        self.next_button = QPushButton()
        self.next_button.setObjectName("Primary")
        self.next_button.setMinimumWidth(200)
        self.next_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.next_button.clicked.connect(self.go_next)
        self._bind(self.next_button, "prep_next")
        self.restart_button = QPushButton()
        self.restart_button.clicked.connect(self.start_over)
        self._bind(self.restart_button, "prep_restart")
        self.cancel_button = QPushButton()
        self.cancel_button.clicked.connect(self.show_home)
        self._bind(self.cancel_button, "prep_cancel")
        footer.addWidget(self.back_button)
        footer.addWidget(self.cancel_button)
        footer.addWidget(self.restart_button)
        footer.addStretch()
        footer.addWidget(self.next_button)
        self.footer_host = QWidget()
        self.footer_host.setLayout(footer)
        root.addWidget(self.footer_host)
        self.step_error = QLabel()
        self.step_error.setWordWrap(True)
        self.step_error.setObjectName("ResultBlocked")
        self.step_error.setVisible(False)
        root.addWidget(self.step_error)
        self.show_home()

    def _bind(self, widget, key: str):
        self._texts.append((widget, key))
        widget.setText(t(key, self.lang))
        return widget

    def _scroll(self, inner: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(inner)
        return scroll

    def _card(self) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)
        return frame, layout

    def _photo(self, key: str) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        image = FitImage(key, 96)
        label = QLabel()
        label.setObjectName("Muted")
        label.setWordWrap(True)
        layout.addWidget(image)
        layout.addWidget(label)
        self._photos.append((image, label, key))
        return box

    def _note(self, key: str, object_name: str = "Warning") -> QLabel:
        label = self._bind(QLabel(), key)
        label.setWordWrap(True)
        label.setObjectName(object_name)
        return label

    def _home_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        hero = QFrame()
        hero.setObjectName("Hero")
        hero.setMaximumWidth(720)
        hero.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        body = QVBoxLayout(hero)
        body.setContentsMargins(32, 28, 32, 28)
        body.setSpacing(14)
        icon = QLabel("HCl")
        icon.setObjectName("IconBubble")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.addWidget(icon, 0, Qt.AlignmentFlag.AlignLeft)
        title = self._bind(QLabel(), "prep_home_title")
        title.setObjectName("HeroTitle")
        title.setWordWrap(True)
        body.addWidget(title)
        intro = self._note("prep_home_body", "Muted")
        body.addWidget(intro)
        photos = QHBoxLayout()
        photos.setSpacing(8)
        for key in ("hcl", "flask", "beakers"):
            photos.addWidget(self._photo(key))
        body.addLayout(photos)
        self.assistant_note = self._note("assistant_note")
        body.addWidget(self.assistant_note)
        self.start_button = QPushButton()
        self.start_button.setObjectName("Primary")
        self.start_button.setMinimumHeight(48)
        self.start_button.setMinimumWidth(260)
        self.start_button.clicked.connect(self.start_new)
        self._bind(self.start_button, "prep_start")
        self.example_button = QPushButton()
        self.example_button.setMinimumHeight(44)
        self.example_button.clicked.connect(self.start_example)
        self._bind(self.example_button, "prep_example")
        body.addWidget(self.start_button)
        body.addWidget(self.example_button)
        chips = QVBoxLayout()
        chips.setSpacing(8)
        for key, mark in (
            ("prep_chip_questions", "1"),
            ("prep_chip_sds", "2"),
            ("prep_chip_quantity", "3"),
        ):
            chip = QLabel()
            chip.setObjectName("IconCard")
            chip.setWordWrap(True)
            chip.setText(f"  {mark}    {t(key, self.lang)}")
            self._texts.append((chip, key))
            chips.addWidget(chip)
        body.addLayout(chips)
        body.addWidget(self._calculator_card())
        row.addWidget(hero)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)
        return page

    def _calculator_card(self) -> QFrame:
        frame, body = self._card()
        title = self._bind(QLabel(), "calc_title")
        title.setObjectName("Heading")
        title.setStyleSheet("font-size:20px; font-weight:750; background:transparent;")
        body.addWidget(title)
        body.addWidget(self._note("calc_body", "Muted"))
        form = QFormLayout()
        self.calc_c1 = QLineEdit()
        self.calc_c2 = QLineEdit()
        self.calc_volume = QLineEdit()
        self.calc_unit = QComboBox()
        self.calc_unit.addItems(["mL", "L"])
        basis_row = QWidget()
        basis_layout = QVBoxLayout(basis_row)
        basis_layout.setContentsMargins(0, 0, 0, 0)
        self.calc_basis_group = QButtonGroup(self)
        self.calc_basis_buttons: dict[str, QRadioButton] = {}
        for key, value in BASIS_CHOICES:
            radio = QRadioButton()
            self._bind(radio, key)
            self.calc_basis_group.addButton(radio)
            self.calc_basis_buttons[value] = radio
            basis_layout.addWidget(radio)
        form.addRow(self._field_label("calc_c1"), self.calc_c1)
        form.addRow(self._field_label("calc_basis"), basis_row)
        form.addRow(self._field_label("calc_c2"), self.calc_c2)
        volume_row = QWidget()
        volume_layout = QHBoxLayout(volume_row)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.addWidget(self.calc_volume)
        volume_layout.addWidget(self.calc_unit)
        form.addRow(self._field_label("calc_volume"), volume_row)
        body.addLayout(form)
        self.calc_button = QPushButton()
        self.calc_button.setObjectName("Primary")
        self.calc_button.setMinimumHeight(42)
        self.calc_button.clicked.connect(self.run_calculator)
        self._bind(self.calc_button, "calc_run")
        body.addWidget(self.calc_button, 0, Qt.AlignmentFlag.AlignLeft)
        self.calc_result = QLabel()
        self.calc_result.setWordWrap(True)
        self.calc_result.setObjectName("ResultBlocked")
        self.calc_result.setVisible(False)
        body.addWidget(self.calc_result)
        self.last_calc = None
        return frame

    def _field_label(self, key: str) -> QLabel:
        label = self._bind(QLabel(), key)
        label.setObjectName("Muted")
        return label

    def run_calculator(self) -> None:
        missing = []
        if not self._positive(self.calc_c1.text()):
            missing.append(t("calc_c1", self.lang))
        if not self._calc_basis():
            missing.append(t("calc_basis", self.lang))
        if not self._positive(self.calc_c2.text()):
            missing.append(t("calc_c2", self.lang))
        if not self._positive(self.calc_volume.text()):
            missing.append(t("calc_volume", self.lang))
        if missing:
            self.last_calc = None
            self.calc_result.setText(t("calc_missing", self.lang) + " " + ", ".join(missing))
            self.calc_result.setVisible(True)
            return
        result = review_preparation(
            name="hesap",
            c1=self.calc_c1.text(),
            basis=self._calc_basis(),
            c2=self.calc_c2.text(),
            volume=self.calc_volume.text(),
            volume_unit=self.calc_unit.currentText(),
        )
        self.last_calc = result
        lines = [t(result.code, self.lang), t("prep_ratio_not_applied", self.lang)]
        if result.math_value is not None:
            lines.append(f"{t('prep_math_ok', self.lang)}: {result.math_value:g} {result.math_unit}")
            lines.append(t("prep_rounding", self.lang))
            lines.append(t("prep_not_approval", self.lang))
            lines.append(t("prep_density_only_ww", self.lang))
        else:
            lines.append(t(result.math_code, self.lang))
        lines.append(t("prep_approval_blocked", self.lang))
        lines.append(t("prep_acid_warning", self.lang))
        if result.value is not None:
            raise RuntimeError("Preparation review returned an approved quantity.")
        self.calc_result.setText("\n".join(lines))
        self.calc_result.setVisible(True)
        _polish(self.calc_result)

    def _calc_basis(self) -> str:
        for value, button in self.calc_basis_buttons.items():
            if button.isChecked():
                return value
        return ""

    def _chemical_page(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        card, body = self._card()
        body.addWidget(self._heading("prep_chemical_title"))
        body.addWidget(self._note("prep_chemical_body", "Muted"))
        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.c1_edit = QLineEdit()
        form.addRow(self._bind(QLabel(), "name"), self.name_edit)
        form.addRow(self._bind(QLabel(), "prep_c1"), self.c1_edit)
        body.addLayout(form)
        body.addWidget(self._note("prep_chemical_warn"))
        layout.addWidget(card)
        layout.addStretch()
        return self._scroll(page)

    def _basis_page(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        card, body = self._card()
        body.addWidget(self._heading("prep_basis_title"))
        body.addWidget(self._note("prep_basis_body", "Muted"))
        self.example_basis_note = self._note("prep_example_basis")
        body.addWidget(self.example_basis_note)
        self.basis_group = QButtonGroup(self)
        self.basis_buttons: dict[str, QRadioButton] = {}
        for key, basis in BASIS_CHOICES:
            button = QRadioButton()
            button.setProperty("basis", basis)
            self._bind(button, key)
            self.basis_group.addButton(button)
            self.basis_buttons[basis] = button
            body.addWidget(button)
        body.addWidget(self._note("prep_basis_warn"))
        layout.addWidget(card)
        layout.addStretch()
        return self._scroll(page)

    def _target_page(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        card, body = self._card()
        body.addWidget(self._heading("prep_target_title"))
        body.addWidget(self._note("prep_target_body", "Muted"))
        form = QFormLayout()
        self.c2_edit = QLineEdit()
        form.addRow(self._bind(QLabel(), "prep_c2"), self.c2_edit)
        body.addLayout(form)
        body.addWidget(self._note("prep_target_warn"))
        layout.addWidget(card)
        layout.addStretch()
        return self._scroll(page)

    def _volume_page(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        card, body = self._card()
        body.addWidget(self._heading("prep_volume_title"))
        body.addWidget(self._note("prep_volume_body", "Muted"))
        form = QFormLayout()
        self.volume_edit = QLineEdit()
        self.volume_unit = QComboBox()
        self.volume_unit.addItems(["mL", "L"])
        form.addRow(self._bind(QLabel(), "prep_final_volume"), self.volume_edit)
        form.addRow(self._bind(QLabel(), "unit"), self.volume_unit)
        body.addLayout(form)
        body.addWidget(self._note("prep_volume_warn"))
        layout.addWidget(card)
        layout.addStretch()
        return self._scroll(page)

    def _check_page(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        card, body = self._card()
        body.addWidget(self._heading("prep_check_title"))
        body.addWidget(self._note("prep_check_body", "Muted"))
        body.addWidget(self._bind(QLabel(), "prep_summary_title"))
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setObjectName("IconCard")
        body.addWidget(self.summary)
        self.density_box = QWidget()
        density_form = QFormLayout(self.density_box)
        self.density_edit = QLineEdit()
        self.density_edit.setPlaceholderText(t("prep_density_hint", self.lang))
        density_form.addRow(self._bind(QLabel(), "prep_density"), self.density_edit)
        self.density_note = self._note("prep_ww_volume_blocked")
        density_form.addRow(self.density_note)
        self.density_box.setVisible(False)
        body.addWidget(self.density_box)
        self.label_title = self._bind(QLabel(), "prep_label_title")
        body.addWidget(self.label_title)
        label_form = QFormLayout()
        self.label_concentration = QLineEdit()
        self.label_density = QLineEdit()
        self.label_sds = QLineEdit()
        label_form.addRow(self._bind(QLabel(), "prep_label_concentration"), self.label_concentration)
        label_form.addRow(self._bind(QLabel(), "prep_label_density"), self.label_density)
        label_form.addRow(self._bind(QLabel(), "prep_label_sds"), self.label_sds)
        body.addLayout(label_form)
        self.label_status = self._note("prep_label_status")
        body.addWidget(self.label_status)
        self.label_save = QPushButton()
        self.label_save.clicked.connect(self.save_label_note)
        self._bind(self.label_save, "prep_label_save")
        body.addWidget(self.label_save)
        self.label_result = QLabel()
        self.label_result.setWordWrap(True)
        body.addWidget(self.label_result)
        self.seen_basis = QCheckBox()
        self.seen_density = QCheckBox()
        self.seen_procedure = QCheckBox()
        for box, key in (
            (self.seen_basis, "prep_seen_basis"),
            (self.seen_density, "prep_seen_density"),
            (self.seen_procedure, "prep_seen_procedure"),
        ):
            self._bind(box, key)
            body.addWidget(box)
        body.addWidget(self._note("prep_check_warn"))
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setObjectName("ResultBlocked")
        self.result_label.setVisible(False)
        body.addWidget(self.result_label)
        layout.addWidget(card)
        layout.addStretch()
        return self._scroll(page)

    def _heading(self, key: str) -> QLabel:
        label = self._bind(QLabel(), key)
        label.setObjectName("Heading")
        label.setStyleSheet("font-size:22px; font-weight:750; background:transparent;")
        label.setWordWrap(True)
        return label

    def basis_value(self) -> str:
        button = self.basis_group.checkedButton()
        if button is None:
            return ""
        return str(button.property("basis") or "")

    def set_label_saver(self, saver) -> None:
        self._label_saver = saver

    def show_home(self) -> None:
        self.step = 0
        self.stack.setCurrentIndex(0)
        self.progress_host.setVisible(False)
        self.footer_host.setVisible(False)
        self.step_error.setVisible(False)

    def start_over(self) -> None:
        self._clear_answers()
        self.show_home()

    def start_new(self) -> None:
        self.example_mode = False
        self._clear_answers()
        self._show_step(1)

    def start_example(self) -> None:
        self.example_mode = True
        self._clear_answers()
        self.name_edit.setText("HCl")
        self.c1_edit.setText("32")
        self.c2_edit.setText("18,5")
        self._show_step(1)

    def _clear_answers(self) -> None:
        self.name_edit.clear()
        self.c1_edit.clear()
        self.c2_edit.clear()
        self.volume_edit.clear()
        self.volume_unit.setCurrentIndex(0)
        self.density_edit.clear()
        self.basis_group.setExclusive(False)
        for button in self.basis_buttons.values():
            button.setChecked(False)
        self.basis_group.setExclusive(True)
        self.seen_basis.setChecked(False)
        self.seen_density.setChecked(False)
        self.seen_procedure.setChecked(False)
        self.label_concentration.clear()
        self.label_density.clear()
        self.label_sds.clear()
        self.label_result.clear()
        self.last_result = None
        self.result_label.clear()
        self.result_label.setVisible(False)
        self.step_error.setVisible(False)

    def go_back(self) -> None:
        self.step_error.setVisible(False)
        if self.step <= 1:
            self.show_home()
            return
        self._show_step(self.step - 1)

    def go_next(self) -> None:
        if self.step == 0:
            return
        if not self._valid_step():
            return
        if self.step == 5:
            self._run_review()
            return
        self._show_step(self.step + 1)

    def _valid_step(self) -> bool:
        self.step_error.setVisible(False)
        if self.step == 1:
            if not self.name_edit.text().strip() or not self._positive(self.c1_edit.text()):
                return self._fail("prep_missing")
        elif self.step == 2:
            if not self.basis_value():
                return self._fail("prep_missing")
        elif self.step == 3:
            target = finite_number(self.c2_edit.text())
            start = finite_number(self.c1_edit.text())
            if target is None or target <= 0:
                return self._fail("prep_missing")
            if start is None or target >= start:
                return self._fail("prep_not_lower")
        elif self.step == 4:
            if not self._positive(self.volume_edit.text()):
                return self._fail("prep_missing")
        return True

    def _positive(self, text: str) -> bool:
        number = finite_number(text)
        return number is not None and number > 0

    def _fail(self, key: str) -> bool:
        self.step_error.setText(t(key, self.lang))
        self.step_error.setVisible(True)
        return False

    def _show_step(self, step: int) -> None:
        self.step = step
        self.stack.setCurrentIndex(step)
        self.progress_host.setVisible(True)
        self.footer_host.setVisible(True)
        self.step_error.setVisible(False)
        self.example_basis_note.setVisible(self.example_mode)
        self.density_box.setVisible(self.basis_value() == "percent_w_w")
        if step == 5:
            self._fill_summary()
            self.next_button.setText(t("prep_check_btn", self.lang))
        else:
            self.next_button.setText(t("prep_next", self.lang))
        self._paint_progress()

    def _paint_progress(self) -> None:
        for index, label in enumerate(self.step_labels, start=1):
            if index == self.step:
                name = "StepOn"
            elif index < self.step:
                name = "StepDone"
            else:
                name = "StepOff"
            label.setObjectName(name)
            _polish(label)

    def _fill_summary(self) -> None:
        basis_key = {value: key for key, value in BASIS_CHOICES}.get(self.basis_value(), "")
        basis_text = t(basis_key, self.lang) if basis_key else "—"
        lines = [
            f"{t('name', self.lang)}: {self.name_edit.text().strip()}",
            f"{t('prep_c1', self.lang)}: {self.c1_edit.text().strip()}",
            f"{t('prep_step_basis', self.lang)}: {basis_text}",
            f"{t('prep_c2', self.lang)}: {self.c2_edit.text().strip()}",
            f"{t('prep_final_volume', self.lang)}: {self.volume_edit.text().strip()} {self.volume_unit.currentText()}",
        ]
        self.summary.setText("\n".join(lines))

    def _run_review(self) -> None:
        result = review_preparation(
            name=self.name_edit.text(),
            c1=self.c1_edit.text(),
            basis=self.basis_value(),
            c2=self.c2_edit.text(),
            volume=self.volume_edit.text(),
            volume_unit=self.volume_unit.currentText(),
            density=self.density_edit.text(),
            sds_basis_checked=self.seen_basis.isChecked(),
            sds_density_checked=self.seen_density.isChecked(),
            procedure_checked=self.seen_procedure.isChecked(),
        )
        self.last_result = result
        self._show_result(result)

    def save_label_note(self) -> None:
        if self._label_saver is None:
            self.label_result.setText(t("prep_label_status", self.lang))
            return
        self._label_saver(
            self.name_edit.text().strip(),
            self.label_concentration.text().strip(),
            self.label_density.text().strip(),
            self.label_sds.text().strip(),
        )
        self.label_result.setText(t("prep_label_saved", self.lang))

    def _show_result(self, result) -> None:
        lines = [t(result.code, self.lang), t("prep_ratio_not_applied", self.lang)]
        if result.math_value is not None:
            lines.append(f"{t('prep_math_ok', self.lang)}: {result.math_value:g} {result.math_unit}")
            lines.append(t("prep_rounding", self.lang))
            lines.append(t("prep_not_approval", self.lang))
            lines.append(t("prep_density_only_ww", self.lang))
        else:
            lines.append(t(result.math_code, self.lang))
        lines.append(t("prep_approval_blocked", self.lang))
        lines.append(t("prep_acid_warning", self.lang))
        lines.append(t("prep_label_status", self.lang))
        if is_hcl_example(self.name_edit.text(), self.c1_edit.text(), self.c2_edit.text()):
            lines.append(t("prep_example_result", self.lang))
        if result.value is not None:
            raise RuntimeError("Preparation review returned an approved quantity.")
        self.result_label.setObjectName("ResultBlocked")
        self.result_label.setText("\n".join(lines))
        self.result_label.setVisible(True)
        _polish(self.result_label)

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        for image, label, key in self._photos:
            image.set_lang(lang)
            label.setText(image_caption(key, lang))
        for widget, key in self._texts:
            if isinstance(widget, QLabel) and widget is self.summary:
                continue
            text = t(key, lang)
            if widget in {self.start_button, self.example_button} or widget in self.step_labels:
                if widget in self.step_labels:
                    widget.setText(text)
                else:
                    widget.setText(text)
            else:
                widget.setText(text)
        chip_keys = {"prep_chip_questions": "1", "prep_chip_sds": "2", "prep_chip_quantity": "3"}
        for widget, key in self._texts:
            if key in chip_keys:
                widget.setText(f"  {chip_keys[key]}    {t(key, lang)}")
        self.density_edit.setPlaceholderText(t("prep_density_hint", lang))
        if self.step == 5:
            self.next_button.setText(t("prep_check_btn", lang))
            self._fill_summary()
        elif self.step > 0:
            self.next_button.setText(t("prep_next", lang))
        if self.last_result is not None and self.step == 5:
            self._show_result(self.last_result)
        if self.step_error.isVisible():
            current = self.step_error.text()
            for key in ("prep_missing", "prep_not_lower"):
                if current in {t(key, "tr"), t(key, "en")}:
                    self.step_error.setText(t(key, lang))
        if self.calc_result.text():
            self.run_calculator()
