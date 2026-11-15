"""
Kardeş sitelerin (drdevrim.com — Nuxt, devrimbirikensipahi.com.tr — Django) çerezsiz beacon uçları:

    POST /api/t/pageview/   {site, vid, sid, url, title, referrer, tz, sw, sh, attr, prev_vid?}
    POST /api/t/event/      {site, vid, sid, events:[{event_type, data, page_url}], attr}

Kimlik ve oturum GÖVDEDEN gelir (çapraz site çerezi yok): vid = localStorage'daki kalıcı ziyaretçi kimliği,
sid = istemcinin ürettiği 30 dk'lık oturum kimliği → session_key "<site>:<sid>". Gövde text/plain olarak gönderilir
(CORS ön-uçuşu yok); yanıt yalnızca izinli kökenlere (settings.TRACKING_SITES[...]["origins"]) açılır.
Aynı ziyaretçi siteler arası linkle geçtiğinde (?dtv=…) prev_vid ile eski kimlik yeniye birleştirilir.
"""
import json
import logging
import re
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .views import MIND_EVENTS, VALID_EVENTS, _rate_limited, _ip_hash

logger = logging.getLogger(__name__)
ID_RE = re.compile(r"^[a-f0-9]{16,40}$")
EVENTS_LIMIT_PER_IP = 1200  # saatte — bir sekme dakikada en çok birkaç beacon atar


def _origin_allowed(request):
    origin = request.headers.get("Origin", "")
    if not origin:
        return True, ""  # sendBeacon/no-cors bazı tarayıcılarda Origin göndermez; site kodu + hız limiti korur
    host = (urlparse(origin).hostname or "").lower()
    for site in settings.TRACKING_SITES.values():
        for o in site["origins"]:
            if (urlparse(o).hostname or "").lower() == host:
                return True, origin
    for o in settings.TRACKING_DEV_ORIGINS:
        if origin.rstrip("/") == o.rstrip("/"):
            return True, origin
    return False, origin


