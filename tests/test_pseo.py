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
        for lang in ("en", "de", "ar", "tr", "bg"):
            for t in SeoTopic.objects.all():
                with translation.override(lang):
                    url = reverse("guides:detail", kwargs={"slug": t.localized(lang).slug})
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200, url)
                html = r.content.decode()
                self.assertEqual(html.count("<h1"), 1, url)
                self.assertIsNone(MONEY.search(_visible(html)), url)
                self.assertNotIn("{rating}", html, url)  # meta'daki yer tutucu Google puanıyla dolmalı
                self.assertIn("https://cdn.example.com/real.jpg", html)
                self.assertIn("instagram.com/drdevrimbirikensipahi", html)
                suffix = "" if lang == "tr" else f"{lang}/"  # drdevrim.com: o anki dilin ana sayfası
                self.assertIn(f'href="https://drdevrim.com/{suffix}"', html)
                self.assertIn(f"https://devrimbirikensipahi.com.tr/{suffix}", html)

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

    def test_area_pages_in_every_language(self):
        from apps.seo.area_data import AREAS

        for lang in LANGUAGE_META:
            with translation.override(lang):
                urls = [reverse("areas:index")] + [reverse("areas:detail", kwargs={"area": k}) for k in AREAS]
            for url in urls:
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200, url)
                html = r.content.decode()
                self.assertEqual(html.count("<h1"), 1, url)
                self.assertIsNone(MONEY.search(_visible(html)), url)
                self.assertIn("https://cdn.example.com/real.jpg", html)  # her sayfada gerçek fotoğraf
                self.assertNotIn("%(", re.search(r"<title>(.*?)</title>", html, re.S).group(1), url)
        with translation.override("tr"):
            self.assertEqual(reverse("areas:detail", kwargs={"area": "nisantasi"}), "/tr/dis-klinigi/nisantasi/")
        self.assertIn("Taksim", self.client.get("/dental-clinic/taksim/").content.decode())
        self.assertEqual(self.client.get("/dental-clinic/kadikoy/").status_code, 404)

    def test_single_sitemap_contains_every_section(self):
        xml = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("<urlset", xml)
        self.assertNotIn("<sitemapindex", xml)                    # indeks değil, tek sitemap
        for path in ("/guide/", "/packages/", "/prices/", "/dental-holidays-from/", "/treatments/", "/dental-clinic/taksim/"):
            self.assertIn(path, xml)
        self.assertGreaterEqual(xml.count("<url>"), len(TOPICS) * len(LANGUAGE_META))
        self.assertIn('hreflang="x-default"', xml)

    def test_untranslated_topic_language_redirects_to_canonical_slug(self):
        t = SeoTopic.objects.get(key="dental-tourism")
        with translation.override("de"):
            url = reverse("guides:detail", kwargs={"slug": t.slug})  # EN slug, DE prefix
        r = self.client.get(url)
        self.assertEqual(r.status_code, 301)
        self.assertIn("zahntourismus", r["Location"])
