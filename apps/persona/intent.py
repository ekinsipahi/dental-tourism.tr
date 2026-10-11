"""
Arama niyeti → persona öncülü (cold start).

Ziyaretçi henüz hiçbir şey yapmadan, geldiği reklam kelimesi (utm_term / Google Ads
keyword), organik landing URL'si ve referrer sorgusundan persona tahmini yapılır.
Sözlük 16 dili kapsar; eşleşmeler ağırlıklı skor üretir.
"""
import re
import unicodedata
from urllib.parse import parse_qs, unquote_plus, urlparse

from .models import (PERSONA_FEAR, PERSONA_PREMIUM, PERSONA_PRICE, PERSONA_QUALITY, PERSONA_READY,
                     PERSONA_SHAME, PERSONA_SKEPTIC, PERSONA_TRUST, PERSONA_URGENCY)

# (desen, ağırlık). Desenler küçük harf, aksansız metinde aranır (kelime kökü).
#
# Niyetler AYRI tutulur (karıştırılmaz):
#   "cheap / billig / ucuz"              → PRICE   (pazarlıkçı; en güçlü fiyat sinyali)
#   "cost / price / how much"            → PRICE   (fiyat merakı; daha zayıf)
#   "dental work / teeth done / care"    → TRUST   (tedavi ihtiyacı olan, iyi bir hekim arayan — ucuz arayan DEĞİL)
#   "best / quality / custom / kişiye özel" → QUALITY (doğru, kişiye özel, uzun ömürlü tedavi arayan)
#   "luxury / vip / exclusive / lüks"    → PREMIUM (lüks/ayrıcalık HİSSİ arayan — kalite arayandan ayrı)
# "package" fiyat sinyali değildir (dental tourism packages = paket/organizasyon arayışı).
# Karışık sorguda en güçlü sinyal kazanır: "cheap dental work" → price, "best dental work" → quality, "luxury dental clinic" → premium.
LEXICON = {
    PERSONA_PRICE: [
        ("cheap", 2.0), ("cost", 1.6), ("price", 1.6), ("prices", 1.6), ("afford", 1.8), ("budget", 1.5),
        ("how much", 1.6), ("deal", 1.2), ("save", 1.0), ("discount", 1.8), ("lowest", 1.8),
        ("preis", 1.6), ("kosten", 1.6), ("gunstig", 2.0), ("billig", 2.0), ("was kostet", 1.8),
        ("prijs", 1.6), ("kosten", 1.6), ("goedkoop", 2.0), ("wat kost", 1.8),
        ("prix", 1.6), ("cout", 1.6), ("pas cher", 2.0), ("tarif", 1.4),
        ("prezzo", 1.6), ("prezzi", 1.6), ("costo", 1.6), ("economic", 1.8),
        ("precio", 1.6), ("barato", 2.0), ("cuanto cuesta", 1.8),
        ("cena", 1.6), ("koszt", 1.6), ("tanio", 2.0), ("tani", 2.0),
        ("цена", 1.6), ("стоимост", 1.6), ("дешев", 2.0), ("сколько стоит", 1.8),
        ("ціна", 1.6), ("вартість", 1.6), ("дешев", 2.0),
        ("سعر", 1.6), ("اسعار", 1.6), ("تكلفة", 1.6), ("رخيص", 2.0), ("كم سعر", 1.8),
        ("pris", 1.6), ("billig", 2.0), ("kostnad", 1.6), ("koster", 1.6), ("pret", 1.6), ("ieftin", 2.0),
        ("qiymet", 1.6), ("ucuz", 2.0), ("fiyat", 1.6), ("ucret", 1.6),
    ],
    PERSONA_FEAR: [
        ("safe", 2.0), ("safety", 2.0), ("risk", 2.0), ("danger", 2.0), ("horror", 2.5), ("gone wrong", 2.5),
        ("botched", 2.5), ("complication", 2.0), ("infection", 1.8), ("scam", 2.0), ("legit", 1.5),
        ("sicher", 2.0), ("gefahr", 2.0), ("risiko", 2.0), ("pfusch", 2.5), ("schief gelaufen", 2.5),
        ("veilig", 2.0), ("gevaarlijk", 2.0), ("mislukt", 2.2),
        ("securit", 2.0), ("risque", 2.0),
        ("sicur", 2.0), ("rischi", 2.0), ("pericolos", 2.0),
        ("segur", 2.0), ("riesgo", 2.0), ("peligro", 2.0),
        ("bezpiecz", 2.0), ("ryzyko", 2.0), ("powiklan", 2.0),
        ("безопас", 2.0), ("риск", 2.0), ("осложнен", 2.0), ("опасн", 2.0),
        ("безпеч", 2.0), ("ризик", 2.0), ("ускладн", 2.0),
        ("امان", 2.0), ("مخاطر", 2.0), ("خطر", 2.0), ("مضاعفات", 2.0),
        ("saker", 2.0), ("sikker", 2.0), ("farlig", 2.0), ("sigur", 2.0), ("riscuri", 2.0),
        ("tehlukesiz", 2.0), ("guvenli", 2.0), ("risk", 2.0), ("tehlike", 2.0),
    ],
    PERSONA_SHAME: [
        ("smile", 1.5), ("hollywood", 2.0), ("smile makeover", 2.2), ("veneer", 1.4), ("crooked", 1.8),
        ("yellow teeth", 1.8), ("ugly teeth", 2.5), ("gap", 1.2), ("whiten", 1.0), ("aesthetic", 1.4),
        ("lacheln", 1.5), ("veneers", 1.4), ("schiefe zahne", 1.8), ("hollywood smile", 2.0),
        ("glimlach", 1.5), ("facings", 1.4), ("sourire", 1.5), ("facette", 1.4),
        ("sorriso", 1.5), ("faccette", 1.4), ("sonrisa", 1.5), ("carillas", 1.4),
        ("usmiech", 1.5), ("licowki", 1.4), ("улыбк", 1.5), ("винир", 1.4), ("посмішк", 1.5),
        ("ابتسامة", 1.5), ("هوليود", 2.0), ("قشور", 1.4), ("leende", 1.5), ("smil", 1.5),
        ("zambet", 1.5), ("fatete", 1.4), ("gulus", 1.5), ("gulus tasarimi", 2.2), ("lamina", 1.4),
    ],
    PERSONA_URGENCY: [
        ("fast", 1.6), ("quick", 1.6), ("same day", 2.0), ("one day", 1.8), ("in a week", 2.0),
        ("emergency", 2.5), ("urgent", 2.5), ("wedding", 2.5), ("asap", 2.0), ("tooth pain", 2.0),
        ("schnell", 1.6), ("notfall", 2.5), ("sofort", 2.0), ("hochzeit", 2.5), ("in einer woche", 2.0),
        ("snel", 1.6), ("spoed", 2.5), ("bruiloft", 2.5), ("rapide", 1.6), ("urgence", 2.5), ("mariage", 2.5),
        ("veloc", 1.6), ("urgenz", 2.5), ("matrimonio", 2.5), ("rapido", 1.6), ("urgencia", 2.5), ("boda", 2.5),
        ("szybk", 1.6), ("pilne", 2.5), ("slub", 2.5), ("быстр", 1.6), ("срочн", 2.5), ("свадьб", 2.5),
        ("швидк", 1.6), ("терміново", 2.5), ("весілл", 2.5), ("سريع", 1.6), ("عاجل", 2.5), ("زفاف", 2.5),
        ("snabb", 1.6), ("akut", 2.5), ("hurtig", 1.6), ("rask", 1.6), ("rapid", 1.6), ("urgent", 2.5),
        ("tecili", 2.5), ("hizli", 1.6), ("acil", 2.5), ("dugun", 2.5),
    ],
    PERSONA_QUALITY: [
        # Kalite / kişiye özel tedavi: doğru tedavi, deneyimli hekim, isimli malzeme, uzun ömür
        ("best", 1.8), ("top", 1.2), ("quality", 2.0), ("high quality", 2.2), ("experienced", 1.6),
        ("specialist", 1.4), ("expert", 1.4), ("qualitat", 2.0), ("kwaliteit", 2.0), ("qualite", 2.0), ("qualita", 2.0),
        ("calidad", 2.0), ("jakosc", 2.0), ("качеств", 2.0), ("якіст", 2.0), ("جودة", 2.0),
        ("kvalitet", 2.0), ("calitate", 2.0), ("keyfiyyet", 2.0), ("kalite", 2.0), ("kaliteli", 2.2),
        ("straumann", 2.0), ("nobel biocare", 2.0), ("emax", 1.6), ("e max", 1.6), ("german implant", 1.6),
        ("custom", 1.8), ("personalised", 2.0), ("personalized", 2.0), ("tailored", 2.0), ("individual", 1.6),
        ("natural looking", 2.0), ("natural result", 2.0), ("long lasting", 2.0), ("durable", 1.8),
        ("minimally invasive", 2.2), ("no shaving", 2.0), ("prepless", 2.0), ("no prep", 2.0),
        ("digital smile design", 1.8), ("prosthodontist", 2.0), ("3d scan", 1.4), ("microscope", 1.6),
        ("beste", 1.4), ("hochwertig", 1.8), ("beste klinik", 1.8), ("individuell", 2.0), ("massgeschneidert", 2.0),
        ("naturlich", 1.6), ("langlebig", 2.0), ("ohne abschleifen", 2.2), ("erfahren", 1.6),
        ("persoonlijk", 1.6), ("op maat", 2.0), ("natuurlijk", 1.6), ("duurzaam", 1.8), ("ervaren", 1.6),
        ("meilleur", 1.4), ("sur mesure", 2.0), ("personnalis", 2.0), ("naturel", 1.6),
        ("migliore", 1.4), ("su misura", 2.0), ("personalizzat", 2.0), ("naturale", 1.6), ("duratur", 1.8),
        ("mejor", 1.4), ("a medida", 2.0), ("personalizad", 2.0), ("duradero", 1.8),
        ("najlepsz", 1.4), ("indywidualn", 2.0), ("naturaln", 1.6), ("trwal", 1.8), ("doswiadczon", 1.6),
        ("лучш", 1.4), ("индивидуальн", 2.0), ("естественн", 1.6), ("долговечн", 2.0), ("опытн", 1.6),
        ("кращ", 1.4), ("індивідуальн", 2.0), ("природн", 1.6), ("довговічн", 2.0), ("досвідчен", 1.6),
        ("افضل", 1.4), ("مخصص", 2.0), ("طبيعي", 1.6), ("خبرة", 1.6),
        ("bast", 1.4), ("bedste", 1.4), ("skraddarsy", 2.0), ("individuel", 1.6), ("holdbar", 1.8), ("hallbar", 1.8),
        ("cel mai bun", 1.4), ("personalizat", 2.0), ("natural", 1.4),
        ("en yaxsi", 1.4), ("ferdi", 1.6), ("en iyi", 1.4), ("kisiye ozel", 2.4), ("dogal gorunum", 2.0),
        ("uzun omurlu", 2.0), ("kesimsiz", 2.0), ("deneyimli", 1.6), ("uzman", 1.4),
    ],
    PERSONA_PREMIUM: [
        # Lüks / VIP hissi: ayrıcalık, mahremiyet, beklememe, "en pahalısı olsun" — kalite arayışından AYRI
        ("luxury", 2.4), ("luxurious", 2.4), ("premium", 2.2), ("vip", 2.4), ("private clinic", 1.8),
        ("exclusive", 2.2), ("high end", 2.0), ("5 star", 2.0), ("five star", 2.0), ("boutique", 1.8),
        ("celebrity", 2.2), ("celebrities", 2.2), ("concierge", 2.2), ("discreet", 1.8), ("first class", 2.0),
        ("luxus", 2.4), ("exklusiv", 2.2), ("privatklinik", 1.8), ("promi", 1.8),
        ("luxe", 2.4), ("exclusief", 2.2), ("exclusif", 2.2), ("haut de gamme", 2.2),
        ("lusso", 2.4), ("esclusiv", 2.2), ("lujo", 2.4), ("exclusiva", 2.2), ("famosos", 2.0),
        ("luksus", 2.4), ("ekskluzyw", 2.2), ("premium klinik", 2.0),
        ("премиум", 2.2), ("люкс", 2.4), ("элитн", 2.2), ("vip клиник", 2.4), ("преміум", 2.2), ("елітн", 2.2),
        ("فاخر", 2.4), ("فخم", 2.4), ("المشاهير", 2.2), ("حصري", 2.2),
        ("lyx", 2.4), ("lux", 2.0),
        ("luks", 2.4), ("unlu", 1.8), ("unluler", 2.2), ("ayricalik", 2.0), ("5 yildiz", 2.0),
    ],
    PERSONA_SKEPTIC: [
        ("review", 1.6), ("reviews", 1.6), ("experience", 1.4), ("worth it", 1.8), ("is it worth", 1.8),
        ("vs", 1.2), ("versus", 1.2), ("compare", 1.4), ("reddit", 2.0), ("forum", 1.8), ("pros and cons", 1.8),
        ("erfahrung", 1.8), ("bewertung", 1.6), ("vergleich", 1.4), ("lohnt", 1.8),
        ("ervaring", 1.8), ("review", 1.6), ("avis", 1.6), ("experience", 1.4), ("forum", 1.8),
        ("recension", 1.6), ("opinion", 1.6), ("opinie", 1.6), ("doswiadcz", 1.8),
        ("отзыв", 1.8), ("опыт", 1.4), ("стоит ли", 1.8), ("відгук", 1.8), ("досвід", 1.4),
        ("تجربة", 1.6), ("تجارب", 1.6), ("تقييم", 1.6), ("erfarenhet", 1.8), ("anmeldelse", 1.6),
        ("erfaring", 1.8), ("pareri", 1.6), ("rey", 1.2), ("yorum", 1.6), ("deneyim", 1.6),
    ],
    PERSONA_TRUST: [
        # Tedavi ihtiyacı (need-based) — fiyat veya lüks sinyali taşımaz
        ("dental work", 1.2), ("teeth done", 1.2), ("dental care", 1.0), ("dental treatment", 1.0),
        ("get my teeth", 1.2), ("zahnbehandlung", 1.0), ("zahne machen", 1.2), ("tandheelkundige zorg", 1.0),
        ("tanden laten", 1.2), ("soins dentaires", 1.0), ("cure dentali", 1.0), ("tratamiento dental", 1.0),
        ("leczenie zebow", 1.0), ("лечение зубов", 1.0), ("лікування зубів", 1.0), ("علاج الاسنان", 1.0),
        ("tandvard", 1.0), ("tandbehandling", 1.0), ("tannbehandling", 1.0), ("tratament dentar", 1.0),
        ("dis mualicesi", 1.0), ("dis tedavisi", 1.0), ("dis yaptirmak", 1.2),
        ("dentist istanbul", 1.0), ("clinic", 0.6), ("doctor", 0.8), ("trusted", 2.0), ("reliable", 2.0),
        ("recommend", 1.8), ("vertrauen", 2.0), ("seriös", 2.0), ("serios", 2.0), ("betrouwbaar", 2.0),
        ("fiable", 2.0), ("affidabile", 2.0), ("confiable", 2.0), ("zaufan", 2.0), ("надежн", 2.0),
        ("надійн", 2.0), ("موثوق", 2.0), ("palitlig", 2.0), ("palidelig", 2.0), ("de incredere", 2.0),
        ("etibarli", 2.0), ("guvenilir", 2.0),
    ],
    PERSONA_READY: [
        ("book", 1.6), ("appointment", 1.8), ("contact", 1.2), ("whatsapp", 1.8), ("near me", 1.2),
        ("termin", 1.8), ("afspraak", 1.8), ("rendez-vous", 1.8), ("rendez vous", 1.8),
        ("appuntamento", 1.8), ("prenot", 1.8), ("cita", 1.8), ("reserv", 1.6), ("wizyt", 1.8),
        ("запис", 1.8), ("prenotare", 1.8), ("موعد", 1.8), ("حجز", 1.8), ("boka", 1.8), ("bestil", 1.8),
        ("programare", 1.8), ("randevu", 1.8), ("qeydiyyat", 1.6),
    ],
}

