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


@register.simple_tag
def mind_messages():
    """Persona motorunun teşhisine göre canlı mesajlar (components/mind_nudge.html).

    Hepsi sayfaya gömülür, yalnızca <html data-mind="…"> ile eşleşen görünür; ziyaretçi SSS açtıkça /
    gezdikçe tracker.js data-mind'i günceller (localStorage dt_mind) ve mesaj sayfa yenilenmeden değişir."""
    from django.utils.translation import gettext as _

    from apps.seo.common import persona_hook

    extra = {
        "quality": (_("A treatment planned for you — not a template"),
                    _("No one-size-fits-all packages: your plan is made only for you, after the dentist has examined your case."),
                    _("Get my personal treatment plan")),
        "skeptic": (_("Everything here is real"),
                    _("Real reviews with their source, named materials and a written plan before you travel."),
                    _("Ask any question — free")),
        "price": None, "premium": None, "fear": None, "shame": None, "trust": None, "urgency": None, "ready": None,
    }
    buttons = {"price": _("Get a free price quote"), "premium": _("Request a private appointment"),
               "fear": _("Ask any question — free"), "ready": _("Book now")}
    out = []
    for p, custom in extra.items():
        if custom:
            title, text, btn = custom
        else:
            title, text = persona_hook({"persona": p})
            btn = buttons.get(p, _("Ask a question"))
        out.append({"key": p, "title": title, "text": text, "button": btn, "reviews": p in ("skeptic", "trust")})
    return out


def core_faq(clinic=None):
    """Her sayfanın altındaki ORTAK SSS — her soru bir persona'ya etiketli (data-mind-q).

    Ziyaretçi hangisini açıp kaç saniye okuduysa persona motoru o yöne sayar
    ("Acıtır mı?" → korku, "Ne kadar tutar?" → fiyat, "Yorumlar gerçek mi?" → şüphe …)."""
    from django.utils.translation import gettext as _

    years = getattr(clinic, "years_experience", None)
    items = [
        ("skeptic", _("Is it safe to get dental treatment in Turkey?"),
         _("Yes, when you choose a licensed clinic with experienced dentists and certified materials. "
           "Ask for the dentist's credentials, the brands of implants and crowns, and a written "
           "treatment plan before you travel.")),
        ("price", _("How much does dental treatment in Istanbul cost?"),
         _("Very affordable compared with Western Europe — with the same materials and techniques. "
           "We do not publish one-size-fits-all prices: call us or send photos on WhatsApp and you "
           "receive a fixed written quote before treatment starts.")),
        ("fear", _("Does the treatment hurt?"),
         _("Treatment is done under local anaesthesia, so you feel pressure but not pain. The dentist explains "
           "each step before starting, and you can ask for a break at any time.")),
        ("quality", _("Will my treatment plan be made for me personally?"),
         _("Yes. We do not sell ready-made packages: the dentist examines your photos or X-ray, saves healthy "
           "teeth first and plans only what you actually need.")),
        ("skeptic", _("Are the reviews and photos on this site real?"),
         _("Yes. Our reviews are on Google with their source, and the photos show our own clinic, team and "
           "patients (shared with their consent).")),
        ("premium", _("Can I have a private, discreet appointment?"),
         _("Yes. Your appointments are planned around your schedule, and the same dentist looks after you from "
           "the first consultation to the final check.")),
        ("shame", _("Can I choose the shape and shade of my new teeth?"),
         _("Yes. With a digital smile design you see and approve the shape and shade before anything is made — "
           "we aim for a natural result that suits your face.")),
        ("urgency", _("How long do I need to stay in Istanbul?"),
         _("It depends on the treatment: fillings, cleaning and composite veneers take 1–3 days, "
           "crowns and porcelain veneers about 5–7 days, implants usually two visits a few months apart.")),
        ("trust", _("Do you speak my language?"),
         _("We communicate with international patients in English and other languages, and you can "
           "message the dentist directly on WhatsApp before, during and after your treatment.")),
    ]
    if years:
        items.append(("trust", _("How experienced is the dentist?"),
                      _("Our lead dentist has %(years)s years of clinical experience.") % {"years": years}))
    return [{"question": q, "answer": a, "mind": m} for m, q, a in items]


@register.simple_tag(takes_context=True)
def page_faq(context, faq=None, faq_title=None, wrap_class=None):
    """Sayfanın kendi SSS'sini kaydeder; base.html footer'dan önce {% faq_block %} ile tek yerde basar."""
    request = context.get("request")
    if request is not None:
        request._page_faq = (list(faq or []), faq_title, wrap_class)
    return ""


