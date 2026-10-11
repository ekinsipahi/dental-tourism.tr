"""
Ana klinik + hekim profil çevirilerini apps/clinics/profile_content/<dil>.json dosyalarından yükler.

  python manage.py seed_profile_translations [--overwrite]

Dosya: {tagline, short_description, p1..p4, weekend_h, weekend, location_h, location, faq: [[s, c]...],
        meta_title, meta_description, doctor_title, doctor_meta_title, ekin_title}
Klinik açıklaması = p1..p4 + hafta sonu + konum bölümleri; Dr. Devrim bio = p1..p3; Dt. Ekin bio = p4.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from dental_tourism.languages import LANGUAGE_META

from apps.clinics.models import Clinic, ClinicTranslation, Doctor, DoctorTranslation
from apps.localization.models import TranslationStatus

CONTENT_DIR = Path(__file__).resolve().parents[2] / "profile_content"
LIVE = (TranslationStatus.MACHINE, TranslationStatus.REVIEWED)


def _save(model, fk, obj, lang, values, overwrite):
    tr = model.objects.filter(**{fk: obj, "language_code": lang}).first()
    if tr and tr.status in LIVE and not overwrite:
        return 0
    tr = tr or model(**{fk: obj, "language_code": lang})
    for k, v in values.items():
        setattr(tr, k, v)
    tr.status = TranslationStatus.REVIEWED
    tr.source_hash = obj.compute_source_hash()
    tr.model_used = "seed_profile_translations"
    tr.translated_at = timezone.now()
    tr.error = ""
    tr.save()
    return 1


class Command(BaseCommand):
    help = "Klinik ve hekim profil çevirilerini yükler"

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true")

    def handle(self, overwrite=False, **o):
        clinic = Clinic.primary()
        devrim = Doctor.objects.filter(clinic=clinic, slug="devrim-biriken-sipahi").first()
        ekin = Doctor.objects.filter(clinic=clinic, slug="ekin-sipahi").first()
        n = 0
        with transaction.atomic():
            for lang in LANGUAGE_META:
                f = CONTENT_DIR / f"{lang}.json"
                if not f.exists():
                    continue
                d = json.loads(f.read_text(encoding="utf-8"))
                desc = "\n\n".join([d["p1"], d["p2"], d["p3"], d["p4"], "## " + d["weekend_h"], d["weekend"],
                                    "## " + d["location_h"], d["location"]])
                n += _save(ClinicTranslation, "clinic", clinic, lang, {
                    "tagline": d["tagline"], "short_description": d["short_description"], "description": desc,
                    "faq": [{"question": q, "answer": a} for q, a in d["faq"]],
                    "meta_title": d["meta_title"][:70], "meta_description": d["meta_description"][:170]}, overwrite)
                if devrim:
                    n += _save(DoctorTranslation, "doctor", devrim, lang, {
                        "title_display": d["doctor_title"], "bio": "\n\n".join([d["p1"], d["p2"], d["p3"]]),
                        "meta_title": d["doctor_meta_title"][:70], "meta_description": d["short_description"][:170]},
                        overwrite)
                if ekin:
                    n += _save(DoctorTranslation, "doctor", ekin, lang, {
                        "title_display": d["ekin_title"], "bio": d["p4"], "meta_title": "", "meta_description": ""},
                        overwrite)
        self.stdout.write(self.style.SUCCESS(f"✓ {n} profil çevirisi yazıldı"))
