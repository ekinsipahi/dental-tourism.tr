import re

from django.conf import settings
from django.urls import reverse
from django.utils import translation

from apps.clinics.models import City

from .base import SeededTestCase


class PageRenderingTests(SeededTestCase):
    def _urls(self):
        return [reverse("core:home"), reverse("treatments:list"), reverse("prices:index"), reverse("core:contact"),
                reverse("core:about"), reverse("clinics:list"), reverse("blog:post_list"),
                reverse("clinics:detail", kwargs={"slug": "dr-devrim-sipahi"}),
                reverse("treatments:detail", kwargs={"slug": "dental-implants"}),
                reverse("prices:detail", kwargs={"slug": "dental-implants"}),
                reverse("treatments:city", kwargs={"slug": "dental-implants",
                                                   "city_slug": City.objects.get(slug="istanbul").localized().slug})]

    def test_all_languages_render_with_single_h1(self):
        for lang, _ in settings.LANGUAGES:
            with translation.override(lang):
                urls = self._urls()
            for url in urls:
                with self.subTest(lang=lang, url=url):
                    r = self.client.get(url)
                    self.assertEqual(r.status_code, 200)
                    html = r.content.decode()
                    self.assertEqual(len(re.findall(r"<h1[\s>]", html)), 1)
                    self.assertIn('rel="canonical"', html)
                    self.assertIn(f'<html lang="{lang}"', html)

    def test_url_segments_are_localized(self):
        with translation.override("de"):
            self.assertEqual(reverse("treatments:list"), "/de/behandlungen/")
        with translation.override("tr"):
            self.assertEqual(reverse("prices:index"), "/tr/fiyatlar/")

    def test_arabic_is_rtl(self):
        html = self.client.get("/ar/").content.decode()
        self.assertIn('dir="rtl"', html)

    def test_untranslated_treatment_is_noindex_without_hreflang(self):
        html = self.client.get("/de/behandlungen/dental-implants/").content.decode()
        self.assertIn('content="noindex,follow"', html)
        self.assertNotIn('rel="alternate" hreflang="de"', html)

    def test_home_has_hreflang_for_all_languages_and_x_default(self):
        html = self.client.get("/").content.decode()
        for lang, _ in settings.LANGUAGES:
            self.assertIn(f'hreflang="{lang}"', html)
        self.assertIn('hreflang="x-default" href="https://dentaltourism.tr/"', html)

    def test_structured_data(self):
        html = self.client.get("/treatments/dental-implants/").content.decode()
        for t in ('"MedicalProcedure"', '"FAQPage"', '"BreadcrumbList"'):
            self.assertIn(t, html)
        self.assertNotIn('"AggregateOffer"', html)  # fiyat şeması yok (fiyatlar yayınlanmaz)

    def test_robots_and_sitemap(self):
        self.assertIn("Sitemap: https://dentaltourism.tr/sitemap.xml", self.client.get("/robots.txt").content.decode())
        xml = self.client.get("/sitemap-treatments.xml").content.decode()
        self.assertIn("<loc>https://dentaltourism.tr/treatments/dental-implants/</loc>", xml)
        self.assertIn('hreflang="x-default"', xml)

    def test_contact_form_creates_lead_for_primary_clinic(self):
        from apps.tracking.models import Lead

        r = self.client.post("/contact/", {"name": "Test", "phone": "+49 151 2345678", "consent": "on",
                                           "message": "hi"})
        self.assertEqual(r.status_code, 302)
        lead = Lead.objects.get()
        self.assertEqual(lead.clinic.slug, "dr-devrim-sipahi")

    def test_contact_form_honeypot_blocks_spam(self):
        from apps.tracking.models import Lead

        self.client.post("/contact/", {"name": "Bot", "phone": "+49 151 2345678", "consent": "on",
                                       "website": "http://spam"})
        self.assertFalse(Lead.objects.exists())
