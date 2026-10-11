from django.core.paginator import Paginator
from django.db.models import F
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language, gettext as _

from apps.core.seo import page_meta, Seo, absolute, alternates_for, faq_schema, organization_schema, reverse_in
from apps.localization.models import LIVE_STATUSES, localize_list, with_translations
from apps.localization.resolve import language_slugs, resolve_slug

from .models import BlogCategory, BlogPost, RelatedPost

PER_PAGE = 12


def _posts_in_language(qs, lang):
    """Sadece o dilde okunabilir (kaynak dili o dil veya canlı çevirisi olan) yazılar."""
    from django.db.models import Q

    return qs.filter(Q(source_language=lang) | Q(translations__language_code=lang,
                                                    translations__status__in=LIVE_STATUSES)).distinct()


def _categories(lang):
    cats = BlogCategory.objects.filter(posts__status=BlogPost.STATUS_PUBLISHED).distinct()
    return localize_list(with_translations(cats, lang), lang)


def blog_list(request):
    lang = get_language()
    qs = _posts_in_language(BlogPost.published.all(), lang)
    page = Paginator(with_translations(qs, lang), PER_PAGE).get_page(request.GET.get("page"))
    posts = localize_list(page.object_list, lang, fallback=False)
    canonical = absolute(request.path + (f"?page={page.number}" if page.number > 1 else ""))
    _meta_blog = page_meta("blog", _("Dental Tourism Blog — Guides, Costs & Patient Advice"),
                           _("Honest guides about dental treatment in Turkey: implant and veneer costs, safety, "
                      "recovery and how to choose a dentist in Istanbul."))
    seo = Seo(
        title=_meta_blog[0],
        description=_meta_blog[1],
        canonical=canonical,
        alternates=alternates_for("blog:post_list") if page.number == 1 else {},
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Blog"), request.path)],
    )
    return render(request, "blog/list.html", {"seo": seo, "posts": posts, "page_obj": page,
                                              "categories": _categories(lang), "page_type": "blog_list"})


def _category_or_redirect(lang, category_slug):
    res = resolve_slug(BlogCategory, lang, category_slug)
    if res is None:
        raise Http404
    return res


def blog_category(request, category_slug):
    lang = get_language()
    res = _category_or_redirect(lang, category_slug)
    cat = res.obj
    loc = cat.localized(lang)
    if res.redirect_to_lang:
        return redirect(cat.get_absolute_url(lang), permanent=True)
    qs = _posts_in_language(BlogPost.published.filter(category=cat), lang)
    page = Paginator(with_translations(qs, lang), PER_PAGE).get_page(request.GET.get("page"))
    posts = localize_list(page.object_list, lang, fallback=False)
    slugs = language_slugs(cat)
    alternates = {lg: absolute(reverse_in(lg, "blog:category", {"category_slug": s})) for lg, s in slugs.items()}
    seo = Seo(
        title=loc.meta_title or _("%(category)s — Dental Tourism Blog") % {"category": loc.name},
        description=loc.meta_description or loc.description,
        canonical=alternates.get(lang, absolute(request.path)),
        alternates=alternates if page.number == 1 else {},
        robots="noindex,follow" if (loc.is_fallback or not posts) else "index,follow",
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Blog"), reverse("blog:post_list")),
                     (loc.name, request.path)],
    )
    return render(request, "blog/category.html", {"seo": seo, "category": loc, "posts": posts, "page_obj": page,
                                                  "categories": _categories(lang), "page_type": "blog_category"})


def blog_detail(request, category_slug, post_slug):
    lang = get_language()
    res = resolve_slug(BlogPost, lang, post_slug, BlogPost.published.all())
    if res is None:
        raise Http404
    post = res.obj
    loc = post.localized(lang)
    correct_url = post.get_absolute_url(lang)
    # Yanlış dil slug'ı / kategori slug'ı → tek doğru URL'ye 301
    if res.redirect_to_lang or (not loc.is_fallback and request.path != correct_url):
        return redirect(correct_url, permanent=True)
    if loc.is_fallback:
        # Bu dilde çeviri yok: kaynak dildeki yazıya yönlendir (duplicate içerik üretme)
        return redirect(post.get_absolute_url(post.source_language), permanent=False)

    cat_loc = post.category.localized(lang)
    alternates = {lg: absolute(post.get_absolute_url(lg)) for lg in post.live_languages()}
    canonical = post.canonical_url or alternates.get(lang)

    related_ids = list(RelatedPost.objects.filter(post=post).values_list("related_post_id", flat=True)[:6])
    related_qs = BlogPost.published.filter(pk__in=related_ids) if related_ids else \
        BlogPost.published.filter(category=post.category).exclude(pk=post.pk)
    related = localize_list(with_translations(_posts_in_language(related_qs, lang)[:4], lang), lang, fallback=False)

    author = None
    if post.reviewed_by:
        author = {"@type": "Person", "name": post.reviewed_by.full_name,
                  "url": absolute(post.reviewed_by.get_absolute_url())}
    article = {
        "@context": "https://schema.org",
        "@type": post.schema_type,
        "headline": loc.title[:110],
        "description": loc.meta_description or loc.excerpt,
        "inLanguage": lang,
        "mainEntityOfPage": canonical,
        "datePublished": post.published_at.isoformat() if post.published_at else None,
        "dateModified": post.updated_at.isoformat(),
        "author": author or {"@id": absolute("/#organization")},
        "publisher": organization_schema(),
        "image": absolute(post.image_src) if post.image_src else None,
        "keywords": loc.focus_keyword or None,
        "wordCount": len((loc.content or "").split()),
    }
    if post.reviewed_by:
        article["reviewedBy"] = author
    if post.schema_type == "MedicalWebPage":
        article["lastReviewed"] = post.updated_at.date().isoformat()

    seo = Seo(
        title=loc.meta_title or loc.title,
        description=loc.meta_description or loc.excerpt,
        canonical=canonical,
        alternates=alternates,
        og_type="article",
        robots="noindex,follow" if post.noindex else "index,follow,max-image-preview:large",
        image=post.image_src,
        image_alt=loc.featured_image_alt or loc.title,
        published=post.published_at.isoformat() if post.published_at else "",
        modified=post.updated_at.isoformat(),
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Blog"), reverse("blog:post_list")),
                     (cat_loc.name, post.category.get_absolute_url(lang)), (loc.title, request.path)],
        schema=[s for s in [{k: v for k, v in article.items() if v is not None}, faq_schema(loc.faq)] if s],
    )
    if not getattr(request, "is_bot", False):
        BlogPost.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)

    treatment = post.treatment.localized(lang) if post.treatment else None
    return render(request, "blog/detail.html", {
        "seo": seo, "post": post, "p": loc, "category": cat_loc, "related": related, "treatment": treatment,
        "reviewer": post.reviewed_by.localized(lang) if post.reviewed_by else None,
        "page_type": "blog_detail", "funnel_stage": post.funnel_stage,
    })
