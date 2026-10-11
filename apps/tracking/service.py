"""
apps/tracking/service.py

Her request'te çağrılır. Session'ı bulur veya oluşturur.
Traffic source'u otomatik tespit eder.
Cihaz bilgilerini parse eder.
"""
import hashlib
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import VisitorSession

logger = logging.getLogger(__name__)

# Lazy import — device-detector opsiyonel
try:
    from device_detector import DeviceDetector
    DEVICE_DETECTOR_AVAILABLE = True
except ImportError:
    DEVICE_DETECTOR_AVAILABLE = False


def _hash_ip(ip: str) -> str:
    """IP'yi SHA256 ile hash'le — GDPR uyumlu."""
    return hashlib.sha256(ip.encode()).hexdigest()[:32]


def _get_client_ip(request) -> str:
    """Proxy arkasında da gerçek IP'yi al."""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _detect_traffic_source(request) -> dict:
    """
    URL parametrelerine bakarak trafik kaynağını tespit et.
    Hiçbiri yoksa referrer'a bak.
    """
    from .models import TrafficSource

    params = request.GET

    # Google Ads — gclid var mı?
    gclid = params.get("gclid", "").strip()
    if gclid:
        return {
            "traffic_source": TrafficSource.GOOGLE_ADS,
            "gclid":          gclid,
            "google_campaign": params.get("utm_campaign", ""),
            "google_adgroup":  params.get("utm_content", ""),
            "google_keyword":  params.get("utm_term", ""),
            "google_matchtype": params.get("matchtype", ""),
            "google_network":   params.get("network", ""),
        }

    # Meta Ads — fbclid var mı?
    fbclid = params.get("fbclid", "").strip()
    if fbclid:
        return {
            "traffic_source": TrafficSource.META_ADS,
            "fbclid":         fbclid,
            "fb_campaign":    params.get("utm_campaign", ""),
            "fb_adset":       params.get("utm_content", ""),
            "fb_ad":          params.get("utm_term", ""),
            "fb_placement":   params.get("placement", ""),
        }

    # UTM parametreleri var mı?
    utm_source = params.get("utm_source", "").lower()
    utm_medium = params.get("utm_medium", "").lower()

    if utm_source:
        if "google" in utm_source and "cpc" in utm_medium:
            source = TrafficSource.GOOGLE_ADS
        elif utm_source in ["facebook", "instagram", "meta"] or "fb" in utm_source:
            source = TrafficSource.META_ADS
        elif utm_medium == "email":
            source = TrafficSource.EMAIL
        elif utm_source == "whatsapp":
            source = TrafficSource.WHATSAPP
        else:
            source = TrafficSource.REFERRAL
        return {"traffic_source": source, **{
            f"utm_{k}": params.get(f"utm_{k}", "")
            for k in ["source", "medium", "campaign", "content", "term"]
        }}

    # Referrer'a bak
    referrer = request.META.get("HTTP_REFERER", "").lower()
    if referrer:
        if "google" in referrer:
            return {"traffic_source": TrafficSource.GOOGLE_ORG, "referrer_url": referrer}
        if "bing" in referrer or "msn" in referrer:
            return {"traffic_source": TrafficSource.BING_ORG, "referrer_url": referrer}
        if any(s in referrer for s in ["facebook", "instagram", "twitter", "linkedin", "tiktok"]):
            return {"traffic_source": TrafficSource.SOCIAL, "referrer_url": referrer}
        return {"traffic_source": TrafficSource.REFERRAL, "referrer_url": referrer}

    return {"traffic_source": TrafficSource.DIRECT}


