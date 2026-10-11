import tempfile

from apps.seo.audit import audit_fields
from apps.seo.models import Keyword
from apps.seo.services import import_csv, seed_keywords

from .base import SeededTestCase


class AuditTests(SeededTestCase):
    def test_detects_h1_and_meta_problems(self):
        issues = audit_fields(title="X", meta_title="x" * 80, meta_description="short", focus_keyword="implant",
                              body="# Title\nshort", kind="blog")
        text = " ".join(issues)
        self.assertIn("H1", text)
        self.assertIn("Meta title", text)
        self.assertIn("Meta description", text)

    def test_clean_content_passes(self):
        body = "Dental implants in Istanbul are explained here.\n\n## A\n" + "word " * 800 + \
               "\n## B\n[x](/treatments/) [y](/prices/)"
        issues = audit_fields(title="Dental implants guide", meta_title="Dental implants in Istanbul guide",
                              meta_description="Dental implants in Istanbul: " + "a" * 120, slug="dental-implants-guide",
                              focus_keyword="dental implants", body=body, kind="blog")
        self.assertEqual(issues, [])


class KeywordTests(SeededTestCase):
    def test_seed_is_idempotent_and_targets_pages(self):
        before = Keyword.objects.count()
        self.assertEqual(seed_keywords(["de"]), 0)  # seed_data zaten oluşturdu
        self.assertEqual(Keyword.objects.count(), before)

    def test_csv_import_tags_treatment_and_intent(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("Keyword,Volume,KD\nzahnimplantate türkei kosten erfahrung,1300,22\n")
        created, _ = import_csv(f.name, "de")
        self.assertEqual(created, 1)
        kw = Keyword.objects.get(term="zahnimplantate türkei kosten erfahrung")
        self.assertEqual(kw.search_volume, 1300)
        self.assertEqual(kw.treatment.key, "dental-implants")
        self.assertEqual(kw.persona_hint, "price")
