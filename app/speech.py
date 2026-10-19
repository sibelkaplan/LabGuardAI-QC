"""Local speech. A missing voice must not close the application."""

from __future__ import annotations

import shutil
import subprocess
import sys

from PySide6.QtCore import QLocale, QObject, QProcess


class Narrator(QObject):
    def __init__(self):
        super().__init__()
        self.engine = None
        self.available = False
        self.turkish = False
        self.voice = ""
        self.status = "speech_unavailable"
        self._process: QProcess | None = None
        self._paused = False
        self._last_text = ""
        self._try_qt()
        if not self.available:
            self._try_macos_say()
        if not self.available:
            self.status = "speech_unavailable"

    def speak(self, text: str) -> str:
        spoken = " ".join(str(text or "").split())
        if not spoken:
            self.status = "speech_empty"
            return self.status
        if not self.available:
            self.status = "speech_unavailable"
            return self.status
        self._last_text = spoken
        try:
            if self.engine is not None:
                return self._speak_qt(spoken)
            return self._speak_say(spoken)
        except Exception:
            self.available = False
            self.status = "speech_unavailable"
            return self.status

    def stop(self) -> None:
        self._paused = False
        if self.engine is not None:
            try:
                self.engine.stop()
            except Exception:
                self.available = False
                self.status = "speech_unavailable"
        if self._process is not None:
            self._process.kill()
            self._process = None

    def _try_qt(self) -> None:
        try:
            from PySide6.QtTextToSpeech import QTextToSpeech

            engine = QTextToSpeech(self)
            if engine.errorReason() != QTextToSpeech.ErrorReason.NoError:
                return
            turkish = QLocale(QLocale.Language.Turkish)
            if any(item.language() == QLocale.Language.Turkish for item in engine.availableLocales()):
                engine.setLocale(turkish)
                self.turkish = True
            self.engine = engine
            self.available = True
            self.status = "speech_ready" if self.turkish else "speech_fallback"
        except Exception:
            self.engine = None

    def _try_macos_say(self) -> None:
        if sys.platform != "darwin" or shutil.which("say") is None:
            return
        try:
            completed = subprocess.run(
                ["say", "-v", "?"],
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
        except Exception:
            return
        listing = completed.stdout or ""
        for line in listing.splitlines():
            if "tr_TR" in line:
                self.voice = line.split()[0]
                self.available = True
                self.turkish = True
                self.status = "speech_ready"
                return

    def _speak_qt(self, spoken: str) -> str:
        from PySide6.QtTextToSpeech import QTextToSpeech

        state = self.engine.state()
        if state == QTextToSpeech.State.Speaking:
            self.engine.pause()
            self.status = "speech_paused"
            return self.status
        if state == QTextToSpeech.State.Paused:
            self.engine.resume()
            self.status = "speech_ready" if self.turkish else "speech_fallback"
            return self.status
        self.engine.say(spoken)
        self.status = "speech_ready" if self.turkish else "speech_fallback"
        return self.status

    def _speak_say(self, spoken: str) -> str:
        if self._process is not None and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
            self._process = None
            self._paused = True
            self.status = "speech_paused"
            return self.status
        if self._paused:
            self._paused = False
        process = QProcess(self)
        process.start("say", ["-v", self.voice, spoken])
        if not process.waitForStarted(1000):
            self.status = "speech_unavailable"
            return self.status
        self._process = process
        self.status = "speech_ready"
        return self.status
