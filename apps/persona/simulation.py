"""
Persona ML doğrulama simülasyonu.

Gerçek motoru (intent → inference → Thompson Sampling → event'ler → dönüşüm → bandit güncelleme
→ supervised model eğitimi → ML policy) sentetik ziyaretçilerle uçtan uca çalıştırır.

Her sanal ziyaretçinin gizli bir "gerçek persona"sı vardır. Dönüşüm olasılığı, gösterilen varyantın
gerçek persona ile eşleşmesine bağlıdır (eşleşirse yüksek). Sistem bunu bilmeden öğrenmelidir:
  - zamanla doğru varyantı gösterme oranı artmalı,
  - dönüşüm oranı rastgele varyant göstermekten yüksek olmalı,
  - supervised model anlamlı AUC ile eğitilip IPS değerlendirmesini geçmeli.

Varsayılan olarak her şey bir transaction içinde çalışır ve sonunda GERİ ALINIR (gerçek veriyi kirletmez).
"""
import random
import tempfile
from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.core.cache import cache
from django.db import transaction
from django.test import RequestFactory, override_settings
from django.utils import timezone

from .models import PERSONAS, PersonaExposure

TRUE_MIX = {"price": .30, "fear": .15, "skeptic": .15, "shame": .15, "trust": .10, "premium": .04,
            "quality": .06, "urgency": .03, "ready": .02}
QUERIES = {
    "price": {"en": "dental implants turkey cost", "de": "zahnimplantate türkei kosten", "nl": "tandimplantaten turkije prijs"},
    "fear": {"en": "is dental treatment in turkey safe", "de": "zahnbehandlung türkei risiken sicher", "nl": "tandarts turkije veilig"},
    "skeptic": {"en": "veneers turkey reviews reddit", "de": "veneers türkei erfahrungen", "nl": "facings turkije ervaringen"},
    "shame": {"en": "hollywood smile turkey", "de": "hollywood smile türkei veneers", "nl": "hollywood smile turkije"},
    "trust": {"en": "trusted dentist istanbul recommend", "de": "seriöser zahnarzt istanbul", "nl": "betrouwbaar tandarts istanbul"},
    "premium": {"en": "luxury vip dental clinic istanbul", "de": "luxus zahnklinik istanbul vip", "nl": "luxe tandarts istanbul premium"},
    "quality": {"en": "best high quality dentist istanbul", "de": "beste hochwertige zahnklinik istanbul", "nl": "beste kwaliteit tandarts istanbul"},
    "urgency": {"en": "emergency dentist istanbul fast", "de": "notfall zahnarzt istanbul schnell", "nl": "spoed tandarts istanbul"},
    "ready": {"en": "book dentist istanbul appointment", "de": "zahnarzt istanbul termin", "nl": "tandarts istanbul afspraak"},
}
BEHAVIOR = {
    "price": [("section_time", {"section": "price", "seconds": 70}), ("price_hover", {})],
    "fear": [("section_time", {"section": "safety", "seconds": 80}), ("cert_click", {})],
    "skeptic": [("faq_open", {}), ("faq_open", {}), ("section_time", {"section": "reviews", "seconds": 90})],
    "shame": [("before_after", {"seconds": 60}), ("gallery_view", {"section": "before_after"})],
    "trust": [("video_play", {}), ("video_time", {"seconds": 150})],
    "premium": [("gallery_view", {}), ("gallery_view", {})],
    "quality": [("section_view", {"section": "doctor"}), ("cert_click", {})],
    "urgency": [("urgency_cta", {}), ("cta_click", {})],
    "ready": [("form_start", {}), ("cta_click", {})],
}


def true_conversion_rate(true_persona, shown):
    """Gizli dünya modeli: doğru varyant ~3x dönüştürür, varsayılan sayfa orta, yanlış varyant düşük."""
    if shown == true_persona:
        return 0.12
    if shown == "unknown":
        return 0.05
    return 0.025


class _Rollback(Exception):
    pass


