"""Shared schematic motion. These are drawings, not photographs or video.

Acid is drawn falling into water that is already in the vessel.
Water is never drawn onto concentrated acid.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF

PETROL = QColor("#0B5964")
PALE = QColor("#E5F0F1")
INK = QColor("#18353A")
WATER = QColor("#7EB8C9")
ACID = QColor("#C6D36A")
GLASS = QColor("#F4FBFC")

# Fractions of the drawing frame: x, y, w, h.
HOTSPOTS = {
    "label": (("label", 0.06, 0.16, 0.36, 0.68), ("sds", 0.50, 0.18, 0.40, 0.64)),
    "ppe": (
        ("goggles", 0.04, 0.28, 0.17, 0.46),
        ("shield", 0.23, 0.28, 0.17, 0.46),
        ("glove", 0.42, 0.28, 0.17, 0.46),
    ),
    "acid_into_water": (("water", 0.30, 0.28, 0.28, 0.58), ("acid", 0.64, 0.10, 0.24, 0.36)),
    "area": (("hood", 0.06, 0.12, 0.48, 0.72),),
}


def hit(visual: str, fx: float, fy: float) -> str:
    for key, x, y, w, h in HOTSPOTS.get(visual, ()):
        if x <= fx <= x + w and y <= fy <= y + h:
            return key
    return ""


def paint_scene(painter: QPainter, frame: QRectF, visual: str, progress: float, lang: str) -> None:
    painter.save()
    if visual == "label":
        _label(painter, frame, progress, lang)
    elif visual == "risk":
        _risk(painter, frame, progress)
    elif visual == "area":
        _area(painter, frame, progress, lang)
    elif visual == "ppe":
        _ppe(painter, frame, progress)
    elif visual == "acid_into_water":
        _acid_into_water(painter, frame, progress, lang)
    elif visual == "emergency":
        _emergency(painter, frame, progress)
    elif visual == "waste":
        _waste(painter, frame, progress)
    elif visual == "wash_stack":
        _wash(painter, frame, progress)
    elif visual == "fluor_dish":
        _fluor(painter, frame, progress)
    elif visual == "fluor_cut":
        _fluor_cut(painter, frame, progress)
    elif visual in {"bernard_rig", "bernard_gas"}:
        _bernard(painter, frame, progress, rising=visual == "bernard_gas")
    else:
        _extra(painter, frame, visual, progress, lang)
    painter.restore()


def _font(painter: QPainter, size: int) -> None:
    font = QFont("Helvetica Neue", size)
    font.setBold(True)
    painter.setFont(font)


def _caption(painter: QPainter, rect: QRectF, word: str) -> None:
    painter.setPen(INK)
    _font(painter, 13)
    painter.drawText(rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, word)


def _label(painter: QPainter, frame: QRectF, progress: float, lang: str) -> None:
    bottle = QRectF(frame.left() + frame.width() * 0.10, frame.top() + frame.height() * 0.28, frame.width() * 0.22, frame.height() * 0.48)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(bottle, 16, 16)
    neck = QRectF(bottle.center().x() - 16, bottle.top() - 22, 32, 26)
    painter.drawRoundedRect(neck, 6, 6)
    slide = min(1.0, progress * 1.4)
    tag = QRectF(bottle.left() + 10, bottle.top() + 18 + (1 - slide) * 30, bottle.width() - 20, bottle.height() * 0.42)
    painter.setBrush(QColor("#F3E2A5"))
    painter.drawRoundedRect(tag, 6, 6)
    _caption(painter, bottle.adjusted(0, 0, 0, 22), "Etiket" if lang != "en" else "Label")
    sheet = QRectF(frame.left() + frame.width() * 0.52, frame.top() + frame.height() * 0.20, frame.width() * 0.32, frame.height() * 0.58)
    turn = 0.55 + 0.45 * min(1.0, progress)
    shown = QRectF(sheet.center().x() - sheet.width() * turn / 2, sheet.top(), sheet.width() * turn, sheet.height())
    painter.setPen(QPen(PETROL, 2))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(shown, 4, 4)
    painter.setPen(QPen(PALE, 4))
    for step in range(1, 4):
        y = shown.top() + shown.height() * step / 4
        painter.drawLine(int(shown.left() + 8), int(y), int(shown.right() - 8), int(y))
    _caption(painter, sheet.adjusted(0, 0, 0, 22), "SDS")


def _risk(painter: QPainter, frame: QRectF, progress: float) -> None:
    pulse = 1.0 + 0.06 * math.sin(progress * math.tau * 3)
    side = min(frame.width(), frame.height()) * 0.34 * pulse
    center = frame.center()
    triangle = [
        QPointF(center.x(), center.y() - side * 0.55),
        QPointF(center.x() - side * 0.55, center.y() + side * 0.42),
        QPointF(center.x() + side * 0.55, center.y() + side * 0.42),
    ]
    painter.setPen(QPen(QColor("#8A5A00"), 4))
    painter.setBrush(QColor("#F6E3A1"))
    painter.drawPolygon(QPolygonF(triangle))
    painter.setPen(QPen(QColor("#8A5A00"), 6))
    painter.drawLine(QPointF(center.x(), center.y() - side * 0.12), QPointF(center.x(), center.y() + side * 0.16))
    painter.drawPoint(QPointF(center.x(), center.y() + side * 0.26))


def _area(painter: QPainter, frame: QRectF, progress: float, lang: str) -> None:
    hood = QRectF(frame.left() + frame.width() * 0.08, frame.top() + frame.height() * 0.16, frame.width() * 0.46, frame.height() * 0.66)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(hood, 8, 8)
    sash_y = hood.top() + 16 + (hood.height() - 36) * min(1.0, progress)
    painter.setBrush(QColor("#D5E7EA"))
    painter.drawRect(QRectF(hood.left() + 8, sash_y, hood.width() - 16, 14))
    _caption(painter, hood, "Çeker ocak" if lang != "en" else "Hood")
    bowl = QRectF(hood.right() + 36, frame.top() + frame.height() * 0.34, 90, 36)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(bowl, 12, 12)
    arc = (progress * 2) % 1
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WATER)
    painter.drawEllipse(QRectF(bowl.center().x() - 8, bowl.top() - 28 + arc * 40, 16, 16))


def _ppe(painter: QPainter, frame: QRectF, progress: float) -> None:
    bob = 8 * math.sin(progress * math.tau * 2)
    slots = (0.08, 0.28, 0.48, 0.68, 0.84)
    top = frame.top() + frame.height() * 0.30
    _goggles(painter, frame.left() + frame.width() * slots[0], top + bob)
    _shield(painter, frame.left() + frame.width() * slots[1], top - bob)
    _glove(painter, frame.left() + frame.width() * slots[2], top + bob)
    _coat(painter, frame.left() + frame.width() * slots[3], top)
    _shoe(painter, frame.left() + frame.width() * slots[4], top + 20)


def _goggles(painter: QPainter, x: float, y: float) -> None:
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#D7EEF2"))
    painter.drawEllipse(QRectF(x, y, 34, 28))
    painter.drawEllipse(QRectF(x + 30, y, 34, 28))
    painter.drawArc(QRectF(x - 8, y + 6, 20, 16), 40 * 16, 120 * 16)


def _shield(painter: QPainter, x: float, y: float) -> None:
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#E7F4EA"))
    painter.drawRoundedRect(QRectF(x, y, 54, 70), 18, 18)
    painter.drawLine(QPointF(x + 8, y + 18), QPointF(x + 46, y + 18))


def _glove(painter: QPainter, x: float, y: float) -> None:
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#F2D7B5"))
    painter.drawRoundedRect(QRectF(x + 8, y + 24, 36, 48), 12, 12)
    for index in range(4):
        painter.drawRoundedRect(QRectF(x + 8 + index * 9, y, 10, 30), 4, 4)


def _coat(painter: QPainter, x: float, y: float) -> None:
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(QRectF(x, y + 10, 48, 70), 8, 8)
    painter.drawLine(QPointF(x + 24, y + 16), QPointF(x + 24, y + 74))


def _shoe(painter: QPainter, x: float, y: float) -> None:
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#20383C"))
    painter.drawRoundedRect(QRectF(x, y + 36, 46, 18), 6, 6)
    painter.drawRoundedRect(QRectF(x + 8, y + 18, 22, 22), 4, 4)


def _acid_into_water(painter: QPainter, frame: QRectF, progress: float, lang: str) -> None:
    beaker = QRectF(frame.center().x() - 90, frame.top() + frame.height() * 0.30, 130, frame.height() * 0.52)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(beaker, 10, 18)
    level = 0.42 + 0.18 * min(1.0, progress / 0.3)
    wave = 3 * math.sin(progress * math.tau * 4)
    liquid_h = beaker.height() * level
    liquid = QRectF(beaker.left() + 6, beaker.bottom() - liquid_h - 6 + wave * 0.2, beaker.width() - 12, liquid_h)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WATER)
    painter.drawRoundedRect(liquid, 6, 6)
    painter.setPen(QPen(QColor("#FFFFFF"), 2))
    painter.drawArc(QRectF(liquid.left() + 8, liquid.top() - 4, 28, 12), 0, 180 * 16)
    painter.setPen(INK)
    _font(painter, 14)
    painter.drawText(liquid, Qt.AlignmentFlag.AlignCenter, "Su" if lang != "en" else "Water")
    tilt = min(1.0, max(0.0, (progress - 0.15) / 0.35))
    bottle = QRectF(beaker.right() + 28, frame.top() + 28 + tilt * 10, 58, 78)
    painter.save()
    painter.translate(bottle.center())
    painter.rotate(28 * tilt)
    painter.translate(-bottle.center())
    painter.setPen(QPen(PETROL, 2))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(bottle, 8, 8)
    painter.drawRoundedRect(QRectF(bottle.center().x() - 8, bottle.top() - 12, 16, 16), 3, 3)
    painter.setPen(INK)
    _font(painter, 12)
    painter.drawText(bottle, Qt.AlignmentFlag.AlignCenter, "Asit" if lang != "en" else "Acid")
    painter.restore()
    if progress > 0.28:
        cycle = ((progress - 0.28) * 2.4) % 1.0
        start_y = bottle.bottom()
        end_y = liquid.top() + 6
        for offset in (0.0, 0.33, 0.66):
            local = (cycle + offset) % 1.0
            y = start_y + (end_y - start_y) * local
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(ACID)
            painter.drawEllipse(QRectF(beaker.center().x() - 6, y, 12, 16))


def _emergency(painter: QPainter, frame: QRectF, progress: float) -> None:
    head = QRectF(frame.center().x() - 70, frame.center().y() - 20, 140, 70)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(head, 16, 16)
    shower = QRectF(frame.center().x() - 16, frame.top() + 36, 32, 18)
    painter.setBrush(PETROL)
    painter.drawRoundedRect(shower, 4, 4)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WATER)
    for index in range(5):
        drop = (progress * 1.5 + index * 0.18) % 1.0
        y = shower.bottom() + drop * (head.top() - shower.bottom())
        painter.drawEllipse(QRectF(shower.center().x() - 16 + index * 8, y, 8, 12))


def _waste(painter: QPainter, frame: QRectF, progress: float) -> None:
    body = QRectF(frame.center().x() - 50, frame.center().y() - 40, 100, 130)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(body, 14, 14)
    cap_y = body.top() - 28 + (1 - min(1.0, progress * 1.3)) * 40
    painter.setBrush(PETROL)
    painter.drawRoundedRect(QRectF(body.center().x() - 18, cap_y, 36, 22), 4, 4)


def _wash(painter: QPainter, frame: QRectF, progress: float) -> None:
    shake = 10 * math.sin(progress * math.tau * 3)
    left = frame.left() + frame.width() * 0.16 + shake
    top = frame.top() + frame.height() * 0.22
    for index, color in enumerate((QColor("#D9E4C5"), QColor("#E7F0F2"), WATER)):
        sieve = QRectF(left, top + index * 48, frame.width() * 0.34, 36)
        painter.setPen(QPen(PETROL, 3))
        painter.setBrush(color)
        painter.drawRoundedRect(sieve, 16, 16)
        painter.setPen(QPen(PETROL, 1))
        for line in range(4):
            x = sieve.left() + 12 + line * 18
            painter.drawLine(QPointF(x, sieve.top() + 8), QPointF(x, sieve.bottom() - 8))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WATER)
    for index in range(4):
        fall = (progress * 1.6 + index * 0.22) % 1.0
        painter.drawEllipse(QRectF(left + frame.width() * 0.12, frame.top() + 16 + fall * 70, 8, 14))
    chunk = QRectF(frame.left() + frame.width() * 0.66, frame.top() + frame.height() * 0.42, 70, 36)
    painter.setPen(QPen(PETROL, 2))
    painter.setBrush(QColor("#C4B49A"))
    painter.drawRoundedRect(chunk, 8, 8)


def _fluor(painter: QPainter, frame: QRectF, progress: float) -> None:
    lamp = QRectF(frame.left() + frame.width() * 0.12, frame.top() + 24, 70, 28)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#24383C"))
    painter.drawRoundedRect(lamp, 6, 6)
    sweep = 0.15 + 0.55 * (0.5 + 0.5 * math.sin(progress * math.tau * 2))
    beam = QPointF(frame.left() + frame.width() * sweep, frame.top() + frame.height() * 0.72)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(186, 230, 120, 90))
    painter.drawPolygon(QPolygonF([
        QPointF(lamp.center().x() - 8, lamp.bottom()),
        QPointF(lamp.center().x() + 8, lamp.bottom()),
        beam,
    ]))
    dish = QRectF(frame.left() + frame.width() * 0.28, frame.top() + frame.height() * 0.58, frame.width() * 0.46, 28)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#1C2C30"))
    painter.drawRoundedRect(dish, 12, 12)
    for index in range(6):
        grain_x = dish.left() + 18 + index * 28
        lit = abs((grain_x - beam.x()) / frame.width()) < 0.08
        painter.setBrush(QColor("#E4F5A8") if lit else QColor("#6D7C80"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(grain_x, dish.top() + 6, 12, 12))


def _fluor_cut(painter: QPainter, frame: QRectF, progress: float) -> None:
    paper = QRectF(frame.center().x() - 90, frame.center().y() - 80, 180, 170)
    painter.setPen(QPen(PETROL, 2))
    painter.setBrush(QColor("#F7F4EA"))
    painter.drawRoundedRect(paper, 6, 6)
    ring = 20 + 48 * min(1.0, progress)
    painter.setPen(QPen(QColor("#C6D36A"), 6))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QRectF(paper.center().x() - ring / 2, paper.center().y() - ring / 2, ring, ring))


def _bernard(painter: QPainter, frame: QRectF, progress: float, rising: bool) -> None:
    sample = QRectF(frame.left() + frame.width() * 0.08, frame.top() + frame.height() * 0.48, frame.width() * 0.18, frame.height() * 0.32)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(sample, 12, 12)
    painter.setBrush(QColor("#C4B49A"))
    painter.drawRoundedRect(QRectF(sample.left() + 10, sample.bottom() - 28, sample.width() - 20, 16), 4, 4)
    acid = QRectF(frame.left() + frame.width() * 0.32, frame.top() + frame.height() * 0.16, frame.width() * 0.12, frame.height() * 0.28)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(acid, 8, 8)
    column = QRectF(frame.left() + frame.width() * 0.68, frame.top() + frame.height() * 0.14, 36, frame.height() * 0.70)
    painter.setBrush(GLASS)
    painter.drawRoundedRect(column, 8, 8)
    level = 0.55 - (0.22 * progress if rising else 0.0)
    liquid_top = column.top() + column.height() * level
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WATER)
    painter.drawRect(QRectF(column.left() + 4, liquid_top, column.width() - 8, column.bottom() - liquid_top - 4))
    if rising:
        bubble_y = column.bottom() - 20 - progress * (column.height() * 0.45)
        painter.setBrush(ACID)
        painter.drawEllipse(QRectF(column.center().x() - 8, bubble_y, 16, 16))
    painter.setPen(QPen(PETROL, 3))
    painter.drawLine(
        QPointF(sample.right(), sample.center().y()),
        QPointF(column.left(), column.center().y()),
    )


def _fr(frame: QRectF, x: float, y: float, w: float, h: float) -> QRectF:
    return QRectF(
        frame.left() + frame.width() * x,
        frame.top() + frame.height() * y,
        frame.width() * w,
        frame.height() * h,
    )


def _say(lang: str, turkish: str, english: str) -> str:
    return english if lang == "en" else turkish


def _note(painter: QPainter, rect: QRectF, word: str) -> None:
    painter.setPen(INK)
    _font(painter, 11)
    painter.drawText(rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, word)


def _fallback_flask(painter: QPainter, frame: QRectF) -> None:
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(frame.adjusted(8, 8, -8, -8), 12, 12)
    painter.drawEllipse(QRectF(frame.center().x() - 18, frame.center().y() - 28, 36, 16))
    painter.drawLine(QPointF(frame.center().x() - 10, frame.center().y() - 12), QPointF(frame.center().x() - 22, frame.center().y() + 24))
    painter.drawLine(QPointF(frame.center().x() + 10, frame.center().y() - 12), QPointF(frame.center().x() + 22, frame.center().y() + 24))
    painter.drawLine(QPointF(frame.center().x() - 22, frame.center().y() + 24), QPointF(frame.center().x() + 22, frame.center().y() + 24))


def _auto_cup(painter: QPainter, frame: QRectF, lang: str) -> None:
    cup = _fr(frame, 0.30, 0.22, 0.40, 0.46)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(cup, 16, 16)
    painter.drawEllipse(QRectF(cup.left() - 4, cup.top() - 8, cup.width() + 8, 16))
    painter.setBrush(QColor("#C4B49A"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QRectF(cup.center().x() - 30, cup.bottom() - 34, 22, 16))
    painter.drawEllipse(QRectF(cup.center().x() - 6, cup.bottom() - 30, 18, 14))
    painter.drawEllipse(QRectF(cup.center().x() + 12, cup.bottom() - 38, 14, 12))
    _note(painter, cup.adjusted(0, 0, 0, 28), _say(lang, "Örnek kabı", "Sample cup"))


def _auto_cell(painter: QPainter, frame: QRectF, lang: str) -> None:
    cell = _fr(frame, 0.18, 0.24, 0.40, 0.48)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(cell, 12, 12)
    lid = QRectF(cell.left() + 8, cell.top() - 12, cell.width() - 16, 16)
    painter.setBrush(PETROL)
    painter.drawRoundedRect(lid, 4, 4)
    painter.setPen(QPen(PETROL, 3))
    painter.drawLine(QPointF(cell.right(), cell.top() + 28), QPointF(cell.right() + frame.width() * 0.16, cell.top() + 8))
    inlet = _fr(frame, 0.64, 0.16, 0.18, 0.22)
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(inlet, 8, 8)
    painter.drawRoundedRect(QRectF(inlet.center().x() - 8, inlet.top() - 10, 16, 12), 3, 3)
    _note(painter, cell.adjusted(0, 0, 0, 24), _say(lang, "Kapalı hücre", "Closed cell"))
    _note(painter, inlet.adjusted(0, 0, 0, 22), _say(lang, "Asit girişi", "Acid inlet"))


def _auto_sensor(painter: QPainter, frame: QRectF, lang: str) -> None:
    probe = _fr(frame, 0.16, 0.34, 0.22, 0.28)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#D7EEF2"))
    painter.drawEllipse(QRectF(probe.left(), probe.top(), probe.width() * 0.7, probe.height() * 0.55))
    painter.drawLine(QPointF(probe.center().x(), probe.top() + probe.height() * 0.4), QPointF(probe.center().x(), probe.bottom()))
    screen = _fr(frame, 0.50, 0.26, 0.32, 0.32)
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(screen, 8, 8)
    painter.setPen(QPen(PALE, 3))
    painter.drawLine(QPointF(screen.left() + 12, screen.center().y()), QPointF(screen.right() - 12, screen.center().y()))
    _note(painter, probe.adjusted(0, 0, 0, 22), _say(lang, "Algılayıcı", "Sensor"))
    _note(painter, screen.adjusted(0, 0, 0, 22), _say(lang, "Boş ekran", "Blank display"))


def _water_three(painter: QPainter, frame: QRectF, lang: str) -> None:
    still = _fr(frame, 0.05, 0.18, 0.28, 0.55)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    flask = QRectF(still.left(), still.bottom() - still.height() * 0.42, still.width() * 0.42, still.height() * 0.38)
    painter.drawEllipse(flask)
    painter.drawLine(QPointF(flask.right(), flask.center().y()), QPointF(still.right() - 8, still.top() + 18))
    painter.drawEllipse(QRectF(still.right() - 28, still.top() + 8, 22, 22))
    di = _fr(frame, 0.37, 0.18, 0.26, 0.55)
    column = QRectF(di.center().x() - 16, di.top() + 8, 32, di.height() * 0.62)
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(column, 10, 10)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#C9D5C0"))
    for index in range(4):
        painter.drawEllipse(QRectF(column.left() + 8, column.top() + 10 + index * 18, 10, 10))
    ro = _fr(frame, 0.68, 0.18, 0.27, 0.55)
    tube = QRectF(ro.left(), ro.center().y() - 16, ro.width() * 0.72, 32)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(tube, 12, 12)
    painter.setPen(QPen(PETROL, 2, Qt.PenStyle.DashLine))
    painter.drawLine(QPointF(tube.center().x(), tube.top() + 4), QPointF(tube.center().x(), tube.bottom() - 4))
    _note(painter, still, _say(lang, "Distilasyon", "Distillation"))
    _note(painter, di, _say(lang, "Deiyonizasyon", "Deionization"))
    _note(painter, ro, _say(lang, "Ters ozmoz", "Reverse osmosis"))


def _water_flow(painter: QPainter, frame: QRectF, progress: float, lang: str) -> None:
    feed = _fr(frame, 0.06, 0.32, 0.20, 0.36)
    process = _fr(frame, 0.40, 0.24, 0.18, 0.48)
    product = _fr(frame, 0.74, 0.32, 0.20, 0.36)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(feed, 10, 10)
    painter.drawRoundedRect(product, 10, 10)
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(process, 8, 8)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WATER)
    painter.drawRoundedRect(QRectF(feed.left() + 6, feed.center().y(), feed.width() - 12, feed.height() * 0.35), 4, 4)
    painter.drawRoundedRect(QRectF(product.left() + 6, product.center().y(), product.width() - 12, product.height() * 0.35), 4, 4)
    shift = 8 * progress
    painter.setPen(QPen(PETROL, 3))
    painter.drawLine(QPointF(feed.right() + shift, feed.center().y()), QPointF(process.left() - 4 + shift, process.center().y()))
    painter.drawLine(QPointF(process.right() + shift, process.center().y()), QPointF(product.left() - 4 + shift, product.center().y()))
    _note(painter, feed.adjusted(0, 0, 0, 20), _say(lang, "Besleme", "Feed"))
    _note(painter, process.adjusted(0, 0, 0, 20), _say(lang, "İşlem", "Process"))
    _note(painter, product.adjusted(0, 0, 0, 20), _say(lang, "Ürün", "Product"))


def _acid_ppe(painter: QPainter, frame: QRectF, lang: str) -> None:
    slots = (
        (0.06, "goggles", _say(lang, "Gözlük", "Goggles")),
        (0.37, "shield", _say(lang, "Siper", "Shield")),
        (0.68, "glove", _say(lang, "Eldiven", "Gloves")),
    )
    for x, kind, word in slots:
        box = _fr(frame, x, 0.16, 0.26, 0.62)
        painter.setPen(QPen(PETROL, 3))
        if kind == "goggles":
            painter.setBrush(QColor("#D7EEF2"))
            painter.drawEllipse(QRectF(box.left(), box.top() + 16, box.width() * 0.46, box.height() * 0.28))
            painter.drawEllipse(QRectF(box.left() + box.width() * 0.42, box.top() + 16, box.width() * 0.46, box.height() * 0.28))
        elif kind == "shield":
            painter.setBrush(QColor("#E7F4EA"))
            painter.drawRoundedRect(QRectF(box.left() + 8, box.top(), box.width() * 0.7, box.height() * 0.55), 14, 14)
            painter.drawLine(QPointF(box.left() + 14, box.top() + 16), QPointF(box.left() + box.width() * 0.62, box.top() + 16))
        else:
            painter.setBrush(QColor("#D7E4F2"))
            painter.drawRoundedRect(QRectF(box.left() + 10, box.top() + 28, box.width() * 0.55, box.height() * 0.40), 8, 8)
            for index in range(4):
                painter.drawRoundedRect(QRectF(box.left() + 10 + index * (box.width() * 0.14), box.top() + 6, box.width() * 0.12, 26), 3, 3)
        _note(painter, box, word)


def _acid_order(painter: QPainter, frame: QRectF, progress: float, lang: str) -> None:
    beaker = _fr(frame, 0.16, 0.34, 0.34, 0.46)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(beaker, 8, 8)
    liquid_h = beaker.height() * (0.35 + 0.25 * min(1.0, progress))
    liquid = QRectF(beaker.left() + 6, beaker.bottom() - liquid_h - 6, beaker.width() - 12, liquid_h)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WATER)
    painter.drawRoundedRect(liquid, 4, 4)
    painter.setPen(INK)
    _font(painter, 13)
    painter.drawText(liquid, Qt.AlignmentFlag.AlignCenter, _say(lang, "Su", "Water"))
    bottle = _fr(frame, 0.62, 0.16, 0.18, 0.30)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(bottle, 8, 8)
    painter.drawRoundedRect(QRectF(bottle.center().x() - 8, bottle.top() - 12, 16, 14), 3, 3)
    _note(painter, bottle, _say(lang, "Asit", "Acid"))
    if progress > 0.45:
        painter.setBrush(ACID)
        painter.setPen(Qt.PenStyle.NoPen)
        drop_y = frame.top() + frame.height() * (0.48 + 0.12 * progress)
        painter.drawEllipse(QRectF(beaker.center().x(), drop_y, 12, 16))


def _shaker(painter: QPainter, frame: QRectF, progress: float, lang: str) -> None:
    shake = 8 * math.sin(progress * math.tau * 3)
    deck = _fr(frame, 0.08, 0.32, 0.40, 0.28)
    deck.translate(shake, 0)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#E7F0F2"))
    painter.drawRoundedRect(deck, 10, 10)
    painter.setPen(QPen(PETROL, 1))
    for line in range(5):
        x = deck.left() + 10 + line * (deck.width() / 6)
        painter.drawLine(QPointF(x, deck.top() + 8), QPointF(x, deck.bottom() - 8))
    scoop = _fr(frame, 0.58, 0.34, 0.28, 0.30)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#F2D7B5"))
    painter.drawEllipse(QRectF(scoop.left(), scoop.top() + 8, scoop.width() * 0.55, scoop.height() * 0.45))
    painter.drawLine(QPointF(scoop.center().x(), scoop.center().y()), QPointF(scoop.right() - 4, scoop.bottom() - 4))
    _note(painter, deck.adjusted(0, 0, 0, 22), _say(lang, "Sarsıntı", "Shaker"))
    _note(painter, scoop.adjusted(0, 0, 0, 18), _say(lang, "Kürek", "Scoop"))


def _dry(painter: QPainter, frame: QRectF, lang: str) -> None:
    tray = _fr(frame, 0.08, 0.46, 0.40, 0.18)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#E7EEF0"))
    painter.drawRoundedRect(tray, 8, 8)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#C4B49A"))
    for index in range(5):
        painter.drawEllipse(QRectF(tray.left() + 12 + index * 18, tray.center().y() - 4, 10, 8))
    oven = _fr(frame, 0.58, 0.22, 0.28, 0.50)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(oven, 8, 8)
    window = QRectF(oven.left() + 10, oven.top() + 12, oven.width() - 28, oven.height() * 0.45)
    painter.setBrush(QColor("#D5E7EA"))
    painter.drawRoundedRect(window, 4, 4)
    painter.drawLine(QPointF(oven.right() - 10, oven.center().y() - 8), QPointF(oven.right() - 10, oven.center().y() + 10))
    _note(painter, tray.adjusted(0, 0, 0, 22), _say(lang, "Tepsi", "Tray"))
    _note(painter, oven.adjusted(0, 0, 0, 20), _say(lang, "Fırın", "Oven"))


def _bag(painter: QPainter, frame: QRectF, lang: str) -> None:
    bag = _fr(frame, 0.14, 0.24, 0.30, 0.48)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#F4E7C8"))
    painter.drawRoundedRect(QRectF(bag.left(), bag.top() + 16, bag.width(), bag.height() - 16), 12, 12)
    painter.drawLine(QPointF(bag.left() + 8, bag.top() + 16), QPointF(bag.center().x(), bag.top()))
    painter.drawLine(QPointF(bag.right() - 8, bag.top() + 16), QPointF(bag.center().x(), bag.top()))
    tag = _fr(frame, 0.56, 0.32, 0.26, 0.28)
    painter.setBrush(QColor("#F3E2A5"))
    painter.drawRoundedRect(tag, 6, 6)
    painter.setPen(QPen(PETROL, 2))
    painter.drawLine(QPointF(tag.left() + 8, tag.center().y()), QPointF(tag.right() - 8, tag.center().y()))
    _note(painter, bag.adjusted(0, 0, 0, 22), _say(lang, "Torba", "Bag"))
    _note(painter, tag.adjusted(0, 0, 0, 20), _say(lang, "Etiket", "Label"))


def _grain_light(painter: QPainter, frame: QRectF, lang: str) -> None:
    grain = _fr(frame, 0.16, 0.40, 0.28, 0.28)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#C4B49A"))
    painter.drawPolygon(QPolygonF([
        QPointF(grain.left() + 8, grain.bottom() - 4),
        QPointF(grain.left() + grain.width() * 0.2, grain.top() + 10),
        QPointF(grain.center().x(), grain.top()),
        QPointF(grain.right() - 4, grain.center().y()),
        QPointF(grain.right() - 12, grain.bottom()),
    ]))
    lamp = _fr(frame, 0.58, 0.18, 0.22, 0.16)
    painter.setBrush(QColor("#F6E3A1"))
    painter.drawEllipse(lamp)
    painter.setPen(QPen(QColor("#E1C15A"), 2))
    for index in range(3):
        painter.drawLine(QPointF(lamp.center().x(), lamp.bottom()), QPointF(grain.center().x() - 10 + index * 10, grain.top()))
    _note(painter, grain.adjusted(0, 0, 0, 22), _say(lang, "Islak tane", "Wet grain"))
    _note(painter, lamp.adjusted(0, 0, 0, 20), _say(lang, "Işık", "Light"))


def _sheet(painter: QPainter, frame: QRectF, lang: str) -> None:
    paper = _fr(frame, 0.10, 0.16, 0.80, 0.68)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#F7F4EA"))
    painter.drawRoundedRect(paper, 6, 6)
    painter.setPen(QPen(PETROL, 2))
    for step in (1, 2):
        x = paper.left() + paper.width() * step / 3
        painter.drawLine(QPointF(x, paper.top() + 8), QPointF(x, paper.bottom() - 8))
    words = (
        _say(lang, "Erken", "Early"),
        _say(lang, "Geç", "Late"),
        _say(lang, "Artık", "Residue"),
    )
    for index, word in enumerate(words):
        cell = QRectF(paper.left() + paper.width() * index / 3, paper.top(), paper.width() / 3, 28)
        painter.setPen(INK)
        _font(painter, 12)
        painter.drawText(cell, Qt.AlignmentFlag.AlignCenter, word)


def _specimen(painter: QPainter, rect: QRectF, kind: str) -> None:
    painter.setPen(QPen(PETROL, 2))
    if kind == "calcite":
        painter.setBrush(QColor("#E7EEF2"))
        painter.drawPolygon(QPolygonF([
            QPointF(rect.center().x(), rect.top()),
            QPointF(rect.right(), rect.center().y() - 6),
            QPointF(rect.center().x(), rect.bottom()),
            QPointF(rect.left(), rect.center().y() + 8),
        ]))
    elif kind == "dolomite":
        painter.setBrush(QColor("#D5DDD4"))
        painter.drawRoundedRect(rect.adjusted(4, 8, -4, -4), 4, 4)
    elif kind == "gypsum":
        painter.setBrush(QColor("#F4F0E4"))
        painter.drawRoundedRect(QRectF(rect.left(), rect.center().y(), rect.width(), rect.height() * 0.28), 3, 3)
    else:
        painter.setBrush(QColor("#D9D3C8"))
        painter.drawRoundedRect(rect.adjusted(6, 4, -6, -8), 3, 3)


def _minerals(painter: QPainter, frame: QRectF, progress: float, lang: str) -> None:
    kinds = (
        (0.06, 0.20, "calcite", _say(lang, "Kalsit", "Calcite")),
        (0.30, 0.20, "dolomite", _say(lang, "Dolomit", "Dolomite")),
        (0.54, 0.18, "gypsum", _say(lang, "Jips", "Gypsum")),
        (0.76, 0.18, "anhydrite", _say(lang, "Anhidrit", "Anhydrite")),
    )
    for x, w, kind, word in kinds:
        box = _fr(frame, x, 0.22, w, 0.46)
        _specimen(painter, QRectF(box.left(), box.top(), box.width(), box.height() * 0.7), kind)
        _note(painter, box, word)
    if progress > 0.4:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ACID)
        painter.drawEllipse(QRectF(frame.left() + frame.width() * 0.12, frame.top() + frame.height() * 0.30, 12, 12))
        painter.drawEllipse(QRectF(frame.left() + frame.width() * 0.36, frame.top() + frame.height() * 0.34, 8, 8))


def _calculator(painter: QPainter, frame: QRectF) -> None:
    body = _fr(frame, 0.28, 0.12, 0.44, 0.76)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(body, 10, 10)
    screen = QRectF(body.left() + 12, body.top() + 12, body.width() - 24, body.height() * 0.22)
    painter.setBrush(PALE)
    painter.drawRoundedRect(screen, 4, 4)
    painter.setBrush(QColor("#E5F0F1"))
    for row in range(3):
        for col in range(3):
            key = QRectF(body.left() + 14 + col * (body.width() * 0.28), body.top() + body.height() * 0.40 + row * (body.height() * 0.16), body.width() * 0.18, body.height() * 0.10)
            painter.drawRoundedRect(key, 3, 3)


def _clipboard(painter: QPainter, frame: QRectF) -> None:
    board = _fr(frame, 0.30, 0.12, 0.40, 0.74)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#F7F4EA"))
    painter.drawRoundedRect(board, 8, 8)
    painter.setBrush(PETROL)
    painter.drawRoundedRect(QRectF(board.center().x() - 16, board.top() - 6, 32, 14), 4, 4)
    painter.setPen(QPen(PALE, 3))
    for step in range(1, 5):
        y = board.top() + board.height() * step / 5
        painter.drawLine(QPointF(board.left() + 12, y), QPointF(board.right() - 12, y))


def _phenol(painter: QPainter, frame: QRectF, lang: str) -> None:
    beaker = _fr(frame, 0.34, 0.22, 0.32, 0.52)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(beaker, 8, 8)
    liquid = QRectF(beaker.left() + 6, beaker.center().y(), beaker.width() - 12, beaker.height() * 0.40)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#F4C2D4"))
    painter.drawRoundedRect(liquid, 4, 4)
    _note(painter, beaker.adjusted(0, 0, 0, 22), _say(lang, "Belirteç", "Indicator"))


def _stain(painter: QPainter, frame: QRectF, lang: str) -> None:
    left = _fr(frame, 0.16, 0.28, 0.24, 0.36)
    right = _fr(frame, 0.56, 0.28, 0.24, 0.36)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#E7A0A8"))
    painter.drawEllipse(left)
    painter.setBrush(QColor("#E4E7EA"))
    painter.drawEllipse(right)
    _note(painter, left.adjusted(0, 0, 0, 24), _say(lang, "Boyalı tane", "Stained grain"))
    _note(painter, right.adjusted(0, 0, 0, 24), _say(lang, "Soluk tane", "Pale grain"))


def _bubbles(painter: QPainter, frame: QRectF, lang: str) -> None:
    dish = _fr(frame, 0.22, 0.42, 0.56, 0.22)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(dish, 12, 12)
    painter.setBrush(QColor("#C4B49A"))
    painter.drawEllipse(QRectF(dish.left() + 16, dish.center().y() - 8, 18, 14))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(ACID)
    painter.drawEllipse(QRectF(dish.center().x(), dish.top() - 16, 12, 12))
    painter.drawEllipse(QRectF(dish.center().x() + 18, dish.top() - 28, 16, 16))
    _note(painter, dish.adjusted(0, 0, 0, 24), _say(lang, "Kabarcık", "Bubble"))


def _evaporite_pair(painter: QPainter, frame: QRectF, lang: str) -> None:
    left = _fr(frame, 0.12, 0.28, 0.30, 0.40)
    right = _fr(frame, 0.56, 0.24, 0.28, 0.46)
    _specimen(painter, left, "gypsum")
    _specimen(painter, right, "anhydrite")
    _note(painter, left.adjusted(0, 0, 0, 24), _say(lang, "Jips", "Gypsum"))
    _note(painter, right.adjusted(0, 0, 0, 22), _say(lang, "Anhidrit", "Anhydrite"))


def _precip(painter: QPainter, frame: QRectF, lang: str) -> None:
    dish = _fr(frame, 0.24, 0.30, 0.52, 0.36)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawEllipse(dish)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#F7F7F7"))
    painter.drawEllipse(QRectF(dish.center().x() - 28, dish.center().y() - 10, 56, 24))
    _note(painter, dish.adjusted(0, 0, 0, 20), _say(lang, "Çökelek", "Precipitate"))


def _coal_pair(painter: QPainter, frame: QRectF, lang: str) -> None:
    chunk = _fr(frame, 0.12, 0.30, 0.28, 0.36)
    bed = _fr(frame, 0.54, 0.28, 0.32, 0.40)
    painter.setPen(QPen(PETROL, 2))
    painter.setBrush(QColor("#2C3334"))
    painter.drawRoundedRect(chunk, 8, 8)
    painter.setBrush(QColor("#4A5550"))
    painter.drawRoundedRect(bed, 4, 4)
    painter.setPen(QPen(QColor("#C5C2B8"), 2))
    for index in range(4):
        y = bed.top() + 8 + index * (bed.height() / 5)
        painter.drawLine(QPointF(bed.left() + 6, y), QPointF(bed.right() - 6, y))
    _note(painter, chunk.adjusted(0, 0, 0, 22), _say(lang, "Kömür", "Coal"))
    _note(painter, bed.adjusted(0, 0, 0, 22), _say(lang, "Şeyl", "Shale"))


def _calcite(painter: QPainter, frame: QRectF, lang: str) -> None:
    rock = _fr(frame, 0.32, 0.22, 0.36, 0.46)
    _specimen(painter, rock, "calcite")
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(ACID)
    painter.drawEllipse(QRectF(rock.right() - 8, rock.top() - 10, 14, 14))
    _note(painter, rock.adjusted(0, 0, 0, 28), _say(lang, "Kalsit şematik", "Calcite schematic"))


def _quartz(painter: QPainter, frame: QRectF, lang: str) -> None:
    rock = _fr(frame, 0.36, 0.18, 0.28, 0.55)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(QColor("#F4FBFC"))
    painter.drawPolygon(QPolygonF([
        QPointF(rock.center().x(), rock.top()),
        QPointF(rock.right(), rock.top() + rock.height() * 0.35),
        QPointF(rock.right() - 8, rock.bottom()),
        QPointF(rock.left() + 8, rock.bottom()),
        QPointF(rock.left(), rock.top() + rock.height() * 0.35),
    ]))
    _note(painter, rock.adjusted(0, 0, 0, 22), _say(lang, "Kuvars şematik", "Quartz schematic"))


def _sand(painter: QPainter, frame: QRectF, lang: str) -> None:
    bed = _fr(frame, 0.16, 0.34, 0.68, 0.32)
    painter.setPen(QPen(PETROL, 2))
    painter.setBrush(QColor("#E6D3A8"))
    painter.drawRoundedRect(bed, 8, 8)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#C4B49A"))
    for index in range(8):
        painter.drawEllipse(QRectF(bed.left() + 10 + (index % 8) * (bed.width() / 9), bed.center().y() - 6, 12, 10))
    _note(painter, bed.adjusted(0, 0, 0, 24), _say(lang, "Kumtaşı şematik", "Sandstone schematic"))


def _shale(painter: QPainter, frame: QRectF, lang: str) -> None:
    slab = _fr(frame, 0.18, 0.28, 0.64, 0.40)
    painter.setPen(QPen(PETROL, 2))
    painter.setBrush(QColor("#8E948C"))
    painter.drawRoundedRect(slab, 4, 4)
    painter.setPen(QPen(QColor("#F4F7F4"), 2))
    for index in range(5):
        y = slab.top() + 8 + index * (slab.height() / 6)
        painter.drawLine(QPointF(slab.left() + 8, y), QPointF(slab.right() - 8, y))
    _note(painter, slab.adjusted(0, 0, 0, 22), _say(lang, "Şeyl şematik", "Shale schematic"))


def _odor(painter: QPainter, frame: QRectF, lang: str) -> None:
    dish = _fr(frame, 0.22, 0.40, 0.40, 0.24)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(GLASS)
    painter.drawRoundedRect(dish, 12, 12)
    painter.setPen(QPen(PETROL, 2))
    for index in range(3):
        start = QPointF(dish.right() + 8, dish.top() + 8 + index * 14)
        painter.drawArc(QRectF(start.x(), start.y(), 28, 12), 0, 180 * 16)
    _note(painter, dish.adjusted(0, 0, 0, 24), _say(lang, "Koku", "Odor"))


def _trouble(painter: QPainter, frame: QRectF, lang: str) -> None:
    beaker = _fr(frame, 0.08, 0.28, 0.22, 0.40)
    painter.setPen(QPen(PETROL, 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(beaker, 6, 6)
    lamp = _fr(frame, 0.40, 0.24, 0.20, 0.16)
    painter.setBrush(QColor("#24383C"))
    painter.drawRoundedRect(lamp, 4, 4)
    dish = _fr(frame, 0.68, 0.40, 0.22, 0.16)
    painter.setBrush(GLASS)
    painter.drawRoundedRect(dish, 8, 8)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(ACID)
    painter.drawEllipse(QRectF(dish.center().x() - 6, dish.top() - 14, 12, 12))
    _note(painter, frame.adjusted(0, 0, 0, -4), _say(lang, "Tek başına ad koymaz", "Not a name by itself"))


def _extra(painter: QPainter, frame: QRectF, visual: str, progress: float, lang: str) -> None:
    if visual == "auto_cup":
        _auto_cup(painter, frame, lang)
    elif visual == "auto_cell":
        _auto_cell(painter, frame, lang)
    elif visual == "auto_sensor":
        _auto_sensor(painter, frame, lang)
    elif visual == "water_three":
        _water_three(painter, frame, lang)
    elif visual == "water_flow":
        _water_flow(painter, frame, progress, lang)
    elif visual == "acid_ppe":
        _acid_ppe(painter, frame, lang)
    elif visual == "acid_order":
        _acid_order(painter, frame, progress, lang)
    elif visual == "collect_shaker":
        _shaker(painter, frame, progress, lang)
    elif visual == "dry_tray":
        _dry(painter, frame, lang)
    elif visual == "label_bag":
        _bag(painter, frame, lang)
    elif visual == "look_grain":
        _grain_light(painter, frame, lang)
    elif visual == "sheet_cols":
        _sheet(painter, frame, lang)
    elif visual == "mineral_four":
        _minerals(painter, frame, progress, lang)
    elif visual == "calc_keys":
        _calculator(painter, frame)
    elif visual == "clipboard":
        _clipboard(painter, frame)
    elif visual == "phenol_drop":
        _phenol(painter, frame, lang)
    elif visual == "stain_pair":
        _stain(painter, frame, lang)
    elif visual == "bubble_dish":
        _bubbles(painter, frame, lang)
    elif visual == "mineral_pair":
        _evaporite_pair(painter, frame, lang)
    elif visual == "precip_dish":
        _precip(painter, frame, lang)
    elif visual == "coal_pair":
        _coal_pair(painter, frame, lang)
    elif visual == "calcite_rhomb":
        _calcite(painter, frame, lang)
    elif visual == "quartz_grain":
        _quartz(painter, frame, lang)
    elif visual == "sand_grains":
        _sand(painter, frame, lang)
    elif visual == "shale_layers":
        _shale(painter, frame, lang)
    elif visual == "odor_dish":
        _odor(painter, frame, lang)
    elif visual == "trouble_three":
        _trouble(painter, frame, lang)
    else:
        _fallback_flask(painter, frame)


_DRAWN = {
    "studio_scene": "acid_into_water",
    "calc_scene": "calc_keys",
    "devices_scene": "bernard_rig",
    "rocks_scene": "mineral_four",
    "ppe_scene": "acid_ppe",
    "inventory_scene": "clipboard",
    "inspection_scene": "clipboard",
    "auto_scene": "auto_cell",
    "water_scene": "water_three",
    "phenol_scene": "phenol_drop",
    "stain_scene": "stain_pair",
    "bubble_scene": "bubble_dish",
    "pair_scene": "mineral_pair",
    "uv_scene": "fluor_dish",
    "cut_scene": "fluor_cut",
    "acetone_scene": "fluor_cut",
    "chloride_scene": "precip_dish",
    "sulfate_scene": "precip_dish",
    "coal_pair_scene": "coal_pair",
    "calcite_scene": "calcite_rhomb",
    "quartz_scene": "quartz_grain",
    "sand_scene": "sand_grains",
    "shale_scene": "shale_layers",
    "carb_scene": "shale_layers",
    "odor_scene": "odor_dish",
    "trouble_scene": "trouble_three",
    "label_scene": "label_bag",
    "sheet_scene": "sheet_cols",
}


def paint_drawn(painter: QPainter, frame: QRectF, key: str, lang: str = "tr") -> None:
    paint_scene(painter, frame, _DRAWN.get(key, "fallback_flask"), 0.62, lang)
