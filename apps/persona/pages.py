"""
Site içi gezinme → persona kanıtı (SAYAÇ + SÜRE) — üç site için ortak.

Bir sayfa iki aşamada puan verir:
  1. Açılınca          → sinyalin %25'i (LOAD_SHARE) — sadece tıklayıp çıkan kişi az puan alır
  2. Çıkarken (süre)    → kalan %75 × min(süre / tam okuma sn, 1); 5 sn altı = 0 (yanlış tık / geri dönüş)
Yani 60+ sn okunan "en iyi klinik" rehberi tam puan, 3 sn bakılıp çıkılan neredeyse hiç.

Sayfa anlamı iki yoldan bulunur:
  dentaltourism.tr  → URL çözümlenir (resolve): fiyat sayfaları, rehberler, tedavi slug'ları (17 dil)
  drdevrim.com / devrimbirikensipahi.com.tr → apps.tracking.pagetypes sayfa TÜRÜ (home, pseo-area, treatment,
                    doctor, reviews, contact, redirect, booking …) + yoldaki tedavi kelimesi (implant, lamina, zirkon…)

Sayfa türü → persona (PAGE_TYPE_SIGNALS):
  price / package                                  → price
  doctor, about                                    → trust (+ kalite): "doktorlara bakıyor → güven arıyor"
  reviews                                          → skeptic + trust: "yorumları okuyor → kararsız, kanıt arıyor"
  treatment, guide, blog, qa                       → skeptic (araştırıyor) — tür tercihi DEĞİL
  pseo-area ("Şişli diş hekimi", "Nişantaşı…")     → ready + urgency: yakınında, şimdi arıyor
  contact / booking / redirect / thanks            → ready

Sıra (SEQUENCE_RULES): tek sayfa değil, GEZİNME de kanıt — "hizmetler arası geçince kararsız/araştırıyor",
"tedaviden sonra hekime baktı → güven arıyor", "birden fazla bölge sayfası → yakınında arıyor",
"gezdikten sonra iletişime geçti → karar aşaması". Bu bonuslar süreye bağlı değildir (gezinmenin kendisi sinyaldir).

Her sayfa ziyaret başına en fazla REPEAT_CAP kez sayılır (yenilemek skoru şişirmez).
"""
import re

from django.core.cache import cache
from django.urls import Resolver404, resolve

from .models import (PERSONA_FEAR, PERSONA_PREMIUM, PERSONA_PRICE, PERSONA_QUALITY, PERSONA_READY,
                     PERSONA_SHAME, PERSONA_SKEPTIC, PERSONA_TRUST, PERSONA_URGENCY)

REPEAT_CAP = 2
PERSONA_CAP = 6.0
LOAD_SHARE = 0.25        # sayfa açılınca verilen pay
DWELL_FULL = 60          # bu kadar saniye okunursa kalan payın tamamı
DWELL_MIN = 5            # altı = sayılmaz
# Sayfa türüne göre "tam okuma" süresi: iletişim sayfasında 20 sn kalmak zaten anlamlıdır, bir blog yazısı 90 sn ister
DWELL_FULL_BY_TYPE = {"contact": 20, "booking": 30, "redirect": 10, "thanks": 10, "confirmation": 10,
                      "blog": 90, "guide": 90, "reviews": 75, "qa": 75, "doctor": 45, "emergency": 30}

