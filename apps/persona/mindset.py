"""
"Bu kişinin aklında şu an ne var?" — sayaç tabanlı kanıt + anlık görüntü.

Ziyaretçi sayfalar arasında gezdikçe, SSS açtıkça ("Acıtır mı?" → korku, "Ödeme nasıl?" → fiyat),
fiyatını sordukça her sinyal sayılır ve oturumun `evidence` listesine yazılır. Ziyaretçi aradığı /
WhatsApp'a yazdığı / form gönderdiği anda `snapshot()` alınır ve tıklama kaydına + lead'e kopyalanır;
admin panelde "Aklındaki: 😟 Korku %62 · 💶 Fiyat %21 — neden: 'Acıtır mı?' SSS'si, garanti rehberi…" görünür.
"""
import re

from django.utils import timezone

from .intent import _compile, normalize, score_text
from .models import (PERSONA_FEAR, PERSONA_PREMIUM, PERSONA_PRICE, PERSONA_QUALITY, PERSONA_READY,
                     PERSONA_SHAME, PERSONA_SKEPTIC, PERSONA_TRUST, PERSONA_UNKNOWN, PERSONA_URGENCY)

LABELS = {
    PERSONA_PRICE: "💶 Fiyat",
    PERSONA_PREMIUM: "💎 Lüks / VIP",
    PERSONA_QUALITY: "🎯 Kalite / kişiye özel",
    PERSONA_SKEPTIC: "🔍 Şüphe / araştırma",
    PERSONA_FEAR: "😟 Korku / ağrı",
    PERSONA_SHAME: "🙈 Estetik / gülüş",
    PERSONA_URGENCY: "⚡ Acele / zaman",
    PERSONA_TRUST: "🤝 Güven / hekim",
    PERSONA_READY: "✅ Karar vermiş",
    PERSONA_UNKNOWN: "❔ Belirsiz",
}

