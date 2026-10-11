import re

import bleach
import markdown as md
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, gettext_lazy as _

from dental_tourism.languages import LANGUAGE_META

from apps.core.seo import localized_language_links

register = template.Library()

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p", "h2", "h3", "h4", "h5", "table", "thead", "tbody", "tr", "th", "td", "img", "hr", "br",
    "pre", "code", "span", "div", "figure", "figcaption", "sup", "sub", "details", "summary",
]
ALLOWED_ATTRS = {"*": ["id", "class"], "a": ["href", "title", "rel", "target"],
                 "img": ["src", "alt", "title", "width", "height", "loading"], "th": ["align"], "td": ["align"]}


@register.filter(name="markdown")
def render_markdown(text):
    """Markdown → güvenli HTML. İçerikteki H1'ler H2'ye düşürülür (sayfada tek H1 kuralı)."""
    if not text:
        return ""
    text = re.sub(r"^#(?!#)\s*", "## ", text, flags=re.M)
    html = md.markdown(text, extensions=["tables", "toc", "sane_lists", "attr_list"],
                       extension_configs={"toc": {"permalink": False}})
    html = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    html = html.replace("<img ", '<img loading="lazy" ')
    html = re.sub(r'<a href="(https?://(?!dentaltourism\.tr)[^"]+)"', r'<a href="\1" rel="noopener" target="_blank"', html)
    return mark_safe(html)


@register.filter
def toc(text):
    """Markdown'daki H2'lerden içindekiler listesi: [(id, başlık)]."""
    if not text:
        return []
    from markdown.extensions.toc import slugify as md_slug

    items = []
    for m in re.finditer(r"^##\s+(.+)$", text, flags=re.M):
        title = re.sub(r"[*_`]", "", m.group(1)).strip()
        items.append((md_slug(title, "-"), title))
    return items


@register.simple_tag(takes_context=True)
def language_links(context, seo=None):
    alternates = getattr(seo, "alternates", {}) if seo else {}
    return localized_language_links(alternates, get_language())


@register.filter
def money(value, currency="EUR"):
    if value in (None, ""):
        return ""
    symbol = {"EUR": "€", "GBP": "£", "USD": "$", "TRY": "₺", "PLN": "zł", "SEK": "kr", "DKK": "kr",
              "NOK": "kr", "AZN": "₼", "RON": "lei", "CHF": "CHF", "UAH": "₴"}.get(currency, currency)
    amount = f"{float(value):,.0f}".replace(",", " ")
    return f"{symbol}{amount}" if symbol in ("€", "£", "$", "₺") else f"{amount} {symbol}"


@register.filter
def stars(rating):
    try:
        n = int(round(float(rating)))
    except (TypeError, ValueError):
        return ""
    return "★" * n + "☆" * (5 - n)


@register.filter
def flag(country_code):
    """Ülke bayrağı GÖRSELİ (emoji bayraklar Windows'ta görünmez). static/img/flags/c/<cc>.png"""
    if not country_code or len(country_code) != 2:
        return ""
    from django.templatetags.static import static

    cc = country_code.lower()
    return mark_safe(f'<img class="flag" src="{static(f"img/flags/c/{cc}.png")}" alt="{cc.upper()}" '
                     f'width="20" height="14" loading="lazy">')


@register.simple_tag
def lang_flag(lang_code, size=20):
    """Dil bayrağı görseli: static/img/flags/<dil>.png (+@2x)."""
    from django.templatetags.static import static

    h = round(int(size) * 0.7)
    return mark_safe(f'<img class="flag" src="{static(f"img/flags/{lang_code}.png")}" '
                     f'srcset="{static(f"img/flags/{lang_code}@2x.png")} 2x" alt="" width="{size}" height="{h}">')


UNIT_LABELS = {
    "per tooth": _("per tooth"), "per implant": _("per implant"), "per crown": _("per crown"),
    "per arch": _("per arch"), "per jaw": _("per jaw"), "per session": _("per session"), "per smile": _("per smile"),
}


@register.filter
def unit_label(unit):
    return UNIT_LABELS.get((unit or "").strip().lower(), unit)


# ── Admin'den düzenlenebilir içerik blokları ─────────────────────────────────
def _block(key, lang):
    from django.core.cache import cache

    from apps.core.models import ContentBlock

    ck = f"cblock:{key}:{lang}"
    data = cache.get(ck)
    if data is None:
        block = ContentBlock.objects.filter(key=key, is_active=True).first()
        data = {}
        if block is not None:
            loc = block.localized(lang)
            # Bu dilde çeviri yoksa şablondaki (gettext ile çevrilmiş) varsayılan kullanılsın
            if not loc.is_fallback:
                data = {f: getattr(loc, f) for f in ContentBlock.TRANSLATED_FIELDS}
            data["button_url"] = block.button_url
            data["image"] = block.image.url if block.image else block.image_url
        cache.set(ck, data, 300)
    return data


@register.simple_tag
def cblock(key, field, default=""):
    """{% cblock "home-reviews" "title" _("Real patients, real results") %}"""
    value = _block(key, get_language()).get(field)
    return value if value else default


@register.simple_tag
def cblock_data(key):
    """{% cblock_data "home-faq" as b %} → b.items, b.title, b.image ..."""
    return _block(key, get_language())


@register.simple_tag
def review_text(review):
    """{% review_text r as rt %} → rt.text (ziyaretçinin dilinde), rt.translated, rt.original, rt.source_lang"""
    lang = get_language()
    text, translated = review.text_in(lang)
    src = LANGUAGE_META.get(review.language or "", {})
    return {"text": text, "translated": translated, "original": review.text,
            "source_lang": src.get("native", review.language or "")}
