"""Run LabGuard AI.

The README command is `python app/main.py`. That puts the app folder on
sys.path, so the project root is added before the package imports.
"""

from __future__ import annotations

import os
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication

from app.main_window import LabGuard


def main() -> int:
    # A desktop window should survive the launching terminal closing.
    # SIGHUP is what that terminal sends; without this, the process exits
    # with no Python traceback.
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("LabGuard AI")
    window = LabGuard()
    window.show()
    window.raise_()
    window.activateWindow()
    if os.environ.get("LABGUARD_EXIT_AFTER_SHOW") == "1":
        window.close()
        return 0
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
