"""Original lesson notes grounded in the Geolog mud-logger handbook.

The handbook is confidential and is not copied. No page image, figure, reagent
amount, or acid strength from that document is stored here.
"""

from __future__ import annotations

from app.academy_content import _lesson

LIMIT = (
    "Kaynak: GEOLOG Mud Logger Handbook, belge G-61-003-VAR-20, Rev. 01.00, 2020. "
    "Belge GEOLOG mülkiyetindedir, dahili kullanım içindir ve dağıtılmaz. "
    "Bu kart özgün bir özettir. Sayfa metni ve şekiller kopyalanmadı."
)
LIMIT_EN = (
    "Source: GEOLOG Mud Logger Handbook, document G-61-003-VAR-20, Rev. 01.00, 2020. "
    "The document is GEOLOG property, for internal use, and is not for distribution. "
    "This card is an original summary. Page text and figures were not copied."
)

NOT_IN_BOOK = (
    "Bu konu GEOLOG Mud Logger Handbook içinde bir test yöntemi olarak yok. "
    "Kart başka bir genel dersten duruyor. El kitabına aitmiş gibi okunmasın. " + LIMIT
)
NOT_IN_BOOK_EN = (
    "This topic is not a test method in the GEOLOG Mud Logger Handbook. "
    "The card remains a separate general lesson. Do not read it as part of that handbook. " + LIMIT_EN
)


def _src(page_tr: str, page_en: str) -> tuple[str, str]:
    return (page_tr + " " + LIMIT, page_en + " " + LIMIT_EN)


NOTES = {
    "bernard": _src(
        "Modül 5, s. 27. Gaz hacmi ile karbonat ilişkisi özetlendi. Operatör örneğindeki asit derişimi, kütle ve dakika bu karta yazılmadı.",
        "Module 5, p. 27. The gas-volume and carbonate relationship is summarized. The operator example's acid strength, mass, and minutes are not written on this card.",
    ),
    "auto-calcimeter": _src(
        "Modül 5, s. 28. Sabit hacimli hücre ve basınç-zaman ilkesi özetlendi. Marka tuşu, doğruluk iddiası ve dolomit katsayısı hesap olarak kullanılmadı.",
        "Module 5, p. 28. The constant-volume cell and the pressure-time idea are summarized. A brand key, an accuracy claim, and a dolomite factor are not used as a calculation.",
    ),
    "uv": _src(
        "Modül 4, s. 22–24. Doğrudan floresansın sınırı özetlendi. Dalga boyu tablosu kopyalanmadı.",
        "Module 4, pp. 22–24. The limit of direct fluorescence is summarized. The wavelength table was not copied.",
    ),
    "solvent-cut": _src(
        "Modül 4, s. 24. Çözücü lekesinin ayrı bir gözlem olduğu özetlendi. Çözücü adı ve miktarı yazılmadı.",
        "Module 4, p. 24. A solvent mark is summarized as a separate observation. The solvent name and amount are not written.",
    ),
    "calcite": _src(
        "Modül 1, s. 4 ve Modül 3, s. 15–16. Kalsit karbonat ailesinde anılır. Tanı kartı sayfa kopyası değildir.",
        "Module 1, p. 4 and Module 3, pp. 15–16. Calcite is named in the carbonate family. The recognition card is not a page copy.",
    ),
    "dolomite": _src(
        "Modül 1, s. 4 ve Modül 5, s. 28. Dolomit karbonat olarak anılır. Erken ve geç okuma farkının katsayısı bu uygulamada hesaplanmaz.",
        "Module 1, p. 4 and Module 5, p. 28. Dolomite is named as a carbonate. The factor on an early and a late reading is not calculated here.",
    ),
    "gypsum": _src(
        "Modül 1, s. 4 ve Modül 2, s. 8. Jips evaporit olarak anılır ve yıkamada kolay dağılır. Ayırma reaktifi yazılmamıştır.",
        "Module 1, p. 4 and Module 2, p. 8. Gypsum is named as an evaporite and breaks up easily in washing. No separating reagent is written.",
    ),
    "anhydrite": _src(
        "Modül 1, s. 4. Anhidrit evaporit ailesinde sayılır. El kitabı bir kimyasal ayırma tarifi vermez.",
        "Module 1, p. 4. Anhydrite is counted in the evaporite family. The handbook does not give a chemical separation recipe.",
    ),
    "phenol": (NOT_IN_BOOK, NOT_IN_BOOK_EN),
    "alizarin": (NOT_IN_BOOK, NOT_IN_BOOK_EN),
    "chloride": (NOT_IN_BOOK, NOT_IN_BOOK_EN),
    "acetone-test": (NOT_IN_BOOK, NOT_IN_BOOK_EN),
    "sulfate": _src(
        "s. 105 yalnızca çamur logger görevleri arasında sülfat testini sayar. Yöntem, reaktif ve gözlem yazılmamıştır. Aşağıdaki genel ilke bu belgeden kopyalanmadı.",
        "p. 105 only names a sulphate test among mud-logger duties. No method, reagent, or observation is written. The general note below was not copied from that document.",
    ),
}


