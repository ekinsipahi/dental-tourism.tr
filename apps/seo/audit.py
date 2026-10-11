"""
On-page SEO denetimi — her dil için ayrı.

Admin'de yazı formunda "SEO kontrol" alanında ve `manage.py seo audit` raporunda kullanılır.
"""
import re

from slugify import slugify

TITLE_MAX = 60
DESC_MIN, DESC_MAX = 120, 160
MIN_WORDS = {"blog": 700, "treatment": 500, "landing": 400}


def _norm(s):
    return slugify(s or "", separator=" ")


def audit_fields(*, title="", meta_title="", meta_description="", focus_keyword="", slug="", body="",
                 image_alt=None, has_image=False, kind="blog", faq=None):
    issues = []
    mt = meta_title or title
    if not mt:
        issues.append("Meta title yok")
    elif len(mt) > TITLE_MAX:
        issues.append(f"Meta title {len(mt)} karakter (max {TITLE_MAX})")
    if not meta_description:
        issues.append("Meta description yok")
    elif not DESC_MIN <= len(meta_description) <= DESC_MAX:
        issues.append(f"Meta description {len(meta_description)} karakter ({DESC_MIN}-{DESC_MAX} olmalı)")
    if re.search(r"^#\s", body or "", flags=re.M):
        issues.append("İçerikte H1 (# ) var — sayfada tek H1 olmalı, ## kullanın")
    h2 = len(re.findall(r"^##\s", body or "", flags=re.M))
    if h2 < 2:
        issues.append(f"Sadece {h2} adet H2 — içeriği alt başlıklara bölün")
    words = len((body or "").split())
    if words < MIN_WORDS.get(kind, 400):
        issues.append(f"İçerik kısa: {words} kelime (öneri ≥ {MIN_WORDS.get(kind, 400)})")
    if not focus_keyword:
        issues.append("Focus keyword belirlenmemiş")
    else:
        kw = _norm(focus_keyword)
        if kw not in _norm(mt):
            issues.append("Focus keyword meta title'da geçmiyor")
        if kw not in _norm(meta_description):
            issues.append("Focus keyword meta description'da geçmiyor")
        first = _norm((body or "")[:600])
        if kw not in first:
            issues.append("Focus keyword ilk paragrafta geçmiyor")
        kw_tokens = set(kw.split())
        if slug and not kw_tokens & set(slug.split("-")):
            issues.append("Slug focus keyword'den kelime içermiyor")
    links = len(re.findall(r"\]\((/|https?://dentaltourism)", body or ""))
    if kind == "blog" and links < 2:
        issues.append(f"İç link sayısı {links} — en az 2 ilgili sayfaya link verin")
    if has_image and not image_alt:
        issues.append("Görsel alt metni yok")
    if kind in ("treatment", "landing") and not faq:
        issues.append("FAQ yok (FAQPage schema için önerilir)")
    return issues


def audit_post(post, lang=None):
    loc = post.localized(lang) if lang else post
    return audit_fields(title=loc.title, meta_title=loc.meta_title, meta_description=loc.meta_description,
                        focus_keyword=loc.focus_keyword, slug=loc.slug, body=loc.content,
                        image_alt=loc.featured_image_alt, has_image=bool(post.image_src), kind="blog",
                        faq=loc.faq)


def audit_treatment(t, lang=None):
    loc = t.localized(lang) if lang else t
    return audit_fields(title=loc.name, meta_title=loc.meta_title, meta_description=loc.meta_description,
                        focus_keyword=loc.focus_keyword, slug=loc.slug, body=loc.body, kind="treatment",
                        faq=loc.faq)


def audit_landing(page, lang=None):
    loc = page.localized(lang) if lang else page
    return audit_fields(title=loc.h1, meta_title=loc.meta_title, meta_description=loc.meta_description,
                        focus_keyword=loc.focus_keyword, body=f"{loc.intro}\n\n{loc.body}", kind="landing",
                        faq=loc.faq)
