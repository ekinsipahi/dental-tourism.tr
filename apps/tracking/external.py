"""
Kardeş sitelerin (drdevrim.com — Nuxt, devrimbirikensipahi.com.tr — Django) çerezsiz beacon uçları:

    POST /api/t/pageview/   {site, vid, sid, url, title, referrer, tz, sw, sh, attr, prev_vid?}
    POST /api/t/event/      {site, vid, sid, events:[{event_type, data, page_url}], attr}
    POST /api/t/lead/       {site, vid, sid, name, phone, email?, message?, page, language?, source, gclid?, attr?}
                            → {ok, lead_id}. Sunucudan sunucuya: X-DT-Key: <settings.DT_LEAD_KEY> başlığı köken
                            kontrolünü ve hız limitini atlar (+ external_id, created_at isteğe bağlı).

Kimlik ve oturum GÖVDEDEN gelir (çapraz site çerezi yok): vid = localStorage'daki kalıcı ziyaretçi kimliği,
sid = istemcinin ürettiği 30 dk'lık oturum kimliği → session_key "<site>:<sid>". Gövde text/plain olarak gönderilir
(CORS ön-uçuşu yok); yanıt yalnızca izinli kökenlere (settings.TRACKING_SITES[...]["origins"]) açılır.
Aynı ziyaretçi siteler arası linkle geçtiğinde (?dtv=…) prev_vid ile eski kimlik yeniye birleştirilir.
"""
import hmac
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


def _decision(preq):
    """Kardeş siteye dönen kişiselleştirme kararı: persona + aklındaki (mind) + o dildeki nazik mesaj.
    Zayıf sinyalde mesaj yok (dentaltourism'deki mind_nudge ile aynı mantık; metinler aynı katalogdan)."""
    from django.utils import translation

    from .service import current_mindset

    try:
        mind = current_mindset(preq.session.session_key) or {}
    except Exception:  # noqa: BLE001
        return {}
    top, level = mind.get("top", "unknown"), mind.get("level", "weak")
    out = {"persona": top, "level": level, "confidence": mind.get("confidence", 0.0), "message": None}
    if top != "unknown" and level != "weak":
        try:
            from apps.core.templatetags.site_tags import mind_messages

            with translation.override(preq.LANGUAGE_CODE):
                for m in mind_messages():
                    if m["key"] == top:
                        out["message"] = {"key": top, "title": str(m["title"]), "text": str(m["text"]), "button": str(m["button"])}
        except Exception:  # noqa: BLE001
            pass
    return out


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
            observe_page(preq.session.session_key, preq.path, page_type=str(body.get("page_type", ""))[:40])
        except Exception as e:  # noqa: BLE001
            logger.error(f"ext persona: {e}")
    except Exception as e:  # noqa: BLE001
        logger.error(f"ext_pageview: {e}")
        return _cors(JsonResponse({"ok": False}, status=500), preq._origin)
    return _cors(JsonResponse({"ok": True, "decision": _decision(preq)}), preq._origin)


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
            payload["decision"] = _decision(preq)
    except Exception as e:  # noqa: BLE001
        logger.error(f"ext_event: {e}")
        return _cors(JsonResponse({"ok": False}, status=500), preq._origin)
    return _cors(JsonResponse(payload), preq._origin)


LEAD_LIMIT_PER_SID = 3     # saatte, oturum (site:sid) başına
LEAD_LIMIT_PER_IP = 10     # saatte, IP başına
LEAD_BODY_MAX = 16 * 1024