def _parse_device(user_agent: str) -> dict:
    """
    User-Agent'tan cihaz bilgilerini çıkar.
    device-detector varsa kullan, yoksa basit regex.
    """
    if not user_agent:
        return {}

    if DEVICE_DETECTOR_AVAILABLE:
        try:
            dd = DeviceDetector(user_agent).parse()
            return {
                "device_type":    dd.device_type() or "",
                "device_brand":   dd.device_brand() or "",
                "device_model":   dd.device_model() or "",
                "os_name":        dd.os_name() or "",
                "os_version":     dd.os_version() or "",
                "browser_name":   dd.client_name() or "",
                "browser_version": dd.client_version() or "",
            }
        except Exception:
            pass

    # Basit fallback
    ua_lower = user_agent.lower()
    device_type = "desktop"
    if "mobile" in ua_lower or "android" in ua_lower:
        device_type = "mobile"
    elif "tablet" in ua_lower or "ipad" in ua_lower:
        device_type = "tablet"

    os_name = ""
    if "iphone" in ua_lower or "ipad" in ua_lower:
        os_name = "iOS"
    elif "android" in ua_lower:
        os_name = "Android"
    elif "windows" in ua_lower:
        os_name = "Windows"
    elif "mac" in ua_lower:
        os_name = "macOS"
    elif "linux" in ua_lower:
        os_name = "Linux"

    browser_name = ""
    if "chrome" in ua_lower and "chromium" not in ua_lower:
        browser_name = "Chrome"
    elif "safari" in ua_lower and "chrome" not in ua_lower:
        browser_name = "Safari"
    elif "firefox" in ua_lower:
        browser_name = "Firefox"
    elif "edge" in ua_lower:
        browser_name = "Edge"

    return {
        "device_type":  device_type,
        "os_name":      os_name,
        "browser_name": browser_name,
    }


def get_or_create_session(request) -> "VisitorSession":
    """
    Ana giriş noktası. Her middleware çağrısında burası çalışır.

    1. Django session key al (yoksa oluştur)
    2. Cache'e bak (hızlı yol)
    3. DB'ye bak
    4. Yoksa oluştur — tüm bilgileri parse et
    """
    from .models import VisitorSession

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cache_key   = f"tracking_session:{session_key}"

    # Cache hit
    cached_id = cache.get(cache_key)
    if cached_id:
        try:
            session = VisitorSession.objects.get(id=cached_id)
            # Returning visitor — sayacı artır
            _maybe_increment_session(request, session)
            return session
        except VisitorSession.DoesNotExist:
            cache.delete(cache_key)

    # DB'de var mı?
    session = VisitorSession.objects.filter(session_key=session_key).first()

    if session:
        _maybe_increment_session(request, session)
    else:
        session = _create_session(request, session_key)

    cache.set(cache_key, session.id, 60 * 30)  # 30 dk cache
    return session


def _maybe_increment_session(request, session):
    """
    Eğer son görülmeden bu yana 30+ dk geçtiyse yeni session sayılır.
    Traffic source güncellenebilir (yeni kampanyadan geldiyse).
    """
    now = timezone.now()
    threshold = now - timedelta(minutes=30)

    if session.last_seen < threshold:
        # Yeni ziyaret
        session.session_count += 1
        # Yeni traffic source var mı?
        source_data = _detect_traffic_source(request)
        if source_data.get("gclid") or source_data.get("fbclid"):
            # Paid source gelmiş — güncelle
            for key, val in source_data.items():
                if val and hasattr(session, key):
                    setattr(session, key, val)
            session.traffic_source = source_data["traffic_source"]
        session.save(update_fields=["session_count", "last_seen", "traffic_source",
                                     "gclid", "fbclid", "utm_source", "utm_campaign"])


def _create_session(request, session_key: str) -> "VisitorSession":
    """Yeni session oluştur — tüm bilgileri doldur."""
    from .models import VisitorSession

    ip = _get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")

    source_data = _detect_traffic_source(request)
    device_data = _parse_device(ua)

    from .visitor import get_visitor_id

    vid = get_visitor_id(request)
    prev = VisitorSession.objects.filter(visitor_id=vid).order_by("-last_seen").first() if vid else None
    if prev is not None:
        # Reklam atfını kaybetme: bu ziyarette reklam parametresi yoksa öncekini devral (ilk dokunuş korunur)
        for f in ("gclid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
                  "google_campaign", "google_keyword", "fb_campaign"):
            if not source_data.get(f) and getattr(prev, f, None):
                source_data[f] = getattr(prev, f)
    session = VisitorSession.objects.create(
        session_key   = session_key,
        visitor_id    = vid,
        session_count = (prev.session_count + 1) if prev else 1,
        landing_page  = request.path,
        referrer_url  = request.META.get("HTTP_REFERER", ""),
        ip_hash       = _hash_ip(ip) if ip else "",
        user_agent    = ua[:500],
        language_code = request.LANGUAGE_CODE if hasattr(request, "LANGUAGE_CODE") else "",
        **source_data,
        **device_data,
    )

    # IP bazlı coğrafya (opsiyonel — harici servis gerekir)
    _enrich_geo_async(session.id, ip)

    logger.info(f"New session: {session_key[:12]} | {source_data.get('traffic_source')} | {device_data.get('device_type')}")
    return session


