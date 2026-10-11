"""
Çok dilli sitemap — her URL için hreflang alternates + x-default.
Sadece o dilde gerçekten yayında olan (çevirisi canlı) sayfalar listelenir.
"""
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils.translation import get_language

ALL_LANGS = [c for c, _ in settings.LANGUAGES]


class I18nSitemap(Sitemap):
    protocol = "https"
    i18n = True
    alternates = True
    x_default = True
    languages = ALL_LANGS

    def get_urls(self, page=1, site=None, protocol=None):
        # İstek hangi host'tan gelirse gelsin kanonik domain kullanılır
        return super().get_urls(page=page, site=_Site(), protocol=self.protocol)


class _Site:
    domain = settings.SITE_URL.split("://", 1)[-1]
    name = settings.SITE_NAME


class StaticSitemap(I18nSitemap):
    changefreq = "weekly"

    def items(self):
        return [("core:home", 1.0), ("core:about", 0.6), ("core:contact", 0.7), ("treatments:list", 0.9),
                ("prices:index", 0.8), ("packages:index", 0.9), ("guides:index", 0.7), ("clinics:list", 0.6),
                ("blog:post_list", 0.7)]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]


class TranslatableSitemap(I18nSitemap):
    """Nesne başına sadece canlı dilleri döndürür."""

    def get_languages_for_item(self, item):
        return item.live_languages()


class TreatmentSitemap(TranslatableSitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        from apps.treatments.models import Treatment

        return Treatment.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("treatments:detail", kwargs={"slug": obj.localized(get_language()).slug})

    def lastmod(self, obj):
        return obj.updated_at


class LandingPageSitemap(TranslatableSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        from apps.seo.models import LandingPage

        return (LandingPage.objects.filter(is_active=True, noindex=False, treatment__is_active=True,
                                           page_type=LandingPage.TYPE_TREATMENT_CITY)
                .select_related("treatment", "city"))

    def get_languages_for_item(self, item):
        return [lg for lg in item.live_languages() if item.treatment.has_language(lg)]

    def location(self, obj):
        lang = get_language()
        t = obj.treatment.localized(lang)
        return reverse("treatments:city", kwargs={"slug": t.slug, "city_slug": obj.city.localized(lang).slug})

    def lastmod(self, obj):
        return obj.updated_at


class ClinicSitemap(TranslatableSitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        from apps.clinics.models import Clinic

        return Clinic.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class DoctorSitemap(TranslatableSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        from apps.clinics.models import Doctor

        return Doctor.objects.filter(is_active=True, clinic__status="approved")


class BlogPostSitemap(TranslatableSitemap):
    changefreq = "weekly"

    def items(self):
        from apps.blog.models import BlogPost

        return BlogPost.published.filter(noindex=False)

    def location(self, obj):
        return obj.get_absolute_url(get_language())

    def lastmod(self, obj):
        return obj.updated_at

    def priority(self, obj):
        return {"decision": 0.8, "consideration": 0.7}.get(obj.funnel_stage, 0.6)


class BlogCategorySitemap(TranslatableSitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        from apps.blog.models import BlogCategory

        return BlogCategory.objects.filter(posts__status="published").distinct()

    def location(self, obj):
        return obj.get_absolute_url(get_language())


class _TreatmentPerLang(TranslatableSitemap):
    """Tedavi başına, tedavinin canlı olduğu dillerde bir URL (paket + maliyet sayfaları)."""
    changefreq = "weekly"
    viewname = ""

    def items(self):
        from apps.treatments.models import Treatment

        return Treatment.objects.filter(is_active=True)

    def location(self, obj):
        return reverse(self.viewname, kwargs={"slug": obj.localized(get_language()).slug})

    def lastmod(self, obj):
        return obj.updated_at


class PackageSitemap(_TreatmentPerLang):
    priority = 0.85
    viewname = "packages:treatment"


class PriceSitemap(_TreatmentPerLang):
    priority = 0.8
    viewname = "prices:detail"


class OriginSitemap(I18nSitemap):
    """Ülkeden paket sayfaları: her ülke yalnızca o ülkenin pazar dillerinde."""
    changefreq = "monthly"
    priority = 0.75

    def items(self):
        from apps.seo.package_data import ORIGINS

        return [c for c in ORIGINS if c != "TR"]

    def get_languages_for_item(self, item):
        from apps.seo.package_data import langs_for_origin

        return langs_for_origin(item)

    def location(self, item):
        from apps.seo.package_data import country_slug

        return reverse("origins:detail", kwargs={"country": country_slug(item, get_language())})


class GuideSitemap(TranslatableSitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        from apps.seo.models import SeoTopic

        return SeoTopic.objects.filter(is_active=True, noindex=False)

    def location(self, obj):
        return reverse("guides:detail", kwargs={"slug": obj.localized(get_language()).slug})

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "pages": StaticSitemap,
    "treatments": TreatmentSitemap,
    "packages": PackageSitemap,
    "prices": PriceSitemap,
    "origins": OriginSitemap,
    "guides": GuideSitemap,
    "landing": LandingPageSitemap,
    "clinics": ClinicSitemap,
    "doctors": DoctorSitemap,
    "blog": BlogPostSitemap,
    "blog-categories": BlogCategorySitemap,
}