def _lead_key_ok(request):
    """Sunucudan sunucuya aktarım: X-DT-Key başlığı DT_LEAD_KEY ile eşleşiyor mu? (None = başlık yok)"""
    given = request.headers.get("X-DT-Key", "")
    if not given:
        return None
    key = settings.DT_LEAD_KEY or ""
    return bool(key) and hmac.compare_digest(given.encode(), key.encode())


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def ext_lead(request):
    """Kardeş sitelerin merkezi lead ucu: formdan (dt-track.js → dtTrack.lead) ya da kardeş sitenin arka ucundan
    (X-DT-Key) gelen lead, Lead(site=…) olarak kaydedilir ve varsa "<site>:<sid>" oturumuna bağlanır."""
    s2s = _lead_key_ok(request)
    if s2s is False:
        return JsonResponse({"ok": False, "error": "key"}, status=403)
    ok, origin = _origin_allowed(request)
    if request.method == "OPTIONS":
        return _cors(HttpResponse(status=204 if ok else 403), origin)
    if not s2s:
        if not ok:
            return JsonResponse({"ok": False, "error": "origin"}, status=403)
        if getattr(request, "is_bot", False):
            return JsonResponse({"ok": False, "error": "forbidden"}, status=403)
    if len(request.body) > LEAD_BODY_MAX:
        return _cors(JsonResponse({"ok": False, "error": "payload too large"}, status=413), origin)
    body = _body(request)
    if body is None:
        return _cors(JsonResponse({"ok": False}, status=400), origin)
    if body.get("website"):  # spam tuzağı — gerçek kullanıcı doldurmaz
        return _cors(JsonResponse({"ok": False}, status=400), origin)

    site = str(body.get("site", ""))[:12]
    sid, vid = str(body.get("sid", ""))[:40], str(body.get("vid", ""))[:40]
    if site not in settings.TRACKING_SITES or (site == "dt" and not s2s):
        return _cors(JsonResponse({"ok": False, "error": "site"}, status=400), origin)
    if (sid and not ID_RE.match(sid)) or (vid and not ID_RE.match(vid)) or (not sid and not s2s):
        return _cors(JsonResponse({"ok": False, "error": "sid"}, status=400), origin)

    name = str(body.get("name", ""))[:200].strip()
    phone = str(body.get("phone", ""))[:30].strip()
    email = str(body.get("email", ""))[:254].strip()
    message = str(body.get("message", ""))[:3000].strip()
    page = str(body.get("page", ""))[:500].strip()
    language = str(body.get("language", ""))[:10].strip()
    source = str(body.get("source", "form"))[:20]
    external_id = str(body.get("external_id", ""))[:60].strip() if s2s else ""
    from .models import Lead

    if source not in Lead.EXTERNAL_SOURCES:
        source = Lead.SOURCE_FORM
    if not phone and not name:
        return _cors(JsonResponse({"ok": False, "error": "name or phone required"}, status=400), origin)
    if phone and sum(c.isdigit() for c in phone) < 7:
        return _cors(JsonResponse({"ok": False, "error": "invalid phone"}, status=400), origin)
    if not s2s and (_rate_limited(f"ext-lead-s:{site}:{sid}", LEAD_LIMIT_PER_SID, 3600)
                    or _rate_limited(f"ext-lead-ip:{_ip_hash(request)}", LEAD_LIMIT_PER_IP, 3600)):
        return _cors(JsonResponse({"ok": False, "error": "too many requests"}, status=429), origin)
    if external_id:
        dup = Lead.objects.filter(site=site, external_id=external_id).only("pk").first()
        if dup is not None:  # aynı kaydın tekrar aktarımı: ikinci lead açılmaz
            return _cors(JsonResponse({"ok": True, "lead_id": dup.pk, "duplicate": True}), origin)

    from .service import ExternalPageRequest, create_lead, get_or_create_external_session

    try:
        preq = ExternalPageRequest(request, site, sid, vid, page, str(body.get("referrer", ""))[:1000])
        if not language:  # dil verilmediyse sayfa yolundan (/de/…)
            from dental_tourism.languages import LANGUAGE_META

            first = preq.path.strip("/").split("/")[0]
            language = first if first in LANGUAGE_META else ""
        if sid:
            session = get_or_create_external_session(preq)
            _attribution(session, body)
            gclid = str(body.get("gclid", ""))[:255]
            if gclid and not session.gclid:
                type(session).objects.filter(pk=session.pk).update(gclid=gclid, traffic_source="google_ads")
                session.gclid, session.traffic_source = gclid, "google_ads"
        else:
            preq.tracking_session = None  # arka uçtan oturumsuz aktarım: lead bağımsız kaydedilir
            preq.session.session_key = ""
        lead = create_lead(preq, name=name, phone=phone, email=email, message=message, page=page,
                           language=language, source=source)
        upd = {"site": site}
        if external_id:
            upd["external_id"] = external_id
        if s2s and body.get("created_at"):
            from django.utils.dateparse import parse_datetime

            created = parse_datetime(str(body["created_at"])[:40])
            if created is not None:
                from django.utils import timezone as tz

                upd["created_at"] = created if tz.is_aware(created) else tz.make_aware(created)
        Lead.objects.filter(pk=lead.pk).update(**upd)
    except Exception as e:  # noqa: BLE001
        logger.error(f"ext_lead: {e}")
        return _cors(JsonResponse({"ok": False, "error": "server error"}, status=500), origin)
    return _cors(JsonResponse({"ok": True, "lead_id": lead.pk}), origin)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def ext_persona(request):
    """SPA route geçişi / yeniden kontrol: {site, vid, sid, url} → mevcut karar (DB'ye yazmaz)."""
    preq, body, err = _prepare(request)
    if err is not None:
        return err
    return _cors(JsonResponse({"ok": True, "decision": _decision(preq)}), preq._origin)
