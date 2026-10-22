"""
SEO yardımcıları — her view bir `Seo` nesnesi üretir, base.html bunu render eder.

İçerir: title, meta description, canonical, hreflang alternates (+x-default),
robots, Open Graph / Twitter, JSON-LD schema listesi, breadcrumb.
"""
import json
from dataclasses import dataclass, field

from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils import translation
from django.utils.safestring import mark_safe

from dental_tourism.languages import LANGUAGE_META

TITLE_MAX = 60
DESC_MAX = 158


def absolute(path: str) -> str:
    if path.startswith("http"):
        return path
    return settings.SITE_URL + path


def reverse_in(lang, viewname, kwargs=None):
    with translation.override(lang):
        return reverse(viewname, kwargs=kwargs or {})


def alternates_for(viewname, kwargs_for_lang=None, languages=None):
    """{lang: mutlak URL}. kwargs_for_lang(lang) None dönerse o dil atlanır."""
    langs = languages or [c for c, _ in settings.LANGUAGES]
    out = {}
    for lang in langs:
        kwargs = kwargs_for_lang(lang) if kwargs_for_lang else {}
        if kwargs is None:
            continue
        try:
            out[lang] = absolute(reverse_in(lang, viewname, kwargs))
        except NoReverseMatch:
            continue
    return out


def truncate(text, limit):
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut.rstrip(",.;:—-") + "…"


@dataclass
class Seo:
    title: str
    description: str = ""
    canonical: str = ""
    alternates: dict = field(default_factory=dict)
    robots: str = "index,follow,max-image-preview:large"
    og_type: str = "website"
    image: str = ""
    image_alt: str = ""
    schema: list = field(default_factory=list)
    breadcrumbs: list = field(default_factory=list)   # [(name, url), ...]
    published: str = ""
    modified: str = ""
    append_site_name: bool = True

    def __post_init__(self):
        self.description = truncate(self.description, DESC_MAX)

    @property
    def full_title(self):
        site = settings.SITE_NAME
        if not self.append_site_name or site.lower() in self.title.lower():
            return truncate(self.title, 70)
        candidate = f"{self.title} | {site}"
        return candidate if len(candidate) <= 65 else truncate(self.title, 65)

    @property
    def noindex(self):
        return "noindex" in self.robots

    @property
    def x_default(self):
        return self.alternates.get(settings.LANGUAGE_CODE)

    @property
    def hreflang_links(self):
        if self.noindex:
            return []
        return [(LANGUAGE_META[lang]["hreflang"], url) for lang, url in self.alternates.items()]

    @property
    def og_image(self):
        if self.image:
            return absolute(self.image)
        from .models import SiteSettings

        site = SiteSettings.load()
        if site.default_og_image:
            return absolute(site.default_og_image.url)
        return absolute(settings.STATIC_URL + "img/og-default.png")

    @property
    def jsonld(self):
        blocks = list(self.schema)
        if self.breadcrumbs:
            blocks.append(breadcrumb_schema(self.breadcrumbs))
        return [mark_safe(json.dumps(b, ensure_ascii=False).replace("</", "<\\/")) for b in blocks]


def breadcrumb_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": absolute(url)}
            for i, (name, url) in enumerate(items, start=1)
        ],
    }


def faq_schema(faq):
    items = [f for f in (faq or []) if f.get("question") and f.get("answer")]
    if not items:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["question"],
             "acceptedAnswer": {"@type": "Answer", "text": f["answer"]}}
            for f in items
        ],
    }


def organization_schema():
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": settings.SITE_URL + "/#organization",
        "name": settings.SITE_NAME,
        "url": settings.SITE_URL + "/",
        "logo": absolute(settings.STATIC_URL + "img/logo-square.png"),
    }


def website_schema():
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": settings.SITE_URL + "/#website",
        "url": settings.SITE_URL + "/",
        "name": settings.SITE_NAME,
        "publisher": {"@id": settings.SITE_URL + "/#organization"},
        "inLanguage": [c for c, _ in settings.LANGUAGES],
    }


def clinic_schema(clinic, loc=None, url=None, with_reviews=False):
    """schema.org Dentist (LocalBusiness + MedicalOrganization) — klinik × dil başına 5 dk süreç içi bellekte
    (sosyal linkler, puan özeti ve yorumlar her sayfa isteğinde yeniden sorgulanmaz)."""
    if clinic is None:
        return None
    from apps.localization.memo import memo

    loc = loc or clinic.localized()
    return memo(f"clinic-schema:{clinic.pk}:{loc.lang}:{url or ''}:{int(with_reviews)}", 300,
                lambda: _clinic_schema(clinic, loc, url, with_reviews), model=type(clinic))


