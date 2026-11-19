"""
Açılışta içerik seed'i — deploy'a (build.sh) ve cron'a bağımlı olmadan.

Render'daki build komutu seed adımlarını her zaman çalıştırmıyor (migrate çalışıyor, seed_translations çalışmıyor);
dosyadan gelen içerik (blog yazıları, çeviriler, hekim notları) canlıya ancak elle ya da gece cron'uyla ulaşıyordu.
Çözüm: web süreci (wsgi) ayağa kalkınca arka planda bir iş parçacığı `seed_media` + `seed_translations` koşar.
Hepsi idempotent ("yalnızca eksikler"); birden çok gunicorn worker'ı aynı anda başlarsa Postgres advisory lock ile
sırayla çalışırlar (ikincisi hiçbir şey yazmaz) ve her worker kendi süreç içi önbelleğini temizler — sitemap ve
listeler yeni içeriği hemen görür.

  BOOT_SEEDS=False  → kapalı (geliştirme/test); üretimde varsayılan açık.
"""
import logging
import threading
import time

from django.conf import settings

logger = logging.getLogger(__name__)
LOCK_KEY = 734_002_119  # pg_advisory_lock anahtarı (rastgele sabit)


def run_seeds_now(delay=0):
    """Seed'leri bu iş parçacığında, senkron çalıştırır. Dönüş: 'ok' | 'failed'."""
    import os

    from django.core.cache import caches
    from django.core.management import call_command
    from django.db import connection, connections

    if delay:
        time.sleep(delay)
    auto_translate = settings.AUTO_TRANSLATE_ON_PUBLISH  # seed komutları bunu kapatır; web sürecinde geri açılmalı
    locked = False
    try:
        if connection.vendor == "postgresql":
            with connection.cursor() as c:
                c.execute("SELECT pg_advisory_lock(%s)", [LOCK_KEY])  # diğer worker bitene kadar bekle
            locked = True
        with open(os.devnull, "w") as null:
            call_command("seed_media", verbosity=0, stdout=null)
            call_command("seed_translations", verbosity=0, stdout=null)
        status = "ok"
        logger.info("boot seeds ok")
    except Exception:
        status = "failed"
        logger.exception("boot seeds failed")
    finally:
        settings.AUTO_TRANSLATE_ON_PUBLISH = auto_translate
        try:
            if locked:
                with connection.cursor() as c:
                    c.execute("SELECT pg_advisory_unlock(%s)", [LOCK_KEY])
        except Exception:
            logger.exception("boot seeds: unlock failed")
        try:
            from apps.localization.memo import bump
            from apps.blog.models import BlogCategory, BlogPost

            caches["local"].clear()  # sitemap, bot sayfa önbelleği, listeler: yeni içerik görünsün
            bump(BlogPost)
            bump(BlogCategory)
        except Exception:
            logger.exception("boot seeds: cache clear failed")
        connections.close_all()
    return status


def start_boot_seeds():
    """wsgi.py'den çağrılır: ayarlar izin veriyorsa seed'leri arka plan iş parçacığında başlatır."""
    if not getattr(settings, "BOOT_SEEDS", False):
        return None
    t = threading.Thread(target=run_seeds_now, kwargs={"delay": 3}, name="boot-seeds", daemon=True)
    t.start()
    return t
