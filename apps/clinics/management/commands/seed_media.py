"""
Kliniğin GERÇEK fotoğraflarını static/img/clinic/ altından veritabanına bağlar (URL olarak).

Render gibi geçici diskli sunucularda media/ yüklemeleri her deploy'da silinir; bu görseller repoda
durduğu için WhiteNoise ile kalıcı sunulur. Admin'den yeni görsel eklemek için "image_url" alanına link
verilebilir (ya da kalıcı bir depolama — S3/Supabase Storage — bağlanabilir).

  python manage.py seed_media
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.templatetags.static import static

from apps.clinics.models import BeforeAfterCase, Clinic, ClinicImage, Doctor

GALLERY = [  # (dosya, tür, alt, slider'da göster)
    ("devrim-slide1.jpg", "room", "Dr. Devrim Sipahi treating a patient, dental clinic Şişli Istanbul", True),
    ("devrim-slide2.jpg", "room", "Dental treatment at our clinic in Şişli, Istanbul", True),
    ("devrim-contact.jpg", "room", "Dental clinic in Şişli, Istanbul — treatment room", True),
    ("IMG_0543.jpg", "room", "Dental clinic Şişli Istanbul — clinic interior", True),
    ("devrim-slide3.jpg", "team", "Dr. Dt. Devrim Biriken Sipahi, dentist in Istanbul", True),
    ("devrim-slide4.jpg", "team", "Dr. Dt. Devrim Biriken Sipahi at work, Istanbul", True),
    ("devrim3.jpg", "room", "Dr. Devrim Biriken Sipahi examining a patient, Şişli Istanbul", True),
]


class Command(BaseCommand):
    help = "Gerçek klinik fotoğraflarını (static/img/clinic) veritabanına bağlar"

    def handle(self, **o):
        clinic = Clinic.primary()
        n = 0
        for i, (fname, kind, alt, hero) in enumerate(GALLERY):
            url = static(f"img/clinic/gallery/{fname}")
            if not ClinicImage.objects.filter(clinic=clinic, image_url=url).exists() and \
                    not ClinicImage.objects.filter(clinic=clinic, image__endswith=fname).exists():
                ClinicImage.objects.create(clinic=clinic, image_url=url, alt=alt, kind=kind, show_in_hero=hero, order=i)
                n += 1
        if not clinic.cover_image and not clinic.cover_image_url:
            clinic.cover_image_url = static("img/clinic/cover.jpg")
            clinic.save(update_fields=["cover_image_url"])
        devrim = Doctor.objects.filter(clinic=clinic, slug="devrim-biriken-sipahi").first()
        if devrim and not devrim.photo and not devrim.photo_url:
            devrim.photo_url = static("img/clinic/dr-devrim-sipahi.jpg")
            devrim.save(update_fields=["photo_url"])
        # Önce-sonra vakaları (apps/clinics/case_content.json — 16 dilde başlık + açıklama, sıra: zirkonya → kompozit → Sanem, Hazan)
        from apps.treatments.models import Treatment

        old = json.loads((Path(settings.BASE_DIR) / "apps/core/data/old_site_content.json").read_text(encoding="utf-8"))
        cases = json.loads((Path(settings.BASE_DIR) / "apps/clinics/case_content.json").read_text(encoding="utf-8"))
        for c in cases:
            key = c["key"]
            obj = BeforeAfterCase.objects.filter(clinic=clinic, key=key).first()
            if obj is None and key in old.get("cases", {}):
                obj = BeforeAfterCase.objects.filter(clinic=clinic, caption__startswith=old["cases"][key]["en"][:60]).first()
            en = c["text"]["en"]
            fields = dict(key=key, title=en["title"], caption=en["caption"], translations=c["text"], order=c["order"],
                          treatment=Treatment.objects.filter(slug=c["treatment"]).first() if c["treatment"] else None,
                          before_image_url=static(f"img/clinic/cases/{key}-before.jpg"),
                          after_image_url=static(f"img/clinic/cases/{key}-after.jpg"))
            if obj is None:
                BeforeAfterCase.objects.create(clinic=clinic, is_published=True, patient_consent=True, **fields)
                n += 1
            else:
                for f, v in fields.items():
                    setattr(obj, f, v)
                obj.save()
        self.stdout.write(self.style.SUCCESS(f"✓ {n} medya kaydı eklendi"))
