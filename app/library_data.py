"""Identity cards for the chemical library.

Formulas and names are chemical identity. Hazard, GHS, PPE, storage,
emergency, and SDS fields are intentionally unverified: this file does not
assign them.
"""

from __future__ import annotations

NEEDS_VERIFICATION = "needs_verification"

STARTERS = (
    {
        "id": "hcl",
        "name_tr": "Hidroklorik asit",
        "name_en": "Hydrochloric acid",
        "formula": "HCl",
        "category": "acid",
        "aliases": ("hcl", "hidroklorik", "hydrochloric", "hidrojen klorür"),
        "identity_tr": "Formülü HCl olan hidrojen klorürdür. Sulu çözeltisine hidroklorik asit denir.",
        "identity_en": "Hydrogen chloride, formula HCl. Its solution in water is called hydrochloric acid.",
    },
    {
        "id": "caco3",
        "name_tr": "Kalsiyum karbonat",
        "name_en": "Calcium carbonate",
        "formula": "CaCO3",
        "category": "mineral",
        "aliases": ("caco3", "kalsiyum karbonat", "calcium carbonate", "kalsit"),
        "identity_tr": "Formülü CaCO3 olan bir kalsiyum tuzudur.",
        "identity_en": "A calcium salt with the formula CaCO3.",
    },
    {
        "id": "acetone",
        "name_tr": "Aseton",
        "name_en": "Acetone",
        "formula": "C3H6O",
        "category": "solvent",
        "aliases": ("aseton", "acetone", "propanon", "c3h6o"),
        "identity_tr": "Formülü C3H6O olan bir ketondur. Yaygın adı asetondur.",
        "identity_en": "A ketone with the formula C3H6O. Its common name is acetone.",
    },
    {
        "id": "nacl",
        "name_tr": "Sodyum klorür",
        "name_en": "Sodium chloride",
        "formula": "NaCl",
        "category": "salt",
        "aliases": ("nacl", "sodyum klorür", "sodium chloride", "tuz"),
        "identity_tr": "Formülü NaCl olan bir tuzdur.",
        "identity_en": "A salt with the formula NaCl.",
    },
    {
        "id": "naoh",
        "name_tr": "Sodyum hidroksit",
        "name_en": "Sodium hydroxide",
        "formula": "NaOH",
        "category": "base",
        "aliases": ("naoh", "sodyum hidroksit", "sodium hydroxide", "kostik"),
        "identity_tr": "Formülü NaOH olan bir bazdır.",
        "identity_en": "A base with the formula NaOH.",
    },
    {
        "id": "kcl",
        "name_tr": "Potasyum klorür",
        "name_en": "Potassium chloride",
        "formula": "KCl",
        "category": "salt",
        "aliases": ("kcl", "potasyum klorür", "potasyum klorur", "potassium chloride"),
        "identity_tr": "Formülü KCl olan bir tuzdur.",
        "identity_en": "A salt with the formula KCl.",
    },
    {
        "id": "ipa",
        "name_tr": "İzopropil alkol",
        "name_en": "Isopropyl alcohol",
        "formula": "C3H8O",
        "category": "solvent",
        "aliases": ("izopropil", "isopropyl", "ipa", "propan-2-ol", "izopropanol"),
        "identity_tr": "Formülü C3H8O olan bir alkoldür. Yaygın adı izopropil alkoldür.",
        "identity_en": "An alcohol with the formula C3H8O. Its common name is isopropyl alcohol.",
    },
)


def user_record(row: dict) -> dict:
    name = row["name"]
    return {
        "id": f"user:{row['id']}",
        "name_tr": name,
        "name_en": name,
        "formula": row["formula"] or "—",
        "category": row["category"],
        "aliases": (name,),
        "identity_tr": name,
        "identity_en": name,
        "user_note": row["user_note"],
        "source": "user",
    }


def all_records(additions: list[dict]) -> list[dict]:
    records = [dict(item, source="starter", user_note="") for item in STARTERS]
    records.extend(user_record(row) for row in additions)
    return records


def record_name(record: dict, lang: str) -> str:
    return record["name_en"] if lang == "en" else record["name_tr"]


