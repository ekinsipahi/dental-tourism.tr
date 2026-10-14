"""
İçerik makinesi — Claude ile SEO içerik üretimi.

  generate_post_from_keyword(kw)    → Keyword'ün dilinde blog taslağı (status=review)
  generate_post(topic, lang, ...)   → serbest konu
  generate_treatment_content(t)     → tedavi sayfası gövdesi + FAQ + meta (kaynak dil)
  generate_landing(page)            → programatik sayfa metni (kaynak dil)
  expand_keywords(lang, treatment)  → AI ile long-tail keyword önerileri

Tüm üretimler veritabanındaki GERÇEK verilerle (klinik bilgisi, fiyatlar) beslenir;
model fiyat/istatistik uyduramaz. Yayınlanan içerik otomatik olarak diğer dillere çevrilir.
"""
import json
import logging

from django.conf import settings
from django.urls import reverse
from django.utils import translation
from slugify import slugify

from dental_tourism.languages import LANGUAGE_META

from apps.localization import llm

from .models import BlogCategory, BlogPost

logger = logging.getLogger(__name__)

WRITER_SYSTEM = """You are the senior medical content writer of {site}, a dental tourism website in Istanbul, Turkey.
You write patient-education content that ranks on Google AND converts readers into consultation requests.

Principles (E-E-A-T, YMYL health content):
- Accurate, balanced, evidence-based. Explain risks and alternatives honestly. No miracle claims, no guarantees beyond those in FACTS.
- NEVER state prices, price ranges or currency amounts (no €, £, $). Pricing is always personal: tell readers they get a personal plan and fixed written quote after a free WhatsApp consultation. Percentages of savings are allowed only qualitatively ("significantly less than at home").
- NEVER promise or imply hotels, flights, airport transfers, accommodation or transport — the clinic does not arrange travel (and do not say so bluntly either). Frame value instead: the patient's budget goes into the treatment plan, not extras, and more affordable options are available; appointments are planned around the patient's travel dates.
- Use ONLY numbers (years, patient counts, ratings, durations) given in FACTS. If a number is not in FACTS, describe qualitatively.
- Ethical stance of the clinic: only the treatment the patient actually needs; saving the natural tooth comes first.
- Write natively in the requested language for that market (not translated-sounding). Use the terms locals search for.
- Structure: short intro that contains the focus keyword in the first 100 words, then ## H2 sections (and ### H3 where useful), lists, and one comparison table when it helps. Never use a single '#' H1 (the page title is the H1).
- Add 2-4 natural internal links using ONLY the URLs listed in INTERNAL LINKS (Markdown links).
- End with a short, non-pushy call to action to get a free assessment via WhatsApp.
- "slug": lowercase, hyphenated, ASCII, 3-7 words in the target language with the main keyword.
- "meta_title" max 60 chars, keyword first. "meta_description" 140-158 chars with keyword and a benefit.
- "faq": 4-6 real questions people ask about this topic, concise answers (2-4 sentences)."""

POST_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"}, "slug": {"type": "string"}, "excerpt": {"type": "string"},
        "content": {"type": "string"},
        "faq": {"type": "array", "items": {"type": "object", "properties": {
            "question": {"type": "string"}, "answer": {"type": "string"}},
            "required": ["question", "answer"], "additionalProperties": False}},
        "meta_title": {"type": "string"}, "meta_description": {"type": "string"},
        "focus_keyword": {"type": "string"}, "featured_image_alt": {"type": "string"},
        "funnel_stage": {"type": "string", "enum": ["awareness", "consideration", "decision"]},
        "target_personas": {"type": "array", "items": {"type": "string", "enum": [
            "skeptic", "price", "premium", "quality", "ready", "fear", "shame", "urgency", "trust"]}},
    },
    "required": ["title", "slug", "excerpt", "content", "faq", "meta_title", "meta_description", "focus_keyword",
                 "featured_image_alt", "funnel_stage", "target_personas"],
    "additionalProperties": False,
}

