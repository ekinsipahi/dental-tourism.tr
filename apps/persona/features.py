"""Persona inference + policy + ML için ortak özellik çıkarımı."""
from .models import PERSONAS

PAID = {"google_ads", "meta_ads"}
ORGANIC = {"google_organic", "bing_organic"}
SOCIAL = {"social", "facebook", "instagram"}


def source_bucket(session) -> str:
    src = (session.referral_source or "").lower()
    if src in PAID:
        return "paid"
    if src in ORGANIC or "google" in src or "bing" in src:
        return "organic"
    if src in SOCIAL:
        return "social"
    if src in ("", "direct", "unknown"):
        return "direct"
    return "referral"


def inferred_persona(session) -> str:
    probs = session.persona_scores or {}
    return max(probs, key=probs.get) if probs else "unknown"


def segment_key(session) -> str:
    """Bandit bağlamı: TAHMİN EDİLEN persona × cihaz × kaynak.

    Böylece bandit "bu tipteki ziyaretçiye hangi varyant daha çok dönüştürüyor" sorusunu öğrenir.
    Az veri olan segmentler önce persona seviyesine (backoff), sonra global orana geri düşer."""
    return f"{inferred_persona(session)}|{session.device_type or 'unk'}|{source_bucket(session)}"


def backoff_key(segment: str) -> str:
    return segment.split("|", 1)[0] + "|*"


def context_features(session) -> dict:
    """Policy kararı anındaki bağlam (ML conversion modelinin girdisi)."""
    intent = session.intent_scores or {}
    f = {
        "lang": session.language_code or "xx",
        "device": session.device_type or "unk",
        "source": source_bucket(session),
        "country": session.country_code or "xx",
        "visit_number": min(session.total_sessions, 5),
        "has_query": 1 if session.search_query else 0,
        "pageviews": min(session.total_page_views, 20),
        "time_spent": min(session.total_time_spent_sec, 1800),
        "max_scroll": session.max_scroll_depth,
        "price_signal": session.price_section_clicks + session.price_section_time / 30,
        "review_signal": session.review_section_time / 30 + session.testimonial_reads,
        "aesthetic_signal": session.before_after_views + session.before_after_time / 30 + session.gallery_views,
        "safety_signal": session.certification_clicks + session.safety_section_time / 30,
        "video_signal": session.video_plays + session.video_watch_time / 60,
        "blog_reads": session.blog_reads,
    }
    for p in PERSONAS:
        f[f"intent_{p}"] = float(intent.get(p, 0.0))
    for p, v in (session.persona_scores or {}).items():
        f[f"infer_{p}"] = float(v)
    return f


def with_arm(features: dict, persona: str) -> dict:
    """Bağlam × aksiyon etkileşim özellikleri — modelin 'doğru kişiye doğru varyant' etkisini
    az veriyle de öğrenebilmesi için açıkça verilir."""
    row = dict(features)
    row["arm"] = persona
    infer = {k[6:]: v for k, v in features.items() if k.startswith("infer_")}
    best = max(infer, key=infer.get) if infer else "unknown"
    row["arm_infer_prob"] = float(infer.get(persona, 0.0))
    row["arm_is_inferred"] = 1.0 if persona == best else 0.0
    row["arm_intent"] = float(features.get(f"intent_{persona}", 0.0))
    row["arm_is_default"] = 1.0 if persona == "unknown" else 0.0
    return row
