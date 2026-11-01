from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language, gettext as _

from apps.blog.models import BlogPost
from apps.clinics.models import Review
from apps.core.seo import Seo, absolute, alternates_for, faq_schema, fill_proof, page_meta, reverse_in
from apps.localization.models import localize_list, with_translations
from apps.localization.resolve import language_slugs, resolve_slug

from .models import Treatment
from .services import offers_for, related_treatments


def treatment_list(request):
    lang = get_language()
    items = [{"loc": loc} for loc in localize_list(with_translations(Treatment.objects.filter(is_active=True), lang), lang)]
    _meta_treatments = page_meta("treatments", _("Dental Treatments in Istanbul 2026 — Implants, Veneers, Crowns"),
                           _("Implants, veneers, zirconia crowns, All-on-4, root canal and whitening in Istanbul — how "
                             "each works, how long you stay and who it suits. Free assessment."))
    seo = Seo(
        title=_meta_treatments[0],
        description=_meta_treatments[1],
        canonical=absolute(request.path),
        alternates=alternates_for("treatments:list"),
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Treatments"), request.path)],
        schema=[{
            "@context": "https://schema.org", "@type": "ItemList",
            "itemListElement": [{"@type": "ListItem", "position": i, "name": it["loc"].name,
                                 "url": absolute(it["loc"].object.get_absolute_url())}
                                for i, it in enumerate(items, 1)],
        }],
    )
    return render(request, "treatments/list.html", {"seo": seo, "items": items, "page_type": "treatments"})


def treatment_url(treatment, lang, slug=None):
    slug = slug or treatment.localized(lang).slug
    return reverse_in(lang, "treatments:detail", {"slug": slug})


def treatment_detail(request, slug):
    lang = get_language()
    res = resolve_slug(Treatment, lang, slug, Treatment.objects.filter(is_active=True))
    if res is None:
        raise Http404
    t = res.obj
    if res.redirect_to_lang:
        return redirect(treatment_url(t, lang), permanent=True)

    loc = t.localized(lang)
    slugs = language_slugs(t)
    alternates = {lg: absolute(reverse_in(lg, "treatments:detail", {"slug": s})) for lg, s in slugs.items()}
    canonical = alternates.get(lang) or alternates.get(t.source_language)

    offers = offers_for(t)

    from apps.localization.memo import memo

    def _city_pages():
        out = []
        for page in t.landing_pages.filter(page_type="treatment_city", is_active=True).select_related("city"):
            city_loc = page.city.localized(lang)
            out.append({"name": city_loc.name,
                        "url": reverse("treatments:city", kwargs={"slug": loc.slug, "city_slug": city_loc.slug})})
        return out
    city_pages = memo(f"city-pages:{t.pk}:{lang}", 300, _city_pages, model=Treatment)
    posts = memo(f"treatment-posts:{t.pk}:{lang}", 300,
                 lambda: localize_list(with_translations(BlogPost.published.filter(treatment=t)[:4], lang), lang, fallback=False),
                 model=BlogPost)
    from apps.clinics.models import light_reviews

    reviews = memo(f"treatment-reviews:{t.pk}:{lang}", 300,
                   lambda: list(light_reviews(Review.objects.filter(is_published=True, treatment=t).exclude(text=""), lang)[:6]),
                   model=Treatment)

    procedure = {
        "@context": "https://schema.org",
        "@type": "MedicalProcedure",
        "name": loc.name,
        "description": loc.short_description,
        "url": canonical,
        "procedureType": "https://schema.org/NoninvasiveProcedure" if t.category in ("cosmetic", "general")
        else "https://schema.org/SurgicalProcedure",
        "bodyLocation": t.body_location,
    }

    seo = Seo(
        title=fill_proof(loc.meta_title) or _("%(treatment)s in Istanbul — Procedure & Personal Plan") % {"treatment": loc.name},
        description=fill_proof(loc.meta_description) or loc.short_description,
        canonical=canonical,
        alternates=alternates,
        robots="noindex,follow" if loc.is_fallback else "index,follow,max-image-preview:large",
        image=t.image_src,
        image_alt=t.image_alt or loc.name,
        modified=t.updated_at.isoformat(),
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Treatments"), reverse("treatments:list")),
                     (loc.name, request.path)],
        schema=[s for s in [procedure, faq_schema(loc.faq)] if s],
    )
    from apps.clinics.models import Clinic
    from apps.seo.common import clinic_bundle

    clinic = Clinic.primary()
    bundle = clinic_bundle(clinic, lang) if clinic else {}
    return render(request, "treatments/detail.html", {
        "seo": seo, "t": loc, "offers": offers, "doctor": bundle.get("doctor"), "doctor_loc": bundle.get("doctor_loc"),
        "city_pages": city_pages, "posts": posts, "reviews": reviews,
        "related": related_treatments(t, lang), "page_type": "treatment",
        "package_url": reverse("packages:treatment", kwargs={"slug": loc.slug}),
    })
