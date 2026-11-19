"""Açılış seed'i (apps/core/boot.py): dosyadaki blog yazısı ve kategori çevirileri web süreci açılınca canlıya ulaşır."""
from django.test import override_settings

from apps.blog.models import BlogCategory, BlogPost
from apps.core import boot

from .base import SeededTestCase


class BootSeedTests(SeededTestCase):
    def test_run_seeds_now_applies_file_content_and_restores_settings(self):
        with override_settings(AUTO_TRANSLATE_ON_PUBLISH=True):
            self.assertEqual(boot.run_seeds_now(), "ok")
            from django.conf import settings

            self.assertTrue(settings.AUTO_TRANSLATE_ON_PUBLISH)  # seed komutları kapatır, web süreci için geri açılır
        self.assertEqual(BlogCategory.objects.get(slug="safety-and-quality").translations.count(), 16)
        post = BlogPost.objects.get(slug="is-it-safe-to-get-dental-implants-in-turkey")
        self.assertEqual(post.status, BlogPost.STATUS_PUBLISHED)
        self.assertTrue(post.is_published)
        self.assertEqual(post.doctor_author.slug, "devrim-biriken-sipahi")
        # ikinci koşu idempotent: dateModified oynamaz
        updated = post.updated_at
        self.assertEqual(boot.run_seeds_now(), "ok")
        post.refresh_from_db()
        self.assertEqual(post.updated_at, updated)
        # yazı canlı ve sitemap'te
        self.assertEqual(self.client.get(post.get_absolute_url("en")).status_code, 200)
        self.assertIn(post.get_absolute_url("en"), self.client.get("/sitemap-blog.xml").content.decode())

    def test_disabled_by_setting(self):
        with override_settings(BOOT_SEEDS=False):
            self.assertIsNone(boot.start_boot_seeds())

    def test_thread_runs_when_enabled(self):
        with override_settings(BOOT_SEEDS=True):
            t = boot.start_boot_seeds()
            self.assertIsNotNone(t)
            t.join(timeout=120)
            self.assertFalse(t.is_alive())
