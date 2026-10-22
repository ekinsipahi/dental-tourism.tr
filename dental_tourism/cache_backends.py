"""
Redis'e dayanıklı önbellek: Render Key Value (ücretsiz plan) yeniden başlarsa ya da anlık kopmada Django'nun
yerleşik RedisCache'i istisna fırlatır ve SAYFA 500 verir. Burada önbellek hatası = "önbellekte yok" sayılır;
oturumlar (cached_db) ve tüm cache.get kullanıcıları veritabanından devam eder. Hata dakikada bir loglanır.
"""
import logging
import time

from django.core.cache.backends.redis import RedisCache

logger = logging.getLogger(__name__)
_last_log = 0.0


def _swallow(default):
    def deco(fn):
        def wrapper(self, *args, **kwargs):
            global _last_log
            try:
                return fn(self, *args, **kwargs)
            except Exception as e:  # noqa: BLE001 — redis.exceptions.RedisError, OSError, TimeoutError …
                now = time.monotonic()
                if now - _last_log > 60:
                    _last_log = now
                    logger.warning("Redis cache unavailable (%s: %s) — serving without cache", type(e).__name__, e)
                return default() if callable(default) else default
        wrapper.__name__ = fn.__name__
        return wrapper
    return deco


class ResilientRedisCache(RedisCache):
    get = _swallow(None)(RedisCache.get)
    set = _swallow(None)(RedisCache.set)
    add = _swallow(False)(RedisCache.add)
    touch = _swallow(False)(RedisCache.touch)
    delete = _swallow(False)(RedisCache.delete)
    has_key = _swallow(False)(RedisCache.has_key)
    get_many = _swallow(dict)(RedisCache.get_many)
    set_many = _swallow(list)(RedisCache.set_many)
    delete_many = _swallow(None)(RedisCache.delete_many)
    clear = _swallow(False)(RedisCache.clear)
    incr = _swallow(0)(RedisCache.incr)

    def get(self, key, default=None, version=None):  # noqa: F811 — hata halinde çağıranın default'u döner
        return _swallow(lambda: default)(RedisCache.get)(self, key, default, version)
