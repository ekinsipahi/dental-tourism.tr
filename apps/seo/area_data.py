"""
Semt (ilçe / mahalle) sayfaları — programatik yerel SEO: "dental clinic şişli", "dentist taksim", "zahnarzt nişantaşı" …

URL: /<dil>/<dental-clinic segmenti>/<semt>/   (EN: /dental-clinic/nisantasi/)  — 17 dil, hepsi sitemap'te, FİYAT YOK.
Hub: /<dil>/<dental-clinic segmenti>/

Klinik Şişli'de (Abide-i Hürriyet Cd 148 — koordinat Google Maps kaydından). Semtler kliniğin çevresindeki,
ulaşımı kolay merkezler. "in" = klinik o semtte, "near" = yakın semt (sayfa mesafeyi ve yolu dürüstçe söyler).
Mesafe koordinatlardan hesaplanır (kuş uçuşu); taksi / yürüme süresi mesafeden kaba aralık olarak türetilir.
"""
from math import asin, cos, radians, sin, sqrt

CLINIC_LOC = (41.066152, 28.982098)
NEAREST_STATION = ("Şişli-Mecidiyeköy", (41.0641, 28.9930))

# metro: [(hat, biniş, iniş), …]  — iniş hep Şişli-Mecidiyeköy (M2/M7)
# places: semtin bilinen yerleri (özel isim, çevrilmez)
# names: Latin olmayan alfabeli dillerde semt adı (diğer dillerde Türkçe yazımı kullanılır)
AREAS = {
    "sisli": {"name": "Şişli", "kind": "in", "loc": (41.0602, 28.9871), "order": 1,
              "metro": [("M2", "Osmanbey", "Şişli-Mecidiyeköy")], "places": ["Şişli Camii", "Bomonti", "Cevahir"],
              "names": {"ru": "Шишли", "uk": "Шишлі", "bg": "Шишли", "ar": "شيشلي"}},
    "osmanbey": {"name": "Osmanbey", "kind": "near", "loc": (41.0524, 28.9874), "order": 2,
                 "metro": [("M2", "Osmanbey", "Şişli-Mecidiyeköy")],
                 "places": ["Halaskargazi Caddesi", "Rumeli Caddesi", "Pangaltı"],
                 "names": {"ru": "Османбей", "uk": "Османбей", "bg": "Османбей", "ar": "عثمان باي"}},
    "nisantasi": {"name": "Nişantaşı", "kind": "near", "loc": (41.0503, 28.9937), "order": 3,
                  "metro": [("M2", "Osmanbey", "Şişli-Mecidiyeköy")],
                  "places": ["Teşvikiye", "Abdi İpekçi Caddesi", "Maçka Parkı"],
                  "names": {"ru": "Нишанташи", "uk": "Нішанташи", "bg": "Нишанташъ", "ar": "نيشانتاشي"}},
    "taksim": {"name": "Taksim", "kind": "near", "loc": (41.0370, 28.9850), "order": 4,
               "metro": [("M2", "Taksim", "Şişli-Mecidiyeköy")],
               "places": ["Taksim Meydanı", "İstiklal Caddesi", "Cihangir", "Harbiye"],
               "names": {"ru": "Таксим", "uk": "Таксим", "bg": "Таксим", "ar": "تقسيم"}},
    "mecidiyekoy": {"name": "Mecidiyeköy", "kind": "near", "loc": (41.0670, 28.9960), "order": 5,
                    "metro": [], "places": ["Cevahir", "Esentepe", "Trump Towers"],
                    "names": {"ru": "Меджидиекёй", "uk": "Меджидієкьой", "bg": "Меджидиекьой", "ar": "مجيدية كوي"}},
    "gayrettepe": {"name": "Gayrettepe", "kind": "near", "loc": (41.0680, 29.0075), "order": 6,
                   "metro": [("M2", "Gayrettepe", "Şişli-Mecidiyeköy")], "places": ["Fulya", "Esentepe", "Zincirlikuyu"],
                   "names": {"ru": "Гайреттепе", "uk": "Гайреттепе", "bg": "Гайретепе", "ar": "غايرت تبه"}},
    "kagithane": {"name": "Kağıthane", "kind": "near", "loc": (41.0825, 28.9715), "order": 7,
                  "metro": [("M7", "Kağıthane", "Mecidiyeköy")], "places": ["Çağlayan", "Gültepe"],
                  "names": {"ru": "Кягытхане", "uk": "Кягитхане", "bg": "Кяатхане", "ar": "كاغيتهانه"}},
    "besiktas": {"name": "Beşiktaş", "kind": "near", "loc": (41.0430, 29.0070), "order": 8,
                 "metro": [], "places": ["Beşiktaş Çarşı", "Dolmabahçe", "Barbaros Bulvarı"],
                 "names": {"ru": "Бешикташ", "uk": "Бешикташ", "bg": "Бешикташ", "ar": "بشكتاش"}},
    "ortakoy": {"name": "Ortaköy", "kind": "near", "loc": (41.0475, 29.0270), "order": 9,
                "metro": [], "places": ["Ortaköy Meydanı", "Kuruçeşme", "Arnavutköy"],
                "names": {"ru": "Ортакёй", "uk": "Ортакьой", "bg": "Ортакьой", "ar": "أورتاكوي"}},
    "levent": {"name": "Levent", "kind": "near", "loc": (41.0790, 29.0110), "order": 10,
               "metro": [("M2", "Levent", "Şişli-Mecidiyeköy")], "places": ["Kanyon", "Metrocity", "Büyükdere Caddesi"],
               "names": {"ru": "Левент", "uk": "Левент", "bg": "Левент", "ar": "ليفنت"}},
    "4-levent": {"name": "4. Levent", "kind": "near", "loc": (41.0860, 29.0070), "order": 11,
                 "metro": [("M2", "4. Levent", "Şişli-Mecidiyeköy")], "places": ["İstanbul Sapphire", "Büyükdere Caddesi"],
                 "names": {"ru": "4-й Левент", "uk": "4-й Левент", "bg": "4-ти Левент", "ar": "ليفنت 4"}},
    "etiler": {"name": "Etiler", "kind": "near", "loc": (41.0820, 29.0330), "order": 12,
               "metro": [("M6", "Etiler", "Levent"), ("M2", "Levent", "Şişli-Mecidiyeköy")],
               "places": ["Nispetiye Caddesi", "Akmerkez", "Ulus"],
               "names": {"ru": "Этилер", "uk": "Етілер", "bg": "Етилер", "ar": "إتيلر"}},
    "maslak": {"name": "Maslak", "kind": "near", "loc": (41.1100, 29.0200), "order": 13,
               "metro": [("M2", "İTÜ-Ayazağa", "Şişli-Mecidiyeköy")], "places": ["İTÜ Ayazağa", "Vadi İstanbul"],
               "names": {"ru": "Маслак", "uk": "Маслак", "bg": "Маслак", "ar": "مسلك"}},
}