TREATMENT_SIGNALS = {
    "porcelain-veneers": {PERSONA_SKEPTIC: 0.5, PERSONA_SHAME: 0.2},
    "zirconia-crowns": {PERSONA_SKEPTIC: 0.5},
    "all-on-4-implants": {PERSONA_SKEPTIC: 0.5, PERSONA_FEAR: 0.2},
    "hollywood-smile": {PERSONA_SKEPTIC: 0.4, PERSONA_SHAME: 0.3, PERSONA_PREMIUM: 0.3},
    "dental-implants": {PERSONA_SKEPTIC: 0.5, PERSONA_FEAR: 0.2},
    "composite-veneers": {PERSONA_SKEPTIC: 0.5, PERSONA_SHAME: 0.2},
    "teeth-whitening": {PERSONA_SKEPTIC: 0.4, PERSONA_SHAME: 0.2},
    "root-canal-treatment": {PERSONA_SKEPTIC: 0.5, PERSONA_FEAR: 0.2},
    "tooth-fillings": {PERSONA_SKEPTIC: 0.4},
    "teeth-cleaning": {PERSONA_SKEPTIC: 0.4},
    "orthodontics": {PERSONA_SKEPTIC: 0.5, PERSONA_SHAME: 0.2},
    "gum-treatment": {PERSONA_SKEPTIC: 0.4, PERSONA_FEAR: 0.3},
    "pediatric-dentistry": {PERSONA_SKEPTIC: 0.4, PERSONA_TRUST: 0.3},
    # Kardeş sitelerin hizmet sayfaları (drdevrim /hizmetler/*, devrimbirikensipahi kategori sayfaları)
    "tooth-extraction": {PERSONA_FEAR: 0.5, PERSONA_URGENCY: 0.4, PERSONA_SKEPTIC: 0.2},      # diş çekimi: ağrı var, korkuyor
    "emergency-dentistry": {PERSONA_URGENCY: 1.2, PERSONA_FEAR: 0.4, PERSONA_READY: 0.4},     # acil diş: şimdi, hemen
    "digital-dentistry": {PERSONA_QUALITY: 0.7, PERSONA_PREMIUM: 0.2, PERSONA_SKEPTIC: 0.2},  # dijital/CAD-CAM: teknolojiye bakıyor
    "oral-surgery": {PERSONA_FEAR: 0.7, PERSONA_SKEPTIC: 0.3},                                # apikal rezeksiyon, 20 yaş: korku
    "dentures": {PERSONA_SKEPTIC: 0.4, PERSONA_PRICE: 0.2, PERSONA_FEAR: 0.2},                # protez: kıyaslıyor
}

# Kardeş sitelerin pSEO aileleri: ARAMA NİYETİ URL'DEDİR — "hafta sonu açık dişçi" acildir, "en iyi dişçi" kaliteyi
# kıyaslar, "prof. diş hekimi" statü/uzmanlık arar, "estetik diş kliniği" görünüş derdindedir, "<semt> dişçi" yakınında
# ve şimdi arıyordur. (drdevrim: /haftasonu/<ilçe>/, /en-iyi-disci/<ilçe>/, /uzman-dis-hekimi/, /prof-dis-hekimi/,
# /estetik-dis-klinigi/, /disci/<ilçe>/<semt>/; devrimbirikensipahi: /sisli-dis-hekimi, /acil-dis-hekimi)
PSEO_FAMILY_SIGNALS = {
    "haftasonu": {PERSONA_URGENCY: 1.0, PERSONA_READY: 0.4},
    "hafta-sonu": {PERSONA_URGENCY: 1.0, PERSONA_READY: 0.4},
    "acil": {PERSONA_URGENCY: 1.2, PERSONA_READY: 0.4, PERSONA_FEAR: 0.2},
    "en-iyi-disci": {PERSONA_QUALITY: 0.8, PERSONA_SKEPTIC: 0.4, PERSONA_READY: 0.2},
    "uzman-dis-hekimi": {PERSONA_QUALITY: 0.8, PERSONA_TRUST: 0.3, PERSONA_READY: 0.2},
    "prof-dis-hekimi": {PERSONA_QUALITY: 0.7, PERSONA_PREMIUM: 0.4, PERSONA_TRUST: 0.3},
    "estetik-dis-klinigi": {PERSONA_SHAME: 0.6, PERSONA_PREMIUM: 0.5, PERSONA_READY: 0.2},
    "disci": {PERSONA_READY: 0.5, PERSONA_URGENCY: 0.3},
}


