"""
Persona kanıtını kayıtlı ham veriden yeniden kurar: takip tarafındaki PageView + TrackingEvent satırları zaman
sırasıyla motordan geçirilir (sayfa sinyali, okuma süresi, SSS, iletişim tıklamaları, dönüşler…), sayaçlar sıfırdan
sayılır, teşhis yenilenir. Kullanım: eşzamanlı beacon'ların birbirinin üstüne yazdığı eski oturumları onarmak
(`manage.py rebuild_personas`) ve saat başı 'eksik kanıt' taraması (periodic --job tracking).
"""
import logging
from datetime import timedelta
from urllib.parse import urlparse

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

COUNTER_FIELDS = ("price_section_clicks", "price_section_time", "before_after_views", "before_after_time", "gallery_views",
                  "doctor_profile_views", "certification_clicks", "safety_section_time", "review_section_time",
                  "testimonial_reads", "video_plays", "video_watch_time", "faq_interactions", "blog_reads",
                  "urgency_keyword_hits", "cta_clicks", "whatsapp_clicks", "phone_clicks", "form_starts", "form_submits",
                  "total_page_views", "total_time_spent_sec", "bounce_count")
CONTACT_EVENTS = ("whatsapp_click", "phone_click", "form_submit", "form_start", "maps_click", "email_click",
                  "contact_return", "phone_copy", "booking_step")


def needs_repair(psession, tsession) -> bool:
    """Takipte iletişim olayı var ama persona kanıt günlüğünde karşılığı yok → eşzamanlı yazma kaybı."""
    n_contact = tsession.events.filter(event_type__in=CONTACT_EVENTS).count()
    if not n_contact:
        return False
    n_evidence = sum(1 for e in (psession.evidence or []) if e.get("k") == "click")
    return n_evidence < n_contact


def rebuild_session(psession, tsession) -> dict:
    """Tek oturumu ham veriden yeniden kur. Döner: {'pages','events','persona','confidence'}."""
    from .engine import (EVENT_ALIASES, VISIT_GAP, _count_evidence, _page_type, _rediagnose, _update_aggregates,
                         decay_evidence)
    from .models import BehaviorEvent
    from .pages import apply_page

    valid = {c for c, _ in BehaviorEvent.EVENT_TYPES}
    timeline = [(pv.timestamp, 0, pv) for pv in tsession.pageviews.all().order_by("timestamp")]
    timeline += [(ev.timestamp, 1, ev) for ev in tsession.events.all().order_by("timestamp")]
    timeline.sort(key=lambda x: (x[0], x[1]))
    if not timeline:
        return {}
    for f in COUNTER_FIELDS:
        setattr(psession, f, 0)
    psession.avg_scroll_depth = psession.max_scroll_depth = 0.0
    psession.page_scores, psession.pages_seen, psession.evidence = {}, [], []
    psession.visit_started_at = timeline[0][0]
    last, visits, n_pages, n_events = None, 1, 0, 0
    for t, kind, obj in timeline:
        if last is not None and t - last > VISIT_GAP:
            decay_evidence(psession)
            visits += 1
            psession.visit_started_at = t
        last = t
        if kind == 0:
            n_pages += 1
            apply_page(psession, urlparse(obj.url).path or "/", obj.page_type or "")
            continue
        et = EVENT_ALIASES.get(obj.event_type, obj.event_type)
        if et not in valid:
            continue
        n_events += 1
        data = obj.data if isinstance(obj.data, dict) else {}
        ptype = _page_type(psession, obj.page_url)
        _update_aggregates(psession, et, data, ptype, save=False)
        _count_evidence(psession, et, data, obj.page_url, ptype, now=t, save=False)
    psession.total_sessions = max(psession.total_sessions or 1, visits)
    _rediagnose(psession, force=True)
    psession.save()
    cache.delete(f"persona:{psession.session_key}")
    return {"pages": n_pages, "events": n_events, "persona": psession.assigned_persona,
            "confidence": psession.persona_confidence}


def rebuild_many(days=30, site="", only_missing=False, limit=None, log=None) -> dict:
    """İnsan oturumlarını (HUMAN_Q) tarar; persona satırı olmayanları atlar."""
    from apps.tracking.models import HUMAN_Q, VisitorSession as TSession

    from .models import VisitorSession as PSession

    since = timezone.now() - timedelta(days=days)
    qs = TSession.objects.filter(HUMAN_Q, created_at__gte=since).order_by("created_at")
    if site:
        qs = qs.filter(site=site)
    if limit:
        qs = qs[:limit]
    stats = {"scanned": 0, "rebuilt": 0, "skipped_no_persona": 0, "skipped_ok": 0, "changed": 0}
    for ts in qs.iterator(chunk_size=200):
        stats["scanned"] += 1
        with transaction.atomic():
            ps = PSession.objects.select_for_update().filter(session_key=ts.session_key).first()
            if ps is None:
                stats["skipped_no_persona"] += 1
                continue
            if only_missing and not needs_repair(ps, ts):
                stats["skipped_ok"] += 1
                continue
            before = ps.assigned_persona
            r = rebuild_session(ps, ts)
        if not r:
            continue
        stats["rebuilt"] += 1
        if r["persona"] != before:
            stats["changed"] += 1
        if log:
            log(f"{ts.site} {ts.session_key[:20]:20s} {r['pages']}p/{r['events']}e  {before} → {r['persona']} ({r['confidence']:.2f})")
    return stats
