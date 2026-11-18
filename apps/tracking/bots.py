"""
JS çalıştıran tarayıcı botları: PetalBot/Huawei Cloud, Google'ın render edicisi, barındırma/VPS ağlarından gelen
başsız (headless) Chrome'lar sayfa beacon'ını gönderir ama hiç dokunmaz (kaydırma, tıklama, parmak yok).
Üç işaret:
  1. navigator.webdriver (tarayıcı otomasyon altında) → oturum hiç açılmaz (pageview beacon'ında reddedilir)
  2. IP kuruluşu veri merkezi/bulut (ipinfo "org") → bot_reason="datacenter" (coğrafya zenginleştirmesinde)
  3. Hiç etkileşim yok → saat başı tarama bunu doğrular; tek bir insan hareketi (engaged / tıklama) bayrağı kaldırır
"Gerçek ziyaretçi" tanımı tek yerde: models.HUMAN_Q (beacon göndermiş + bot bayrağı yok).
"""
import logging
import re

logger = logging.getLogger(__name__)

# Veri merkezi / bulut / barındırma kuruluşları. Cloudflare ve Akamai BİLEREK yok: iCloud Private Relay kullanan
# gerçek Safari ziyaretçileri bu ağlardan çıkar.
DATACENTER_RE = re.compile(
    r"huawei|google llc|googl?e cloud|amazon|aws|microsoft|azure|alibaba|aliyun|tencent|baidu|oracle|hetzner|ovh|"
    r"digitalocean|linode|akamai connected cloud|vultr|choopa|contabo|leaseweb|m247|datacamp|zenlayer|scaleway|"
    r"hostinger|bacloud|hostroyale|ionos|godaddy|hostwinds|psychz|servermania|colocrossing|quadranet|fdcservers|"
    r"\bvps\b|hosting|host(ed|ing) services|data ?cent(er|re)|server(s|farm)?\b|cloud(?!flare)",
    re.I)
NOT_DATACENTER_RE = re.compile(r"cloudflare|akamai technologies|apple|icloud", re.I)

# İnsan kanıtı: bunlardan biri geldiyse veri merkezi bayrağı kalkar (VPN/kurumsal proxy arkasındaki gerçek kişi)
ENGAGEMENT_EVENTS = frozenset({
    "engaged", "whatsapp_click", "phone_click", "maps_click", "email_click", "cta_click", "form_start", "form_submit",
    "faq_open", "faq_read", "phone_copy", "nav_click", "ui_click", "gallery_view", "before_after_interact",
    "video_play", "booking_step", "language_switch", "instagram_click", "youtube_click", "chatbot_open", "chatbot_message",
})


def is_datacenter(org: str) -> bool:
    org = org or ""
    if not org or NOT_DATACENTER_RE.search(org):
        return False
    return bool(DATACENTER_RE.search(org))


def flag_session_if_datacenter(session_id, org: str) -> bool:
    """Coğrafya zenginleştirmesinden hemen sonra: kuruluş veri merkeziyse ve oturum hiç dokunmadıysa bayrakla."""
    from .models import VisitorSession

    if not is_datacenter(org):
        return False
    n = VisitorSession.objects.filter(id=session_id, bot_reason="", engaged_at__isnull=True,
                                      whatsapp_clicks=0, phone_clicks=0, form_submits=0).update(bot_reason="datacenter")
    return bool(n)


def flag_datacenter_sessions(days: int = 3) -> dict:
    """Saat başı: son N günde veri merkezinden gelmiş, hiç dokunmamış oturumları bot olarak işaretle (idempotent)."""
    from datetime import timedelta

    from django.utils import timezone

    from .models import TrackingEvent, VisitorSession

    since = timezone.now() - timedelta(days=days)
    cand = (VisitorSession.objects.filter(created_at__gte=since, bot_reason="", engaged_at__isnull=True,
                                          whatsapp_clicks=0, phone_clicks=0, form_submits=0)
            .exclude(ip_org="").only("id", "ip_org"))
    ids = [s.id for s in cand if is_datacenter(s.ip_org)]
    if not ids:
        return {"checked": cand.count(), "flagged": 0}
    touched = set(TrackingEvent.objects.filter(session_id__in=ids, event_type__in=ENGAGEMENT_EVENTS)
                  .values_list("session_id", flat=True).distinct())
    ids = [i for i in ids if i not in touched]
    n = VisitorSession.objects.filter(id__in=ids).update(bot_reason="datacenter")
    logger.info("datacenter sessions flagged: %s (engaged kept: %s)", n, len(touched))
    return {"checked": len(ids) + len(touched), "flagged": n, "kept_engaged": len(touched)}


def unflag_on_engagement(session, event_type: str):
    """İnsan hareketi geldi: 'datacenter' bayrağı kalkar, engaged_at dolar. Döner: güncellenen alan adları."""
    from django.utils import timezone

    if event_type not in ENGAGEMENT_EVENTS:
        return []
    fields = []
    if not session.engaged_at:
        session.engaged_at = timezone.now()
        fields.append("engaged_at")
    if session.bot_reason == "datacenter":
        session.bot_reason = ""
        fields.append("bot_reason")
    return fields
