"""Önbellek veritabanında değil; Redis koparsa site ayakta kalır; sitemap süreç içi 'local' önbellekte."""
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from dental_tourism.cache_backends import ResilientRedisCache

from .base import SeededTestCase


class CacheSettingsTests(SimpleTestCase):
    def test_no_database_cache_and_aliases_exist(self):
        for alias in ("default", "sessions", "local"):
            self.assertNotIn("db.DatabaseCache", settings.CACHES[alias]["BACKEND"], alias)
        self.assertEqual(settings.SESSION_CACHE_ALIAS, "sessions")
        self.assertIn("locmem", settings.CACHES["local"]["BACKEND"])  # büyük bloblar her zaman süreç içi

    def test_redis_outage_degrades_to_cache_miss(self):
        import redis

        cache = ResilientRedisCache("redis://127.0.0.1:1/0", {})
        boom = mock.MagicMock()
        for name in ("get", "set", "add", "delete", "get_many", "has_key", "incr", "clear"):
            getattr(boom, name).side_effect = redis.exceptions.ConnectionError("down")
        with mock.patch.object(type(cache), "_cache", new_callable=mock.PropertyMock, return_value=boom):
            self.assertEqual(cache.get("k", "fallback"), "fallback")
            self.assertIsNone(cache.set("k", 1))
            self.assertFalse(cache.add("k", 1))
            self.assertFalse(cache.delete("k"))
            self.assertEqual(cache.get_many(["k"]), {})
            self.assertFalse(cache.has_key("k"))


class HealthzTests(SeededTestCase):
    def test_healthz_reports_cache_backend(self):
        r = self.client.get("/healthz")
        self.assertEqual((r.status_code, r.content), (200, b"ok"))
        self.assertIn(r["X-Cache-Backend"], ("redis", "locmem"))
        self.assertEqual(r["X-Cache-Ping"], "ok")