FUNNEL_BRIEF = {
    "awareness": "TOP OF FUNNEL: educate and answer the question thoroughly. Mention treatment abroad only briefly.",
    "consideration": "MID FUNNEL: compare options, costs (home country vs Istanbul using FACTS only), quality "
                     "criteria, how to evaluate a clinic.",
    "decision": "BOTTOM OF FUNNEL: why this clinic, the process step by step, planning appointments around the trip, what is included, "
                "strong but honest call to action.",
}


def _facts(lang, treatment=None):
    from apps.clinics.models import Clinic
    clinic = Clinic.primary()
    facts = {"site": settings.SITE_NAME}
    if clinic:
        facts["clinic"] = {
            "name": clinic.name, "city": clinic.city.name, "district": clinic.district, "address": clinic.address,
            "years_experience_lead_dentist": clinic.years_experience, "patients_treated": clinic.patients_treated,
            "google_rating": float(clinic.google_rating) if clinic.google_rating else None,
            "google_review_count": clinic.google_review_count, "languages": clinic.languages_spoken,
            "accreditations": clinic.accreditations or "none listed — do not claim any",
            "airport_transfer": clinic.offers_airport_transfer,
        }
        doctor = clinic.doctors.filter(is_lead_doctor=True).first()
        if doctor:
            facts["lead_dentist"] = {"name": doctor.full_name, "university": doctor.university,
                                     "graduation_year": doctor.graduation_year}
    if treatment:
        facts["treatment"] = {"name": treatment.name, "stay_in_istanbul_days": treatment.stay_days,
                              "visits": treatment.visits, "pricing": "never published — personal quote via WhatsApp"}
    return facts


def _internal_links(lang, treatment=None):
    from apps.treatments.models import Treatment

    links = {}
    with translation.override(lang):
        links["contact / free consultation"] = reverse("core:contact")
        links["all treatments"] = reverse("treatments:list")
        links["price list"] = reverse("prices:index")
        for t in Treatment.objects.filter(is_active=True)[:12]:
            loc = t.localized(lang)
            links[f"treatment: {loc.name}"] = reverse("treatments:detail", kwargs={"slug": loc.slug})
        if treatment:
            loc = treatment.localized(lang)
            links[f"price comparison: {loc.name}"] = reverse("prices:detail", kwargs={"slug": loc.slug})
    return links


