"""Mudlogging Academy lessons.

These are general lessons. They are not manufacturer manuals, SDS documents,
or approved site procedures. Chemical-test text does not give a reagent
amount, concentration, or mixing recipe.
"""

from __future__ import annotations

CATEGORIES = (
    "devices",
    "tests",
    "rocks",
    "shows",
    "measure",
    "safety",
    "trouble",
    "samples",
)


def _lesson(
    lesson_id: str,
    categories: tuple[str, ...],
    animation: str | None,
    title_tr: str,
    title_en: str,
    summary_tr: str,
    summary_en: str,
    sections: tuple[tuple[str, str, str, str], ...],
) -> dict:
    return {
        "id": lesson_id,
        "categories": categories,
        "animation": animation,
        "title_tr": title_tr,
        "title_en": title_en,
        "summary_tr": summary_tr,
        "summary_en": summary_en,
        "sections": [
            {"title_tr": a, "title_en": b, "body_tr": c, "body_en": d}
            for a, b, c, d in sections
        ],
    }


LESSONS = (
    _lesson(
        "auto-calcimeter",
        ("devices",),
        "auto",
        "Otomatik kalsimetre",
        "Automatic calcimeter",
        "Kapalı hücrede karbonat tepkimesinden ölçüm okumanın genel mantığı.",
        "The general idea of reading a carbonate reaction inside a closed cell.",
        (
            (
                "Tanım",
                "Definition",
                "Otomatik kalsimetre, katı bir örneğin karbonat içeriği için gaz veya basınç okuması üreten bir laboratuvar cihazıdır. Bu kart bir markanın kılavuzu değildir.",
                "An automatic calcimeter is a laboratory instrument that produces a gas or pressure reading for the carbonate content of a solid sample. This card is not a brand manual.",
            ),
            (
                "Çalışma prensibi",
                "Principle",
                "Karbonatlı örnek asitle tepkimeye girince karbondioksit oluşur. Cihaz bu gazın kapalı hücredeki etkisini bir algılayıcıyla okur ve kendi yazılımındaki dönüşümle bir sonuç gösterir. Asidin derişimi ve veriliş yolu modele aittir; burada yoktur.",
                "When a carbonate sample reacts with acid, carbon dioxide forms. The instrument reads the effect of that gas in a closed cell and shows a result from its own conversion. Acid strength and the way it is added belong to the model and are not stated here.",
            ),
            (
                "Parçalar",
                "Parts",
                "Genel parçalar örnek kabı, kapalı hücre, asit girişi, algılayıcı ve ekrandır. Tuş adları ve menü yolları üreticiye göre değişir. Bu uygulamada uydurulmaz.",
                "General parts are a sample cup, a closed cell, an acid inlet, a sensor, and a display. Key names and menu paths differ by maker. They are not invented here.",
            ),
            (
                "Ölçüm mantığı",
                "Measurement logic",
                "Boş okuma, örnek okuması ve cihazın kendi dönüşümü ayrı adımlardır. Ekrandaki sayı, ancak kalibrasyon ve örnek hazırlığı kılavuzdaki gibi yapıldıysa o cihazın sonucudur. Bu canlandırma sayı üretmez.",
                "A blank reading, a sample reading, and the instrument's own conversion are separate steps. A number on the display is that instrument's result only when calibration and sample preparation follow its manual. This animation produces no number.",
            ),
            (
                "Sonuç yorumlama",
                "Interpretation",
                "Yüksek okuma daha çok karbonat anlamına gelebilir, ama mineral türünü tek başına ayırmaz. Kalsit ve dolomit aynı genel tepkimeyi verebilir. Kesin ayrım başka gözlem veya analiz ister.",
                "A higher reading can mean more carbonate, but it does not by itself separate mineral species. Calcite and dolomite can give the same general reaction. A firm separation needs other observations or analysis.",
            ),
            (
                "Kalibrasyon",
                "Calibration",
                "Kalibrasyon, üreticinin tarif ettiği standartla ve sıklıkla yapılır. Standartın adı, kabul aralığı ve tuş sırası bu kartta yoktur.",
                "Calibration uses the standard and the interval the manufacturer describes. The standard's name, the acceptance range, and the key sequence are not on this card.",
            ),
            (
                "Sık görülen hatalar",
                "Common errors",
                "Sızdıran kapak, ıslak veya kirli hücre, eksik örnek tanımı ve tarihi geçmiş kalibrasyon okumayı bozar. Arıza kodu görürseniz o modelin kılavuzuna bakın. Kod listesi burada uydurulmaz.",
                "A leaking cap, a wet or dirty cell, an unclear sample description, and an out-of-date calibration spoil the reading. If you see a fault code, use that model's manual. A code list is not invented here.",
            ),
            (
                "Güvenlik",
                "Safety",
                "Asit kullanılır. KKD, havalandırma ve dökülme adımı ürün SDS'si ile işyerinin prosedüründedir. Bu ders asit hazırlama tarifi değildir.",
                "Acid is used. PPE, ventilation, and the spill step are in the product SDS and the site procedure. This lesson is not an acid-preparation recipe.",
            ),
        ),
    ),
    _lesson(
        "bernard",
        ("devices",),
        "bernard",
        "Bernard kalsimetresi",
        "Bernard calcimeter",
        "Gaz hacminden karbonat düşünmenin genel mantığı ve teorik stokiyometri.",
        "The general idea of inferring carbonate from gas volume, plus theoretical stoichiometry.",
        (
            (
                "Tanım",
                "Definition",
                "Bernard düzeni, karbonatlı örneğin asitle verdiği karbondioksitin hacmini ölçen klasik bir gaz ölçerdir. Çizim şematiktir. Bir üreticinin parça numarası değildir.",
                "A Bernard arrangement is a classic gas meter for the carbon dioxide volume released when a carbonate sample meets acid. The drawing is a schematic. It is not a manufacturer's part number.",
            ),
            (
                "Parçaların görevleri",
                "What the parts do",
                "Örnek kabı katıyı tutar. Asit kabı tepkime sıvısını tutar; derişim yazılmaz. Bağlantı borusu gazı ölçüm borusuna taşır. Ölçüm borusu yer değiştiren sıvının seviyesini gösterir. Denge kabı seviyeyi karşılaştırmaya yarar. Conta gaz kaçırırsa hacim yanlış olur.",
                "The sample vessel holds the solid. The acid vessel holds the reaction liquid; its strength is not stated. The connecting tube carries gas to the measuring tube. The measuring tube shows the displaced liquid level. The leveling vessel is used to compare levels. A leaking seal makes the volume wrong.",
            ),
            (
                "Gaz hacmi ölçümünün mantığı",
                "Why gas volume is measured",
                "Oluşan karbondioksit kapalı düzenekte yer kaplar ve sıvı seviyesini oynatır. Okunan hacim, sıcaklık ve basınca bağlıdır. Ham milimetre, düzeltilmeden karbonat yüzdesi değildir.",
                "The carbon dioxide occupies space in the closed rig and moves a liquid level. The volume read depends on temperature and pressure. A raw scale mark is not a carbonate percent until it is corrected.",
            ),
            (
                "Karbonat tayini",
                "Carbonate determination",
                "Düzeltilmiş gaz hacmi örnek kütlesiyle ilişkilendirilir. Dönüşüm katsayısı cihazın yönteminden gelir. Bu uygulama katsayı uydurmaz.",
                "The corrected gas volume is related to the sample mass. The conversion factor comes from the instrument method. This application does not invent a factor.",
            ),
            (
                "Örnek hesaplama",
                "Example calculation",
                "Bu yalnızca teorik stokiyometridir, cihaz okuması değildir. Kalsiyum karbonatın mol kütlesi 100,09 g/mol'dür. Standart koşullarda, 0 °C ve 1 atm, bir mol gaz 22,4 L yer kaplar. Bu yüzden 100,09 g kalsiyum karbonat bu koşullarda 22,4 L karbondioksite karşılık gelir. Gerçek deneyde örnek kütlesi, ölçülen hacim ve sıcaklık-basınç düzeltmesi gerekir. Üretici katsayısı burada uygulanmaz.",
                "This is theoretical stoichiometry only, not an instrument reading. The molar mass of calcium carbonate is 100.09 g/mol. At 0 °C and 1 atm, one mole of gas occupies 22.4 L. So 100.09 g of calcium carbonate corresponds to 22.4 L of carbon dioxide at those conditions. A real run also needs the sample mass, the measured volume, and a temperature-pressure correction. A manufacturer factor is not applied here.",
            ),
            (
                "Sonuç yorumlama",
                "Interpretation",
                "Sonuç toplam karbonat davranışını anlatır. Kalsit ile dolomiti, jips ile karbonatı veya çimento türünü tek başına ayırmaz.",
                "The result describes total carbonate behavior. It does not by itself separate calcite from dolomite, gypsum from carbonate, or cement types.",
            ),
            (
                "Hata kaynakları",
                "Error sources",
                "Kaçak, kabarcık, seviye dengelemeden okuma, sıcaklığı yok sayma ve örneği tartmadan yorum yapmak başlıca hatalardır. Asit damlatma adımı modelin yöntemindedir; burada tarif edilmez.",
                "Leaks, bubbles, reading before the levels are balanced, ignoring temperature, and interpreting without a sample mass are the main errors. The acid-addition step is in the model method and is not written out here.",
            ),
        ),
    ),
    _lesson(
        "pure-water",
        ("devices",),
        "water",
        "Saf su cihazları",
        "Pure-water systems",
        "Distilasyon, deiyonizasyon ve ters ozmoz aynı işlem değildir.",
        "Distillation, deionization, and reverse osmosis are not the same process.",
        (
            (
                "Farklar",
                "Differences",
                "Distilasyon suyu buharlaştırıp yeniden yoğunlaştırır. Uçucu olmayan birçok madde geride kalır; uçucu maddeler buharla gelebilir. Deiyonizasyon, iyon değişim reçinesiyle iyonları tutar. Çözünmüş organik maddeyi veya mikrobu tek başına giderdiği söylenemez. Ters ozmoz, basınç altında bir zardan geçirir ve birçok çözünmüş katıyı azaltır. Tutma oranı membran üreticisinin verisidir; burada sayı verilmez.",
                "Distillation evaporates water and condenses it again. Many non-volatile substances stay behind; volatile substances can travel with the vapor. Deionization holds ions on an ion-exchange resin. It cannot be said, by itself, to remove dissolved organic matter or microbes. Reverse osmosis pushes water through a membrane under pressure and reduces many dissolved solids. The rejection rate is the membrane maker's data; no number is given here.",
            ),
            (
                "Bileşenler",
                "Components",
                "Distilasyon düzeneğinde kaynatma kabı, soğutucu ve toplama kabı vardır. Deiyonizasyonda kartuş veya reçine yatağı ve giriş-çıkış vardır. Ters ozmozda ön filtre, pompa veya şebeke basıncı, membran ve atık hattı vardır. Vana adları modele göredir.",
                "A distillation rig has a boiling vessel, a condenser, and a collection vessel. Deionization has a cartridge or resin bed and an inlet and outlet. Reverse osmosis has a prefilter, a pump or mains pressure, a membrane, and a reject line. Valve names depend on the model.",
            ),
            (
                "Su kalitesi",
                "Water quality",
                "Bir test yönteminin istediği su, o yöntemde yazar. Distile, deiyonize ve ozmoz suyu birbirinin yerine otomatik geçmez.",
                "The water a test method requires is written in that method. Distilled, deionized, and osmosis water are not automatic substitutes for each other.",
            ),
            (
                "İletkenlik",
                "Conductivity",
                "Düşük iletkenlik, az iyon bulunduğuna işaret eder. İletkenlik organik kirliliği, parçacığı veya biyolojik yükü tek başına göstermez. Kabul sınırı yöntemden okunur; bu kart bir mikrosiemens sınırı koymaz.",
                "Low conductivity points to few ions. Conductivity does not by itself show organic contamination, particles, or biological load. The acceptance limit is read from the method; this card sets no microsiemens limit.",
            ),
            (
                "Bakım",
                "Maintenance",
                "Reçine, membran ve filtre ömrü üreticinin tarifindedir. Süre veya litre uydurulmaz. Kirli kartuşu yıkayıp sonsuza kadar kullanmak bu dersin önerisi değildir.",
                "Resin, membrane, and filter life are in the manufacturer's description. A time or a litre value is not invented. Washing a dirty cartridge and using it forever is not this lesson's advice.",
            ),
            (
                "Sorun giderme",
                "Troubleshooting",
                "İletkenlik yükselirse bağlantı, tükenmiş reçine, delinmiş membran veya kirli cam akla gelir. Hangisi olduğu ölçülmeden ilan edilmez. Modelin arıza tablosu kullanılır.",
                "If conductivity rises, a connection, exhausted resin, a pierced membrane, or dirty glass may be involved. Which one it is, is not declared before it is measured. Use the model's fault table.",
            ),
        ),
    ),
    _lesson(
        "phenol",
        ("tests",),
        None,
        "Fenolftalein",
        "Phenolphthalein",
        "Asit-baz geçişini gösteren bir indikatör. Bu bir yöntem değildir. Titrasyon tarifi yoktur.",
        "An indicator of an acid-base change. This is not a method. No titration recipe is given.",
        (
            (
                "Amaç",
                "Purpose",
                "Fenolftalein, çözeltinin belirli bir asit-baz bölgesinde renk değiştirmesi için kullanılır. Sondaj sıvısı alkalinitesi konuşulurken adı geçer. Bu kart bir titrasyon yöntemi değildir.",
                "Phenolphthalein is used because a solution changes color in a particular acid-base region. The name comes up when drilling-fluid alkalinity is discussed. This card is not a titration method.",
            ),
            (
                "Prensip",
                "Principle",
                "Belirteç asidik bölgede renksiz, yeterince bazik bölgede pembe görünür. Geçişin tam yeri ve çözelti derişimi ürün ve yönteme aittir. Burada derişim yazılmaz.",
                "The indicator looks colorless in the acidic region and pink in a sufficiently basic region. The exact change and the solution strength belong to the product and the method. No strength is written here.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Renksiz kalma, pembeleşme veya pembenin kaybolması not edilir. Bulanık çamur rengi gizleyebilir.",
                "Staying colorless, turning pink, or losing the pink color is recorded. A cloudy mud can hide the color.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Renk, o belirtecin gördüğü asit-baz bölgesini anlatır. Tek başına çamurun bütün kimyasını veya bir katkı maddesinin dozunu vermez.",
                "The color describes the acid-base region that indicator sees. It does not by itself give the whole mud chemistry or an additive dose.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Koyu renk, yağ, boya ve başka belirteçler gözlemi bozar.",
                "A dark color, oil, dye, and other indicators spoil the observation.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Bu ekran damla sayısı, normalite veya bitiş noktası formülü vermez. Onlar onaylı yöntemdedir.",
                "This screen gives no drop count, normality, or endpoint formula. Those belong in an approved method.",
            ),
            (
                "KKD",
                "PPE",
                "Belirteç çözeltisinin KKD'si o ürünün SDS belgesindedir. Bu kart malzeme seçmez.",
                "PPE for the indicator solution is in that product's SDS. This card does not choose a material.",
            ),
            (
                "Atık",
                "Waste",
                "Artık çözelti işyerinin atık kuralına gider. Lavaboya dökme talimatı burada yoktur.",
                "Leftover solution follows the site waste rule. A sink-disposal instruction is not given here.",
            ),
            (
                "Kaynak",
                "Source",
                "Genel asit-baz belirteç bilgisi. Ürün SDS'si bu uygulamada yüklü değildir.",
                "General acid-base indicator information. The product SDS is not loaded in this application.",
            ),
        ),
    ),
    _lesson(
        "alizarin",
        ("tests",),
        None,
        "Alizarin Red S ile kalsit ve dolomit",
        "Calcite and dolomite with Alizarin Red S",
        "Boyama ayrımı yayınlanmış yönteme bağlıdır. Bu bir yöntem değildir. Asit derişimi burada yoktur. Boya ve asit için tehlike, kendi SDS belgelerindedir.",
        "A stain separation depends on a published method. This is not a method. Acid strength is not stated here. The hazard of the stain and of the acid is in their own SDS documents.",
        (
            (
                "Amaç",
                "Purpose",
                "Alizarin Red S boyaması, karbonat minerallerini ayırmaya yardım etmek için kullanılır. Kesin raporun yerine geçmez.",
                "An Alizarin Red S stain is used to help separate carbonate minerals. It does not replace a definitive report.",
            ),
            (
                "Prensip",
                "Principle",
                "Yayınlanmış boyama yöntemlerinde kalsit boyayı dolomitten farklı tutabilir. Ayrım, o yöntemdeki asit düzenine bağlıdır. Derişim ve süre bu uygulamada uydurulmaz. Kaynak olarak Friedman'ın 1959 boyama çalışması anılır; yöntem metni burada kopyalanmaz.",
                "In published staining methods, calcite can hold the dye differently from dolomite. The separation depends on the acid arrangement in that method. Strength and time are not invented here. Friedman's 1959 staining study is cited as the source; its method text is not copied here.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Yüzeyde kırmızı veya pembe tutunma, zayıf tutunma ya da tutunmama not edilir. Islak ve kuru görünüm farklı olabilir.",
                "Red or pink hold on the surface, a weak hold, or no hold is recorded. Wet and dry looks can differ.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Beklenen boya farkı kalsit lehinde yorumlanır, dolomit aleyhine tek başına hüküm kurmaz. Karışık taneler ara sonuç verir.",
                "An expected dye difference is read toward calcite. It does not by itself rule dolomite in or out. Mixed grains give an in-between result.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "İnce toz, demir boyası, kirli yüzey ve yöntemin dışında bir asit düzeni sonucu değiştirir.",
                "Fine powder, iron stain, a dirty surface, and an acid arrangement outside the method change the result.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Renk veya tek bir boya lekesi mineralin adı değildir. Şüphede ince kesit veya laboratuvar analizi gerekir.",
                "A color or a single dye spot is not the mineral's name. When there is doubt, a thin section or laboratory analysis is needed.",
            ),
            (
                "KKD",
                "PPE",
                "Boyanın ve kullanılan asidin KKD'si kendi SDS belgelerindedir.",
                "PPE for the dye and for the acid used is in their own SDS documents.",
            ),
            (
                "Atık",
                "Waste",
                "Boyalı asitli atık, işyerinin kimyasal atık kuralına gider.",
                "Dyed acidic waste follows the site chemical-waste rule.",
            ),
            (
                "Kaynak",
                "Source",
                "Friedman, G. M., 1959, Identification of carbonate minerals by staining methods, Journal of Sedimentary Petrology. Bu kart o makalenin işlem tarifini içermez.",
                "Friedman, G. M., 1959, Identification of carbonate minerals by staining methods, Journal of Sedimentary Petrology. This card does not contain that paper's procedure.",
            ),
        ),
    ),
    _lesson(
        "carbonate-rxn",
        ("tests",),
        None,
        "Karbonat tepkimesi",
        "Carbonate reaction",
        "Asitle gaz çıkması karbonat davranışını düşündürür. Bu bir yöntem değildir. Miktar vermez. Asit sınıfının tehlikesi SDS'den okunur.",
        "Gas with acid suggests carbonate behavior. This is not a method. It does not give an amount. The hazard of the acid class is read from the SDS.",
        (
            (
                "Amaç",
                "Purpose",
                "Kırıntıda karbonat olup olmadığına dair ilk gözlemi anlatmak.",
                "To describe a first observation of whether a cutting may contain carbonate.",
            ),
            (
                "Prensip",
                "Principle",
                "Karbonat asitle karbondioksit gazı verebilir ve kabarcık görülür. Asidin adı ve derişimi onaylı yöntemdedir. Burada yazılmaz.",
                "Carbonate can release carbon dioxide with acid, and bubbles may be seen. The acid's name and strength are in an approved method. They are not written here.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Kabarcığın varlığı, hızı ve sürmesi not edilir. Hız, tane boyu ve mineral ile değişir. Hız bir yüzde değildir.",
                "Whether bubbles appear, how fast, and how long they last is recorded. Speed changes with grain size and mineral. Speed is not a percent.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Bol kabarcık karbonat lehinedir. Az kabarcık, karbonat yok demek için yetmez. Dolomit soğuk gözlemde zayıf kalabilir.",
                "Many bubbles point toward carbonate. Few bubbles are not enough to say carbonate is absent. Dolomite can look weak in a cold observation.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Sıkışmış hava, gözenek suyu ve bazı katkı maddeleri de kabarcık yapabilir.",
                "Trapped air, pore water, and some additives can also make bubbles.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Gözlem nicel tayin değildir. Yüzde için kalsimetre veya laboratuvar analizi gerekir. O cihazın tarifi bu kartta yoktur.",
                "The observation is not a quantitative assay. A percent needs a calcimeter or laboratory analysis. That instrument's recipe is not on this card.",
            ),
            (
                "KKD",
                "PPE",
                "Asidin KKD'si SDS'den okunur.",
                "PPE for the acid is read from the SDS.",
            ),
            (
                "Atık",
                "Waste",
                "Asitli kırıntı işyeri atık kuralına gider.",
                "Acid-wet cuttings follow the site waste rule.",
            ),
            (
                "Kaynak",
                "Source",
                "Genel karbonat-asit tepkimesi. Ürün SDS'si ve saha yöntemi ayrı belgelerdir.",
                "The general carbonate-acid reaction. The product SDS and the field method are separate documents.",
            ),
        ),
    ),
    _lesson(
        "gypsum-test",
        ("tests", "rocks"),
        None,
        "Jips ve anhidrit ayrımı",
        "Separating gypsum and anhydrite",
        "Su içeriği ve sertlik ayrımda kullanılır. Bu bir yöntem değildir. Tek renk yeterli değildir.",
        "Water content and hardness are used. This is not a method. Color alone is not enough.",
        (
            (
                "Amaç",
                "Purpose",
                "Jips ile anhidriti birbirine benzeyen beyaz veya gri örneklerde ayırmaya yardım etmek.",
                "To help separate gypsum and anhydrite in white or gray samples that look alike.",
            ),
            (
                "Prensip",
                "Principle",
                "Jips kalsiyum sülfatın sulu halidir. Anhidrit sulu değildir. Jips tırnakla çizilebilir yumuşaklıkta anılır. Anhidrit daha sert anılır. Isıtınca jipsin suyunu bırakması klasik bir ayrım fikridir. Sıcaklık ve süre bu kartta uydurulmaz.",
                "Gypsum is the hydrated form of calcium sulfate. Anhydrite is not hydrated. Gypsum is described as soft enough to scratch with a fingernail. Anhydrite is described as harder. Gypsum giving up water when heated is a classic separation idea. Temperature and time are not invented on this card.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Çizilme, dilinim, kütle hissi ve varsa ısı deneyi not edilir. Yalnızca beyazlık not edilmez.",
                "Scratching, cleavage, how heavy it feels, and a heat trial if one is used are recorded. Whiteness alone is not the note.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Yumuşak ve sulu davranış jipse gider. Daha sert ve susuz davranış anhidrite gider. Ara örnekler karışıktır.",
                "Soft, hydrated behavior points to gypsum. Harder, anhydrous behavior points to anhydrite. In-between samples are mixed.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Talk, kil ve tebeşir de yumuşak ve açık renkli olabilir.",
                "Talc, clay, and chalk can also be soft and light colored.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Renk ayrım değildir. Kesin ad için optik veya laboratuvar verisi gerekir.",
                "Color is not the separation. A firm name needs optical or laboratory data.",
            ),
            (
                "KKD",
                "PPE",
                "Isı veya asit kullanılıyorsa o işlemin KKD'si iş prosedüründedir. Bu kart ısı ayarı vermez.",
                "If heat or acid is used, PPE for that job is in the work procedure. This card gives no heat setting.",
            ),
            (
                "Atık",
                "Waste",
                "Deney artığı işyeri kuralına göre ayrılır.",
                "Test residue is separated by the site rule.",
            ),
            (
                "Kaynak",
                "Source",
                "Mineral formülleri CaSO4·2H2O ve CaSO4 genel mineralojidir. Bir saha tarifinin yerine geçmez.",
                "The formulas CaSO4·2H2O and CaSO4 are general mineralogy. They do not replace a field recipe.",
            ),
        ),
    ),
    _lesson(
        "uv",
        ("tests", "shows"),
        None,
        "UV floresansı",
        "UV fluorescence",
        "Floresans hidrokarbonun kesin kanıtı değildir. Bu bir yöntem değildir.",
        "Fluorescence is not definite proof of hydrocarbon. This is not a method.",
        (
            (
                "Amaç",
                "Purpose",
                "Kırıntı veya çamurdaki floresansı gözlemek ve sınırını bilmek.",
                "To observe fluorescence in cuttings or mud and to know its limit.",
            ),
            (
                "Prensip",
                "Principle",
                "Bazı hidrokarbonlar ve bazı mineraller morötesi ışıkta görünür ışık verir. Lamba dalga boyu cihazın etiketindedir. Bu kart dalga boyu uydurmaz.",
                "Some hydrocarbons and some minerals give visible light under ultraviolet light. The lamp wavelength is on the instrument label. This card does not invent a wavelength.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Renk, parlaklık, tane içi veya yüzeyde oluş ve ıslak-kuru farkı not edilir.",
                "Color, brightness, whether it is inside the grain or on the surface, and the wet-dry difference are recorded.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Floresans hidrokarbon ihtimalini akla getirir. Tek başına hidrokarbonun kesin kanıtı sayılmaz.",
                "Fluorescence brings hydrocarbon to mind as a possibility. By itself it is not counted as definite proof of hydrocarbon.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Yağ bazlı çamur, bazı katkılar, boya ve floresan mineraller aynı görünümü verebilir.",
                "Oil-based mud, some additives, dye, and fluorescent minerals can give the same look.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Karar için kesim, koku, çözücü gözlemi ve jeoloji birlikte okunur. Yine de bu dörtlü bir laboratuvar raporu değildir.",
                "A cut, odor, a solvent observation, and the geology are read together. Even together they are not a laboratory report.",
            ),
            (
                "KKD",
                "PPE",
                "Morötesi lambanın göz ve cilt uyarısı üretici etiketindedir. Bu kart lamba modeli seçmez.",
                "The ultraviolet lamp's eye and skin warning is on the maker's label. This card does not choose a lamp model.",
            ),
            (
                "Atık",
                "Waste",
                "Çözücü kullanıldıysa atık, çözücünün kuralına gider. Çözücü miktarı burada yoktur.",
                "If a solvent was used, the waste follows that solvent's rule. A solvent amount is not stated here.",
            ),
            (
                "Kaynak",
                "Source",
                "Genel mudlogging gözlem sınırı. Bir hidrokarbon standardının analiz yöntemi değildir.",
                "A general mud-logging observation limit. It is not an analytical method from a hydrocarbon standard.",
            ),
        ),
    ),
    _lesson(
        "solvent-cut",
        ("tests", "shows"),
        "fluor",
        "Solvent cut",
        "Solvent cut",
        "Çözücünün taşıdığı leke bir gözlemdir. Bu bir yöntem değildir. Çözücü tarifi yoktur. Birçok çözücü kolay alevlenir.",
        "A mark carried by a solvent is an observation. This is not a method. No solvent recipe is given. Many solvents are highly flammable.",
        (
            (
                "Amaç",
                "Purpose",
                "Kırıntıdaki çözünebilir hidrokarbon lekesini görmek.",
                "To see a soluble hydrocarbon mark on a cutting.",
            ),
            (
                "Prensip",
                "Principle",
                "Uygun bir çözücü bazı hidrokarbonları taşıyıp bir halka veya akıntı bırakabilir. Hangi çözücünün kullanılacağı onaylı yöntemdedir. Ad, miktar ve bekleme süresi burada uydurulmaz.",
                "A suitable solvent can carry some hydrocarbons and leave a ring or a streak. Which solvent is used belongs in an approved method. A name, an amount, and a waiting time are not invented here.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Halkanın rengi, hızı ve kalıntının yeri not edilir.",
                "The ring's color, speed, and where the residue sits are recorded.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Kalıntı çözünebilir madde lehinedir. Hidrokarbonun türünü veya doygunluğunu tek başına söylemez.",
                "A residue points toward soluble material. It does not by itself name the hydrocarbon type or the saturation.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Çamur katkısı, yağ ve kirli tepsi aynı lekeyi yapabilir.",
                "A mud additive, oil, and a dirty tray can make the same mark.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Cut, floresansın yerine geçmez ve floresans da cut'ın yerine geçmez. İkisi de kesin kanıt değildir.",
                "A cut does not replace fluorescence, and fluorescence does not replace a cut. Neither is definite proof.",
            ),
            (
                "KKD",
                "PPE",
                "Çözücü seçilirse KKD ve havalandırma o SDS'den okunur. Birçok çözücü kolay alevlenir.",
                "If a solvent is chosen, PPE and ventilation are read from that SDS. Many solvents are highly flammable.",
            ),
            (
                "Atık",
                "Waste",
                "Çözücü atığı işyeri kuralına gider. Lavabo tarifi yoktur.",
                "Solvent waste follows the site rule. There is no sink recipe.",
            ),
            (
                "Kaynak",
                "Source",
                "Genel mudlogging cut gözlemi. Ürün SDS'si ayrıca doğrulanır.",
                "A general mud-logging cut observation. The product SDS is verified separately.",
            ),
        ),
    ),
    _lesson(
        "acetone-test",
        ("tests", "shows"),
        None,
        "Aseton testi",
        "Acetone test",
        "Aseton bazı lekeleri taşıyabilir. Bu bir yöntem değildir. Miktar ve kesin kanıt yoktur. Aseton kolay alevlenir bir çözücüdür.",
        "Acetone can carry some marks. This is not a method. There is no amount and no definite proof. Acetone is a highly flammable solvent.",
        (
            (
                "Amaç",
                "Purpose",
                "Asetonun kırıntıdaki bazı çözünebilir maddeleri hareket ettirip ettirmediğini gözlemek.",
                "To observe whether acetone moves some soluble material on a cutting.",
            ),
            (
                "Prensip",
                "Principle",
                "Aseton birçok organik maddeyi çözer. Bir lekenin dağılması o maddenin asetonda çözünebildiğini düşündürür. Hidrokarbonun adı veya doygunluğu çıkmaz. Miktar yazılmaz.",
                "Acetone dissolves many organic materials. A mark that spreads suggests that material can dissolve in acetone. It does not yield the hydrocarbon's name or the saturation. No amount is stated.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Lekenin yayılması, renk bırakması veya değişmemesi not edilir.",
                "Whether the mark spreads, leaves a color, or stays unchanged is recorded.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Yayılma çözünür madde lehinedir. Tek başına hidrokarbon kanıtı değildir.",
                "Spreading points toward soluble material. By itself it is not proof of hydrocarbon.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Boya, katkı ve başka çözünür organikler de yayılır.",
                "Dye, additives, and other soluble organics also spread.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Bu kart damlatma sayısı veya bekleme süresi vermez. Aseton kolay alevlenir bir sıvı olarak anılır; şişenin etiketi esastır.",
                "This card gives no drop count or waiting time. Acetone is described as a highly flammable liquid; the bottle label governs.",
            ),
            (
                "KKD",
                "PPE",
                "Göz, eldiven ve havalandırma o ürünün SDS belgesindedir. Eldiven malzemesi burada seçilmez.",
                "Eyes, gloves, and ventilation are in that product's SDS. Glove material is not chosen here.",
            ),
            (
                "Atık",
                "Waste",
                "Asetonlu atık, yanıcı çözücü kuralına göre ayrılır.",
                "Acetone waste is separated under the flammable-solvent rule.",
            ),
            (
                "Kaynak",
                "Source",
                "Genel çözücü bilgisi. Kütüphanedeki aseton kartı ürün SDS'si değildir.",
                "General solvent information. The acetone card in the library is not a product SDS.",
            ),
        ),
    ),
    _lesson(
        "chloride",
        ("tests",),
        None,
        "Klorür testi",
        "Chloride test",
        "Gümüş tuzu ile beyaz çökelek genel bir klorür işaretidir. Bu bir yöntem değildir. Derişim yoktur.",
        "A white precipitate with a silver salt is a general chloride sign. This is not a method. No strength is given.",
        (
            (
                "Amaç",
                "Purpose",
                "Süzüntüde klorür bulunup bulunmadığına dair nitel bir işaret okumak.",
                "To read a qualitative sign of whether chloride is present in a filtrate.",
            ),
            (
                "Prensip",
                "Principle",
                "Klorür, gümüş nitrat gibi bir gümüş tuzuyla beyaz bir çökelek verebilir. Çözelti derişimi ve asit düzeni onaylı yöntemdedir. Burada yazılmaz.",
                "Chloride can give a white precipitate with a silver salt such as silver nitrate. Solution strength and the acid arrangement are in an approved method. They are not written here.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Beyaz bulut veya çökelek, geç oluşma ya da hiç oluşmama not edilir. Bazı gümüş tuzu çökelekleri ışıkta koyulaşır. Süre ve derişim yazılmaz.",
                "A white cloud or precipitate, a late appearance, or no appearance is recorded. Some silver-salt precipitates darken in light. A time and a strength are not written.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Beyaz çökelek klorür lehinedir. Tuzluluk yüzdesi veya formasyon suyu kararı tek başına çıkmaz.",
                "A white precipitate points toward chloride. A salinity percent or a formation-water decision does not come from it alone.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Başka halojenürler ve bazı iyonlar da bulanıklık yapabilir. Çamur katkıları karıştırır.",
                "Other halides and some ions can also cloud the liquid. Mud additives confuse it.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Nicel klorür için onaylı titrasyon veya laboratuvar yöntemi gerekir. Bu kart o yöntemi vermez.",
                "Quantitative chloride needs an approved titration or laboratory method. This card does not give that method.",
            ),
            (
                "KKD",
                "PPE",
                "Gümüş tuzu ve asit için KKD, kendi SDS belgelerindedir.",
                "PPE for the silver salt and the acid is in their own SDS documents.",
            ),
            (
                "Atık",
                "Waste",
                "Gümüşlü atık ayrı toplanır. İşyeri kuralı uygulanır.",
                "Silver-bearing waste is collected separately. The site rule applies.",
            ),
            (
                "Kaynak",
                "Source",
                "Genel nitel analitik kimya. Ürün SDS'si bu uygulamada yoktur.",
                "General qualitative analytical chemistry. The product SDS is not in this application.",
            ),
        ),
    ),
    _lesson(
        "sulfate",
        ("tests",),
        None,
        "Sülfat testi",
        "Sulfate test",
        "Baryum ile beyaz çökelek genel bir sülfat işaretidir. Bu bir yöntem değildir. Derişim yoktur. Baryum sınıfının tehlikesi SDS'den okunur.",
        "A white precipitate with barium is a general sulfate sign. This is not a method. No strength is given. The hazard of the barium class is read from the SDS.",
        (
            (
                "Amaç",
                "Purpose",
                "Süzüntüde sülfat için nitel bir işaret okumak.",
                "To read a qualitative sign of sulfate in a filtrate.",
            ),
            (
                "Prensip",
                "Principle",
                "Sülfat, baryum tuzuyla zor çözünen beyaz bir katı verebilir. Derişim ve asit düzeni yöntemdedir. Baryum bileşikleri zehirli olabilir; SDS okunur.",
                "Sulfate can give a poorly soluble white solid with a barium salt. Strength and the acid arrangement are in the method. Barium compounds can be toxic; the SDS is read.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Beyaz bulutun oluşması veya oluşmaması not edilir.",
                "Whether a white cloud forms or not is recorded.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Çökelek sülfat lehinedir. Jips veya anhidrit tanısı tek başına konmaz.",
                "A precipitate points toward sulfate. Gypsum or anhydrite is not identified from it alone.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Karbonat ve başka iyonlar da bulanıklık yapabilir. Yöntemdeki ayırma adımı bu kartta yoktur.",
                "Carbonate and other ions can also cloud the liquid. The separation step in the method is not on this card.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Nicel sülfat bu ekranda hesaplanmaz.",
                "Quantitative sulfate is not calculated on this screen.",
            ),
            (
                "KKD",
                "PPE",
                "Baryum ürününün KKD'si SDS'den okunur. Bu kart eldiven malzemesi seçmez.",
                "PPE for the barium product is read from the SDS. This card does not choose a glove material.",
            ),
            (
                "Atık",
                "Waste",
                "Baryumlu atık işyerinin zehirli atık kuralına gider.",
                "Barium-bearing waste follows the site rule for toxic waste.",
            ),
            (
                "Kaynak",
                "Source",
                "Genel nitel sülfat bilgisi. Ürün SDS'si ayrıca gerekir.",
                "General qualitative sulfate information. The product SDS is still required.",
            ),
        ),
    ),
    _lesson(
        "coal-test",
        ("tests", "rocks"),
        None,
        "Kömür ve karbonlu şeyl",
        "Coal and carbonaceous shale",
        "Tek ve kesin bir kimyasal test yoktur. Bu bir yöntem değildir.",
        "There is no single definite chemical test. This is not a method.",
        (
            (
                "Amaç",
                "Purpose",
                "Kömür ile karbonlu şeyli birbirine karıştırmadan tarif etmek.",
                "To describe coal and carbonaceous shale without mixing them up.",
            ),
            (
                "Prensip",
                "Principle",
                "Kömür başlıca organik bir kayadır. Karbonlu şeyl, şeyl içinde dağılmış organik madde taşır. İkisini ayıran tek bir kimyasal tepki yoktur.",
                "Coal is chiefly an organic rock. Carbonaceous shale carries organic matter scattered in shale. There is no single chemical reaction that separates the two.",
            ),
            (
                "Gözlemler",
                "Observations",
                "Kırık şekli, çizgi, yoğunluk hissi, tabakalanma ve kirletme birlikte not edilir. Yalnızca siyahlık yetmez.",
                "Break shape, streak, how dense it feels, bedding, and smudging are recorded together. Blackness alone is not enough.",
            ),
            (
                "Yorum",
                "Interpretation",
                "Hafif, elle kirleten ve tabakasız siyah parça kömür lehinedir. Yaprağımsı, daha ağır ve killi siyah parça karbonlu şeyl lehinedir. İkisi birden şüphe bırakır.",
                "A light, smudging, unbedded black piece points toward coal. A fissile, heavier, clay-rich black piece points toward carbonaceous shale. Both together leave doubt.",
            ),
            (
                "Karıştırıcı etkenler",
                "Confounding factors",
                "Bitümlü şeyl, boya, çamur katkısı ve yanmış kırıntı siyah görünebilir.",
                "Bituminous shale, dye, a mud additive, and burnt cuttings can look black.",
            ),
            (
                "Sınırlar",
                "Limits",
                "Bu uygulama kömür için tek ve kesin bir kimyasal test varmış gibi davranmaz. Ad, jeolog ve laboratuvar verisiyle konur.",
                "This application does not treat coal as if it had one definite chemical test. The name is given with a geologist and laboratory data.",
            ),
            (
                "KKD",
                "PPE",
                "Yakma deneyi bu kartta tarif edilmez. Yapılıyorsa işyerinin prosedürü ve KKD'si geçerlidir.",
                "A burning trial is not described on this card. If one is done, the site procedure and its PPE apply.",
            ),
            (
                "Atık",
                "Waste",
                "Kırıntı atığı işyeri kuralına gider.",
                "Cutting waste follows the site rule.",
            ),
            (
                "Kaynak",
                "Source",
                "Genel sedimanter kayaç ayrımı. Bir kömür standardının analiz yöntemi değildir.",
                "A general sedimentary-rock separation. It is not an analytical method from a coal standard.",
            ),
        ),
    ),
)


