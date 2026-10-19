"""Schematic animations for the Mudlogging Academy.

Drawings are labelled schematics. They are not videos, photographs, or
operating procedures. Acid is drawn going into water. Water is never drawn
onto concentrated acid. No measured quantity is painted.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app.i18n import t
from app.motion import paint_scene
from app.speech import Narrator

STEPS = {
    "auto_cup": {
        "see_tr": "Kapta katı örnek duruyor. Kütle yazılmıyor.",
        "see_en": "A solid sample sits in the cup. No mass is written.",
        "does_tr": "Kap, örneği ölçüm hücresinden ayrı tutar.",
        "does_en": "The cup keeps the sample apart from the measuring cell.",
        "why_tr": "Tartılmamış örnekten yüzde çıkmaz.",
        "why_en": "An unweighed sample does not produce a percent.",
    },
    "auto_cell": {
        "see_tr": "Kapalı bir hücre ve asit girişi görünüyor.",
        "see_en": "A closed cell and an acid inlet are visible.",
        "does_tr": "Hücre gazı içeride tutar. Girişin yolu modele aittir.",
        "does_en": "The cell keeps the gas inside. The inlet path belongs to the model.",
        "why_tr": "Açık kapta gaz kaçar ve hacim eksik kalır.",
        "why_en": "Gas escapes from an open vessel and the volume is short.",
    },
    "auto_sensor": {
        "see_tr": "Algılayıcı ve boş bir ekran görünüyor.",
        "see_en": "A sensor and a blank display are visible.",
        "does_tr": "Algılayıcı değişimi izler. Ekran bu çizimde sayı üretmez.",
        "does_en": "The sensor follows a change. This drawing does not produce a number.",
        "why_tr": "Birim ve kalibrasyon, modelin kılavuzundadır.",
        "why_en": "The unit and the calibration are in the model manual.",
    },
    "bernard_rig": {
        "see_tr": "Örnek kabı, asit kabı, bağlantı borusu ve ölçü borusu.",
        "see_en": "A sample cup, an acid cup, a connecting tube, and a measuring tube.",
        "does_tr": "Asit örnekle karşılaşınca gaz, ölçü borusuna gider.",
        "does_en": "When acid meets the sample, gas moves toward the measuring tube.",
        "why_tr": "Parçayı tanımak, henüz karbonat yüzdesi okumak değildir.",
        "why_en": "Naming the part is not yet reading a carbonate percent.",
    },
    "bernard_gas": {
        "see_tr": "Sarı daire gazın yer değiştirmesini temsil eder. Mililitre yoktur.",
        "see_en": "The yellow circle stands for displaced gas. There are no millilitres.",
        "does_tr": "Ölçü borusu seviye farkını gösterir.",
        "does_en": "The measuring tube shows a difference in level.",
        "why_tr": "Ham hacim, sıcaklık ve basınç düzeltmesinden sonra kütleyle ilişkilendirilir.",
        "why_en": "The raw volume is related to mass after a temperature and pressure correction.",
    },
    "water_three": {
        "see_tr": "Üç ayrı düzenek: distilasyon, deiyonizasyon, ters ozmoz.",
        "see_en": "Three separate rigs: distillation, deionization, reverse osmosis.",
        "does_tr": "Her düzenek suyu başka bir yolla işler.",
        "does_en": "Each rig treats water by a different path.",
        "why_tr": "Üç ürün aynı su değildir. Bu çizim her cihazın içi değildir.",
        "why_en": "The three products are not the same water. This drawing is not every instrument's interior.",
    },
    "water_flow": {
        "see_tr": "Su beslemeden işleme, oradan ürüne ilerliyor.",
        "see_en": "Water moves from feed to treatment and then to product.",
        "does_tr": "Gösterge suyun iletkenliğini izleyebilir. Eşik modele aittir.",
        "does_en": "An indicator can follow conductivity. The threshold belongs to the model.",
        "why_tr": "Değişen kalite, filtre, reçine veya membranı akla getirir. Teşhis kılavuzdadır.",
        "why_en": "Changing quality suggests the filter, resin, or membrane. The diagnosis is in the manual.",
    },
    "acid_ppe": {
        "see_tr": "Sıçrama gözlüğü, yüz siperi ve eldiven yan yana.",
        "see_en": "Splash goggles, a face shield, and gloves side by side.",
        "does_tr": "Gözlük göze, siper yüze, eldiven ele yöneliktir.",
        "does_en": "Goggles are for the eyes, the shield for the face, and gloves for the hands.",
        "why_tr": "Siper gözlüğün yerine geçmez. Eldiven malzemesi SDS ile kontrol edilir.",
        "why_en": "A shield does not replace goggles. Glove material is checked with the SDS.",
    },
    "acid_order": {
        "see_tr": "Kapta önce su var. Asit damlası suyun içine iniyor.",
        "see_en": "Water is already in the vessel. An acid drop is falling into that water.",
        "does_tr": "Bu sıra genel güvenlik ilkesidir. Miktar yazılmaz.",
        "does_en": "This order is a general safety principle. No amount is written.",
        "why_tr": "Su, derişik asidin üzerine çizilmez. Hazırlama onayı SDS ve prosedür ister.",
        "why_en": "Water is not drawn onto concentrated acid. Preparation approval needs the SDS and the procedure.",
    },
    "collect_shaker": {
        "see_tr": "Sarsıntı ve temiz bir kürek.",
        "see_en": "A shaker and a clean scoop.",
        "does_tr": "Kürek, lag süresindeki kırıntıyı alır.",
        "does_en": "The scoop takes the cuttings at the lag time.",
        "why_tr": "Aralık ve hacim operatöre aittir. Bu çizim kural koymaz.",
        "why_en": "The interval and the volume belong to the operator. This drawing sets no rule.",
    },
    "wash_stack": {
        "see_tr": "Kaba elek, ince elek ve yumuşak su.",
        "see_en": "A coarse sieve, a fine sieve, and a gentle stream.",
        "does_tr": "Elek çamuru taneden ayırır.",
        "does_en": "The sieve separates mud from the grain.",
        "why_tr": "Sert jet jips ve kili kaybettirir. Gözenek müşteriye aittir.",
        "why_en": "A hard jet loses gypsum and clay. The mesh belongs to the customer.",
    },
    "dry_tray": {
        "see_tr": "Yayılmış tepsi ve fırın.",
        "see_en": "A spread tray and an oven.",
        "does_tr": "Fırın suyu uzaklaştırır.",
        "does_en": "The oven drives off water.",
        "why_tr": "Pişirmek örneği değiştirir. Derece yazılmaz.",
        "why_en": "Cooking changes the sample. No setpoint is written.",
    },
    "label_bag": {
        "see_tr": "Torba ve silinmeyen yazı.",
        "see_en": "A bag and a mark that stays.",
        "does_tr": "Etiket operatörü, kuyuyu, derinliği ve birimi tutar.",
        "does_en": "The label holds the operator, the well, the depth, and the unit.",
        "why_tr": "Karışan torba derinliği kaybettirir.",
        "why_en": "A mixed bag loses the depth.",
    },
    "look_grain": {
        "see_tr": "Islak tane ve doğal ışık.",
        "see_en": "A wet grain and natural light.",
        "does_tr": "Işık rengi, sertliği ve dokuyu ayırmaya yardım eder.",
        "does_en": "Light helps separate colour, hardness, and texture.",
        "why_tr": "Renk tek başına mineral adı koymaz.",
        "why_en": "Colour alone does not assign a mineral name.",
    },
    "fluor_dish": {
        "see_tr": "Lamba ve kırıntı kabı.",
        "see_en": "A lamp and a dish of cuttings.",
        "does_tr": "UV, doğrudan parlamayı gösterir.",
        "does_en": "UV shows a direct glow.",
        "why_tr": "Parlama kesin kanıt değildir. Hafif petrol ve katran parlamayabilir.",
        "why_en": "A glow is not definite proof. Light oil and tar may not glow.",
    },
    "fluor_cut": {
        "see_tr": "Kâğıtta şematik bir halka.",
        "see_en": "A schematic ring on paper.",
        "does_tr": "Çözücü, lekeyi taneden uzağa taşıyabilir.",
        "does_en": "A solvent can carry a mark away from the grain.",
        "why_tr": "Miktar ve çözücü adı yazılmaz. SDS ve havalandırma gerekir.",
        "why_en": "The amount and the solvent name are not written. The SDS and ventilation are required.",
    },
    "sheet_cols": {
        "see_tr": "Erken sütun, geç sütun ve artık.",
        "see_en": "An early column, a late column, and residue.",
        "does_tr": "İki zaman, hızlı ve yavaş karbonatı ayırmaya yardım eder.",
        "does_en": "Two times help separate a fast carbonate from a slow one.",
        "why_tr": "Dakika ve dolomit katsayısı bu çizimde çarpılmaz.",
        "why_en": "Minutes and a dolomite factor are not multiplied on this drawing.",
    },
    "mineral_four": {
        "see_tr": "Kalsit, dolomit, jips ve anhidrit örnekleri.",
        "see_en": "Specimens for calcite, dolomite, gypsum, and anhydrite.",
        "does_tr": "Kabarcık karbonat kutusunda belirir.",
        "does_en": "A bubble appears in a carbonate box.",
        "why_tr": "Jips ve anhidrit evaporittir. Reaktif tarifi yoktur.",
        "why_en": "Gypsum and anhydrite are evaporites. There is no reagent recipe.",
    },
}

PETROL = QColor("#0B5964")

# Hotspots are fractions of the stage: x, y, w, h.
ANIMATIONS = {
    "auto": {
        "scenes": (
            {
                "title_tr": "Örnek kabı",
                "title_en": "Sample cup",
                "caption_tr": "Katı örnek kapta durur. Kütle bu çizimde yoktur.",
                "caption_en": "The solid sample sits in the cup. Mass is not on this drawing.",
                "visual": "auto_cup",
                "parts": (
                    ("cup", 0.28, 0.42, 0.44, 0.36, "Örnek kabı katıyı tutar. Hacim yazılmaz.", "The sample cup holds the solid. No volume is written."),
                ),
            },
            {
                "title_tr": "Kapalı hücre",
                "title_en": "Closed cell",
                "caption_tr": "Asit girişi modele aittir. Derişim ve tuş adı yoktur.",
                "caption_en": "The acid inlet belongs to the model. There is no strength and no key name.",
                "visual": "auto_cell",
                "parts": (
                    ("cell", 0.18, 0.28, 0.40, 0.48, "Kapalı hücre gazı içeride tutar.", "The closed cell keeps the gas inside."),
                    ("inlet", 0.62, 0.22, 0.24, 0.22, "Asit girişi. Veriliş yolu kılavuzdadır.", "Acid inlet. How it is added is in the manual."),
                ),
            },
            {
                "title_tr": "Algılayıcı",
                "title_en": "Sensor",
                "caption_tr": "Ekran boştur. Bu canlandırma sayı üretmez.",
                "caption_en": "The display is blank. This animation produces no number.",
                "visual": "auto_sensor",
                "parts": (
                    ("sensor", 0.16, 0.34, 0.28, 0.32, "Algılayıcı basınç veya hacim etkisini okur.", "The sensor reads a pressure or volume effect."),
                    ("screen", 0.52, 0.30, 0.32, 0.28, "Ekran cihazın kendi dönüşümünü gösterir. Burada boş bırakıldı.", "The display shows the instrument's own conversion. It is left blank here."),
                ),
            },
        )
    },
    "bernard": {
        "scenes": (
            {
                "title_tr": "Düzenek",
                "title_en": "Rig",
                "caption_tr": "Parçalar şematiktir. Parça numarası yoktur.",
                "caption_en": "The parts are schematic. There is no part number.",
                "visual": "bernard_rig",
                "parts": (
                    ("sample", 0.06, 0.46, 0.22, 0.36, "Örnek kabı katıyı tutar.", "The sample vessel holds the solid."),
                    ("acid", 0.30, 0.18, 0.18, 0.28, "Asit kabı tepkime sıvısını tutar. Derişim yazılmaz.", "The acid vessel holds the reaction liquid. Strength is not written."),
                    ("tube", 0.50, 0.40, 0.16, 0.16, "Bağlantı borusu gazı taşır.", "The connecting tube carries the gas."),
                    ("burette", 0.68, 0.16, 0.12, 0.66, "Ölçüm borusu sıvı seviyesini gösterir. Ham çizgi yüzde değildir.", "The measuring tube shows the liquid level. A raw line is not a percent."),
                ),
            },
            {
                "title_tr": "Gazın yeri",
                "title_en": "Where the gas goes",
                "caption_tr": "Gaz ölçüm borusuna gider. Hacim sayısı çizilmez.",
                "caption_en": "Gas goes to the measuring tube. No volume number is drawn.",
                "visual": "bernard_gas",
                "parts": (
                    ("gas", 0.62, 0.20, 0.22, 0.50, "Gaz kabarcığı şematiktir. Mililitre yazılmaz.", "The gas bubble is schematic. Millilitres are not written."),
                ),
            },
        )
    },
    "water": {
        "scenes": (
            {
                "title_tr": "Üç ayrı işlem",
                "title_en": "Three separate processes",
                "caption_tr": "Distilasyon, deiyonizasyon ve ters ozmoz aynı cihaz değildir.",
                "caption_en": "Distillation, deionization, and reverse osmosis are not the same instrument.",
                "visual": "water_three",
                "parts": (
                    ("still", 0.06, 0.28, 0.26, 0.44, "Distilasyon buharlaştırıp yoğunlaştırır.", "Distillation evaporates and condenses."),
                    ("di", 0.37, 0.28, 0.26, 0.44, "Deiyonizasyon iyon tutar. Organik maddeyi tek başına giderdiği söylenemez.", "Deionization holds ions. It cannot be said to remove organic matter by itself."),
                    ("ro", 0.68, 0.28, 0.26, 0.44, "Ters ozmoz zardan geçirir. Tutma oranı üreticidedir.", "Reverse osmosis passes water through a membrane. The rejection rate is the manufacturer's."),
                ),
            },
            {
                "title_tr": "Akış",
                "title_en": "Flow",
                "caption_tr": "Besleme kabı, işlem kolonu ve ürün kabı ayrıdır. Vana adı yoktur.",
                "caption_en": "A feed vessel, a process column, and a product vessel stay apart. There is no valve name.",
                "visual": "water_flow",
                "parts": (
                    ("feed", 0.06, 0.36, 0.22, 0.28, "Besleme suyu. Kalite sınırı yöntemdedir.", "Feed water. The quality limit is in the method."),
                    ("process", 0.38, 0.36, 0.24, 0.28, "İşlem kolonu üç yöntemden birini temsil eder.", "The process column stands for one of the three methods."),
                    ("product", 0.72, 0.36, 0.22, 0.28, "Ürün suyu. İletkenlik bütün saflığı göstermez.", "Product water. Conductivity does not show all purity."),
                ),
            },
        )
    },
    "acid": {
        "scenes": (
            {
                "title_tr": "KKD",
                "title_en": "PPE",
                "caption_tr": "Siper, sıçrama gözlüğünün yerine geçmez.",
                "caption_en": "A shield does not replace splash goggles.",
                "visual": "acid_ppe",
                "parts": (
                    ("goggles", 0.08, 0.32, 0.24, 0.36, "Sıçrama gözlüğü. Delikli darbe gözlüğü diye bir ürün seçilmez.", "Splash goggles. A vented impact goggle is not selected as the product."),
                    ("shield", 0.38, 0.32, 0.24, 0.36, "Yüz siperi ek korumadır. Gözlüğün yerine geçmez.", "A face shield is extra protection. It does not replace goggles."),
                    ("glove", 0.68, 0.32, 0.24, 0.36, "Eldiven malzemesi SDS'den kontrol edilir.", "Glove material is checked in the SDS."),
                ),
            },
            {
                "title_tr": "Sıra",
                "title_en": "Order",
                "caption_tr": "Su önce kapta. Asit suya gider. Miktar yoktur.",
                "caption_en": "Water is in the vessel first. Acid goes into the water. There is no amount.",
                "visual": "acid_order",
                "parts": (
                    ("water", 0.16, 0.34, 0.34, 0.46, "Su uygun kabın içindedir. Kap ölçüsü yazılmaz.", "Water is inside a suitable vessel. Vessel size is not written."),
                    ("acid", 0.58, 0.22, 0.26, 0.30, "Asit ayrı kaptadır ve suya eklenir. Suyun asidin üzerine döküldüğü sahne yoktur.", "Acid is in a separate vessel and is added to the water. There is no scene of water poured onto the acid."),
                ),
            },
        )
    },
    "collect": {
        "scenes": (
            {
                "title_tr": "Sarsıntı",
                "title_en": "Shaker",
                "caption_tr": "Kırıntı sarsıntıya gelir. Aralık yazılmaz.",
                "caption_en": "Cuttings arrive at the shaker. No interval is written.",
                "visual": "collect_shaker",
                "parts": (
                    ("shaker", 0.08, 0.34, 0.36, 0.32, "Sarsıntı kırıntıyı çamurdan ayırır.", "The shaker separates cuttings from mud."),
                    ("scoop", 0.56, 0.36, 0.28, 0.28, "Kürek temiz olmalıdır. Derinlik karışır.", "The scoop must be clean. Depths get mixed."),
                ),
            },
        )
    },
    "wash": {
        "scenes": (
            {
                "title_tr": "Elek",
                "title_en": "Sieve",
                "caption_tr": "Su yumuşaktır. Gözenek müşteriye aittir.",
                "caption_en": "The water is gentle. The mesh belongs to the customer.",
                "visual": "wash_stack",
                "parts": (
                    ("coarse", 0.12, 0.22, 0.30, 0.22, "Kaba artık. Eğitim notu bunu kavings sayar. Her saha için kural değildir.", "Coarse residue. The training note treats it as cavings. It is not every site's rule."),
                    ("fine", 0.12, 0.52, 0.30, 0.22, "İnce elek tarif ve kalsimetri tozu için tutulur.", "The fine sieve is kept for the description and for calcimetry powder."),
                    ("water", 0.56, 0.30, 0.28, 0.28, "Yumuşak su. Jips ve kil sert jetle dağılır.", "A gentle stream. Gypsum and clay break up under a hard jet."),
                ),
            },
        )
    },
    "dry": {
        "scenes": (
            {
                "title_tr": "Tepsi",
                "title_en": "Tray",
                "caption_tr": "Örnek yayılır. Fırın derecesi yoktur.",
                "caption_en": "The sample is spread. There is no oven setpoint.",
                "visual": "dry_tray",
                "parts": (
                    ("tray", 0.10, 0.40, 0.36, 0.24, "Metal tepsi. Yığın halinde kurutma içi ıslak bırakır.", "A metal tray. Drying in a pile leaves the inside wet."),
                    ("oven", 0.56, 0.28, 0.30, 0.40, "Fırın kurutur. Pişirmek örneği değiştirir.", "The oven dries. Cooking changes the sample."),
                ),
            },
        )
    },
    "label": {
        "scenes": (
            {
                "title_tr": "Torba",
                "title_en": "Bag",
                "caption_tr": "Etikette operatör, kuyu, derinlik ve birim vardır.",
                "caption_en": "The label has the operator, the well, the depth, and the unit.",
                "visual": "label_bag",
                "parts": (
                    ("bag", 0.12, 0.30, 0.32, 0.40, "Torba türü yıkanmamış, yaş veya kuru diye ayrılır.", "The bag is separated as unwashed, wet, or dry."),
                    ("pen", 0.56, 0.34, 0.28, 0.28, "Silinmeyen yazı. Birim metre veya fit olarak yazılır.", "A mark that stays. The unit is written as metres or feet."),
                ),
            },
        )
    },
    "look": {
        "scenes": (
            {
                "title_tr": "Islak tane",
                "title_en": "Wet grain",
                "caption_tr": "Doğal ışık. Marka mikroskop yoktur.",
                "caption_en": "Natural light. There is no brand of microscope.",
                "visual": "look_grain",
                "parts": (
                    ("grain", 0.14, 0.36, 0.28, 0.28, "Islak tane. Renk tek başına ad koymaz.", "A wet grain. Colour alone does not assign the name."),
                    ("light", 0.54, 0.24, 0.28, 0.22, "Doğal ışık. Yansıma rengi kaydırır.", "Natural light. Reflection shifts the colour."),
                ),
            },
        )
    },
    "fluor": {
        "scenes": (
            {
                "title_tr": "Doğrudan bakış",
                "title_en": "Direct view",
                "caption_tr": "Önce yıkanmamış kırıntı. Lamba modeli yoktur.",
                "caption_en": "Unwashed cuttings first. There is no lamp model.",
                "visual": "fluor_dish",
                "parts": (
                    ("lamp", 0.14, 0.18, 0.28, 0.24, "UV lamba. Dalga boyu bu çizimde yoktur.", "A UV lamp. A wavelength is not on this drawing."),
                    ("dish", 0.52, 0.40, 0.32, 0.28, "Kap. Parlama tek başına kesin kanıt değildir.", "The dish. A glow is not definite proof by itself."),
                ),
            },
            {
                "title_tr": "Çözücü lekesi",
                "title_en": "Solvent mark",
                "caption_tr": "Halka şematiktir. Çözücü miktarı yazılmaz.",
                "caption_en": "The ring is schematic. No solvent amount is written.",
                "visual": "fluor_cut",
                "parts": (
                    ("paper", 0.28, 0.28, 0.44, 0.44, "Kâğıt üzerindeki halka bir gözlemdir. Çözücü SDS ile kontrol edilir.", "A ring on paper is an observation. The solvent is checked with the SDS."),
                ),
            },
        )
    },
    "sheet": {
        "scenes": (
            {
                "title_tr": "İki okuma",
                "title_en": "Two readings",
                "caption_tr": "Erken ve geç sütun. Dakika yazılmaz.",
                "caption_en": "An early and a late column. No minute is written.",
                "visual": "sheet_cols",
                "parts": (
                    ("early", 0.08, 0.32, 0.24, 0.36, "Erken okuma hızlı karbonata daha yakındır.", "The early reading is closer to a fast carbonate."),
                    ("late", 0.38, 0.32, 0.24, 0.36, "Geç okuma yavaş tepkiyi de alır. Katsayı çarpılmaz.", "The late reading also takes a slow reaction. No factor is multiplied."),
                    ("rest", 0.68, 0.32, 0.24, 0.36, "Artık, asidin çözmediği tanedir.", "Residue is the grain the acid does not dissolve."),
                ),
            },
        )
    },
    "minerals": {
        "scenes": (
            {
                "title_tr": "Dört aile üyesi",
                "title_en": "Four family members",
                "caption_tr": "Kabarcık yalnızca karbonat örneğinde belirir.",
                "caption_en": "A bubble appears only on a carbonate specimen.",
                "visual": "mineral_four",
                "parts": (
                    ("calcite", 0.06, 0.28, 0.20, 0.40, "Kalsit karbonattır. Renk tanı koymaz.", "Calcite is a carbonate. Colour does not identify it."),
                    ("dolomite", 0.30, 0.28, 0.20, 0.40, "Dolomit karbonattır. Zayıf kabarcık kanıt değildir.", "Dolomite is a carbonate. A weak bubble is not proof."),
                    ("gypsum", 0.54, 0.28, 0.18, 0.40, "Jips evaporittir ve yıkamada dağılır.", "Gypsum is an evaporite and breaks up in washing."),
                    ("anhydrite", 0.76, 0.28, 0.18, 0.40, "Anhidrit evaporittir. Ayırma tarifi yoktur.", "Anhydrite is an evaporite. There is no separation recipe."),
                ),
            },
        )
    },
}


class Stage(QWidget):
    def __init__(self, player: "ScenePlayer"):
        super().__init__()
        self.player = player
        self.setMinimumSize(560, 280)
        self.setMaximumHeight(360)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.width() and self.height():
            self.player.click_fraction(event.position().x() / self.width(), event.position().y() / self.height())
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#F7FBFA"))
        painter.setPen(QPen(PETROL, 3))
        painter.setBrush(QColor("#FFFFFF"))
        frame = QRectF(8, 8, self.width() - 16, self.height() - 16)
        painter.drawRoundedRect(frame, 16, 16)
        scene = self.player.current()
        if scene is not None:
            _draw(painter, frame, scene["visual"], self.player.progress(), self.player.lang)
        painter.end()


class ScenePlayer(QWidget):
    def __init__(self, animation_id: str):
        super().__init__()
        self.animation_id = animation_id
        self.lang = "tr"
        self.index = 0
        self.elapsed = 0
        self.playing = False
        self.selected_part = ""
        pack = ANIMATIONS[animation_id]
        self.scenes = pack["scenes"]
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._tick)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.banner = QLabel()
        self.banner.setWordWrap(True)
        self.banner.setObjectName("Warning")
        layout.addWidget(self.banner)
        self.stage = Stage(self)
        layout.addWidget(self.stage)
        self.caption = QLabel()
        self.caption.setWordWrap(True)
        self.caption.setObjectName("CaptionChip")
        self.caption.setStyleSheet("font-size:16px; font-weight:650;")
        layout.addWidget(self.caption)
        controls = QHBoxLayout()
        self.play_button = QPushButton()
        self.play_button.setObjectName("Primary")
        self.play_button.clicked.connect(self.play)
        self.pause_button = QPushButton()
        self.pause_button.clicked.connect(self.pause)
        self.restart_button = QPushButton()
        self.restart_button.clicked.connect(self.restart)
        self.prev_button = QPushButton()
        self.prev_button.clicked.connect(self.show_previous)
        self.next_button = QPushButton()
        self.next_button.clicked.connect(self.show_next)
        for button in (self.prev_button, self.play_button, self.pause_button, self.restart_button, self.next_button):
            controls.addWidget(button)
        controls.addStretch()
        layout.addLayout(controls)
        self.part_label = QLabel()
        self.part_label.setWordWrap(True)
        self.part_label.setObjectName("Muted")
        layout.addWidget(self.part_label)
        self.see_label = QLabel()
        self.does_label = QLabel()
        self.why_label = QLabel()
        for label in (self.see_label, self.does_label, self.why_label):
            label.setWordWrap(True)
            layout.addWidget(label)
        speech_row = QHBoxLayout()
        self.listen_button = QPushButton()
        self.listen_button.clicked.connect(self.speak_step)
        self.speech_status = QLabel()
        self.speech_status.setWordWrap(True)
        self.speech_status.setObjectName("Muted")
        speech_row.addWidget(self.listen_button)
        speech_row.addWidget(self.speech_status, 1)
        layout.addLayout(speech_row)
        self.narrator = Narrator()
        self._spoken_index = -1
        self.retranslate("tr")

    def current(self) -> dict | None:
        if not self.scenes:
            return None
        return self.scenes[self.index]

    def progress(self) -> float:
        return max(0.0, min(1.0, self.elapsed / 4000))

    def play(self) -> None:
        self.playing = True
        self.timer.start()

    def pause(self) -> None:
        self.playing = False
        self.timer.stop()

    def restart(self) -> None:
        self.index = 0
        self.elapsed = 0
        self.selected_part = ""
        self._refresh()
        self.play()

    def show_previous(self) -> None:
        self.pause()
        self.index = max(0, self.index - 1)
        self.elapsed = 0
        self._refresh()

    def show_next(self) -> None:
        self.pause()
        self.index = min(len(self.scenes) - 1, self.index + 1)
        self.elapsed = 0
        self._refresh()

    def click_fraction(self, fx: float, fy: float) -> None:
        scene = self.current()
        if scene is None:
            return
        for part in scene["parts"]:
            _key, x, y, w, h, _tr, _en = part
            if x <= fx <= x + w and y <= fy <= y + h:
                self.selected_part = part[0]
                self._refresh()
                return

    def _tick(self) -> None:
        if not self.playing:
            return
        self.elapsed += self.timer.interval()
        if self.elapsed >= 4000 and self.index < len(self.scenes) - 1:
            self.index += 1
            self.elapsed = 0
        elif self.elapsed >= 4000:
            self.pause()
        self._refresh()

    def retranslate(self, lang: str) -> None:
        self.lang = lang
        self.play_button.setText(t("train_play", lang))
        self.pause_button.setText(t("train_pause", lang))
        self.restart_button.setText(t("train_restart", lang))
        self.prev_button.setText(t("train_prev", lang))
        self.next_button.setText(t("train_next", lang))
        self.listen_button.setText(t("listen", lang))
        self.banner.setText(t("mud_schematic", lang))
        self._refresh()

    def speak_step(self) -> None:
        self.speech_status.setText(t(self.narrator.speak(self.step_speech()), self.lang))

    def step_speech(self) -> str:
        scene = self.current()
        if scene is None:
            return ""
        step = STEPS.get(scene["visual"], {})
        suffix = "en" if self.lang == "en" else "tr"
        return " ".join(
            part
            for part in (
                step.get(f"see_{suffix}", ""),
                step.get(f"does_{suffix}", ""),
                step.get(f"why_{suffix}", ""),
            )
            if part
        )

    def _refresh(self) -> None:
        scene = self.current()
        if scene is None:
            return
        self.caption.setText(scene["caption_en"] if self.lang == "en" else scene["caption_tr"])
        text = t("mud_part", self.lang) + ": "
        if self.selected_part:
            for part in scene["parts"]:
                if part[0] == self.selected_part:
                    text += part[6] if self.lang == "en" else part[5]
                    break
        else:
            text += "—"
        self.part_label.setText(text)
        step = STEPS.get(scene["visual"], {})
        suffix = "en" if self.lang == "en" else "tr"
        self.see_label.setText(t("see_q", self.lang) + " " + step.get(f"see_{suffix}", scene["caption_en" if suffix == "en" else "caption_tr"]))
        self.does_label.setText(t("does_q", self.lang) + " " + step.get(f"does_{suffix}", ""))
        self.why_label.setText(t("why_q", self.lang) + " " + step.get(f"why_{suffix}", ""))
        if self._spoken_index != self.index:
            self.narrator.stop()
            self._spoken_index = self.index
        self.stage.update()


def _draw(painter: QPainter, frame: QRectF, visual: str, progress: float, lang: str) -> None:
    paint_scene(painter, frame, visual, progress, lang)