def _cors(resp, origin):
    if origin:
        resp["Access-Control-Allow-Origin"] = origin
        resp["Vary"] = "Origin"
    resp["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    resp["Access-Control-Allow-Headers"] = "Content-Type"
    resp["Access-Control-Max-Age"] = "86400"
    return resp


def _body(request):
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:  # noqa: BLE001
        return None
    return data if isinstance(data, dict) else None


def _prepare(request):
    """Köken, site, kimlikler ve hız limiti kontrolü → (preq, body) ya da hata yanıtı."""
    ok, origin = _origin_allowed(request)
    if request.method == "OPTIONS":
        return None, None, _cors(HttpResponse(status=204 if ok else 403), origin)
    if not ok:
        return None, None, JsonResponse({"ok": False, "error": "origin"}, status=403)
    if getattr(request, "is_bot", False):
        return None, None, _cors(JsonResponse({"ok": True, "bot": True}), origin)
    body = _body(request)
    if body is None:
        return None, None, _cors(JsonResponse({"ok": False}, status=400), origin)
    site = str(body.get("site", ""))[:12]
    sid, vid = str(body.get("sid", "")), str(body.get("vid", ""))
    if site not in settings.TRACKING_SITES or site == "dt" or not ID_RE.match(sid) or (vid and not ID_RE.match(vid)):
        return None, None, _cors(JsonResponse({"ok": False, "error": "site/sid"}, status=400), origin)
    if _rate_limited(f"ext-ip:{_ip_hash(request)}", EVENTS_LIMIT_PER_IP, 3600):
        return None, None, _cors(JsonResponse({"ok": False, "error": "too many requests"}, status=429), origin)
    from .service import ExternalPageRequest

    url = str(body.get("url") or "")
    if not url and isinstance(body.get("events"), list) and body["events"]:
        first = body["events"][0] if isinstance(body["events"][0], dict) else {}
        url = str(first.get("page_url", ""))
    preq = ExternalPageRequest(request, site, sid, vid, url[:1000], str(body.get("referrer", ""))[:1000])
    preq._origin = origin
    return preq, body, None


def _attribution(session, body):
    attr = body.get("attr") if isinstance(body.get("attr"), dict) else {}
    if session and attr:
        fields = ("gclid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
        upd = {f: str(attr[f])[:255] for f in fields if attr.get(f) and not getattr(session, f, None)}
        if upd:
            type(session).objects.filter(pk=session.pk).update(**upd)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def ext_pageview(request):
    preq, body, err = _prepare(request)
    if err is not None:
        return err
    from .models import PageView
    from .pagetypes import page_type_for
    from .service import get_or_create_external_session, merge_visitor

    try:
        prev = str(body.get("prev_vid", ""))
        if prev and ID_RE.match(prev) and preq._dt_vid:
            merge_visitor(prev, preq._dt_vid)  # ?dtv= ile gelen ziyaretçi: eski kimliğin geçmişi yeniye bağlanır
        session = get_or_create_external_session(preq)
        PageView.objects.create(
            session=session, url=str(body.get("url", ""))[:500], title=str(body.get("title", ""))[:300],
            referrer=str(body.get("referrer", ""))[:500],
            page_type=page_type_for(preq.site, preq.path, str(body.get("page_type", ""))[:40]),
        )
        session.page_views += 1
        fields = ["page_views", "last_seen"]
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
        _attribution(session, body)
        try:
            from apps.persona.engine import get_or_create_persona, observe_page

            get_or_create_persona(preq, create=True)
            observe_page(preq.session.session_key, preq.path)
        except Exception as e:  # noqa: BLE001
            logger.error(f"ext persona: {e}")
    except Exception as e:  # noqa: BLE001
        logger.error(f"ext_pageview: {e}")
        return _cors(JsonResponse({"ok": False}, status=500), preq._origin)
    return _cors(JsonResponse({"ok": True}), preq._origin)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def ext_event(request):
    preq, body, err = _prepare(request)
    if err is not None:
        return err
    from apps.persona.engine import get_or_create_persona
    from apps.persona.engine import record_event as persona_record
    from apps.persona.models import VisitorSession as PersonaSession

    from .service import current_mindset, get_or_create_external_session, record_event

    try:
        session = get_or_create_external_session(preq)
        events = body.get("events") if isinstance(body.get("events"), list) else [body]
        events = [e for e in events[:50] if isinstance(e, dict)]
        skey = preq.session.session_key
        psession = PersonaSession.objects.filter(session_key=skey).first()
        if psession is None:
            try:
                get_or_create_persona(preq, create=True)
                psession = PersonaSession.objects.filter(session_key=skey).first()
            except Exception as e:  # noqa: BLE001
                logger.error(f"ext persona create: {e}")
        wants_mind = False
        for ev in events:
            event_type = str(ev.get("event_type", ""))[:30]
            data = ev.get("data") if isinstance(ev.get("data"), dict) else {}
            page_url = str(ev.get("page_url", ""))[:500]
            if event_type in VALID_EVENTS:
                try:
                    record_event(session, event_type, data, page_url)
                except Exception as e:  # noqa: BLE001
                    logger.error(f"ext_event: {e}")
            try:
                persona_record(skey, event_type, data, page_url, str(ev.get("page_type", "")), session=psession)
            except Exception as e:  # noqa: BLE001
                logger.error(f"ext persona event: {e}")
            if event_type in MIND_EVENTS or data.get("position") == "price-note":
                wants_mind = True
        _attribution(session, body)
        payload = {"ok": True}
        if wants_mind:
            m = current_mindset(skey)
            if m:
                payload["mind"] = m.get("top", "")
    except Exception as e:  # noqa: BLE001
        logger.error(f"ext_event: {e}")
        return _cors(JsonResponse({"ok": False}, status=500), preq._origin)
    return _cors(JsonResponse(payload), preq._origin)
