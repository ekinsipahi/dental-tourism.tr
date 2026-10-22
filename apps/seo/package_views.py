"""Diş turizmi paket sayfaları (programatik SEO, 17 dil, fiyatsız)."""
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language, gettext as _


from apps.clinics.models import Review, light_reviews
from apps.core.seo import Seo, absolute, alternates_for, clinic_schema, faq_schema, page_meta, reverse_in
from apps.localization.models import localize_list, with_translations
from apps.localization.resolve import language_slugs, resolve_slug
from apps.treatments.models import Treatment
from apps.treatments.services import offers_for, related_treatments

from . import package_data as P
from .common import pseo_context
from .models import LandingPage


def _hub_faq():
    return [
        {"question": _("What is dental tourism?"),
         "answer": _("Dental tourism means travelling to another country for dental treatment — usually to combine "
                     "experienced dentists, modern clinics and significantly lower costs with a short trip.")},
        {"question": _("What is included in a dental tourism package?"),
         "answer": _("A personal assessment, 3D scan and examination in Istanbul, the treatment itself and aftercare "
                     "via WhatsApp when you are back home. Instead of bundling extras, we put your budget into your "
                     "treatment plan — and more affordable options are available too.")},
        {"question": _("Why is a personalised package better value?"),
         "answer": _("Because you pay for your treatment, not for extras. Your budget goes into the dentist's time, "
                     "quality materials and a result that lasts — and more affordable options are available too. "
                     "Ask us on WhatsApp.")},
        {"question": _("How much does a dental package cost?"),
         "answer": _("We do not sell fixed-price packages, because no two mouths are the same. Send photos or an "
                     "X-ray on WhatsApp and you receive a personal treatment plan with a fixed written quote.")},
        {"question": _("Is an all-inclusive Hollywood smile package a good idea?"),
         "answer": _("Only if you actually need it. Packages that sell 20 veneers before anyone has examined your "
                     "teeth often remove healthy tooth structure. A real plan starts with a diagnosis.")},
        {"question": _("How long does a dental trip to Turkey take?"),
         "answer": _("Most treatments take 3–7 days in Istanbul. Implants usually need two short visits a few "
                     "months apart; we plan both around your flights.")},
    ]


def _cards(lang):
    out = []
    for loc in localize_list(with_translations(Treatment.objects.filter(is_active=True).defer("body", "faq"), lang,
                                               tr_defer=("body", "faq")), lang):
        out.append({"t": loc, "url": reverse("packages:treatment", kwargs={"slug": loc.slug})})
    return out


def _origin_links(lang):
    return [{"code": c, "name": P.country_name(c, lang),
             "url": reverse("origins:detail", kwargs={"country": P.country_slug(c, lang)})}
            for c in P.origin_codes(lang)]


def package_index(request):
    lang = get_language()
    faq = _hub_faq()
    title, desc = page_meta(
        "packages", _("Dental Holiday Packages Istanbul 2026 — Planned on Your X-ray"),
        _("No one-size-fits-all deal: your dental package in Istanbul is planned from your photos or X-ray, with a "
          "fixed written quote and aftercare at home."))
    seo = Seo(
        title=title, description=desc, canonical=absolute(request.path), alternates=alternates_for("packages:index"),
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Dental packages"), request.path)],
        schema=[s for s in [faq_schema(faq), {
            "@context": "https://schema.org", "@type": "ItemList", "name": title,
            "itemListElement": [{"@type": "ListItem", "position": i, "url": absolute(c["url"]), "name": c["t"].name}
                                for i, c in enumerate(_cards(lang), 1)]}] if s],
    )
    ctx = pseo_context(request, offset=1, show_cases=True)
    ctx.update({
        "seo": seo, "cards": _cards(lang), "origins": _origin_links(lang), "faq": faq,
        "h1": _("Dental tourism packages in Istanbul — personalised, not one-size-fits-all"),
        "lead": _("Dental work is more than a Hollywood smile. Your package is built around a real diagnosis — "
                  "and your budget goes into your treatment, not into extras."),
        "eyebrow": _("Dental packages"), "compare_url": _guide_url("best-country-dental-tourism"),
        "keywords": P.keywords_for(lang, "hub"), "page_type": "packages",
    })
    return render(request, "packages/index.html", ctx)


