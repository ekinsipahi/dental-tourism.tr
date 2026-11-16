"""Merkezi lead ucu (/api/t/lead/): kardeş sitelerin formları, köken / tuzak / hız limiti, sunucudan sunucuya aktarım
(X-DT-Key), admin listelerinde site sütunu + doğru alan adına link, yolculukta "muhtemelen aynı ziyaretçi" bloğu."""
import json

from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from .base import BROWSER_UA, SeededTestCase, visit

VID = "a" * 32
SID = "b" * 24
ORIGIN = "https://drdevrim.com"
LEAD = {"site": "drd", "vid": VID, "sid": SID, "name": "Anna", "phone": "+49 151 1234567",
        "page": "https://drdevrim.com/en/dentist/sisli/nisantasi", "source": "form"}


def _post(client, path, body, origin=ORIGIN, ua=BROWSER_UA, **extra):
    kw = {"HTTP_USER_AGENT": ua, **extra}
    if origin:
        kw["HTTP_ORIGIN"] = origin
    return client.post(path, data=json.dumps(body), content_type="text/plain", **kw)


def _admin_client():
    admin = get_user_model().objects.create_superuser("adm", "a@a.com", "pw")
    c = Client(HTTP_USER_AGENT=BROWSER_UA)
    c.force_login(admin)
    return c


