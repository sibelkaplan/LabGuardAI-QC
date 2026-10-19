"""Visual PPE guide. It does not select equipment for a chemical."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget

from app.card_images import FitImage, caption as image_caption
from app.i18n import t
from app.media_view import MediaView

ITEMS = (
    ("goggles", "ppe_goggles"),
    ("shield", "ppe_shield"),
    ("glove", "ppe_glove"),
    ("coat", "ppe_coat"),
    ("boot", "ppe_boot"),
    ("respirator", "ppe_resp"),
    ("hood", "ppe_hood"),
    ("eyewash", "ppe_eye"),
    ("spill", "ppe_spill"),
)


class PpePage(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "tr"
        self._cards: list[tuple] = []
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setSpacing(12)
        self.intro = QLabel()
        self.intro.setObjectName("Warning")
        self.intro.setWordWrap(True)
        layout.addWidget(self.intro)
        for kind, prefix in ITEMS:
            layout.addWidget(self._item(kind, prefix))
        layout.addWidget(self._hardhat())
        layout.addStretch()
        scroll.setWidget(host)
        outer.addWidget(scroll)
        self.retranslate("tr")

    def _item(self, kind: str, prefix: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        row = QHBoxLayout(frame)
        row.setContentsMargins(16, 16, 16, 16)
        row.setSpacing(16)
        picture = MediaView(kind, image_height=200)
        row.addWidget(picture, 1)
        text = QVBoxLayout()
        title = QLabel()
        title.setObjectName("Heading")
        title.setStyleSheet("font-size:18px; font-weight:750; background:transparent;")
        title.setWordWrap(True)
        caption = QLabel()
        caption.setObjectName("Muted")
        caption.setWordWrap(True)
        what = QLabel()
        what.setWordWrap(True)
        when = QLabel()
        when.setWordWrap(True)
        care = QLabel()
        care.setWordWrap(True)
        for label in (title, caption, what, when, care):
            text.addWidget(label)
        row.addLayout(text, 1)
        self._cards.append((title, what, when, care, prefix, caption, picture))
        return frame

    def _hardhat(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        row = QHBoxLayout(frame)
        row.setContentsMargins(16, 16, 16, 16)
        row.setSpacing(16)
        self.hardhat_image = FitImage("hardhat", 200)
        row.addWidget(self.hardhat_image, 1)
        text = QVBoxLayout()
        self.hardhat_title = QLabel()
        self.hardhat_title.setObjectName("Heading")
        self.hardhat_title.setStyleSheet("font-size:18px; font-weight:750; background:transparent;")
        self.hardhat_title.setWordWrap(True)
        self.hardhat_caption = QLabel()
        self.hardhat_caption.setObjectName("Muted")
        self.hardhat_caption.setWordWrap(True)
        self.hardhat_what = QLabel()
        self.hardhat_what.setWordWrap(True)
        self.hardhat_when = QLabel()
        self.hardhat_when.setWordWrap(True)
        self.hardhat_care = QLabel()
        self.hardhat_care.setWordWrap(True)
        for label in (
            self.hardhat_title,
            self.hardhat_caption,
            self.hardhat_what,
            self.hardhat_when,
            self.hardhat_care,
        ):
            text.addWidget(label)
        row.addLayout(text, 1)
        return frame

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.intro.setText(t("ppe_intro", lang))
        for title, what, when, care, prefix, caption, picture in self._cards:
            title.setText(t(f"{prefix}_title", lang))
            picture.retranslate(lang)
            caption.setVisible(False)
            what.setText(f"{t('ppe_what', lang)} {t(f'{prefix}_what', lang)}")
            when.setText(f"{t('ppe_when', lang)} {t(f'{prefix}_when', lang)}")
            care.setText(f"{t('ppe_care', lang)} {t(f'{prefix}_care', lang)}")
        self.hardhat_image.set_lang(lang)
        self.hardhat_title.setText(t("ppe_hardhat_title", lang))
        self.hardhat_caption.setText(image_caption("hardhat", lang))
        self.hardhat_what.setText(f"{t('ppe_what', lang)} {t('ppe_hardhat_what', lang)}")
        self.hardhat_when.setText(f"{t('ppe_when', lang)} {t('ppe_hardhat_when', lang)}")
        self.hardhat_care.setText(f"{t('ppe_care', lang)} {t('ppe_hardhat_care', lang)}")
