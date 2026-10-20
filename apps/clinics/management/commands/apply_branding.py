"""
"Dr. Devrim" kişisel markasını veritabanındaki metinlere uygular (apps/clinics/branding.py).

  python manage.py apply_branding            # ne değişeceğini gösterir (dry-run)
  python manage.py apply_branding --apply    # yazar

Yalnızca anlatı alanları: klinik (slogan, kısa açıklama, Hakkımızda hikâyesi, SSS), hekim biyografileri,
rehberler (giriş, metin, SSS), tedaviler ve içerik blokları. meta_title / meta_description, hasta yorumları,
görsel alt metinleri ve schema DEĞİŞMEZ. Hakkımızda hikâyesinde ilk geçişte tam ad parantez içinde kalır.
Tekrar çalıştırmak güvenlidir (idempotent).
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.clinics.branding import brandify, brandify_data

# Yasal metinler: veri sorumlusu vb. olarak TAM AD kalmalı
LEGAL_BLOCKS = {"page-privacy", "page-kvkk", "page-terms", "page-imprint"}

# (model yolu, alanlar, tam adı ilk geçişte koruyan alanlar)
TARGETS = [
    ("clinics.Clinic", ("tagline", "short_description", "description", "faq"), ("description",)),
    ("clinics.ClinicTranslation", ("tagline", "short_description", "description", "faq"), ("description",)),
    ("clinics.Doctor", ("bio", "title_display"), ()),
    ("clinics.DoctorTranslation", ("bio", "title_display"), ()),
    ("seo.SeoTopic", ("lead", "body", "faq"), ()),
    ("seo.SeoTopicTranslation", ("lead", "body", "faq"), ()),
    ("treatments.Treatment", ("short_description", "body", "faq"), ()),
    ("treatments.TreatmentTranslation", ("short_description", "body", "faq"), ()),
    ("core.ContentBlock", ("eyebrow", "title", "subtitle", "body", "items"), ()),
    ("core.ContentBlockTranslation", ("eyebrow", "title", "subtitle", "body", "items"), ()),
]


def _fk(model):
    return next(f.name for f in model._meta.get_fields() if f.many_to_one and f.related_model.__name__ == "ContentBlock")


class Command(BaseCommand):
    help = "Dr. Devrim kişisel markasını veritabanı metinlerine uygular"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")

    def handle(self, apply=False, **o):
        from django.apps import apps

        changed = []
        with transaction.atomic():
            for path, fields, keep_full in TARGETS:
                Model = apps.get_model(path)
                present = [f for f in fields if any(x.name == f for x in Model._meta.get_fields())]
                qs = Model.objects.all()
                if path == "core.ContentBlock":
                    qs = qs.exclude(key__in=LEGAL_BLOCKS)
                elif path == "core.ContentBlockTranslation":
                    qs = qs.exclude(**{f"{_fk(Model)}__key__in": LEGAL_BLOCKS})
                for row in qs.values("pk", *present):
                    upd = {}
                    for f in present:
                        old = row[f]
                        new = brandify(old, keep_full_first=f in keep_full) if isinstance(old, str) else brandify_data(old)
                        if new != old:
                            upd[f] = new
                    if upd:
                        changed.append(f"{path}#{row['pk']}: {', '.join(upd)}")
                        if apply:
                            Model.objects.filter(pk=row["pk"]).update(**upd)
            if not apply:
                transaction.set_rollback(True)
        if apply:
            from django.core.cache import cache

            cache.clear()
        self.stdout.write(f"{len(changed)} kayıt {'güncellendi' if apply else 'güncellenecek (dry-run)'}")
        for c in changed:
            self.stdout.write("  " + c)
