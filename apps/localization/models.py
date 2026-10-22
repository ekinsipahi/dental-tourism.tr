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

    def _parent_model(self):
        for f in self._meta.fields:
            if f.many_to_one and issubclass(f.related_model, TranslatableModel):
                return f.related_model
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from .memo import bump

        parent = self._parent_model()
        if parent is not None:
            bump(parent)

    def delete(self, *args, **kwargs):
        from .memo import bump

        parent = self._parent_model()
        if parent is not None:
            bump(parent)
        return super().delete(*args, **kwargs)

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
    def _all_live(self):
        """with_all_translations() ile TÜM canlı çeviriler prefetch edildiyse {dil: çeviri}, yoksa None."""
        rows = getattr(self, "_all_tr_list", None)
        if rows is None:
            return None
        d = getattr(self, "_all_tr_map", None)
        if d is None:
            d = self._all_tr_map = {t.language_code: t for t in rows}
        return d

    def get_translation(self, lang, live_only=True):
        if live_only and (allmap := self._all_live()) is not None:
            return allmap.get(lang)
        # with_translations() / with_related_translations() ile o dil prefetch edildiyse DB'ye gitme
        pre = getattr(self, f"_prefetched_tr_{lang}", None) if live_only else None
        if pre is None and live_only and getattr(self, "_prefetched_lang", None) == lang and hasattr(self, "_prefetched_tr"):
            pre = self._prefetched_tr
        if pre is not None:
            return pre[0] if pre else None
        # Aynı nesne üzerinde tekrar tekrar .localized() çağrılır (şablonlar, get_absolute_url) → sonuç nesnede saklanır.
        # (Nesne ömrü genelde tek istektir; save()/refresh_from_db() bu belleği temizler.)
        memo = self.__dict__.setdefault("_tr_memo", {})
        key = (lang, live_only)
        if key not in memo:
            qs = self.translations.filter(language_code=lang)
            if live_only:
                qs = qs.filter(status__in=LIVE_STATUSES)
            memo[key] = qs.first()
        return memo[key]

    def save(self, *args, **kwargs):
        self.__dict__.pop("_tr_memo", None)
        super().save(*args, **kwargs)
        from .memo import bump

        bump(type(self))  # süreç içi memo girişleri (slug çözümü, listeler) bu model için geçersiz

    def delete(self, *args, **kwargs):
        from .memo import bump

        bump(type(self))
        return super().delete(*args, **kwargs)

    def refresh_from_db(self, *args, **kwargs):
        self.__dict__.pop("_tr_memo", None)
        super().refresh_from_db(*args, **kwargs)

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
        allmap = self._all_live()
        langs = set(allmap) if allmap is not None else set(
            self.translations.filter(status__in=LIVE_STATUSES).values_list("language_code", flat=True))
        langs.add(self.source_language)
        return [c for c, _ in settings.LANGUAGES if c in langs]

    def translation_coverage(self) -> dict:
        rows = dict(self.translations.values_list("language_code", "status"))
        total = len(settings.LANGUAGES)
        done = sum(1 for c, _ in settings.LANGUAGES
                   if c == self.source_language or rows.get(c) in LIVE_STATUSES)
        return {"total": total, "done": done, "statuses": rows}


def with_translations(queryset, lang=None, tr_defer=()):
    """Liste sayfalarında N+1 sorgu olmaması için o dildeki çevirileri prefetch eder (dile özel attr:
    _prefetched_tr_<dil> → localize_list çağrılmasa da obj.localized(lang) DB'ye gitmez).
    tr_defer: menü / kart gibi yalnızca ad-slug gereken yerlerde çevirinin ağır alanlarını (body, faq) çekme."""
    lang = lang or get_language() or settings.LANGUAGE_CODE
    tr_model = queryset.model.translations.rel.related_model
    tr_qs = tr_model.objects.filter(language_code=lang, status__in=LIVE_STATUSES)
    if tr_defer:
        tr_qs = tr_qs.defer(*tr_defer)
    return queryset.prefetch_related(Prefetch("translations", queryset=tr_qs, to_attr=f"_prefetched_tr_{lang}"))


def with_related_translations(queryset, path, lang=None):
    """İlişkili çevrilebilir nesnenin (ör. review.treatment, case.treatment) o dildeki çevirisini de tek sorguda
    yükler: şablondaki r.treatment.localized.name / get_absolute_url() döngüde N sorgu üretmez."""
    lang = lang or get_language() or settings.LANGUAGE_CODE
    model = queryset.model._meta.get_field(path).related_model
    tr_model = model.translations.rel.related_model
    return queryset.prefetch_related(
        Prefetch(f"{path}__translations",
                 queryset=tr_model.objects.filter(language_code=lang, status__in=LIVE_STATUSES),
                 to_attr=f"_prefetched_tr_{lang}")
    )


def with_all_translations(queryset, *paths, fields=()):
    """Sitemap gibi her nesnenin TÜM dillerini gezen yerler için: tüm canlı çeviriler tek sorguda.
    paths: ilişkili çevrilebilir nesneler de (ör. "treatment", "city") aynı şekilde yüklenir.
    fields: çeviri satırından yalnızca bu sütunlar (ör. sitemap için language_code, status, slug) — 2 MB → birkaç KB."""
    def _prefetch(path, model):
        tr_model = model.translations.rel.related_model
        lookup = f"{path}__translations" if path else "translations"
        tr_qs = tr_model.objects.filter(status__in=LIVE_STATUSES)
        if fields:  # sitemap: yalnızca slug/dil gerekir; FK sütunu eşleştirme için şart (ertelenirse satır başına SELECT)
            names = {f.name for f in tr_model._meta.concrete_fields}
            tr_qs = tr_qs.only("id", model.translations.rel.field.attname, *[f for f in fields if f in names])
        return Prefetch(lookup, queryset=tr_qs, to_attr="_all_tr_list")

    lookups = [_prefetch("", queryset.model)]
    for path in paths:
        lookups.append(_prefetch(path, queryset.model._meta.get_field(path).related_model))
    return queryset.prefetch_related(*lookups)


def localize_list(objects, lang=None, fallback=True):
    """Nesneleri o dile çevirir. with_translations() ile kullanın."""
    lang = lang or get_language() or settings.LANGUAGE_CODE
    out = []
    for obj in objects:
        if hasattr(obj, "_prefetched_tr"):  # eski attr adıyla prefetch edilmiş nesneler
            obj._prefetched_lang = lang
        loc = obj.localized(lang, fallback=fallback)
        if loc is not None:
            out.append(loc)
    return out
