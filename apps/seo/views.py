"""Programatik SEO sayfaları: tedavi × şehir ve tedavi fiyat karşılaştırma."""
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language, gettext as _

from apps.clinics.models import City, Review
from apps.core.seo import page_meta, Seo, absolute, clinic_schema, faq_schema, reverse_in
from apps.localization.models import localize_list, with_translations
from apps.localization.resolve import language_slugs, resolve_slug
from apps.treatments.models import Treatment
from apps.treatments.services import offers_for, related_treatments

from .models import LandingPage


def _treatment(lang, slug):
    res = resolve_slug(Treatment, lang, slug, Treatment.objects.filter(is_active=True))
    if res is None:
        raise Http404
    return res


def _page(page_type, treatment, city=None):
    return LandingPage.objects.filter(page_type=page_type, treatment=treatment, city=city, is_active=True).first()


def treatment_city(request, slug, city_slug):
    lang = get_language()
    res = _treatment(lang, slug)
    t = res.obj
    city_res = resolve_slug(City, lang, city_slug, City.objects.filter(is_active=True))
    if city_res is None:
        raise Http404
    city = city_res.obj
    t_loc, c_loc = t.localized(lang), city.localized(lang)
    if res.redirect_to_lang or city_res.redirect_to_lang:
        return redirect(reverse("treatments:city", kwargs={"slug": t_loc.slug, "city_slug": c_loc.slug}),
                        permanent=True)

    offers = offers_for(t, city)
    page = _page(LandingPage.TYPE_TREATMENT_CITY, t, city)
    p_loc = page.localized(lang) if page else None
    indexable = bool(page and offers and not page.noindex and p_loc and not p_loc.is_fallback
                     and not t_loc.is_fallback)

    # hreflang: sadece hem tedavinin hem sayfanın o dilde yayında olduğu diller
    alternates = {}
    if page:
        t_slugs, c_slugs = language_slugs(t), language_slugs(city)
        for lg in page.live_languages():
            if lg in t_slugs:
                alternates[lg] = absolute(reverse_in(lg, "treatments:city",
                                                     {"slug": t_slugs[lg], "city_slug": c_slugs.get(lg, city.slug)}))
    canonical = alternates.get(lang) or absolute(request.path)

    h1 = (p_loc.h1 if p_loc else None) or _("%(treatment)s in %(city)s") % {"treatment": t_loc.name, "city": c_loc.name}
    faq = (p_loc.faq if p_loc else None) or t_loc.faq
    clinics = [o.clinic for o in offers]

    seo = Seo(
        title=(p_loc.meta_title if p_loc else "") or _("%(treatment)s in %(city)s — Personal Plan") % {"treatment": t_loc.name, "city": c_loc.name},
        description=(p_loc.meta_description if p_loc else "") or _(
            "Compare %(treatment)s in %(city)s: affordable personal quotes, stay duration, dentist experience and patient "
            "reviews. Free consultation on WhatsApp.") % {"treatment": t_loc.name, "city": c_loc.name},
        canonical=canonical,
        alternates=alternates if indexable else {},
        robots="index,follow,max-image-preview:large" if indexable else "noindex,follow",
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Treatments"), reverse("treatments:list")),
                     (t_loc.name, reverse("treatments:detail", kwargs={"slug": t_loc.slug})), (c_loc.name, request.path)],
        schema=[s for s in [faq_schema(faq)] + [clinic_schema(c) for c in clinics[:5]] if s],
    )
    return render(request, "seo/treatment_city.html", {
        "seo": seo, "t": t_loc, "city": c_loc, "page": p_loc, "h1": h1, "faq": faq, "offers": offers,
        "reviews": Review.objects.filter(is_published=True, clinic__in=clinics).exclude(text="")[:6],
        "related": related_treatments(t, lang), "page_type": "treatment_city",
        "package_url": reverse("packages:treatment", kwargs={"slug": t_loc.slug}),
    })