def _enrich_geo_async(session_id, ip: str):
    """
    IP'den ülke/şehir bilgisi çek.
    Sınırlı arka plan thread havuzunda çalışır — response'u bloklamaz (Redis/Celery yok).
    """
    if not ip or ip in ("127.0.0.1", "::1"):
        return
    try:
        from apps.localization.dispatch import run_in_background

        from .tasks import enrich_geo_task
        run_in_background(enrich_geo_task, str(session_id), ip)
    except Exception:  # noqa: BLE001
        pass


def record_event(session, event_type: str, data: dict, page_url: str = ""):
    """
    Event kaydet ve session aggregate'lerini güncelle.
    API view'dan çağrılır.
    """
    from .models import TrackingEvent

    TrackingEvent.objects.create(
        session    = session,
        event_type = event_type,
        data       = data,
        page_url   = page_url[:500],
    )

    _update_session_from_event(session, event_type, data)
    cache.delete(f"tracking_session:{session.session_key}")


def _update_session_from_event(session, event_type: str, data: dict):
    """Session'daki sayaçları güncelle."""
    from .models import TrackingEvent

    update_fields = ["last_seen"]

    if event_type == TrackingEvent.WHATSAPP_CLICK:
        session.whatsapp_clicks += 1
        session.whatsapp_clicked_at = timezone.now()
        update_fields.extend(["whatsapp_clicks", "whatsapp_clicked_at"])

    elif event_type == TrackingEvent.PHONE_CLICK:
        session.phone_clicks += 1
        update_fields.append("phone_clicks")

    elif event_type == TrackingEvent.MAPS_CLICK:
        session.map_clicks += 1
        update_fields.append("map_clicks")

    elif event_type == TrackingEvent.CTA_CLICK:
        session.cta_clicks += 1
        update_fields.append("cta_clicks")

    elif event_type == TrackingEvent.FORM_START:
        session.form_starts += 1
        update_fields.append("form_starts")

    elif event_type == TrackingEvent.FORM_SUBMIT:
        session.form_submits += 1
        if not session.is_lead:
            session.is_lead = True
            session.lead_at = timezone.now()
            update_fields.extend(["form_submits", "is_lead", "lead_at"])
        else:
            update_fields.append("form_submits")

    elif event_type == TrackingEvent.VIDEO_PLAY:
        session.video_plays += 1
        update_fields.append("video_plays")

    elif event_type == TrackingEvent.SCROLL_DEPTH:
        depth = data.get("depth", 0)
        if depth > session.avg_scroll_depth:
            session.avg_scroll_depth = depth
            update_fields.append("avg_scroll_depth")

    elif event_type == TrackingEvent.TIME_ON_PAGE:
        session.total_time_sec += data.get("seconds", 0)
        session.page_views += 1
        update_fields.extend(["total_time_sec", "page_views"])

    session.save(update_fields=update_fields)


