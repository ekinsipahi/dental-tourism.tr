"""
Üç sitenin farklı URL'lerini ortak "sayfa anlamına" eşler — birleşik yolculuk tek dille okunur:
home · pseo-area · treatment · price · package · guide · origin · doctor · clinic · contact · qa · blog · reviews ·
redirect (tıkla-ara yönlendirme sayfaları) · booking · thanks · page
"""
import re

_RULES = {
    "dt": [  # dentaltourism.tr: sayfa türü şablondan (PAGE_TYPE) gelir; bu tablo yalnızca yedek
        (r"^/(?:[a-z]{2}/)?$", "home"),
        (r"/(?:treatments|behandlungen|tedaviler|lechenie|behandelingen|traitements|trattamenti|tratamientos)/[^/]+/[^/]+/$", "treatment-city"),
        (r"/(?:treatments|behandlungen|tedaviler|lechenie|behandelingen|traitements|trattamenti|tratamientos)/", "treatment"),
        (r"/(?:prices|preise|fiyatlar|ceny|prijzen|prix|prezzi|precios)/", "price"),
        (r"/(?:packages|pakete|paketler|pakety|pakketten|forfaits|pacchetti|paquetes)/", "package"),
        (r"/(?:guide|ratgeber|rehber|gid|gids|rakovodstvo)/", "guide"),
        (r"/(?:dental-clinic|zahnarzt|dis-klinigi|stomatologiya)/", "pseo-area"),
        (r"/(?:dental-holidays-from|dentalen-turizam-ot|stomatologicheskiy-tur-iz)/", "origin"),
        (r"/(?:clinics|kliniken|klinikler|kliniki)/", "clinic"),
        (r"/(?:dentists|zahnaerzte|dis-hekimleri|stomatologi)/", "doctor"),
        (r"/blog/", "blog"),
        (r"/(?:contact|kontakt|iletisim|kontakty)/", "contact"),
        (r"/(?:about|ueber-uns|hakkimizda|o-nas)/", "about"),
    ],
    "drd": [  # drdevrim.com (Nuxt): TR kökte, diğer diller /lang/<kod>/
        (r"^/(?:lang/[a-z]{2}/?)?$", "home"),
        (r"^/(?:en/dentist|de/zahnarzt|ru/stomatolog|uk/stomatolog|bg/zabolekar|disci|haftasonu|en-iyi-disci|"
         r"uzman-dis-hekimi|prof-dis-hekimi|estetik-dis-klinigi)(?:/|$)", "pseo-area"),
        (r"^/hizmetler/", "treatment"),
        (r"^/doktorlar", "doctor"),
        (r"^/iletisim", "contact"),
        (r"^/hasta-yorumlari", "reviews"),
        (r"^/blog", "blog"),
    ],
    "dbs": [  # devrimbirikensipahi.com.tr (Django): TR kökte, diğer diller /<kod>/
        (r"^/(?:[a-z]{2}/)?$", "home"),
        (r"/(?:telefon|whatsapp|maps|instagram)-yonlendirme/", "redirect"),
        (r"/randevu-al", "booking"),
        (r"/(?:tesekkur|callme-tesekkur)", "thanks"),
        (r"/onay/", "confirmation"),
        (r"/dental-tourism", "dental-tourism"),
        (r"/(?:acil-dis|emergency|notfall|urgence|urgenza|urgencia)", "emergency"),   # "acil diş hekimi" — şimdi, hemen
        (r"/(?:neden-biz|why-us|warum-wir|waarom-wij|pourquoi|perche|por-que|dlaczego|pochemu|zashto)", "about"),
        (r"/sisli-dis-(?:hekimi|klinigi)", "pseo-area"),
        (r"/(?:kvkk|privacy|accounts|gizlilik)/", "page"),
        (r"/(?:soru-cevap|question-and-answer)/", "qa"),
        (r"/blog/", "blog"),
        (r"^/(?:[a-z]{2}/)?[a-z0-9-]+/?$", "treatment"),  # kategori sayfaları (8 tedavi slug'ı)
    ],
}
_COMPILED = {site: [(re.compile(p), t) for p, t in rules] for site, rules in _RULES.items()}


def page_type_for(site, path, hint=""):
    """hint: sayfanın kendi bildirdiği tür (dentaltourism şablonları PAGE_TYPE gönderir) — varsa o kazanır."""
    if hint:
        return str(hint)[:40]
    if site == "drd":   # /lang/en/hizmetler/… → /hizmetler/… (dil öneki tür belirlemez)
        path = re.sub(r"^/lang/[a-z]{2}(?=/|$)", "", path or "/") or "/"
    for pattern, kind in _COMPILED.get(site, ()):
        if pattern.search(path or "/"):
            return kind
    return "page"
