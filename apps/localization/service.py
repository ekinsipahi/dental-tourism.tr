"""
AI çeviri servisi.

  translate_object(obj, "de")   → tek dil
  sync_object(obj)              → eksik/eskimiş tüm dilleri kuyruğa atar
  translate_pending()           → DB'de bekleyen tüm işleri sırayla işler (cron / komut)
"""
import json
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from slugify import slugify

from dental_tourism.languages import LANGUAGE_META

from . import llm
from .models import LIVE_STATUSES, TranslationStatus
from .registry import get_spec

logger = logging.getLogger(__name__)

# Asla çevrilmeyecek özel isimler
GLOSSARY_KEEP = [
    "Dr. Devrim Sipahi", "Dr. Dt. Devrim Biriken Sipahi", "dentaltourism.tr", "drdevrim.com",
    "WhatsApp", "All-on-4", "All-on-6", "Şişli", "Osmanbey", "Nişantaşı", "Straumann", "Nobel Biocare",
    "Osstem", "E.max", "CE",
]

SYSTEM_PROMPT = """You are a senior medical localization specialist and native-level SEO copywriter for a dental tourism website in Istanbul, Turkey (dentaltourism.tr). Patients from many countries read this content before deciding to travel for dental treatment.

Your job: LOCALIZE the given content into the target language so that it reads as if it was originally written by a native-speaking dental professional for that market. Not a literal translation.

Rules:
- Use correct, natural dental/medical terminology that patients in the target market actually use and search for.
- Preserve the meaning and every factual claim exactly. Never invent statistics, guarantees, prices, certifications or medical claims that are not in the source.
- Keep prices for treatment in Istanbul exactly as given (they are in EUR). Do not convert them.
- Markdown: keep the same structure (headings, lists, tables, bold, links). Never change URLs. Do not add a top-level "# " heading; the page already has an H1.
- Keep these names unchanged: {glossary}.
- "slug" fields: lowercase, hyphen-separated, 3-8 words, in the target language, ASCII only (transliterate non-Latin scripts), containing the main keyword. No stop-word padding.
- "meta_title" fields: max 60 characters, include the primary keyword near the start. "meta_description" fields: 140-158 characters, compelling, include the keyword and a reason to click.
- "focus_keyword" fields: the phrase a native speaker in the target market would type into Google for this page (not a literal translation if locals search differently).
- Empty source fields stay empty strings.
- Return only the JSON object matching the schema."""


def _system():
    return SYSTEM_PROMPT.format(glossary=", ".join(GLOSSARY_KEEP))


def _language_brief(lang):
    meta = LANGUAGE_META[lang]
    return (f"Target language: {meta['name']} ({meta['native']}, code '{lang}'). "
            f"Primary markets: {', '.join(meta['markets'])}. "
            f"When the text compares to the reader's home country, use '{meta['compare_country']}'. "
            f"Local name for Turkey: '{meta['turkey']}', for Istanbul: '{meta['istanbul']}'.")


def _field_guide(spec):
    lines = []
    for f in spec.fields:
        hint = {"markdown": "Markdown body", "slug": "URL slug", "faq": "list of FAQ question/answer pairs",
                "keyword": "SEO keyword", "list": "list of short strings"}.get(f.kind, "plain text")
        extra = f" — {f.instructions}" if f.instructions else ""
        limit = f" (max {f.max_length} chars)" if f.max_length else ""
        lines.append(f"- {f.name}: {hint}{limit}{extra}")
    return "\n".join(lines)


def unique_slug(spec, obj, lang, base, exclude_pk=None):
    base = slugify(base or "", max_length=180, word_boundary=True) or "page"
    tr_model = spec.translation_model
    slug, n = base, 2
    while True:
        clash = tr_model.objects.filter(language_code=lang, slug=slug)
        if exclude_pk:
            clash = clash.exclude(pk=exclude_pk)
        parent_clash = spec.model.objects.filter(source_language=lang, slug=slug).exclude(pk=obj.pk) \
            if hasattr(spec.model, "slug") else spec.model.objects.none()
        if not clash.exists() and not parent_clash.exists():
            return slug
        slug, n = f"{base}-{n}", n + 1


