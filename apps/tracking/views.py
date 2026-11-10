import hashlib
import hmac
import json
import logging
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.http import Http404, JsonResponse
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
    "email_click","nav_click",
    "contact_return",  # telefon/WhatsApp/harita tıklamasından sonra sekmeye dönüş (away_seconds, likely_contacted)
}

def _page_request(request, body):
    """Beacon gövdesindeki sayfa bağlamı (url, referrer) ile istek vekili — oturum/persona burada doğru veriyle açılır."""
    from .service import PageRequest

    body = body if isinstance(body, dict) else {}
    url = body.get("url") or body.get("page_url") or ""
    if not url and isinstance(body.get("events"), list) and body["events"]:
        first = body["events"][0] if isinstance(body["events"][0], dict) else {}
        url = first.get("page_url", "")
    return PageRequest(request, str(url)[:1000], str(body.get("referrer", ""))[:1000])


def _get_or_create_session(request, body=None):
    """Takip oturumu: varsa al, yoksa SAYFA bağlamıyla (beacon gövdesi) oluştur — sayfa GET'i artık oturum açmaz."""
    try:
        from .service import get_or_create_session

        session = get_or_create_session(_page_request(request, body) if body else request)
        request.tracking_session = session
        return session
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Session create failed: {e}")
        return None


# Kimliksiz uçlar için koruma: lead ucu oturum çerezi + aynı köken + hız limiti ister; webhook paylaşılan anahtar ister.
LEAD_LIMIT_PER_SESSION = 3   # saatte, oturum başına
LEAD_LIMIT_PER_IP = 5        # saatte, IP başına (iki gunicorn işçisi → pratikte en çok iki katı)
WEBHOOK_LIMIT_PER_IP = 120   # saatte — anahtar denemesine karşı


def _ip_hash(request):
    from .service import _get_client_ip

    return hashlib.sha256((_get_client_ip(request) or "?").encode()).hexdigest()[:24]


def _rate_limited(key, limit, window):
    """Süreç içi önbellekte basit sayaç: pencere içinde limit aşıldıysa True."""
    key = f"rl:{key}"
    n = cache.get(key, 0)
    if n >= limit:
        return True
    if n == 0:
        cache.set(key, 1, window)
    else:
        try:
            cache.incr(key)
        except ValueError:  # pencere bu arada kapandı
            cache.set(key, 1, window)
    return False