def _rock(lesson_id, title_tr, title_en, formula, trait_tr, trait_en, like_tr, like_en, limit_tr, limit_en):
    return _lesson(
        lesson_id,
        ("rocks",),
        None,
        title_tr,
        title_en,
        trait_tr,
        trait_en,
        (
            (
                "Ayırt edici özellikler",
                "Distinctive features",
                f"{formula} {trait_tr} Renk tek başına ad koymaz.",
                f"{formula} {trait_en} Color alone does not assign the name.",
            ),
            (
                "Benzeyen örnekler",
                "Lookalikes",
                like_tr,
                like_en,
            ),
            (
                "Tanımanın sınırı",
                "Limit of recognition",
                limit_tr,
                limit_en,
            ),
        ),
    )


ROCKS = (
    _rock(
        "calcite",
        "Kalsit",
        "Calcite",
        "CaCO3.",
        "Romboedral dilinim ve asitle belirgin kabarcık kalsit için sık anılır. Sertliği Mohs ölçeğinde 3 olarak bilinir.",
        "Rhombohedral cleavage and clear bubbles with acid are often cited for calcite. Its hardness is known as 3 on the Mohs scale.",
        "Tebeşir, mermer ve bazı dolomitler açık renkli olabilir.",
        "Chalk, marble, and some dolomites can be light colored.",
        "Kabarcık hızı tane boyuna bağlıdır. Yüzde veya mineral saflığı bu kartta hesaplanmaz.",
        "Bubble speed depends on grain size. A percent or mineral purity is not calculated on this card.",
    ),
    _rock(
        "dolomite",
        "Dolomit",
        "Dolomite",
        "CaMg(CO3)2.",
        "Dolomit karbonattır. Soğuk gözlemde kalsitten daha zayıf kabarcık verdiği sık söylenir. Toz halinde davranış değişebilir.",
        "Dolomite is a carbonate. It is often said to bubble more weakly than calcite in a cold observation. Powdered behavior can change.",
        "Kalsit, ankerit ve kirli kireçtaşı benzeyebilir.",
        "Calcite, ankerite, and dirty limestone can look alike.",
        "Zayıf kabarcık dolomit kanıtı değildir. Boyama veya analiz gerekir. Asit derişimi burada yoktur.",
        "A weak bubble is not proof of dolomite. A stain or analysis is needed. Acid strength is not stated here.",
    ),
    _rock(
        "gypsum",
        "Jips",
        "Gypsum",
        "CaSO4·2H2O.",
        "Yumuşaktır ve tırnakla çizildiği söylenir. Sulu kalsiyum sülfattır.",
        "It is soft and is said to be scratched by a fingernail. It is hydrated calcium sulfate.",
        "Anhidrit, talk ve kil açık renkli ve yumuşak görünebilir.",
        "Anhydrite, talc, and clay can look light colored and soft.",
        "Beyazlık jips demek değildir. Ayrım jips-anhidrit kartındaki sınırlarla okunur.",
        "Whiteness does not mean gypsum. The separation is read with the limits on the gypsum-anhydrite card.",
    ),
    _rock(
        "anhydrite",
        "Anhidrit",
        "Anhydrite",
        "CaSO4.",
        "Susuz kalsiyum sülfattır ve jipsten sert anılır.",
        "It is anhydrous calcium sulfate and is described as harder than gypsum.",
        "Jips ve bazı karbonatlar aynı renklerde olur.",
        "Gypsum and some carbonates occur in the same colors.",
        "Sertlik tek başına ad koymaz. Laboratuvar verisi şüpheyi kapatır.",
        "Hardness alone does not assign the name. Laboratory data closes the doubt.",
    ),
    _rock(
        "quartz",
        "Kuvars",
        "Quartz",
        "SiO2.",
        "Serttir. Mohs ölçeğinde 7 olarak bilinir. Seyreltik asitle karbonat gibi kabarcık vermez.",
        "It is hard. It is known as 7 on the Mohs scale. It does not bubble with dilute acid the way carbonate does.",
        "Feldispat ve temiz kalsit parlak görünebilir.",
        "Feldspar and clean calcite can look bright.",
        "Renkli kuvars da kuvarstır. Renk tür koymaz. Asit tarifi bu kartta yoktur.",
        "Colored quartz is still quartz. Color does not set the variety. An acid recipe is not on this card.",
    ),
    _rock(
        "limestone",
        "Kireçtaşı",
        "Limestone",
        "Başlıca kalsitli bir kayadır.",
        "Kayaçtır, tek bir mineral adı değildir. Asitle kabarcık vermesi karbonat lehinedir.",
        "It is a rock, not a single mineral name. Bubbles with acid point toward carbonate.",
        "Dolomitik kireçtaşı, tebeşir ve marn benzeyebilir.",
        "Dolomitic limestone, chalk, and marl can look alike.",
        "Kayaç adı, tane, çimento ve fosil ile birlikte konur. Yalnızca renk yetmez.",
        "The rock name is given together with grains, cement, and fossils. Color alone is not enough.",
    ),
    _rock(
        "sandstone",
        "Kumtaşı",
        "Sandstone",
        "Kum boyu taneli bir kayadır.",
        "Taneler çoğunlukla kuvars olabilir. Çimento karbonat, silis veya demir olabilir. Çimento asitle kabarcık verirse karbonat çimento akla gelir.",
        "Grains can be mostly quartz. Cement can be carbonate, silica, or iron. If the cement bubbles with acid, carbonate cement comes to mind.",
        "Silttaşı ve gevrek konglomera karışabilir.",
        "Siltstone and a loose conglomerate can be confused with it.",
        "Tane boyu göz kararı yüzde değildir. Elek verisi yoksa boy aralığı iddia edilmez.",
        "Grain size by eye is not a percent. Without sieve data, a size range is not claimed.",
    ),
    _rock(
        "shale",
        "Şeyl",
        "Shale",
        "İnce taneli ve yapraklanabilen bir kayadır.",
        "Kil ve silt boyu malzeme ve fissil kırık şeyl için anılır.",
        "Clay- and silt-size material and a fissile break are cited for shale.",
        "Silttaşı, çamurtaşı ve karbonlu şeyl benzeyebilir.",
        "Siltstone, mudstone, and carbonaceous shale can look alike.",
        "Siyah şeyl kömür değildir. Ayrım kömür kartındaki sınırla okunur.",
        "Black shale is not coal. The separation is read with the limit on the coal card.",
    ),
    _rock(
        "coal",
        "Kömür",
        "Coal",
        "Başlıca organik bir kayadır.",
        "Hafiflik, elde kir bırakma ve parlak veya mat kırık birlikte anılır. Tek kimyasal test yoktur.",
        "Light weight, smudging the hand, and a bright or dull break are cited together. There is no single chemical test.",
        "Karbonlu şeyl, bitümlü şeyl ve yanmış kırıntı siyahtır.",
        "Carbonaceous shale, bituminous shale, and burnt cuttings are black.",
        "Yalnızca siyaha bakarak kömür denmez.",
        "Coal is not named from black color alone.",
    ),
    _rock(
        "carb-shale",
        "Karbonlu şeyl",
        "Carbonaceous shale",
        "Organik madde içeren şeyldir.",
        "Yapraklanma durur, kömürden daha taşsı hissedilebilir. Tek kimyasal test yoktur.",
        "Bedding remains, and it can feel more stony than coal. There is no single chemical test.",
        "Kömür ve koyu şeyl benzeyebilir.",
        "Coal and dark shale can look alike.",
        "Renk ve tek bir çözücü lekesi ad koymaz.",
        "Color and a single solvent mark do not assign the name.",
    ),
)