@register.simple_tag(takes_context=True)
def faq_block(context, faq=None, faq_title=None, wrap_class=None):
    """Sayfanın SSS'si + ortak SSS tek bölümde, sayfanın altında, her yerde aynı tasarım.

    Sayfa kendi SSS'sini basmadıysa base.html sonda yalnızca ortak SSS'yi basar (bir sayfada bir kez)."""
    from django.template.loader import render_to_string

    request = context.get("request")
    if request is not None:
        if getattr(request, "_faq_done", False):
            return ""
        request._faq_done = True
        if faq is None and getattr(request, "_page_faq", None):
            faq, faq_title, wrap_class = request._page_faq
    core = core_faq(context.get("clinic"))
    tags = {" ".join(str(c["question"]).lower().split()): c["mind"] for c in core}
    seen, items = set(), []
    for it in list(faq or []) + core:
        q = it.get("question") if isinstance(it, dict) else getattr(it, "question", "")
        a = it.get("answer") if isinstance(it, dict) else getattr(it, "answer", "")
        key = " ".join(str(q).lower().split())
        if not q or key in seen:
            continue
        seen.add(key)
        items.append({"question": q, "answer": a, "mind": tags.get(key, "")})
    # request=... VERİLMEZ: aksi halde tüm context processor'lar (site_context, persona) bu parça için yeniden çalışır
    return render_to_string("components/faq.html", {"faq": items, "faq_title": faq_title, "wrap_class": wrap_class})


def _results_cases(clinic, lang):
    """Önce/sonra vakaları (düz sözlükler) — dil başına 5 dk süreç içi bellekte: her sayfada 42 KB JSON + ~13 sorgu yerine 0."""
    from django.core.cache import caches

    from apps.localization.models import with_related_translations

    key = f"results:{clinic.pk}:{lang}"
    cases = caches["local"].get(key)
    if cases is not None:
        return cases
    qs = with_related_translations(clinic.cases.filter(is_published=True, patient_consent=True).select_related("treatment"),
                                   "treatment", lang).order_by("order", "pk")
    cases = []
    for c in qs:
        if not (c.before_src and c.after_src):
            continue
        title, caption = c.text_in(lang)
        tname = ""
        if c.treatment_id:
            try:
                tname = c.treatment.localized(lang).name
            except Exception:  # noqa: BLE001
                tname = c.treatment.name
        cases.append({"before": c.before_src, "after": c.after_src, "title": title, "caption": caption,
                      "treatment": tname, "treatment_url": c.treatment.get_absolute_url() if c.treatment_id else ""})
    caches["local"].set(key, cases, 300)
    return cases


@register.simple_tag(takes_context=True)
def results_block(context, limit=None):
    """Önce / sonra sonuçları — sürüklenebilir karşılaştırma kartları. Her sayfada bir kez:
    ana sayfada yorumların altında, diğer sayfalarda içeriğin sonunda (SSS'nin üstünde)."""
    from django.template.loader import render_to_string
    from django.utils.translation import get_language

    request = context.get("request")
    if request is not None:
        if getattr(request, "_results_done", False):
            return ""
        request._results_done = True
    clinic = context.get("clinic")
    if clinic is None:
        return ""
    lang = get_language()
    cases = _results_cases(clinic, lang)
    if limit:
        cases = cases[: int(limit)]
    if not cases:
        return ""
    return render_to_string("components/results.html", {"cases": cases, "wa_url": context.get("wa_url"),
                                                        "contact_email": context.get("contact_email"),
                                                        "clinic": clinic})  # request yok: bkz. faq_block


# Diş değiştiren tedaviler: önce kendi dişin kurtarılabilir mi? (konumlandırma: "save the natural tooth first")
SAVE_FIRST_KEYS = {"dental-implants", "all-on-4", "zirconia-crowns", "porcelain-veneers", "hollywood-smile"}


@register.inclusion_tag("components/save_first.html")
def save_first(t):
    """{% save_first t %} — implant / kron / lamina sayfalarında "önce dişinizi kurtaralım" kutusu."""
    from django.urls import NoReverseMatch, reverse
    from django.utils.translation import get_language

    key = getattr(t, "key", "")
    if key not in SAVE_FIRST_KEYS:
        return {"show": False}
    url = ""
    try:
        from apps.treatments.models import Treatment

        from apps.localization.memo import memo

        def load():
            rc = Treatment.objects.filter(key="root-canal", is_active=True).first()
            return reverse("treatments:detail", kwargs={"slug": rc.localized(get_language()).slug}) if rc else ""
        url = memo(f"root-canal-url:{get_language()}", 300, load, model=Treatment)
    except NoReverseMatch:
        url = ""
    return {"show": True, "root_canal_url": url}

