import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

logger = logging.getLogger(__name__)

VALID_EVENTS = {
    "whatsapp_click","phone_click","maps_click","cta_click",
    "form_start","form_submit","video_play","video_progress",
    "scroll_depth","time_on_page","section_view",
    "instagram_click","youtube_click","before_after_interact",
    "chatbot_open","chatbot_message","language_switch","review_read",
}

def _get_or_create_session(request):
    """Session'ı al — yoksa yeni oluştur."""
    session = getattr(request, "tracking_session", None)
    if session:
        return session
    # Middleware çalışmadıysa manual oluştur
    try:
        from .service import get_or_create_session
        return get_or_create_session(request)
    except Exception as e:
        logger.warning(f"Session create failed: {e}")
        return None


MIND_EVENTS = {"faq_open", "faq_read", "cert_click", "before_after", "before_after_interact", "video_play", "youtube_click"}

@csrf_exempt
@require_POST
def collect_event(request):
    if getattr(request, "is_bot", False):
        return JsonResponse({"ok": True})
    from . import visitor

    try:
        _peek = json.loads(request.body.decode("utf-8"))
    except Exception:  # noqa: BLE001
        _peek = {}
    # Çerez silinmiş ama localStorage'da kimlik varsa onu kullan (tracker.js her olayda `vid` gönderir)
    body_vid = visitor.clean(_peek.get("vid")) if isinstance(_peek, dict) else ""
    if body_vid and not visitor.clean(request.COOKIES.get(visitor.COOKIE)):
        request._dt_vid, request._dt_vid_new = body_vid, True
    session = _get_or_create_session(request)
    vid = visitor.get_visitor_id(request)
    if session and vid and not session.visitor_id:
        type(session).objects.filter(pk=session.pk).update(visitor_id=vid)
    if not session:
        return JsonResponse({"ok": False, "error": "no session"}, status=400)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    event_type = str(body.get("event_type", ""))[:30]

    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    page_url = str(body.get("page_url", ""))[:500]
    if event_type in VALID_EVENTS:
        try:
            from .service import record_event
            record_event(session, event_type, data, page_url)
        except Exception as e:
            logger.error(f"collect_event: {e}")

    # Aynı event persona motorunu da besler (tek beacon)
    try:
        from apps.persona.engine import record_event as persona_record
        persona_record(request.session.session_key, event_type, data, page_url, str(body.get("page_type", "")))
    except Exception as e:
        logger.error(f"persona event: {e}")

    # localStorage'da saklanan ilk-dokunuş reklam atfı (gclid/fbclid/utm) — oturumda yoksa doldur
    attr = body.get("attr") if isinstance(body.get("attr"), dict) else {}
    if session and attr:
        fields = ("gclid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
        upd = {f: str(attr[f])[:255] for f in fields if attr.get(f) and not getattr(session, f, None)}
        if upd:
            type(session).objects.filter(pk=session.pk).update(**upd)

    payload = {"ok": True}
    if event_type in MIND_EVENTS or data.get("position") == "price-note":
        # Sayfa yenilenmeden konumlandırma: tracker.js bunu localStorage'a (dt_mind) yazar, mesajı anında değiştirir
        from .service import current_mindset

        m = current_mindset(request.session.session_key)
        if m:
            payload["mind"] = m.get("top", "")
    resp = JsonResponse(payload)
    return visitor.set_cookie(request, resp)  # çerez silinmişse localStorage'daki kimlikle geri yaz


@csrf_exempt
@require_POST
def collect_pageview(request):
    if getattr(request, "is_bot", False):
        return JsonResponse({"ok": True})
    from . import visitor

    try:
        _peek = json.loads(request.body.decode("utf-8"))
    except Exception:  # noqa: BLE001
        _peek = {}
    # Çerez silinmiş ama localStorage'da kimlik varsa onu kullan (tracker.js her olayda `vid` gönderir)
    body_vid = visitor.clean(_peek.get("vid")) if isinstance(_peek, dict) else ""
    if body_vid and not visitor.clean(request.COOKIES.get(visitor.COOKIE)):
        request._dt_vid, request._dt_vid_new = body_vid, True
    session = _get_or_create_session(request)
    vid = visitor.get_visitor_id(request)
    if session and vid and not session.visitor_id:
        type(session).objects.filter(pk=session.pk).update(visitor_id=vid)

    try:
        body = json.loads(request.body.decode("utf-8"))
        if session:
            from .models import PageView
            PageView.objects.create(
                session  = session,
                url      = body.get("url", "")[:500],
                title    = body.get("title", "")[:300],
                referrer = body.get("referrer", "")[:500],
            )
            session.page_views += 1
            session.save(update_fields=["page_views","last_seen"])
    except Exception as e:
        logger.error(f"collect_pageview: {e}")

    return JsonResponse({"ok": True})


@csrf_exempt
@require_POST
def submit_lead(request):
    _get_or_create_session(request)  # request.tracking_session'ı garanti eder

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    name    = body.get("name", "").strip()
    phone   = body.get("phone", "").strip()
    message = body.get("message", "").strip()
    page    = body.get("page", "").strip()
    lang    = body.get("language", "").strip()

    if not phone and not name:
        return JsonResponse({"ok": False, "error": "name or phone required"}, status=400)

    try:
        from .service import create_lead
        lead = create_lead(request, name=name, phone=phone, email=str(body.get("email", "")).strip(),
                           message=message, page=page, language=lang)
        return JsonResponse({"ok": True, "lead_id": lead.id})
    except Exception as e:
        logger.error(f"submit_lead: {e}")
        return JsonResponse({"ok": False, "error": "server error"}, status=500)


@csrf_exempt
@require_POST
def whatsapp_webhook(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    wa_phone   = body.get("phone", "").strip()
    wa_message = body.get("message", "").strip()
    if not wa_phone:
        return JsonResponse({"ok": False, "error": "phone required"}, status=400)

    from .service import match_whatsapp
    result = match_whatsapp(wa_phone, wa_message)
    return JsonResponse({"ok": True, **result})


def session_status(request):
    session = getattr(request, "tracking_session", None)
    if not session:
        return JsonResponse({"session": None})
    return JsonResponse({"session": {
        "id":             str(session.id),
        "traffic_source": session.traffic_source,
        "has_gclid":      bool(session.gclid),
        "has_fbclid":     bool(session.fbclid),
        "device_type":    session.device_type,
        "ip_country":     session.ip_country,
        "is_lead":        session.is_lead,
        "intent_score":   session.conversion_intent_score,
        "persona":        session.assigned_persona,
    }})


@staff_member_required
def dashboard_stats(request):
    from django.db.models import Count
    from .models import VisitorSession, Lead
    from django.utils import timezone
    from datetime import timedelta

    now         = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start  = today_start - timedelta(days=7)
    sessions    = VisitorSession.objects.all()
    leads       = Lead.objects.all()

    return JsonResponse({
        "today": {
            "sessions":    sessions.filter(created_at__gte=today_start).count(),
            "leads":       leads.filter(created_at__gte=today_start).count(),
            "wa_clicks":   sessions.filter(created_at__gte=today_start, whatsapp_clicks__gte=1).count(),
            "phone_clicks": sessions.filter(created_at__gte=today_start, phone_clicks__gte=1).count(),
        },
        "week": {
            "sessions":  sessions.filter(created_at__gte=week_start).count(),
            "leads":     leads.filter(created_at__gte=week_start).count(),
            "converted": leads.filter(created_at__gte=week_start, status="treated").count(),
        },
        "total": {
            "sessions":  sessions.count(),
            "leads":     leads.count(),
            "converted": leads.filter(status="treated").count(),
        },
        "by_source": list(sessions.values("traffic_source").annotate(count=Count("id")).order_by("-count")),
        "by_country": list(sessions.exclude(ip_country="").values("ip_country").annotate(count=Count("id")).order_by("-count")[:10]),
        "by_device": list(sessions.exclude(device_type="").values("device_type").annotate(count=Count("id"))),
        "top_pages": list(sessions.exclude(landing_page="").values("landing_page").annotate(count=Count("id")).order_by("-count")[:10]),
    })
