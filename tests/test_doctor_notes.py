"""Hekimin notları: fiyat / paket / tedavi sayfalarında şablon metnin yerine geçen, dile göre gelen birinci ağızdan
içerik; hekim kutusunun alanlardan (üniversite, mezuniyet, üyelik) beslenmesi; Dt. Ekin'in bilgileri."""
from django.core.management import call_command

from .base import SeededTestCase


class DoctorNoteTests(SeededTestCase):
    def _t(self):
        from apps.treatments.models import Treatment

        return Treatment.objects.get(key="root-canal")

    def test_price_page_shows_dentist_note_instead_of_generic_bullets(self):
        t = self._t()
        self.assertIn("Your diagnosis: how many teeth and their condition", self.client.get("/prices/root-canal-treatment/").content.decode())
        t.price_factors = "The number of roots and canals changes the quote.\n\nCanals close to the sinus are difficult."
        t.save()
        html = self.client.get("/prices/root-canal-treatment/").content.decode()
        self.assertIn("The number of roots and canals changes the quote.", html)
        self.assertIn("Canals close to the sinus are difficult.", html)
        self.assertIn("The dentist's note", html)
        self.assertNotIn("Your diagnosis: how many teeth and their condition", html)

    def test_package_and_treatment_pages_show_program_and_refusals_in_the_page_language(self):
        t = self._t()
        t.program, t.refusals = "We start as soon as you arrive.", "We decline unrealistic requests."
        t.save()
        from apps.localization.models import TranslationStatus

        tr = t.get_translation("de", live_only=False)  # seed_data: ad + slug var, içerik beklemede → canlı yap
        tr.program, tr.refusals = "Wir beginnen gleich nach Ihrer Ankunft.", "Unrealistische Wünsche lehnen wir ab."
        tr.status = TranslationStatus.REVIEWED
        tr.save()
        pkg = self.client.get("/packages/root-canal-treatment/").content.decode()
        self.assertIn("We start as soon as you arrive.", pkg)
        self.assertNotIn("How to choose the best", pkg)  # şablon paragrafı hekim notuyla yer değiştirir
        self.assertIn("We decline unrealistic requests.", self.client.get("/treatments/root-canal-treatment/").content.decode())
        de = self.client.get("/de/pakete/" + tr.slug + "/").content.decode()
        self.assertIn("Wir beginnen gleich nach Ihrer Ankunft.", de)
        self.assertIn("Tag für Tag", de)

    def test_notes_are_served_from_memory_after_first_request(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        t = self._t()
        t.price_factors = "Experience is the biggest factor."
        t.save()
        self.client.get("/")
        self.client.get("/prices/root-canal-treatment/")
        with CaptureQueriesContext(connection) as ctx:
            html = self.client.get("/prices/root-canal-treatment/").content.decode()
        self.assertIn("Experience is the biggest factor.", html)
        self.assertEqual(len(ctx.captured_queries), 0)


class DoctorFactsTests(SeededTestCase):
    def test_ekin_facts_are_seeded_once_and_shown(self):
        from apps.clinics.models import Clinic, Doctor

        Doctor.objects.create(clinic=Clinic.primary(), honorific="Dt.", name="Ekin Sipahi", slug="ekin-sipahi",
                              source_language="en", bio="Two generations, one line.")  # canlıda import_old_site oluşturur
        call_command("seed_profile_translations", verbosity=0)
        ekin = Doctor.objects.get(slug="ekin-sipahi")
        self.assertEqual((ekin.graduation_year, ekin.instagram), (2025, "dt.ekinsipahi"))
        self.assertIn("Kent", ekin.university)
        ekin.university = "Edited by admin"
        ekin.save()
        call_command("seed_profile_translations", verbosity=0)  # dolu alan ezilmez
        self.assertEqual(Doctor.objects.get(slug="ekin-sipahi").university, "Edited by admin")
        html = self.client.get("/dentists/ekin-sipahi/").content.decode()
        self.assertIn("2025", html)
        self.assertIn("instagram.com/dt.ekinsipahi/", html)

    def test_proof_box_uses_doctor_fields(self):
        from apps.clinics.models import Doctor

        lead = Doctor.objects.get(slug="devrim-biriken-sipahi")
        html = self.client.get("/prices/dental-implants/").content.decode()
        self.assertIn("Graduate of " + lead.university, html)
        for m in lead.memberships:
            self.assertIn(m, html)


class NoteSeedingTests(SeededTestCase):
    """seed_treatment_translations: hekim notları dosyadan dolar; yalnızca not eklendiğinde çevirinin kaynak hash'i
    tazelenir (AI yeniden çeviri / OUTDATED tetiklenmez); notla ilgisi olmayan kaynak değişikliği 'güncel' sayılmaz."""

    def _run(self, tmp, en, de):
        import json
        from unittest import mock

        from apps.treatments.management.commands import seed_treatment_translations as cmd

        (tmp / "en.json").write_text(json.dumps(en), encoding="utf-8")
        (tmp / "de.json").write_text(json.dumps(de), encoding="utf-8")
        with mock.patch.object(cmd, "CONTENT_DIR", tmp):
            call_command("seed_treatment_translations", verbosity=0)

    def test_notes_fill_and_hash_refresh_across_two_runs(self):
        import tempfile
        from pathlib import Path

        from apps.localization.models import TranslationStatus
        from apps.treatments.models import Treatment

        t = Treatment.objects.get(key="root-canal")
        de = t.get_translation("de", live_only=False)
        de.status, de.source_hash = TranslationStatus.REVIEWED, t.compute_source_hash()  # canlı, güncel çeviri
        de.save()
        slug = t.slug
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            self._run(tmp, {slug: {"price_factors": "Price A"}}, {slug: {"price_factors": "Preis A"}})
            t.refresh_from_db(); de.refresh_from_db()
            self.assertEqual((t.price_factors, de.price_factors), ("Price A", "Preis A"))
            self.assertEqual(de.source_hash, t.compute_source_hash())  # not eklendi → hâlâ güncel
            # ikinci deploy: yeni bir not alanı daha
            self._run(tmp, {slug: {"price_factors": "Price A", "program": "Prog B"}},
                      {slug: {"price_factors": "Preis A", "program": "Programm B"}})
            t.refresh_from_db(); de.refresh_from_db()
            self.assertEqual((t.program, de.program), ("Prog B", "Programm B"))
            self.assertEqual(de.source_hash, t.compute_source_hash())
            self.assertEqual(de.status, TranslationStatus.REVIEWED)
            # admin'de dolu alan ezilmez; notla ilgisi olmayan kaynak değişikliği hash'i 'güncel' yapmaz
            t.body, t.price_factors = t.body + "\n\nEdited by the dentist.", "Edited price note"
            t.save()
            self._run(tmp, {slug: {"price_factors": "Price A", "program": "Prog B"}},
                      {slug: {"price_factors": "Preis A", "program": "Programm B"}})
            t.refresh_from_db(); de.refresh_from_db()
            self.assertEqual(t.price_factors, "Edited price note")
            self.assertNotEqual(de.source_hash, t.compute_source_hash())
