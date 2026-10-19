"""Large local photograph or a labelled illustration. A click opens a larger view."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QFrame, QLabel, QVBoxLayout

from app.i18n import t
from app.illustrations import Sketch
from app.media_catalog import asset_for


class MediaView(QFrame):
    def __init__(self, asset_id: str, formula: str = "", image_height: int = 240):
        super().__init__()
        self.asset_id = asset_id
        self.formula = formula
        self.lang = "tr"
        self.image_height = image_height
        self.loaded = "illustration"
        self._pixmap = QPixmap()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setMinimumHeight(image_height)
        self.image.setObjectName("MediaWell")
        self.image.setStyleSheet("border-radius:12px;")
        self.sketch = Sketch("flask", formula, large=True)
        self.sketch.setVisible(False)
        self.caption = QLabel()
        self.caption.setObjectName("Muted")
        self.caption.setWordWrap(True)
        self.hint = QLabel()
        self.hint.setObjectName("Muted")
        self.hint.setWordWrap(True)
        layout.addWidget(self.image)
        layout.addWidget(self.sketch)
        layout.addWidget(self.caption)
        layout.addWidget(self.hint)
        self.reload()

    def reload(self) -> None:
        record = asset_for(self.asset_id)
        sketch_kind = "flask"
        if record is not None:
            sketch_kind = record.get("sketch") or "flask"
        self.sketch.kind = sketch_kind
        self.sketch.formula = self.formula
        self.sketch.setMinimumSize(220, self.image_height)
        self.sketch.setMaximumHeight(self.image_height + 20)
        self._pixmap = QPixmap()
        if record is not None and record["kind"] == "photo" and record["available"]:
            pixmap = QPixmap(str(record["path"]))
            if not pixmap.isNull():
                self._pixmap = pixmap
                self.loaded = "photo"
                self.image.setVisible(True)
                self.sketch.setVisible(False)
                self._fit()
                self._apply_caption(record)
                return
        self.loaded = "illustration"
        self.image.setVisible(False)
        self.sketch.setVisible(True)
        self.sketch.update()
        self._apply_caption(record)

    def _apply_caption(self, record: dict | None) -> None:
        if record is None:
            self.caption.setText(t("library_illustration", self.lang))
        else:
            key = "caption_en" if self.lang == "en" else "caption_tr"
            self.caption.setText(record.get(key) or t("library_illustration", self.lang))
        self.hint.setText(t("media_enlarge", self.lang))

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.reload()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._fit()

    def _fit(self) -> None:
        if self._pixmap.isNull():
            return
        scaled = self._pixmap.scaled(
            max(self.image.width(), 280),
            self.image_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image.setPixmap(scaled)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.enlarge()
        super().mouseReleaseEvent(event)

    def enlarge(self) -> QDialog:
        dialog = QDialog(self.window())
        dialog.setWindowTitle("LabGuard AI")
        dialog.resize(920, 760)
        layout = QVBoxLayout(dialog)
        picture = QLabel()
        picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if not self._pixmap.isNull():
            picture.setPixmap(
                self._pixmap.scaled(
                    880,
                    620,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            big = Sketch(self.sketch.kind, self.formula, large=True)
            big.setMinimumSize(720, 460)
            picture = big
        note = QLabel(self.caption.text())
        note.setWordWrap(True)
        layout.addWidget(picture, 1)
        layout.addWidget(note)
        dialog.show()
        return dialog