SHOWS = (
    _lesson(
        "show-odor",
        ("shows",),
        None,
        "Koku ve leke",
        "Odor and stain",
        "Koku bir emaredir. Hidrokarbonun kesin kanıtı değildir.",
        "Odor is a show. It is not definite proof of hydrocarbon.",
        (
            (
                "Amaç",
                "Purpose",
                "Kırıntı veya çamurdaki kokuyu diğer gözlemlerden ayrı yazmak.",
                "To write the odor of cuttings or mud apart from the other observations.",
            ),
            (
                "Prensip",
                "Principle",
                "Bazı hidrokarbonlar koku verir. Birçok katkı, çözücü ve çürük koku da verir.",
                "Some hydrocarbons smell. Many additives, solvents, and decay also smell.",
            ),
            (
                "Gözlem",
                "Observation",
                "Kokunun varlığı veya yokluğu not edilir. Şiddet için sayı uydurulmaz.",
                "Whether an odor is present or absent is recorded. A number for its strength is not invented.",
            ),
            (
                "Sınır",
                "Limit",
                "Koku tek başına hidrokarbon kanıtı değildir. UV floresansı da tek başına kanıt değildir.",
                "Odor alone is not proof of hydrocarbon. UV fluorescence alone is not proof either.",
            ),
        ),
    ),
)

