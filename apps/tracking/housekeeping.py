"""
Cron'a bağımlı olmayan bakım (Render blueprint cron'u güncellenmemiş/çalışmamış olsa bile veri temiz kalsın):
ilk beacon'da ve sonra işçi başına 30 dakikada bir, arka plan thread havuzunda
  1. veri merkezinden gelmiş, hiç dokunmamış oturumlar bot olarak işaretlenir (bots.flag_datacenter_sessions)
  2. iletişim tıklaması persona kanıtına girmemiş oturumlar ham veriden onarılır (persona.rebuild, only_missing)
İşçi açılışındaki ilk turda 30 gün, sonrakilerde 2 gün taranır. İdempotent; satır kilitleri eşzamanlı işçileri sıraya sokar.
Kapatmak: TRACKING_HOUSEKEEPING=False (testlerde kapalı).
"""
import logging

from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)

THROTTLE_SEC = 30 * 60
BOOT_DAYS, REGULAR_DAYS = 30, 2


def maybe_run():
    """Pageview beacon'ından çağrılır; isteği bloklamaz. Döner: bu çağrıda iş planlandı mı."""
    if not getattr(settings, "TRACKING_HOUSEKEEPING", True):
        return False
    local = caches["local"]
    if local.get("housekeeping:last"):
        return False
    local.set("housekeeping:last", 1, THROTTLE_SEC)
    first = not local.get("housekeeping:boot")
    local.set("housekeeping:boot", 1, 30 * 86400)
    try:
        from apps.localization.dispatch import run_in_background

        run_in_background(run, BOOT_DAYS if first else REGULAR_DAYS)
    except Exception:  # noqa: BLE001
        logger.exception("housekeeping schedule failed")
        return False
    return True


def run(days=REGULAR_DAYS):
    from apps.persona.rebuild import rebuild_many

    from .bots import flag_datacenter_sessions

    flagged = repaired = None
    try:
        flagged = flag_datacenter_sessions(days=3)
    except Exception:  # noqa: BLE001
        logger.exception("housekeeping: datacenter flagging failed")
    try:
        repaired = rebuild_many(days=days, only_missing=True)
    except Exception:  # noqa: BLE001
        logger.exception("housekeeping: persona repair failed")
    logger.info("housekeeping (%s gün): flagged=%s repaired=%s", days, flagged, repaired)
    return {"flagged": flagged, "repaired": repaired}