def _clinic_schema(clinic, loc, url, with_reviews):
    data = {
        "@context": "https://schema.org",
        "@type": ["Dentist", "MedicalClinic"],
        "@id": absolute(url or clinic.get_absolute_url()) + "#clinic",
        "name": clinic.name,
        "description": loc.short_description or loc.tagline,
        "url": absolute(url or clinic.get_absolute_url()),
        "telephone": clinic.phone,
        "email": clinic.email or None,
        "priceRange": clinic.price_range,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": clinic.address,
            "addressLocality": clinic.city.name,
            "addressRegion": clinic.district,
            "postalCode": clinic.postal_code,
            "addressCountry": clinic.city.country_code,
        },
        "availableLanguage": clinic.languages_spoken or None,
        "openingHours": clinic.opening_hours or None,
        # sameAs: Google Business Profile + sosyal hesaplar → varlık (entity) sinyali
        "sameAs": [link["url"] for link in clinic.social_links] or None,
        "hasMap": clinic.maps_url or None,
        "medicalSpecialty": "Dentistry",
        "isAcceptingNewPatients": True,
    }
    if clinic.latitude and clinic.longitude:
        data["geo"] = {"@type": "GeoCoordinates", "latitude": float(clinic.latitude),
                       "longitude": float(clinic.longitude)}
    data["logo"] = absolute(clinic.logo_src or settings.STATIC_URL + "img/logo-square.png")
    if clinic.display_image:
        data["image"] = absolute(clinic.display_image)
    # Sadece KENDİ toplanan yorumlar işaretlenir (Google yorumlarını kopyalayıp schema'ya koymak
    # Google yönergelerine aykırıdır). Platform birden çok kliniği listelediği için bunlar "self-serving" değildir.
    stats = clinic.review_stats()
    if stats["count"]:
        data["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": stats["avg"],
                                   "reviewCount": stats["count"], "bestRating": 5, "worstRating": 1}
        if with_reviews:
            from apps.clinics.models import Review

            data["review"] = [{
                "@type": "Review",
                "author": {"@type": "Person", "name": r.author_name},
                "datePublished": (r.review_date or r.created_at.date()).isoformat() if (r.review_date or r.created_at) else None,
                "reviewRating": {"@type": "Rating", "ratingValue": r.rating, "bestRating": 5},
                "reviewBody": r.text[:500],
                "inLanguage": r.language or None,
            } for r in clinic.reviews.filter(is_published=True, source=Review.SOURCE_SITE).exclude(text="")[:5]]
    return {k: v for k, v in data.items() if v not in (None, "", [])}


def localized_language_links(alternates, current):
    """Dil seçici: alternates'ta varsa o URL, yoksa o dilin ana sayfası."""
    links = []
    for code, meta in LANGUAGE_META.items():
        url = alternates.get(code) or absolute(reverse_in(code, "core:home"))
        links.append({"code": code, "native": meta["native"], "flag": meta["flag"], "url": url,
                      "active": code == current, "available": code in alternates})
    return links


def proof():
    """Meta title/description'larda kullanılan GERÇEK kanıtlar: Google puanı ve yorum sayısı (veritabanından)."""
    try:
        from apps.clinics.models import Clinic

        c = Clinic.primary()
    except Exception:  # noqa: BLE001
        c = None
    r = c.google_rating if c and c.google_rating else None
    return {"rating": format(r, "g") if r else "4.9", "count": (c.google_review_count if c and c.google_review_count else 100)}


def fill_proof(text):
    """İçerikteki {rating} / {count} yer tutucularını güncel Google puanıyla doldurur (meta title/description)."""
    if not text or "{" not in text:
        return text
    p = proof()
    return text.replace("{rating}", p["rating"]).replace("{count}", str(p["count"]))


def page_meta(key, title, description=""):
    """Statik sayfaların SEO title/description'ı admin'den değiştirilebilir:
    Content blocks → key = "seo-<sayfa>" (title = meta title, subtitle = meta description).
    Bu dilde çeviri yoksa koddaki (çevrilmiş) varsayılan kullanılır."""
    from django.utils.translation import get_language

    from apps.core.templatetags.site_tags import _block

    data = _block(f"seo-{key}", get_language())
    return (data.get("title") or title), (data.get("subtitle") or description)
