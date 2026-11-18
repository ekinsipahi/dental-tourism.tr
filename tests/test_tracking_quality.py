"""Veri kalitesi (2026-11-18): JS çalıştıran botlar sayılmaz, eşzamanlı beacon kaybı onarılır, yeni olaylar ve kardeş
sitelerin sayfa/bölüm/tıklama anlamları mevcut 8 persona tipine kanıt olarak girer."""
import json
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client

from apps.persona.models import VisitorSession as PersonaSession
from apps.tracking.models import HUMAN_Q, PageView, TrackingEvent, VisitorSession

from .base import BROWSER_UA, SeededTestCase

DRD, DBS = "https://drdevrim.com", "https://devrimbirikensipahi.com.tr"
VID = "c" * 32


def ext(client, path, body, origin=DRD):
    return client.post(path, data=json.dumps(body), content_type="text/plain", HTTP_USER_AGENT=BROWSER_UA, HTTP_ORIGIN=origin)


def events(client, sid, evs, site="drd", origin=DRD, vid=VID):
    return ext(client, "/api/t/event/", {"site": site, "vid": vid, "sid": sid, "events": evs}, origin)


def labels(session_key):
    p = PersonaSession.objects.get(session_key=session_key)
    return " | ".join(e["l"] for e in (p.evidence or []))


