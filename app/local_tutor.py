"""Answers drawn from lessons already stored in the application.

There is no remote model behind this module. It must not be described as one.
"""

from __future__ import annotations

from app.academy_content import find_lesson, lesson_summary, lesson_text

NOT_A_MODEL = {
    "tr": "Bağlı bir yapay zekâ servisi yok. Bu cevap uygulamanın içindeki dersten seçildi.",
    "en": "No connected AI service is available. This answer was chosen from a lesson stored in the application.",
}


def answer(question: str, lesson_id: str = "", lang: str = "tr") -> dict:
    text = " ".join(str(question or "").casefold().split())
    language = "en" if lang == "en" else "tr"
    lesson = find_lesson(lesson_id) if lesson_id else None
    reply, open_id = _pick(text, lesson, language)
    if not reply:
        reply = _unknown(language)
        open_id = ""
    return {
        "text": reply + "\n" + NOT_A_MODEL[language],
        "open_id": open_id,
        "remote": False,
    }


def _pick(text: str, lesson: dict | None, lang: str) -> tuple[str, str]:
    if not text:
        return _unknown(lang), ""
    if _has(text, "fenolftalein", "alizarin", "klorür", "chloride", "aseton", "acetone") and _has(
        text, "kitap", "handbook", "el kitabı", "kaynak"
    ):
        return (
            _tr(
                lang,
                "Bu test GEOLOG el kitabında bir yöntem olarak yok. Kart ayrı bir genel derstir. Reaktif miktarı yazılmaz.",
                "This test is not a method in the GEOLOG handbook. The card is a separate general lesson. No reagent amount is written.",
            ),
            "phenol",
        )
    if _has(text, "yıkama", "elek", "wash", "sieve"):
        return (
            _tr(
                lang,
                "Elek listesi müşteriye aittir. Yumuşak su kullanılır. Jips, tebeşir ve kil sert jetle dağılır. Deterjan oranı ve elek milimetresi bu cevapta yoktur.",
                "The sieve list belongs to the customer. A gentle stream is used. Gypsum, chalk, and clay break up under a hard jet. A detergent ratio and sieve millimetres are not in this answer.",
            ),
            "sample-wash",
        )
    if _has(text, "otomatik", "automatic") and _has(text, "fark", "differ"):
        return (
            _tr(
                lang,
                "Bernard düzeni gaz hacmini gözle okur. Otomatik cihaz algılayıcı kullanır ve kendi dönüşümünü uygular. İkisinin tuş sırası bu uygulamada yoktur.",
                "A Bernard rig reads gas volume by eye. An automatic instrument uses a sensor and its own conversion. Neither key sequence is in this application.",
            ),
            "auto-calcimeter",
        )
    if _has(text, "gaz", "gas") and _has(text, "karbonat", "carbonate"):
        return (
            _tr(
                lang,
                "Karbonat asitle karbondioksit verebilir. Ölçülen gaz hacmi, sıcaklık ve basınç düzeltmesinden sonra örnek kütlesiyle ilişkilendirilir. 22,4 L karşılığı teorik stokiyometridir, cihaz okuması değildir.",
                "Carbonate can release carbon dioxide with acid. Measured gas volume is related to sample mass after a temperature and pressure correction. The 22.4 L figure is theoretical stoichiometry, not an instrument reading.",
            ),
            "bernard",
        )
    if _has(text, "hatalı", "hata", "yanlış", "error", "wrong", "neden sonuç"):
        return (
            _tr(
                lang,
                "Kaçak, kabarcık, seviye dengelemeden okuma ve örneği tartmamak hacmi bozar. Arıza kodu modelin kılavuzundadır.",
                "A leak, bubbles, reading before the levels are balanced, and not weighing the sample spoil the volume. A fault code is in the model manual.",
            ),
            "trouble-gas",
        )
    if _has(text, "basit", "anlamadım", "simpler", "simple"):
        if lesson is not None:
            return lesson_summary(lesson, lang), lesson["id"]
        return (
            _tr(
                lang,
                "Bernard düzeni, karbonatlı örneğin verdiği gazın yer değiştirmesini gösterir. Yüzde için üretici katsayısı gerekir.",
                "A Bernard rig shows the gas displaced by a carbonate sample. A percent needs the manufacturer's factor.",
            ),
            "bernard",
        )
    if _has(text, "kalsit", "calcite") and _has(text, "dolomit", "dolomite"):
        return (
            _tr(
                lang,
                "İkisi de karbonattır. Kalsit genellikle daha belirgin kabarcık verir. Zayıf kabarcık tek başına dolomit kanıtı değildir. Renk de tanı koymaz.",
                "Both are carbonates. Calcite usually bubbles more clearly. A weak bubble is not proof of dolomite by itself. Color does not identify either one.",
            ),
            "dolomite",
        )
    if _has(text, "kanıt", "proof") or _has(text, "floresan", "fluores"):
        return (
            _tr(
                lang,
                "UV floresansı hidrokarbon ihtimalini akla getirir. Tek başına kesin kanıt değildir. Yağ, katkı ve bazı mineraller de parlayabilir.",
                "UV fluorescence suggests hydrocarbon as a possibility. By itself it is not definite proof. Oil, additives, and some minerals can also glow.",
            ),
            "uv",
        )
    if _has(text, "eldiven", "glove"):
        return (
            _tr(
                lang,
                "Eldiven malzemesi kimyasalın güncel SDS belgesinden kontrol edilir. Bu uygulama malzeme seçmez. Yüz siperi sıçrama gözlüğünün yerine geçmez.",
                "Glove material is checked in the chemical's current SDS. This application does not choose a material. A face shield does not replace splash goggles.",
            ),
            "safety-ppe",
        )
    if _has(text, "tuş", "tus", "marka", "model", "menü", "menu", "kaç ml", "kac ml"):
        return "", ""
    if "bernard" in text:
        return _stored(lang, "bernard")
    if _has(text, "otomatik", "automatic") and _has(text, "kalsimetre", "calcimeter"):
        return _stored(lang, "auto-calcimeter")
    if _has(text, "numune", "sample") and _has(text, "hazır", "hazir", "prepare", "yık", "yik", "wash"):
        return _stored(lang, "sample-wash")
    if _has(text, "jips", "gypsum") and _has(text, "anhidrit", "anhydrite"):
        return _stored(lang, "mineral-split")
    if _has(text, "sınır", "sinir", "limit") and _has(text, "test"):
        return (
            _tr(
                lang,
                "Kart, gözlemin neyi kanıtlamadığını yazar. Reaktif miktarı ve kesin mineral adı bu cevapta yoktur.",
                "The card states what an observation does not prove. A reagent amount and a certain mineral name are not in this answer.",
            ),
            "",
        )
    useful = [word for word in text.split() if len(word) > 4]
    if lesson is not None and any(word in lesson_text(lesson, lang).casefold() for word in useful[:4]):
        return lesson_summary(lesson, lang), lesson["id"]
    return "", ""


def _stored(lang: str, lesson_id: str) -> tuple[str, str]:
    lesson = find_lesson(lesson_id)
    if lesson is None:
        return "", ""
    return lesson_summary(lesson, lang), lesson_id


def _unknown(lang: str) -> str:
    return _tr(
        lang,
        "Bu sorunun cevabı yüklü derslerde yok. Cihaz modeli, reaktif miktarı ve SDS için üretici kılavuzu ile iş prosedürü gerekir.",
        "This question is not answered by the stored lessons. The instrument model, a reagent amount, and the SDS need the manufacturer manual and the work procedure.",
    )


def _has(text: str, *words: str) -> bool:
    return any(word in text for word in words)


def _tr(lang: str, turkish: str, english: str) -> str:
    return english if lang == "en" else turkish
