"""Hekimin düzelttiği iddialar: kompozit lamina "1-2 yılda bir cila ister / 5-7 yıl dayanır" cümleleri ne dosyalarda
ne de (apply_content_fixes sonrası) veritabanında kalmalı."""
import json
import re
from pathlib import Path

from django.core.management import call_command

from .base import SeededTestCase

ROOT = Path(__file__).resolve().parents[1]
WRONG = re.compile(r"polishing every year or two|regular polishing|bir-iki yılda bir cila|düzenli cilayla|alle ein bis zwei Jahre poliert|"
                   r"раз в один-два года|раз на один-два роки|cada uno o dos años|ogni uno-due anni|tous les un à deux ans|"
                   r"elke één à twee jaar|co rok–dwa|la unul-doi ani|на всяка година-две|bir-iki ildən bir|hvert eller hvert andet år|"
                   r"hvert eller annethvert år|poleras vartannat år|كل سنة أو سنتين|needs polishing and repairs more often")


class ContentFixTests(SeededTestCase):
    def test_files_no_longer_carry_the_wrong_composite_claims(self):
        files = [ROOT / "apps/core/seed_content.py", *sorted((ROOT / "apps/treatments/treatment_content").glob("*.json"))]
        for f in files:
            text = f.read_text(encoding="utf-8")
            self.assertIsNone(WRONG.search(text), f.name)
        fixes = json.loads((ROOT / "apps/treatments/content_fixes.json").read_text(encoding="utf-8"))
        self.assertEqual(len(fixes), 17)
        for lang, items in fixes.items():
            self.assertEqual(len(items), 3, lang)
            self.assertTrue(all("20" in i["new"] for i in items[:2]), lang)  # 20 yıldır kullanan hastalar

    def test_apply_content_fixes_updates_live_rows_once(self):
        from apps.localization.models import TranslationStatus
        from apps.treatments.models import Treatment

        t = Treatment.objects.get(key="composite-veneers")
        t.body = t.body + "\n\nThey are faster and more affordable than porcelain and fully reversible, but they can stain and chip more easily and need polishing every year or two."
        t.faq = [{"question": "How long do composite veneers last?", "answer": "Typically 5–7 years with good care and regular polishing."}]
        t.save()
        de = t.get_translation("de", live_only=False)
        de.body, de.status = "## Vor- und Nachteile\nSie sind schneller und günstiger als Keramik und vollständig rückgängig zu machen, verfärben sich aber leichter, können eher absplittern und müssen alle ein bis zwei Jahre poliert werden.", TranslationStatus.REVIEWED
        de.save()
        call_command("apply_content_fixes", verbosity=0)
        t.refresh_from_db(); de.refresh_from_db()
        self.assertIn("20 years", t.body)
        self.assertNotIn("every year or two", t.body)
        self.assertIn("20 years", t.faq[0]["answer"])
        self.assertIn("seit 20 Jahren", de.body)
        self.assertNotIn("ein bis zwei Jahre", de.body)
        html = self.client.get("/treatments/composite-veneers/").content.decode()
        self.assertIn("20 years", html)
        self.assertNotIn("every year or two", html)
        before = (t.updated_at, de.updated_at)
        call_command("apply_content_fixes", verbosity=0)  # ikinci çalıştırma hiçbir şey yazmaz
        t.refresh_from_db(); de.refresh_from_db()
        self.assertEqual(before, (t.updated_at, de.updated_at))