_QUERY_PARAMS = ("utm_term", "keyword", "q", "query", "kw", "search", "p", "text")


def normalize(text: str) -> str:
    text = unquote_plus(text or "").lower()
    # Latin aksanlarını kaldır (ü→u, ç→c, ş→s); Kiril/Arap harflerine dokunma
    out = []
    for ch in unicodedata.normalize("NFKD", text):
        if unicodedata.combining(ch):
            continue
        out.append(ch)
    text = "".join(out).replace("ı", "i").replace("ß", "ss").replace("ø", "o").replace("æ", "ae").replace("å", "a")
    return re.sub(r"[\-_/+]+", " ", text)


def _compile(pat):
    norm = normalize(pat)
    # Kısa Latin kelimeler (vs, top, gap, vip...) kelime sınırıyla, uzunlar kök olarak aranır
    if len(norm) <= 4 and norm.isascii():
        return re.compile(rf"\b{re.escape(norm)}\b")
    return re.compile(re.escape(norm))


_COMPILED = {p: [(_compile(pat), w) for pat, w in pats] for p, pats in LEXICON.items()}


def extract_query(request) -> str:
    """utm_term, reklam kelimesi veya referrer arama sorgusu."""
    for p in _QUERY_PARAMS[:5]:
        v = request.GET.get(p)
        if v:
            return v[:300]
    ref = request.META.get("HTTP_REFERER", "")
    if ref:
        qs = parse_qs(urlparse(ref).query)
        for p in _QUERY_PARAMS:
            if qs.get(p):
                return qs[p][0][:300]
    return ""


def score_text(text: str) -> dict:
    t = normalize(text)
    if not t:
        return {}
    scores = {}
    for persona, patterns in _COMPILED.items():
        s = 0.0
        for rx, w in patterns:
            if rx.search(t):
                s += w
        if s:
            scores[persona] = round(s, 2)
    return scores


def intent_scores(request) -> dict:
    """Arama sorgusu + landing path birleşimi. Sorgu daha güçlü sinyaldir."""
    query = extract_query(request)
    scores = {}
    for persona, s in score_text(query).items():
        scores[persona] = scores.get(persona, 0) + s
    for persona, s in score_text(request.path).items():
        scores[persona] = scores.get(persona, 0) + s * 0.5
    return {"query": query, "scores": scores}