def pseo_family(path):
    """/haftasonu/cekmekoy/ → 'haftasonu'; /lang/en/… ve /en/… önekleri atlanır; bilinmeyen aile → ''."""
    parts = [p for p in (path or "").split("/") if p]
    if parts and parts[0] == "lang":
        parts = parts[1:]
    if parts and len(parts[0]) == 2 and parts[0].isalpha():
        parts = parts[1:]
    return parts[0] if parts and parts[0] in PSEO_FAMILY_SIGNALS else ""

# Kardeş sitelerin tedavi URL'leri (TR / EN / DE / RU slug parçaları) → kanonik tedavi anahtarı
EXT_TREATMENT_WORDS = (
    ("all-on", "all-on-4-implants"), ("allon", "all-on-4-implants"),
    ("implant-ustu", "dentures"), ("sabit-protez", "dentures"), ("protez", "dentures"), ("denture", "dentures"), ("prothese", "dentures"),
    ("implant", "dental-implants"), ("имплант", "dental-implants"),
    ("acil", "emergency-dentistry"), ("emergency", "emergency-dentistry"), ("notfall", "emergency-dentistry"),
    ("cekim", "tooth-extraction"), ("extraction", "tooth-extraction"), ("удален", "tooth-extraction"),
    ("dijital", "digital-dentistry"), ("digital", "digital-dentistry"), ("cad-cam", "digital-dentistry"),
    ("apikal", "oral-surgery"), ("rezeksiyon", "oral-surgery"), ("cerrahi", "oral-surgery"), ("surgery", "oral-surgery"),
    ("yirmi-yas", "oral-surgery"), ("20-yas", "oral-surgery"), ("gomulu", "oral-surgery"),
    ("fissur", "pediatric-dentistry"), ("sut-dis", "pediatric-dentistry"),
    ("piyasment", "gum-treatment"), ("kuretaj", "gum-treatment"),
    ("metal-tel", "orthodontics"),
    ("gulus", "hollywood-smile"),
    ("lamina", "porcelain-veneers"), ("veneer", "porcelain-veneers"), ("porselen", "porcelain-veneers"),
    ("винир", "porcelain-veneers"), ("facette", "porcelain-veneers"),
    ("zirkon", "zirconia-crowns"), ("zircon", "zirconia-crowns"), ("kaplama", "zirconia-crowns"), ("kron", "zirconia-crowns"),
    ("crown", "zirconia-crowns"), ("циркон", "zirconia-crowns"),
    ("hollywood", "hollywood-smile"), ("gulus-tasarim", "hollywood-smile"), ("smile-design", "hollywood-smile"),
    ("smile-makeover", "hollywood-smile"), ("estetik-dis", "hollywood-smile"), ("estetik", "hollywood-smile"),
    ("kompozit", "composite-veneers"), ("composite", "composite-veneers"), ("bonding", "composite-veneers"),
    ("beyazlat", "teeth-whitening"), ("whitening", "teeth-whitening"), ("bleaching", "teeth-whitening"), ("отбелив", "teeth-whitening"),
    ("kanal", "root-canal-treatment"), ("root-canal", "root-canal-treatment"), ("endodont", "root-canal-treatment"),
    ("dolgu", "tooth-fillings"), ("filling", "tooth-fillings"), ("fullung", "tooth-fillings"),
    ("temizl", "teeth-cleaning"), ("cleaning", "teeth-cleaning"), ("dis-tasi", "teeth-cleaning"), ("hygiene", "teeth-cleaning"),
    ("ortodonti", "orthodontics"), ("orthodont", "orthodontics"), ("braces", "orthodontics"), ("seffaf-plak", "orthodontics"),
    ("invisalign", "orthodontics"), ("tel-tedavi", "orthodontics"),
    ("diseti", "gum-treatment"), ("periodont", "gum-treatment"), ("gum", "gum-treatment"), ("zahnfleisch", "gum-treatment"),
    ("cocuk", "pediatric-dentistry"), ("pedodonti", "pediatric-dentistry"), ("pediatric", "pediatric-dentistry"), ("kinder", "pediatric-dentistry"),
)

