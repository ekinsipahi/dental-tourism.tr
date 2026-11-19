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


def _first_paragraph(markdown_text, limit=260):
    """Hekim biyografisinin ilk paragrafı (düz metin) — yazar kutusu için."""
    import re

    for para in re.split(r"\n\s*\n", (markdown_text or "").strip()):
        text = re.sub(r"[#*_`>\[\]()]+", "", para).strip()
        if len(text) > 40:
            return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"
    return ""


def _content_images(markdown_text):
    """Gövdedeki görseller (Markdown ![..](src) ve ham <img src>) — şemadaki image listesi için."""
    import re

    text = markdown_text or ""
    return re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text) + re.findall(r'<img[^>]+src="([^"]+)"', text)


def person_schema(doctor_loc, url):
    """Yazar/onaylayan hekim için Person — hekim sayfasındaki Person ile aynı @id (tek kimlik)."""
    d = doctor_loc.object
    out = {"@type": "Person", "@id": url + "#person", "name": d.full_name, "url": url,
           "jobTitle": doctor_loc.title_display or "Dentist",
           "image": absolute(d.photo_src) if d.photo_src else None,
           "sameAs": [f"https://www.instagram.com/{d.instagram}/"] if d.instagram else None}
    return {k: v for k, v in out.items() if v}


def _post_extras(post, lang):
    """Yazı sayfasının yardımcı verisi (URL'ler, kategori, hreflang, ilgili yazılar, hekim, tedavi) — (yazı, dil)
    başına 5 dk süreç içi bellekte: 17 dilin hreflang'ı için her istekte onlarca çeviri sorgusu atılmaz."""
    from apps.localization.memo import memo

    def load():
        related_ids = list(RelatedPost.objects.filter(post=post).values_list("related_post_id", flat=True)[:6])
        related_qs = BlogPost.published.filter(pk__in=related_ids) if related_ids else \
            BlogPost.published.filter(category=post.category).exclude(pk=post.pk)
        # Yazar = yazan/konuşan hekim (doctor_author); yoksa onaylayan hekim yazar sayılır. Onaylayan hekim
        # yazardan farklıysa ayrıca "medically reviewed by" olarak gösterilir.
        author = post.doctor_author or post.reviewed_by
        reviewer = post.reviewed_by if post.reviewed_by and post.reviewed_by != author else None
        return {
            "url": post.get_absolute_url(lang),
            "source_url": post.get_absolute_url(post.source_language),
            "cat_loc": post.category.localized(lang),
            "cat_url": post.category.get_absolute_url(lang),
            "alternates": {lg: absolute(post.get_absolute_url(lg)) for lg in post.live_languages()},
            "related": localize_list(with_translations(_posts_in_language(related_qs, lang)[:4], lang), lang, fallback=False),
            "author": author.localized(lang) if author else None,
            "author_url": absolute(author.get_absolute_url()) if author else "",
            "author_bio": _first_paragraph(author.localized(lang).bio) if author else "",
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

    author = person_schema(extras["author"], extras["author_url"]) if extras["author"] else None
    reviewer = extras["reviewer"]
    images = [absolute(post.image_src)] if post.image_src else []
    images += [absolute(src) for src in _content_images(loc.content) if absolute(src) not in images]
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
        "image": images or None,
        "keywords": loc.focus_keyword or None,
        "wordCount": len((loc.content or "").split()),
        "articleSection": cat_loc.name,
        "isAccessibleForFree": True,
        # AEO: sesli asistan / özet için doğrudan cevap paragrafı ve anahtar noktalar listesi
        "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".prose > p:first-of-type", ".prose > ul:first-of-type"]},
    }
    if extras["treatment"]:
        article["about"] = {"@type": "MedicalProcedure", "name": extras["treatment"].name}
    if reviewer:
        article["reviewedBy"] = person_schema(reviewer, extras["reviewer_url"])
    elif author and post.schema_type == "MedicalWebPage":
        article["reviewedBy"] = author
    if post.schema_type == "MedicalWebPage":
        article["lastReviewed"] = post.updated_at.date().isoformat()
        article["audience"] = {"@type": "MedicalAudience", "audienceType": "Patient"}

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
        "author": extras["author"], "author_url": extras["author_url"], "author_bio": extras["author_bio"],
        "reviewer": reviewer, "reviewer_url": extras["reviewer_url"],
        "page_type": "blog_detail", "funnel_stage": post.funnel_stage,
    })
