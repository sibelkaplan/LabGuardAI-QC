"""Sidebar mark: a shield and a laboratory flask. Drawn locally."""

from __future__ import annotations

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget


class LogoMark(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LogoMark")
        self.setFixedSize(42, 42)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRoundedRect(QRectF(1, 1, 40, 40), 9, 9)
        petrol = QColor("#0B5964")
        painter.setPen(QPen(petrol, 1))
        painter.setBrush(petrol)
        shield = QPolygonF(
            [
                QPointF(8, 6),
                QPointF(34, 6),
                QPointF(34, 20),
                QPointF(21, 36),
                QPointF(8, 20),
            ]
        )
        painter.drawPolygon(shield)
        painter.setPen(QPen(QColor("#FFFFFF"), 1.4))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRoundedRect(QRectF(18, 11, 6, 5), 1, 1)
        painter.drawPolygon(
            QPolygonF(
                [
                    QPointF(19, 16),
                    QPointF(23, 16),
                    QPointF(30, 31),
                    QPointF(12, 31),
                ]
            )
        )
        painter.drawLine(16, 26, 26, 26)
        painter.end()