def annotate(lessons: list[dict]) -> list[dict]:
    for lesson in lessons:
        note = NOTES.get(lesson["id"])
        if note is None:
            continue
        lesson["source_tr"], lesson["source_en"] = note
        lesson["sections"].append(
            {
                "title_tr": "Kaynak ve doğrulama",
                "title_en": "Source and check",
                "body_tr": note[0],
                "body_en": note[1],
            }
        )
    return lessons


def extra_lessons() -> list[dict]:
    rows = [
        _lesson(
            "sample-collect",
            ("samples",),
            "collect",
            "Numune toplama",
            "Sample collection",
            "Kırıntı, çamurla yüzeye gelen kaya parçasıdır. Aralık ve hacim operatöre aittir.",
            "Cuttings are rock pieces brought up by the mud. The interval and the volume belong to the operator.",
            (
                (
                    "Ne toplanır",
                    "What is collected",
                    "Matkap kayayı parçalar. Çamur bu parçaları elekli sarsıntıya taşır. Dip karotu ve yan karot başka aletlerle alınır. Bu kart onların tarifini vermez.",
                    "The bit breaks the rock. Mud carries those pieces to the shaker. A bottom core and a sidewall core use other tools. This card does not describe them.",
                ),
                (
                    "Ne zaman",
                    "When",
                    "Örnek, hesaplanmış lag süresine göre alınır. Metraj aralığını petrol şirketi verir. Aralık bu kartta sabitlenmez.",
                    "The sample is taken against a calculated lag. The oil company sets the depth interval. This card does not fix that interval.",
                ),
                (
                    "Temiz alet",
                    "Clean tools",
                    "Sarsıntının birkaç katından, yıkanmış kova ve yıkanmış bir kürekle alınır. Alet kirliyse bir önceki derinlik yeni örneğe karışır.",
                    "Take it from the shaker levels with a washed bucket and a washed scoop. A dirty tool mixes the previous depth into the new sample.",
                ),
                (
                    "Takımlar",
                    "Sets",
                    "Eğitim notu yıkanmamış referansı, yıkanmış yaş örneği, yıkanmış kuru örneği ve kapalı bir jeokimya şişesini ayrı tutar. Şişenin doluluk payı ve eklenecek çözelti buraya yazılmadı.",
                    "The training note keeps an unwashed reference, a washed wet sample, a washed dry sample, and a sealed geochemistry vial apart. The vial fill and any added solution are not written here.",
                ),
                (
                    "Kaynak ve doğrulama",
                    "Source and check",
                    NOTES_COLLECT[0],
                    NOTES_COLLECT[1],
                ),
            ),
        ),
        _lesson(
            "sample-wash",
            ("samples",),
            "wash",
            "Numune yıkama ve eleme",
            "Washing and sieving",
            "Elek dizisi çamuru ayırır. Gözenek müşteriye aittir. Kaba artık kavings sayılabilir.",
            "A sieve stack separates mud. The mesh belongs to the customer. Coarse residue can be cavings.",
            (
                (
                    "İlke",
                    "Principle",
                    "Önce müşterinin elek listesi kullanılır. Liste yoksa eğitim notu, kabadan inceye bir yedek dizi önerir. Milimetre listesi bu karta kopyalanmadı.",
                    "Use the customer's sieve list first. If there is no list, the training note offers a coarse-to-fine fallback. The millimetre list was not copied onto this card.",
                ),
                (
                    "Su bazlı çamur",
                    "Water-based mud",
                    "Elekler lavaboda, parmak yardımıyla yumuşak suyla yıkanır. Tebeşir, kil ve jips gibi dağılgan kayaçta sert su jeti örneği eksiltir.",
                    "Sieves are washed in a sink with a gentle stream, helped by the fingers. On a fragile rock such as chalk, clay, or gypsum, a hard jet loses sample.",
                ),
                (
                    "Kayıp",
                    "Loss",
                    "Yıkanmadan önceki hacim ile yıkanmış artık karşılaştırılır. Fark, yıkamada giden ince taneyi gösterir. Hacim kabı bu çizimde yoktur.",
                    "The volume before washing is compared with the washed residue. The difference shows fines lost in washing. No measuring vessel is on this drawing.",
                ),
                (
                    "Kaba elek",
                    "Coarse sieve",
                    "Eğitim notu en kaba artığı sistemli olarak ayırır ve bunu kavings kabul eder. Bu, her sahanın kuralı diye sunulmaz. Müşteri başka diyorsa o geçerlidir.",
                    "The training note sets the coarsest residue aside and treats it as cavings. That is not offered as every field's rule. If the customer says otherwise, that instruction stands.",
                ),
                (
                    "Yağ bazlı çamur",
                    "Oil-based mud",
                    "Yağ bazlı temizleme ayrı bir iştir. Deterjan oranı ve motorin banyosu bu kartta yoktur. Çözücü yanıcıdır. SDS ve iş prosedürü gerekir.",
                    "Oil-mud cleaning is a separate job. A detergent ratio and a diesel bath are not on this card. Solvent is flammable. The SDS and the work procedure are required.",
                ),
                (
                    "Kaynak ve doğrulama",
                    "Source and check",
                    NOTES_WASH[0],
                    NOTES_WASH[1],
                ),
            ),
        ),
        _lesson(
            "sample-dry",
            ("samples",),
            "dry",
            "Numune kurutma",
            "Sample drying",
            "Kırıntı tepside yayılır ve fırında yavaş kurur. Pişirmek örneği değiştirir.",
            "Cuttings are spread on a tray and dry slowly in an oven. Cooking changes the sample.",
        (
                (
                    "Nasıl",
                    "How",
                    "Yıkanmış kırıntı metal bir tepsiye ince yayılır. Eğitim notu tepsiyi kurutma fırınında tutar ve örneği pişirmemeyi söyler. Fırın derecesi bu notta yoktur, uydurulmaz.",
                    "Washed cuttings are spread thinly on a metal tray. The training note keeps the tray in a drying oven and says not to cook the sample. An oven setpoint is not in that note and is not invented.",
                ),
                (
                    "Neden",
                    "Why",
                    "Islak yüzey rengi, kokuyu ve floresansı değiştirir. Aşırı ısı da organik göstergeyi ve bazı mineralleri bozar.",
                    "A wet surface changes colour, odour, and fluorescence. Too much heat also spoils an organic show and some minerals.",
                ),
                (
                    "Kaynak ve doğrulama",
                    "Source and check",
                    NOTES_DRY[0],
                    NOTES_DRY[1],
                ),
            ),
        ),
        _lesson(
            "sample-label",
            ("samples",),
            "label",
            "Etiket ve paketleme",
            "Labels and packing",
            "Torba; operatörü, kuyuyu, ölçülmüş derinliği ve birimi taşır.",
            "A bag carries the operator, the well, the measured depth, and the unit.",
            (
                (
                    "Etiket",
                    "Label",
                    "Silinmeyen kalem kullanılır. Operatör, kuyu, ölçülmüş derinlik ve birim okunur. Aynı bilgi her kutuda aynı satırda durur.",
                    "Use a mark that does not wash off. Operator, well, measured depth, and unit stay readable. The same fact sits on the same line of every box.",
                ),
                (
                    "Ayrım",
                    "Separation",
                    "Yıkanmamış, yıkanmış yaş ve yıkanmış kuru torbalar karıştırılmaz. Büyük ve küçük torba ölçüsü eğitim notunda örnektir, bu karta aktarılmadı.",
                    "Unwashed, washed wet, and washed dry bags are not mixed. Large and small bag sizes in the training note are an example and were not copied here.",
                ),
                (
                    "Sevkiyat",
                    "Dispatch",
                    "Kutu ve sevkiyat müşteri talimatınadır. Manifestonun imzalı bir kopyası birimde kalır. Adres ve kutu sayısı uydurulmaz.",
                    "The box and the dispatch follow the customer. A signed copy of the manifest stays in the unit. An address and a box count are not invented.",
                ),
                (
                    "Kaynak ve doğrulama",
                    "Source and check",
                    NOTES_LABEL[0],
                    NOTES_LABEL[1],
                ),
            ),
        ),
        _lesson(
            "sample-look",
            ("samples", "rocks"),
            "look",
            "Görsel ve mineralojik inceleme",
            "Visual and mineral examination",
            "Islak kırıntı, doğal ışıkta ve yansıma kontrol edilerek tarif edilir.",
            "Wet cuttings are described in natural light, with reflections checked.",
            (
                (
                    "Sıra",
                    "Order",
                    "Eğitim notunun tarifi şunları ister: kaya adı ve bolluk, renk, sertlik, doku, matris ve çimento, tane ve fosil, görünen gözenek, petrol emaresi.",
                    "The training note's description asks for rock name and abundance, colour, hardness, texture, matrix and cement, grains and fossils, apparent porosity, and an oil show.",
                ),
                (
                    "Işık",
                    "Light",
                    "Renk, ıslak örnekte ve doğal ışıkta bakılır. Yansıma rengi kaydırır. Renk tek başına ad koymaz.",
                    "Colour is judged on a wet sample in natural light. Reflection shifts the colour. Colour alone does not assign the name.",
                ),
                (
                    "Büyüteç",
                    "Magnification",
                    "Modül bir mikroskop markası vermez. Sahanın büyüteci veya mikroskobu kullanılır. Modelin ayarı burada yoktur.",
                    "The module names no microscope brand. Use the site lens or microscope. That model's settings are not here.",
                ),
                (
                    "Gözenek",
                    "Porosity",
                    "Kırıntıda gözenek niteliklidir ve yumuşak örnekte zordur. Eğitim notundaki yüzde bantları bu karta kopyalanmadı.",
                    "Porosity on cuttings is qualitative and is hard on a soft sample. The percent bands in the training note were not copied onto this card.",
                ),
                (
                    "Kaynak ve doğrulama",
                    "Source and check",
                    NOTES_LOOK[0],
                    NOTES_LOOK[1],
                ),
            ),
        ),
        _lesson(
            "fluor-direct",
            ("shows", "samples"),
            "fluor",
            "Doğrudan floresans",
            "Direct fluorescence",
            "Yıkanmamış kırıntı önce koklanır, sonra UV altında bakılır. Parlama tek başına kanıt değildir.",
            "Unwashed cuttings are smelled first, then viewed under UV. A glow is not proof by itself.",
            (
                (
                    "Sıra",
                    "Order",
                    "Başka işten önce koku ve floroskop gelir. Önce yıkanmamış kırıntı, sonra yıkanmış kırıntı bakılır. Lamba modeli bu kartta yoktur.",
                    "Odour and the fluoroscope come before other work. Unwashed cuttings are viewed first, then washed cuttings. A lamp model is not on this card.",
                ),
                (
                    "Sınır",
                    "Limit",
                    "Çok hafif petrol, kondensat ve ağır katran doğrudan parlama vermeyebilir. Parlama olmaması hidrokarbon yoktur demek değildir. Parlama da tek başına kesin kanıt değildir.",
                    "A very light oil, a condensate, and a heavy tar may give no direct glow. No glow does not mean no hydrocarbon. A glow is not definite proof by itself.",
                ),
                (
                    "Karışıklık",
                    "Confusion",
                    "Çamur katkısı da parlayabilir. Birime varınca sahadaki çamur ürünleri kontrol edilir. Çamurdaki iz, jeoloğa ve çamur mühendisine bildirilir.",
                    "A mud additive can also glow. On arrival, mud products at the site are checked. A trace in the mud is reported to the geologist and the mud engineer.",
                ),
                (
                    "Neden solar",
                    "Why it fades",
                    "Sıvı hidrokarbon uçar. Çamur ağırlığı, çamur tipi, matkap, aşırı denge, yıkama ve tane boyu görülen emareyi değiştirir.",
                    "Liquid hydrocarbon evaporates. Mud weight, mud type, the bit, overbalance, washing, and grain size change the show that is seen.",
                ),
                (
                    "Kaynak ve doğrulama",
                    "Source and check",
                    NOTES_FLUOR[0],
                    NOTES_FLUOR[1],
                ),
            ),
        ),
        _lesson(
            "calc-sheet",
            ("devices", "measure"),
            "sheet",
            "Kalsimetri sonuç düzeni",
            "Calcimetry result layout",
            "Erken okuma, geç okuma, dolomit sütunu ve artık ayrı tutulur. Katsayı hesaplanmaz.",
            "An early reading, a late reading, a dolomite column, and residue stay apart. No factor is calculated.",
            (
                (
                    "Ne görülür",
                    "What is seen",
                    "Eğitim notundaki kırıntı formu erken bir karbonat sütunu, daha geç bir sütun, dolomit sütunu, artık ve floresans için yer ayırır. Dakikalar ve formun kendisi kopyalanmadı.",
                    "The cutting form in the training note leaves room for an early carbonate column, a later column, a dolomite column, residue, and fluorescence. The minutes and the form itself were not copied.",
                ),
                (
                    "Nasıl yorumlanır",
                    "How it is read",
                    "Erken okuma hızlı tepkiyen karbonata daha yakındır. Geç okuma yavaş tepkiyi de alır. İkisinin farkına eğitim notu bir katsayı uygular. Bu uygulama o katsayıyı çarpmaz.",
                    "An early reading is closer to a fast carbonate. A later reading also takes a slow reaction. The training note applies a factor to the difference. This application does not multiply by that factor.",
                ),
                (
                    "Artık",
                    "Residue",
                    "Asidin çözmediği tane kurutulup tartılabilir. Eğitim notu kuvars, pirit, mika, glokonit, demir oksit ve kili bu grupta sayar. Tartım bu çizimde yoktur.",
                    "Grains the acid does not dissolve can be dried and weighed. The training note counts quartz, pyrite, mica, glauconite, iron oxide, and clay in that group. No weighing is on this drawing.",
                ),
                (
                    "Kaynak ve doğrulama",
                    "Source and check",
                    NOTES_SHEET[0],
                    NOTES_SHEET[1],
                ),
            ),
        ),
        _lesson(
            "mineral-split",
            ("rocks", "samples"),
            "minerals",
            "Kalsit, dolomit, jips, anhidrit",
            "Calcite, dolomite, gypsum, anhydrite",
            "İlk ikisi karbonattır. Jips ve anhidrit evaporittir. Renk tanı koymaz.",
            "The first two are carbonates. Gypsum and anhydrite are evaporites. Colour does not identify them.",
            (
                (
                    "Aile",
                    "Family",
                    "Eğitim notu kireçtaşı ve dolotaşı karbonat, jips ve anhidriti evaporit sayar. Bu aile adı, tek bir tanenin kesin adı değildir.",
                    "The training note counts limestone and dolostone as carbonates, and gypsum and anhydrite as evaporites. A family name is not the certain name of one grain.",
                ),
                (
                    "Asit",
                    "Acid",
                    "Karbonat asitle gaz verebilir. Jips ve anhidrit bu gazın kaynağı olarak anlatılmaz. Kabarcık hızı tane boyuna bağlıdır ve tek başına dolomit kanıtı değildir.",
                    "Carbonate can release gas with acid. Gypsum and anhydrite are not described as the source of that gas. Bubble speed depends on grain size and is not proof of dolomite by itself.",
                ),
                (
                    "Yıkama",
                    "Washing",
                    "Jips, yıkamada tebeşir ve kil gibi dağılgan sayılır. Sert su jeti taneyi kaybettirir.",
                    "Gypsum is counted with chalk and clay as fragile in washing. A hard jet loses the grain.",
                ),
                (
                    "Ne yok",
                    "What is absent",
                    "El kitabı jips ile anhidriti ayıran bir reaktif tarifi vermez. Eski tehlikeli yöntemler bu karta yazılmaz.",
                    "The handbook does not give a reagent recipe that separates gypsum from anhydrite. Old hazardous methods are not written on this card.",
                ),
                (
                    "Kaynak ve doğrulama",
                    "Source and check",
                    NOTES_MIN[0],
                    NOTES_MIN[1],
                ),
            ),
        ),
    ]
    for lesson in rows:
        lesson["source_tr"] = lesson["sections"][-1]["body_tr"]
        lesson["source_en"] = lesson["sections"][-1]["body_en"]
    return rows


