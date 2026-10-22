"""Supabase'e giden trafiği azaltan değişiklikler: bot sayfa önbelleği, toplu olaylar, tek anahtarlı sitemap,
oturumsuz anonim GET, imzalı persona önizleme çerezi."""
import json

from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext

from .base import BROWSER_UA, SeededTestCase

BOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


class PerformanceTests(SeededTestCase):
    def test_bot_gets_cached_page_without_db_queries(self):
        r1 = self.client.get("/treatments/dental-implants/", HTTP_USER_AGENT=BOT)
        self.assertEqual((r1.status_code, r1["X-Bot-Cache"]), (200, "MISS"))
        with CaptureQueriesContext(connection) as ctx:
            r2 = self.client.get("/treatments/dental-implants/", HTTP_USER_AGENT=BOT)
        self.assertEqual((r2.status_code, r2["X-Bot-Cache"]), (200, "HIT"))
        self.assertEqual(r2.content, r1.content)
        self.assertEqual(len(ctx.captured_queries), 0)
        # insanlar ve query string'li istekler önbellekten gelmez
        self.assertFalse(self.client.get("/treatments/dental-implants/", HTTP_USER_AGENT=BROWSER_UA).has_header("X-Bot-Cache"))
        self.assertFalse(self.client.get("/treatments/dental-implants/?x=1", HTTP_USER_AGENT=BOT).has_header("X-Bot-Cache"))

    def test_anonymous_page_view_does_not_read_django_session(self):
        self.client.get("/")  # oturum çerezi oluşur (takip anahtarı)
        with CaptureQueriesContext(connection) as ctx:
            self.assertEqual(self.client.get("/treatments/dental-implants/").status_code, 200)
        self.assertFalse(any("django_session" in q["sql"] for q in ctx.captured_queries))
        self.assertFalse(any("django_cache" in q["sql"] for q in ctx.captured_queries))  # önbellek DB'de değil

    def test_batched_events_are_recorded_once_per_session_fetch(self):
        from apps.tracking.models import TrackingEvent, VisitorSession

        self.client.get("/")
        body = {"events": [{"event_type": "scroll_depth", "data": {"depth": 50}},
                           {"event_type": "section_view", "data": {"section": "reviews"}},
                           {"event_type": "whatsapp_click", "data": {"element": "whatsapp", "position": "hero"}}]}
        r = self.client.post("/api/tracking/event/", data=json.dumps(body), content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(TrackingEvent.objects.filter(event_type="whatsapp_click").count(), 1)
        self.assertEqual(VisitorSession.objects.get().whatsapp_clicks, 1)
        self.assertIn('data-stage="decision"', self.client.get("/").content.decode())

    def test_sitemap_is_served_from_one_cached_blob(self):
        first = self.client.get("/sitemap.xml")
        self.assertEqual(first.status_code, 200)
        self.assertIn(b"<urlset", first.content)
        with CaptureQueriesContext(connection) as ctx:
            again = self.client.get("/sitemap.xml?nocache=1", HTTP_ACCEPT_LANGUAGE="de")
        self.assertEqual(again.content, first.content)
        self.assertEqual(len(ctx.captured_queries), 0)

    @override_settings(PERSONA_UI_ENABLED=True, DEBUG=True)
    def test_persona_preview_persists_in_signed_cookie(self):
        r = self.client.get("/?persona=premium")
        self.assertIn("persona_preview", r.cookies)
        self.assertIn('data-persona="premium"', self.client.get("/").content.decode())
        self.client.cookies["persona_preview"] = "tampered"  # imzasız çerez yok sayılır → zorlanmış persona yok
        self.assertNotIn('data-persona="premium"', self.client.get("/").content.decode())

    def test_returning_visitor_page_view_hits_no_database(self):
        """Aynı ziyaretçinin sonraki sayfa istekleri — takip işareti, persona önbelleği ve süreç içi memo
        (slug çözümü, çeviriler, teklifler, listeler) sayesinde — veritabanına hiç gitmez."""
        self.client.get("/")
        self.client.get("/treatments/dental-implants/")  # bellek ısınır
        for url in ("/treatments/dental-implants/", "/clinics/dr-devrim-sipahi/", "/"):
            self.client.get(url)
            with CaptureQueriesContext(connection) as ctx:
                r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
            self.assertFalse(r.has_header("X-Bot-Cache"))  # bot önbelleği değil, gerçek render
            self.assertEqual([q["sql"] for q in ctx.captured_queries], [], url)

    def test_memo_is_invalidated_when_content_is_saved(self):
        """Admin'de kaydedilen içerik aynı işçide anında görünür (model sürümü artar → eski memo girişleri geçersiz)."""
        from apps.treatments.models import Treatment

        url = "/treatments/dental-implants/"
        self.assertEqual(self.client.get(url).status_code, 200)
        t = Treatment.objects.get(key="dental-implants")
        t.short_description = "Renamed lead text for the memo test"
        t.save()
        self.assertIn("Renamed lead text for the memo test", self.client.get(url).content.decode())
        if t.get_translation("de") is not None:  # canlı Almanca çeviri varsa: çeviri kaydı da ana modelin sürümünü artırır
            from apps.core.seo import reverse_in

            tr = t.get_translation("de")
            de_url = reverse_in("de", "treatments:detail", {"slug": tr.slug})
            self.assertEqual(self.client.get(de_url).status_code, 200)  # bellek ısınır
            tr.short_description = "Geänderter Einleitungstext"
            tr.save()
            self.assertIn("Geänderter Einleitungstext", self.client.get(de_url).content.decode())
