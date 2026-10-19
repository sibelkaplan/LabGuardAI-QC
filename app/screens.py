"""Additional screens: calculations, chemical record, chart, and quiz."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.calc.concentration import convert_mass, convert_volume, mass_from_molarity, mass_from_solution
from app.calc.dilution import hazardous_product_dilution, solve_dilution
from app.calc.mudlogging import (
    annular_capacity,
    annular_velocity,
    ecd,
    hydrostatic_pressure,
    lag_time,
    pipe_capacity,
    pit_volume,
)
from app.calc.result import CalcResult
from app.calc.stock import days_of_supply
from app.calc.units import CONCENTRATION_BASES
from app.constants import GHS_CODES
from app.card_images import FitImage, caption
from app.i18n import t
from app.training import QUIZ, score_quiz

STATUS_COLORS = {
    "ok": "#0B5964",
    "expiring": "#8A5A00",
    "expired": "#8C2F2F",
    "review": "#3E595D",
}


class StatusChart(QWidget):
    """Bar chart of date-status counts already stored in the database."""

    def __init__(self):
        super().__init__()
        self.counts = {"ok": 0, "expiring": 0, "expired": 0, "review": 0}
        self.lang = "tr"
        self.setMinimumHeight(150)

    def set_counts(self, counts: dict[str, int], lang: str) -> None:
        self.counts = {key: int(counts.get(key, 0)) for key in self.counts}
        self.lang = lang
        self.update()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#FFFFFF"))
        keys = list(self.counts)
        total = sum(self.counts.values())
        width = max(self.width() - 40, 1)
        gap = 16
        bar_width = max((width - gap * (len(keys) - 1)) / len(keys), 20)
        baseline = self.height() - 28
        top = 16
        peak = max(self.counts.values()) or 1
        for index, key in enumerate(keys):
            value = self.counts[key]
            height = 0 if total == 0 else (baseline - top) * value / peak
            left = 20 + index * (bar_width + gap)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(STATUS_COLORS[key]))
            painter.drawRoundedRect(int(left), int(baseline - height), int(bar_width), int(height), 6, 6)
            painter.setPen(QPen(QColor("#18353A")))
            label = t(f"status_{key}" if key != "ok" else "status_ok", self.lang)
            if key == "expiring":
                label = t("status_expiring", self.lang)
            elif key == "expired":
                label = t("status_expired", self.lang)
            elif key == "review":
                label = t("status_review", self.lang)
            else:
                label = t("status_ok", self.lang)
            painter.drawText(int(left), baseline + 4, int(bar_width), 20, Qt.AlignmentFlag.AlignCenter, f"{label} {value}")
        painter.end()


def _card() -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(8)
    return frame, layout


def _result_label() -> QLabel:
    label = QLabel()
    label.setWordWrap(True)
    label.setObjectName("ResultBlocked")
    label.setText("")
    label.setVisible(False)
    return label


def _apply_result(label: QLabel, result: CalcResult, lang: str) -> None:
    label.setObjectName("ResultBlocked" if result.blocked else "ResultOk")
    lines = [t(result.code, lang)]
    if result.value is not None:
        lines.append(f"{result.value:.6g} {result.unit}".strip())
    if result.formula:
        lines.append(result.formula)
    label.setText("\n".join(lines))
    label.setVisible(True)
    label.style().unpolish(label)
    label.style().polish(label)


class CalcPage(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "tr"
        self._texts: list[tuple[QWidget, str]] = []
        self._persist = None
        self._loader = None
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self.calc_image = FitImage("calc_scene", 120)
        self.calc_caption = QLabel()
        self.calc_caption.setObjectName("Muted")
        self.calc_caption.setWordWrap(True)
        root.addWidget(self.calc_image)
        root.addWidget(self.calc_caption)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._dilution_tab(), "")
        self.tabs.addTab(self._units_tab(), "")
        self.tabs.addTab(self._mud_tab(), "")
        self.tabs.addTab(self._stock_tab(), "")
        root.addWidget(self.tabs, 1)
        self.latest = _result_label()
        root.addWidget(self.latest)
        self.history = QTableWidget(0, 4)
        self.history.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history.verticalHeader().setVisible(False)
        self.history.setMinimumHeight(140)
        header = self.history.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setMinimumSectionSize(110)
        root.addWidget(self.history)

    def set_callbacks(self, persist, loader) -> None:
        self._persist = persist
        self._loader = loader

    def _bind(self, widget, key: str):
        self._texts.append((widget, key))
        return widget

    def _action(self, key: str, slot) -> QPushButton:
        button = QPushButton()
        button.setObjectName("Primary")
        button.setMaximumWidth(320)
        button.clicked.connect(slot)
        return self._bind(button, key)

    def _scroll(self, inner: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(inner)
        return scroll

    def _dilution_tab(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        note = self._bind(QLabel(), "calc_note")
        note.setWordWrap(True)
        note.setObjectName("Warning")
        layout.addWidget(note)
        card, body = _card()
        body.addWidget(self._bind(QLabel(), "same_basis_title"))
        hint = self._bind(QLabel(), "leave_one_blank")
        hint.setWordWrap(True)
        body.addWidget(hint)
        form = QFormLayout()
        self.basis = QComboBox()
        self.basis.addItems(list(CONCENTRATION_BASES))
        self.c1 = QLineEdit()
        self.v1 = QLineEdit()
        self.c2 = QLineEdit()
        self.v2 = QLineEdit()
        form.addRow(self._bind(QLabel(), "basis"), self.basis)
        form.addRow(self._bind(QLabel(), "c1"), self.c1)
        form.addRow(self._bind(QLabel(), "v1"), self.v1)
        form.addRow(self._bind(QLabel(), "c2"), self.c2)
        form.addRow(self._bind(QLabel(), "v2"), self.v2)
        body.addLayout(form)
        body.addWidget(self._action("calculate", self.calculate_dilution))
        self.dilution_result = _result_label()
        body.addWidget(self.dilution_result)
        layout.addWidget(card)
        blocked_card, blocked_body = _card()
        blocked_body.addWidget(self._bind(QLabel(), "hazardous_title"))
        hazard = self._bind(QLabel(), "hazardous_body")
        hazard.setWordWrap(True)
        blocked_body.addWidget(hazard)
        hazard_button = QPushButton()
        hazard_button.clicked.connect(self.calculate_hazardous)
        self._bind(hazard_button, "show_blocked")
        blocked_body.addWidget(hazard_button)
        self.hazard_result = _result_label()
        blocked_body.addWidget(self.hazard_result)
        layout.addWidget(blocked_card)
        layout.addStretch()
        return self._scroll(page)

    def _units_tab(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        card, body = _card()
        body.addWidget(self._bind(QLabel(), "units_title"))
        form = QFormLayout()
        self.unit_value = QLineEdit()
        self.unit_from = QComboBox()
        self.unit_from.addItems(["mL", "L", "mg", "g", "kg"])
        self.unit_to = QComboBox()
        self.unit_to.addItems(["mL", "L", "mg", "g", "kg"])
        form.addRow(self._bind(QLabel(), "value"), self.unit_value)
        form.addRow(self._bind(QLabel(), "from_unit"), self.unit_from)
        form.addRow(self._bind(QLabel(), "to_unit"), self.unit_to)
        body.addLayout(form)
        body.addWidget(self._action("calculate", self.calculate_units))
        self.units_result = _result_label()
        body.addWidget(self.units_result)
        layout.addWidget(card)
        mass_card, mass_body = _card()
        mass_form = QFormLayout()
        self.sol_conc = QLineEdit()
        self.sol_basis = QComboBox()
        self.sol_basis.addItems(["g/L", "mg/L", "mg/mL", "g/mL"])
        self.sol_volume = QLineEdit()
        self.sol_volume_unit = QComboBox()
        self.sol_volume_unit.addItems(["mL", "L"])
        self.sol_mass_unit = QComboBox()
        self.sol_mass_unit.addItems(["mg", "g", "kg"])
        mass_form.addRow(self._bind(QLabel(), "concentration"), self.sol_conc)
        mass_form.addRow(self._bind(QLabel(), "basis"), self.sol_basis)
        mass_form.addRow(self._bind(QLabel(), "solution_volume"), self.sol_volume)
        mass_form.addRow(self._bind(QLabel(), "volume_unit"), self.sol_volume_unit)
        mass_form.addRow(self._bind(QLabel(), "mass_unit"), self.sol_mass_unit)
        mass_body.addLayout(mass_form)
        mass_body.addWidget(self._action("calculate", self.calculate_solution_mass))
        self.solution_result = _result_label()
        mass_body.addWidget(self.solution_result)
        molar_form = QFormLayout()
        self.molarity = QLineEdit()
        self.molar_volume = QLineEdit()
        self.molar_mass = QLineEdit()
        self.molar_volume_unit = QComboBox()
        self.molar_volume_unit.addItems(["mL", "L"])
        molar_form.addRow(self._bind(QLabel(), "molarity"), self.molarity)
        molar_form.addRow(self._bind(QLabel(), "solution_volume"), self.molar_volume)
        molar_form.addRow(self._bind(QLabel(), "volume_unit"), self.molar_volume_unit)
        molar_form.addRow(self._bind(QLabel(), "molar_mass"), self.molar_mass)
        mass_body.addLayout(molar_form)
        mass_body.addWidget(self._action("calculate", self.calculate_molar_mass))
        self.molar_result = _result_label()
        mass_body.addWidget(self.molar_result)
        layout.addWidget(mass_card)
        layout.addStretch()
        return self._scroll(page)

    def _mud_tab(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        source = self._bind(QLabel(), "mud_source")
        source.setWordWrap(True)
        source.setObjectName("Warning")
        layout.addWidget(source)
        card, body = _card()
        body.addWidget(self._bind(QLabel(), "mud_title"))
        form = QFormLayout()
        self.mud_weight = QLineEdit()
        self.tvd = QLineEdit()
        self.pressure_loss = QLineEdit()
        form.addRow(self._bind(QLabel(), "mud_weight"), self.mud_weight)
        form.addRow(self._bind(QLabel(), "tvd"), self.tvd)
        form.addRow(self._bind(QLabel(), "pressure_loss"), self.pressure_loss)
        body.addLayout(form)
        body.addWidget(self._action("calc_hydrostatic", self.calculate_hydrostatic))
        self.mud_result = _result_label()
        body.addWidget(self.mud_result)
        body.addWidget(self._action("calc_ecd", self.calculate_ecd))
        self.ecd_result = _result_label()
        body.addWidget(self.ecd_result)
        layout.addWidget(card)
        geo, geo_body = _card()
        geo_form = QFormLayout()
        self.flow = QLineEdit()
        self.hole_id = QLineEdit()
        self.pipe_od = QLineEdit()
        self.pipe_id = QLineEdit()
        self.pit_length = QLineEdit()
        self.pit_width = QLineEdit()
        self.pit_height = QLineEdit()
        self.annular_volume = QLineEdit()
        self.pump_output = QLineEdit()
        geo_form.addRow(self._bind(QLabel(), "flow"), self.flow)
        geo_form.addRow(self._bind(QLabel(), "hole_id"), self.hole_id)
        geo_form.addRow(self._bind(QLabel(), "pipe_od"), self.pipe_od)
        geo_form.addRow(self._bind(QLabel(), "pipe_id"), self.pipe_id)
        geo_form.addRow(self._bind(QLabel(), "length"), self.pit_length)
        geo_form.addRow(self._bind(QLabel(), "width"), self.pit_width)
        geo_form.addRow(self._bind(QLabel(), "height"), self.pit_height)
        geo_form.addRow(self._bind(QLabel(), "annular_volume"), self.annular_volume)
        geo_form.addRow(self._bind(QLabel(), "pump_output"), self.pump_output)
        geo_body.addLayout(geo_form)
        for key, slot in (
            ("calc_velocity", self.calculate_velocity),
            ("calc_capacity", self.calculate_capacity),
            ("calc_annulus", self.calculate_annulus),
            ("calc_pit", self.calculate_pit),
            ("calc_lag", self.calculate_lag),
        ):
            geo_body.addWidget(self._action(key, slot))
        self.geometry_result = _result_label()
        geo_body.addWidget(self.geometry_result)
        layout.addWidget(geo)
        layout.addStretch()
        return self._scroll(page)

    def _stock_tab(self) -> QScrollArea:
        page = QWidget()
        layout = QVBoxLayout(page)
        card, body = _card()
        body.addWidget(self._bind(QLabel(), "stock_title"))
        form = QFormLayout()
        self.on_hand = QLineEdit()
        self.on_hand_unit = QLineEdit()
        self.use_per_day = QLineEdit()
        self.use_unit = QLineEdit()
        form.addRow(self._bind(QLabel(), "on_hand"), self.on_hand)
        form.addRow(self._bind(QLabel(), "unit"), self.on_hand_unit)
        form.addRow(self._bind(QLabel(), "use_per_day"), self.use_per_day)
        form.addRow(self._bind(QLabel(), "unit"), self.use_unit)
        body.addLayout(form)
        body.addWidget(self._action("calculate", self.calculate_stock))
        self.stock_result = _result_label()
        body.addWidget(self.stock_result)
        layout.addWidget(card)
        layout.addStretch()
        return self._scroll(page)

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.calc_image.set_lang(lang)
        self.calc_caption.setText(caption("calc_scene", lang))
        for widget, key in self._texts:
            widget.setText(t(key, lang))
        self.tabs.setTabText(0, t("same_basis_title", lang))
        self.tabs.setTabText(1, t("units_title", lang))
        self.tabs.setTabText(2, t("mud_title", lang))
        self.tabs.setTabText(3, t("stock_title", lang))
        self.history.setHorizontalHeaderLabels(
            [t("calc", lang), t("result", lang), t("value", lang), t("timestamp", lang)]
        )
        self.refresh_history()

    def _remember(self, module: str, inputs: dict, result: CalcResult, label: QLabel) -> None:
        _apply_result(label, result, self.lang)
        _apply_result(self.latest, result, self.lang)
        if self._persist is not None:
            self._persist(module, inputs, result)
        self.refresh_history()

    def calculate_dilution(self) -> CalcResult:
        result = solve_dilution(
            c1=self.c1.text(),
            v1=self.v1.text(),
            c2=self.c2.text(),
            v2=self.v2.text(),
            basis=self.basis.currentText(),
        )
        self._remember(
            "dilution",
            {"c1": self.c1.text(), "v1": self.v1.text(), "c2": self.c2.text(), "v2": self.v2.text(), "basis": self.basis.currentText()},
            result,
            self.dilution_result,
        )
        return result

    def calculate_hazardous(self) -> CalcResult:
        result = hazardous_product_dilution(
            product_concentration=37,
            basis="percent_w_w",
            density=1.19,
            target_concentration=1,
            target_volume=1000,
            expert_approved=True,
            verified_product_data=True,
        )
        self._remember("dilution", {"hazardous": True}, result, self.hazard_result)
        return result

    def calculate_units(self) -> CalcResult:
        value = self.unit_value.text()
        source = self.unit_from.currentText()
        target = self.unit_to.currentText()
        if source in {"mL", "L"} and target in {"mL", "L"}:
            result = convert_volume(value, source, target)
        elif source in {"mg", "g", "kg"} and target in {"mg", "g", "kg"}:
            result = convert_mass(value, source, target)
        else:
            result = convert_volume(value, source, target)
        self._remember("units", {"value": value, "from": source, "to": target}, result, self.units_result)
        return result

    def calculate_solution_mass(self) -> CalcResult:
        result = mass_from_solution(
            concentration=self.sol_conc.text(),
            concentration_basis=self.sol_basis.currentText(),
            volume=self.sol_volume.text(),
            volume_unit=self.sol_volume_unit.currentText(),
            mass_unit=self.sol_mass_unit.currentText(),
        )
        self._remember("units", {"solution": self.sol_conc.text()}, result, self.solution_result)
        return result

    def calculate_molar_mass(self) -> CalcResult:
        result = mass_from_molarity(
            molarity_mol_per_l=self.molarity.text(),
            volume=self.molar_volume.text(),
            volume_unit=self.molar_volume_unit.currentText(),
            molar_mass_g_per_mol=self.molar_mass.text(),
            mass_unit=self.sol_mass_unit.currentText(),
        )
        self._remember("units", {"molarity": self.molarity.text(), "molar_mass": self.molar_mass.text()}, result, self.molar_result)
        return result

    def calculate_hydrostatic(self) -> CalcResult:
        result = hydrostatic_pressure(self.mud_weight.text(), self.tvd.text())
        self._remember(
            "mud",
            {"mud_weight": self.mud_weight.text(), "tvd": self.tvd.text()},
            result,
            self.mud_result,
        )
        return result

    def calculate_ecd(self) -> CalcResult:
        result = ecd(self.mud_weight.text(), self.pressure_loss.text(), self.tvd.text())
        self._remember(
            "mud",
            {"mud_weight": self.mud_weight.text(), "loss": self.pressure_loss.text(), "tvd": self.tvd.text()},
            result,
            self.ecd_result,
        )
        return result

    def calculate_velocity(self) -> CalcResult:
        result = annular_velocity(self.flow.text(), self.hole_id.text(), self.pipe_od.text())
        self._remember(
            "mud",
            {"flow": self.flow.text(), "hole": self.hole_id.text(), "pipe": self.pipe_od.text()},
            result,
            self.geometry_result,
        )
        return result

    def calculate_capacity(self) -> CalcResult:
        result = pipe_capacity(self.pipe_id.text())
        self._remember("mud", {"pipe_id": self.pipe_id.text()}, result, self.geometry_result)
        return result

    def calculate_annulus(self) -> CalcResult:
        result = annular_capacity(self.hole_id.text(), self.pipe_od.text())
        self._remember(
            "mud",
            {"hole": self.hole_id.text(), "pipe": self.pipe_od.text()},
            result,
            self.geometry_result,
        )
        return result

    def calculate_pit(self) -> CalcResult:
        result = pit_volume(self.pit_length.text(), self.pit_width.text(), self.pit_height.text())
        self._remember(
            "mud",
            {"length": self.pit_length.text(), "width": self.pit_width.text(), "height": self.pit_height.text()},
            result,
            self.geometry_result,
        )
        return result

    def calculate_lag(self) -> CalcResult:
        result = lag_time(self.annular_volume.text(), self.pump_output.text())
        self._remember(
            "mud",
            {"volume": self.annular_volume.text(), "pump": self.pump_output.text()},
            result,
            self.geometry_result,
        )
        return result

    def calculate_stock(self) -> CalcResult:
        result = days_of_supply(
            on_hand=self.on_hand.text(),
            on_hand_unit=self.on_hand_unit.text(),
            use_per_day=self.use_per_day.text(),
            use_unit=self.use_unit.text(),
        )
        self._remember(
            "stock",
            {"on_hand": self.on_hand.text(), "unit": self.on_hand_unit.text(), "use": self.use_per_day.text()},
            result,
            self.stock_result,
        )
        return result

    def refresh_history(self) -> None:
        rows = self._loader() if self._loader else []
        self.history.setRowCount(len(rows))
        for index, row in enumerate(rows):
            value = "" if row["value"] is None else f"{row['value']:.6g} {row['unit']}".strip()
            values = [row["module"], t(row["code"], self.lang), value, row["created_at"]]
            for column, text in enumerate(values):
                self.history.setItem(index, column, QTableWidgetItem(text))


class DetailPage(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "tr"
        self.record_id = None
        self._texts: list[tuple[QWidget, str]] = []
        self._facts: list[tuple[QLabel, str]] = []
        layout = QVBoxLayout(self)
        self.disclaimer = QLabel()
        self.disclaimer.setWordWrap(True)
        self.disclaimer.setObjectName("Warning")
        self._texts.append((self.disclaimer, "detail_disclaimer"))
        layout.addWidget(self.disclaimer)
        self.fact_card, fact_layout = _card()
        self.fact_labels = {}
        for key in ("name", "quantity", "unit", "location", "expiry", "status", "sds_document", "sds_revision", "qr_id"):
            row = QHBoxLayout()
            caption = QLabel()
            self._texts.append((caption, key))
            value = QLabel("—")
            value.setWordWrap(True)
            self.fact_labels[key] = value
            row.addWidget(caption, 1)
            row.addWidget(value, 2)
            fact_layout.addLayout(row)
        layout.addWidget(self.fact_card)
        ghs_card, ghs_layout = _card()
        hint = QLabel()
        hint.setWordWrap(True)
        self._texts.append((hint, "ghs_hint"))
        ghs_layout.addWidget(hint)
        self.ghs_boxes: dict[str, QCheckBox] = {}
        for code in GHS_CODES:
            box = QCheckBox()
            self._texts.append((box, code))
            self.ghs_boxes[code] = box
            ghs_layout.addWidget(box)
        self.ghs_empty = QLabel()
        self._texts.append((self.ghs_empty, "ghs_empty"))
        ghs_layout.addWidget(self.ghs_empty)
        self.ghs_marks = QLabel()
        self.ghs_marks.setWordWrap(True)
        ghs_layout.addWidget(self.ghs_marks)
        layout.addWidget(ghs_card)
        form_card, form_layout = _card()
        form = QFormLayout()
        self.purpose = QLineEdit()
        self.hazard_notes = QLineEdit()
        self.ppe_notes = QLineEdit()
        self.glove_notes = QLineEdit()
        self.storage_notes = QLineEdit()
        for key, field in (
            ("purpose", self.purpose),
            ("hazard_notes", self.hazard_notes),
            ("ppe_notes", self.ppe_notes),
            ("glove_notes", self.glove_notes),
            ("storage_notes", self.storage_notes),
        ):
            form.addRow(self._label(key), field)
        form_layout.addLayout(form)
        self.save_button = QPushButton()
        self.save_button.setObjectName("Primary")
        self._texts.append((self.save_button, "save_detail"))
        form_layout.addWidget(self.save_button)
        self.status = QLabel()
        self.status.setWordWrap(True)
        form_layout.addWidget(self.status)
        layout.addWidget(form_card)
        layout.addStretch()

    def _label(self, key: str) -> QLabel:
        label = QLabel()
        self._texts.append((label, key))
        return label

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        for widget, key in self._texts:
            widget.setText(t(key, lang))
        self._render_marks()

    def load(self, record: dict) -> None:
        self.record_id = record["id"]
        self.fact_labels["name"].setText(record["name"])
        quantity = record["quantity"]
        self.fact_labels["quantity"].setText(str(int(quantity) if float(quantity).is_integer() else quantity))
        self.fact_labels["unit"].setText(record["unit"])
        self.fact_labels["location"].setText(record["location"])
        self.fact_labels["expiry"].setText(record["expiry"] or "—")
        self.fact_labels["status"].setText(t({"ok": "status_ok", "expiring": "status_expiring", "expired": "status_expired", "review": "status_review"}[record["status"]], self.lang))
        self.fact_labels["sds_document"].setText(record["sds_document"] or "—")
        self.fact_labels["sds_revision"].setText(record["sds_revision"] or "—")
        self.fact_labels["qr_id"].setText(record["qr_id"] or "—")
        selected = set(filter(None, (record.get("ghs_codes") or "").split(",")))
        for code, box in self.ghs_boxes.items():
            box.setChecked(code in selected)
        self.purpose.setText(record.get("purpose") or "")
        self.hazard_notes.setText(record.get("hazard_notes") or "")
        self.ppe_notes.setText(record.get("ppe_notes") or "")
        self.glove_notes.setText(record.get("glove_notes") or "")
        self.storage_notes.setText(record.get("storage_notes") or "")
        self._render_marks()

    def notes(self) -> dict:
        codes = [code for code, box in self.ghs_boxes.items() if box.isChecked()]
        return {
            "purpose": self.purpose.text(),
            "hazard_notes": self.hazard_notes.text(),
            "ghs_codes": ",".join(codes),
            "ppe_notes": self.ppe_notes.text(),
            "glove_notes": self.glove_notes.text(),
            "storage_notes": self.storage_notes.text(),
        }

    def _render_marks(self) -> None:
        codes = [code for code, box in self.ghs_boxes.items() if box.isChecked()]
        self.ghs_empty.setVisible(not codes)
        if codes:
            self.ghs_marks.setText("  ".join(f"◆ {t(code, self.lang)}" for code in codes))
        else:
            self.ghs_marks.setText("")


class QuizPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "tr"
        self._texts: list[tuple[QWidget, str]] = []
        self.groups: list[QButtonGroup] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel()
        self._texts.append((title, "quiz_title"))
        layout.addWidget(title)
        note = QLabel()
        note.setWordWrap(True)
        note.setObjectName("Muted")
        self._texts.append((note, "quiz_note"))
        layout.addWidget(note)
        for item in QUIZ:
            question = QLabel()
            question.setWordWrap(True)
            self._texts.append((question, item["question"]))
            layout.addWidget(question)
            group = QButtonGroup(self)
            self.groups.append(group)
            for index, key in enumerate(item["choices"]):
                choice = QRadioButton()
                self._texts.append((choice, key))
                group.addButton(choice, index)
                layout.addWidget(choice)
        self.submit = QPushButton()
        self.submit.setObjectName("Primary")
        self.submit.clicked.connect(self.grade)
        self._texts.append((self.submit, "quiz_submit"))
        layout.addWidget(self.submit)
        self.score = QLabel()
        self.score.setWordWrap(True)
        layout.addWidget(self.score)

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        for widget, key in self._texts:
            widget.setText(t(key, lang))

    def grade(self) -> tuple[int, int]:
        choices = []
        for group in self.groups:
            checked = group.checkedId()
            choices.append(checked if checked >= 0 else -1)
        correct, total = score_quiz(choices)
        self.score.setText(f"{t('quiz_score', self.lang)}: {correct}/{total}. {t('quiz_note', self.lang)}")
        return correct, total