def _price_faq():
    return [
        {"question": _("How much does dental treatment in Turkey cost?"),
         "answer": _("Dental treatment in Turkey is very affordable compared with Western Europe, the UK or the Gulf. "
                     "The exact cost depends on your teeth, so we give you a personal, fixed quote after the dentist "
                     "has seen your photos or X-ray — call us or send them on WhatsApp.")},
        {"question": _("Why don't you publish a price list?"),
         "answer": _("Because a price list sells the same treatment to everyone. Two patients asking for 'implants' "
                     "may need completely different plans. We prefer to tell you your real price.")},
        {"question": _("Are cheap dental clinics in Turkey a risk?"),
         "answer": _("A very low price often means cheaper materials, no diagnosis or unnecessary treatment. Ask "
                     "for material brands, the dentist's name and a written plan — quality and affordability can "
                     "go together.")},
        {"question": _("Is the quote fixed?"),
         "answer": _("Yes. What we agree in writing before treatment is what you pay — no hidden costs.")},
    ]


def price_index(request):
    from .common import pseo_context

    lang = get_language()
    cards = [{"loc": loc, "url": reverse("prices:detail", kwargs={"slug": loc.slug})}
             for loc in localize_list(with_translations(Treatment.objects.filter(is_active=True), lang), lang)]
    from apps.core.seo import alternates_for

    title, desc = page_meta(
        "prices", _("Dental Prices in Turkey 2026 — What Really Decides the Cost"),
        _("Why one price list can't fit every mouth, what a fair quote includes and how to get a fixed written price "
          "from the dentist — free on WhatsApp."))
    faq = _price_faq()
    seo = Seo(title=title, description=desc, canonical=absolute(request.path), alternates=alternates_for("prices:index"),
              breadcrumbs=[(_("Home"), reverse("core:home")), (_("Prices"), request.path)],
              schema=[faq_schema(faq)])
    ctx = pseo_context(request, offset=2)
    ctx.update({"seo": seo, "cards": cards, "faq": faq, "eyebrow": _("Prices"),
                "h1": _("Dental prices in Turkey: affordable — and personal"),
                "lead": _("How much do teeth cost in Turkey? Very affordable compared with home — but the honest "
                          "answer is a personal quote, not a price list."),
                "page_type": "price_index"})
    return render(request, "seo/price_index.html", ctx)


def treatment_price(request, slug):
    from .common import pseo_context

    lang = get_language()
    res = _treatment(lang, slug)
    t = res.obj
    t_loc = t.localized(lang)
    if res.redirect_to_lang:
        return redirect(reverse("prices:detail", kwargs={"slug": t_loc.slug}), permanent=True)
    t_slugs = language_slugs(t)
    alternates = {lg: absolute(reverse_in(lg, "prices:detail", {"slug": s})) for lg, s in t_slugs.items()}
    indexable = not t_loc.is_fallback
    h1 = _("%(treatment)s cost in Turkey — affordable, with a fixed quote") % {"treatment": t_loc.name}
    faq = (t_loc.faq or []) + _price_faq()[2:]
    seo = Seo(
        title=_("%(treatment)s Cost in Turkey 2026 — Fixed Written Quote") % {"treatment": t_loc.name},
        description=_("%(treatment)s in Istanbul: what decides the cost, what a fair quote includes and how to get a "
                      "fixed written quote from the dentist — free on WhatsApp.") % {"treatment": t_loc.name},
        canonical=alternates.get(lang) or absolute(request.path),
        alternates=alternates if indexable else {},
        robots="index,follow" if indexable else "noindex,follow",
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Prices"), reverse("prices:index")), (t_loc.name, request.path)],
        schema=[s for s in [faq_schema(faq)] if s],
    )
    ctx = pseo_context(request, offset=t.pk + 3, show_cases=t.slug in {"composite-veneers", "hollywood-smile",
                                                                        "porcelain-veneers", "teeth-whitening"})
    if t_loc.image_src:
        ctx["hero_photo"] = {"src": t_loc.image_src, "alt": t_loc.image_alt or t_loc.name}
    ctx.update({
        "seo": seo, "t": t_loc, "h1": h1, "faq": faq, "eyebrow": _("Prices"),
        "lead": _("What affects the price of %(treatment)s, what is included — and how to get your personal quote "
                  "by phone or WhatsApp.") % {"treatment": t_loc.name},
        "treatment_url": reverse("treatments:detail", kwargs={"slug": t_loc.slug}),
        "package_url": reverse("packages:treatment", kwargs={"slug": t_loc.slug}),
        "related": related_treatments(t, lang), "page_type": "treatment_price",
    })
    return render(request, "seo/treatment_price.html", ctx)