def km_between(a, b):
    lat1, lon1, lat2, lon2 = map(radians, (*a, *b))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * asin(sqrt(h))


def area_km(key):
    """Kliniğe kuş uçuşu mesafe, 0.5 km'ye yuvarlı (en az 0.5)."""
    return max(0.5, round(km_between(AREAS[key]["loc"], CLINIC_LOC) * 2) / 2)


def station_km():
    return round(km_between(NEAREST_STATION[1], CLINIC_LOC), 1)


def walk_minutes(key):
    """Yalnızca yürünebilir mesafede (≤ 2.5 km): yol ≈ kuş uçuşu × 1.3, 5 km/s, 5 dk'ya yuvarlı."""
    km = km_between(AREAS[key]["loc"], CLINIC_LOC)
    if km > 2.5:
        return None
    return max(5, int(round(km * 1.3 * 12 / 5)) * 5)


def taxi_minutes(key):
    km = km_between(AREAS[key]["loc"], CLINIC_LOC)
    for limit, band in ((1.5, "5–10"), (3, "10–15"), (5, "10–20"), (8, "15–25")):
        if km <= limit:
            return band
    return "20–35"


def area_name(key, lang):
    a = AREAS[key]
    return a["names"].get(lang, a["name"])


def ordered_keys():
    return sorted(AREAS, key=lambda k: AREAS[k]["order"])


# ── Keyword kalıpları ({a} = semt adı o dilde; Latin alfabeli dillerde aksansız yazımı da eklenir) ──
AREA_KEYWORDS = {
    "en": ["dental clinic {a}", "dentist {a}", "dentist in {a}", "dental clinic near {a}", "{a} dentist", "dental {a}",
           "teeth whitening {a}", "dental implant {a}"],
    "tr": ["{a} diş kliniği", "{a} diş hekimi", "{a} dişçi", "{a} diş doktoru", "{a} implant", "{a} diş beyazlatma",
           "{a} ağız ve diş sağlığı"],
    "de": ["zahnarzt {a}", "zahnklinik {a}", "zahnarzt {a} istanbul", "bleaching {a}"],
    "nl": ["tandarts {a}", "tandartskliniek {a}", "tandarts {a} istanbul"],
    "fr": ["dentiste {a}", "clinique dentaire {a}", "dentiste {a} istanbul"],
    "it": ["dentista {a}", "clinica dentale {a}", "dentista {a} istanbul"],
    "es": ["dentista {a}", "clínica dental {a}", "dentista {a} estambul"],
    "pl": ["dentysta {a}", "klinika stomatologiczna {a}", "dentysta {a} stambuł"],
    "ru": ["стоматология {a}", "стоматолог {a}", "зубной врач {a}", "стоматология {a} стамбул"],
    "uk": ["стоматологія {a}", "стоматолог {a}", "стоматологія {a} стамбул"],
    "ar": ["عيادة أسنان {a}", "طبيب أسنان {a}", "عيادة أسنان في {a} إسطنبول"],
    "sv": ["tandläkare {a}", "tandklinik {a}", "tandläkare {a} istanbul"],
    "da": ["tandlæge {a}", "tandklinik {a}", "tandlæge {a} istanbul"],
    "no": ["tannlege {a}", "tannklinikk {a}", "tannlege {a} istanbul"],
    "ro": ["dentist {a}", "clinică stomatologică {a}", "dentist {a} istanbul"],
    "bg": ["зъболекар {a}", "дентална клиника {a}", "зъболекар {a} истанбул"],
    "az": ["{a} diş klinikası", "{a} diş həkimi", "{a} stomatoloq"],
}
HUB_KEYWORDS = {
    "en": ["dental clinics in istanbul", "dentist near me istanbul", "dentist in istanbul", "dental clinic istanbul european side"],
    "tr": ["şişli diş kliniği", "yakınımdaki diş kliniği istanbul", "avrupa yakası diş kliniği"],
}

_ASCII = str.maketrans("şŞıİğĞüÜöÖçÇ", "sSiIgGuUoOcC")


def keywords_for(lang, key):
    name = area_name(key, lang).lower().replace("i̇", "i")
    names = [name]
    plain = name.translate(_ASCII)
    if plain != name:
        names.append(plain)
    out = []
    for i, pat in enumerate(AREA_KEYWORDS.get(lang, [])):
        for n in (names if i == 0 else names[:1]):
            out.append(pat.format(a=n))
    return out