TOPIC_SIGNALS = {
    "best-dental-clinic-istanbul": {PERSONA_QUALITY: 1.1, PERSONA_SKEPTIC: 0.5},
    "best-dental-clinic-turkey": {PERSONA_QUALITY: 1.0, PERSONA_SKEPTIC: 0.7},
    "dental-care-turkey": {PERSONA_TRUST: 0.6},
    "dental-tourism": {PERSONA_SKEPTIC: 0.6},
    "best-country-dental-tourism": {PERSONA_SKEPTIC: 0.9, PERSONA_PRICE: 0.4},
    "teeth-done-in-turkey": {PERSONA_SKEPTIC: 0.7, PERSONA_FEAR: 0.4},
    "dental-surgery-turkey": {PERSONA_FEAR: 0.9, PERSONA_QUALITY: 0.3},
    "dental-guarantee-aftercare": {PERSONA_FEAR: 1.0, PERSONA_QUALITY: 0.6, PERSONA_TRUST: 0.3},
    "smile-gallery": {PERSONA_SHAME: 1.1, PERSONA_PREMIUM: 0.6},
    "dental-clinic-istanbul": {PERSONA_READY: 0.6},
    "dental-care-antalya": {PERSONA_READY: 0.3},
    "dental-clinic-aegean": {PERSONA_READY: 0.3},
    "dental-clinic-ankara": {PERSONA_READY: 0.3},
    "istanbul-guide": {PERSONA_READY: 0.8, PERSONA_PREMIUM: 0.3},
    "dental-tourism-agency": {PERSONA_READY: 0.4},
}

VIEW_SIGNALS = {
    "prices:index": {PERSONA_PRICE: 1.3},
    "prices:detail": {PERSONA_PRICE: 1.2},
    "packages:index": {PERSONA_PRICE: 0.6, PERSONA_PREMIUM: 0.4},
    "packages:treatment": {PERSONA_PRICE: 0.5},
    "origins:detail": {PERSONA_PRICE: 0.3, PERSONA_READY: 0.4},
    "clinics:detail": {PERSONA_TRUST: 0.6, PERSONA_SKEPTIC: 0.3},
    "doctors:detail": {PERSONA_QUALITY: 0.9, PERSONA_TRUST: 0.5},
    "core:about": {PERSONA_TRUST: 0.7, PERSONA_QUALITY: 0.5},
    "core:contact": {PERSONA_READY: 1.3},
    "blog:post_detail": {PERSONA_SKEPTIC: 0.5},
    "guides:index": {PERSONA_SKEPTIC: 0.4},
}

