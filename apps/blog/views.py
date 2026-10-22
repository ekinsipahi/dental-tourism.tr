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
    from apps.localization.memo import memo

    def load():
        cats = BlogCategory.objects.filter(posts__status=BlogPost.STATUS_PUBLISHED).distinct()
        return localize_list(with_translations(cats, lang), lang)
    return memo(f"blog-categories:{lang}", 300, load, model=BlogCategory)


def _post_page(qs, lang, number, key):
    """Sayfalanmış yazı listesi — (liste, sayfa no) başına 5 dk süreç içi bellekte; yalnızca o sayfanın yazıları saklanır."""
    from apps.localization.memo import memo

    number = str(number) if number is not None and str(number).isdigit() else "1"
    number = str(min(int(number), 999))

    def load():
        paginator = Paginator(with_translations(qs, lang), PER_PAGE)
        page = paginator.get_page(number)
        posts = localize_list(page.object_list, lang, fallback=False)
        page.object_list = posts
        paginator.object_list = posts  # sayfa sayısı hesaplandı (count önbellekte); tüm liste belleğe alınmaz
        return page, posts
    return memo(f"{key}:{number}", 300, load, model=BlogPost)


def _post_extras(post, lang):
    """Yazı sayfasının yardımcı verisi (URL'ler, kategori, hreflang, ilgili yazılar, hekim, tedavi) — (yazı, dil)
    başına 5 dk süreç içi bellekte: 17 dilin hreflang'ı için her istekte onlarca çeviri sorgusu atılmaz."""
    from apps.localization.memo import memo

    def load():
        related_ids = list(RelatedPost.objects.filter(post=post).values_list("related_post_id", flat=True)[:6])
        related_qs = BlogPost.published.filter(pk__in=related_ids) if related_ids else \
            BlogPost.published.filter(category=post.category).exclude(pk=post.pk)
        reviewer = post.reviewed_by
        return {
            "url": post.get_absolute_url(lang),
            "source_url": post.get_absolute_url(post.source_language),
            "cat_loc": post.category.localized(lang),
            "cat_url": post.category.get_absolute_url(lang),
            "alternates": {lg: absolute(post.get_absolute_url(lg)) for lg in post.live_languages()},
            "related": localize_list(with_translations(_posts_in_language(related_qs, lang)[:4], lang), lang, fallback=False),
            "reviewer": reviewer.localized(lang) if reviewer else None,
            "reviewer_url": absolute(reviewer.get_absolute_url()) if reviewer else "",
            "treatment": post.treatment.localized(lang) if post.treatment else None,
        }
    return memo(f"post-extras:{post.pk}:{lang}", 300, load, model=BlogPost)


def blog_list(request):
    lang = get_language()
    qs = _posts_in_language(BlogPost.published.all(), lang)
    page, posts = _post_page(qs, lang, request.GET.get("page"), f"blog-list:{lang}")
    canonical = absolute(request.path + (f"?page={page.number}" if page.number > 1 else ""))
    _meta_blog = page_meta("blog", _("Dental Tourism Blog 2026 — Honest Advice from Dentists"),
                           _("Implant and veneer costs, safety, recovery and choosing a dentist in Istanbul — practical, "
                             "honest advice from dentists with 35+ years' experience."))
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
    page, posts = _post_page(qs, lang, request.GET.get("page"), f"blog-cat:{cat.pk}:{lang}")
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
    extras = _post_extras(post, lang)  # URL'ler, kategori, hreflang, ilgili yazılar, hekim, tedavi — bellekten
    correct_url = extras["url"]
    # Yanlış dil slug'ı / kategori slug'ı → tek doğru URL'ye 301
    if res.redirect_to_lang or (not loc.is_fallback and request.path != correct_url):
        return redirect(correct_url, permanent=True)
    if loc.is_fallback:
        # Bu dilde çeviri yok: kaynak dildeki yazıya yönlendir (duplicate içerik üretme)
        return redirect(extras["source_url"], permanent=False)

    cat_loc, alternates = extras["cat_loc"], extras["alternates"]
    canonical = post.canonical_url or alternates.get(lang)
    related = extras["related"]

    author = None
    reviewer = extras["reviewer"]
    if reviewer:
        author = {"@type": "Person", "name": reviewer.full_name, "url": extras["reviewer_url"]}
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
    if reviewer:
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
                     (cat_loc.name, extras["cat_url"]), (loc.title, request.path)],
        schema=[s for s in [{k: v for k, v in article.items() if v is not None}, faq_schema(loc.faq)] if s],
    )
    if not getattr(request, "is_bot", False):
        BlogPost.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)

    return render(request, "blog/detail.html", {
        "seo": seo, "post": post, "p": loc, "category": cat_loc, "related": related, "treatment": extras["treatment"],
        "reviewer": reviewer,
        "page_type": "blog_detail", "funnel_stage": post.funnel_stage,
    })
