"""
Çok dilli içerik için ortak soyut modeller.

Desen:
  - Ana model (ör. BlogPost, Treatment) `TranslatableModel`'den türer ve
    içeriğin KAYNAK dilindeki metnini kendi alanlarında tutar (source_language).
  - Her ana modelin bir `<Model>Translation` modeli vardır (`BaseTranslation`'dan türer),
    `related_name="translations"` ile bağlanır ve aynı metin alanlarını taşır.
  - `obj.localized(lang)` → o dilde içerik (yoksa kaynak dile fallback) döner.
  - Çeviriler AI ile otomatik üretilir (apps.localization.service), insan
    düzeltirse status=reviewed olur ve kaynak değişse bile üzerine yazılmaz
    (outdated olarak işaretlenir).
"""
import hashlib
import json

from django.conf import settings
from django.db import models
from django.db.models import Prefetch
from django.utils.translation import get_language


class TranslationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    MACHINE = "machine", "AI translated"
    REVIEWED = "reviewed", "Human reviewed"
    OUTDATED = "outdated", "Outdated (source changed)"
    FAILED = "failed", "Failed"


LIVE_STATUSES = (TranslationStatus.MACHINE, TranslationStatus.REVIEWED, TranslationStatus.OUTDATED)


class BaseTranslation(models.Model):
    language_code = models.CharField(max_length=10, choices=settings.LANGUAGES, db_index=True)
    status = models.CharField(max_length=12, choices=TranslationStatus.choices,
                              default=TranslationStatus.PENDING, db_index=True)
    source_hash = models.CharField(max_length=64, blank=True, editable=False)
    model_used = models.CharField(max_length=60, blank=True, editable=False)
    translated_at = models.DateTimeField(null=True, blank=True, editable=False)
    error = models.TextField(blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def is_live(self):
        return self.status in LIVE_STATUSES


class Localized:
    """Bir nesnenin belirli dildeki görünümü.

    Önce çeviri satırına, sonra ana nesneye bakar — şablonda `loc.title`,
    `loc.icon` gibi her iki modelden alanlar şeffafça okunabilir.
    """

    def __init__(self, obj, translation, lang, is_fallback):
        self._obj = obj
        self._tr = translation
        self.lang = lang
        self.is_fallback = is_fallback
        self.object = obj

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if self._tr is not None and name in self._obj.TRANSLATED_FIELDS:
            value = getattr(self._tr, name, None)
            if value not in (None, "", [], {}):
                return value
        return getattr(self._obj, name)

    def __str__(self):
        return str(getattr(self, "name", None) or getattr(self, "title", None) or self._obj)


class TranslatableModel(models.Model):
    """Kaynak dilde içerik tutan ana modeller için mixin."""

    #: Hem ana modelde hem çeviri modelinde bulunan metin alanları
    TRANSLATED_FIELDS: tuple = ()

    source_language = models.CharField(max_length=10, choices=settings.LANGUAGES,
                                       default=settings.LANGUAGE_CODE,
                                       help_text="İçeriği hangi dilde yazdınız? Diğer dillere bundan çevrilir.")
    auto_translate = models.BooleanField(default=True,
                                         help_text="Kaydedince / yayınlanınca diğer tüm dillere AI ile çevir.")

    class Meta:
        abstract = True

    # ── Kaynak metin ──────────────────────────────────────────────────────
    def source_payload(self) -> dict:
        return {f: getattr(self, f) for f in self.TRANSLATED_FIELDS}

    def compute_source_hash(self) -> str:
        raw = json.dumps(self.source_payload(), sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    # ── Çeviri erişimi ────────────────────────────────────────────────────
    def get_translation(self, lang, live_only=True):
        # with_translations() ile o dil için (sadece canlı satırlar) prefetch edildiyse DB'ye gitme
        if live_only and getattr(self, "_prefetched_lang", None) == lang and hasattr(self, "_prefetched_tr"):
            return self._prefetched_tr[0] if self._prefetched_tr else None
        qs = self.translations.filter(language_code=lang)
        if live_only:
            qs = qs.filter(status__in=LIVE_STATUSES)
        return qs.first()

    def has_language(self, lang) -> bool:
        return lang == self.source_language or self.get_translation(lang) is not None

    def localized(self, lang=None, fallback=True):
        lang = lang or get_language() or settings.LANGUAGE_CODE
        if lang == self.source_language:
            return Localized(self, None, lang, False)
        tr = self.get_translation(lang)
        if tr is not None:
            return Localized(self, tr, lang, False)
        if not fallback:
            return None
        return Localized(self, None, self.source_language, True)

    def live_languages(self) -> list:
        langs = set(self.translations.filter(status__in=LIVE_STATUSES).values_list("language_code", flat=True))
        langs.add(self.source_language)
        return [c for c, _ in settings.LANGUAGES if c in langs]

    def translation_coverage(self) -> dict:
        rows = dict(self.translations.values_list("language_code", "status"))
        total = len(settings.LANGUAGES)
        done = sum(1 for c, _ in settings.LANGUAGES
                   if c == self.source_language or rows.get(c) in LIVE_STATUSES)
        return {"total": total, "done": done, "statuses": rows}


def with_translations(queryset, lang=None):
    """Liste sayfalarında N+1 sorgu olmaması için o dildeki çevirileri prefetch eder."""
    lang = lang or get_language() or settings.LANGUAGE_CODE
    tr_model = queryset.model.translations.rel.related_model
    return queryset.prefetch_related(
        Prefetch("translations",
                 queryset=tr_model.objects.filter(language_code=lang, status__in=LIVE_STATUSES),
                 to_attr="_prefetched_tr")
    )


def localize_list(objects, lang=None, fallback=True):
    """Nesneleri o dile çevirir. with_translations() ile kullanın."""
    lang = lang or get_language() or settings.LANGUAGE_CODE
    out = []
    for obj in objects:
        if hasattr(obj, "_prefetched_tr"):
            obj._prefetched_lang = lang
        loc = obj.localized(lang, fallback=fallback)
        if loc is not None:
            out.append(loc)
    return out
