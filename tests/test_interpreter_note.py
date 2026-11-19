"""Rusça sayfalarda tercüman notu; klinik dilleri tr/en (hekim, 19.11.2026)."""
from apps.clinics.models import Clinic

from .base import SeededTestCase


class InterpreterNoteTests(SeededTestCase):
    def test_russian_pages_mention_interpreter_only_in_russian(self):
        ru = self.client.get("/ru/").content.decode()
        self.assertIn("русскоговорящий переводчик", ru)
        en = self.client.get("/").content.decode()
        self.assertNotIn("interpreter", en)

    def test_clinic_languages_are_turkish_and_english(self):
        self.assertEqual(Clinic.primary().languages_spoken, ["tr", "en"])
