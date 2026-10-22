"""Dile özel slug'dan nesne çözümleme + doğru URL'ye 301 yönlendirme."""
from django.conf import settings

from .models import LIVE_STATUSES


class Resolved:
    def __init__(self, obj, redirect_to_lang=None, is_fallback=False):
        self.obj = obj
        self.redirect_to_lang = redirect_to_lang  # bu dilde başka slug var → yönlendir
        self.is_fallback = is_fallback            # bu dilde içerik yok → kaynak dil gösteriliyor


def resolve_slug(model, lang, slug, base_qs=None):
    """
    1. lang dilindeki çeviri slug'ı → nesne
    2. kaynak dil slug'ı → nesne (lang'de çeviri varsa doğru slug'a yönlendir)
    3. başka bir dilin slug'ı → nesneyi bul, lang'deki doğru URL'ye yönlendir
    Sonuç (nesne + o dildeki çevirisi) süreç içi bellekte: aynı sayfa 5 dk boyunca DB'ye sorulmaz.
    """
    from .memo import memo

    qs_key = str(base_qs.query) if base_qs is not None else "all"
    return memo(f"resolve:{model._meta.label_lower}:{lang}:{slug}:{hash(qs_key)}", 300,
                lambda: _resolve_slug(model, lang, slug, base_qs), model=model)


def _resolve_slug(model, lang, slug, base_qs=None):
    qs = base_qs if base_qs is not None else model.objects.all()
    tr_model = model.translations.rel.related_model
    fk = model.translations.field.name

    tr = tr_model.objects.filter(language_code=lang, slug=slug, status__in=LIVE_STATUSES,
                                 **{f"{fk}__in": qs}).first()
    if tr:
        obj = getattr(tr, fk)
        obj.localized(lang)  # çeviri nesne üzerinde ezberlenir → memo ile birlikte saklanır (sonraki istekte 0 sorgu)
        return Resolved(obj)

    obj = qs.filter(slug=slug).first()
    if obj:
        if lang != obj.source_language and obj.get_translation(lang):
            return Resolved(obj, redirect_to_lang=lang)
        obj.localized(lang)
        return Resolved(obj, is_fallback=lang != obj.source_language)

    tr = tr_model.objects.filter(slug=slug, status__in=LIVE_STATUSES, **{f"{fk}__in": qs}).first()
    if tr:
        return Resolved(getattr(tr, fk), redirect_to_lang=lang)
    return None


def language_slugs(obj):
    """{lang: slug} — nesnenin yayında olduğu tüm diller (süreç içi bellek, 5 dk)."""
    from .memo import memo

    return memo(f"slugs:{obj._meta.label_lower}:{obj.pk}", 300, lambda: _language_slugs(obj), model=type(obj))


def _language_slugs(obj):
    out = {obj.source_language: obj.slug}
    # values_list: .only() FK sütununu erteliyor, Django her satır için ek SELECT yapıyordu (1 yerine 17 sorgu)
    for code, slug in obj.translations.filter(status__in=LIVE_STATUSES).values_list("language_code", "slug"):
        out[code] = slug
    return {c: out[c] for c, _ in settings.LANGUAGES if c in out}
