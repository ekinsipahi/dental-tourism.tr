from unittest import mock

from django.test import override_settings

from apps.blog.models import BlogCategory, BlogPost
from apps.localization.models import TranslationStatus
from apps.localization.registry import get_spec
from apps.localization.resolve import resolve_slug
from apps.localization.service import languages_needing_work, translate_object
from apps.treatments.models import Treatment

from .base import SeededTestCase, fake_translation


def _patch_llm():
    def fake(system, blocks, schema, effort="medium", max_tokens=0):
        lang = blocks[-1]["text"].split("code '")[1].split("'")[0]
        props = schema["properties"]
        spec = next(s for s in __import__("apps.localization.registry", fromlist=["x"]).all_specs().values()
                    if set(f.name for f in s.fields) == set(props))
        return fake_translation(spec, lang)
    return mock.patch("apps.localization.llm.generate_json", side_effect=fake)


@override_settings(ANTHROPIC_API_KEY="test-key")
class TranslationServiceTests(SeededTestCase):
    def setUp(self):
        super().setUp()
        self.post = BlogPost.objects.create(
            title="Dental implants guide", slug="dental-implants-guide", category=BlogCategory.objects.first(),
            content="## Intro\nText", status=BlogPost.STATUS_PUBLISHED, source_language="en")

    def test_translate_creates_live_translation_with_localized_slug(self):
        with _patch_llm():
            self.assertEqual(translate_object(self.post, "de"), "translated")
        tr = self.post.translations.get(language_code="de")
        self.assertEqual(tr.status, TranslationStatus.MACHINE)
        self.assertEqual(tr.slug, "slug-de-test")
        self.assertEqual(self.post.localized("de").title, "[de] text")

    def test_slug_is_stable_on_retranslation(self):
        with _patch_llm():
            translate_object(self.post, "de")
            self.post.content += "\nmore"
            self.post.save()
            translate_object(self.post, "de")
        self.assertEqual(self.post.translations.get(language_code="de").slug, "slug-de-test")

    def test_reviewed_translation_is_not_overwritten(self):
        with _patch_llm():
            translate_object(self.post, "fr")
        tr = self.post.translations.get(language_code="fr")
        tr.title = "Titre humain"
        tr.status = TranslationStatus.REVIEWED
        tr.save()
        self.post.content += "\nchanged"
        self.post.save()
        self.assertNotIn("fr", languages_needing_work(self.post))
        tr.refresh_from_db()
        self.assertEqual(tr.status, TranslationStatus.OUTDATED)
        self.assertEqual(tr.title, "Titre humain")

    def test_up_to_date_translation_is_skipped(self):
        with _patch_llm():
            translate_object(self.post, "nl")
            self.assertEqual(translate_object(self.post, "nl"), "up_to_date")

    def test_failed_llm_marks_failed(self):
        from apps.localization.llm import LLMError

        with mock.patch("apps.localization.llm.generate_json", side_effect=LLMError("boom")):
            self.assertEqual(translate_object(self.post, "it"), "failed")
        self.assertEqual(self.post.translations.get(language_code="it").status, TranslationStatus.FAILED)
        self.assertIn("it", languages_needing_work(self.post))

    def test_blog_detail_in_translated_language_and_301_for_wrong_slug(self):
        with _patch_llm():
            translate_object(self.post.category, "de")
            translate_object(self.post, "de")
        url_de = self.post.get_absolute_url("de")
        self.assertTrue(url_de.startswith("/de/blog/"))
        r = self.client.get(url_de)
        self.assertEqual(r.status_code, 200)
        self.assertIn('hreflang="de"', r.content.decode())
        self.assertIn('hreflang="en"', r.content.decode())
        # İngilizce slug ile Almanca URL → doğru Almanca URL'ye 301
        wrong = f"/de/blog/{self.post.category.slug}/{self.post.slug}/"
        r = self.client.get(wrong)
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r["Location"], url_de)

    def test_untranslated_post_redirects_to_source_language(self):
        r = self.client.get(f"/fr/blog/{self.post.category.slug}/{self.post.slug}/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], self.post.get_absolute_url("en"))

    def test_resolve_slug_from_other_language_requests_redirect(self):
        t = Treatment.objects.get(key="dental-implants")
        tr = t.translations.get(language_code="de")
        tr.status = TranslationStatus.MACHINE
        tr.save()
        res = resolve_slug(Treatment, "de", "dental-implants")
        self.assertEqual(res.redirect_to_lang, "de")
        res = resolve_slug(Treatment, "de", "zahnimplantate")
        self.assertIsNone(res.redirect_to_lang)
        self.assertEqual(res.obj, t)

    def test_all_specs_have_valid_schema(self):
        for model in (BlogPost, BlogCategory, Treatment):
            schema = get_spec(model).json_schema()
            self.assertFalse(schema["additionalProperties"])
            self.assertEqual(set(schema["required"]), set(schema["properties"]))
