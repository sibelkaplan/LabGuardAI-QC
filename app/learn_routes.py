"""Home search targets. A click opens a stored lesson or an existing screen."""

from __future__ import annotations

from app.academy_content import ALL_LESSONS, lesson_summary, lesson_title
from app.i18n import t
from app.library_data import STARTERS, record_name

_STOP = {"ve", "ile", "için", "icin", "the", "and", "bir"}
_VOWELS = set("aeıiuüoö")


def _matches(word: str, haystack: str) -> bool:
    tokens = haystack.split()
    if word in tokens:
        return True
    if len(word) < 5:
        return False
    stem = word[:-1] if word[-1] in _VOWELS else word
    return any(token.startswith(stem) for token in tokens)


def search_targets(query: str, lang: str = "tr") -> list[tuple[str, str, str]]:
    needle = " ".join(str(query or "").casefold().split())
    if len(needle) < 2:
        return []
    found: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    def add(kind: str, value: str, label: str) -> None:
        token = kind + ":" + value
        if token in seen:
            return
        seen.add(token)
        found.append((kind, value, label))

    if any(word in needle for word in ("seyrelt", "hazırla", "hazirla", "molarite", "w/w", "w/v")):
        add("page", "prepare", "Asit hazırlama" if lang != "en" else "Acid preparation")
    if any(
        word in needle
        for word in (
            "eldiven",
            "glove",
            "gözlük",
            "gozluk",
            "goggle",
            "siper",
            "shield",
            "maske",
            "respirator",
            "önlük",
            "onluk",
            "eyewash",
        )
    ):
        add("page", "ppe", "KKD ve eldiven" if lang != "en" else "PPE and gloves")
    if "kalsimetre" in needle and any(word in needle for word in ("neden", "hata", "vermiyor", "sonuç", "sonuc", "why")):
        add("lesson", "trouble-gas", "Kalsimetre neden sonuç vermeyebilir?")

    words = [word for word in needle.split() if word not in _STOP and len(word) > 2]
    ranked = []
    for lesson in ALL_LESSONS:
        haystack = " ".join(
            [lesson["title_tr"], lesson["title_en"], lesson["summary_tr"], lesson["summary_en"], lesson["id"]]
        ).casefold()
        if needle in haystack:
            ranked.append((len(words) + 2, lesson))
            continue
        hits = sum(1 for word in words if _matches(word, haystack))
        if hits:
            ranked.append((hits, lesson))
    ranked.sort(key=lambda item: item[0], reverse=True)
    kind_lesson = t("search_kind_lesson", lang)
    for _score, lesson in ranked:
        summary = lesson_summary(lesson, lang)
        short = summary if len(summary) <= 90 else summary[:87] + "…"
        label = f"{kind_lesson} · {lesson_title(lesson, lang)}\n{short}"
        source = lesson.get("source_en" if lang == "en" else "source_tr", "")
        if source:
            bit = " ".join(str(source).split())
            if len(bit) > 110:
                bit = bit[:107] + "…"
            label += "\n" + bit
        add("lesson", lesson["id"], label)
        if len(found) >= 6:
            break
    if len(found) < 6:
        kind_chemical = t("search_kind_chemical", lang)
        identity_key = "identity_en" if lang == "en" else "identity_tr"
        for record in STARTERS:
            haystack = " ".join(
                [record["name_tr"], record["name_en"], record["formula"], *record["aliases"]]
            ).casefold()
            hit = needle in haystack or any(_matches(word, haystack) for word in words)
            if not hit:
                continue
            add(
                "chemical",
                record["id"],
                f"{kind_chemical} · {record_name(record, lang)}\n{record[identity_key]}",
            )
            if len(found) >= 6:
                break
    return found[:6]
