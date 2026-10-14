"""
Diş turizmi PAKET sayfaları için veri — programatik SEO.

Sayfa tipleri (hepsi 17 dilde, hepsi sitemap'te, hiçbirinde fiyat yok):
  hub        /packages/                                   dental tourism packages
  treatment  /packages/<tedavi>/                          <tedavi> package in Istanbul
  origin     /dental-holidays-from/<ülke>/                dental holiday packages from <ülke>
  compare    /packages/compare-destinations/              Turkey vs Mexico, Thailand, Vietnam, Bali, Hungary…
"""
from babel import Locale
from slugify import slugify

from dental_tourism.languages import LANGUAGE_META

# Köken ülkeler: İstanbul'a yaklaşık uçuş süresi (saat, direkt veya tek aktarmalı) ve bilinen kalkış şehirleri.
# Uzun mesafeli ülkelerde (long_haul) tedavi tek / az sayıda seyahate göre planlanır.
ORIGINS = {
    "GB": {"hours": 4, "cities": ["London", "Manchester", "Birmingham", "Edinburgh"]},
    "IE": {"hours": 4, "cities": ["Dublin"]},
    "US": {"hours": 10, "cities": ["New York", "Chicago", "Los Angeles"], "long_haul": True},
    "CA": {"hours": 10, "cities": ["Toronto", "Montreal", "Vancouver"], "long_haul": True},
    "AU": {"hours": 20, "cities": ["Sydney", "Melbourne", "Brisbane", "Perth"], "long_haul": True},
    "NZ": {"hours": 24, "cities": ["Auckland", "Christchurch"], "long_haul": True},
    "DE": {"hours": 3, "cities": ["Berlin", "Frankfurt", "München", "Hamburg", "Köln", "Düsseldorf"]},
    "AT": {"hours": 2.5, "cities": ["Wien", "Graz", "Salzburg"]},
    "CH": {"hours": 3, "cities": ["Zürich", "Genève", "Basel"]},
    "NL": {"hours": 3.5, "cities": ["Amsterdam", "Rotterdam", "Eindhoven"]},
    "BE": {"hours": 3.5, "cities": ["Brussel", "Antwerpen"]},
    "FR": {"hours": 3.5, "cities": ["Paris", "Lyon", "Marseille"]},
    "IT": {"hours": 2.5, "cities": ["Roma", "Milano"]},
    "ES": {"hours": 4, "cities": ["Madrid", "Barcelona"]},
    "PL": {"hours": 2.5, "cities": ["Warszawa", "Kraków"]},
    "RU": {"hours": 4, "cities": ["Москва", "Санкт-Петербург"]},
    "KZ": {"hours": 5, "cities": ["Алматы", "Астана"]},
    "BY": {"hours": 3, "cities": ["Минск"]},
    "UA": {"hours": 3, "cities": ["Київ", "Одеса"]},
    "SA": {"hours": 4, "cities": ["الرياض", "جدة"]},
    "AE": {"hours": 4.5, "cities": ["دبي", "أبوظبي"]},
    "IQ": {"hours": 3, "cities": ["بغداد", "أربيل"]},
    "KW": {"hours": 3.5, "cities": ["الكويت"]},
    "QA": {"hours": 4, "cities": ["الدوحة"]},
    "BH": {"hours": 4, "cities": ["المنامة"]},
    "OM": {"hours": 5, "cities": ["مسقط"]},
    "SE": {"hours": 3.5, "cities": ["Stockholm", "Göteborg"]},
    "DK": {"hours": 3, "cities": ["København", "Aarhus"]},
    "NO": {"hours": 3.5, "cities": ["Oslo", "Bergen"]},
    "RO": {"hours": 1.5, "cities": ["București", "Cluj-Napoca"]},
    "MD": {"hours": 1.5, "cities": ["Chișinău"]},
    "BG": {"hours": 1.5, "cities": ["София", "Пловдив", "Варна", "Бургас"]},
    "AZ": {"hours": 3, "cities": ["Bakı"]},
    "TR": {"hours": 0, "cities": ["İstanbul", "Ankara", "İzmir"]},
}

# Karşılaştırma sayfasındaki destinasyonlar (fiyat yok — nitel karşılaştırma)
DESTINATIONS = ["MX", "TH", "VN", "ID", "HU", "HR", "AL", "IN", "CR", "PH"]

NON_LATIN_SLUG_FROM_EN = {"ar"}
# Otomatik transliterasyonu kötü olan ülke slug'ları: {dil: {ülke: slug}}
COUNTRY_SLUG_OVERRIDES = {"bg": {"BG": "bulgaria"}}


def origin_codes(lang):
    """Bu dilde origin sayfası olan ülkeler (dilin hedef pazarları; TR hariç)."""
    return [c for c in LANGUAGE_META[lang]["markets"] if c in ORIGINS and c != "TR"]


def country_name(code, lang):
    try:
        return Locale.parse(lang).territories.get(code, code)
    except Exception:  # noqa: BLE001
        return Locale.parse("en").territories.get(code, code)