MEASURE = (
    _lesson(
        "measure-map",
        ("measure",),
        None,
        "Hesaplar ekranındaki formüller",
        "Formulas on the calculation screen",
        "Hidrostatik, hız, kapasite ve gecikme teorik birim dönüşümleridir.",
        "Hydrostatic pressure, velocity, capacity, and lag are theoretical unit conversions.",
        (
            (
                "Ne var",
                "What is there",
                "Hesaplar ekranında hidrostatik basınç 12/231 ile, halka hızı, boru ve halka kapasitesi, tank hacmi ve gecikme süresi vardır. ECD için halka basınç kaybı kullanıcıdan istenir. Bu akademi o sayfanın yerine sayı koymaz.",
                "The calculation screen has hydrostatic pressure with 12/231, annular velocity, pipe and annular capacity, pit volume, and lag time. ECD asks the user for annular pressure loss. This academy does not put a number in that page's place.",
            ),
            (
                "Sınır",
                "Limit",
                "Bunlar kuyu kontrol formülü veya kill sheet değildir. Asit hesabı da teoriktir. Kütlece, hacimce ve kütle/hacim yüzdesi birbirine çevrilmez. Eksik yoğunluk veya ürün bilgisi varsa hesap ekranı bunu yazar. Sonuç saha hazırlama onayı değildir.",
                "These are not well-control formulas or a kill sheet. The acid calculation is theoretical too. Percent by mass, by volume, and by mass/volume are not converted into each other. If density or product data is missing, the calculation screen says so. The result is not a field-preparation approval.",
            ),
        ),
    ),
)