# Sayfa TÜRÜ → persona (kardeş siteler; dentaltourism'de URL çözülemezse yedek). Ağırlıklar VIEW_SIGNALS ile aynı ölçekte.
PAGE_TYPE_SIGNALS = {
    "home": {PERSONA_TRUST: 0.2, PERSONA_SKEPTIC: 0.2},            # ana sayfada uzun kalmak: tanımaya çalışıyor
    "pseo-area": {PERSONA_READY: 0.4, PERSONA_URGENCY: 0.3},       # "Şişli diş hekimi" — yakınında, şimdi arıyor
    "treatment": {PERSONA_SKEPTIC: 0.5},                           # tedaviyi okuyor — araştırıyor
    "treatment-city": {PERSONA_SKEPTIC: 0.4, PERSONA_READY: 0.3},
    "price": {PERSONA_PRICE: 1.3},
    "package": {PERSONA_PRICE: 0.6, PERSONA_PREMIUM: 0.4},
    "guide": {PERSONA_SKEPTIC: 0.4},
    "origin": {PERSONA_PRICE: 0.3, PERSONA_READY: 0.4},
    "doctor": {PERSONA_TRUST: 0.9, PERSONA_QUALITY: 0.6},         # "doktorlara bakıyor → güven arıyor"
    "clinic": {PERSONA_TRUST: 0.6, PERSONA_SKEPTIC: 0.3},
    "about": {PERSONA_TRUST: 0.7, PERSONA_QUALITY: 0.5},
    "contact": {PERSONA_READY: 1.3},
    "booking": {PERSONA_READY: 1.5},
    "redirect": {PERSONA_READY: 1.5},                              # tıkla-ara yönlendirme sayfası = aramaya gitti
    "thanks": {PERSONA_READY: 1.0},
    "confirmation": {PERSONA_READY: 1.0},
    "qa": {PERSONA_SKEPTIC: 0.6},
    "blog": {PERSONA_SKEPTIC: 0.5},
    "reviews": {PERSONA_SKEPTIC: 0.7, PERSONA_TRUST: 0.6},        # "yorumları okuyor → kararsız, kanıt arıyor"
    "dental-tourism": {PERSONA_SKEPTIC: 0.4, PERSONA_PRICE: 0.3},
    "emergency": {PERSONA_URGENCY: 1.2, PERSONA_FEAR: 0.4, PERSONA_READY: 0.4},   # "acil diş hekimi" sayfası
    "page": {},
}

# dentaltourism view adı → ortak sayfa türü (sıra kuralları ve tür bazlı okuma süresi için)
_DT_KIND_TYPES = (
    ("treatments:city", "treatment-city"), ("treatments:detail", "treatment"), ("treatments:list", "treatment"),
    ("prices:", "price"), ("packages:", "package"), ("guide:", "guide"), ("guides:", "guide"), ("origins:", "origin"),
    ("doctors:", "doctor"), ("clinics:", "clinic"), ("core:about", "about"), ("core:contact", "contact"),
    ("core:thanks", "thanks"), ("core:home", "home"), ("blog:", "blog"),
)

# Gezinme sırası → bonus. (bu sayfanın türü, koşul(önceki türler, bu türden kaçıncı sayfa), sinyal, kanıt etiketi)
_RESEARCH = {"treatment", "treatment-city", "pseo-area", "guide", "blog", "qa"}
SEQUENCE_RULES = (
    ("treatment", lambda prev, n: 2 <= n <= 4, {PERSONA_SKEPTIC: 0.4, PERSONA_QUALITY: 0.2},
     "Tedaviler arası geçiş ({n}. tedavi) — kararsız, araştırıyor"),
    ("pseo-area", lambda prev, n: 2 <= n <= 4, {PERSONA_URGENCY: 0.4, PERSONA_READY: 0.3},
     "Birden fazla bölge sayfası ({n}.) — yakınında diş hekimi arıyor"),
    ("doctor", lambda prev, n: n == 1 and prev & _RESEARCH, {PERSONA_TRUST: 0.4},
     "Tedaviyi okuduktan sonra hekime baktı — güven arıyor"),
    ("reviews", lambda prev, n: n == 1 and prev & (_RESEARCH | {"doctor", "price"}), {PERSONA_SKEPTIC: 0.3},
     "Gezdikten sonra yorumlara geçti — kararsız, kanıt arıyor"),
    ("price", lambda prev, n: n == 1 and prev & {"treatment", "treatment-city"}, {PERSONA_PRICE: 0.3},
     "Tedaviyi okudu, fiyata baktı"),
    ("contact", lambda prev, n: n == 1 and len(prev) >= 2, {PERSONA_READY: 0.4},
     "Gezdikten sonra iletişime geçti — karar aşaması"),
    ("booking", lambda prev, n: n == 1 and len(prev) >= 1, {PERSONA_READY: 0.4},
     "Gezdikten sonra randevuya geçti — karar aşaması"),
    ("redirect", lambda prev, n: n == 1 and len(prev) >= 1, {PERSONA_READY: 0.4},
     "Gezdikten sonra aramaya gitti — karar aşaması"),
    ("emergency", lambda prev, n: n == 1, {PERSONA_URGENCY: 0.3},
     "Acil diş hekimi sayfasına geldi — şimdi, hemen"),
)