GENERAL = {
    "hcl": {
        "use_tr": "Laboratuvarlarda güçlü bir mineral asit olarak tanınır. Bu kart işyerinin prosedürünü vermez.",
        "use_en": "Known in laboratories as a strong mineral acid. This card does not give the site procedure.",
        "hazard_tr": "Genel bilgi: hidroklorik asit çözeltileri cilt ve göz için aşındırıcı olabilir. Bu şişenin etiketi doğrulanmadı.",
        "hazard_en": "General information: hydrochloric acid solutions can be corrosive to skin and eyes. This bottle's label is not verified.",
        "storage_tr": "Kabını kapalı tutma ve ayırma koşulları ürün SDS'sindedir. Bu kart sıcaklık veya raf talimatı vermez.",
        "storage_en": "Keeping the container closed and segregation are in the product SDS. This card does not give a temperature or shelf instruction.",
        "source_tr": "Genel kaynak: PubChem CID 313 (Hydrochloric acid) ve Regulation (EC) No 1272/2008 Annex VI. Bunlar bu ürünün SDS belgesi değildir.",
        "source_en": "General source: PubChem CID 313 (Hydrochloric acid) and Regulation (EC) No 1272/2008 Annex VI. These are not this product's SDS.",
    },
    "caco3": {
        "use_tr": "Kalsiyumun karbonat tuzudur. Laboratuvarda katı madde olarak tanınır. Kullanım amacı iş prosedüründen okunur.",
        "use_en": "It is the carbonate salt of calcium. Laboratories know it as a solid. The purpose is read from the site procedure.",
        "hazard_tr": "Bu uygulama kalsiyum karbonata bir GHS piktogramı atamaz. Toz ve ürün sınıfı SDS'ye bağlıdır.",
        "hazard_en": "This application does not assign a GHS pictogram to calcium carbonate. Dust and the product class depend on the SDS.",
        "storage_tr": "Kuru ve kapalı tutma koşulları ürün SDS'sindedir.",
        "storage_en": "Dry and closed storage conditions are in the product SDS.",
        "source_tr": "Genel kaynak: PubChem CID 10112 (Calcium carbonate). Bu, ürün SDS'si değildir.",
        "source_en": "General source: PubChem CID 10112 (Calcium carbonate). This is not the product SDS.",
    },
    "acetone": {
        "use_tr": "Yaygın bir laboratuvar çözücüsüdür. Bu kart bir temizlik veya seyreltme talimatı değildir.",
        "use_en": "It is a common laboratory solvent. This card is not a cleaning or dilution instruction.",
        "hazard_tr": "Genel bilgi: aseton kolay alevlenir bir sıvı olarak sınıflandırılan bir çözücüdür. Bu şişenin etiket piktogramları doğrulanmadı.",
        "hazard_en": "General information: acetone is a solvent classified as a highly flammable liquid. This bottle's label pictograms are not verified.",
        "storage_tr": "Tutuşturma kaynaklarından uzak tutma kuralı ürün SDS'sindedir. Bu kart bir depolama prosedürü değildir.",
        "storage_en": "Keeping it away from ignition sources is in the product SDS. This card is not a storage procedure.",
        "source_tr": "Genel kaynak: PubChem CID 180 (Acetone) ve Regulation (EC) No 1272/2008 Annex VI. Bunlar bu ürünün SDS belgesi değildir.",
        "source_en": "General source: PubChem CID 180 (Acetone) and Regulation (EC) No 1272/2008 Annex VI. These are not this product's SDS.",
    },
    "nacl": {
        "use_tr": "Yaygın bir tuzdur. Laboratuvarda çözelti ve referans maddesi olarak tanınır. İşyerindeki amaç prosedürden okunur.",
        "use_en": "It is a common salt. Laboratories know it as a solution and a reference material. The site purpose is read from the procedure.",
        "hazard_tr": "Bu uygulama sodyum klorüre bir GHS piktogramı atamaz.",
        "hazard_en": "This application does not assign a GHS pictogram to sodium chloride.",
        "storage_tr": "Kapalı kap ve nem koşulları ürün SDS'sindedir.",
        "storage_en": "A closed container and moisture conditions are in the product SDS.",
        "source_tr": "Genel kaynak: PubChem CID 5234 (Sodium chloride). Bu, ürün SDS'si değildir.",
        "source_en": "General source: PubChem CID 5234 (Sodium chloride). This is not the product SDS.",
    },
    "naoh": {
        "use_tr": "Güçlü bir baz olarak tanınır. Çözelti hazırlama talimatı bu kartta yoktur.",
        "use_en": "It is known as a strong base. This card has no instruction for preparing a solution.",
        "hazard_tr": "Genel bilgi: sodyum hidroksit katısı ve çözeltileri cilt ve göz için aşındırıcı olabilir. Bu şişenin etiketi doğrulanmadı.",
        "hazard_en": "General information: sodium hydroxide solid and solutions can be corrosive to skin and eyes. This bottle's label is not verified.",
        "storage_tr": "Nemden koruma ve ayırma koşulları ürün SDS'sindedir.",
        "storage_en": "Protection from moisture and segregation are in the product SDS.",
        "source_tr": "Genel kaynak: PubChem CID 14798 (Sodium hydroxide) ve Regulation (EC) No 1272/2008 Annex VI. Bunlar bu ürünün SDS belgesi değildir.",
        "source_en": "General source: PubChem CID 14798 (Sodium hydroxide) and Regulation (EC) No 1272/2008 Annex VI. These are not this product's SDS.",
    },
    "kcl": {
        "use_tr": "Potasyumun klorür tuzudur. Laboratuvar ve sondaj sıvısı bağlamında adı geçer. Bu kart bir çamur reçetesi değildir.",
        "use_en": "It is the chloride salt of potassium. The name appears in laboratory and drilling-fluid contexts. This card is not a mud recipe.",
        "hazard_tr": "Bu uygulama potasyum klorüre bir GHS piktogramı atamaz.",
        "hazard_en": "This application does not assign a GHS pictogram to potassium chloride.",
        "storage_tr": "Kapalı kap koşulları ürün SDS'sindedir.",
        "storage_en": "Closed-container conditions are in the product SDS.",
        "source_tr": "Genel kaynak: PubChem CID 4873 (Potassium chloride). Bu, ürün SDS'si değildir.",
        "source_en": "General source: PubChem CID 4873 (Potassium chloride). This is not the product SDS.",
    },
    "ipa": {
        "use_tr": "Yaygın bir alkol çözücüsüdür. Bu kart bir temizlik talimatı değildir.",
        "use_en": "It is a common alcohol solvent. This card is not a cleaning instruction.",
        "hazard_tr": "Genel bilgi: izopropil alkol kolay alevlenir bir sıvı olarak sınıflandırılan bir çözücüdür. Bu şişenin etiket piktogramları doğrulanmadı.",
        "hazard_en": "General information: isopropyl alcohol is a solvent classified as a highly flammable liquid. This bottle's label pictograms are not verified.",
        "storage_tr": "Tutuşturma kaynaklarından uzak tutma kuralı ürün SDS'sindedir.",
        "storage_en": "Keeping it away from ignition sources is in the product SDS.",
        "source_tr": "Genel kaynak: PubChem CID 3776 (Isopropyl alcohol) ve Regulation (EC) No 1272/2008 Annex VI. Bunlar bu ürünün SDS belgesi değildir.",
        "source_en": "General source: PubChem CID 3776 (Isopropyl alcohol) and Regulation (EC) No 1272/2008 Annex VI. These are not this product's SDS.",
    },
}


def general_field(record: dict, field: str, lang: str) -> str:
    block = GENERAL.get(record["id"], {})
    return block.get(f"{field}_{'en' if lang == 'en' else 'tr'}", "")


def record_identity(record: dict, lang: str) -> str:
    return record["identity_en"] if lang == "en" else record["identity_tr"]


def filter_records(records: list[dict], query: str, category: str) -> list[dict]:
    needle = " ".join(query.casefold().split())
    found = []
    for record in records:
        if category and category != "all" and record["category"] != category:
            continue
        if needle:
            haystack = " ".join(
                [
                    record["name_tr"],
                    record["name_en"],
                    record["formula"],
                    " ".join(record.get("aliases") or ()),
                ]
            ).casefold()
            if needle not in haystack:
                continue
        found.append(record)
    return found
