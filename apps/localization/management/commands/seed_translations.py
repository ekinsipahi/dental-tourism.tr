"""
Dosyalardaki (API anahtarı gerekmeyen) tüm çevirileri yükler — yalnızca EKSİK olanları; admin düzenlemelerini EZMEZ.
Render build'inde her deploy'da çalışır (build.sh): yeni bir dil eklendiğinde içerikler canlı DB'ye böyle taşınır.

  python manage.py seed_translations

Sırasıyla: şehir adları (LANGUAGE_META) → tedaviler → klinik/hekim profilleri → rehberler → yorumlar.
Keyword tablosu (yüzlerce upsert) yalnızca keyword'ü hiç olmayan bir dil varsa yeniden yazılır; her deploy'da değil.
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Şehir, tedavi, profil, rehber ve yorum çevirilerini dosyalardan yükler (yalnızca eksikler)"

    def handle(self, **o):
        from django.conf import settings

        # Yükleme sırasında kayıt sinyali AI çevirisini tetiklemesin (dosyadaki çeviri yazılmadan önce MACHINE
        # çeviri oluşursa seed komutları onu "canlı" sayıp atlar)
        settings.AUTO_TRANSLATE_ON_PUBLISH = False

        from dental_tourism.languages import LANGUAGE_META

        from apps.core.management.commands.seed_data import Command as SeedData
        from apps.seo.models import Keyword

        SeedData(stdout=self.stdout, stderr=self.stderr)._city()
        call_command("seed_treatment_translations", stdout=self.stdout)
        call_command("seed_profile_translations", stdout=self.stdout)
        missing_kw = set(LANGUAGE_META) - set(Keyword.objects.values_list("language", flat=True).distinct())
        call_command("seed_topics", no_keywords=not missing_kw, stdout=self.stdout)
        call_command("seed_review_translations", stdout=self.stdout)
