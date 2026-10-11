"""
Persona motoru — middleware ve tracking API buradan çağırır.

  get_or_create_persona(request) → şablonlara giden persona dict'i
  record_event(session_key, ...)  → davranış sinyali + dönüşüm geri bildirimi
"""
import logging
import math
import random
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from . import bandit
from .features import context_features, segment_key
from .intent import intent_scores
from .models import (PERSONA_FEAR, PERSONA_PREMIUM, PERSONA_PRICE, PERSONA_READY, PERSONA_SHAME,
                     PERSONA_SKEPTIC, PERSONA_THEME, PERSONA_TRUST, PERSONA_UNKNOWN, PERSONA_URGENCY,
                     PERSONAS, BehaviorEvent, PersonaExposure, VisitorSession)

logger = logging.getLogger(__name__)

CACHE_TTL = 60 * 5
VISIT_GAP = timedelta(minutes=30)
SWITCH_CONFIDENCE = 0.45
CONVERSION_EVENTS = {"whatsapp_click": "whatsapp", "phone_click": "phone", "form_submit": "form"}

DEFAULT_RESULT = {
    "persona": PERSONA_UNKNOWN, "inferred": PERSONA_UNKNOWN, "confidence": 0.0,
    "theme_class": "theme-default", "method": "none", "is_known": False,
    "is_second_visit": False, "scores": {},
}


# ══ 1. Inference ═════════════════════════════════════════════════════════════
def behavior_scores(s: VisitorSession) -> dict:
    """Sayfa içi davranıştan persona kanıtları (log-skor katkıları)."""
    sc = {p: 0.0 for p in PERSONAS}

    # Fiyat
    sc[PERSONA_PRICE] += min(s.price_section_clicks, 4) * 0.8 + min(s.price_section_time, 180) / 45
    # Estetik
    sc[PERSONA_SHAME] += s.before_after_views * 1.2 + min(s.before_after_time, 180) / 40 + s.gallery_views * 0.4
    sc[PERSONA_PREMIUM] += s.gallery_views * 0.5 + s.doctor_profile_views * 0.8
    # Güvenlik / korku
    sc[PERSONA_FEAR] += s.certification_clicks * 1.5 + min(s.safety_section_time, 180) / 40 \
        + s.doctor_profile_views * 0.4 + s.faq_interactions * 0.5
    # Güven
    sc[PERSONA_TRUST] += min(s.video_watch_time, 300) / 60 + s.video_plays * 0.6 \
        + min(s.review_section_time, 240) / 50 + s.testimonial_reads * 0.6
    # Araştırmacı
    sc[PERSONA_SKEPTIC] += s.faq_interactions * 0.6 + s.blog_reads * 0.7 + min(s.review_section_time, 240) / 80
    if s.max_scroll_depth >= 75:
        sc[PERSONA_SKEPTIC] += 0.6
        sc[PERSONA_TRUST] += 0.4
    if s.total_time_spent_sec > 300:
        sc[PERSONA_SKEPTIC] += 0.8
        sc[PERSONA_TRUST] += 0.6
    # Acil
    sc[PERSONA_URGENCY] += s.urgency_keyword_hits * 1.5
    if 0 < s.total_time_spent_sec < 40 and s.cta_clicks:
        sc[PERSONA_URGENCY] += 0.8
    # Hazır
    sc[PERSONA_READY] += s.cta_clicks * 0.6 + s.form_starts * 1.5 + s.whatsapp_clicks * 2.0
    if s.total_sessions >= 3:
        sc[PERSONA_READY] += 1.0
        sc[PERSONA_TRUST] += 0.5
    return sc


def infer(s: VisitorSession) -> dict:
    """Arama niyeti öncülü + davranış kanıtı → persona olasılık dağılımı.

    Kanıt yoksa 'unknown' baskın kalır (varsayılan sayfa).
    """
    intent = (s.intent_scores or {})
    beh = behavior_scores(s)
    logits = {p: 0.9 * intent.get(p, 0.0) + beh[p] for p in PERSONAS}
    evidence = sum(v for v in logits.values() if v > 0)
    # 'unknown' kolu: kanıt arttıkça zayıflar
    logits[PERSONA_UNKNOWN] = max(0.0, 2.0 - evidence * 0.6)
    m = max(logits.values())
    exp = {k: math.exp(v - m) for k, v in logits.items()}
    z = sum(exp.values())
    return {k: round(v / z, 4) for k, v in exp.items()}


