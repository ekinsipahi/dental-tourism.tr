"""Keyword üretimi, içe aktarma ve sayfa eşleme."""
import csv
import logging

from django.db import IntegrityError
from django.urls import reverse
from django.utils import translation

from dental_tourism.languages import LANGUAGE_META

from apps.clinics.models import City
from apps.treatments.models import Treatment

from .keyword_data import HOME_TERMS, KEYWORD_PATTERNS, TREATMENT_KEYS, TREATMENT_NAMES
from .models import Keyword

logger = logging.getLogger(__name__)


def _treatment_term(t, lang):
    if t.key in TREATMENT_KEYS:
        return TREATMENT_NAMES[lang][TREATMENT_KEYS.index(t.key)].lower()
    return t.localized(lang).name.lower()


def seed_keywords(languages=None):
    """Tedavi × şehir × kalıp × dil matrisinden keyword üretir (mevcutları atlar)."""
    created = 0
    cities = list(City.objects.filter(is_active=True))
    treatments = list(Treatment.objects.filter(is_active=True))
    for lang in languages or LANGUAGE_META:
        meta = LANGUAGE_META[lang]
        for t in treatments:
            term_t = _treatment_term(t, lang)
            for pattern, intent, funnel, persona, page_type in KEYWORD_PATTERNS.get(lang, []):
                city_list = cities if "{city}" in pattern else [None]
                homes = HOME_TERMS.get(lang, [""]) if "{home}" in pattern else [""]
                for city in city_list:
                    for home in homes:
                        term = pattern.format(t=term_t, city=(city.localized(lang).name if city else "").lower(),
                                              country=meta["turkey"].lower(), home=home)
                        term = " ".join(term.split())
                        try:
                            _, was_created = Keyword.objects.get_or_create(term=term, language=lang, defaults={
                                "treatment": t, "city": city, "intent": intent, "funnel_stage": funnel,
                                "persona_hint": persona, "page_type": page_type, "source": "seed",
                                "priority": 70 if intent != "informational" else 50,
                            })
                            created += was_created
                        except IntegrityError:
                            continue
    assign_targets()
    return created


def target_url_for(kw):
    """Keyword'ün hedef sayfası (o dilde)."""
    if kw.blog_post_id:
        return kw.blog_post.get_absolute_url(kw.language) if kw.blog_post.is_published else ""
    if not kw.treatment_id:
        return ""
    with translation.override(kw.language):
        loc = kw.treatment.localized(kw.language)
        if kw.page_type == "treatment_city" and kw.city_id:
            return reverse("treatments:city", kwargs={"slug": loc.slug, "city_slug": kw.city.localized(kw.language).slug})
        if kw.page_type == "treatment_price":
            return reverse("prices:detail", kwargs={"slug": loc.slug})
        if kw.page_type == "treatment":
            return reverse("treatments:detail", kwargs={"slug": loc.slug})
    return ""


def assign_targets():
    n = 0
    for kw in Keyword.objects.select_related("treatment", "city", "blog_post").exclude(status="ignored"):
        url = target_url_for(kw)
        if url and url != kw.target_url:
            kw.target_url = url
            if kw.status == "new":
                kw.status = "targeted"
            kw.save(update_fields=["target_url", "status"])
            n += 1
    return n


def import_csv(path, language, source="import"):
    """Ahrefs / Semrush / Google Keyword Planner CSV'si.
    Sütun adları esnek: keyword|term, volume|search volume|avg. monthly searches, kd|difficulty, cpc, position."""
    def pick(row, *names):
        for n in names:
            for k, v in row.items():
                if k and k.strip().lower() == n:
                    return v
        return None

    def num(v, cast=int):
        try:
            return cast(str(v).replace(",", "").replace("%", "").strip())
        except (TypeError, ValueError):
            return None

    created = updated = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        for row in csv.DictReader(f, dialect=dialect):
            term = (pick(row, "keyword", "term", "query", "top queries") or "").strip().lower()
            if not term:
                continue
            defaults = {k: v for k, v in {
                "search_volume": num(pick(row, "volume", "search volume", "avg. monthly searches")),
                "difficulty": num(pick(row, "kd", "keyword difficulty", "difficulty")),
                "cpc": num(pick(row, "cpc", "cpc (usd)", "top of page bid (high range)"), float),
                "current_position": num(pick(row, "position", "current position"), float),
                "clicks_28d": num(pick(row, "clicks")),
                "impressions_28d": num(pick(row, "impressions")),
            }.items() if v is not None}
            obj, was_created = Keyword.objects.get_or_create(term=term, language=language,
                                                             defaults={**defaults, "source": source})
            if was_created:
                created += 1
            elif defaults:
                Keyword.objects.filter(pk=obj.pk).update(**defaults)
                updated += 1
    _auto_tag_imported(language)
    return created, updated


def _auto_tag_imported(language):
    """İçe aktarılan kelimeleri tedaviye/niyete göre otomatik etiketle."""
    from apps.persona.intent import normalize, score_text

    treatments = list(Treatment.objects.filter(is_active=True))
    for kw in Keyword.objects.filter(language=language, treatment__isnull=True):
        nterm = normalize(kw.term)
        for t in treatments:
            if normalize(_treatment_term(t, language)) in nterm or normalize(t.localized(language).name) in nterm:
                kw.treatment = t
                break
        scores = score_text(kw.term)
        if scores:
            kw.persona_hint = max(scores, key=scores.get)
            if kw.persona_hint == "price":
                kw.page_type, kw.intent = "treatment_price", "commercial"
            elif kw.persona_hint in ("fear", "skeptic"):
                kw.page_type, kw.intent, kw.funnel_stage = "blog", "informational", "awareness"
        kw.save()
