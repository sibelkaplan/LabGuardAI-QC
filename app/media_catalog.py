"""Local picture catalog. Photographs stay in the project so the app can open offline."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREDITS = ROOT / "assets" / "credits.json"
VIDEO_FILE = ROOT / "assets" / "training" / "acid-safety.mp4"


@lru_cache(maxsize=1)
def catalog() -> dict:
    return json.loads(CREDITS.read_text(encoding="utf-8"))


def asset_for(asset_id: str) -> dict | None:
    item = catalog().get(asset_id)
    if item is None:
        return None
    record = dict(item)
    record["id"] = asset_id
    relative = item.get("file") or ""
    path = ROOT / "assets" / relative if relative else None
    record["path"] = path
    record["available"] = bool(path and path.is_file() and path.stat().st_size > 0)
    if item.get("kind") == "photo" and not record["available"]:
        record["kind"] = "illustration"
    return record


def training_video() -> Path | None:
    if VIDEO_FILE.is_file() and VIDEO_FILE.stat().st_size > 0:
        return VIDEO_FILE
    return None
