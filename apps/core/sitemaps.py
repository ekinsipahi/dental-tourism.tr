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
        self._loc_cache, self._lang_cache = {}, {}
        try:
            return super().get_urls(page=page, site=_Site(), protocol=self.protocol)
        finally:
            self._loc_cache, self._lang_cache = {}, {}

    # Django her URL'nin hreflang alternatiflerini üretirken aynı (nesne, dil) adresini defalarca hesaplar
    # (n × dil²). Her (nesne, dil) bir kez hesaplanır, dil listesi nesne başına bir kez alınır.
    def _location(self, item, force_lang_code=None):
        cache = getattr(self, "_loc_cache", None)
        if cache is None:
            return super()._location(item, force_lang_code)
        key = (id(item[0]), force_lang_code or item[1])
        if key not in cache:
            cache[key] = super()._location(item, force_lang_code)
        return cache[key]

    def get_languages_for_item(self, item):
        cache = getattr(self, "_lang_cache", None)
        if cache is None:
            return self._languages_for(item)
        key = id(item)
        if key not in cache:
            cache[key] = self._languages_for(item)
        return cache[key]

    def _languages_for(self, item):
        return self.languages


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

    def _languages_for(self, item):
        return item.live_languages()


def _all(qs, *paths):
    from apps.localization.models import with_all_translations

    return with_all_translations(qs, *paths)


class TreatmentSitemap(TranslatableSitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        from apps.treatments.models import Treatment

        return _all(Treatment.objects.filter(is_active=True))

    def location(self, obj):
        return reverse("treatments:detail", kwargs={"slug": obj.localized(get_language()).slug})

    def lastmod(self, obj):
        return obj.updated_at


class LandingPageSitemap(TranslatableSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        from apps.seo.models import LandingPage

        return _all(LandingPage.objects.filter(is_active=True, noindex=False, treatment__is_active=True,
                                               page_type=LandingPage.TYPE_TREATMENT_CITY)
                    .select_related("treatment", "city"), "treatment", "city")

    def _languages_for(self, item):
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

        return _all(Clinic.objects.published())

    def lastmod(self, obj):
        return obj.updated_at


class DoctorSitemap(TranslatableSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        from apps.clinics.models import Doctor

        return _all(Doctor.objects.filter(is_active=True, clinic__status="approved"))


class BlogPostSitemap(TranslatableSitemap):
    changefreq = "weekly"

    def items(self):
        from apps.blog.models import BlogPost

        return _all(BlogPost.published.filter(noindex=False))

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

        return _all(BlogCategory.objects.filter(posts__status="published").distinct())

    def location(self, obj):
        return obj.get_absolute_url(get_language())


class _TreatmentPerLang(TranslatableSitemap):
    """Tedavi başına, tedavinin canlı olduğu dillerde bir URL (paket + maliyet sayfaları)."""
    changefreq = "weekly"
    viewname = ""

    def items(self):
        from apps.treatments.models import Treatment

        return _all(Treatment.objects.filter(is_active=True))

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

    def _languages_for(self, item):
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

        return _all(SeoTopic.objects.filter(is_active=True, noindex=False))

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
