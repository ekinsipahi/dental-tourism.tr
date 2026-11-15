"""Çok siteli takip: kardeş sitelerin çerezsiz beacon'ları (/api/t/), köken kontrolü, site/sayfa türü, siteler arası
kimlik birleştirme ve admin yolculuk görünümü."""
import json

from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from .base import BROWSER_UA, SeededTestCase, visit

VID = "a" * 32
SID = "b" * 24
ORIGIN = "https://drdevrim.com"


def _post(client, path, body, origin=ORIGIN, ua=BROWSER_UA):
    kw = {"HTTP_USER_AGENT": ua}
    if origin:
        kw["HTTP_ORIGIN"] = origin
    return client.post(path, data=json.dumps(body), content_type="text/plain", **kw)


class ExternalBeaconTests(SeededTestCase):
    def test_pageview_from_drdevrim_opens_a_site_session_with_page_context(self):
        from apps.persona.models import VisitorSession as PersonaSession
        from apps.tracking.models import PageView, VisitorSession

        c = Client()
        r = _post(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": SID, "url": "https://drdevrim.com/en/dentist/sisli/nisantasi?gclid=xyz",
                                           "title": "Dentist Nişantaşı", "referrer": "https://www.google.com/", "tz": "Europe/Berlin"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Access-Control-Allow-Origin"], ORIGIN)
        s = VisitorSession.objects.get(session_key=f"drd:{SID}")
        self.assertEqual((s.site, s.visitor_id, s.landing_page, s.gclid, s.traffic_source), ("drd", VID, "/en/dentist/sisli/nisantasi", "xyz", "google_ads"))
        self.assertEqual(s.language_code, "en")
        pv = PageView.objects.get(session=s)
        self.assertEqual(pv.page_type, "pseo-area")
        self.assertEqual(PersonaSession.objects.get(session_key=f"drd:{SID}").site, "drd")
        self.assertNotIn("sessionid", r.cookies)  # çerezsiz

    def test_events_update_counters_and_disallowed_origin_is_rejected(self):
        from apps.tracking.models import ContactClick, VisitorSession

        c = Client()
        _post(c, "/api/t/pageview/", {"site": "dbs", "vid": VID, "sid": SID, "url": "https://devrimbirikensipahi.com.tr/de/"},
              origin="https://devrimbirikensipahi.com.tr")
        r = _post(c, "/api/t/event/", {"site": "dbs", "vid": VID, "sid": SID, "events": [
            {"event_type": "phone_click", "data": {"element": "phone", "position": "float"}, "page_url": "/de/"},
            {"event_type": "faq_read", "data": {"q": "Preise?", "seconds": 12}, "page_url": "/de/"}]},
            origin="https://devrimbirikensipahi.com.tr")
        self.assertEqual(r.status_code, 200)
        s = VisitorSession.objects.get(session_key=f"dbs:{SID}")
        self.assertEqual((s.site, s.phone_clicks), ("dbs", 1))
        self.assertEqual(ContactClick.objects.filter(session=s, event_type="phone_click").count(), 1)
        self.assertEqual(_post(c, "/api/t/event/", {"site": "dbs", "vid": VID, "sid": SID, "events": []}, origin="https://evil.example").status_code, 403)
        self.assertEqual(_post(c, "/api/t/pageview/", {"site": "dt", "vid": VID, "sid": SID, "url": "https://x/"}).status_code, 400)
        self.assertEqual(_post(c, "/api/t/pageview/", {"site": "drd", "vid": VID, "sid": "zz"}).status_code, 400)
        self.assertEqual(c.options("/api/t/event/", HTTP_ORIGIN=ORIGIN).status_code, 204)

    def test_handoff_merges_visitor_history_across_sites(self):
        from apps.tracking.models import VisitorSession

        # 1) dentaltourism.tr'de gezinti (çerezli, kendi kimliği)
        visit(self.client, "/")
        dt_vid = self.client.cookies["dt_vid"].value
        # 2) drdevrim.com'a kendi kimliğiyle gelmişti; linkteki ?dtv= ile dentaltourism kimliğini benimser → eski kimlik birleşir
        old = "c" * 32
        c = Client()
        _post(c, "/api/t/pageview/", {"site": "drd", "vid": old, "sid": "d" * 24, "url": "https://drdevrim.com/"})
        _post(c, "/api/t/pageview/", {"site": "drd", "vid": dt_vid, "sid": "e" * 24, "url": "https://drdevrim.com/hizmetler/implant", "prev_vid": old})
        self.assertEqual(VisitorSession.objects.filter(visitor_id=dt_vid).count(), 3)  # dt + 2 drd oturumu
        self.assertFalse(VisitorSession.objects.filter(visitor_id=old).exists())
        # admin yolculuk görünümü üç siteyi tek zaman çizgisinde gösterir
        admin = get_user_model().objects.create_superuser("adm", "a@a.com", "pw")
        self.client.force_login(admin)
        html = self.client.get(f"/admin/tracking/visitorsession/journey/?vid={dt_vid}").content.decode()
        self.assertIn("dentaltourism.tr", html)
        self.assertIn("drdevrim.com", html)
        self.assertIn("/hizmetler/implant", html)
        self.assertEqual(self.client.get("/admin/tracking/visitorsession/?site=drd").status_code, 200)

    def test_dentaltourism_tracker_carries_identity_and_page_type(self):
        from apps.tracking.models import PageView

        visit(self.client, "/treatments/dental-implants/")
        self.assertEqual(PageView.objects.get().page_type, "treatment")
        js = open("static/js/dt-track.js", encoding="utf-8").read()
        self.assertIn("/api/t/pageview/", js)
        self.assertIn("dtv", js)