def match_whatsapp(wa_phone: str, wa_message: str, received_at=None) -> dict:
    """
    Gelen WhatsApp mesajını session ile eşleştir.

    Algoritma:
    1. Son 30 dakikada WA butonuna basan sessionları bul
    2. Varsa → eşleştir, confidence = 1.0
    3. Yoksa → manuel eşleştirme gerekiyor, confidence = 0
    """
    from .models import VisitorSession, WhatsAppMatch, Lead

    if received_at is None:
        received_at = timezone.now()

    window_start = received_at - timedelta(minutes=30)

    # Son 30 dk'da WA butonuna basan sessionlar
    candidates = VisitorSession.objects.filter(
        whatsapp_clicked_at__gte=window_start,
        whatsapp_clicked_at__lte=received_at,
        whatsapp_matched=False,
    ).order_by("-whatsapp_clicked_at")  # En yakın zamanlı önce

    if not candidates.exists():
        # Eşleştirme yok — pending kayıt oluştur
        match = WhatsAppMatch.objects.create(
            wa_phone       = wa_phone,
            wa_message     = wa_message,
            wa_received_at = received_at,
            match_confidence = 0.0,
        )
        return {"matched": False, "match_id": str(match.id), "confidence": 0.0}

    best = candidates.first()
    time_diff = abs((received_at - best.whatsapp_clicked_at).total_seconds())

    # Confidence: 30 dakikada 0'dan 1'e lineer düşüş
    confidence = max(0.0, 1.0 - (time_diff / 1800))

    # Eşleştir
    match = WhatsAppMatch.objects.create(
        session            = best,
        wa_phone           = wa_phone,
        wa_message         = wa_message,
        wa_received_at     = received_at,
        button_clicked_at  = best.whatsapp_clicked_at,
        time_diff_seconds  = int(time_diff),
        match_confidence   = confidence,
    )

    best.whatsapp_matched     = True
    best.whatsapp_match_phone = wa_phone
    best.whatsapp_match_time  = received_at
    best.is_lead              = True
    best.lead_at              = received_at
    best.save(update_fields=["whatsapp_matched", "whatsapp_match_phone",
                              "whatsapp_match_time", "is_lead", "lead_at"])

    # Lead oluştur
    lead = Lead.objects.create(
        session        = best,
        source         = Lead.SOURCE_WHATSAPP,
        phone          = wa_phone,
        message        = wa_message,
        traffic_source = best.traffic_source,
        gclid          = best.gclid or "",
        fbclid         = best.fbclid or "",
        utm_campaign   = best.utm_campaign,
        utm_source     = best.utm_source,
        device_type    = best.device_type,
        ip_country     = best.ip_country,
        ip_city        = best.ip_city,
        whatsapp_matched           = True,
        whatsapp_match_confidence  = confidence,
    )
    match.lead = lead
    match.save(update_fields=["lead"])

    logger.info(f"WA matched: {wa_phone} → {best.session_key[:12]} (conf: {confidence:.0%}, diff: {int(time_diff)}s)")

    return {
        "matched":    True,
        "match_id":   str(match.id),
        "session_id": str(best.id),
        "lead_id":    lead.id,
        "confidence": confidence,
        "time_diff":  int(time_diff),
    }

def create_lead(request, *, name="", phone="", email="", message="", page="", language="",
                source="form", clinic=None, treatment=None):
    """Form / API'den gelen lead'i oluşturur, oturum + persona bağlamını kopyalar, bildirim gönderir."""
    from django.conf import settings
    from django.core.mail import send_mail

    from apps.clinics.models import Clinic

    from .models import Lead

    session = getattr(request, "tracking_session", None)
    persona = (getattr(request, "persona", None) or {}).get("persona", "")
    clinic = clinic or Clinic.primary()
    lead = Lead.objects.create(
        session=session, clinic=clinic, treatment=treatment, persona=persona if persona != "unknown" else "",
        source=source, name=name[:200], phone=phone[:30], email=email[:254], message=message,
        page=page[:500], language=language[:10],
        traffic_source=session.traffic_source if session else "",
        gclid=(session.gclid or "") if session else "",
        fbclid=(session.fbclid or "") if session else "",
        utm_campaign=session.utm_campaign if session else "",
        utm_source=session.utm_source if session else "",
        device_type=session.device_type if session else "",
        ip_country=session.ip_country if session else "",
        ip_city=session.ip_city if session else "",
    )
    if session:
        session.mark_lead()
    if request.session.session_key:
        try:
            from apps.persona.engine import record_event as persona_record

            persona_record(request.session.session_key, "form_submit", {"lead": lead.pk}, page)
        except Exception:  # noqa: BLE001
            logger.exception("persona conversion record failed")

    recipient = (clinic.email if clinic and clinic.email else None) or settings.LEAD_NOTIFY_EMAIL
    if recipient:
        body = (f"Yeni lead #{lead.pk}\nİsim: {name}\nTelefon: {phone}\nE-posta: {email}\n"
                f"Dil: {language}\nSayfa: {page}\nPersona: {persona}\n"
                f"Kaynak: {lead.traffic_source} {lead.utm_campaign}\n\nMesaj:\n{message}")
        try:
            send_mail(f"[Lead] {name or phone} — {language.upper()}", body, settings.DEFAULT_FROM_EMAIL,
                      [recipient], fail_silently=True)
        except Exception:  # noqa: BLE001
            logger.exception("lead mail failed")
    return lead
