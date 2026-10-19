"""Local card and lesson images.

A missing file becomes a drawn panel. It is never left as a broken-image icon.
Captions say whether the file is a photograph or a drawing.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "images"
PHOTO_DIR = ROOT / "assets" / "photos"

# kind, file, caption_tr, caption_en
CATALOG = {
    "robot": (
        "drawing",
        "robot.jpg",
        "Özgün çizim. Bağlı bir yapay zekâ servisi değildir.",
        "Original drawing. It is not a connected AI service.",
    ),
    "microscope": (
        "drawing",
        "microscope.png",
        "Kamu malı çizim. Fotoğraf değildir. Numaralar kaynak çizimindedir; bu uygulama cihaz modeli yazmaz.",
        "Public-domain drawing. Not a photograph. The numbers belong to the source drawing; this application names no instrument model.",
    ),
    "flask": (
        "photo",
        "flask.jpg",
        "Fotoğraf. Boş bir erlen. Üzerindeki mililitre işaretleri bir hazırlama tarifi değildir.",
        "Photograph. An empty Erlenmeyer flask. The millilitre marks are not a preparation recipe.",
    ),
    "beakers": (
        "photo",
        "beakers.jpg",
        "Fotoğraf. Beherler. İçlerindeki renkli sıvı bir hazırlama tarifi veya sonuç değildir.",
        "Photograph. Beakers. The coloured liquids are not a preparation recipe or a result.",
    ),
    "glassware": (
        "photo",
        "glassware.jpg",
        "Fotoğraf. Laboratuvar cam malzemesi. Belirli bir cihazın kullanım kılavuzu değildir. Kalsimetre değildir ve üç su düzeneğinin tamamı değildir.",
        "Photograph. Laboratory glassware. It is not a manual for one instrument. It is not a calcimeter and it is not the whole set of three water rigs.",
    ),
    "hcl": (
        "photo",
        "hcl.jpg",
        "Fotoğraf. Üzerinde hidroklorik asit yazan bir şişe. Bu işyerinin ürünü ve SDS belgesi değildir.",
        "Photograph. A bottle labelled hydrochloric acid. It is not this workplace's product or SDS.",
    ),
    "limestone": (
        "photo",
        "limestone.jpg",
        "Fotoğraf. Kireçtaşı olarak kaydedilmiş bir kayaç yüzeyi. Renk ve doku tek başına tanı değildir.",
        "Photograph. A rock surface recorded as limestone. Colour and texture are not an identification by themselves.",
    ),
    "dolomite": (
        "photo",
        "dolomite.jpg",
        "Fotoğraf. Commons kaydında Fas dolomiti olarak geçer. Renk tanı koymaz.",
        "Photograph. The Commons record calls this dolomite from Morocco. Colour does not identify it.",
    ),
    "gypsum": (
        "photo",
        "gypsum.jpg",
        "Fotoğraf. Jips olarak kaydedilmiş bir örnek. Bu biçim her jips kırıntısının görünüşü değildir.",
        "Photograph. A specimen recorded as gypsum. This form is not how every gypsum cutting looks.",
    ),
    "anhydrite": (
        "photo",
        "anhydrite.jpg",
        "Fotoğraf. Commons kaydında anhidrit olarak geçer. Renk tanı koymaz.",
        "Photograph. The Commons record calls this anhydrite. Colour does not identify it.",
    ),
    "coal": (
        "photo",
        "coal.jpg",
        "Fotoğraf. Bitümlü kömür olarak kaydedilmiş bir örnek. Tek bir test kömürü kanıtlamaz.",
        "Photograph. A specimen recorded as bituminous coal. One test does not prove coal.",
    ),
    "sieve": (
        "photo",
        "sieve.jpg",
        "Fotoğraf. Eleme için kullanılmış bir tel örgü. Müşterinin elek listesi ve milimetre değeri burada yoktur.",
        "Photograph. A wire mesh used for sieving. The customer's sieve list and millimetre size are not here.",
    ),
    "glove": (
        "photo",
        "glove.jpg",
        "Fotoğraf. Mavi bir nitril eldiven örneği. Her kimyasal için uygun olduğu anlamına gelmez.",
        "Photograph. An example of a blue nitrile glove. It does not mean the glove suits every chemical.",
    ),
    "shield": (
        "photo",
        "shield.jpg",
        "Fotoğraf. Bir yüz siperi. Kimyasal sıçrama siperi olduğu doğrulanmadı. Sıçrama gözlüğünün yerine geçmez.",
        "Photograph. A face shield. It is not confirmed as a chemical-splash shield. It does not replace splash goggles.",
    ),
    "logo": (
        "drawing",
        "logo.png",
        "Özgün amblem. Fotoğraf değildir.",
        "Original emblem. Not a photograph.",
    ),
    "derrick": (
        "drawing",
        "derrick.png",
        "Özgün kule çizimi. Fotoğraf değildir ve bir sahayı göstermez.",
        "Original derrick drawing. Not a photograph and not a picture of one site.",
    ),
    "tray": (
        "drawing",
        "tray.png",
        "Özgün numune tepsisi çizimi. Fotoğraf değildir.",
        "Original sample-tray drawing. Not a photograph.",
    ),
    "molecule": (
        "drawing",
        "molecule.png",
        "Özgün motif. Belirli bir maddenin molekül yapısı değildir.",
        "Original motif. It is not the molecular structure of one substance.",
    ),
    "banner": (
        "drawing",
        "banner.png",
        "Eğitim bandı. Kireçtaşı fotoğrafı, boş erlen fotoğrafı ve özgün kule çizimi bir aradadır. Ayakta kule çizimi durur. Ekipman taşıyan bir kamyon bu bantta yoktur.",
        "Training banner. A limestone photograph, an empty-flask photograph, and an original derrick drawing. The standing derrick stays a drawing. A truck carrying equipment is not on this banner.",
    ),
    "fallback": (
        "drawing",
        "fallback.png",
        "Yedek çizim. İstenen dosya açılamadı.",
        "Fallback drawing. The requested file could not be opened.",
    ),
    "studio_scene": (
        "drawing",
        "@studio_scene",
        "Şematik çizim. Görsel eğitim sahnesi. Fotoğraf veya video değildir.",
        "Schematic drawing. A visual-training scene. Not a photograph or a video.",
    ),
    "calc_scene": (
        "drawing",
        "@calc_scene",
        "Şematik hesap çizimi. Sonuç ve hazırlama onayı değildir.",
        "Schematic calculation drawing. Not a result and not a preparation approval.",
    ),
    "devices_scene": (
        "drawing",
        "@devices_scene",
        "Şematik cihaz çizimi. Marka ve parça numarası yoktur. Cam malzeme fotoğrafı kalsimetre değildir.",
        "Schematic instrument drawing. No brand and no part number. A glassware photograph is not a calcimeter.",
    ),
    "rocks_scene": (
        "drawing",
        "@rocks_scene",
        "Şematik kayaç çizimi. Kireçtaşı fotoğrafı her mineral değildir ve kalsit değildir.",
        "Schematic rock drawing. A limestone photograph is not every mineral and is not calcite.",
    ),
    "ppe_scene": (
        "drawing",
        "@ppe_scene",
        "Şematik KKD çizimi. Yüz siperi sıçrama gözlüğünün yerine geçmez. Eldiven her kimyasal için gösterilmez. Doğrulanmış bir sıçrama gözlüğü fotoğrafı bu uygulamada yoktur.",
        "Schematic PPE drawing. A face shield does not replace splash goggles. The glove is not shown as suiting every chemical. A verified splash-goggle photograph is not in this application.",
    ),
    "hardhat": (
        "photo",
        "modern-hardhat.jpg",
        "Fotoğraf. Hong Kong'da bir şantiyede duran plastik baret. Dosya başlığı beyaz baret der. Kabuktaki basılı tarih ve marka bu uygulamanın onayı değildir. 1930'lardan kalma deri bir madenci kaskı değildir. Yandaki eldiven kimyasal eldiveni olarak önerilmez. Peachyeung316, CC BY-SA 4.0.",
        "Photograph. A plastic hard hat sitting on a worksite in Hong Kong. The file title calls it a white hard hat. The printed date and brand on the shell are not this application's approval. It is not a 1930s leather miner's helmet. The gloves beside it are not recommended as chemical gloves. Peachyeung316, CC BY-SA 4.0.",
    ),
    "inventory_scene": (
        "drawing",
        "@inventory_scene",
        "Şematik kayıt çizimi. Distilasyon camı envanter değildir.",
        "Schematic record drawing. Distillation glass is not an inventory.",
    ),
    "inspection_scene": (
        "drawing",
        "@inspection_scene",
        "Şematik denetim çizimi. İşaret, laboratuvarın güvenli olduğunun kanıtı değildir.",
        "Schematic inspection drawing. A mark is not proof that the laboratory is safe.",
    ),
    "auto_scene": (
        "drawing",
        "@auto_scene",
        "Şematik kapalı hücre. Bir markanın kalsimetresi değildir.",
        "Schematic closed cell. It is not one brand of calcimeter.",
    ),
    "water_scene": (
        "drawing",
        "@water_scene",
        "Şematik üç su düzeneği. Distilasyon camının fotoğrafı bütün sistem değildir.",
        "Schematic of three water rigs. A distillation-glass photograph is not the whole system.",
    ),
    "phenol_scene": (
        "drawing",
        "@phenol_scene",
        "Şematik belirteç. Renk bir tarif veya sonuç belgesi değildir.",
        "Schematic indicator. The colour is not a recipe or a result record.",
    ),
    "stain_scene": (
        "drawing",
        "@stain_scene",
        "Şematik boyama. Yöntem metni kopyalanmadı. Asit derişimi yoktur.",
        "Schematic stain. The method text was not copied. There is no acid strength.",
    ),
    "bubble_scene": (
        "drawing",
        "@bubble_scene",
        "Şematik kabarcık. Miktar ve asit adı yoktur.",
        "Schematic bubble. There is no amount and no acid name.",
    ),
    "pair_scene": (
        "drawing",
        "@pair_scene",
        "Şematik jips ve anhidrit. Renk tanı değildir. Ayırma tarifi yoktur.",
        "Schematic gypsum and anhydrite. Colour is not an identification. There is no separation recipe.",
    ),
    "uv_scene": (
        "drawing",
        "@uv_scene",
        "Şematik UV bakışı. Parlama kesin kanıt değildir. Lamba modeli yoktur.",
        "Schematic UV view. A glow is not definite proof. There is no lamp model.",
    ),
    "cut_scene": (
        "drawing",
        "@cut_scene",
        "Şematik çözücü lekesi. Çözücü adı ve miktarı yoktur.",
        "Schematic solvent mark. There is no solvent name and no amount.",
    ),
    "acetone_scene": (
        "drawing",
        "@acetone_scene",
        "Şematik aseton gözlemi. Miktar yoktur ve leke kesin kanıt değildir.",
        "Schematic acetone observation. There is no amount, and the mark is not definite proof.",
    ),
    "chloride_scene": (
        "drawing",
        "@chloride_scene",
        "Şematik çökelek. Derişim ve tarif yoktur. Tuz kristali fotoğrafı bu test değildir.",
        "Schematic precipitate. There is no strength and no recipe. A salt-crystal photograph is not this test.",
    ),
    "sulfate_scene": (
        "drawing",
        "@sulfate_scene",
        "Şematik çizim. Sülfat testi için yöntem bu uygulamada yoktur.",
        "Schematic drawing. This application has no method for a sulfate test.",
    ),
    "coal_pair_scene": (
        "drawing",
        "@coal_pair_scene",
        "Şematik kömür ve şeyl. Tek kimyasal test yoktur. Kömür fotoğrafı şeyl değildir.",
        "Schematic coal and shale. There is no single chemical test. A coal photograph is not shale.",
    ),
    "calcite_scene": (
        "photo",
        "calcite.jpg",
        "Fotoğraf. Doğal Tarih Müzesi, Londra kaydında İzlanda spatı olarak geçen kalsit çeşidi. Reytharfjorthur, İzlanda. Berrak bir kristal her kalsit kırıntısı değildir. Kireçtaşı yüzeyi ve beyaz toz bu kare değildir. Renk tanı koymaz. Daderot, CC0.",
        "Photograph. Calcite, the variety Iceland spar, recorded at the Natural History Museum, London, from Reytharfjorthur, Iceland. A clear crystal is not every calcite cutting. A limestone surface and a white powder are not this frame. Colour does not identify it. Daderot, CC0.",
    ),
    "quartz_scene": (
        "photo",
        "quartz.jpg",
        "Fotoğraf. GeoDIL 2523 kaydında kaya kristali olarak geçen renksiz kuvars. Renk tür koymaz. Bu kristal her kuvars kırıntısının görünüşü değildir. Darla Sondrol, CC0.",
        "Photograph. Colorless quartz recorded as rock crystal in GeoDIL 2523. Colour does not set the variety. This crystal is not how every quartz cutting looks. Darla Sondrol, CC0.",
    ),
    "sand_scene": (
        "photo",
        "sandstone.jpg",
        "Fotoğraf. GeoDIL 474 kaydında kumtaşı olarak geçen el örneği. Kaynak, çimentoyu hematit olarak yazar. Sarı-kırmızı renk tanı değildir. Elek listesi ve milimetre değeri yoktur. Nessa Eull, CC0.",
        "Photograph. A hand specimen recorded as sandstone in GeoDIL 474. The source names hematite as the cement. The yellow-red colour is not an identification. There is no sieve list and no millimetre size. Nessa Eull, CC0.",
    ),
    "shale_scene": (
        "photo",
        "shale.jpg",
        "Fotoğraf. GeoDIL 478 kaydında arenalı şeyl olarak geçen el örneği. Kaynak, örnekte kuvars da bulunduğunu ve tipik şeylden daha masif olduğunu yazar. Siyahlık kömür demek değildir. Kömür fotoğrafı bu kayaç değildir. Nessa Eull, CC0.",
        "Photograph. A hand specimen recorded as arenaceous shale in GeoDIL 478. The source says the specimen also contains quartz and is more massive than a typical fissile shale. Black colour does not mean coal. A coal photograph is not this rock. Nessa Eull, CC0.",
    ),
    "carb_scene": (
        "photo",
        "carb-shale.jpg",
        "Fotoğraf. GeoDIL 242 kaydında karbonlu şeyl olarak geçen el örneği. Kaynak, beyazımsı bitki izleri ve dilinim yazar. Siyahlık kömür demek değildir. Kömür fotoğrafı bu kayaç değildir. Darla Sondrol, CC0.",
        "Photograph. A hand specimen recorded as carbonaceous shale in GeoDIL 242. The source describes whitish plant impressions and cleavage. Black colour does not mean coal. A coal photograph is not this rock. Darla Sondrol, CC0.",
    ),
    "odor_scene": (
        "drawing",
        "@odor_scene",
        "Şematik koku. Koku hidrokarbonun kesin kanıtı değildir.",
        "Schematic odor. An odor is not definite proof of hydrocarbon.",
    ),
    "trouble_scene": (
        "drawing",
        "@trouble_scene",
        "Şematik karışık gözlem. Renk, kabarcık ve parlama tek başına ad koymaz.",
        "Schematic mixed observation. Colour, a bubble, and a glow do not assign a name by themselves.",
    ),
    "label_scene": (
        "drawing",
        "@label_scene",
        "Şematik torba ve etiket. Kuyu adı ve derinlik bu çizimde yoktur.",
        "Schematic bag and label. A well name and a depth are not on this drawing.",
    ),
    "sheet_scene": (
        "drawing",
        "@sheet_scene",
        "Şematik sonuç kâğıdı. Dakika ve katsayı yazılmaz.",
        "Schematic result sheet. Minutes and a factor are not written.",
    ),
    "hero_lab": (
        "photo",
        "01_hero_laboratory.jpg",
        "Kullanıcının verdiği fotoğraf. Eldivenli bir el sıvı döküyor. Bu bir hazırlama yöntemi değildir. Suyun asidin üzerine döküldüğü söylenmez. Kalsimetre değildir. Lisansı ayrıca doğrulanmadı.",
        "Photograph supplied by the user. A gloved hand pours a liquid. This is not a preparation method. It does not say that water is poured onto acid. It is not a calcimeter. The license was not independently verified.",
    ),
    "acid_pour": (
        "photo",
        "02_acid_preparation.jpg",
        "Kullanıcının verdiği fotoğraf. Bir behere sıvı dökülüyor. Hazırlama yöntemi değildir. Suyun asidin üzerine döküldüğü söylenmez. Lisansı ayrıca doğrulanmadı.",
        "Photograph supplied by the user. Liquid is poured into a beaker. It is not a preparation method. It does not say that water is poured onto acid. The license was not independently verified.",
    ),
    "rock_samples": (
        "photo",
        "03_rock_mineral_samples.jpg",
        "Kullanıcının verdiği örnek fotoğrafı. Renk ve doku tanı koymaz. Kalsit veya kireçtaşı adı bu kareden okunmaz. Lisansı ayrıca doğrulanmadı.",
        "Specimen photograph supplied by the user. Colour and texture are not an identification. The frame does not name calcite or limestone. The license was not independently verified.",
    ),
    "tube_photo": (
        "photo",
        "04_chemical_tests.jpg",
        "Kullanıcının verdiği fotoğraf. Renkli sıvılar bir test sonucu veya tarif değildir. Tam bir yöntem değildir. Lisansı ayrıca doğrulanmadı.",
        "Photograph supplied by the user. The coloured liquids are not a test result or a recipe. This is not a complete method. The license was not independently verified.",
    ),
    "instruments_photo": (
        "photo",
        "05_microscope_instruments.jpg",
        "Kullanıcının verdiği mikroskop fotoğrafı. Cihaz modeli yazılmaz. Kalsimetre değildir. Lisansı ayrıca doğrulanmadı.",
        "Microscope photograph supplied by the user. No instrument model is named. It is not a calcimeter. The license was not independently verified.",
    ),
    "ppe_photo": (
        "photo",
        "06_safety_ppe.jpg",
        "Kullanıcının verdiği KKD fotoğrafı. Yüz siperi sıçrama gözlüğünün yerine geçmez. Eldiven uygunluğu SDS belgesinden gelir. Sıçrama derecesi bu kareden okunmaz. Lisansı ayrıca doğrulanmadı.",
        "PPE photograph supplied by the user. A face shield does not replace splash goggles. Glove suitability comes from the SDS. A splash rating is not read from this frame. The license was not independently verified.",
    ),
}

LESSON_IMAGES = {
    "auto-calcimeter": "auto_scene",
    "bernard": "devices_scene",
    "pure-water": "glassware",
    "phenol": "phenol_scene",
    "alizarin": "stain_scene",
    "carbonate-rxn": "bubble_scene",
    "gypsum-test": "pair_scene",
    "uv": "uv_scene",
    "solvent-cut": "cut_scene",
    "acetone-test": "acetone_scene",
    "chloride": "chloride_scene",
    "sulfate": "sulfate_scene",
    "coal-test": "coal_pair_scene",
    "calcite": "calcite_scene",
    "dolomite": "dolomite",
    "gypsum": "gypsum",
    "anhydrite": "anhydrite",
    "quartz": "quartz_scene",
    "limestone": "limestone",
    "sandstone": "sand_scene",
    "shale": "shale_scene",
    "coal": "coal",
    "carb-shale": "carb_scene",
    "show-odor": "odor_scene",
    "measure-map": "calc_scene",
    "safety-ppe": "ppe_scene",
    "trouble-gas": "devices_scene",
    "trouble-water": "water_scene",
    "trouble-tests": "trouble_scene",
    "sample-collect": "tray",
    "sample-wash": "sieve",
    "sample-dry": "tray",
    "sample-label": "label_scene",
    "sample-look": "microscope",
    "fluor-direct": "uv_scene",
    "calc-sheet": "sheet_scene",
    "mineral-split": "rocks_scene",
}


def image_path(key: str) -> Path:
    _kind, filename, _tr, _en = CATALOG[key]
    if filename.startswith("@"):
        return IMAGE_DIR / "fallback.png"
    local = IMAGE_DIR / filename
    if local.exists():
        return local
    photo = PHOTO_DIR / filename
    if photo.exists():
        return photo
    return local


def caption(key: str, lang: str) -> str:
    _kind, _filename, turkish, english = CATALOG.get(key, CATALOG["fallback"])
    return english if lang == "en" else turkish


def lesson_image_key(lesson_id: str) -> str:
    return LESSON_IMAGES.get(lesson_id, "fallback")


def _fallback_pixmap(width: int, height: int) -> QPixmap:
    width = max(40, width)
    height = max(40, height)
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#E5F0F1"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#0B5964"), 3))
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawRoundedRect(12, 12, width - 24, height - 24, 12, 12)
    painter.drawEllipse(width // 2 - 18, height // 2 - 28, 36, 16)
    painter.drawLine(width // 2 - 10, height // 2 - 12, width // 2 - 22, height // 2 + 24)
    painter.drawLine(width // 2 + 10, height // 2 - 12, width // 2 + 22, height // 2 + 24)
    painter.drawLine(width // 2 - 22, height // 2 + 24, width // 2 + 22, height // 2 + 24)
    painter.end()
    return pixmap


def _drawn_pixmap(key: str, width: int, height: int, lang: str) -> QPixmap:
    from app.motion import paint_drawn

    width = max(40, width)
    height = max(40, height)
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#F7FBFA"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    paint_drawn(painter, QRectF(2, 2, width - 4, height - 4), key, lang)
    painter.end()
    return pixmap


def load_pixmap(key: str, width: int, height: int, lang: str = "tr") -> QPixmap:
    chosen = key if key in CATALOG else "fallback"
    _kind, filename, _tr, _en = CATALOG[chosen]
    if filename.startswith("@"):
        return _drawn_pixmap(chosen, width, height, lang)
    path = image_path(chosen)
    source = QPixmap(str(path))
    if source.isNull():
        source = QPixmap(str(image_path("fallback")))
    if source.isNull():
        return _fallback_pixmap(width, height)
    scaled = source.scaled(
        max(1, width),
        max(1, height),
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = max(0, (scaled.width() - width) // 2)
    y = max(0, (scaled.height() - height) // 2)
    return scaled.copy(x, y, max(1, width), max(1, height))


class FitImage(QLabel):
    def __init__(self, key: str, height: int = 110, lang: str = "tr"):
        super().__init__()
        self.image_key = key
        self.lang = lang
        self._height = height
        self.setFixedHeight(height)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setPixmap(load_pixmap(key, 160, height, lang))

    def set_lang(self, lang: str) -> None:
        self.lang = lang
        if self.width() > 8:
            self.setPixmap(load_pixmap(self.image_key, self.width(), self._height, lang))

    def sizeHint(self) -> QSize:
        return QSize(120, self._height)

    def minimumSizeHint(self) -> QSize:
        return QSize(40, self._height)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.width() > 8:
            self.setPixmap(load_pixmap(self.image_key, self.width(), self._height, self.lang))
