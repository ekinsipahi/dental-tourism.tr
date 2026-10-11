"""Mevcut yorumların çevirilerini apps/clinics/review_translations.json'dan yükler (yazar adına göre eşleşir)."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.clinics.models import Review

SRC = Path(__file__).resolve().parents[2] / "review_translations.json"


class Command(BaseCommand):
    help = "Yorum çevirilerini yükler"

    def handle(self, **o):
        data = json.loads(SRC.read_text(encoding="utf-8"))
        n = 0
        for r in Review.objects.exclude(text=""):
            tr = data.get(r.author_name)
            if tr:
                Review.objects.filter(pk=r.pk).update(text_translations={**tr, **(r.text_translations or {})})
                n += 1
        self.stdout.write(self.style.SUCCESS(f"✓ {n} yorumun çevirisi yüklendi"))
