"""
Zamanlanmış işler — Redis/Celery YOK, sistem cron'u ile çalıştırılır.

  python manage.py periodic                       # tüm işler
  python manage.py periodic --job translations    # tek iş

Önerilen crontab:
  15 * * * *   cd /srv/app && venv/bin/python manage.py periodic --job translations --job conversions
  0 4 * * *    cd /srv/app && venv/bin/python manage.py periodic --job related --job cleanup
  0 3 * * 1    cd /srv/app && venv/bin/python manage.py periodic --job persona
"""
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


def job_translations():
    from apps.localization.tasks import translate_missing

    return translate_missing()


def job_related():
    from apps.blog.tasks import compute_related_posts

    return compute_related_posts()


def job_persona():
    from apps.persona.tasks import retrain_ml_model

    return retrain_ml_model()


def job_cleanup():
    from django.core.management import call_command

    from apps.tracking.tasks import cleanup_old_sessions

    call_command("clearsessions", verbosity=0)  # süresi dolmuş django_session satırları (90 gün)
    return cleanup_old_sessions()


def job_conversions():
    """Son 24 saatte başarısız olan reklam dönüşümlerini yeniden gönderir."""
    from apps.tracking.models import AdConversion
    from apps.tracking.tasks import send_google_conversion, send_meta_conversion

    n = 0
    since = timezone.now() - timedelta(hours=24)
    for conv in AdConversion.objects.filter(status=AdConversion.STATUS_FAILED, created_at__gte=since):
        if conv.platform == AdConversion.PLATFORM_GOOGLE:
            send_google_conversion(conv.id)
        else:
            send_meta_conversion(conv.id)
        n += 1
    return {"retried": n}


JOBS = {"translations": job_translations, "related": job_related, "persona": job_persona,
        "cleanup": job_cleanup, "conversions": job_conversions}


class Command(BaseCommand):
    help = "Zamanlanmış işler (cron ile çalıştırın; Redis/Celery gerekmez)"

    def add_arguments(self, parser):
        parser.add_argument("--job", action="append", choices=list(JOBS), help="Tekrarlanabilir; boşsa hepsi")

    def handle(self, job=None, **o):
        for name in job or list(JOBS):
            try:
                result = JOBS[name]()
                self.stdout.write(f"✓ {name}: {result}")
            except Exception as e:  # noqa: BLE001 — bir işin hatası diğerlerini durdurmasın
                logger.exception("periodic job %s failed", name)
                self.stdout.write(self.style.ERROR(f"✗ {name}: {e}"))
