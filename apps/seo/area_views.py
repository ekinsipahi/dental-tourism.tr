"""Semt sayfaları — "dental clinic şişli / dentist taksim / zahnarzt nişantaşı" (programatik yerel SEO, 17 dil, fiyatsız)."""
from urllib.parse import quote

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import get_language, gettext as _

from apps.core.seo import Seo, absolute, clinic_schema, faq_schema, proof, reverse_in
from apps.localization.models import localize_list, with_translations
from apps.treatments.models import Treatment

from . import area_data as A
from .common import pseo_context

LANGS = [c for c, _n in settings.LANGUAGES]


def _num(x):
    return f"{x:g}"


def _area_links(lang, exclude=None):
    return [{"key": k, "name": A.area_name(k, lang), "km": _num(A.area_km(k)),
             "url": reverse("areas:detail", kwargs={"area": k})} for k in A.ordered_keys() if k != exclude]


def _treatment_links(lang):
    qs = with_translations(Treatment.objects.filter(is_active=True).defer("body", "faq", "short_description"), lang,
                           tr_defer=("body", "faq", "short_description"))
    return [{"name": loc.name, "icon": getattr(loc, "icon", ""), "url": reverse("treatments:detail", kwargs={"slug": loc.slug})}
            for loc in localize_list(qs, lang)]


def _routes(key):
    """Ulaşım satırları (çevrilmiş): metro hatları, yürüme, taksi, havalimanı."""
    a = A.AREAS[key]
    lines = []
    if a["metro"]:
        legs = " · ".join(f"{line} {frm} → {to}" for line, frm, to in a["metro"])
        label = _("Metro")
        lines.append(f"{label}: {legs}")
    walk = A.walk_minutes(key)
    if walk:
        lines.append(_("On foot: about %(min)s minutes") % {"min": walk})
    lines.append(_("By taxi: about %(min)s minutes, depending on traffic") % {"min": A.taxi_minutes(key)})
    return lines


def _directions_url(key, clinic):
    origin = quote(f"{A.AREAS[key]['name']}, İstanbul")
    dest = f"{clinic.latitude},{clinic.longitude}" if clinic and clinic.latitude else quote("Abide-i Hürriyet Cd 148, Şişli")
    return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}"


def _faq(key, name, routes):
    return [
        {"question": _("How do I get to the clinic from %(area)s?") % {"area": name},
         "answer": " ".join(r.rstrip(".") + "." for r in routes) + " " +
         _("Nearest metro station: Şişli-Mecidiyeköy (M2, M7), about %(km)s km from the clinic.") % {"km": _num(A.station_km())}},
        {"question": _("Is the clinic open at weekends?"),
         "answer": _("Yes. Our clinic in Şişli is open 7 days a week, including Saturday and Sunday.")},
        {"question": _("Do you treat expats and visitors staying in Istanbul?"),
         "answer": _("Yes. Many of our patients are expats or visitors staying in Istanbul. Send a photo or an X-ray on "
                     "WhatsApp and the dentist will reply with your options.")},
        {"question": _("How much does treatment cost?"),
         "answer": _("Send your photos or X-ray on WhatsApp. After the dentist has reviewed your case you receive "
                     "a personal plan with a fixed written quote — we never publish one-size-fits-all prices.")},
    ]


