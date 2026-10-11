"""
Klasörden veya URL listesinden klinik galerisine toplu görsel aktarma.
Büyük görseller max 2000px'e küçültülür ve JPEG (kalite 82) olarak optimize edilir.

  python manage.py import_images /path/to/folder --clinic dr-devrim-sipahi --kind interior --alt "Dental clinic Şişli Istanbul" --hero
  python manage.py import_images --urls links.txt --clinic dr-devrim-sipahi          # sadece link olarak ekler
  python manage.py import_images a.jpg b.jpg --clinic dr-devrim-sipahi --skip "img*"
"""
import fnmatch
import io
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from apps.clinics.models import Clinic, ClinicImage

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def optimize(path, max_px=2000, quality=82):
    from PIL import Image, ImageOps

    im = Image.open(path)
    im.draft("RGB", (max_px, max_px))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()


class Command(BaseCommand):
    help = "Klasör / dosya / URL listesinden klinik galerisine görsel aktarır"

    def add_arguments(self, parser):
        parser.add_argument("paths", nargs="*")
        parser.add_argument("--clinic", required=True)
        parser.add_argument("--kind", default="interior", choices=[k for k, _ in ClinicImage.KIND_CHOICES])
        parser.add_argument("--alt", default="", help="SEO alt metni (sonuna sıra no eklenir)")
        parser.add_argument("--hero", action="store_true", help="Slider'da göster")
        parser.add_argument("--urls", default="", help="Her satırda bir görsel URL'si olan dosya")
        parser.add_argument("--skip", action="append", default=[], help="Atlanacak dosya deseni (img*)")
        parser.add_argument("--max-px", type=int, default=2000)

    def handle(self, *args, paths, clinic, kind, alt, hero, urls, skip, max_px, **o):
        clinic_obj = Clinic.objects.filter(slug=clinic).first()
        if clinic_obj is None:
            raise CommandError(f"Klinik bulunamadı: {clinic}")
        files = []
        for p in map(Path, paths):
            if p.is_dir():
                files += sorted(f for f in p.iterdir() if f.suffix.lower() in EXTS)
            elif p.suffix.lower() in EXTS:
                files.append(p)
        files = [f for f in files if not any(fnmatch.fnmatch(f.name, pat) for pat in skip)]
        start = clinic_obj.images.count()
        n = 0
        for f in files:
            if clinic_obj.images.filter(image__icontains=f.stem.replace(" ", "_")[:40]).exists():
                self.stdout.write(f"  ⏭ {f.name} (zaten var)")
                continue
            n += 1
            img = ClinicImage(clinic=clinic_obj, kind=kind, show_in_hero=hero, order=start + n,
                              alt=f"{alt or clinic_obj.name} {start + n}".strip())
            img.image.save(f"{f.stem}.jpg", ContentFile(optimize(f, max_px)), save=True)
            self.stdout.write(f"  ✓ {f.name}")
        if urls:
            for line in Path(urls).read_text().splitlines():
                url = line.strip()
                if url.startswith("http") and not clinic_obj.images.filter(image_url=url).exists():
                    n += 1
                    ClinicImage.objects.create(clinic=clinic_obj, kind=kind, show_in_hero=hero, image_url=url,
                                               order=start + n, alt=f"{alt or clinic_obj.name} {start + n}".strip())
                    self.stdout.write(f"  ✓ {url}")
        self.stdout.write(self.style.SUCCESS(f"✓ {n} görsel eklendi → {clinic_obj}"))
