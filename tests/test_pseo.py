"""Programatik SEO: konu/paket/fiyat sayfaları — 16 dil, fiyatsız, gerçek foto, backlink, sitemap."""
import re

from django.core.management import call_command
from django.urls import reverse
from django.utils import translation

from dental_tourism.languages import LANGUAGE_META

from apps.clinics.models import Clinic, ClinicImage
from apps.seo.models import SeoTopic
from apps.seo.topics import TOPICS

from .base import SeededTestCase

MONEY = re.compile(r"[€£$]\s?\d|\d\s?(?:€|EUR|GBP|USD)\b|\d+\s?[–-]\s?\d+\s?%")


def _visible(html):
    return re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S)


class PseoTests(SeededTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("seed_topics", "--no-keywords", verbosity=0, stdout=open("/dev/null", "w"))
        clinic = Clinic.primary()
        ClinicImage.objects.create(clinic=clinic, image_url="https://cdn.example.com/real.jpg", alt="Clinic room")
        clinic.instagram = "drdevrimbirikensipahi"
        clinic.save()

    def test_all_topics_live_in_16_languages(self):
        self.assertEqual(SeoTopic.objects.count(), len(TOPICS))
        for t in SeoTopic.objects.all():
            self.assertEqual(len(t.live_languages()), len(LANGUAGE_META), t.key)

    def test_guide_pages_render_without_prices_with_photo_and_backlinks(self):
        for lang in ("en", "de", "ar", "tr"):
            for t in SeoTopic.objects.all():
                with translation.override(lang):
                    url = reverse("guides:detail", kwargs={"slug": t.localized(lang).slug})
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200, url)
                html = r.content.decode()
                self.assertEqual(html.count("<h1"), 1, url)
                self.assertIsNone(MONEY.search(_visible(html)), url)
                self.assertIn("https://cdn.example.com/real.jpg", html)
                self.assertIn("instagram.com/drdevrimbirikensipahi", html)
                self.assertIn('href="https://drdevrim.com/"', html)  # her dilde ana sayfa
                old = "https://devrimbirikensipahi.com.tr/" if lang == "tr" else "https://devrimbirikensipahi.com.tr/en/"
                self.assertIn(old, html)

    def test_package_and_price_pages(self):
        for name, kwargs in [("packages:index", {}), ("prices:index", {}),
                             ("packages:treatment", {"slug": "dental-implants"}),
                             ("prices:detail", {"slug": "dental-implants"}),
                             ("origins:detail", {"country": "australia"})]:
            with translation.override("en"):
                url = reverse(name, kwargs=kwargs)
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
            self.assertIsNone(MONEY.search(_visible(r.content.decode())), url)

    def test_sitemaps_list_pseo_sections(self):
        idx = self.client.get("/sitemap.xml").content.decode()
        for section in ("guides", "packages", "prices", "origins"):
            self.assertIn(f"sitemap-{section}.xml", idx)
        guides = self.client.get("/sitemap-guides.xml").content.decode()
        self.assertGreaterEqual(guides.count("<url>"), len(TOPICS) * len(LANGUAGE_META))
        self.assertIn('hreflang="x-default"', guides)

    def test_untranslated_topic_language_redirects_to_canonical_slug(self):
        t = SeoTopic.objects.get(key="dental-tourism")
        with translation.override("de"):
            url = reverse("guides:detail", kwargs={"slug": t.slug})  # EN slug, DE prefix
        r = self.client.get(url)
        self.assertEqual(r.status_code, 301)
        self.assertIn("zahntourismus", r["Location"])
