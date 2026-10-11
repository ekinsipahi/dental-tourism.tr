"""
Site içi gezinme → persona kanıtı.

Ziyaretçi nerede vakit geçiriyorsa persona'sı o yöne kayar:
  fiyat sayfaları / paketler                      → price
  lüks tedaviler (porselen lamina, zirkonyum, All-on-4, Hollywood smile),
  "en iyi klinik" rehberleri, hekim profili        → premium
  önce-sonra galerisi, estetik tedaviler          → shame (estetik)
  garanti / takip / cerrahi rehberleri            → fear
  yorumlar, karşılaştırma, "should I" rehberleri  → skeptic
  hakkımızda, klinik profili, kanal/dolgu         → trust
  iletişim, İstanbul rehberi, lokasyonlar         → ready
Her sayfa türü oturum başına en fazla REPEAT_CAP kez sayılır (aynı sayfayı yenilemek skoru şişirmez).
Tüm dillerdeki slug'lar çözülür (/de/behandlungen/keramik-veneers/ → porcelain-veneers).
"""
from django.core.cache import cache
from django.urls import Resolver404, resolve

from .models import (PERSONA_FEAR, PERSONA_PREMIUM, PERSONA_PRICE, PERSONA_READY, PERSONA_SHAME,
                     PERSONA_SKEPTIC, PERSONA_TRUST)

REPEAT_CAP = 2
PERSONA_CAP = 6.0

TREATMENT_SIGNALS = {
    "porcelain-veneers": {PERSONA_PREMIUM: 0.9, PERSONA_SHAME: 0.6},
    "zirconia-crowns": {PERSONA_PREMIUM: 0.8},
    "all-on-4-implants": {PERSONA_PREMIUM: 0.9, PERSONA_FEAR: 0.3},
    "hollywood-smile": {PERSONA_SHAME: 1.0, PERSONA_PREMIUM: 0.7},
    "dental-implants": {PERSONA_PREMIUM: 0.5, PERSONA_FEAR: 0.4},
    "composite-veneers": {PERSONA_SHAME: 0.7, PERSONA_PRICE: 0.3},
    "teeth-whitening": {PERSONA_SHAME: 0.6},
    "root-canal-treatment": {PERSONA_TRUST: 0.5, PERSONA_FEAR: 0.4},
    "tooth-fillings": {PERSONA_TRUST: 0.4},
    "teeth-cleaning": {PERSONA_TRUST: 0.4},
}

TOPIC_SIGNALS = {
    "best-dental-clinic-istanbul": {PERSONA_PREMIUM: 1.0, PERSONA_SKEPTIC: 0.6},
    "best-dental-clinic-turkey": {PERSONA_PREMIUM: 0.9, PERSONA_SKEPTIC: 0.8},
    "dental-care-turkey": {PERSONA_TRUST: 0.6},
    "dental-tourism": {PERSONA_SKEPTIC: 0.6},
    "best-country-dental-tourism": {PERSONA_SKEPTIC: 0.9, PERSONA_PRICE: 0.4},
    "teeth-done-in-turkey": {PERSONA_SKEPTIC: 0.7, PERSONA_FEAR: 0.4},
    "dental-surgery-turkey": {PERSONA_FEAR: 0.9},
    "dental-guarantee-aftercare": {PERSONA_FEAR: 1.1, PERSONA_TRUST: 0.4},
    "smile-gallery": {PERSONA_SHAME: 1.1, PERSONA_PREMIUM: 0.4},
    "dental-clinic-istanbul": {PERSONA_READY: 0.6},
    "dental-care-antalya": {PERSONA_READY: 0.3},
    "dental-clinic-aegean": {PERSONA_READY: 0.3},
    "dental-clinic-ankara": {PERSONA_READY: 0.3},
    "istanbul-guide": {PERSONA_READY: 0.8},
    "dental-tourism-agency": {PERSONA_READY: 0.4},
}

VIEW_SIGNALS = {
    "prices:index": {PERSONA_PRICE: 1.3},
    "prices:detail": {PERSONA_PRICE: 1.2},
    "packages:index": {PERSONA_PRICE: 0.6},
    "packages:treatment": {PERSONA_PRICE: 0.5},
    "origins:detail": {PERSONA_PRICE: 0.3, PERSONA_READY: 0.4},
    "clinics:detail": {PERSONA_TRUST: 0.6, PERSONA_SKEPTIC: 0.3},
    "doctors:detail": {PERSONA_PREMIUM: 0.6, PERSONA_TRUST: 0.6},
    "core:about": {PERSONA_TRUST: 0.7, PERSONA_PREMIUM: 0.3},
    "core:contact": {PERSONA_READY: 1.3},
    "blog:post_detail": {PERSONA_SKEPTIC: 0.5},
    "guides:index": {PERSONA_SKEPTIC: 0.4},
}


def _slug_map(model_label):
    """{(lang-agnostic) slug: canonical EN slug/key} — tüm çeviri slug'ları, 1 saat cache'li."""
    key = f"persona:slugmap:{model_label}"
    data = cache.get(key)
    if data is not None:
        return data
    data = {}
    if model_label == "treatment":
        from apps.treatments.models import Treatment, TreatmentTranslation

        for t in Treatment.objects.only("slug"):
            data[t.slug] = t.slug
        for tr in TreatmentTranslation.objects.select_related("treatment").only("slug", "treatment__slug"):
            data[tr.slug] = tr.treatment.slug
    else:
        from apps.seo.models import SeoTopic, SeoTopicTranslation

        for t in SeoTopic.objects.only("slug", "key"):
            data[t.slug] = t.key
        for tr in SeoTopicTranslation.objects.select_related("topic").only("slug", "topic__key"):
            data[tr.slug] = tr.topic.key
    cache.set(key, data, 3600)
    return data


def page_signal(path):
    """(sayfa_türü, {persona: ağırlık}) — eşleşme yoksa (None, {})."""
    try:
        match = resolve(path)
    except Resolver404:
        return None, {}
    name = match.view_name or ""
    slug = match.kwargs.get("slug", "")
    if name in ("treatments:detail", "treatments:city", "packages:treatment", "prices:detail") and slug:
        canonical = _slug_map("treatment").get(slug, slug)
        sig = dict(TREATMENT_SIGNALS.get(canonical, {}))
        for p, w in VIEW_SIGNALS.get(name, {}).items():
            sig[p] = sig.get(p, 0) + w
        return f"{name}:{canonical}", sig
    if name == "guides:detail" and slug:
        topic = _slug_map("topic").get(slug, slug)
        return f"guide:{topic}", dict(TOPIC_SIGNALS.get(topic, {}))
    return name, dict(VIEW_SIGNALS.get(name, {}))


def apply_page(session, path):
    """Oturuma sayfa kanıtını ekler. Değişiklik olduysa True."""
    kind, sig = page_signal(path)
    if not kind:
        return False
    seen = list(session.pages_seen or [])
    if seen.count(kind) >= REPEAT_CAP:
        return False
    seen.append(kind)
    session.pages_seen = seen[-30:]
    if sig:
        scores = dict(session.page_scores or {})
        for p, w in sig.items():
            scores[p] = round(min(PERSONA_CAP, scores.get(p, 0.0) + w), 2)
        session.page_scores = scores
    return True