class ContentMachine:
    def _system(self):
        return WRITER_SYSTEM.format(site=settings.SITE_NAME)

    def _write(self, *, lang, brief, schema, facts, links, max_tokens=32000):
        meta = LANGUAGE_META[lang]
        blocks = [
            {"text": "FACTS (the only numbers you may use):\n" + json.dumps(facts, ensure_ascii=False, indent=1),
             "cache": True},
            {"text": f"LANGUAGE: {meta['name']} ({lang}). Markets: {', '.join(meta['markets'])}. "
                     f"Home-country name to use: {meta['compare_country']}. Turkey = '{meta['turkey']}', "
                     f"Istanbul = '{meta['istanbul']}'.\n\nINTERNAL LINKS:\n"
                     + "\n".join(f"- {k}: {v}" for k, v in links.items()) + f"\n\nTASK:\n{brief}"},
        ]
        return llm.generate_json(system=self._system(), blocks=blocks, schema=schema,
                                 effort=settings.GENERATION_EFFORT, max_tokens=max_tokens)

    # ── Blog ──────────────────────────────────────────────────────────────
    def generate_post(self, topic, lang="en", category=None, funnel_stage="awareness", treatment=None,
                      focus_keyword="", schema_type="BlogPosting"):
        category = category or BlogCategory.objects.filter(funnel_stage=funnel_stage).first() \
            or BlogCategory.objects.first()
        if category is None:
            raise ValueError("Önce en az bir BlogCategory oluşturun (seed_data komutu oluşturur).")
        brief = (f"Write a {1300 if funnel_stage != 'decision' else 1100}-1800 word blog article.\n"
                 f"Topic: {topic}\nFocus keyword (as searched in this language): {focus_keyword or 'choose the best one'}\n"
                 f"Funnel: {FUNNEL_BRIEF.get(funnel_stage, '')}")
        data = self._write(lang=lang, brief=brief, schema=POST_SCHEMA, facts=_facts(lang, treatment),
                           links=_internal_links(lang, treatment))
        slug = slugify(data["slug"] or data["title"], max_length=180)
        base, n = slug, 2
        while BlogPost.objects.filter(slug=slug).exists():
            slug, n = f"{base}-{n}", n + 1
        post = BlogPost.objects.create(
            title=data["title"][:200], slug=slug, category=category, treatment=treatment,
            content=data["content"], excerpt=data["excerpt"][:300], faq=data["faq"],
            meta_title=data["meta_title"][:70], meta_description=data["meta_description"][:170],
            focus_keyword=data["focus_keyword"][:120], featured_image_alt=data["featured_image_alt"][:200],
            funnel_stage=data.get("funnel_stage") or funnel_stage, target_personas=data.get("target_personas", []),
            schema_type=schema_type, source_language=lang, content_source=BlogPost.SOURCE_AI,
            ai_generation_prompt=topic, status=BlogPost.STATUS_REVIEW,
        )
        logger.info("generated post #%s [%s] %s", post.pk, lang, post.title)
        return post

    def generate_post_from_keyword(self, kw):
        funnel = kw.funnel_stage or {"informational": "awareness", "commercial": "consideration",
                                     "transactional": "decision"}.get(kw.intent, "awareness")
        try:
            post = self.generate_post(topic=kw.term, lang=kw.language, funnel_stage=funnel, treatment=kw.treatment,
                                      focus_keyword=kw.term)
        except llm.LLMError as e:
            logger.error("keyword %s generation failed: %s", kw, e)
            return None
        kw.blog_post = post
        kw.status = "planned"
        kw.page_type = "blog"
        kw.save(update_fields=["blog_post", "status", "page_type"])
        return post

    # ── Tedavi sayfası ────────────────────────────────────────────────────
    def generate_treatment_content(self, treatment, overwrite=False):
        if treatment.body and not overwrite:
            return treatment
        lang = treatment.source_language
        schema = {
            "type": "object",
            "properties": {
                "short_description": {"type": "string"}, "body": {"type": "string"},
                "faq": POST_SCHEMA["properties"]["faq"],
                "meta_title": {"type": "string"}, "meta_description": {"type": "string"},
                "focus_keyword": {"type": "string"},
            },
            "required": ["short_description", "body", "faq", "meta_title", "meta_description", "focus_keyword"],
            "additionalProperties": False,
        }
        brief = (f"Write the main service page for '{treatment.name}' in Istanbul (900-1400 words). Sections: what it "
                 "is and who it is for, the procedure step by step and timeline in Istanbul, materials/brands "
                 "(only from FACTS), cost in Istanbul vs home country (FACTS only), risks and aftercare, why patients "
                 "choose this clinic. short_description: 1-2 sentences (max 300 chars).")
        data = self._write(lang=lang, brief=brief, schema=schema, facts=_facts(lang, treatment),
                           links=_internal_links(lang, treatment))
        for f in schema["required"]:
            setattr(treatment, f, data[f])
        treatment.short_description = treatment.short_description[:400]
        treatment.meta_title = treatment.meta_title[:70]
        treatment.meta_description = treatment.meta_description[:170]
        treatment.save()
        return treatment

    # ── Programatik sayfa ─────────────────────────────────────────────────
    def generate_landing(self, page, overwrite=False):
        if page.generated_by_ai and page.body and not overwrite:
            return page
        lang = page.source_language
        t = page.treatment
        schema = {
            "type": "object",
            "properties": {
                "h1": {"type": "string"}, "intro": {"type": "string"}, "body": {"type": "string"},
                "faq": POST_SCHEMA["properties"]["faq"],
                "meta_title": {"type": "string"}, "meta_description": {"type": "string"},
                "focus_keyword": {"type": "string"},
            },
            "required": ["h1", "intro", "body", "faq", "meta_title", "meta_description", "focus_keyword"],
            "additionalProperties": False,
        }
        if page.page_type == "treatment_city":
            brief = (f"Landing page targeting '{t.name} {page.city.name}'. The template already renders a clinic list, "
                     "price table and reviews from data, so write: intro (80-120 words, keyword in first sentence), "
                     "body (500-800 words) covering why patients choose this city for this treatment, how the trip "
                     "works (arrival, appointments, recovery, sightseeing), how to choose a clinic there, and what "
                     "is included. FAQ 4-6 items specific to this treatment in this city.")
        else:
            brief = (f"Dental package page targeting '{t.name} package {LANGUAGE_META[lang]['turkey']}' (dental tourism "
                     "package). Core message: dental work is more than a Hollywood smile — every package is personalised "
                     "after a real diagnosis. Write: intro (80-120 words), body (500-800 words) covering what the package "
                     "includes (assessment, 3D scan, treatment, aftercare — the budget goes into the treatment plan, not extras; "
                     "more affordable options exist; never promise hotels, flights or transfers), how appointments are "
                     "planned around the trip, why fixed 'all inclusive' packages sold before seeing your teeth are risky, and how to get a "
                     "personal plan via WhatsApp. NO prices or amounts. FAQ 4-6 questions.")
        data = self._write(lang=lang, brief=brief, schema=schema, facts=_facts(lang, t), links=_internal_links(lang, t))
        for f in schema["required"]:
            setattr(page, f, data[f])
        page.h1 = page.h1[:200]
        page.meta_title = page.meta_title[:70]
        page.meta_description = page.meta_description[:170]
        page.generated_by_ai = True
        page.save()
        return page

    # ── Keyword genişletme ────────────────────────────────────────────────
    def expand_keywords(self, lang, treatment=None, count=40):
        meta = LANGUAGE_META[lang]
        schema = {
            "type": "object",
            "properties": {"keywords": {"type": "array", "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                    "intent": {"type": "string", "enum": ["informational", "commercial", "transactional",
                                                          "navigational"]},
                    "funnel_stage": {"type": "string", "enum": ["awareness", "consideration", "decision"]},
                    "persona_hint": {"type": "string", "enum": ["skeptic", "price", "premium", "quality", "ready", "fear",
                                                                "shame", "urgency", "trust", ""]},
                    "page_type": {"type": "string", "enum": ["treatment", "treatment_city", "treatment_price",
                                                             "blog", "home"]},
                    "priority": {"type": "integer"},
                },
                "required": ["term", "intent", "funnel_stage", "persona_hint", "page_type", "priority"],
                "additionalProperties": False}}},
            "required": ["keywords"], "additionalProperties": False,
        }
        subject = treatment.localized(lang).name if treatment else "dental treatment abroad"
        system = ("You are an international SEO keyword researcher specialising in medical/dental tourism to "
                  "Turkey. You know how real people in each market phrase their Google searches, including "
                  "colloquial terms, misspellings that are common, and question-style queries.")
        blocks = [{"text": f"Market language: {meta['name']} ({lang}); countries: {', '.join(meta['markets'])}.\n"
                           f"Subject: {subject} in {meta['turkey']} / {meta['istanbul']}.\n"
                           f"Return {count} distinct search queries people in these markets actually type, written "
                           "in that language, mixing head terms, long-tail, questions (how much/is it safe/reviews), "
                           "comparisons vs home country, and city-specific queries. priority 1-100 (business value "
                           "× likely volume). No brand names of other clinics."}]
        data = llm.generate_json(system=system, blocks=blocks, schema=schema, effort="medium", max_tokens=8000)
        return data["keywords"]