def country_slug(code, lang):
    if code in COUNTRY_SLUG_OVERRIDES.get(lang, {}):
        return COUNTRY_SLUG_OVERRIDES[lang][code]
    name = country_name(code, "en" if lang in NON_LATIN_SLUG_FROM_EN else lang)
    return slugify(name)


def code_from_slug(slug, lang):
    for code in origin_codes(lang):
        if country_slug(code, lang) == slug:
            return code
    return None


def langs_for_origin(code):
    return [lg for lg in LANGUAGE_META if code in origin_codes(lg)]


# ── Keyword kalıpları (sayfalarda kullanılan + .md raporuna yazılan) ─────────
# {t}=tedavi adı (o dilde), {c}=ülke adı (o dilde), {city}=kalkış şehri
PACKAGE_KEYWORDS = {
    "en": {
        "hub": ["dental tourism packages", "dental travel packages", "dental vacation packages turkey",
                "dental holiday packages turkey", "all inclusive dental tourism packages 2026",
                "best dental tourism packages", "dental tourism packages 2026 prices", "what is dental tourism",
                "what is tourism package", "dental visit turkey", "exclusive dental team travel",
                "dental tourism websites", "cheap dental tourism packages"],
        "treatment": ["{t} package turkey", "{t} package istanbul", "{t} holiday package", "{t} all inclusive turkey"],
        "origin": ["dental holiday packages from {c}", "dental tourism packages from {c}",
                   "dental holiday packages from {city}", "dental travel turkey from {c}"],
        "compare": ["mexico dental tourism packages all inclusive", "dental vacation packages mexico",
                    "best mexico dental tourism packages", "cancun dental vacation packages all inclusive",
                    "thailand dental tourism packages all inclusive", "dental tourism thailand cost",
                    "thailand dental holiday packages from australia", "vietnam dental tourism packages",
                    "vietnam dental holiday packages from australia", "vietnam dental holiday packages from nz",
                    "bali dental holiday packages all inclusive", "bali dental holiday packages from nz",
                    "dental holiday packages bali", "dental holiday packages hungary", "dental holiday packages croatia",
                    "dental tourism albania packages", "dental tourism packages in india",
                    "dental tourism packages costa rica", "dental holiday packages philippines",
                    "mexico dental tourism packages reddit"],
    },
    "de": {"hub": ["zahnbehandlung türkei paket", "zahnurlaub türkei", "zahntourismus türkei pakete",
                   "zahnreise türkei all inclusive", "was ist zahntourismus"],
           "treatment": ["{t} türkei paket", "{t} istanbul komplettpaket", "{t} zahnurlaub türkei"],
           "origin": ["zahnurlaub türkei aus {c}", "zahnbehandlung türkei von {c}", "zahnreise istanbul ab {city}"],
           "compare": ["zahnurlaub ungarn oder türkei", "zahnbehandlung kroatien oder türkei", "zahntourismus vergleich"]},
    "nl": {"hub": ["tandarts turkije pakket", "tandartsvakantie turkije", "tandheelkundig toerisme pakketten",
                   "tandarts reis turkije all inclusive", "wat is tandheelkundig toerisme"],
           "treatment": ["{t} turkije pakket", "{t} istanbul all inclusive", "{t} tandartsreis"],
           "origin": ["tandartsvakantie turkije vanuit {c}", "tandarts turkije vanuit {c}", "tandartsreis vanaf {city}"],
           "compare": ["tandarts hongarije of turkije", "tandartsvakantie vergelijken"]},
    "fr": {"hub": ["forfait soins dentaires turquie", "tourisme dentaire turquie forfait", "séjour dentaire turquie",
                   "voyage dentaire tout compris", "qu'est-ce que le tourisme dentaire"],
           "treatment": ["forfait {t} turquie", "{t} istanbul tout compris", "séjour {t} turquie"],
           "origin": ["séjour dentaire turquie depuis {c}", "tourisme dentaire turquie depuis {c}", "voyage dentaire depuis {city}"],
           "compare": ["soins dentaires hongrie ou turquie", "tourisme dentaire comparatif"]},
    "it": {"hub": ["pacchetto dentista turchia", "turismo dentale turchia pacchetti", "vacanza dentale turchia",
                   "viaggio dentale tutto incluso", "cos'è il turismo dentale"],
           "treatment": ["pacchetto {t} turchia", "{t} istanbul tutto incluso", "vacanza {t} turchia"],
           "origin": ["turismo dentale turchia dall'{c}", "vacanza dentale turchia da {c}", "dentista istanbul da {city}"],
           "compare": ["dentista ungheria o turchia", "turismo dentale confronto"]},
    "es": {"hub": ["paquete dental turquía", "turismo dental turquía paquetes", "vacaciones dentales turquía",
                   "viaje dental todo incluido", "qué es el turismo dental"],
           "treatment": ["paquete {t} turquía", "{t} estambul todo incluido", "viaje {t} turquía"],
           "origin": ["turismo dental turquía desde {c}", "viaje dental turquía desde {c}", "dentista estambul desde {city}"],
           "compare": ["turismo dental méxico o turquía", "turismo dental comparativa"]},
    "pl": {"hub": ["turystyka dentystyczna turcja pakiet", "leczenie zębów turcja pakiet", "wakacje dentystyczne turcja",
                   "co to jest turystyka dentystyczna"],
           "treatment": ["{t} turcja pakiet", "{t} stambuł all inclusive"],
           "origin": ["leczenie zębów w turcji z {c}", "turystyka dentystyczna z {c}", "dentysta stambuł z {city}"],
           "compare": ["leczenie zębów węgry czy turcja", "turystyka dentystyczna porównanie"]},
    "ru": {"hub": ["стоматологический тур в турцию", "лечение зубов в турции пакет", "стоматологический туризм турция",
                   "что такое стоматологический туризм"],
           "treatment": ["{t} в турции пакет", "{t} стамбул тур"],
           "origin": ["лечение зубов в турции из {c}", "стоматологический тур из {c}", "стоматология стамбул из {city}"],
           "compare": ["лечение зубов в турции или венгрии", "стоматологический туризм сравнение"]},
    "uk": {"hub": ["стоматологічний тур туреччина", "лікування зубів у туреччині пакет", "стоматологічний туризм туреччина"],
           "treatment": ["{t} туреччина пакет", "{t} стамбул тур"],
           "origin": ["лікування зубів у туреччині з {c}", "стоматологічний тур з {c}"],
           "compare": ["стоматологічний туризм порівняння"]},
    "ar": {"hub": ["باقات السياحة العلاجية للأسنان في تركيا", "رحلة علاج الأسنان في تركيا", "ما هي السياحة العلاجية للأسنان"],
           "treatment": ["باقة {t} في تركيا", "{t} في إسطنبول شامل"],
           "origin": ["علاج الأسنان في تركيا من {c}", "رحلة علاج الأسنان من {c}", "طبيب أسنان إسطنبول من {city}"],
           "compare": ["علاج الأسنان في تركيا أم المجر", "مقارنة السياحة العلاجية للأسنان"]},
    "sv": {"hub": ["tandvårdsresa turkiet paket", "tandvård turkiet paketresa", "vad är tandturism"],
           "treatment": ["{t} turkiet paket", "{t} istanbul paketresa"],
           "origin": ["tandvårdsresa turkiet från {c}", "tandläkare istanbul från {city}"],
           "compare": ["tandvård ungern eller turkiet"]},
    "da": {"hub": ["tandlægerejse tyrkiet pakke", "tandbehandling tyrkiet pakkerejse", "hvad er tandturisme"],
           "treatment": ["{t} tyrkiet pakke", "{t} istanbul pakkerejse"],
           "origin": ["tandlægerejse tyrkiet fra {c}", "tandlæge istanbul fra {city}"],
           "compare": ["tandlæge ungarn eller tyrkiet"]},
    "no": {"hub": ["tannlegereise tyrkia pakke", "tannbehandling tyrkia pakkereise", "hva er tannturisme"],
           "treatment": ["{t} tyrkia pakke", "{t} istanbul pakkereise"],
           "origin": ["tannlegereise tyrkia fra {c}", "tannlege istanbul fra {city}"],
           "compare": ["tannlege ungarn eller tyrkia"]},
    "ro": {"hub": ["pachet stomatologic turcia", "turism dentar turcia pachete", "ce este turismul dentar"],
           "treatment": ["pachet {t} turcia", "{t} istanbul all inclusive"],
           "origin": ["turism dentar turcia din {c}", "dentist istanbul din {city}"],
           "compare": ["dentist ungaria sau turcia"]},
    "bg": {"hub": ["дентален туризъм турция пакет", "лечение на зъби в турция пакет", "дентална почивка турция",
                   "какво е дентален туризъм"],
           "treatment": ["{t} турция пакет", "{t} истанбул пакет"],
           "origin": ["лечение на зъби в турция от {c}", "зъболекар истанбул от {city}"],
           "compare": ["зъби в турция или унгария", "дентален туризъм сравнение"]},
    "az": {"hub": ["türkiyədə diş müalicəsi paketi", "diş turizmi türkiyə", "diş turizmi nədir"],
           "treatment": ["{t} türkiyə paketi", "{t} istanbul paket"],
           "origin": ["{c}dan türkiyəyə diş müalicəsi", "bakıdan istanbula diş müalicəsi"],
           "compare": ["diş turizmi müqayisə"]},
    "tr": {"hub": ["diş turizmi paketleri", "diş tedavisi tatil paketi", "yurt dışından gelen hastalar için diş paketi",
                   "diş turizmi nedir"],
           "treatment": ["{t} paketi istanbul", "{t} tatil paketi"],
           "origin": ["{c} türkiye diş tedavisi", "{city} istanbul diş tedavisi"],
           "compare": ["diş turizmi türkiye macaristan karşılaştırma"]},
}


def keywords_for(lang, page_type, treatment_name="", country="", cities=()):
    out = []
    for pat in PACKAGE_KEYWORDS.get(lang, {}).get(page_type, []):
        if "{city}" in pat:
            out += [pat.format(t=treatment_name.lower(), c=country.lower(), city=city.lower()) for city in cities[:3]]
        else:
            out.append(pat.format(t=treatment_name.lower(), c=country.lower()))
    return out