def _same_origin(request):
    """Origin/Referer başlığı varsa bizim alanımızdan olmalı (başka siteden / scriptten POST reddedilir)."""
    src = request.META.get("HTTP_ORIGIN") or request.META.get("HTTP_REFERER") or ""
    if not src:
        return True  # başlık yok: oturum çerezi + hız limiti korur
    host = (urlparse(src).hostname or "").lower()
    try:
        own = request.get_host().split(":")[0].lower()
    except Exception:  # noqa: BLE001
        own = ""
    allowed = {h.lstrip(".").lower() for h in settings.ALLOWED_HOSTS}
    # Dış siteler (ör. https://drdevrim.com) TRACKING_ALLOWED_ORIGINS ile eklenir — ileride CORS entegrasyonu için
    allowed |= {(urlparse(o).hostname or o).lstrip(".").lower() for o in settings.TRACKING_ALLOWED_ORIGINS if o}
    return bool(host) and (host == own or host in allowed or "*" in allowed)


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
    session = _get_or_create_session(request, _peek)
    vid = visitor.get_visitor_id(request)
    if session and vid and not session.visitor_id:
        type(session).objects.filter(pk=session.pk).update(visitor_id=vid)
    if not session:
        return JsonResponse({"ok": False, "error": "no session"}, status=400)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    # Tek olay {event_type,…} ya da toplu {events:[{event_type,…}, …]} (tracker.js 4 sn'de bir / çıkışta toplar).
    # Toplu istekte takip oturumu (middleware) ve persona oturumu BİR kez okunur, her olay için ayrı ayrı değil.
    events = body.get("events") if isinstance(body.get("events"), list) else [body]
    events = [e for e in events[:50] if isinstance(e, dict)]
    from .service import record_event
    from apps.persona.engine import record_event as persona_record
    from apps.persona.models import VisitorSession as PersonaSession

    skey = request.session.session_key
    psession = PersonaSession.objects.filter(session_key=skey).first() if skey else None
    if psession is None and skey:
        try:  # olay pageview beacon'ından önce geldiyse persona oturumu burada açılır
            from apps.persona.engine import get_or_create_persona

            preq = _page_request(request, body)
            preq.tracking_session = session
            get_or_create_persona(preq, create=True)
            psession = PersonaSession.objects.filter(session_key=skey).first()
        except Exception as e:  # noqa: BLE001
            logger.error(f"persona create: {e}")
    wants_mind = False
    for ev in events:
        event_type = str(ev.get("event_type", ""))[:30]
        data = ev.get("data") if isinstance(ev.get("data"), dict) else {}
        page_url = str(ev.get("page_url", ""))[:500]
        if event_type in VALID_EVENTS:
            try:
                record_event(session, event_type, data, page_url)
            except Exception as e:
                logger.error(f"collect_event: {e}")
        # Aynı event persona motorunu da besler (tek beacon)
        try:
            persona_record(skey, event_type, data, page_url, str(ev.get("page_type", "")), session=psession)
        except Exception as e:
            logger.error(f"persona event: {e}")
        if event_type in MIND_EVENTS or data.get("position") == "price-note":
            wants_mind = True

    # localStorage'da saklanan ilk-dokunuş reklam atfı (gclid/fbclid/utm) — oturumda yoksa doldur
    attr = body.get("attr") if isinstance(body.get("attr"), dict) else {}
    if session and attr:
        fields = ("gclid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
        upd = {f: str(attr[f])[:255] for f in fields if attr.get(f) and not getattr(session, f, None)}
        if upd:
            type(session).objects.filter(pk=session.pk).update(**upd)

    payload = {"ok": True}
    if wants_mind:
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
    session = _get_or_create_session(request, _peek)
    vid = visitor.get_visitor_id(request)
    if session and vid and not session.visitor_id:
        type(session).objects.filter(pk=session.pk).update(visitor_id=vid)

    try:
        body = json.loads(request.body.decode("utf-8"))
        if session:
            # Persona oturumu da ilk beacon'da doğar (sayfa GET'inde DB'ye gidilmez); sayfanın GET/referrer bağlamıyla
            try:
                from apps.persona.engine import get_or_create_persona

                preq = _page_request(request, body)
                preq.tracking_session = session
                get_or_create_persona(preq, create=True)
            except Exception as e:  # noqa: BLE001
                logger.error(f"persona create: {e}")
            from .models import PageView
            PageView.objects.create(
                session  = session,
                url      = body.get("url", "")[:500],
                title    = body.get("title", "")[:300],
                referrer = body.get("referrer", "")[:500],
            )
            session.page_views += 1
            try:  # sayfanın persona sinyali (GET'te değil burada: sayfa isteği DB'ye gitmesin)
                from urllib.parse import urlparse

                from apps.persona.engine import observe_page

                observe_page(request.session.session_key, urlparse(body.get("url", "")).path or "/")
            except Exception as e:  # noqa: BLE001
                logger.error(f"persona observe: {e}")
            fields = ["page_views", "last_seen"]
            # Tarayıcı saat dilimi + ekran: IP proxy/VPN'den geçse de gerçek ülkeyi gösterir (geo.py)
            from .geo import is_valid_tz

            if is_valid_tz(body.get("tz")) and body["tz"] != session.timezone_name:
                session.timezone_name = body["tz"]
                fields.append("timezone_name")
            for key, f in (("sw", "screen_width"), ("sh", "screen_height")):
                v = body.get(key)
                if isinstance(v, int) and 0 < v < 32768 and not getattr(session, f):
                    setattr(session, f, v)
                    fields.append(f)
            session.save(update_fields=fields)
    except Exception as e:
        logger.error(f"collect_pageview: {e}")

    return JsonResponse({"ok": True})


@csrf_exempt
@require_POST
def submit_lead(request):
    # Kimliksiz uç: yalnızca sitede sayfa açmış (oturum çerezli), aynı kökenden gelen, bot olmayan ve hız limitini
    # aşmayan istekler lead oluşturabilir — dışarıdan script ile sahte lead basılamaz.
    session_cookie = request.COOKIES.get(settings.SESSION_COOKIE_NAME, "")
    if getattr(request, "is_bot", False) or not session_cookie or not _same_origin(request):
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)
    if len(request.body) > 16 * 1024:  # tek lead için fazlasıyla yeterli; büyük gövdeyle DB/log şişirilemesin
        return JsonResponse({"ok": False, "error": "payload too large"}, status=413)
    if (_rate_limited(f"lead-s:{session_cookie[:40]}", LEAD_LIMIT_PER_SESSION, 3600)
            or _rate_limited(f"lead-ip:{_ip_hash(request)}", LEAD_LIMIT_PER_IP, 3600)):
        return JsonResponse({"ok": False, "error": "too many requests"}, status=429)
    _get_or_create_session(request, {"url": str(request.META.get("HTTP_REFERER", ""))[:1000]})  # oturum yoksa formun sayfasıyla aç

    try:
        body = json.loads(request.body.decode("utf-8"))
        if not isinstance(body, dict):
            raise ValueError
    except Exception:
        return JsonResponse({"ok": False}, status=400)
    if body.get("website"):  # spam tuzağı (formdaki gizli alan) — gerçek kullanıcı doldurmaz
        return JsonResponse({"ok": False}, status=400)

    name    = str(body.get("name", ""))[:200].strip()
    phone   = str(body.get("phone", ""))[:30].strip()
    message = str(body.get("message", ""))[:3000].strip()
    page    = str(body.get("page", ""))[:500].strip()
    lang    = str(body.get("language", ""))[:10].strip()

    if not phone and not name:
        return JsonResponse({"ok": False, "error": "name or phone required"}, status=400)
    if phone and sum(c.isdigit() for c in phone) < 7:
        return JsonResponse({"ok": False, "error": "invalid phone"}, status=400)

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
    """WhatsApp sağlayıcısından gelen mesaj bildirimi → oturum eşleştirme (match_whatsapp).
    Paylaşılan gizli anahtar şart (WHATSAPP_WEBHOOK_SECRET, .env / Render env; X-Webhook-Secret ya da
    Authorization: Bearer başlığı). Anahtar tanımlı değilse uç kapalıdır (404); yanlışsa 403 — dışarıdan sahte
    WhatsApp lead'i / eşleşmesi üretilemez. IP başına hız limiti anahtar denemesini de keser."""
    secret = settings.WHATSAPP_WEBHOOK_SECRET
    if not secret:
        raise Http404
    if _rate_limited(f"wh-ip:{_ip_hash(request)}", WEBHOOK_LIMIT_PER_IP, 3600):
        return JsonResponse({"ok": False, "error": "too many requests"}, status=429)
    given = request.headers.get("X-Webhook-Secret", "") or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not hmac.compare_digest(given.encode(), secret.encode()):
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)
    try:
        body = json.loads(request.body.decode("utf-8"))
        if not isinstance(body, dict):
            raise ValueError
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    wa_phone   = str(body.get("phone", ""))[:30].strip()
    wa_message = str(body.get("message", ""))[:3000].strip()
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
    sessions    = VisitorSession.objects.filter(page_views__gt=0)  # gerçek ziyaretçi: JS beacon'ı göndermiş oturum
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
