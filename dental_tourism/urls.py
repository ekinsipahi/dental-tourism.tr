"""
URL yapısı — tüm site 16 dilde, URL segmentleri o dile çevrilir:

  /                                  → EN ana sayfa (varsayılan dil prefix'siz)
  /de/                               → DE ana sayfa
  /de/behandlungen/zahnimplantate/   → tedavi sayfası (slug o dile ait)
  /de/behandlungen/zahnimplantate/istanbul/ → programatik tedavi × şehir sayfası
  /de/preise/zahnimplantate/         → tedavi maliyet sayfası (RAKAM YOK — kişisel teklif)
  /de/<packages>/zahnimplantate/     → tedavi paket sayfası
  /de/<dental-holidays-from>/<ülke>/ → ülkeden paket sayfası
  /de/<guide>/<konu-slug>/           → konu (rehber) sayfaları — apps/seo/topics.py
  /de/kliniken/dr-devrim-sipahi/     → klinik profili
  /de/zahnaerzte/devrim-sipahi/      → hekim profili
  /de/blog/<kategori>/<yazi>/        → blog
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from apps.core import views as core_views
from apps.core.sitemaps import SITEMAPS

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", core_views.robots_txt, name="robots"),
    # Render health check — veritabanına dokunmaz, HTTPS yönlendirmesinden muaf (SECURE_REDIRECT_EXEMPT)
    path("healthz", lambda request: HttpResponse("ok", content_type="text/plain"), name="healthz"),
    path("llms.txt", core_views.llms_txt, name="llms"),
    path("favicon.ico", core_views.favicon, name="favicon"),
    path("apple-touch-icon.png", core_views.apple_touch_icon),
    path("site.webmanifest", core_views.webmanifest, name="webmanifest"),
    # TEK sitemap: tüm bölümler (sayfalar, tedaviler, rehberler, paketler, fiyat, köken, blog, klinik, hekim)
    # hreflang alternates + x-default ile tek <urlset> içinde
    # 6 saat önbellek (DatabaseCache) — 949 URL × 16 dil hreflang her istekte yeniden üretilmez
    path("sitemap.xml", cache_page(60 * 60 * 6)(sitemap), {"sitemaps": SITEMAPS}, name="sitemap-index"),
    path("sitemap-<section>.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap-section"),
    path("api/persona/", include("apps.persona.api_urls")),
    path("api/tracking/", include("apps.tracking.urls")),
    path("api/dashboard/", include("apps.persona.dashboard_urls")),
]

urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path(_("treatments/"), include("apps.treatments.urls")),
    path(_("prices/"), include("apps.seo.urls")),
    path(_("packages/"), include("apps.seo.package_urls")),
    path(_("dental-holidays-from/"), include("apps.seo.origin_urls")),
    path(_("guide/"), include("apps.seo.guide_urls")),
    path(_("dental-clinic/"), include("apps.seo.area_urls")),
    path(_("clinics/"), include("apps.clinics.urls")),
    path(_("dentists/"), include("apps.clinics.doctor_urls")),
    path("blog/", include("apps.blog.urls")),
    prefix_default_language=False,
)

handler404 = "apps.core.views.page_not_found"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
