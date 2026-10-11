"""
Şablonlardaki {% cblock "anahtar" "alan" _("varsayılan") %} kullanımlarını tarar ve admin'de
düzenlenebilir ContentBlock kayıtlarını oluşturur (mevcut metinlere dokunmaz).

    python manage.py sync_content_blocks
"""
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import ContentBlock

PATTERN = re.compile(r'\{%\s*cblock\s+"([\w-]+)"\s+"(\w+)"\s+_\("((?:[^"\\]|\\.)*)"\)')

LABELS = {
    "home-hero": "Ana sayfa — Hero (bölüm)", "home-hero-eyebrow": "Ana sayfa — Hero üst etiketi",
    "home-hero-default": "Ana sayfa — Hero metni (varsayılan / Google'ın gördüğü)", "home-treatments": "Ana sayfa — Tedaviler bölümü",
    "home-reviews": "Ana sayfa — Yorumlar bölümü", "home-how": "Ana sayfa — Nasıl çalışır",
    "home-clinic-search": "Ana sayfa — Klinik arama", "home-contact": "Ana sayfa — İletişim formu",
    "home-faq": "Ana sayfa — SSS", "home-cta": "Ana sayfa — Son çağrı (CTA)", "clinics-list": "Klinikler sayfası",
}
SEO_PAGES = {
    "seo-home": "SEO — Ana sayfa title/description", "seo-about": "SEO — Hakkımızda", "seo-contact": "SEO — İletişim",
    "seo-treatments": "SEO — Tedaviler listesi", "seo-prices": "SEO — Fiyat listesi",
    "seo-clinics": "SEO — Klinikler listesi", "seo-blog": "SEO — Blog",
}


class Command(BaseCommand):
    help = "Şablonlardaki düzenlenebilir metinler için ContentBlock kayıtlarını oluşturur"

    def handle(self, *args, **o):
        found = {}
        for path in Path(settings.BASE_DIR, "templates").rglob("*.html"):
            for key, field, default in PATTERN.findall(path.read_text(encoding="utf-8")):
                found.setdefault(key, {}).setdefault(field, default.replace('\\"', '"'))
        created = updated = 0
        from django.conf import settings as dj

        dj.AUTO_TRANSLATE_ON_PUBLISH = False  # varsayılanlar zaten .po'da çevrili
        from apps.core.views import HOME_SECTIONS

        section_order = {f"home-{n}": (i + 1) * 10 for i, n in enumerate(HOME_SECTIONS)}
        for key, fields in sorted(found.items()):
            page = key.split("-")[0] if key.split("-")[0] in dict(ContentBlock.PAGE_CHOICES) else "global"
            label = LABELS.get(key) or next((v for k, v in LABELS.items() if key.startswith(k)),
                                            key.replace("-", " ").title())
            block, was_created = ContentBlock.objects.get_or_create(
                key=key, defaults={"page": page, "label": label, "order": section_order.get(key, 0),
                                   "source_language": "en"})
            changed = False
            for field, default in fields.items():
                if not getattr(block, field):
                    setattr(block, field, default)
                    changed = True
            if changed:
                block.save()
            created += was_created
            updated += changed and not was_created
        # Ana sayfa bölüm kontrol blokları (sıra + göster/gizle)
        for name in HOME_SECTIONS:
            ContentBlock.objects.get_or_create(key=f"home-{name}", defaults={
                "page": "home", "label": LABELS.get(f"home-{name}", f"Ana sayfa — {name}"),
                "order": section_order[f"home-{name}"], "source_language": "en"})
        for key, label in SEO_PAGES.items():
            ContentBlock.objects.get_or_create(key=key, defaults={"page": "global", "label": label,
                                                                  "source_language": "en", "auto_translate": True})
        self.stdout.write(self.style.SUCCESS(f"✓ {created} yeni, {updated} güncellenen içerik bloğu"))
