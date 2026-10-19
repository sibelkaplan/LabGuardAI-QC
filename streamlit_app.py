"""Browser edition of LabGuard AI.

The desktop application remains ``python app/main.py``. This file does not
open the desktop SQLite database and does not call a remote model.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from app.academy_content import (
    CATEGORIES,
    filter_lessons,
    find_lesson,
    lesson_summary,
    lesson_text,
    lesson_title,
)
from app.calc.dilution import hazardous_product_dilution
from app.calc.mudlogging import hydrostatic_pressure
from app.calc.preparation import VOLUME_UNITS, review_preparation
from app.calc.units import CONCENTRATION_BASES
from app.constants import CHECK_KEYS, INCIDENT_KINDS, SEVERITIES
from app.database import (
    add_chemical,
    add_incident,
    add_inspection,
    connect,
    list_chemicals,
    list_incidents,
    list_inspection_rows,
)
from app.i18n import t
from app.learn_routes import search_targets
from app.library_data import STARTERS, general_field, record_identity, record_name
from app.local_tutor import answer
from app.validation import ValidationError

PPE_ITEMS = (
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

ROOT = Path(__file__).resolve().parent
PHOTOS = ROOT / "assets" / "photos"
IMAGES = ROOT / "assets" / "images"
DESKTOP_DB_MARK = "Application Support/LabGuardAI"

HOME_PHOTOS = (
    ("01_hero_laboratory.jpg", PHOTOS),
    ("02_acid_preparation.jpg", PHOTOS),
    ("03_rock_mineral_samples.jpg", PHOTOS),
    ("04_chemical_tests.jpg", PHOTOS),
    ("05_microscope_instruments.jpg", PHOTOS),
    ("06_safety_ppe.jpg", PHOTOS),
)


def session_db_path(folder: Path) -> Path:
    """A private file for this browser session. Never the desktop database."""
    path = (folder / "web-session.db").resolve()
    if DESKTOP_DB_MARK in str(path):
        raise RuntimeError("The web edition does not open the desktop database.")
    return path


def open_session(folder: Path):
    os.environ.pop("LABGUARD_DB", None)
    return connect(session_db_path(folder))


def photo(name: str) -> Path | None:
    for folder in (PHOTOS, IMAGES):
        path = folder / name
        if path.is_file():
            return path
    return None


def prepare_lines(name: str, c1: float, basis: str, c2: float, volume: float, unit: str) -> tuple[str, str]:
    """Theoretical ratio plus the standing refusal. Check boxes are not accepted."""
    review = review_preparation(
        name=name,
        c1=c1,
        basis=basis,
        c2=c2,
        volume=volume,
        volume_unit=unit,
        density=1.18,
        sds_basis_checked=True,
        sds_density_checked=True,
        procedure_checked=True,
    )
    if review.math_value is None:
        math_line = review.approval.detail
    else:
        math_line = (
            f"Kuramsal stok hacmi {review.math_value} {review.math_unit}. "
            "Bu sayı bir hazırlama onayı değildir."
        )
    blocked = hazardous_product_dilution(
        product_concentration=37,
        basis="percent_w_w",
        density=1.19,
        target_concentration=10,
        target_volume=1000,
        expert_approved=True,
        verified_product_data=True,
    )
    refusal = blocked.detail if blocked.value is None else "Hazardous dilution returned a quantity."
    return math_line, refusal


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="LabGuard AI", page_icon="🧪", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background: #FFFFFF; color: #18353A; }
        h1, h2, h3 { color: #102E33; }
        div[data-testid="stSidebar"] { background: #F7FAFA; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if "web_dir" not in st.session_state:
        st.session_state["web_dir"] = tempfile.mkdtemp(prefix="labguard-web-")
    lang = st.session_state.get("lang", "tr")
    connection = open_session(Path(st.session_state["web_dir"]))

    st.sidebar.markdown("**LabGuard AI**")
    st.sidebar.caption("Laboratory Safety Intelligence")
    st.sidebar.warning(t("demo_banner", lang))
    lang = st.sidebar.radio("Dil / Language", ("tr", "en"), index=0 if lang == "tr" else 1)
    st.session_state["lang"] = lang
    page = st.sidebar.radio(
        "Sayfa" if lang != "en" else "Page",
        (
            "Ana sayfa" if lang != "en" else "Home",
            "Akademi" if lang != "en" else "Academy",
            "Asit hazırlama" if lang != "en" else "Acid preparation",
            "Hesaplar" if lang != "en" else "Calculations",
            "Kütüphane" if lang != "en" else "Library",
            "KKD" if lang != "en" else "PPE",
            "Envanter" if lang != "en" else "Inventory",
            "Denetim" if lang != "en" else "Inspection",
            "Olay" if lang != "en" else "Incident",
            "Eğitmen" if lang != "en" else "Tutor",
        ),
    )

    hero = photo("01_hero_laboratory.jpg")
    if page.startswith("Ana") or page == "Home":
        _home(st, lang, hero)
    elif page.startswith("Akademi") or page == "Academy":
        _academy(st, lang)
    elif page.startswith("Asit") or page == "Acid preparation":
        _prepare(st, lang)
    elif page.startswith("Hesap") or page == "Calculations":
        _calc(st, lang)
    elif page.startswith("Kütüphane") or page == "Library":
        _library(st, lang)
    elif page in {"KKD", "PPE"}:
        _ppe(st, lang)
    elif page.startswith("Envanter") or page == "Inventory":
        _inventory(st, lang, connection)
    elif page.startswith("Denetim") or page == "Inspection":
        _inspection(st, lang, connection)
    elif page.startswith("Olay") or page == "Incident":
        _incident(st, lang, connection)
    else:
        _tutor(st, lang)
    connection.close()


def _home(st, lang: str, hero: Path | None) -> None:
    left, right = st.columns((3, 2))
    with left:
        st.caption("LABORATUVAR GÜVENLİĞİ" if lang != "en" else "LABORATORY SAFETY")
        st.title("LabGuard AI'ye Hoş Geldiniz" if lang != "en" else "Welcome to LabGuard AI")
        st.write("Görsel eğitim ve laboratuvar araçları." if lang != "en" else "Visual training and laboratory tools.")
        st.caption(t("demo_short", lang) if t("demo_short", lang) != "demo_short" else "DEMO — yerel kayıt")
    if hero is not None:
        with right:
            st.image(str(hero), use_container_width=True)
    query = st.text_input(
        "Ara" if lang != "en" else "Search",
        placeholder="asit hazırlama, jips, KKD" if lang != "en" else "acid preparation, gypsum, PPE",
    )
    for kind, value, label in search_targets(query, lang):
        st.write(f"{kind}: {label} ({value})")
    cards = (
        ("02_acid_preparation.jpg", "Asit hazırlama" if lang != "en" else "Acid preparation", "Görsel adımlar. Tarif değildir." if lang != "en" else "Visual steps. Not a recipe."),
        ("03_rock_mineral_samples.jpg", "Kayaç ve mineral" if lang != "en" else "Rocks and minerals", "Örnek fotoğrafı. Renk tanı değildir." if lang != "en" else "Specimen photo. Colour is not an identification."),
        ("04_chemical_tests.jpg", "Kimyasal testler" if lang != "en" else "Chemical tests", "Gözlem kartları. Tam yöntem değildir." if lang != "en" else "Observation cards. Not a complete method."),
        ("05_microscope_instruments.jpg", "Laboratuvar cihazları" if lang != "en" else "Laboratory instruments", "Mikroskop fotoğrafı. Model değildir." if lang != "en" else "Microscope photograph. Not a model."),
    )
    columns = st.columns(4)
    for column, (filename, title, body) in zip(columns, cards):
        path = photo(filename)
        with column:
            if path is not None:
                column.image(str(path), use_container_width=True)
            column.subheader(title)
            column.caption(body)


def _academy(st, lang: str) -> None:
    st.header("Mudlogging Akademisi" if lang != "en" else "Mudlogging Academy")
    st.caption("Şematik eğitim. Video değildir. Yöntem kopyalanmaz." if lang != "en" else "Schematic lessons. Not a video. Methods are not copied.")
    category = st.selectbox("Kategori" if lang != "en" else "Category", ("",) + CATEGORIES)
    query = st.text_input("Ders ara" if lang != "en" else "Find a lesson")
    lessons = filter_lessons(query, category)
    names = [lesson_title(lesson, lang) for lesson in lessons]
    if not names:
        st.info("Ders yok." if lang != "en" else "No lesson.")
        return
    chosen = st.selectbox("Ders" if lang != "en" else "Lesson", names)
    lesson = lessons[names.index(chosen)]
    st.subheader(lesson_title(lesson, lang))
    st.write(lesson_summary(lesson, lang))
    st.write(lesson_text(lesson, lang))
    if "Bu bir yöntem değildir" not in lesson_text(lesson, "tr") and lesson["id"] in {
        "phenol",
        "alizarin",
        "sulfate",
        "chloride",
        "acetone-test",
        "carbonate-rxn",
    }:
        st.caption("Bu bir yöntem değildir." if lang != "en" else "This is not a method.")


def _prepare(st, lang: str) -> None:
    st.header("Asit hazırlama" if lang != "en" else "Acid preparation")
    image = photo("02_acid_preparation.jpg") or photo("hcl.jpg")
    if image is not None:
        st.image(str(image), use_container_width=True)
    st.caption("Fotoğraf bir hazırlama yöntemi değildir. Su, derişik asidin üzerine dökülmez." if lang != "en" else "The photograph is not a preparation method. Water is not poured onto concentrated acid.")
    name = st.text_input("Ad" if lang != "en" else "Name", value="HCl")
    c1 = st.number_input("C1", min_value=0.0, value=32.0)
    basis = st.selectbox("Baz" if lang != "en" else "Basis", CONCENTRATION_BASES, index=list(CONCENTRATION_BASES).index("percent_v_v"))
    c2 = st.number_input("C2", min_value=0.0, value=18.5)
    volume = st.number_input("Hacim" if lang != "en" else "Volume", min_value=0.0, value=1000.0)
    unit = st.selectbox("Birim" if lang != "en" else "Unit", VOLUME_UNITS)
    if st.button("Hesapla" if lang != "en" else "Calculate"):
        math_line, refusal = prepare_lines(name, c1, basis, c2, volume, unit)
        st.info(math_line)
        st.warning(refusal)


def _calc(st, lang: str) -> None:
    st.header("Hesaplar" if lang != "en" else "Calculations")
    st.caption("Kuramsal hidrostatik. Sonuç bir işlem onayı değildir." if lang != "en" else "Theoretical hydrostatic pressure. The result is not a work approval.")
    weight = st.number_input("Çamur ağırlığı, ppg" if lang != "en" else "Mud weight, ppg", min_value=0.0, value=10.0)
    depth = st.number_input("TVD, ft", min_value=0.0, value=1000.0)
    if st.button("Hidrostatik" if lang != "en" else "Hydrostatic"):
        result = hydrostatic_pressure(weight, depth)
        if result.value is None:
            st.warning(result.detail)
        else:
            st.info(f"{result.value} {result.unit}. {result.detail}")


def _library(st, lang: str) -> None:
    st.header("Kimyasal tanıma" if lang != "en" else "Chemical recognition")
    st.caption("GHS piktogramı atanmaz. Alanlar ürün SDS'si değildir." if lang != "en" else "No GHS pictogram is assigned. Fields are not the product SDS.")
    names = [record_name(record, lang) for record in STARTERS]
    chosen = st.selectbox("Kayıt" if lang != "en" else "Record", names)
    record = STARTERS[names.index(chosen)]
    image = photo(f"{record['id']}.jpg")
    if image is not None:
        st.image(str(image), width=220)
    st.subheader(record_name(record, lang))
    st.write(record.get("formula", ""))
    st.write(record_identity(record, lang))
    for field in ("use", "hazard", "storage", "source"):
        text = general_field(record, field, lang)
        if text:
            st.write(text)


def _ppe(st, lang: str) -> None:
    st.header("Görsel KKD" if lang != "en" else "Visual PPE")
    st.warning(t("ppe_note", lang) if t("ppe_note", lang) != "ppe_note" else "Bu liste hatırlatmadır. SDS ve işyeri değerlendirmesi ekipmanı seçer.")
    image = photo("06_safety_ppe.jpg")
    if image is not None:
        st.image(str(image), use_container_width=True)
        st.caption("Yüz siperi sıçrama gözlüğünün yerine geçmez. Eldiven her kimyasal için gösterilmez." if lang != "en" else "A face shield does not replace splash goggles. The glove is not shown as suiting every chemical.")
    for key, prefix in PPE_ITEMS:
        st.subheader(t(prefix + "_title", lang))
        for suffix in ("_what", "_when", "_care"):
            line = t(prefix + suffix, lang)
            if line != prefix + suffix:
                st.write(line)
        local = photo(key + ".jpg")
        if local is not None and key in {"glove", "coat", "boot", "eyewash", "hood", "shield"}:
            st.image(str(local), width=180)


def _inventory(st, lang: str, connection) -> None:
    st.header("Kimyasal envanter" if lang != "en" else "Chemical inventory")
    st.caption("Bu tarayıcı oturumunun geçici dosyasıdır. Masaüstü veritabanı değildir." if lang != "en" else "This is the browser session's temporary file. It is not the desktop database.")
    with st.form("chemical"):
        name = st.text_input("Ad" if lang != "en" else "Name")
        quantity = st.text_input("Miktar" if lang != "en" else "Quantity", value="1")
        unit = st.text_input("Birim" if lang != "en" else "Unit", value="g")
        location = st.text_input("Yer" if lang != "en" else "Location", value="Raf")
        expiry = st.text_input("Son kullanma" if lang != "en" else "Expiry", value="2099-01-01")
        submitted = st.form_submit_button("Kaydet" if lang != "en" else "Save")
    if submitted:
        try:
            add_chemical(
                connection,
                {
                    "name": name,
                    "quantity": quantity,
                    "unit": unit,
                    "location": location,
                    "expiry": expiry,
                },
            )
        except ValidationError as exc:
            st.error(str(exc))
    rows = list_chemicals(connection)
    if rows:
        st.dataframe([{key: row.get(key, "") for key in ("name", "quantity", "unit", "location", "expiry")} for row in rows])


def _inspection(st, lang: str, connection) -> None:
    st.header("Haftalık denetim" if lang != "en" else "Weekly inspection")
    st.caption("İşaretler hatırlatmadır. SDS doğrulaması değildir." if lang != "en" else "Ticks are reminders. They are not an SDS verification.")
    with st.form("inspection"):
        inspector = st.text_input("Denetçi" if lang != "en" else "Inspector")
        items = {key: st.checkbox(t(key, lang) if t(key, lang) != key else key, value=False) for key in CHECK_KEYS}
        submitted = st.form_submit_button("Kaydet" if lang != "en" else "Save")
    if submitted:
        try:
            add_inspection(connection, {"inspector": inspector, "items": items})
        except ValidationError as exc:
            st.error(str(exc))
    rows = list_inspection_rows(connection)
    if rows:
        st.dataframe(rows)


def _incident(st, lang: str, connection) -> None:
    st.header("Olay bildirimi" if lang != "en" else "Incident report")
    with st.form("incident"):
        kind = st.selectbox("Tür" if lang != "en" else "Kind", INCIDENT_KINDS)
        severity = st.selectbox("Şiddet" if lang != "en" else "Severity", SEVERITIES)
        description = st.text_area("Açıklama" if lang != "en" else "Description")
        submitted = st.form_submit_button("Kaydet" if lang != "en" else "Save")
    if submitted:
        try:
            add_incident(
                connection,
                {"kind": kind, "severity": severity, "description": description, "status": "open"},
            )
        except ValidationError as exc:
            st.error(str(exc))
    rows = list_incidents(connection)
    if rows:
        st.dataframe(rows)


def _tutor(st, lang: str) -> None:
    st.header("Yerel içerik yardımcısı" if lang != "en" else "Local content assistant")
    st.warning("Bağlı bir yapay zekâ servisi yok." if lang != "en" else "No connected AI service is available.")
    question = st.text_input("Soru" if lang != "en" else "Question", value="Bernard kalsimetresi")
    if st.button("Sor" if lang != "en" else "Ask"):
        result = answer(question, lang=lang)
        st.write(result["text"])
        st.caption(f"remote={result['remote']}")
        if result["open_id"]:
            lesson = find_lesson(result["open_id"])
            if lesson is not None:
                st.write(lesson_title(lesson, lang))


if __name__ == "__main__":
    main()
