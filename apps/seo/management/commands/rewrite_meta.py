"""
Meta title / description'ları dosyalardan veritabanına yazar (yalnızca bu iki alan; içerik EZİLMEZ).

  python manage.py rewrite_meta            # ne değişeceğini gösterir (dry-run)
  python manage.py rewrite_meta --apply    # yazar

Kaynaklar: apps/seo/topics.py + topic_content/<dil>.json (rehberler), apps/core/seed_content.py +
treatment_content/<dil>.json (tedaviler), apps/clinics/profile_meta.json (klinik + hekimler).
Metinlerdeki {rating} / {count} sayfa açılırken güncel Google puanıyla dolar (apps.core.seo.fill_proof).
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction


def _set(obj, lang, title, desc, apply, out):
    """Kaynak dildeyse nesnenin kendisine, değilse o dildeki çeviriye yazar."""
    if not title and not desc:
        return
    if lang == obj.source_language:
        target = obj
    else:
        target = obj.translations.filter(language_code=lang).first()
        if target is None:
            return
    if (target.meta_title, target.meta_description) == (title[:70], desc[:170]):
        return
    out.append(f"{obj.__class__.__name__}:{getattr(obj, 'key', None) or obj.slug}:{lang}")
    if apply:
        target.meta_title, target.meta_description = title[:70], desc[:170]
        target.save(update_fields=["meta_title", "meta_description"])


class Command(BaseCommand):
    help = "Meta title/description'ları dosyalardan veritabanına yazar"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")

    def handle(self, apply=False, **o):
        from apps.clinics.models import Clinic, Doctor
        from apps.core import seed_content as S
        from apps.seo.models import SeoTopic
        from apps.seo.topics import TOPICS
        from apps.treatments.models import Treatment
        from dental_tourism.languages import LANGUAGE_META

        base = Path(settings.BASE_DIR)
        changed = []
        with transaction.atomic():
            topic_files = {lg: json.loads((base / f"apps/seo/topic_content/{lg}.json").read_text(encoding="utf-8"))
                           for lg in LANGUAGE_META if (base / f"apps/seo/topic_content/{lg}.json").exists()}
            for topic in SeoTopic.objects.filter(key__in=TOPICS):
                en = TOPICS[topic.key]["en"]
                for lg in LANGUAGE_META:
                    d = en if lg == "en" else topic_files.get(lg, {}).get(topic.key)
                    if d:
                        _set(topic, lg, d["meta_title"], d["meta_description"], apply, changed)

            tr_files = {lg: json.loads((base / f"apps/treatments/treatment_content/{lg}.json").read_text(encoding="utf-8"))
                        for lg in LANGUAGE_META if (base / f"apps/treatments/treatment_content/{lg}.json").exists()}
            src = {t["key"]: t for t in S.TREATMENTS}
            for t in Treatment.objects.filter(key__in=src):
                for lg in LANGUAGE_META:
                    d = src[t.key] if lg == "en" else tr_files.get(lg, {}).get(t.slug)
                    if d:
                        _set(t, lg, d["meta_title"], d["meta_description"], apply, changed)

            prof = json.loads((base / "apps/clinics/profile_meta.json").read_text(encoding="utf-8"))
            clinic = Clinic.primary()
            targets = [(clinic, prof["clinic"])] + [
                (doc, prof[doc.slug]) for doc in Doctor.objects.filter(clinic=clinic, slug__in=prof)]
            for obj, data in targets:
                for lg, d in data.items():
                    _set(obj, lg, d["meta_title"], d["meta_description"], apply, changed)
            if not apply:
                transaction.set_rollback(True)
        self.stdout.write(f"{len(changed)} kayıt {'güncellendi' if apply else 'güncellenecek (dry-run)'}")
        for c in changed[:400]:
            self.stdout.write("  " + c)
