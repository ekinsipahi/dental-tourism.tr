"""Konu (rehber) sayfaları — /guide/<slug>/ , 17 dilde (SeoTopic)."""
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language, gettext as _

from apps.core.seo import Seo, absolute, alternates_for, faq_schema, fill_proof, page_meta, reverse_in
from apps.localization.models import localize_list, with_translations
from apps.localization.resolve import language_slugs, resolve_slug

from .common import pseo_context
from .models import SeoTopic


def _faq(loc):
    return [{"question": f.get("question") or f.get("q"), "answer": f.get("answer") or f.get("a")}
            for f in (loc.faq or []) if isinstance(f, dict)]


def _guide_links(lang, exclude=None):
    qs = with_translations(SeoTopic.objects.filter(is_active=True, noindex=False), lang)
    return [{"url": reverse("guides:detail", kwargs={"slug": loc.slug}), "h1": loc.h1, "key": loc.object.key,
             "lead": loc.lead}
            for loc in localize_list(qs, lang, fallback=False) if loc.object.pk != exclude]


def guide_index(request):
    lang = get_language()
    guides = _guide_links(lang)
    title, desc = page_meta("guides", _("Dental Tourism Guides 2026 — Turkey & Istanbul, by Dentists"),
                            _("Choosing a clinic, reviews, safety, travel, guarantee and aftercare — honest guides to "
                              "dental treatment in Turkey, written by dentists in Istanbul."))
    seo = Seo(title=title, description=desc, canonical=absolute(request.path), alternates=alternates_for("guides:index"),
              breadcrumbs=[(_("Home"), reverse("core:home")), (_("Guides"), request.path)],
              schema=[{"@context": "https://schema.org", "@type": "ItemList", "name": title,
                       "itemListElement": [{"@type": "ListItem", "position": i, "url": absolute(g["url"]), "name": g["h1"]}
                                           for i, g in enumerate(guides, 1)]}])
    ctx = pseo_context(request, offset=0)
    ctx.update({"seo": seo, "guides": guides, "h1": _("Dental tourism guides: Turkey and Istanbul"),
                "lead": _("Everything you need to decide with confidence — written by a dentist, without sales talk."),
                "page_type": "guides"})
    return render(request, "guides/index.html", ctx)


def guide_detail(request, slug):
    lang = get_language()
    res = resolve_slug(SeoTopic, lang, slug, SeoTopic.objects.filter(is_active=True))
    if res is None:
        raise Http404
    topic = res.obj
    loc = topic.localized(lang)
    if res.redirect_to_lang:
        return redirect(reverse("guides:detail", kwargs={"slug": loc.slug}), permanent=True)
    slugs = language_slugs(topic)
    alternates = {lg: absolute(reverse_in(lg, "guides:detail", {"slug": s})) for lg, s in slugs.items()}
    indexable = not loc.is_fallback and not topic.noindex
    faq = _faq(loc)
    ctx = pseo_context(request, offset=topic.order, show_cases=topic.show_cases)
    if topic.image_id:
        ctx["hero_photo"] = topic.image
    seo = Seo(
        title=fill_proof(loc.meta_title) or loc.h1, description=fill_proof(loc.meta_description) or loc.lead,
        canonical=alternates.get(lang) or absolute(request.path),
        alternates=alternates if indexable else {},
        robots="index,follow,max-image-preview:large" if indexable else "noindex,follow",
        image=absolute(ctx["hero_photo"].src) if ctx.get("hero_photo") else "",
        image_alt=ctx["hero_photo"].alt if ctx.get("hero_photo") else "",
        og_type="article",
        modified=topic.updated_at.isoformat() if topic.updated_at else "",
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Guides"), reverse("guides:index")), (loc.h1, request.path)],
        schema=[s for s in [faq_schema(faq), {
            "@context": "https://schema.org", "@type": "MedicalWebPage", "name": loc.h1, "about": loc.h1,
            "inLanguage": lang, "url": alternates.get(lang) or absolute(request.path),
            **({"reviewedBy": {"@type": "Person", "name": ctx["doctor"].name}} if ctx.get("doctor") else {}),
            **({"lastReviewed": topic.updated_at.date().isoformat()} if topic.updated_at else {}),
        }] if s],
    )
    from django.conf import settings

    ctx["partner_url"] = settings.PARTNER_AGENCY_URL if topic.key == "dental-tourism-agency" else ""
    if topic.key in ("dental-clinic-istanbul", "best-dental-clinic-istanbul", "istanbul-guide"):
        from .area_views import _area_links  # İstanbul rehberlerinden semt sayfalarına iç link

        ctx["areas"], ctx["areas_hub"] = _area_links(lang), reverse("areas:index")
    ctx.update({"seo": seo, "topic": topic, "t": loc, "h1": loc.h1, "lead": loc.lead, "faq": faq,
                "eyebrow": _("Guide"), "related_guides": _guide_links(lang, exclude=topic.pk)[:8],
                "page_type": f"guide_{topic.kind}"})
    return render(request, "guides/detail.html", ctx)