# ══ 2. Policy ═════════════════════════════════════════════════════════════════
def decide(session: VisitorSession, probs: dict):
    """Hangi varyant gösterilecek? Döner: (persona, method, propensity, features, model_version)."""
    from .ml import active_model, predict_arms

    features = context_features(session)
    model, version = active_model()
    if model is not None:
        eps = settings.PERSONA_EXPLORATION_RATE
        arms = bandit.ARMS
        if random.random() < eps:
            pick = random.choice(arms)
            return pick, "ml", eps / len(arms), features, version
        preds = predict_arms(model, features, arms)
        pick = max(preds, key=preds.get)
        return pick, "ml", (1 - eps) + eps / len(arms), features, version

    pick, propensity = bandit.choose(segment_key(session), probs)
    return pick, "bandit", propensity, features, ""


def _start_exposure(session, probs):
    persona, method, propensity, features, version = decide(session, probs)
    inferred = max(probs, key=probs.get) if probs else PERSONA_UNKNOWN
    seg = segment_key(session)
    exp = PersonaExposure.objects.create(
        session=session, visit_number=session.total_sessions, persona=persona, inferred_persona=inferred,
        segment=seg, policy=method, propensity=propensity, features=features, model_version=version or "",
    )
    bandit.record_impression(seg, persona)
    session.shown_persona = persona
    return exp


# ══ 3. Request entry point ════════════════════════════════════════════════════
def funnel_stage(session):
    """Huni aşaması — arayüz buna göre değişir (base.html data-stage):
    awareness     → ilk keşif: eğitici, sakin
    consideration → dönen / fiyat, önce-sonra, hekim, 3+ sayfa: güven kanıtı öne çıkar
    decision      → WhatsApp / telefon / form / CTA'ya dokundu: iletişim butonları öne çıkar
    """
    if (session.whatsapp_clicks or session.phone_clicks or session.form_starts or session.form_submits
            or session.cta_clicks):
        return "decision"
    if (session.total_sessions >= 2 or session.total_page_views >= 3 or session.price_section_clicks
            or session.price_section_time >= 10 or session.before_after_views or session.doctor_profile_views
            or session.testimonial_reads >= 2):
        return "consideration"
    return "awareness"


def _result(session, probs, method):
    shown = session.shown_persona or PERSONA_UNKNOWN
    inferred = max(probs, key=probs.get) if probs else PERSONA_UNKNOWN
    return {
        "persona": shown,
        "inferred": inferred,
        "confidence": round(probs.get(inferred, 0.0), 3),
        "theme_class": PERSONA_THEME.get(shown, "theme-default"),
        "method": method,
        "is_known": shown != PERSONA_UNKNOWN,
        "is_second_visit": session.total_sessions >= 2,
        "stage": funnel_stage(session),
        "scores": probs,
        "session_id": session.pk,
    }


def _forced(request):
    """?persona=price ile önizleme (DEBUG veya staff). Exposure kaydedilmez."""
    forced = request.GET.get("persona")
    allowed = settings.DEBUG or (getattr(request, "user", None) and request.user.is_staff)
    if forced is not None and allowed:
        if forced in PERSONAS:
            request.session["persona_preview"] = forced
        else:
            request.session.pop("persona_preview", None)
    preview = request.session.get("persona_preview") if allowed else None
    if preview:
        return {**DEFAULT_RESULT, "persona": preview, "inferred": preview, "confidence": 1.0,
                "theme_class": PERSONA_THEME[preview], "method": "forced", "is_known": True}
    return None