def _visitor(rng, factory, i):
    from .engine import get_or_create_persona, record_event

    true = rng.choices(list(TRUE_MIX), weights=list(TRUE_MIX.values()))[0]
    lang = rng.choice(["en", "de", "nl"])
    device = rng.choice(["mobile", "mobile", "desktop"])
    ua = "Mozilla/5.0 (iPhone) Mobile Safari" if device == "mobile" else "Mozilla/5.0 (Windows NT 10.0) Chrome/120"
    params = {}
    has_query = rng.random() < 0.5
    if has_query:
        params = {"utm_term": QUERIES[true][lang], "gclid": f"sim{i}"}
    request = factory.get(f"/{lang}/", params, HTTP_USER_AGENT=ua)
    request.session = SessionStore()
    request.session.save()
    request.is_bot = False
    request.LANGUAGE_CODE = lang
    request.tracking_session = None
    request.user = AnonymousUser()
    key = request.session.session_key

    first = get_or_create_persona(request)
    # Ziyaretçinin %70'i persona'sına uygun davranış sergiler (sayfada gezinir)
    if rng.random() < 0.7:
        for ev, data in BEHAVIOR[true]:
            record_event(key, ev, data)
        request = factory.get(f"/{lang}/treatments/", HTTP_USER_AGENT=ua)
        request.session = SessionStore(session_key=key)
        request.is_bot, request.LANGUAGE_CODE, request.tracking_session = False, lang, None
        request.user = AnonymousUser()
    final = get_or_create_persona(request)
    shown = final["persona"]
    converted = rng.random() < true_conversion_rate(true, shown)
    if converted:
        record_event(key, "whatsapp_click", {})
    return {"true": true, "shown": shown, "first": first["persona"], "converted": converted,
            "inferred": final["inferred"], "has_query": has_query}


def _summary(rows):
    n = len(rows) or 1
    return {
        "visitors": len(rows),
        "match_rate": round(sum(r["shown"] == r["true"] for r in rows) / n, 3),
        "inferred_accuracy": round(sum(r["inferred"] == r["true"] for r in rows) / n, 3),
        "conversion_rate": round(sum(r["converted"] for r in rows) / n, 4),
    }


def run(n=3000, ml_phase=1000, seed=42, keep=False, log=print):
    """Simülasyonu çalıştırır, metrik sözlüğü döner."""
    rng = random.Random(seed)
    random.seed(seed)  # bandit örneklemesi de deterministik olsun
    factory = RequestFactory()
    result = {}
    model_dir = tempfile.mkdtemp(prefix="persona_sim_")

    def body():
        from . import ml

        cache.clear()
        ml._cache.update(loaded_at=0, model=None, version=None)
        rows = []
        for i in range(n):
            rows.append(_visitor(rng, factory, i))
            if log and (i + 1) % 500 == 0:
                log(f"  bandit: {i + 1}/{n} ziyaretçi — son 500 CR={_summary(rows[-500:])['conversion_rate']}")
        k = max(1, n // 5)
        result["bandit_first_20pct"] = _summary(rows[:k])
        result["bandit_last_20pct"] = _summary(rows[-k:])
        result["bandit_all"] = _summary(rows)
        # Referans değerler (gizli dünya modelinden analitik)
        result["reference"] = {
            "always_default_cr": 0.05,
            "random_variant_cr": round(sum(TRUE_MIX[t] * sum(true_conversion_rate(t, s) for s in ["unknown"] + PERSONAS)
                                           / (len(PERSONAS) + 1) for t in TRUE_MIX), 4),
            "oracle_cr": 0.12,
        }
        # Dönüşüm penceresi kapanmış gibi göster (eğitim seti için)
        PersonaExposure.objects.update(created_at=timezone.now() - timedelta(days=2))
        with override_settings(PERSONA_MODEL_DIR=model_dir):
            train = ml.train(force=True)
        result["ml_training"] = {k: train.get(k) for k in ("trained", "active", "metrics", "samples", "positives")}
        if train.get("active") and ml_phase:
            ml._cache["loaded_at"] = 0
            rows2 = [_visitor(rng, factory, n + i) for i in range(ml_phase)]
            result["ml_policy"] = _summary(rows2)
            result["ml_policy"]["method"] = PersonaExposure.objects.order_by("-id").first().policy
        if not keep:
            raise _Rollback()

    try:
        with transaction.atomic():
            body()
    except _Rollback:
        pass
    finally:
        from . import ml

        ml._cache.update(loaded_at=0, model=None, version=None)
        cache.clear()
    return result