# SSS / içerik metinlerine özel ek sözlük (arama sorgularında kullanılmaz: "tooth pain" aramasında acil kalsın)
CONTENT_LEXICON = {
    PERSONA_FEAR: [
        ("hurt", 2.2), ("pain", 2.2), ("painful", 2.2), ("anaesthe", 1.8), ("anesthe", 1.8), ("sedation", 1.8),
        ("numb", 1.6), ("goes wrong", 2.0), ("guarantee", 1.4), ("warranty", 1.4), ("afraid", 2.2), ("scared", 2.2),
        ("schmerz", 2.2), ("weh", 1.8), ("betaubung", 1.8), ("narkose", 1.8), ("garantie", 1.4), ("angst", 2.2),
        ("pijn", 2.2), ("verdoving", 1.8), ("douleur", 2.2), ("douloureux", 2.2), ("anesthesie", 1.8), ("peur", 2.2),
        ("dolore", 2.2), ("fa male", 2.2), ("anestesia", 1.8), ("garanzia", 1.4), ("paura", 2.2),
        ("dolor", 2.2), ("duele", 2.2), ("garantia", 1.4), ("miedo", 2.2),
        ("bol", 2.0), ("boli", 2.0), ("znieczul", 1.8), ("gwarancj", 1.4), ("strach", 2.2),
        ("боль", 2.2), ("больно", 2.2), ("анестез", 1.8), ("гаранти", 1.4), ("страх", 2.2), ("біль", 2.2), ("боляче", 2.2),
        ("ألم", 2.2), ("مؤلم", 2.2), ("تخدير", 1.8), ("ضمان", 1.4), ("خوف", 2.2),
        ("smarta", 2.2), ("ont", 1.8), ("bedovning", 1.8), ("smerte", 2.2), ("bedovelse", 1.8), ("rædsel", 2.0),
        ("durere", 2.2), ("doare", 2.2), ("anestezie", 1.8), ("frica", 2.2),
        ("agri", 2.2), ("agril", 2.2), ("agrisi", 2.2), ("agriyir", 2.2), ("acir", 2.2), ("acitir", 2.2), ("aciyor", 2.2), ("acimaz", 2.2), ("uyusturma", 1.8), ("narkoz", 1.8),
        ("garanti", 1.4), ("korku", 2.2), ("korkuyorum", 2.2),
    ],
    PERSONA_QUALITY: [
        ("last", 2.0), ("how experienced", 1.6), ("lifespan", 1.8), ("material", 1.6), ("brand", 1.6),
        ("which implant", 1.8), ("zirconia or", 1.6), ("porcelain or", 1.6), ("haltbar", 1.8),
        ("hoe lang", 1.4), ("duree de vie", 1.8), ("durata", 1.4), ("cuanto dura", 1.6), ("jak dlugo", 1.4),
        ("сколько служ", 1.8), ("скільки служ", 1.8), ("كم تدوم", 1.8), ("hur lange", 1.4), ("hvor lenge", 1.4),
        ("hvor lang", 1.4), ("cat timp", 1.4), ("ne kadar dayanir", 1.8), ("omru", 1.6), ("malzeme", 1.6), ("marka", 1.6),
    ],
    PERSONA_URGENCY: [
        ("how long", 1.4), ("stay", 0.8), ("weekend", 1.4), ("holiday", 1.2), ("wochenende", 1.4), ("hafta sonu", 1.4),
        ("tatil", 1.2), ("ne kadar kal", 1.6), ("wie lange", 1.4), ("combien de temps", 1.4), ("quanto tempo", 1.4),
        ("cuanto tiempo", 1.4), ("сколько времени", 1.4), ("how many days", 1.8), ("how long does it take", 1.6), ("how many visits", 1.6), ("one trip", 1.6),
        ("wie viele tage", 1.8), ("hoeveel dagen", 1.8), ("combien de jours", 1.8), ("quanti giorni", 1.8),
        ("cuantos dias", 1.8), ("ile dni", 1.8), ("сколько дней", 1.8), ("скільки днів", 1.8), ("كم يوم", 1.8),
        ("hur manga dagar", 1.8), ("hvor mange dage", 1.8), ("hvor mange dager", 1.8), ("cate zile", 1.8),
        ("nece gun", 1.8), ("kac gun", 1.8), ("kac seans", 1.6),
    ],
    PERSONA_PRICE: [
        ("payment", 1.6), ("pay", 1.2), ("installment", 1.8), ("included", 1.4), ("deposit", 1.4), ("quote", 1.4),
        ("zahlung", 1.6), ("raten", 1.8), ("betaling", 1.6), ("paiement", 1.6), ("pagamento", 1.6), ("pago", 1.6),
        ("platnosc", 1.6), ("оплат", 1.6), ("рассроч", 1.8), ("розстроч", 1.8), ("الدفع", 1.6), ("تقسيط", 1.8),
        ("betalning", 1.6), ("plata", 1.6), ("odenis", 1.6), ("odeme", 1.6), ("taksit", 1.8), ("dahil", 1.2),
    ],
    PERSONA_READY: [
        ("where is the clinic", 1.6), ("address", 1.4), ("how do i get", 1.4), ("travel from", 1.2), ("near", 0.8),
        ("adres", 1.4), ("nerede", 1.4), ("wo ist", 1.4), ("anfahrt", 1.4), ("ou se trouve", 1.4), ("dove si trova", 1.4),
        ("donde esta", 1.4), ("gdzie", 1.2), ("где находится", 1.4), ("де знаходиться", 1.4), ("أين", 1.2),
    ],
    PERSONA_TRUST: [
        ("speak", 1.2), ("language", 1.0), ("sprechen", 1.2), ("dil", 0.8), ("konus", 1.0),
    ],
    PERSONA_PREMIUM: [
        ("hotel", 1.4), ("transfer", 1.4), ("chauffeur", 1.8), ("private room", 1.8), ("otel", 1.4), ("отель", 1.4),
        ("فندق", 1.4),
    ],
    PERSONA_SHAME: [
        ("colour", 1.4), ("color", 1.4), ("shade", 1.4), ("farbe", 1.4), ("couleur", 1.4), ("renk", 1.4),
        ("before and after", 1.6), ("look natural", 1.6), ("fake", 1.8), ("too white", 1.8), ("vorher nachher", 1.6),
        ("avant apres", 1.6), ("antes y despues", 1.6), ("once sonra", 1.6), ("dogal gorun", 1.6),
    ],
}
_CONTENT = {p: [(_compile(pat), w) for pat, w in pats] for p, pats in CONTENT_LEXICON.items()}

EVIDENCE_CAP = 60
FAQ_WEIGHT = 0.6        # sözlükle sınıflanan soru: skor × ağırlık (en fazla FAQ_MAX)
FAQ_MAX = 1.5           # etiketli (ortak SSS) soru: tam puan = 1.5
FAQ_OPEN_SHARE = 0.3    # açınca verilen pay — 1 sn açıp kapatan az puan alır
FAQ_READ_FULL = 8       # bu kadar saniye açık kalırsa kalan payın tamamı (cevaplar 2-3 cümle)
FAQ_READ_MIN = 2        # altı = okumadı
PERSONA_CAP = 6.0


def score_content(text):
    """SSS / içerik metni sınıflandırma. Arama sözlüğünden farkı:
    'güvenli mi / risk' soruları ŞÜPHE (araştırıyor) sayılır; KORKU yalnızca ağrı / uyuşturma / 'ters giderse'."""
    scores = dict(score_text(text))
    # "dental care / clinic / doctor" gibi genel kelimeler her soruda geçer — SSS'de güven sinyali sayılmaz
    scores.pop(PERSONA_TRUST, None)
    if PERSONA_FEAR in scores:
        scores[PERSONA_SKEPTIC] = round(scores.get(PERSONA_SKEPTIC, 0) + scores.pop(PERSONA_FEAR), 2)
    t = normalize(text)
    for p, pats in _CONTENT.items():
        s = sum(w for rx, w in pats if rx.search(t))
        if s:
            scores[p] = round(scores.get(p, 0) + s, 2)
    return scores


