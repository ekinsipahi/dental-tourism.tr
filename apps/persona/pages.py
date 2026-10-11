"""
Site içi gezinme → persona kanıtı (SAYAÇ + SÜRE).

Bir sayfa iki aşamada puan verir:
  1. Açılınca          → sinyalin %25'i (LOAD_SHARE) — sadece tıklayıp çıkan kişi az puan alır
  2. Çıkarken (süre)    → kalan %75 × min(süre / 60 sn, 1); 5 sn altı = 0 (yanlış tık / geri dönüş)
Yani 60+ sn okunan "en iyi klinik" rehberi tam puan, 3 sn bakılıp çıkılan neredeyse hiç.

Sayfa grupları:
  fiyat sayfaları (/prices/…), paketler                         → price
  "en iyi klinik" rehberleri, hekim profili, hakkımızda           → quality
  tedavi sayfaları (implant, lamina, zirkonyum…)                  → skeptic (araştırıyor) — tür tercihi DEĞİL
  garanti / takip / cerrahi rehberleri                            → fear (+ kalite)
  yorumlar, karşılaştırma, "hangi ülke" rehberleri                → skeptic
  gülüş galerisi                                                  → shame (estetik)
  iletişim, İstanbul rehberi, lokasyonlar                         → ready
Her sayfa türü ziyaret başına en fazla REPEAT_CAP kez sayılır (yenilemek skoru şişirmez).
Tüm dillerdeki slug'lar çözülür (/de/behandlungen/keramik-veneers/ → porcelain-veneers).
"""
from django.core.cache import cache
from django.urls import Resolver404, resolve

from .models import (PERSONA_FEAR, PERSONA_PREMIUM, PERSONA_PRICE, PERSONA_QUALITY, PERSONA_READY,
                     PERSONA_SHAME, PERSONA_SKEPTIC, PERSONA_TRUST)

REPEAT_CAP = 2
PERSONA_CAP = 6.0
LOAD_SHARE = 0.25        # sayfa açılınca verilen pay
DWELL_FULL = 60          # bu kadar saniye okunursa kalan payın tamamı
DWELL_MIN = 5            # altı = sayılmaz

TREATMENT_SIGNALS = {
    "porcelain-veneers": {PERSONA_SKEPTIC: 0.5, PERSONA_SHAME: 0.2},
    "zirconia-crowns": {PERSONA_SKEPTIC: 0.5},
    "all-on-4-implants": {PERSONA_SKEPTIC: 0.5, PERSONA_FEAR: 0.2},
    "hollywood-smile": {PERSONA_SKEPTIC: 0.4, PERSONA_SHAME: 0.3, PERSONA_PREMIUM: 0.3},
    "dental-implants": {PERSONA_SKEPTIC: 0.5, PERSONA_FEAR: 0.2},
    "composite-veneers": {PERSONA_SKEPTIC: 0.5, PERSONA_SHAME: 0.2},
    "teeth-whitening": {PERSONA_SKEPTIC: 0.4, PERSONA_SHAME: 0.2},
    "root-canal-treatment": {PERSONA_SKEPTIC: 0.5, PERSONA_FEAR: 0.2},
    "tooth-fillings": {PERSONA_SKEPTIC: 0.4},
    "teeth-cleaning": {PERSONA_SKEPTIC: 0.4},
}

TOPIC_SIGNALS = {
    "best-dental-clinic-istanbul": {PERSONA_QUALITY: 1.1, PERSONA_SKEPTIC: 0.5},
    "best-dental-clinic-turkey": {PERSONA_QUALITY: 1.0, PERSONA_SKEPTIC: 0.7},
    "dental-care-turkey": {PERSONA_TRUST: 0.6},
    "dental-tourism": {PERSONA_SKEPTIC: 0.6},
    "best-country-dental-tourism": {PERSONA_SKEPTIC: 0.9, PERSONA_PRICE: 0.4},
    "teeth-done-in-turkey": {PERSONA_SKEPTIC: 0.7, PERSONA_FEAR: 0.4},
    "dental-surgery-turkey": {PERSONA_FEAR: 0.9, PERSONA_QUALITY: 0.3},
    "dental-guarantee-aftercare": {PERSONA_FEAR: 1.0, PERSONA_QUALITY: 0.6, PERSONA_TRUST: 0.3},
    "smile-gallery": {PERSONA_SHAME: 1.1, PERSONA_PREMIUM: 0.6},
    "dental-clinic-istanbul": {PERSONA_READY: 0.6},
    "dental-care-antalya": {PERSONA_READY: 0.3},
    "dental-clinic-aegean": {PERSONA_READY: 0.3},
    "dental-clinic-ankara": {PERSONA_READY: 0.3},
    "istanbul-guide": {PERSONA_READY: 0.8, PERSONA_PREMIUM: 0.3},
    "dental-tourism-agency": {PERSONA_READY: 0.4},
}

VIEW_SIGNALS = {
    "prices:index": {PERSONA_PRICE: 1.3},
    "prices:detail": {PERSONA_PRICE: 1.2},
    "packages:index": {PERSONA_PRICE: 0.6, PERSONA_PREMIUM: 0.4},
    "packages:treatment": {PERSONA_PRICE: 0.5},
    "origins:detail": {PERSONA_PRICE: 0.3, PERSONA_READY: 0.4},
    "clinics:detail": {PERSONA_TRUST: 0.6, PERSONA_SKEPTIC: 0.3},
    "doctors:detail": {PERSONA_QUALITY: 0.9, PERSONA_TRUST: 0.5},
    "core:about": {PERSONA_TRUST: 0.7, PERSONA_QUALITY: 0.5},
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


def _add(session, sig, share):
    scores = dict(session.page_scores or {})
    added = {}
    for p, w in sig.items():
        v = round(w * share, 3)
        if v > 0:
            scores[p] = round(min(PERSONA_CAP, scores.get(p, 0.0) + v), 2)
            added[p] = v
    session.page_scores = scores
    return added


def apply_page(session, path):
    """Sayfa açıldı → sinyalin LOAD_SHARE kadarı. Değişiklik olduysa True."""
    kind, sig = page_signal(path)
    if not kind:
        return False
    seen = list(session.pages_seen or [])
    if seen.count(kind) >= REPEAT_CAP:
        return False
    seen.append(kind)
    session.pages_seen = seen[-40:]
    if sig:
        _add(session, sig, LOAD_SHARE)
    return True


def apply_dwell(session, path, seconds):
    """Sayfadan çıkarken: kalan pay × okuma süresi. Kanıt günlüğüne 'sayfa — 45 sn' yazılır."""
    from .mindset import add_evidence

    kind, sig = page_signal(path)
    if not kind:
        return False
    seconds = max(0, int(seconds or 0))
    seen = list(session.pages_seen or [])
    key = f"dwell:{kind}"
    if seen.count(key) >= REPEAT_CAP:
        return False
    seen.append(key)
    session.pages_seen = seen[-40:]
    factor = 0.0 if seconds < DWELL_MIN else min(seconds / DWELL_FULL, 1.0)
    added = _add(session, sig, (1 - LOAD_SHARE) * factor) if sig else {}
    total = {p: round(v * (LOAD_SHARE + (1 - LOAD_SHARE) * factor), 2) for p, v in sig.items()} if sig else {}
    add_evidence(session, "page", f"{kind} — {seconds} sn", total or {"unknown": 0})
    return bool(added) or True