class ExternalLeadTests(SeededTestCase):
    def test_lead_from_drdevrim_is_linked_to_the_site_session(self):
        from apps.tracking.models import Lead, TrackingEvent, VisitorSession

        c = Client()
        _post(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": SID,
                                      "url": "https://drdevrim.com/en/dentist/sisli/nisantasi?gclid=xyz&utm_campaign=implant"})
        r = _post(c, "/api/t/lead/", {**LEAD, "email": "anna@example.com", "message": "Preis?", "language": "en"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Access-Control-Allow-Origin"], ORIGIN)
        lead = Lead.objects.get(pk=r.json()["lead_id"])
        s = VisitorSession.objects.get(session_key=f"drd:{SID}")
        self.assertEqual((lead.site, lead.source, lead.session_id, lead.name, lead.phone), ("drd", "form", s.pk, "Anna", "+49 151 1234567"))
        self.assertEqual((lead.traffic_source, lead.gclid, lead.language, s.google_campaign), ("google_ads", "xyz", "en", "implant"))
        self.assertEqual(lead.device_type, s.device_type)
        self.assertIsNotNone(lead.clinic)
        s.refresh_from_db()
        self.assertTrue(s.is_lead)
        self.assertEqual(s.form_submits, 1)
        self.assertTrue(TrackingEvent.objects.filter(session=s, event_type="form_submit", data__lead=lead.pk).exists())

    def test_lead_without_prior_beacon_opens_the_session_and_infers_language(self):
        from apps.tracking.models import Lead, VisitorSession

        r = _post(Client(), "/api/t/lead/", {**LEAD, "source": "chatbot", "gclid": "g-1", "page": "https://drdevrim.com/de/implant"},
                  origin="https://www.drdevrim.com")
        self.assertEqual(r.status_code, 200)
        lead = Lead.objects.get()
        s = VisitorSession.objects.get(session_key=f"drd:{SID}")
        self.assertEqual((lead.session_id, lead.source, lead.language, s.site, s.visitor_id), (s.pk, "chatbot", "de", "drd", VID))
        self.assertEqual((lead.gclid, lead.traffic_source), ("g-1", "google_ads"))

    def test_rejects_honeypot_invalid_input_and_foreign_origin(self):
        from apps.tracking.models import Lead

        c = Client()
        self.assertEqual(_post(c, "/api/t/lead/", {**LEAD, "website": "http://spam"}).status_code, 400)
        self.assertEqual(_post(c, "/api/t/lead/", {**LEAD, "phone": "123"}).status_code, 400)
        self.assertEqual(_post(c, "/api/t/lead/", {**LEAD, "phone": "", "name": ""}).status_code, 400)
        self.assertEqual(_post(c, "/api/t/lead/", {**LEAD, "site": "dt"}).status_code, 400)
        self.assertEqual(_post(c, "/api/t/lead/", {**LEAD, "sid": "zz"}).status_code, 400)
        self.assertEqual(_post(c, "/api/t/lead/", {**LEAD, "sid": ""}).status_code, 400)
        self.assertEqual(_post(c, "/api/t/lead/", LEAD, origin="https://evil.example").status_code, 403)
        self.assertEqual(_post(c, "/api/t/lead/", LEAD, ua="Googlebot/2.1").status_code, 403)
        self.assertEqual(c.post("/api/t/lead/", data="[1,2]", content_type="text/plain", HTTP_ORIGIN=ORIGIN, HTTP_USER_AGENT=BROWSER_UA).status_code, 400)
        self.assertEqual(Lead.objects.count(), 0)
        self.assertEqual(c.options("/api/t/lead/", HTTP_ORIGIN=ORIGIN).status_code, 204)
        self.assertEqual(_post(c, "/api/t/lead/", {**LEAD, "source": "weird"}).status_code, 200)
        self.assertEqual(Lead.objects.get().source, "form")  # bilinmeyen kaynak → form

    def test_rate_limited_per_sid_and_per_ip(self):
        from apps.tracking.models import Lead

        c = Client()
        codes = [_post(c, "/api/t/lead/", LEAD).status_code for _ in range(4)]
        self.assertEqual(codes, [200, 200, 200, 429])  # oturum başına 3 / saat
        codes = []
        for i in range(3):  # aynı IP, yeni oturumlar: IP başına 10 / saat (3 + 3 + 3 + 1)
            sid = chr(ord("c") + i) * 24
            codes += [_post(c, "/api/t/lead/", {**LEAD, "sid": sid}).status_code for _ in range(3)]
        self.assertEqual(codes, [200, 200, 200, 200, 200, 200, 200, 429, 429])
        self.assertEqual(Lead.objects.count(), 10)

    @override_settings(DT_LEAD_KEY="sekret")
    def test_server_to_server_with_key_bypasses_origin_and_rate_limit(self):
        from apps.tracking.models import Lead, VisitorSession

        c = Client()
        body = {"site": "dbs", "name": "Mehmet", "phone": "05321234567", "source": "callme", "external_id": "cm-17",
                "page": "https://devrimbirikensipahi.com.tr/tr/iletisim", "language": "tr", "created_at": "2026-11-10T09:30:00+03:00"}
        r = _post(c, "/api/t/lead/", body, origin=None, ua="python-requests/2.31", HTTP_X_DT_KEY="sekret")
        self.assertEqual(r.status_code, 200)
        lead = Lead.objects.get(pk=r.json()["lead_id"])
        self.assertEqual((lead.site, lead.source, lead.external_id, lead.session), ("dbs", "callme", "cm-17", None))
        self.assertEqual(lead.created_at.isoformat(), "2026-11-10T06:30:00+00:00")
        # aynı kaydın tekrar aktarımı: ikinci lead açılmaz
        r2 = _post(c, "/api/t/lead/", body, origin=None, HTTP_X_DT_KEY="sekret")
        self.assertEqual((r2.json()["lead_id"], r2.json().get("duplicate"), Lead.objects.count()), (lead.pk, True, 1))
        # sid/vid verilirse (formdaki dt_sid / dt_vid gizli alanları) oturuma bağlanır; hız limiti yok, dt sitesi de olabilir
        _post(c, "/api/t/pageview/", {"site": "dbs", "vid": VID, "sid": SID, "url": "https://devrimbirikensipahi.com.tr/tr/"},
              origin="https://devrimbirikensipahi.com.tr")
        for i in range(5):
            r = _post(c, "/api/t/lead/", {**body, "external_id": f"cm-{i}", "sid": SID, "vid": VID}, origin="https://evil.example",
                      HTTP_X_DT_KEY="sekret")
            self.assertEqual(r.status_code, 200)
        s = VisitorSession.objects.get(session_key=f"dbs:{SID}")
        self.assertEqual(Lead.objects.filter(session=s, site="dbs").count(), 5)
        self.assertTrue(s.is_lead)
        self.assertEqual(_post(c, "/api/t/lead/", {**body, "site": "dt", "external_id": "x"}, origin=None, HTTP_X_DT_KEY="sekret").status_code, 200)

    def test_server_to_server_without_valid_key_is_refused(self):
        from apps.tracking.models import Lead

        c = Client()
        body = {"site": "dbs", "name": "Mehmet", "phone": "05321234567", "source": "callme"}
        with override_settings(DT_LEAD_KEY="sekret"):
            self.assertEqual(_post(c, "/api/t/lead/", body, origin=None, HTTP_X_DT_KEY="wrong").status_code, 403)
            self.assertEqual(_post(c, "/api/t/lead/", body, origin="https://evil.example").status_code, 403)
            self.assertEqual(_post(c, "/api/t/lead/", body, origin=None).status_code, 400)  # anahtarsız: tarayıcı kuralları (sid şart)
        with override_settings(DT_LEAD_KEY=""):  # kapalı: doğru anahtar bile işe yaramaz
            self.assertEqual(_post(c, "/api/t/lead/", body, origin=None, HTTP_X_DT_KEY="sekret").status_code, 403)
        self.assertEqual(Lead.objects.count(), 0)

    def test_dentaltourism_leads_carry_site_dt(self):
        from apps.tracking.models import Lead

        visit(self.client, "/en/")
        r = self.client.post("/api/tracking/lead/", data=json.dumps({"name": "Anna", "phone": "+491511234567", "page": "/en/"}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Lead.objects.get().site, "dt")

    def test_tracker_script_exposes_lead_api_identity_fields_and_meta_hint(self):
        js = open("static/js/dt-track.js", encoding="utf-8").read()
        for needle in ("/api/t/lead/", "dt_vid", "dt_sid", "dt_site", 'meta[name="dt-page"]', "lead: lead", "sid: SID"):
            self.assertIn(needle, js)


class MultisiteAdminTests(SeededTestCase):
    def _seed(self):
        c = Client()
        _post(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": SID, "url": "https://drdevrim.com/en/dentist/sisli/nisantasi"})
        _post(c, "/api/t/event/", {"site": "drd", "vid": VID, "sid": SID, "events": [
            {"event_type": "phone_click", "data": {"element": "phone", "position": "float"}, "page_url": "/en/dentist/sisli/nisantasi"}]})
        _post(c, "/api/t/lead/", {**LEAD, "page": "/en/dentist/sisli/nisantasi"})
        visit(self.client, "/treatments/dental-implants/")
        self.client.post("/api/tracking/event/", data=json.dumps({"event_type": "whatsapp_click", "data": {"position": "float"}, "page_url": "/en/"}),
                         content_type="application/json")

    def test_lists_show_site_and_link_to_the_right_domain(self):
        self._seed()
        a = _admin_client()
        for url in ("/admin/tracking/lead/", "/admin/tracking/contactclick/", "/admin/tracking/pageview/"):
            html = a.get(url).content.decode()
            self.assertIn("drdevrim.com", html, url)
            self.assertIn('href="https://drdevrim.com/en/dentist/sisli/nisantasi"', html, url)
            self.assertNotIn('href="https://dentaltourism.tr/en/dentist/sisli/nisantasi"', html, url)
            self.assertEqual(a.get(url + "?site=drd").status_code, 200)
            self.assertEqual(a.get(url + "?site=dt").status_code, 200)
        html = a.get("/admin/tracking/pageview/?site=dt").content.decode()  # dt sayfa URL'si tam kaydedilir (testte testserver)
        self.assertIn("testserver/treatments/dental-implants/", html)
        self.assertIn("dentaltourism.tr</span>", html)
        self.assertNotIn("nisantasi", html)
        html = a.get("/admin/tracking/contactclick/?site=dt").content.decode()  # dt tıklaması yol olarak gelir → kendi alan adı
        self.assertIn('href="https://dentaltourism.tr/en/"', html)
        html = a.get("/admin/tracking/lead/?site=drd").content.decode()
        self.assertIn("Anna", html)
        self.assertEqual(a.get("/admin/tracking/lead/?site=dt").content.decode().count("Anna"), 0)
        self.assertEqual(a.get("/admin/tracking/socialclick/?site=drd").status_code, 200)
        self.assertEqual(a.get("/admin/tracking/visitorsession/").status_code, 200)

    def test_journey_shows_probable_same_visitor_from_another_site(self):
        self._seed()  # drd oturumu: VID; dt oturumu: çerezli kimlik — aynı IP (127.0.0.1), aynı UA, aynı cihaz, aynı dakika
        dt_vid = self.client.cookies["dt_vid"].value
        self.assertNotEqual(dt_vid, VID)
        a = _admin_client()
        html = a.get(f"/admin/tracking/visitorsession/journey/?vid={dt_vid}").content.decode()
        self.assertIn("Muhtemelen aynı ziyaretçi", html)
        self.assertIn("YAKLAŞIK", html)
        self.assertIn("https://drdevrim.com/en/dentist/sisli/nisantasi", html)
        self.assertIn("testserver/treatments/dental-implants/", html)
        self.assertIn('href="https://dentaltourism.tr/en/"', html)  # dt olayının yolu kendi alan adına bağlanır
        # farklı tarayıcıdan gelen oturum eşleşmez
        _post(Client(), "/api/t/pageview/", {"site": "dbs", "vid": "f" * 32, "sid": "f" * 24, "url": "https://devrimbirikensipahi.com.tr/tr/"},
              origin="https://devrimbirikensipahi.com.tr", ua="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        html = a.get(f"/admin/tracking/visitorsession/journey/?vid={dt_vid}").content.decode()
        self.assertNotIn("devrimbirikensipahi.com.tr/tr/", html)
        # eşleşmesi olmayan ziyaretçide blok yok
        html = a.get("/admin/tracking/visitorsession/journey/?vid=" + "f" * 32).content.decode()
        self.assertNotIn("Muhtemelen aynı ziyaretçi", html)
