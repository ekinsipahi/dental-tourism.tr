"""
Kliniğin GERÇEK fotoğraflarını static/img/clinic/ altından veritabanına bağlar (URL olarak).

Render gibi geçici diskli sunucularda media/ yüklemeleri her deploy'da silinir; bu görseller repoda
durduğu için WhiteNoise ile kalıcı sunulur. Admin'den yeni görsel eklemek için "image_url" alanına link
verilebilir (ya da kalıcı bir depolama — S3/Supabase Storage — bağlanabilir).

  python manage.py seed_media
"""
import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.templatetags.static import static

from apps.clinics.models import BeforeAfterCase, Clinic, ClinicImage, Doctor

# Tedavi kartları / sayfaları için kliniğin ve hekimlerin GERÇEK fotoğrafları (tedavi anahtarı → dosya, alt metni)
TREATMENT_IMAGES = {
    "root-canal": ("gallery/devrim-slide1.jpg", "Dr. Devrim Sipahi treating a patient at our clinic in Şişli, Istanbul"),
    "tooth-filling": ("gallery/devrim-slide2.jpg", "Dental treatment at our clinic in Şişli, Istanbul"),
    "teeth-cleaning": ("gallery/devrim3.jpg", "Dr. Devrim Biriken Sipahi examining a patient, Şişli Istanbul"),
    "composite-veneers": ("gallery/devrim-contact.jpg", "Dr. Devrim Sipahi at work in the treatment room, Şişli Istanbul"),
    "teeth-whitening": ("dt-ekin-sipahi.jpg", "Dt. Ekin Sipahi, dentist at our family clinic in Şişli, Istanbul"),
    "zirconia-crowns": ("gallery/treatment-room.jpg", "Treatment room and dental chair at our clinic in Şişli, Istanbul"),
    "porcelain-veneers": ("gallery/devrim-slide3.jpg", "Dr. Dt. Devrim Biriken Sipahi, dentist in Istanbul"),
    "hollywood-smile": ("cover.jpg", "Dr. Dt. Devrim Biriken Sipahi at our clinic in Şişli, Istanbul"),
    "dental-implants": ("gallery/IMG_0543.jpg", "Dr. Devrim Sipahi and Dt. Ekin Sipahi performing implant surgery together"),
    "all-on-4": ("dr-devrim-sipahi.jpg", "Dr. Dt. Devrim Biriken Sipahi, 35+ years of experience, Şişli Istanbul"),
}

GALLERY = [  # (dosya, tür, alt, slider'da göster)
    ("devrim-slide1.jpg", "room", "Dr. Devrim Sipahi treating a patient, dental clinic Şişli Istanbul", True),
    ("devrim-slide2.jpg", "room", "Dental treatment at our clinic in Şişli, Istanbul", True),
    ("devrim-contact.jpg", "room", "Dental clinic in Şişli, Istanbul — treatment room", True),
    ("IMG_0543.jpg", "room", "Dental clinic Şişli Istanbul — clinic interior", True),
    ("devrim-slide3.jpg", "team", "Dr. Dt. Devrim Biriken Sipahi, dentist in Istanbul", True),
    ("devrim-slide4.jpg", "team", "Dr. Dt. Devrim Biriken Sipahi at work, Istanbul", True),
    ("devrim3.jpg", "room", "Dr. Devrim Biriken Sipahi examining a patient, Şişli Istanbul", True),
    ("treatment-room.jpg", "equipment", "Treatment room and dental chair at our clinic in Şişli, Istanbul", False),
    ("waiting-lounge.jpg", "interior", "Waiting lounge of our dental clinic in Şişli, Istanbul", False),
]


class Command(BaseCommand):
    help = "Gerçek klinik fotoğraflarını (static/img/clinic) veritabanına bağlar"

    def handle(self, **o):
        clinic = Clinic.primary()
        n = 0
        for i, (fname, kind, alt, hero) in enumerate(GALLERY):
            url = static(f"img/clinic/gallery/{fname}")
            if ClinicImage.objects.filter(clinic=clinic, image__endswith=fname).exists():
                continue
            # static() ortama göre hash'li ya da hash'siz döner (foo.jpg / foo.1a2b3c4d5e6f.jpg) → dosya adıyla eşleştir,
            # aynı fotoğrafın çift kaydını sil (sayfalarda aynı foto iki kez görünüyordu)
            stem, ext = fname.rsplit(".", 1)
            same = [im for im in ClinicImage.objects.filter(clinic=clinic, image_url__contains=f"/gallery/{stem}.")
                    if re.search(rf"/gallery/{re.escape(stem)}(\.[0-9a-f]{{12}})?\.{ext}$", im.image_url)]
            if same:
                keep = same[0]
                if keep.image_url != url:
                    keep.image_url = url
                    keep.save(update_fields=["image_url"])
                ClinicImage.objects.filter(pk__in=[im.pk for im in same[1:]]).delete()
            else:
                ClinicImage.objects.create(clinic=clinic, image_url=url, alt=alt, kind=kind, show_in_hero=hero, order=i)
                n += 1
        from apps.treatments.models import Treatment as _T

        for t in _T.objects.filter(key__in=TREATMENT_IMAGES):
            if not t.image and not t.image_url:
                fname, alt = TREATMENT_IMAGES[t.key]
                t.image_url, t.image_alt = static(f"img/clinic/{fname}"), alt
                t.save(update_fields=["image_url", "image_alt"])
                n += 1
        if not clinic.cover_image and not clinic.cover_image_url:
            clinic.cover_image_url = static("img/clinic/cover.jpg")
            clinic.save(update_fields=["cover_image_url"])
        for slug, fname in (("devrim-biriken-sipahi", "dr-devrim-sipahi.jpg"), ("ekin-sipahi", "dt-ekin-sipahi.jpg")):
            doctor = Doctor.objects.filter(clinic=clinic, slug=slug).first()
            if doctor and not doctor.photo and not doctor.photo_url:
                doctor.photo_url = static(f"img/clinic/{fname}")
                doctor.save(update_fields=["photo_url"])
        # Önce-sonra vakaları (apps/clinics/case_content.json — 17 dilde başlık + açıklama, sıra: zirkonya → kompozit → Sanem, Hazan)
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