def _slug_map(model_label):
    """{(lang-agnostic) slug: canonical EN slug/key} — tüm çeviri slug'ları, 1 saat cache'li."""
    key = f"persona:slugmap:{model_label}"
    data = cache.get(key)
    if data is not None:
        return data
    data = {}
    if model_label == "treatment":
        from apps.treatments.models import Treatment, TreatmentTranslation

        for t in Treatment.objects.only("slug"):
            data[t.slug] = t.slug
        for tr in TreatmentTranslation.objects.select_related("treatment").only("slug", "treatment__slug"):
            data[tr.slug] = tr.treatment.slug
    else:
        from apps.seo.models import SeoTopic, SeoTopicTranslation

        for t in SeoTopic.objects.only("slug", "key"):
            data[t.slug] = t.key
        for tr in SeoTopicTranslation.objects.select_related("topic").only("slug", "topic__key"):
            data[tr.slug] = tr.topic.key
    cache.set(key, data, 3600)
    return data


def page_type_of(site, path, hint=""):
    """Ortak sayfa türü (apps.tracking.pagetypes) — sayfanın bildirdiği ipucu varsa o kazanır."""
    from apps.tracking.pagetypes import page_type_for

    return page_type_for(site or "dt", path or "/", hint or "")


def ext_treatment(path):
    """Kardeş site tedavi yolundan kanonik tedavi anahtarı (/hizmetler/implant → dental-implants); yoksa ''."""
    from .intent import normalize

    p = normalize(path or "").replace(" ", "-")
    for word, key in EXT_TREATMENT_WORDS:
        if word in p:
            return key
    return ""


def _short_path(path):
    p = re.sub(r"/+$", "", path or "/") or "/"
    return p[:60]


def kind_type(kind):
    """pages_seen anahtarı → ortak sayfa türü ('treatment@/hizmetler/implant' → treatment, 'prices:index' → price)."""
    if not kind or kind.startswith(("dwell:", "faq:", "faqr:", "switch:", "seq:")):
        return ""
    if "@" in kind:
        return kind.split("@", 1)[0]
    for prefix, t in _DT_KIND_TYPES:
        if kind.startswith(prefix):
            return t
    return ""


def page_signal(path, site="dt", page_type=""):
    """(sayfa anahtarı, {persona: ağırlık}) — eşleşme yoksa (None, {}).
    dentaltourism: URL çözümlenir; kardeş siteler: sayfa türü (+ yoldaki tedavi kelimesi)."""
    site = site or "dt"
    if site == "dt":
        try:
            match = resolve(path)
        except Resolver404:
            match = None
        if match is not None:
            name = match.view_name or ""
            slug = match.kwargs.get("slug", "")
            if name in ("treatments:detail", "treatments:city", "packages:treatment", "prices:detail") and slug:
                canonical = _slug_map("treatment").get(slug, slug)
                sig = dict(TREATMENT_SIGNALS.get(canonical, {}))
                for p, w in VIEW_SIGNALS.get(name, {}).items():
                    sig[p] = sig.get(p, 0) + w
                return f"{name}:{canonical}", sig
            if name == "guides:detail" and slug:
                topic = _slug_map("topic").get(slug, slug)
                return f"guide:{topic}", dict(TOPIC_SIGNALS.get(topic, {}))
            return name, dict(VIEW_SIGNALS.get(name, {}))
        if not page_type:
            return None, {}
    ptype = page_type_of(site, path, page_type)
    if ptype == "treatment":
        canonical = ext_treatment(path)
        sig = dict(TREATMENT_SIGNALS.get(canonical) or PAGE_TYPE_SIGNALS["treatment"])
    elif ptype == "pseo-area":
        sig = dict(PSEO_FAMILY_SIGNALS.get(pseo_family(path)) or PAGE_TYPE_SIGNALS["pseo-area"])
    else:
        sig = dict(PAGE_TYPE_SIGNALS.get(ptype, {}))
    return f"{ptype}@{_short_path(path)}", sig