NOTES_COLLECT = _src(
    "Modül 2, s. 6–7. Toplama ilkesi özetlendi. Hacim, torba ölçüsü ve jeokimya şişesinin tarifi kopyalanmadı.",
    "Module 2, pp. 6–7. The collection idea is summarized. Volume, bag size, and the geochemistry-vial recipe were not copied.",
)
NOTES_WASH = _src(
    "Modül 2, s. 8. Yıkama ve eleme ilkesi özetlendi. Elek milimetreleri, deterjan oranı ve boya banyosu kopyalanmadı.",
    "Module 2, p. 8. Washing and sieving are summarized. Sieve millimetres, a detergent ratio, and a dye bath were not copied.",
)
NOTES_DRY = _src(
    "Modül 2, s. 7. Kurutma ilkesi özetlendi. Fırın derecesi belgede verilmediği için yazılmadı.",
    "Module 2, p. 7. Drying is summarized. An oven setpoint is not written because the document does not give one.",
)
NOTES_LABEL = _src(
    "Modül 2, s. 6–8. Etiket ve paket ilkesi özetlendi. Torba ölçüsü ve sevkiyat adresi kopyalanmadı.",
    "Module 2, pp. 6–8. Label and packing are summarized. Bag size and a dispatch address were not copied.",
)
NOTES_LOOK = _src(
    "Modül 3, s. 10–19. Görsel tarif listesi özetlendi. Renk kodları ve gözenek bantları kopyalanmadı.",
    "Module 3, pp. 10–19. The visual description list is summarized. Colour codes and porosity bands were not copied.",
)
NOTES_FLUOR = _src(
    "Modül 4, s. 22–24. Doğrudan floresans özetlendi. Dalga boyu tablosu ve şirket formları kopyalanmadı.",
    "Module 4, pp. 22–24. Direct fluorescence is summarized. The wavelength table and company forms were not copied.",
)
NOTES_SHEET = _src(
    "Modül 5, s. 28 ve s. 109. Sonuç düzeni özetlendi. Form, dakikalar ve dolomit katsayısı kopyalanmadı.",
    "Module 5, p. 28 and p. 109. The result layout is summarized. The form, the minutes, and the dolomite factor were not copied.",
)
NOTES_MIN = _src(
    "Modül 1, s. 4, Modül 2, s. 8 ve Modül 5. Dört mineralin aile ayrımı özetlendi. Şekil kopyalanmadı.",
    "Module 1, p. 4, Module 2, p. 8, and Module 5. The family split of the four minerals is summarized. No figure was copied.",
)
