"""
Tedavi çevirilerini apps/treatments/treatment_content/<dil>.json dosyalarından yükler (API anahtarı gerekmez).

  python manage.py seed_treatment_translations             # eksik / başarısız / pending dilleri doldurur
  python manage.py seed_treatment_translations --overwrite # dosyadakini yeniden yazar (yayındaki slug korunur)

Dosya formatı: {"<EN slug>": {"name", "slug", "short_description", "body", "faq": [[soru, cevap]...],
                              "meta_title", "meta_description", "focus_keyword"}}
FİYAT RAKAMI YAZILMAZ.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from dental_tourism.languages import LANGUAGE_META

from apps.localization.models import TranslationStatus
from apps.treatments.models import Treatment, TreatmentTranslation

CONTENT_DIR = Path(__file__).resolve().parents[2] / "treatment_content"


class Command(BaseCommand):
    help = "Tedavi çevirilerini JSON dosyalarından yükler"

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true")

    def handle(self, overwrite=False, **o):
        n = 0
        with transaction.atomic():
            for lang in LANGUAGE_META:
                f = CONTENT_DIR / f"{lang}.json"
                if not f.exists():
                    continue
                data = json.loads(f.read_text(encoding="utf-8"))
                for t in Treatment.objects.filter(slug__in=data):
                    d = data[t.slug]
                    tr = TreatmentTranslation.objects.filter(treatment=t, language_code=lang).first()
                    live = tr and tr.status in (TranslationStatus.MACHINE, TranslationStatus.REVIEWED)
                    if live and not overwrite:
                        continue
                    tr = tr or TreatmentTranslation(treatment=t, language_code=lang)
                    if not (tr.pk and tr.slug and live):
                        tr.slug = d["slug"]
                    tr.name = d["name"]
                    tr.short_description = d["short_description"]
                    tr.body = d["body"]
                    tr.faq = [{"question": q, "answer": a} for q, a in d["faq"]]
                    tr.meta_title = d["meta_title"][:70]
                    tr.meta_description = d["meta_description"][:170]
                    tr.focus_keyword = d.get("focus_keyword", "")
                    tr.status = TranslationStatus.REVIEWED
                    tr.source_hash = t.compute_source_hash()
                    tr.model_used = "seed_treatment_translations"
                    tr.translated_at = timezone.now()
                    tr.error = ""
                    tr.save()
                    n += 1
        self.stdout.write(self.style.SUCCESS(f"✓ {n} tedavi çevirisi yazıldı"))
