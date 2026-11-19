"""seed_blog: dosyadan (Markdown + YAML) blog yazısı ve kategori çevirisi yükleme — idempotent, dosya esastır."""
import io
import json
import shutil
import tempfile
from datetime import timedelta
from pathlib import Path

from django.core.management import call_command
from django.utils import timezone

from apps.blog.models import BlogCategory, BlogPost
from apps.clinics.models import Doctor
from apps.localization.models import TranslationStatus

from .base import SeededTestCase

CONTENT = Path(__file__).resolve().parents[1] / "apps" / "blog" / "content"

POST_EN = """---
title: Is it safe to get dental implants in Turkey?
slug: is-it-safe-to-get-dental-implants-in-turkey
category: safety-and-quality
excerpt: Safety depends on planning, sterilisation and who operates — not on the country.
meta_title: Is It Safe to Get Dental Implants in Turkey? A Dentist Answers
meta_description: What actually determines implant safety, when we refuse to operate, and what to ask any clinic.
focus_keyword: dental implants turkey safe
featured_image: img/blog/implant-safety/hero.jpg
featured_image_alt: Sealed sterile instrument pouches in our clinic
author: devrim-biriken-sipahi
reviewed_by: ekin-sipahi
treatment: dental-implants
schema_type: MedicalWebPage
funnel_stage: consideration
guides: [dental-care-turkey]
status: published
published: %(published)s
faq:
  - q: Do you place implants in one visit?
    a: No. The implant needs time to heal before the final crown.
---
## The short answer
Safety depends on the clinic, not the country.

![Autoclave]({static:img/blog/implant-safety/autoclave.jpg})

## When we say no
Uncontrolled diabetes, heavy smoking, untreated gum disease.

## What to ask any clinic
Who places the implant, which system, what is documented.
"""

POST_DE = """---
title: Sind Zahnimplantate in der Türkei sicher?
slug: sind-zahnimplantate-in-der-tuerkei-sicher
excerpt: Sicherheit hängt von Planung, Sterilisation und dem Behandler ab — nicht vom Land.
meta_title: Sind Zahnimplantate in der Türkei sicher? Eine Zahnärztin antwortet
meta_description: Was die Sicherheit von Implantaten wirklich bestimmt.
focus_keyword: zahnimplantate türkei sicher
featured_image_alt: Versiegelte sterile Instrumentenbeutel in unserer Klinik
faq:
  - q: Setzen Sie Implantate in einem Besuch?
    a: Nein. Das Implantat muss vor der endgültigen Krone einheilen.
---
## Die kurze Antwort
Die Sicherheit hängt von der Klinik ab, nicht vom Land.
"""