SAFETY = (
    _lesson(
        "safety-ppe",
        ("safety",),
        "acid",
        "PPE ve asit güvenliği",
        "PPE and acid safety",
        "Yerel şematik canlandırma. Su önce kapta, asit suya. Miktar yoktur.",
        "A local schematic animation. Water is in the vessel first, then acid goes into the water. No amount is shown.",
        (
            (
                "İlke",
                "Principle",
                "Etiket ve güncel SDS okunur. Yüz siperi sıçrama gözlüğünün yerine geçmez. Eldiven malzemesi SDS'den kontrol edilir. Genel ilke: su uygun kaba önce alınır, asit suya yavaşça eklenir. Suyun konsantre asidin üzerine eklenmesi gösterilmez. Sıçrama, ısı ve asit buharı anlatılır. Miktar, kap ölçüsü ve onay yoktur.",
                "The label and the current SDS are read. A face shield does not replace splash goggles. Glove material is checked in the SDS. General principle: water is placed in a suitable vessel first, and acid is added slowly to the water. Adding water onto concentrated acid is not shown. Splash, heat, and acid vapor are explained. There is no amount, vessel size, or approval.",
            ),
            (
                "Ayrı ders",
                "Separate lesson",
                "Daha uzun adım adım ders Görsel Eğitim Merkezi'ndedir. İkisi de iş prosedürü değildir.",
                "The longer step-by-step lesson is in the Visual training center. Neither is a work procedure.",
            ),
        ),
    ),
)

