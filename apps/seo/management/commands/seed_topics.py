"""
Konu (rehber) sayfalarını ve pSEO keyword'lerini veritabanına yükler.

  python manage.py seed_topics              # yeni konuları ekler, eksik çevirileri ekler (admin düzenlemelerini EZMEZ)
  python manage.py seed_topics --overwrite  # içerikleri dosyadan yeniden yazar
  python manage.py seed_topics --report     # sadece dil kapsamını yazdırır

Kaynak: apps/seo/topics.py (EN) + apps/seo/topic_content/<dil>.json (diğer 15 dil).
Keyword'ler Keyword tablosuna hedef URL'leriyle yazılır (status=targeted).
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone, translation

from dental_tourism.languages import LANGUAGE_META

from apps.localization.models import TranslationStatus
from apps.seo import package_data as P
from apps.seo.models import Keyword, SeoTopic, SeoTopicTranslation
from apps.seo.topics import PRICE_KEYWORDS, TOPICS, TREATMENT_PAGE_KEYWORDS

CONTENT_DIR = Path(__file__).resolve().parents[2] / "topic_content"

# Kullanıcının listelerindeki metrikler (hacim, CPC $, PD)
METRICS = {
    "dental tourism": (3600, None, 35), "dental clinic turkey": (2400, None, 37), "dentist clinic turkey": (1900, None, None),
    "dental care in turkey": (1900, None, 22), "dental tourism turkey": (880, None, 30), "dental price turkey": (880, None, 74),
    "dental tourism packages": (260, 5.41, 11), "best country for dental tourism": (260, None, 37),
    "dental health tourism": (170, None, 40), "best dental clinic in istanbul turkey reviews": (170, 7.21, 61),
    "dental tourism countries": (110, None, 62), "dental tourism agency": (110, None, 16), "istanbul areas to avoid": (50, None, 12),
    "best dental tourism": (30, None, 59), "best dental implant tourism": (20, None, 6),
    "top 10 dental tourism destinations": (10, None, 1), "dental clinic in turkey istanbul": (None, 16.99, None),
    "where to get teeth done in turkey": (None, 10.03, None),
}


def _faq(items):
    return [{"question": q, "answer": a} for q, a in items]


class Command(BaseCommand):
    help = "Konu sayfalarını (16 dil) ve pSEO keyword'lerini yükler"

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true")
        parser.add_argument("--keys", default="", help="yalnızca bu konular (virgülle) — ör. --overwrite --keys dental-clinic-istanbul")
        parser.add_argument("--report", action="store_true")
        parser.add_argument("--no-keywords", action="store_true")

    def handle(self, overwrite=False, report=False, no_keywords=False, keys="", **o):
        only = {k.strip() for k in keys.split(",") if k.strip()}
        content = {}
        for lang in LANGUAGE_META:
            f = CONTENT_DIR / f"{lang}.json"
            if f.exists():
                content[lang] = json.loads(f.read_text(encoding="utf-8"))
        if report:
            for key in TOPICS:
                have = ["en"] + [lg for lg in content if key in content[lg]]
                self.stdout.write(f"{key:32} {len(have):2}/16  eksik: {sorted(set(LANGUAGE_META) - set(have))}")
            return
        with transaction.atomic():
            n_new = n_tr = 0
            for key, data in TOPICS.items():
                if only and key not in only:
                    continue
                en = data["en"]
                topic = SeoTopic.objects.filter(key=key).first()
                fields = {"group": data["group"], "kind": data["kind"], "order": data["order"],
                          "show_cases": data.get("show_cases", False),
                          "keywords": "\n".join(f"{lg}: {kw}" for lg, kws in data["keywords"].items() for kw in kws)}
                body = {"slug": data["slugs"]["en"], "h1": en["h1"], "lead": en["lead"], "body": en["body"],
                        "faq": _faq(en["faq"]), "meta_title": en["meta_title"][:70],
                        "meta_description": en["meta_description"][:170]}
                if topic is None:
                    topic = SeoTopic.objects.create(key=key, source_language="en", **fields, **body)
                    n_new += 1
                else:
                    for k, v in fields.items():
                        setattr(topic, k, v)
                    if overwrite:
                        for k, v in body.items():
                            if k != "slug":
                                setattr(topic, k, v)
                    topic.save()
                src_hash = topic.compute_source_hash()
                for lang, tr_data in ((lg, content[lg].get(key)) for lg in content):
                    if lang == "en" or not tr_data:
                        continue
                    tr = SeoTopicTranslation.objects.filter(topic=topic, language_code=lang).first()
                    if tr and not overwrite and tr.status != TranslationStatus.FAILED:
                        continue
                    tr = tr or SeoTopicTranslation(topic=topic, language_code=lang)
                    if not tr.slug:
                        tr.slug = data["slugs"][lang]
                    tr.h1 = tr_data["h1"]
                    tr.lead = tr_data["lead"]
                    tr.body = tr_data["body"]
                    tr.faq = _faq(tr_data["faq"])
                    tr.meta_title = tr_data["meta_title"][:70]
                    tr.meta_description = tr_data["meta_description"][:170]
                    tr.status = TranslationStatus.REVIEWED
                    tr.source_hash = src_hash
                    tr.model_used = "seed_topics"
                    tr.translated_at = timezone.now()
                    tr.error = ""
                    tr.save()
                    n_tr += 1
        self.stdout.write(self.style.SUCCESS(f"✓ {n_new} yeni konu, {n_tr} çeviri yazıldı"))
        if not no_keywords:
            with transaction.atomic():  # yüzlerce upsert tek commit'te (uzak DB'de / yavaş diskte çok daha hızlı)
                n_kw = self._keywords()
            self.stdout.write(self.style.SUCCESS(f"✓ {n_kw} keyword hedef URL'siyle güncellendi"))

    # ── Keyword tablosu ───────────────────────────────────────────────────
    def _upsert(self, term, lang, url, page_type, intent="commercial", primary=False, treatment=None):
        vol, cpc, pd = METRICS.get(term, (None, None, None))
        kw, _ = Keyword.objects.get_or_create(term=term[:200], language=lang)
        kw.target_url, kw.page_type, kw.status, kw.source = url, page_type, "targeted", "import"
        kw.intent = intent
        from apps.persona.intent import score_text

        sc = score_text(term)
        if sc:  # cheap→price, dental work→trust, best/quality→premium (ayrı niyetler)
            kw.persona_hint = max(sc, key=sc.get)
        kw.is_primary = kw.is_primary or primary
        if treatment:
            kw.treatment = treatment
        if vol is not None:
            kw.search_volume = vol
        if cpc is not None:
            kw.cpc = cpc
        if pd is not None:
            kw.difficulty = pd
        kw.save()
        return 1

    def _keywords(self):
        from django.urls import reverse

        from apps.treatments.models import Treatment

        n = 0
        treatments = list(Treatment.objects.filter(is_active=True))
        for lang in LANGUAGE_META:
            with translation.override(lang):
                for topic in SeoTopic.objects.filter(is_active=True):
                    loc = topic.localized(lang, fallback=False)
                    if loc is None:
                        continue
                    url = reverse("guides:detail", kwargs={"slug": loc.slug})
                    for i, term in enumerate(TOPICS.get(topic.key, {}).get("keywords", {}).get(lang, [])):
                        n += self._upsert(term, lang, url, "guide", "informational" if topic.kind == "guide"
                                          else "commercial", primary=i == 0)
                url = reverse("prices:index")
                for i, term in enumerate(PRICE_KEYWORDS["index"].get(lang, [])):
                    n += self._upsert(term, lang, url, "treatment_price", "transactional", primary=i == 0)
                url = reverse("packages:index")
                for i, term in enumerate(P.keywords_for(lang, "hub")):
                    n += self._upsert(term, lang, url, "package", primary=i == 0)
                for t in treatments:
                    loc = t.localized(lang, fallback=False)
                    if loc is None:
                        continue
                    price_url = reverse("prices:detail", kwargs={"slug": loc.slug})
                    pkg_url = reverse("packages:treatment", kwargs={"slug": loc.slug})
                    terms = [PRICE_KEYWORDS["treatment_pattern"][lang].format(t=loc.name.lower())]
                    if lang == "en":
                        terms += PRICE_KEYWORDS["treatment"].get(t.slug, [])
                    for term in terms:
                        n += self._upsert(term, lang, price_url, "treatment_price", "transactional", treatment=t)
                    terms = P.keywords_for(lang, "treatment", loc.name)
                    if lang == "en":
                        terms += TREATMENT_PAGE_KEYWORDS.get(t.slug, [])
                    for term in terms:
                        n += self._upsert(term, lang, pkg_url, "package", treatment=t)
                for code in P.origin_codes(lang):
                    url = reverse("origins:detail", kwargs={"country": P.country_slug(code, lang)})
                    info = P.ORIGINS[code]
                    for term in P.keywords_for(lang, "origin", country=P.country_name(code, lang), cities=info["cities"]):
                        n += self._upsert(term, lang, url, "package")
        return n