class BotFilterTests(SeededTestCase):
    def test_webdriver_browser_opens_no_session_on_any_site(self):
        c = Client()
        r = ext(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": "1" * 24, "url": DRD + "/", "title": "t", "wd": 1})
        self.assertTrue(json.loads(r.content).get("bot"))
        d = Client(HTTP_USER_AGENT=BROWSER_UA)
        d.get("/")
        d.post("/api/tracking/pageview/", data=json.dumps({"url": "http://testserver/", "wd": 1}), content_type="application/json")
        self.assertEqual(VisitorSession.objects.count(), 0)
        self.assertEqual(PersonaSession.objects.count(), 0)

    def test_datacenter_session_is_flagged_and_not_counted_until_a_human_gesture_arrives(self):
        c = Client()
        ext(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": "2" * 24, "url": DRD + "/disci/sisli/", "title": "t"})
        s = VisitorSession.objects.get()
        from apps.tracking.tasks import enrich_geo_task

        with mock.patch("apps.tracking.tasks.lookup_ip", return_value={
                "ip_country": "SG", "ip_city": "Singapore", "ip_org": "AS136907 HUAWEI CLOUDS", "geo_source": "ipinfo"}):
            enrich_geo_task(str(s.id), "8.8.4.4")
        s.refresh_from_db()
        self.assertEqual((s.ip_org, s.bot_reason), ("AS136907 HUAWEI CLOUDS", "datacenter"))
        self.assertFalse(VisitorSession.objects.filter(HUMAN_Q).exists())

        admin = get_user_model().objects.create_superuser("adm", "a@a.com", "pw")
        self.client.force_login(admin)
        html = self.client.get("/admin/").content.decode()
        self.assertIn("🤖 1", html)                                  # site satırında bot sayısı
        self.assertIn('<div class="n">0</div><div class="l">Gerçek ziyaretçi', html)
        self.assertEqual(self.client.get("/admin/tracking/visitorsession/?human=bot").status_code, 200)
        self.assertEqual(json.loads(self.client.get("/api/tracking/dashboard/").content)["total"]["sessions"], 0)

        # Gerçek bir parmak hareketi geldi (VPN/kurumsal proxy arkasındaki insan): bayrak kalkar, etkileşim zamanı dolar
        events(c, "2" * 24, [{"event_type": "engaged", "data": {"kind": "touch", "after_ms": 1200}, "page_url": "/disci/sisli/"}])
        s.refresh_from_db()
        self.assertEqual(s.bot_reason, "")
        self.assertIsNotNone(s.engaged_at)
        self.assertTrue(VisitorSession.objects.filter(HUMAN_Q).exists())

    def test_hourly_job_flags_untouched_datacenter_sessions_and_keeps_engaged_ones(self):
        c = Client()
        for sid in ("3" * 24, "4" * 24):
            ext(c, "/api/t/pageview/", {"site": "dbs", "vid": VID, "sid": sid, "url": DBS + "/blog/x/", "title": "t"}, origin=DBS)
        VisitorSession.objects.update(ip_org="AS15169 Google LLC")
        events(c, "4" * 24, [{"event_type": "engaged", "data": {"kind": "pointer"}, "page_url": "/blog/x/"}], site="dbs", origin=DBS)
        from apps.tracking.bots import flag_datacenter_sessions, is_datacenter

        self.assertTrue(is_datacenter("AS136907 HUAWEI CLOUDS"))
        self.assertTrue(is_datacenter("AS14618 Amazon.com, Inc."))
        self.assertFalse(is_datacenter("AS9121 Turk Telekomunikasyon Anonim Sirketi"))
        self.assertFalse(is_datacenter("AS13335 Cloudflare, Inc."))     # iCloud Private Relay → gerçek Safari kullanıcısı
        out = flag_datacenter_sessions(days=3)
        self.assertEqual(out["flagged"], 1)
        self.assertEqual(VisitorSession.objects.get(session_key="dbs:" + "3" * 24).bot_reason, "datacenter")
        self.assertEqual(VisitorSession.objects.get(session_key="dbs:" + "4" * 24).bot_reason, "")
        call_command("periodic", "--job", "tracking")     # saat başı cron: aynı işi çalıştırır, hata vermez


class NewSignalTests(SeededTestCase):
    def test_new_events_are_stored_and_become_persona_evidence(self):
        c = Client()
        sid = "5" * 24
        ext(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": sid, "url": DRD + "/hizmetler/implant", "title": "t", "page_type": "treatment"})
        evs = [
            {"event_type": "engaged", "data": {"kind": "mouse", "after_ms": 800}},
            {"event_type": "section_time", "data": {"section": "legacy", "seconds": 40}},
            {"event_type": "nav_click", "data": {"element": "nav", "label": "Fiyatlar", "href": "/#fiyatlar", "position": "navbar"}},
            {"event_type": "ui_click", "data": {"element": "chatbot_toggle", "label": "Canlı destek", "position": "float"}},
            {"event_type": "outbound_click", "data": {"element": "outbound", "label": "Google yorumları", "href": "https://www.google.com/maps/place/Dr+Devrim"}},
            {"event_type": "phone_copy", "data": {"label": "0505 577 18 83", "position": "hero"}},
            {"event_type": "text_copy", "data": {"label": "Halaskargazi Cad. No: 12 Osmanbey Şişli"}},
            {"event_type": "tab_return", "data": {"away_seconds": 45, "label": "45 sn"}},
            {"event_type": "form_start", "data": {"form": "contact"}},
            {"event_type": "form_abandon", "data": {"form": "contact", "field": "phone", "label": "phone"}},
            {"event_type": "gallery_view", "data": {"section": "gallery", "label": "klinik"}},
            {"event_type": "booking_step", "data": {"step": "event_scheduled", "label": "event_scheduled"}},
            {"event_type": "form_submit", "data": {"form": "calendly", "label": "Calendly randevu"}},
            {"event_type": "js_error", "data": {"label": "x is not defined", "src": "/app.js", "line": 3}},
            {"event_type": "rage_click", "data": {"label": "Gönder", "position": "contact"}},
            {"event_type": "exit_intent", "data": {"after_sec": 30, "max_scroll": 60, "label": "60%"}},
            {"event_type": "time_on_page", "data": {"seconds": 50, "segment": 0, "max_scroll": 80, "clicks": 4, "engaged": True}},
        ]
        for e in evs:
            e["page_url"] = "/hizmetler/implant"
        self.assertEqual(events(c, sid, evs).status_code, 200)
        s = VisitorSession.objects.get(session_key="drd:" + sid)
        stored = set(TrackingEvent.objects.filter(session=s).values_list("event_type", flat=True))
        for t in ("engaged", "section_time", "nav_click", "ui_click", "outbound_click", "phone_copy", "text_copy", "tab_return",
                  "form_abandon", "gallery_view", "booking_step", "js_error", "rage_click", "exit_intent", "time_on_page"):
            self.assertIn(t, stored)
        self.assertIsNotNone(s.engaged_at)
        self.assertTrue(s.is_lead)                       # Calendly randevusu = form gönderimi
        pv = PageView.objects.get(session=s)
        self.assertEqual((pv.time_on_page_sec, pv.scroll_depth), (50, 80.0))

        why = labels("drd:" + sid)
        for expected in ("deneyim / klinik hikâyesi bölümünde 40 sn", "'Fiyatlar' öğesine tıkladı", "Canlı desteği / sohbeti açtı",
                         "Google'da yorumlara / haritaya gitti", "Telefon numarasını kopyaladı (hero)", "Adresi kopyaladı",
                         "Başka sekmeye gitti, geri döndü (45 sn)", "Forma başladı", "Formu yarıda bıraktı (son alan: phone)",
                         "Online randevu aldı (Calendly)", "Form gönderdi"):
            self.assertIn(expected, why)
        p = PersonaSession.objects.get(session_key="drd:" + sid)
        self.assertGreater(p.page_scores.get("price", 0), 0)       # "Fiyatlar" tıklaması fiyat kanıtı
        self.assertGreater(p.page_scores.get("trust", 0), 0)       # deneyim bölümü + Google doğrulaması
        self.assertEqual(p.gallery_views, 1)
        self.assertEqual(p.form_submits, 1)
        self.assertEqual(p.assigned_persona, "ready")

        admin = get_user_model().objects.create_superuser("adm", "a@a.com", "pw")
        self.client.force_login(admin)
        html = self.client.get(f"/admin/tracking/visitorsession/journey/?vid={VID}").content.decode()
        for t in ("0505 577 18 83", "Fiyatlar", "event_scheduled", "45 sn"):
            self.assertIn(t, html)
        self.assertEqual(self.client.get("/admin/tracking/contactclick/").status_code, 200)

    def test_pseo_family_and_emergency_pages_give_urgency_quality_and_about_signals(self):
        c = Client()
        def page(site, origin, sid, path, secs):
            vid = sid[0] * 32   # her alt durum ayrı ziyaretçi (aynı kimlik kardeş siteler arasında tek persona satırı olur)
            ext(c, "/api/t/pageview/", {"site": site, "vid": vid, "sid": sid, "url": origin + path, "title": "t"}, origin)
            events(c, sid, [{"event_type": "time_on_page", "data": {"seconds": secs, "segment": 0}, "page_url": path}], site, origin, vid=vid)
            return PersonaSession.objects.get(session_key=f"{site}:{sid}")

        p = page("drd", DRD, "6" * 24, "/haftasonu/cekmekoy/", 25)
        self.assertGreater(p.page_scores.get("urgency", 0), 0.5)
        self.assertIn("pseo-area@/haftasonu/cekmekoy — 25 sn", labels("drd:" + "6" * 24))
        p = page("drd", DRD, "7" * 24, "/en-iyi-disci/sisli/", 40)
        self.assertGreater(p.page_scores.get("quality", 0), 0.5)
        p = page("drd", DRD, "8" * 24, "/prof-dis-hekimi/kadikoy/", 40)
        self.assertGreater(p.page_scores.get("premium", 0), 0.2)
        p = page("dbs", DBS, "9" * 24, "/acil-dis-hekimi/", 15)
        self.assertEqual(PageView.objects.get(session__session_key="dbs:" + "9" * 24).page_type, "emergency")
        self.assertIn("Acil diş hekimi sayfasına geldi", labels("dbs:" + "9" * 24))
        self.assertGreater(p.page_scores.get("urgency", 0), 0.8)
        page("dbs", DBS, "a" * 24, "/why-us/", 30)
        self.assertEqual(PageView.objects.get(session__session_key="dbs:" + "a" * 24).page_type, "about")
        p = page("drd", DRD, "b" * 24, "/hizmetler/dis-cekimi", 30)
        self.assertGreater(p.page_scores.get("fear", 0), 0.3)


class RebuildTests(SeededTestCase):
    def test_rebuild_restores_click_evidence_lost_to_a_concurrent_write(self):
        c = Client()
        sid = "d" * 24
        ext(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": sid, "url": DRD + "/disci/buyukcekmece/kumburgaz/", "title": "t"})
        events(c, sid, [{"event_type": "section_view", "data": {"section": "gallery"}, "page_url": "/disci/buyukcekmece/kumburgaz/"},
                        {"event_type": "whatsapp_click", "data": {"position": "hero", "label": "WhatsApp Randevu Al", "element": "whatsapp"},
                         "page_url": "/disci/buyukcekmece/kumburgaz/"}])
        events(c, sid, [{"event_type": "time_on_page", "data": {"seconds": 22, "segment": 0}, "page_url": "/disci/buyukcekmece/kumburgaz/"}])
        key = "drd:" + sid
        self.assertIn("WhatsApp'ı tıkladı (hero)", labels(key))
        # Eşzamanlı yazma kaybını taklit et: tıklama kanıtı silinmiş, sayaç kalmış
        p = PersonaSession.objects.get(session_key=key)
        p.evidence = [e for e in p.evidence if "tıkladı" not in e["l"]]
        p.page_scores = {}
        p.save(update_fields=["evidence", "page_scores"])
        from apps.persona.rebuild import needs_repair

        self.assertTrue(needs_repair(p, VisitorSession.objects.get(session_key=key)))
        call_command("rebuild_personas", "--days", "1", "--only-missing")
        p.refresh_from_db()
        why = labels(key)
        self.assertIn("WhatsApp'ı tıkladı (hero)", why)
        self.assertIn("pseo-area@/disci/buyukcekmece/kumburgaz — 22 sn", why)
        self.assertEqual(p.whatsapp_clicks, 1)              # sayaçlar sıfırdan sayıldı, çift sayılmadı
        self.assertEqual(p.gallery_views, 1)
        self.assertEqual(p.assigned_persona, "ready")
        self.assertFalse(needs_repair(p, VisitorSession.objects.get(session_key=key)))


class CrossSiteTests(SeededTestCase):
    def test_same_visitor_moving_between_sites_gets_page_types_of_the_current_site(self):
        c = Client()
        ext(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": "e" * 24, "url": DRD + "/hizmetler/implant", "title": "t"})
        ext(c, "/api/t/pageview/", {"site": "dbs", "vid": VID, "sid": "f" * 24, "url": DBS + "/acil-dis-hekimi/", "title": "t"}, DBS)
        p = PersonaSession.objects.get(session_key="dbs:" + "f" * 24)   # aynı kimlik: persona satırı yeni oturuma bağlandı
        self.assertEqual(p.site, "dbs")
        self.assertIn("Acil diş hekimi sayfasına geldi", labels("dbs:" + "f" * 24))


class PageViewDwellTests(SeededTestCase):
    def test_exit_beacon_updates_the_pageview_it_belongs_to_even_if_the_next_pageview_arrived_first(self):
        c = Client()
        sid = "ab" * 12
        body = {"site": "drd", "vid": VID, "sid": sid, "title": "t"}
        ext(c, "/api/t/pageview/", {**body, "url": DRD + "/disci/buyukcekmece/kumburgaz/"})
        ext(c, "/api/t/pageview/", {**body, "url": DRD + "/"})                       # SPA geçişi: yeni sayfa önce geldi
        events(c, sid, [{"event_type": "time_on_page", "data": {"seconds": 33, "segment": 0, "max_scroll": 70},
                         "page_url": "/disci/buyukcekmece/kumburgaz/"}])
        events(c, sid, [{"event_type": "time_on_page", "data": {"seconds": 4, "segment": 0, "max_scroll": 10}, "page_url": "/"}])
        first = PageView.objects.get(session__session_key="drd:" + sid, url__contains="kumburgaz")
        home = PageView.objects.get(session__session_key="drd:" + sid, url=DRD + "/")
        self.assertEqual((first.time_on_page_sec, first.scroll_depth), (33, 70.0))
        self.assertEqual((home.time_on_page_sec, home.scroll_depth), (4, 10.0))