def translate_object(obj, lang, force=False) -> str:
    """Bir nesneyi tek bir dile çevirir. Dönüş: 'translated' | 'up_to_date' | 'outdated' | 'skipped' | 'failed'"""
    spec = get_spec(obj)
    if spec is None:
        raise ValueError(f"{type(obj).__name__} çevrilebilir olarak kayıtlı değil.")
    if lang == obj.source_language:
        return "skipped"

    tr_model = spec.translation_model
    source_hash = obj.compute_source_hash()
    tr = tr_model.objects.filter(**{spec.parent_fk: obj, "language_code": lang}).first()

    if tr and not force:
        if tr.source_hash == source_hash and tr.status in LIVE_STATUSES:
            return "up_to_date"
        if tr.status == TranslationStatus.REVIEWED:
            # İnsan düzeltmesini ezme → işaretle
            tr.status = TranslationStatus.OUTDATED
            tr.save(update_fields=["status", "updated_at"])
            return "outdated"

    source = {f.name: obj.source_payload().get(f.name) for f in spec.fields}
    source_json = json.dumps(source, ensure_ascii=False, indent=1, default=str)
    blocks = [
        {"text": f"Content type: {spec.content_kind}\nSource language: {obj.source_language}\n\n"
                 f"Fields:\n{_field_guide(spec)}\n\nSOURCE CONTENT (JSON):\n{source_json}", "cache": True},
        {"text": _language_brief(lang) + "\n" + (spec.extra_context(obj, lang) or "")},
    ]
    try:
        data = llm.generate_json(system=_system(), blocks=blocks, schema=spec.json_schema(),
                                 effort=settings.TRANSLATION_EFFORT)
    except llm.LLMError as e:
        logger.error("translate %s#%s -> %s failed: %s", type(obj).__name__, obj.pk, lang, e)
        if tr is None:
            tr = tr_model(**{spec.parent_fk: obj, "language_code": lang})
            for f in spec.fields:
                setattr(tr, f.name, source.get(f.name) or ([] if f.kind in ("faq", "list") else ""))
            if spec.field("slug"):
                tr.slug = unique_slug(spec, obj, lang, f"{source.get('slug') or obj.pk}-{lang}")
        tr.status = TranslationStatus.FAILED
        tr.error = str(e)[:2000]
        tr.save()
        return "failed"

    with transaction.atomic():
        tr = tr or tr_model(**{spec.parent_fk: obj, "language_code": lang})
        for f in spec.fields:
            value = data.get(f.name)
            if f.kind == "slug":
                if tr.pk and tr.slug:
                    value = tr.slug  # Yayındaki URL asla değişmez (SEO) — gerekirse admin'den elle değiştirin
                else:
                    value = unique_slug(spec, obj, lang, value or data.get("title") or data.get("name"),
                                        exclude_pk=tr.pk)
            elif f.max_length and isinstance(value, str):
                value = value[: f.max_length]
            setattr(tr, f.name, value if value is not None else "")
        tr.status = TranslationStatus.MACHINE
        tr.source_hash = source_hash
        tr.model_used = settings.CONTENT_MACHINE_MODEL
        tr.translated_at = timezone.now()
        tr.error = ""
        tr.save()
    logger.info("translated %s#%s -> %s", type(obj).__name__, obj.pk, lang)
    return "translated"


def languages_needing_work(obj) -> list:
    """Eksik, başarısız veya kaynağı değişmiş (ve insan onaylı olmayan) diller."""
    spec = get_spec(obj)
    current = obj.compute_source_hash()
    rows = {t.language_code: t for t in obj.translations.all()}
    out = []
    for lang in spec.target_languages(obj):
        tr = rows.get(lang)
        if tr is None or tr.status in (TranslationStatus.PENDING, TranslationStatus.FAILED):
            out.append(lang)
        elif tr.source_hash != current and tr.status == TranslationStatus.MACHINE:
            out.append(lang)
        elif tr.source_hash != current and tr.status == TranslationStatus.REVIEWED:
            tr.status = TranslationStatus.OUTDATED
            tr.save(update_fields=["status", "updated_at"])
    return out


def translate_all(obj, languages=None, force=False) -> dict:
    spec = get_spec(obj)
    langs = languages or (spec.target_languages(obj) if force else languages_needing_work(obj))
    return {lang: translate_object(obj, lang, force=force) for lang in langs}


def sync_object(obj, force=False):
    """Kaydetme sonrası çağrılır: gereken dilleri arka planda çevirir."""
    from .dispatch import dispatch_translation

    spec = get_spec(obj)
    if spec is None or not llm.is_configured():
        return []
    for dep in spec.dependencies(obj):
        dep_spec = get_spec(dep)
        if dep_spec and languages_needing_work(dep):
            dispatch_translation(dep._meta.label_lower, dep.pk, languages_needing_work(dep))
    langs = spec.target_languages(obj) if force else languages_needing_work(obj)
    if langs:
        dispatch_translation(obj._meta.label_lower, obj.pk, langs, force=force)
    return langs