class SeedBlogTests(SeededTestCase):
    def setUp(self):
        super().setUp()
        self.dir = Path(tempfile.mkdtemp())
        shutil.copy(CONTENT / "categories.yaml", self.dir / "categories.yaml")
        clinic = Doctor.objects.get(slug="devrim-biriken-sipahi").clinic
        Doctor.objects.get_or_create(slug="ekin-sipahi", defaults={"clinic": clinic, "name": "Ekin Sipahi",
                                                                   "honorific": "Dt.", "title_display": "Dentist",
                                                                   "source_language": "en"})
        self.post_dir = self.dir / "posts" / "is-it-safe-to-get-dental-implants-in-turkey"
        self.post_dir.mkdir(parents=True)
        self._write("en.md", POST_EN % {"published": "2026-11-18"})
        self._write("de.md", POST_DE)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, name, text):
        (self.post_dir / name).write_text(text, encoding="utf-8")

    def _seed(self):
        out = io.StringIO()
        call_command("seed_blog", dir=str(self.dir), stdout=out, stderr=out)
        return out.getvalue()

    def test_categories_created_with_file_translations(self):
        self._seed()
        cat = BlogCategory.objects.get(slug="safety-and-quality")
        self.assertEqual(cat.funnel_stage, "consideration")
        self.assertEqual(cat.translations.count(), 16)
        de = cat.translations.get(language_code="de")
        self.assertEqual((de.name, de.slug, de.status), ("Sicherheit und Qualität", "sicherheit-und-qualitaet",
                                                         TranslationStatus.REVIEWED))
        # Mevcut kategoriye (seed_data) yalnızca çeviriler eklenir, kendisi ezilmez
        trip = BlogCategory.objects.get(slug="planning-your-trip")
        self.assertEqual(trip.translations.get(language_code="ru").slug, "planirovanie-poezdki")
        self.assertEqual(trip.get_absolute_url("tr"), "/tr/blog/seyahat-plani/")

    def test_post_published_with_author_image_and_translation(self):
        self._seed()
        post = BlogPost.objects.get(slug="is-it-safe-to-get-dental-implants-in-turkey")
        self.assertEqual(post.status, BlogPost.STATUS_PUBLISHED)
        self.assertEqual(post.published_at.date().isoformat(), "2026-11-18")
        self.assertEqual(post.doctor_author, Doctor.objects.get(slug="devrim-biriken-sipahi"))
        self.assertEqual(post.reviewed_by, Doctor.objects.get(slug="ekin-sipahi"))
        self.assertEqual(post.treatment.key, "dental-implants")
        self.assertEqual(post.schema_type, "MedicalWebPage")
        self.assertFalse(post.auto_translate)
        self.assertEqual(post.featured_image_url, "/static/img/blog/implant-safety/hero.jpg")
        self.assertIn("](/static/img/blog/implant-safety/autoclave.jpg)", post.content)
        self.assertEqual(post.faq, [{"question": "Do you place implants in one visit?",
                                     "answer": "No. The implant needs time to heal before the final crown."}])
        de = post.translations.get(language_code="de")
        self.assertEqual((de.status, de.slug, de.model_used), (TranslationStatus.REVIEWED,
                                                               "sind-zahnimplantate-in-der-tuerkei-sicher", "file"))
        self.assertEqual(de.source_hash, post.compute_source_hash())

    def test_detail_page_author_box_schema_and_sitemap(self):
        self._seed()
        post = BlogPost.objects.get(slug="is-it-safe-to-get-dental-implants-in-turkey")
        url = post.get_absolute_url("en")
        self.assertEqual(url, "/blog/safety-and-quality/is-it-safe-to-get-dental-implants-in-turkey/")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        self.assertIn("Written by", html)
        self.assertIn("Dr. Dt. Devrim Biriken Sipahi", html)
        self.assertIn("Medically reviewed by", html)
        self.assertIn("Dt. Ekin Sipahi", html)
        self.assertIn('data-track-section="author"', html)
        self.assertIn('<img loading="lazy" alt="Autoclave" src="/static/img/blog/implant-safety/autoclave.jpg"', html)
        # Yazı içi CTA'lar: "bizi tanıyın" kutusu 3. H2'den hemen önce, tek cümlelik röntgen çağrısı gövde sonunda
        self.assertIn('data-track-section="cta-about"', html)
        self.assertLess(html.index('data-track-section="cta-about"'), html.index('<h2 id="what-to-ask-any-clinic"'))
        self.assertGreater(html.index('data-track-section="cta-about"'), html.index('<h2 id="when-we-say-no"'))
        self.assertIn("Affordable dental treatment in Turkey", html)
        self.assertIn('data-track-section="cta-inline"', html)
        self.assertIn("Send your X-ray on WhatsApp", html)
        schemas = [json.loads(s) for s in self._ld_json(html)]
        article = next(s for s in schemas if s.get("@type") == "MedicalWebPage")
        self.assertEqual(article["author"]["name"], "Dr. Dt. Devrim Biriken Sipahi")
        self.assertTrue(article["author"]["@id"].endswith("/dentists/devrim-biriken-sipahi/#person"))
        self.assertEqual(article["reviewedBy"]["name"], "Dt. Ekin Sipahi")
        self.assertEqual([u.rsplit("/", 1)[1] for u in article["image"]], ["hero.jpg", "autoclave.jpg"])
        self.assertEqual(article["about"], {"@type": "MedicalProcedure", "name": "Dental Implants"})
        self.assertEqual(article["audience"]["audienceType"], "Patient")
        self.assertTrue(any(s.get("@type") == "FAQPage" for s in schemas))
        # Hekim sayfasındaki Person aynı @id'yi taşır (tek kimlik)
        d = self.client.get("/dentists/devrim-biriken-sipahi/").content.decode()
        self.assertIn('"@id": "%s"' % article["author"]["@id"], d)
        # Almanca sürüm kendi slug'ıyla açılır, hreflang iki dili listeler
        de_url = post.get_absolute_url("de")
        self.assertEqual(de_url, "/de/blog/sicherheit-und-qualitaet/sind-zahnimplantate-in-der-tuerkei-sicher/")
        r = self.client.get(de_url)
        self.assertEqual(r.status_code, 200)
        self.assertIn('hreflang="de"', r.content.decode())
        # İç linkler: hekim sayfası (yazar) ve işaret edilen rehber sayfası yazıya link verir
        self.assertEqual(post.related_guides, ["dental-care-turkey"])
        self.assertIn(url, self.client.get("/dentists/devrim-biriken-sipahi/").content.decode())
        call_command("seed_topics", no_keywords=True, stdout=io.StringIO())
        g = self.client.get("/guide/dental-care-turkey/")
        self.assertEqual(g.status_code, 200)
        self.assertIn(url, g.content.decode())
        self.assertIn("From our dentists", g.content.decode())
        self.assertNotIn(url, self.client.get("/guide/dental-tourism/").content.decode())
        # Sitemap
        from django.conf import settings

        sm = self.client.get("/sitemap-blog.xml").content.decode()
        self.assertIn(f"<loc>{settings.SITE_URL}{url}</loc>", sm)
        self.assertIn(f"<loc>{settings.SITE_URL}{de_url}</loc>", sm)
        self.assertNotIn("/fr/blog/", sm)

    @staticmethod
    def _ld_json(html):
        import re

        return re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)

    def test_idempotent_and_file_wins(self):
        self._seed()
        post = BlogPost.objects.get(slug="is-it-safe-to-get-dental-implants-in-turkey")
        updated, tr_updated = post.updated_at, post.translations.get(language_code="de").updated_at
        out = self._seed()
        post.refresh_from_db()
        self.assertEqual(post.updated_at, updated)  # değişiklik yok → kayıt yazılmadı, dateModified oynamadı
        self.assertEqual(post.translations.get(language_code="de").updated_at, tr_updated)
        self.assertIn("unchanged=2", out)
        # Dosya değişti → DB güncellenir
        self._write("en.md", (POST_EN % {"published": "2026-11-18"}).replace("not on the country", "never on the country"))
        self._seed()
        post.refresh_from_db()
        self.assertIn("never on the country", post.excerpt)
        self.assertGreater(post.updated_at, updated)

    def test_future_date_hidden_until_publish_day(self):
        future = (timezone.now() + timedelta(days=3)).date().isoformat()
        self._write("en.md", POST_EN % {"published": future})
        self._seed()
        post = BlogPost.objects.get(slug="is-it-safe-to-get-dental-implants-in-turkey")
        self.assertFalse(post.is_published)
        self.assertEqual(self.client.get("/blog/safety-and-quality/is-it-safe-to-get-dental-implants-in-turkey/").status_code, 404)
        self.assertNotIn("is-it-safe", self.client.get("/sitemap-blog.xml").content.decode())

    def test_export_writes_translation_files(self):
        self._seed()
        (self.post_dir / "de.md").unlink()
        call_command("seed_blog", dir=str(self.dir), export="is-it-safe-to-get-dental-implants-in-turkey",
                     stdout=io.StringIO())
        text = (self.post_dir / "de.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\ntitle: Sind Zahnimplantate in der Türkei sicher?"))
        self.assertIn("## Die kurze Antwort", text)
        # Dışa aktarılan dosya yeniden yüklenince değişiklik üretmez
        out = self._seed()
        self.assertIn("unchanged=2", out)

    def test_missing_category_is_an_error(self):
        from django.core.management.base import CommandError

        self._write("en.md", (POST_EN % {"published": "2026-11-18"}).replace("category: safety-and-quality",
                                                                             "category: nope"))
        with self.assertRaises(CommandError):
            self._seed()