def _add(session, sig, share):
    scores = dict(session.page_scores or {})
    added = {}
    for p, w in sig.items():
        v = round(w * share, 3)
        if v > 0:
            scores[p] = round(min(PERSONA_CAP, scores.get(p, 0.0) + v), 2)
            added[p] = v
    session.page_scores = scores
    return added


def _visit_pages(seen):
    """Bu ziyarette açılan farklı sayfalar (sırayla) — dwell/SSS/switch anahtarları hariç."""
    out = []
    for k in seen:
        if kind_type(k) and k not in out:
            out.append(k)
    return out


def apply_sequence(session, kind, seen):
    """Gezinme sırası kuralları: bu sayfa (kind) az önce eklendi; önceki sayfaların türlerine göre bonus."""
    from .mindset import add_evidence

    ptype = kind_type(kind)
    if not ptype:
        return False
    pages = _visit_pages(seen)
    if kind in pages:
        pages = pages[:pages.index(kind)]      # bu sayfadan öncekiler
    prev_types = {kind_type(k) for k in pages}
    n = sum(1 for k in pages if kind_type(k) == ptype) + 1   # bu türden kaçıncı farklı sayfa
    changed = False
    for rule_type, cond, sig, label in SEQUENCE_RULES:
        if rule_type != ptype or not cond(prev_types, n):
            continue
        key = f"seq:{rule_type}:{n}"
        if key in seen:
            continue
        seen.append(key)
        added = _add(session, sig, 1.0)
        add_evidence(session, "nav", label.format(n=n), added or sig)
        changed = True
    session.pages_seen = seen[-40:]
    return changed


def apply_page(session, path, page_type=""):
    """Sayfa açıldı → sinyalin LOAD_SHARE kadarı + gezinme sırası bonusu. Değişiklik olduysa True."""
    kind, sig = page_signal(path, getattr(session, "site", "dt"), page_type)
    if not kind:
        return False
    seen = list(session.pages_seen or [])
    if seen.count(kind) >= REPEAT_CAP:
        return False
    first_time = kind not in seen
    seen.append(kind)
    session.pages_seen = seen[-40:]
    if sig:
        _add(session, sig, LOAD_SHARE)
    if first_time:
        apply_sequence(session, kind, list(session.pages_seen))
    return True


def apply_dwell(session, path, seconds, page_type=""):
    """Sayfadan çıkarken: kalan pay × okuma süresi. Kanıt günlüğüne 'sayfa — 45 sn' yazılır."""
    from .mindset import add_evidence

    kind, sig = page_signal(path, getattr(session, "site", "dt"), page_type)
    if not kind:
        return False
    seconds = max(0, int(seconds or 0))
    seen = list(session.pages_seen or [])
    key = f"dwell:{kind}"
    if seen.count(key) >= REPEAT_CAP:
        return False
    seen.append(key)
    session.pages_seen = seen[-40:]
    full = DWELL_FULL_BY_TYPE.get(kind_type(kind), DWELL_FULL)
    factor = 0.0 if seconds < DWELL_MIN else min(seconds / full, 1.0)
    added = _add(session, sig, (1 - LOAD_SHARE) * factor) if sig else {}
    total = {p: round(v * (LOAD_SHARE + (1 - LOAD_SHARE) * factor), 2) for p, v in sig.items()} if sig else {}
    add_evidence(session, "page", f"{kind} — {seconds} sn", total or {"unknown": 0})
    return bool(added) or True
