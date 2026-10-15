"""Her şablona enjekte edilen global context: ana klinik, dil meta, WhatsApp linki, menü."""
import urllib.parse

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language, gettext as _

from dental_tourism.languages import LANGUAGE_META


def _nav_treatments(lang):
    key = f"nav:treatments:{lang}"
    items = cache.get(key)
    if items is None:
        from apps.localization.models import localize_list, with_translations
        from apps.treatments.models import Treatment

        qs = with_translations(Treatment.objects.filter(is_active=True, is_featured=True), lang)
        items = [{"name": loc.name, "url": loc.object.get_absolute_url(), "icon": loc.icon}
                 for loc in localize_list(qs, lang)]
        cache.set(key, items, 300)
    return items


def _nav_menu(lang):
    """Navbar mega menü + footer iç linkleri (dile göre cache'li)."""
    key = f"nav:menu:{lang}"
    data = cache.get(key)
    if data is not None:
        return data
    from django.urls import reverse

    from apps.localization.models import localize_list, with_translations
    from apps.seo import package_data as P
    from apps.seo.models import SeoTopic
    from apps.treatments.models import Treatment

    treatments = []
    for loc in localize_list(with_translations(Treatment.objects.filter(is_active=True), lang), lang):
        treatments.append({"name": loc.name, "icon": loc.icon, "url": loc.object.get_absolute_url(),
                           "package_url": reverse("packages:treatment", kwargs={"slug": loc.slug}),
                           "price_url": reverse("prices:detail", kwargs={"slug": loc.slug})})
    groups = {"choose": [], "places": [], "practical": []}
    kind_group = {"pillar": "choose", "general": "choose", "trust": "choose", "compare": "choose",
                  "gallery": "choose", "location": "places", "guide": "practical", "service": "practical",
                  "b2b": "practical"}
    topics = with_translations(SeoTopic.objects.filter(is_active=True, noindex=False), lang)
    for loc in localize_list(topics, lang, fallback=False):
        groups[kind_group.get(loc.object.kind, "practical")].append(
            {"name": loc.h1.split(" — ")[0].split("? ")[0][:70], "url": reverse("guides:detail", kwargs={"slug": loc.slug}),
             "key": loc.object.key})
    origins = [{"code": c, "name": P.country_name(c, lang),
                "url": reverse("origins:detail", kwargs={"country": P.country_slug(c, lang)})}
               for c in P.origin_codes(lang)]
    data = {"treatments": treatments, "guides": groups, "origins": origins,
            "gallery_url": next((g["url"] for g in groups["choose"] if g["key"] == "smile-gallery"), "")}
    cache.set(key, data, 600)
    return data


def build_wa_message(request, lang, clinic=None):
    """Dile + persona'ya özel ön-doldurulmuş WhatsApp mesajı (hekim bağlamı görür)."""
    persona = (getattr(request, "persona", None) or {}).get("persona", "")
    persona_ctx = {
        "fear": _("I have some questions about safety and the treatment process."),
        "price": _("I would like to get a price quote."),
        "urgency": _("I would like to ask about available appointments this week."),
        "shame": _("I would like information about smile design."),
        "premium": _("I would like to request a private appointment."),
        "quality": _("I would like a personalised treatment plan."),
        "ready": _("I would like to book an appointment."),
        "skeptic": _("I would like information about materials and certificates."),
        "trust": _("I would like to learn more."),
    }
    text = _("Hello, I would like a free consultation.")
    if persona in persona_ctx:
        text += " " + str(persona_ctx[persona])
    tracking = getattr(request, "tracking_session", None)
    src = getattr(tracking, "traffic_source", "") if tracking else ""
    tag = {"google_ads": "G-Ads", "meta_ads": "Meta", "google_organic": "Google"}.get(src)
    page = request.path.strip("/").split("/")[-1][:40]
    ref = " · ".join(filter(None, [tag, page]))
    if ref:
        text += f" [{ref}]"
    return urllib.parse.quote(text)


def site_context(request):
    from apps.clinics.models import Clinic

    lang = get_language() or settings.LANGUAGE_CODE
    meta = LANGUAGE_META.get(lang, LANGUAGE_META[settings.LANGUAGE_CODE])
    try:
        clinic = Clinic.primary()
    except Exception:  # noqa: BLE001 — migrate öncesi
        clinic = None
    whatsapp = clinic.whatsapp if clinic else ""
    wa_url = f"https://wa.me/{whatsapp}?text={build_wa_message(request, lang, clinic)}" if whatsapp else ""
    # Normal telefon aramalarına cevap verilemiyor → aramalar WhatsApp üzerinden (sesli/görüntülü)
    wa_call_url = (f"https://wa.me/{whatsapp}?text="
                   + urllib.parse.quote(str(_("Hello, I would like to talk to you on a WhatsApp call.")))) if whatsapp else ""

    try:
        nav_treatments = _nav_treatments(lang)
        nav = _nav_menu(lang)
    except Exception:  # noqa: BLE001
        nav_treatments, nav = [], {}

    from .models import SiteSettings

    try:
        site_settings = SiteSettings.load()
    except Exception:  # noqa: BLE001
        site_settings = None

    return {
        "site_settings": site_settings,
        "site_name": settings.SITE_NAME,
        "site_url": settings.SITE_URL,
        "lang_code": lang,
        "lang_meta": meta,
        "lang_dir": meta["dir"],
        "clinic": clinic,
        "wa_url": wa_url,
        "wa_call_url": wa_call_url,
        "nav_treatments": nav_treatments,
        "nav": nav,
        "is_bot": getattr(request, "is_bot", False),
        "persona_ui": settings.PERSONA_UI_ENABLED,
        "analytics": {
            "gtag": settings.GOOGLE_GTAG_ID,
            "ads": settings.GOOGLE_ADS_CONVERSION,
            "meta_pixel": settings.META_PIXEL_ID,
            "google_verification": settings.GOOGLE_SITE_VERIFICATION,
            "bing_verification": settings.BING_SITE_VERIFICATION,
        },
        "suggested_language": _suggested_language(request, lang),
    }


def _suggested_language(request, current):
    """Tarayıcı dili farklı ve destekleniyorsa küçük bir öneri bandı (otomatik yönlendirme YOK — SEO için)."""
    if getattr(request, "is_bot", False) or request.COOKIES.get("lang_hint_closed"):
        return None
    header = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if not header:
        return None
    first = header.split(",")[0].split(";")[0].strip().lower()[:2]
    if first == "nb" or first == "nn":
        first = "no"
    if first and first != current and first in LANGUAGE_META:
        return {"code": first, **LANGUAGE_META[first]}
    return None