def add_evidence(session, kind, label, scores):
    """Kanıt günlüğüne bir satır ekler: ne yaptı, hangi persona'ya ne kadar puan verdi."""
    if not scores:
        return
    top = max(scores, key=scores.get)
    row = {"at": timezone.now().isoformat(timespec="seconds"), "k": kind, "l": str(label)[:90], "p": top,
           "w": round(float(scores[top]), 2)}
    session.evidence = [*(session.evidence or []), row][-EVIDENCE_CAP:]


def _faq_signal(question, mind=""):
    if mind in LABELS and mind != PERSONA_UNKNOWN:
        return {mind: FAQ_MAX}   # ortak SSS: soru açıkça bir persona'ya etiketli
    return {p: min(FAQ_MAX, v * FAQ_WEIGHT) for p, v in score_content(question).items()}


def apply_faq(session, question, mind="", seconds=None):
    """SSS sinyali iki aşamada:
      açtı (seconds=None)   → sinyalin %30'u
      kapattı / çıktı       → kalan %70 × min(okuma sn / 8, 1); 2 sn altı = okumadı
    Aynı soru her aşamada ziyaret başına bir kez sayılır."""
    q = re.sub(r"\s+", " ", str(question or "")).strip()[:160]
    if not q:
        return False
    phase = "faq" if seconds is None else "faqr"
    key = f"{phase}:{normalize(q)[:60]}"
    seen = list(session.pages_seen or [])
    if key in seen:
        return False
    seen.append(key)
    session.pages_seen = seen[-40:]
    sig = _faq_signal(q, mind)
    if seconds is None:
        share, label = FAQ_OPEN_SHARE, f"SSS açtı: {q}"
    else:
        secs = max(0, int(seconds or 0))
        factor = 0.0 if secs < FAQ_READ_MIN else min(secs / FAQ_READ_FULL, 1.0)
        share, label = (1 - FAQ_OPEN_SHARE) * factor, f"SSS okudu ({secs} sn): {q}"
    page = dict(session.page_scores or {})
    added = {}
    for p, w in sig.items():
        v = round(w * share, 3)
        if v > 0:
            page[p] = round(min(PERSONA_CAP, page.get(p, 0.0) + v), 2)
            added[p] = v
    session.page_scores = page
    add_evidence(session, phase, label, added or {next(iter(sig), PERSONA_UNKNOWN): 0} if sig else {PERSONA_UNKNOWN: 0})
    return True


def snapshot(session):
    """Şu anki zihin durumu: en olası persona, ilk 3 olasılık, son kanıtlar (neden)."""
    from .engine import infer

    if session is None:
        return {}
    probs = infer(session)
    ranked = sorted(((p, v) for p, v in probs.items() if p != PERSONA_UNKNOWN), key=lambda x: -x[1])
    top, conf = ranked[0] if ranked else (PERSONA_UNKNOWN, 0.0)
    if probs.get(PERSONA_UNKNOWN, 0) > conf:
        top, conf = PERSONA_UNKNOWN, probs[PERSONA_UNKNOWN]
    why = [{"k": e.get("k"), "l": e.get("l"), "p": e.get("p"), "w": e.get("w", 0)}
           for e in (session.evidence or [])[-10:]][::-1]
    signals = sum(1 for e in (session.evidence or []) if float(e.get("w") or 0) > 0)
    # Emin olmadan etiketleme: tek bir tık / kısa bakış "güçlü" sayılmaz
    if top == PERSONA_UNKNOWN or signals < 2 or conf < 0.45:
        level = "weak"
    elif signals >= 4 and conf >= 0.65:
        level = "strong"
    else:
        level = "medium"
    return {
        "top": top,
        "label": LABELS.get(top, top),
        "level": level,
        "signals": signals,
        "confidence": round(conf, 3),
        # Yalnızca gerçek kanıtı olanlar (kanıtsız persona'lar softmax tabanında ~%5-6 kalır — gürültü)
        "scores": {p: round(v, 3) for p, v in ranked[:3] if v > (ranked[-1][1] if ranked else 0) * 1.3},
        "why": why,
        "visit": session.total_sessions,
    }


def describe(mind, short=False):
    """Admin / e-posta için düz metin: '😟 Korku / ağrı %62 · 💶 Fiyat %21'."""
    if not mind:
        return "—"
    parts = [f"{LABELS.get(p, p)} %{round(v * 100)}" for p, v in (mind.get("scores") or {}).items()]
    head = " · ".join(parts) or mind.get("label", "—")
    if mind.get("top") == PERSONA_UNKNOWN or mind.get("level") == "weak":
        head = f"{LABELS[PERSONA_UNKNOWN]} (zayıf sinyal) — {head}"
    if short:
        return head
    why = "; ".join(f"{LABELS.get(w['p'], '').split(' ')[0]} {w['l']}" for w in (mind.get("why") or [])[:5])
    return f"{head}\nNeden: {why}" if why else head