TROUBLE = (
    _lesson(
        "trouble-gas",
        ("trouble",),
        "bernard",
        "Gaz ölçer hataları",
        "Gas-meter errors",
        "Kaçak ve seviye hatası hacmi bozar. Tuş sırası yoktur.",
        "A leak and a level error spoil the volume. There is no key sequence.",
        (
            (
                "Ne kontrol edilir",
                "What is checked",
                "Conta, kabarcık, ölçüm borusu seviyesi ve örneğin tartılıp tartılmadığı kontrol listesidir. Arıza kodu modelin kılavuzundadır.",
                "The seal, bubbles, the measuring-tube level, and whether the sample was weighed are the checklist. A fault code is in the model manual.",
            ),
            (
                "Ne yapılmaz",
                "What is not done",
                "Bu kart sızdıran düzeneği çalıştırmaya devam etme veya asit miktarını artırma talimatı vermez.",
                "This card does not tell you to keep running a leaking rig or to increase an acid amount.",
            ),
        ),
    ),
    _lesson(
        "trouble-water",
        ("trouble",),
        "water",
        "Saf su sorunları",
        "Pure-water problems",
        "Yüksek iletkenlik tek bir parçanın suçlanması için yetmez.",
        "High conductivity is not enough to blame one part.",
        (
            (
                "Ne kontrol edilir",
                "What is checked",
                "Bağlantı, kartuş veya membran değişim kaydı ve toplama kabının temizliği bakılır. Değişim süresi üreticidedir.",
                "The connection, the cartridge or membrane change record, and the cleanliness of the collection vessel are checked. The change interval is the manufacturer's.",
            ),
            (
                "Sınır",
                "Limit",
                "İletkenlik organik kirliliği göstermez. Kabul sayısı burada yoktur.",
                "Conductivity does not show organic contamination. An acceptance number is not stated here.",
            ),
        ),
    ),
    _lesson(
        "trouble-tests",
        ("trouble",),
        None,
        "Test gözlemi karışınca",
        "When a test observation is mixed",
        "Renk, kabarcık ve floresans tek başına ad koymaz.",
        "Color, bubbles, and fluorescence do not assign a name by themselves.",
        (
            (
                "Ne yapılır",
                "What is done",
                "Gözlem yeniden, temiz kapta ve kör örnekle karşılaştırılır. Kör örneğin tarifi onaylı yöntemdedir. Burada derişim yoktur.",
                "The observation is repeated in a clean vessel and compared with a blank. The blank's recipe is in an approved method. No strength is stated here.",
            ),
            (
                "Ne denmez",
                "What is not said",
                "UV parlıyorsa hidrokarbon vardır denmez. Siyahsa kömürdür denmez. Beyazsa jipstir denmez.",
                "Do not say hydrocarbon is present because it glows under UV. Do not say it is coal because it is black. Do not say it is gypsum because it is white.",
            ),
        ),
    ),
)

