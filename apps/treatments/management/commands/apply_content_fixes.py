"""
apps/treatments/content_fixes.json'daki metin düzeltmelerini canlı tedavi içeriğine uygular (dil → [eski → yeni]).

Dosyadaki çeviriler (treatment_content/*.json) yalnızca EKSİK satırları doldurur; yayındaki bir cümle yanlışsa
(ör. kompozit lamina "1-2 yılda bir cila ister") düzeltme hem dosyada hem de bu listeyle veritabanında yapılır.
Idempotent: eski metin kalmadıysa hiçbir şey yazmaz. seed_translations (build / günlük cron) tarafından çağrılır.

    python manage.py apply_content_fixes
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.treatments.models import Treatment

FIXES_FILE = Path(__file__).resolve().parents[2] / "content_fixes.json"
TEXT_FIELDS = ("short_description", "body", "price_factors", "program", "refusals", "meta_description")


def _apply(obj, pairs):
    """obj: Treatment (kaynak dil) ya da TreatmentTranslation. Dönüş: değişen alan sayısı."""
    changed = []
    for field in TEXT_FIELDS:
        value = getattr(obj, field, None)
        if not isinstance(value, str) or not value:
            continue
        new = value
        for old, repl in pairs:
            new = new.replace(old, repl)
        if new != value:
            setattr(obj, field, new)
            changed.append(field)
    faq = getattr(obj, "faq", None)
    if isinstance(faq, list) and faq:
        new_faq, touched = [], False
        for item in faq:
            if isinstance(item, dict):
                q, a = str(item.get("question", "")), str(item.get("answer", ""))
                for old, repl in pairs:
                    q, a = q.replace(old, repl), a.replace(old, repl)
                if q != item.get("question") or a != item.get("answer"):
                    touched = True
                new_faq.append({**item, "question": q, "answer": a})
            else:
                new_faq.append(item)
        if touched:
            obj.faq = new_faq
            changed.append("faq")
    if changed:
        if hasattr(obj, "updated_at"):
            changed.append("updated_at")
        obj.save(update_fields=changed)
    return len(changed)


class Command(BaseCommand):
    help = "content_fixes.json'daki (dil → eski → yeni) metin düzeltmelerini tedavi içeriğine uygular (idempotent)"

    def handle(self, **o):
        if not FIXES_FILE.exists():
            self.stdout.write("content_fixes.json yok")
            return
        fixes = json.loads(FIXES_FILE.read_text(encoding="utf-8"))
        n = 0
        with transaction.atomic():
            for lang, items in fixes.items():
                pairs = [(i["old"], i["new"]) for i in items if i.get("old")]
                for t in Treatment.objects.all():
                    if t.source_language == lang:
                        n += _apply(t, pairs)
                    for tr in t.translations.filter(language_code=lang):
                        n += _apply(tr, pairs)
        self.stdout.write(self.style.SUCCESS(f"✓ içerik düzeltmesi: {n} alan güncellendi"))
