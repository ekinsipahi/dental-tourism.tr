"""
Arka plan iş gönderimi.

Redis/Celery YOK: işler web sürecindeki SINIRLI bir thread havuzunda çalışır.
Periyodik işler (ML eğitimi, eksik çeviriler, temizlik) cron ile: `python manage.py periodic`.

Sızıntı önlemleri:
  * Her iş için yeni thread açılmaz — en fazla BACKGROUND_WORKERS (varsayılan 2) işçi thread'i olan tek bir havuz.
  * Aynı nesne için kuyrukta/çalışmakta olan bir çeviri işi varsa ikincisi eklenmez (tekilleştirme).
  * İşçi thread'inin açtığı DB bağlantıları iş bitince `connections.close_all()` ile KAPATILIR
    (close_old_connections yalnızca süresi dolanları kapatır; thread'e özel bağlantı açık kalırdı).
  * Kuyruk dolarsa (BACKGROUND_QUEUE_LIMIT) yeni iş reddedilir ve loglanır — bellek sınırsız büyümez.
Süreç yeniden başlarsa yarım kalan işler kaybolabilir; `python manage.py translate_content --missing` güvenle tamamlar.
"""
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.db import connections, transaction

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_executor = None
_inflight = set()   # tekilleştirme anahtarları
_pending = 0        # kuyruktaki + çalışan iş sayısı


def _pool():
    global _executor
    with _lock:
        if _executor is None:
            _executor = ThreadPoolExecutor(max_workers=getattr(settings, "BACKGROUND_WORKERS", 2),
                                           thread_name_prefix="bg-job")
        return _executor


def _submit(key, func, *args):
    global _pending
    with _lock:
        if key is not None and key in _inflight:
            logger.info("background job skipped (already queued): %s", key)
            return False
        if _pending >= getattr(settings, "BACKGROUND_QUEUE_LIMIT", 200):
            logger.warning("background queue full, job dropped: %s", key or func.__name__)
            return False
        _pending += 1
        if key is not None:
            _inflight.add(key)

    def _wrapped():
        global _pending
        try:
            func(*args)
        except Exception:  # noqa: BLE001 — arka plan işi web sürecini düşürmemeli
            logger.exception("background job failed: %s", key or getattr(func, "__name__", func))
        finally:
            connections.close_all()  # bu thread'in DB bağlantılarını kapat
            with _lock:
                _pending -= 1
                if key is not None:
                    _inflight.discard(key)

    _pool().submit(_wrapped)
    return True


def stats():
    with _lock:
        return {"pending": _pending, "inflight": sorted(map(str, _inflight))}


def _run_translation(label, pk, languages, force):
    from django.apps import apps

    from .service import translate_all

    model = apps.get_model(label)
    obj = model.objects.filter(pk=pk).first()
    if obj is not None:
        result = translate_all(obj, languages=languages, force=force)
        logger.info("translation job %s#%s: %s", label, pk, result)


def dispatch_translation(label, pk, languages, force=False):
    transaction.on_commit(lambda: _submit(("translate", label, pk), _run_translation, label, pk, languages, force))


def run_in_background(func, *args, **kwargs):
    """Genel amaçlı: sınırlı thread havuzunda, transaction commit'inden sonra çalıştırır."""
    transaction.on_commit(lambda: _submit(None, lambda: func(*args, **kwargs)))