def package_treatment(request, slug):
    lang = get_language()
    res = resolve_slug(Treatment, lang, slug, Treatment.objects.filter(is_active=True))
    if res is None:
        raise Http404
    t = res.obj
    loc = t.localized(lang)
    if res.redirect_to_lang:
        return redirect(reverse("packages:treatment", kwargs={"slug": loc.slug}), permanent=True)
    page = LandingPage.objects.filter(page_type=LandingPage.TYPE_TREATMENT_PRICE, treatment=t, is_active=True).first()
    p_loc = page.localized(lang) if page else None
    slugs = language_slugs(t)
    alternates = {lg: absolute(reverse_in(lg, "packages:treatment", {"slug": s})) for lg, s in slugs.items()}
    offers = offers_for(t)
    h1 = _("%(treatment)s package in Istanbul") % {"treatment": loc.name}
    faq = (p_loc.faq if p_loc and not p_loc.is_fallback and p_loc.faq else None) or loc.faq or _hub_faq()
    seo = Seo(
        title=_("%(treatment)s Package Istanbul — Planned on Your X-ray") % {"treatment": loc.name},
        description=_("%(treatment)s package in Istanbul: examination, treatment and aftercare planned around your case "
                      "and travel dates. Fixed written quote, free WhatsApp assessment.") % {"treatment": loc.name},
        canonical=alternates.get(lang) or absolute(request.path),
        alternates={} if loc.is_fallback else alternates,
        robots="noindex,follow" if loc.is_fallback else "index,follow,max-image-preview:large",
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Dental packages"), reverse("packages:index")),
                     (h1, request.path)],
        schema=[s for s in [faq_schema(faq)] + [clinic_schema(o.clinic) for o in offers[:3]] if s],
    )
    ctx = pseo_context(request, offset=t.pk, show_cases=t.slug in CASE_TREATMENTS)
    if loc.image_src:
        ctx["hero_photo"] = {"src": loc.image_src, "alt": loc.image_alt or loc.name}
    ctx.update({
        "seo": seo, "t": loc, "h1": h1, "lead": loc.short_description, "eyebrow": _("Dental packages"),
        "page": p_loc if p_loc and not p_loc.is_fallback else None, "faq": faq,
        "offers": offers, "treatment_url": reverse("treatments:detail", kwargs={"slug": loc.slug}),
        "price_url": reverse("prices:detail", kwargs={"slug": loc.slug}),
        "reviews": light_reviews(Review.objects.filter(is_published=True, treatment=t).exclude(text=""), lang)[:6],
        "related": related_treatments(t, lang), "origins": _origin_links(lang),
        "keywords": P.keywords_for(lang, "treatment", loc.name), "page_type": "package_treatment",
    })
    return render(request, "packages/treatment.html", ctx)


def package_origin(request, country):
    lang = get_language()
    code = P.code_from_slug(country, lang)
    if code is None:
        raise Http404
    info = P.ORIGINS[code]
    name = P.country_name(code, lang)
    alternates = {lg: absolute(reverse_in(lg, "origins:detail", {"country": P.country_slug(code, lg)}))
                  for lg in P.langs_for_origin(code)}
    h1 = _("Dental holiday packages from %(country)s to Istanbul") % {"country": name}
    from apps.clinics.models import Clinic

    reviews = Review.objects.filter(is_published=True, country_code=code, clinic__in=Clinic.objects.published()) \
        .exclude(text="")[:6]
    seo = Seo(
        title=_("%(country)s to Istanbul for Dental Treatment — 2026 Guide") % {"country": name},
        description=_("Travelling from %(country)s for dental treatment? Flight time, how many trips you need, what a "
                      "fair package includes and how aftercare works at home.") % {"country": name},
        canonical=alternates.get(lang) or absolute(request.path),
        alternates=alternates,
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Dental packages"), reverse("packages:index")),
                     (name, request.path)],
        schema=[faq_schema(_origin_faq(name, info))],
    )
    ctx = pseo_context(request, offset=len(code) + ord(code[0]))
    ctx.update({
        "seo": seo, "h1": h1, "country": name, "code": code, "info": info, "cards": _cards(lang),
        "lead": _("Planning dental treatment in Istanbul from %(country)s? Flight times, how many trips you need "
                  "and what a personalised dental package includes.") % {"country": name},
        "eyebrow": _("Dental packages"), "cities": info["cities"][:4],
        "faq": _origin_faq(name, info), "reviews": reviews, "origins": _origin_links(lang),
        "keywords": P.keywords_for(lang, "origin", country=name, cities=info["cities"]),
        "page_type": "package_origin",
    })
    return render(request, "packages/origin.html", ctx)


def _origin_faq(name, info):
    trips = (_("We plan treatment to keep the number of trips to a minimum — often one longer stay, with "
               "implants scheduled so that the second visit is short.") if info.get("long_haul") else
             _("Crowns, veneers and most other treatments need one trip of about a week; implants usually need "
               "two short trips a few months apart."))
    return [
        {"question": _("How long is the flight from %(country)s to Istanbul?") % {"country": name},
         "answer": _("About %(hours)s hours, depending on your departure airport and connection.") %
         {"hours": f"{info['hours']:g}"}},
        {"question": _("How many trips will I need from %(country)s?") % {"country": name}, "answer": trips},
        {"question": _("What happens when I am back in %(country)s?") % {"country": name},
         "answer": _("Follow-up continues on WhatsApp and email. If needed we coordinate with a local dentist and "
                     "guide you by video call — you are never left alone.")},
        {"question": _("How do I get a price for my dental package?"),
         "answer": _("Send your photos or X-ray on WhatsApp. After the dentist has reviewed your case you receive "
                     "a personal plan with a fixed written quote — we never publish one-size-fits-all prices.")},
    ]


CASE_TREATMENTS = {"composite-veneers", "hollywood-smile", "porcelain-veneers", "teeth-whitening"}


def _guide_url(key):
    from .models import SeoTopic

    topic = SeoTopic.objects.filter(key=key, is_active=True).first()
    return topic.get_absolute_url() if topic else ""