from app.handbook_lessons import annotate, extra_lessons

ALL_LESSONS = annotate(list(LESSONS + ROCKS + SHOWS + MEASURE + SAFETY + TROUBLE)) + extra_lessons()


def lesson_title(lesson: dict, lang: str) -> str:
    return lesson["title_en"] if lang == "en" else lesson["title_tr"]


def lesson_summary(lesson: dict, lang: str) -> str:
    return lesson["summary_en"] if lang == "en" else lesson["summary_tr"]


def lesson_text(lesson: dict, lang: str) -> str:
    parts = [lesson_title(lesson, lang), lesson_summary(lesson, lang)]
    for section in lesson["sections"]:
        parts.append(section["title_en"] if lang == "en" else section["title_tr"])
        parts.append(section["body_en"] if lang == "en" else section["body_tr"])
    return "\n".join(parts)


def find_lesson(lesson_id: str) -> dict | None:
    for lesson in ALL_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    return None


def filter_lessons(query: str, category: str) -> list[dict]:
    needle = " ".join(query.casefold().split())
    found = []
    for lesson in ALL_LESSONS:
        if category and category != "all" and category not in lesson["categories"]:
            continue
        if needle:
            haystack = " ".join(
                [
                    lesson["title_tr"],
                    lesson["title_en"],
                    lesson["summary_tr"],
                    lesson["summary_en"],
                    lesson["id"],
                ]
            ).casefold()
            if needle not in haystack:
                continue
        found.append(lesson)
    return found