def area_detail(request, area):
    if area not in A.AREAS:
        raise Http404
    lang = get_language()
    a = A.AREAS[area]
    name = A.area_name(area, lang)
    km = _num(A.area_km(area))
    near = a["kind"] == "near"
    alternates = {lg: absolute(reverse_in(lg, "areas:detail", {"area": area})) for lg in LANGS}
    if near:
        h1 = _("Dental clinic near %(area)s, Istanbul") % {"area": name}
        title = _("Dentist near %(area)s ★%(rating)s — Family Clinic, Open 7 Days") % {"area": name, **proof()}
        desc = _("Dentist near %(area)s: our family clinic in Şişli is %(km)s km away, open 7 days. 35+ years' "
                 "experience, ★ %(rating)s on Google. Free WhatsApp assessment.") % {"area": name, "km": km, **proof()}
        lead = _("Our family dental clinic in Şişli is about %(km)s km from %(area)s. Dr. Devrim "
                 "and her son Dt. Ekin Sipahi examine and treat every patient personally.") % {"area": name, "km": km}
    else:
        h1 = _("Dental clinic in %(area)s, Istanbul") % {"area": name}
        title = _("Dentist in %(area)s ★%(rating)s — Family Clinic, Open 7 Days") % {"area": name, **proof()}
        desc = _("Family dental clinic in %(area)s, Istanbul: 35+ years' experience, ★ %(rating)s on Google, open 7 "
                 "days a week. Free assessment on WhatsApp.") % {"area": name, **proof()}
        lead = _("Our family dental clinic is in %(area)s, Istanbul. Dr. Devrim and her son "
                 "Dt. Ekin Sipahi examine and treat every patient personally.") % {"area": name}
    routes = _routes(area)
    faq = _faq(area, name, routes)
    hub_url = reverse("areas:index")
    ctx = pseo_context(request, offset=a["order"], show_cases=True, photos=9)
    clinic = ctx.get("clinic")
    if len(ctx.get("gallery") or []) > 3:
        ctx["inline_photo"] = ctx["gallery"].pop()
    seo = Seo(
        title=title, description=desc,
        canonical=alternates.get(lang) or absolute(request.path), alternates=alternates,
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Dental clinic by district"), hub_url), (name, request.path)],
        schema=[s for s in [faq_schema(faq), clinic_schema(clinic) if clinic else None] if s],
    )
    ctx.update({
        "seo": seo, "h1": h1, "lead": lead, "eyebrow": _("Dental clinic by district"),
        "area_name": name, "area_key": area, "near": near, "km": km, "taxi": A.taxi_minutes(area), "routes": routes,
        "station_km": _num(A.station_km()), "places": ", ".join(a["places"]),
        "directions_url": _directions_url(area, clinic), "faq": faq,
        "treatments": _treatment_links(lang), "areas": _area_links(lang, exclude=area), "hub_url": hub_url,
        "keywords": A.keywords_for(lang, area), "page_type": "area",
    })
    return render(request, "areas/detail.html", ctx)


def area_index(request):
    lang = get_language()
    alternates = {lg: absolute(reverse_in(lg, "areas:index")) for lg in LANGS}
    h1 = _("Dental clinic near you in Istanbul: Şişli, Nişantaşı, Taksim, Levent and more")
    seo = Seo(
        title=_("Dentist near Şişli, Nişantaşı, Taksim & Levent ★%(rating)s") % proof(),
        description=_("Family dental clinic in Şişli, Istanbul: 35+ years, ★ %(rating)s on Google, open 7 days. Distance "
                      "and route from Nişantaşı, Taksim, Beşiktaş, Levent and more.") % proof(),
        canonical=alternates.get(lang) or absolute(request.path), alternates=alternates,
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Dental clinic by district"), request.path)],
    )
    ctx = pseo_context(request, offset=0, show_cases=True)
    clinic = ctx.get("clinic")
    if clinic and (s := clinic_schema(clinic)):
        seo.schema = [s]
    ctx.update({
        "seo": seo, "h1": h1, "eyebrow": _("Dental clinic by district"),
        "lead": _("Our family dental clinic is in Şişli, close to Nişantaşı, Mecidiyeköy and the M2 metro line. "
                  "Choose your district to see the distance and the easiest way to reach us."),
        "areas": _area_links(lang), "station_km": _num(A.station_km()),
        "treatments": _treatment_links(lang), "page_type": "area_hub",
    })
    return render(request, "areas/index.html", ctx)