def get_or_create_persona(request):
    if getattr(request, "is_bot", False):
        return dict(DEFAULT_RESULT)

    forced = _forced(request)
    if forced:
        return forced

    if not request.session.session_key:
        request.session.save()
    key = request.session.session_key
    cache_key = f"persona:{key}"
    cached = cache.get(cache_key)
    if cached and not request.GET.get("utm_term"):
        return cached

    now = timezone.now()
    session = VisitorSession.objects.filter(session_key=key).first()
    tracking = getattr(request, "tracking_session", None)
    from apps.tracking.visitor import get_visitor_id

    vid = get_visitor_id(request)
    if session is None and vid:
        # Dönen ziyaretçi (yeni sessionid, aynı dt_vid): önceki kaydı bu oturuma bağla — geçmiş korunur
        session = VisitorSession.objects.filter(visitor_id=vid).order_by("-last_seen").first()
        if session is not None:
            session.session_key = key
    if session is None:
        ctx = intent_scores(request)
        session = VisitorSession(
            session_key=key,
            language_code=getattr(request, "LANGUAGE_CODE", "") or "",
            device_type=_detect_device(request),
            referral_source=(getattr(tracking, "traffic_source", "") or _detect_referral(request)),
            country_code=(getattr(tracking, "ip_country", "") or ""),
            landing_path=request.path[:500],
            search_query=ctx["query"],
            intent_scores=ctx["scores"],
            visit_started_at=now,
            visitor_id=vid,
        )
        session.save()
    else:
        if session.last_seen and now - session.last_seen > VISIT_GAP:
            # Yeni ziyaret
            session.total_sessions += 1
            session.visit_started_at = now
            session.last_persona_at_exit = session.shown_persona
            session.shown_persona = PERSONA_UNKNOWN
            ctx = intent_scores(request)
            if ctx["query"]:
                session.search_query = ctx["query"]
                merged = dict(session.intent_scores or {})
                for p, v in ctx["scores"].items():
                    merged[p] = max(merged.get(p, 0), v)
                session.intent_scores = merged
            if tracking and getattr(tracking, "traffic_source", ""):
                session.referral_source = tracking.traffic_source
        session.language_code = getattr(request, "LANGUAGE_CODE", session.language_code)
        if vid and not session.visitor_id:
            session.visitor_id = vid

    probs = infer(session)
    best = max(probs, key=probs.get)
    session.persona_scores = probs
    if best != session.assigned_persona:
        session.update_persona(best, probs[best], "rule")

    exposure = PersonaExposure.objects.filter(session=session, visit_number=session.total_sessions).first()
    method = exposure.policy if exposure else "bandit"
    if exposure is None:
        exposure = _start_exposure(session, probs)
        method = exposure.policy
    elif (exposure.persona == PERSONA_UNKNOWN and not exposure.converted and best != PERSONA_UNKNOWN
          and probs[best] >= SWITCH_CONFIDENCE):
        # Ziyaret varsayılan sayfayla başladı ama güçlü davranış sinyali geldi → bir kez kişiselleştir
        bandit.undo_impression(exposure.segment, exposure.persona)
        exposure.delete()
        exposure = _start_exposure(session, probs)
        method = exposure.policy
    else:
        session.shown_persona = exposure.persona

    session.save()
    result = _result(session, probs, method)
    cache.set(cache_key, result, CACHE_TTL)
    return result


# ══ 4. Events / feedback ══════════════════════════════════════════════════════
EVENT_ALIASES = {
    "scroll_depth": "scroll", "before_after_interact": "before_after", "youtube_click": "video_play",
    "maps_click": "click", "instagram_click": "click", "language_switch": "click",
    "chatbot_open": "click", "chatbot_message": "click", "video_progress": "video_time",
}
SECTION_FIELDS = {
    "price": ("price_section_time", "price_section_clicks"),
    "reviews": ("review_section_time", "testimonial_reads"),
    "safety": ("safety_section_time", "certification_clicks"),
    "before_after": ("before_after_time", "before_after_views"),
    "gallery": (None, "gallery_views"),
    "doctor": (None, "doctor_profile_views"),
    "faq": (None, "faq_interactions"),
    "video": ("video_watch_time", None),
}


def record_event(session_key, event_type, data=None, page_url="", page_type=""):
    data = data if isinstance(data, dict) else {}
    event_type = EVENT_ALIASES.get(event_type, event_type)
    session = VisitorSession.objects.filter(session_key=session_key).first()
    if session is None:
        return
    valid = {c for c, _ in BehaviorEvent.EVENT_TYPES}
    if event_type not in valid:
        return
    BehaviorEvent.objects.create(session=session, event_type=event_type, data=data,
                                 page_url=(page_url or "")[:500], page_type=(page_type or "")[:30])
    _update_aggregates(session, event_type, data, page_type)
    if event_type in CONVERSION_EVENTS:
        _record_conversion(session, CONVERSION_EVENTS[event_type])
    cache.delete(f"persona:{session_key}")


