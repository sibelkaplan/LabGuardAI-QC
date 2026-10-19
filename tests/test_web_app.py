"""Web edition stays off the desktop database and off PySide."""

from __future__ import annotations

import ast
from pathlib import Path

from streamlit_app import DESKTOP_DB_MARK, open_session, prepare_lines, session_db_path

ROOT = Path(__file__).resolve().parents[1]


def test_web_entry_does_not_import_pyside():
    tree = ast.parse((ROOT / "streamlit_app.py").read_text(encoding="utf-8"))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    assert not any("PySide" in name or name.startswith("app.hub") or name.startswith("app.ppe_page") for name in modules)


def test_session_database_is_not_the_desktop_file(tmp_path):
    path = session_db_path(tmp_path)
    assert DESKTOP_DB_MARK not in str(path)
    connection = open_session(tmp_path)
    try:
        assert connection.execute("SELECT COUNT(*) FROM chemicals").fetchone()[0] == 0
    finally:
        connection.close()
    assert path.is_file()


def test_desktop_path_is_refused(tmp_path):
    blocked = tmp_path / "Library" / "Application Support" / "LabGuardAI"
    try:
        session_db_path(blocked)
    except RuntimeError as exc:
        assert "desktop" in str(exc).lower()
    else:
        resolved = (blocked / "web-session.db").resolve()
        if DESKTOP_DB_MARK in str(resolved):
            raise AssertionError("desktop path was accepted")


def test_volume_ratio_stays_theoretical_and_ww_has_no_stock_volume():
    math_line, refusal = prepare_lines("HCl", 32, "percent_v_v", 18.5, 1000, "mL")
    assert "578.1" in math_line
    assert "onay" in math_line.casefold()
    assert "578" not in refusal
    ww_line, _ = prepare_lines("HCl", 32, "percent_w_w", 18.5, 1000, "mL")
    assert "578" not in ww_line
