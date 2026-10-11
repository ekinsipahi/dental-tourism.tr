import json
import re

from django.core.cache import cache

from apps.clinics.models import Clinic, ClinicImage, ClinicLink, Review
from apps.core.models import ContentBlock
from apps.localization.models import TranslationStatus

from .base import SeededTestCase

BOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


def _jsonld(html, type_name):
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        data = json.loads(block)
        types = data.get("@type")
        if type_name == types or (isinstance(types, list) and type_name in types):
            return data
    return None


class ContentBlockTests(SeededTestCase):
    def test_editing_block_changes_home_text(self):
        b = ContentBlock.objects.get(key="home-reviews")
        b.title = "Stories from our patients"
        b.save()
        self.assertIn("Stories from our patients", self.client.get("/").content.decode())

    def test_untranslated_block_falls_back_to_translated_default(self):
        b = ContentBlock.objects.get(key="home-reviews")
        b.title = "Stories from our patients"
        b.save()
        html = self.client.get("/de/", HTTP_USER_AGENT=BOT_UA).content.decode()  # persona'sız varsayılan içerik
        self.assertNotIn("Stories from our patients", html)
        self.assertIn("Echte Patienten, echte Ergebnisse", html)

    def test_translated_block_is_used(self):
        b = ContentBlock.objects.get(key="home-reviews")
        b.translations.create(language_code="de", title="Geschichten unserer Patienten",
                              status=TranslationStatus.MACHINE, source_hash=b.compute_source_hash())
        cache.clear()
        self.assertIn("Geschichten unserer Patienten", self.client.get("/de/", HTTP_USER_AGENT=BOT_UA).content.decode())

    def test_section_can_be_hidden_and_reordered(self):
        ContentBlock.objects.filter(key="home-how").update(visible=False)
        ContentBlock.objects.filter(key="home-faq").update(order=15)  # tedavilerden hemen sonra
        html = self.client.get("/").content.decode()
        self.assertNotIn('id="how-h2"', html)
        self.assertLess(html.index('id="faq-h2"'), html.index('id="reviews-h2"'))

    def test_seo_title_override(self):
        b = ContentBlock.objects.get(key="seo-treatments")
        b.title = "Custom treatments SEO title"
        b.subtitle = "Custom description " + "x" * 120
        b.save()
        html = self.client.get("/treatments/").content.decode()
        self.assertIn("<title>Custom treatments SEO title | dentaltourism.tr</title>", html)
        self.assertIn("Custom description", html)


class ClinicSearchTests(SeededTestCase):
    def setUp(self):
        super().setUp()
        self.primary = Clinic.objects.get(slug="dr-devrim-sipahi")
        self.other = Clinic.objects.create(
            name="Bosphorus Dental", slug="bosphorus-dental", status=Clinic.STATUS_APPROVED, city=self.primary.city,
            district="Beşiktaş", address="X Cd. 1", phone="+90 212 000 00 00", whatsapp="902120000000",
            languages_spoken=["tr", "ru"], google_rating="4.6", offers_airport_transfer=True)

    def test_text_and_filter_search(self):
        r = self.client.get("/clinics/", {"q": "Beşiktaş"})
        html = r.content.decode()
        self.assertIn("Bosphorus Dental", html)
        self.assertNotIn(">Dr. Dt. Devrim Biriken Sipahi Dental Clinic<", html)
        self.assertIn('content="noindex,follow"', html)  # filtreli sayfa indexlenmez

    def test_language_and_transfer_filters(self):
        html = self.client.get("/clinics/", {"language": "ru", "transfer": "on"}).content.decode()
        self.assertIn("Bosphorus Dental", html)
        html = self.client.get("/clinics/", {"language": "de"}).content.decode()
        self.assertNotIn("Bosphorus Dental", html)

    def test_treatment_filter_and_no_prices(self):
        html = self.client.get("/clinics/", {"treatment": "dental-implants"}).content.decode()
        self.assertIn("Dental Clinic", html)
        self.assertNotRegex(html, r"€\s?\d|\d\s?€")  # liste sayfasında fiyat yok
        html = self.client.get("/clinics/", {"treatment": "dental-implants", "q": "zzz-yok"}).content.decode()
        self.assertIn("No clinics match your filters", html)

    def test_unfiltered_list_is_indexable_and_has_photo(self):
        ClinicImage.objects.create(clinic=self.other, image_url="https://cdn.example.com/a.jpg", alt="Bosphorus")
        html = self.client.get("/clinics/").content.decode()
        self.assertIn("index,follow", html)
        self.assertIn("https://cdn.example.com/a.jpg", html)


