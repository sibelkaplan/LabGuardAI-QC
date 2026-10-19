"""Simple labelled drawings. They are illustrations, not photographs."""

from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

PETROL = QColor("#0B5964")
PALE = QColor("#E5F0F1")
INK = QColor("#18353A")


class Sketch(QWidget):
    def __init__(self, kind: str, formula: str = "", large: bool = False):
        super().__init__()
        self.kind = kind
        self.formula = formula
        if large:
            self.setMinimumSize(420, 260)
        else:
            self.setMinimumSize(200, 150)
            self.setMaximumHeight(170)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#FFFFFF"))
        pen = QPen(PETROL, 3)
        painter.setPen(pen)
        painter.setBrush(PALE)
        box = QRectF(8, 8, self.width() - 16, self.height() - 16)
        painter.drawRoundedRect(box, 16, 16)
        painter.setPen(QPen(INK, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        drawer = {
            "flask": self._flask,
            "goggles": self._goggles,
            "shield": self._shield,
            "glove": self._glove,
            "coat": self._coat,
            "boot": self._boot,
            "respirator": self._respirator,
            "hood": self._hood,
            "eyewash": self._eyewash,
            "spill": self._spill,
        }.get(self.kind, self._flask)
        drawer(painter)
        painter.end()

    def _flask(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawRoundedRect(QRectF(70, 28, 40, 18), 4, 4)
        painter.drawPolygon(
            [
                self._p(78, 46),
                self._p(102, 46),
                self._p(124, 108),
                self._p(56, 108),
            ]
        )
        painter.setPen(PETROL)
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        painter.setFont(font)
        painter.drawText(QRectF(20, 78, 140, 28), Qt.AlignmentFlag.AlignCenter, self.formula or "?")

    def _goggles(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawEllipse(QRectF(38, 42, 46, 36))
        painter.drawEllipse(QRectF(96, 42, 46, 36))
        painter.drawArc(QRectF(78, 48, 24, 20), 20 * 16, 140 * 16)

    def _shield(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawRoundedRect(QRectF(58, 28, 64, 78), 18, 18)
        painter.drawLine(90, 28, 90, 18)
        painter.drawLine(74, 18, 106, 18)

    def _glove(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawRoundedRect(QRectF(62, 58, 52, 52), 16, 16)
        painter.drawRoundedRect(QRectF(70, 28, 14, 40), 6, 6)
        painter.drawRoundedRect(QRectF(88, 34, 12, 34), 6, 6)
        painter.drawRoundedRect(QRectF(104, 40, 12, 30), 6, 6)

    def _coat(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawPolygon(
            [
                self._p(90, 26),
                self._p(124, 48),
                self._p(112, 108),
                self._p(68, 108),
                self._p(56, 48),
            ]
        )
        painter.drawLine(90, 40, 90, 108)

    def _boot(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawRoundedRect(QRectF(68, 36, 36, 52), 8, 8)
        painter.drawRoundedRect(QRectF(68, 78, 58, 22), 8, 8)

    def _respirator(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawRoundedRect(QRectF(62, 48, 56, 40), 16, 16)
        painter.drawArc(QRectF(40, 50, 30, 28), 90 * 16, 180 * 16)
        painter.drawArc(QRectF(110, 50, 30, 28), -90 * 16, 180 * 16)

    def _hood(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawRect(QRectF(48, 36, 84, 64))
        painter.drawLine(48, 78, 132, 78)
        painter.setPen(QPen(PETROL, 2, Qt.PenStyle.DashLine))
        painter.drawLine(70, 50, 110, 50)

    def _spill(self, painter: QPainter) -> None:
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawRoundedRect(QRectF(48, 48, 84, 52), 8, 8)
        painter.drawLine(48, 70, 132, 70)
        painter.drawEllipse(QRectF(62, 78, 16, 16))
        painter.drawEllipse(QRectF(102, 78, 16, 16))
        painter.setPen(PETROL)
        painter.drawText(QRectF(48, 50, 84, 20), Qt.AlignmentFlag.AlignCenter, "KIT")

    def _eyewash(self, painter: QPainter) -> None:
        painter.setBrush(PETROL)
        painter.drawEllipse(QRectF(78, 24, 24, 24))
        painter.setBrush(QColor("#F4FBFC"))
        painter.drawRoundedRect(QRectF(46, 58, 40, 22), 8, 8)
        painter.drawRoundedRect(QRectF(94, 58, 40, 22), 8, 8)
        painter.drawLine(90, 48, 66, 58)
        painter.drawLine(90, 48, 114, 58)

    def _p(self, x: float, y: float):
        from PySide6.QtCore import QPointF

        return QPointF(x, y)
