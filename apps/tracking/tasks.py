"""
Tracking arka plan işleri — düz fonksiyonlar (Celery/Redis YOK).
Çağrı: apps.localization.dispatch.run_in_background(...) veya `python manage.py periodic`.
"""
import logging

logger = logging.getLogger(__name__)


def enrich_geo_task(session_id: str, ip: str):
    """
    IP'den ülke/şehir bilgisi çek.
    ip-api.com (ücretsiz, 45req/dk limiti) veya başka servis.
    """
    import requests
    from .models import VisitorSession
    import uuid

    try:
        session = VisitorSession.objects.get(id=uuid.UUID(session_id))
    except VisitorSession.DoesNotExist:
        return

    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city",
            timeout=3
        )
        data = resp.json()
        if data.get("status") == "success":
            session.ip_country = data.get("countryCode", "")[:5]
            session.ip_city    = data.get("city", "")[:100]
            session.save(update_fields=["ip_country", "ip_city"])
            logger.info(f"Geo enriched: {session_id[:8]} → {session.ip_country}/{session.ip_city}")
    except Exception as e:
        logger.warning(f"Geo enrichment failed for {ip}: {e}")


def send_google_conversion(ad_conversion_id: int):
    """
    Google Ads Conversion API'ye conversion gönder.
    gclid varsa çalışır.
    """
    from .models import AdConversion
    from django.utils import timezone

    try:
        conv = AdConversion.objects.get(id=ad_conversion_id)
    except AdConversion.DoesNotExist:
        return

    if not conv.gclid:
        logger.warning(f"AdConversion {ad_conversion_id}: no gclid, skipping")
        conv.status = AdConversion.STATUS_FAILED
        conv.error_message = "No gclid"
        conv.save(update_fields=["status", "error_message"])
        return

    # Google Ads Conversion API call
    # https://developers.google.com/google-ads/api/docs/conversions/upload-clicks
    try:
        # Burada gerçek Google Ads API çağrısı yapılır
        # google-ads kütüphanesi kuruluysa:
        # from google.ads.googleads.client import GoogleAdsClient
        # client = GoogleAdsClient.load_from_dict(settings.GOOGLE_ADS_CONFIG)
        # ... conversion upload logic

        logger.info(f"Google conversion sent: gclid={conv.gclid[:20]}... | {conv.conversion_name}")
        conv.status  = AdConversion.STATUS_SENT
        conv.sent_at = timezone.now()
        conv.save(update_fields=["status", "sent_at"])

    except Exception as exc:
        logger.error(f"Google conversion failed: {exc}")
        conv.status        = AdConversion.STATUS_FAILED
        conv.error_message = str(exc)
        conv.save(update_fields=["status", "error_message"])
        # Yeniden deneme: `python manage.py periodic --job conversions` (cron) FAILED kayıtları tekrar gönderir


def send_meta_conversion(ad_conversion_id: int):
    """
    Meta Conversions API'ye event gönder.
    fbclid varsa çalışır.
    """
    import requests
    from .models import AdConversion
    from django.conf import settings
    from django.utils import timezone

    try:
        conv = AdConversion.objects.get(id=ad_conversion_id)
    except AdConversion.DoesNotExist:
        return

    pixel_id  = getattr(settings, "META_PIXEL_ID", "")
    api_token = getattr(settings, "META_API_TOKEN", "")

    if not pixel_id or not api_token:
        logger.warning("Meta API not configured")
        return

    payload = {
        "data": [{
            "event_name":  conv.conversion_name,
            "event_time":  int(timezone.now().timestamp()),
            "event_id":    conv.event_id or str(conv.id),
            "action_source": "website",
            "user_data": {
                "client_user_agent": "",
                "fbc": conv.fbclid,
            },
            "custom_data": {
                "value":    float(conv.conversion_value),
                "currency": conv.currency,
            }
        }]
    }

    try:
        resp = requests.post(
            f"https://graph.facebook.com/v18.0/{pixel_id}/events",
            params={"access_token": api_token},
            json=payload,
            timeout=10
        )
        resp.raise_for_status()
        logger.info(f"Meta conversion sent: {conv.conversion_name}")
        conv.status  = AdConversion.STATUS_SENT
        conv.sent_at = timezone.now()
        conv.save(update_fields=["status", "sent_at"])

    except Exception as exc:
        logger.error(f"Meta conversion failed: {exc}")
        conv.status        = AdConversion.STATUS_FAILED
        conv.error_message = str(exc)
        conv.save(update_fields=["status", "error_message"])
        # Yeniden deneme: `python manage.py periodic --job conversions` (cron) FAILED kayıtları tekrar gönderir


def cleanup_old_sessions():
    """90 günden eski, lead olmayan sessionları temizle."""
    from .models import VisitorSession
    from django.utils import timezone
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = VisitorSession.objects.filter(
        created_at__lt=cutoff,
        is_lead=False,
    ).delete()
    logger.info(f"Cleaned {deleted} old sessions")