def _num(v, cap=3600):
    try:
        return max(0, min(int(float(v)), cap))
    except (TypeError, ValueError):
        return 0


def _update_aggregates(s, event_type, data, page_type):
    fields = {"last_seen"}

    def inc(field, by=1):
        setattr(s, field, getattr(s, field) + by)
        fields.add(field)

    if event_type == "scroll":
        d = _num(data.get("depth"), 100)
        s.avg_scroll_depth = (s.avg_scroll_depth + d) / 2 if s.avg_scroll_depth else d
        s.max_scroll_depth = max(s.max_scroll_depth, d)
        fields |= {"avg_scroll_depth", "max_scroll_depth"}
    elif event_type == "time_on_page":
        inc("total_time_spent_sec", _num(data.get("seconds"), 1800))
        inc("total_page_views")
        if page_type == "blog_detail":
            inc("blog_reads")
    elif event_type in ("section_view", "section_time"):
        section = str(data.get("section", ""))
        time_field, count_field = SECTION_FIELDS.get(section, (None, None))
        if event_type == "section_time" and time_field:
            inc(time_field, _num(data.get("seconds"), 600))
        elif event_type == "section_view" and count_field:
            inc(count_field)
    elif event_type == "price_hover":
        inc("price_section_clicks")
    elif event_type == "gallery_view":
        inc("before_after_views" if data.get("section") == "before_after" else "gallery_views")
    elif event_type == "before_after":
        inc("before_after_views")
        inc("before_after_time", _num(data.get("seconds"), 600))
    elif event_type == "cert_click":
        inc("certification_clicks")
    elif event_type == "whatsapp_click":
        inc("whatsapp_clicks")
    elif event_type == "phone_click":
        inc("phone_clicks")
    elif event_type == "cta_click":
        inc("cta_clicks")
    elif event_type == "form_start":
        inc("form_starts")
    elif event_type == "form_submit":
        inc("form_submits")
    elif event_type == "faq_open":
        inc("faq_interactions")
    elif event_type == "review_read":
        inc("review_section_time", _num(data.get("seconds"), 600))
    elif event_type == "video_play":
        inc("video_plays")
    elif event_type == "video_time":
        inc("video_watch_time", _num(data.get("seconds"), 1800))
    elif event_type == "urgency_cta":
        inc("urgency_keyword_hits")
    elif event_type == "bounce":
        inc("bounce_count")
        s.last_persona_at_exit = s.shown_persona
        fields.add("last_persona_at_exit")
    s.save(update_fields=list(fields))


def _record_conversion(session, conversion_type):
    now = timezone.now()
    if not session.converted:
        session.converted = True
        session.converted_at = now
        session.save(update_fields=["converted", "converted_at"])
    exposure = PersonaExposure.objects.filter(session=session).order_by("-created_at").first()
    if exposure and not exposure.converted:
        exposure.converted = True
        exposure.conversion_type = conversion_type
        exposure.converted_at = now
        exposure.save(update_fields=["converted", "conversion_type", "converted_at"])
        bandit.record_conversion(exposure.segment, exposure.persona)


# ══ Helpers ═══════════════════════════════════════════════════════════════════
def _detect_device(request):
    ua = request.META.get("HTTP_USER_AGENT", "").lower()
    if "ipad" in ua or "tablet" in ua:
        return "tablet"
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        return "mobile"
    return "desktop"


def _detect_referral(request):
    ref = request.META.get("HTTP_REFERER", "").lower()
    if request.GET.get("gclid"):
        return "google_ads"
    if request.GET.get("fbclid"):
        return "meta_ads"
    if not ref:
        return "direct"
    if "google" in ref:
        return "google_organic"
    if "bing" in ref:
        return "bing_organic"
    if "facebook" in ref or "instagram" in ref:
        return "social"
    return "referral"