class ReviewSystemTests(SeededTestCase):
    def setUp(self):
        super().setUp()
        self.clinic = Clinic.objects.get(slug="dr-devrim-sipahi")
        self.url = f"/clinics/{self.clinic.slug}/review/"

    def _post(self, **kw):
        data = {"author_name": "Anna Katharina Müller", "email": "anna@example.com", "rating": 5,
                "text": "Excellent treatment, very honest dentist and painless implants. Highly recommended!",
                "consent": "on", **kw}
        return self.client.post(self.url, data)

    def test_review_goes_to_moderation_with_short_name(self):
        self._post()
        r = Review.objects.get(source=Review.SOURCE_SITE)
        self.assertFalse(r.is_published)
        self.assertEqual(r.author_name, "Anna M.")
        self.assertNotIn("Excellent treatment", self.client.get(self.clinic.get_absolute_url()).content.decode())

    def test_rate_limit_and_honeypot(self):
        for _ in range(5):
            self._post()
        self.assertEqual(Review.objects.filter(source=Review.SOURCE_SITE).count(), 3)
        cache.clear()
        self._post(website="http://spam")
        self.assertEqual(Review.objects.filter(source=Review.SOURCE_SITE).count(), 3)

    def test_schema_uses_only_internal_reviews(self):
        html = self.client.get(self.clinic.get_absolute_url()).content.decode()
        self.assertNotIn("aggregateRating", _jsonld(html, "Dentist"))  # Google yorumları işaretlenmez
        Review.objects.create(clinic=self.clinic, author_name="Anna M.", rating=4, text="Good", source="site",
                              is_published=True)
        Review.objects.create(clinic=self.clinic, author_name="Bo K.", rating=5, text="Great", source="site",
                              is_published=True)
        html = self.client.get(self.clinic.get_absolute_url()).content.decode()
        data = _jsonld(html, "Dentist")
        self.assertEqual(data["aggregateRating"]["reviewCount"], 2)
        self.assertEqual(data["aggregateRating"]["ratingValue"], 4.5)
        self.assertEqual(len(data["review"]), 2)

    def test_links_and_google_business_in_same_as(self):
        self.clinic.google_business_url = "https://g.page/devrim-sipahi"
        self.clinic.save()
        ClinicLink.objects.create(clinic=self.clinic, platform="tiktok", url="https://tiktok.com/@devrim")
        html = self.client.get(self.clinic.get_absolute_url()).content.decode()
        same_as = _jsonld(html, "Dentist")["sameAs"]
        self.assertIn("https://g.page/devrim-sipahi", same_as)
        self.assertIn("https://tiktok.com/@devrim", same_as)
        self.assertIn("https://www.instagram.com/drdevrimbirikensipahi/", same_as)
        self.assertIn("All Google reviews", html)

    def test_external_review_shows_source_link(self):
        Review.objects.create(clinic=self.clinic, author_name="G User", rating=5, text="From Google",
                              source="google", source_url="https://maps.google.com/review/1")
        html = self.client.get(self.clinic.get_absolute_url()).content.decode()
        self.assertIn('href="https://maps.google.com/review/1"', html)


class FaviconAndImageTests(SeededTestCase):
    def test_favicon_routes(self):
        r = self.client.get("/favicon.ico")
        self.assertIn(r.status_code, (301, 302))
        self.assertIn("favicon.ico", r["Location"])
        manifest = json.loads(self.client.get("/site.webmanifest").content)
        self.assertTrue(any(i["sizes"] == "192x192" for i in manifest["icons"]))
        html = self.client.get("/").content.decode()
        self.assertIn('<link rel="icon" href="/favicon.ico"', html)
        self.assertIn('sizes="48x48"', html)

    def test_image_url_instead_of_upload(self):
        clinic = Clinic.objects.get(slug="dr-devrim-sipahi")
        img = ClinicImage.objects.create(clinic=clinic, image_url="https://cdn.example.com/x.jpg", alt="Room",
                                         show_in_hero=True, order=0)
        self.assertEqual(img.src, "https://cdn.example.com/x.jpg")
        self.assertIn("https://cdn.example.com/x.jpg", self.client.get("/").content.decode())
