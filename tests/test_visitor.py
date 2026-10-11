"""Kalıcı ziyaretçi kimliği (dt_vid) + huni aşaması (data-stage)."""
import json

from django.test import Client

from apps.persona.models import VisitorSession

from .base import BROWSER_UA, SeededTestCase


class VisitorIdTests(SeededTestCase):
    def test_first_visit_sets_persistent_cookie(self):
        r = self.client.get("/")
        self.assertIn("dt_vid", r.cookies)
        vid = r.cookies["dt_vid"].value
        self.assertRegex(vid, r"^[a-f0-9]{32}$")
        self.assertEqual(VisitorSession.objects.get(session_key=self.client.session.session_key).visitor_id, vid)

    def test_returning_visitor_with_new_session_keeps_history(self):
        self.client.get("/?utm_term=cheap+dental+turkey")
        vid = self.client.cookies["dt_vid"].value
        first = VisitorSession.objects.get(visitor_id=vid)
        # Yeni tarayıcı oturumu (sessionid yok) ama aynı dt_vid çerezi
        c2 = Client(HTTP_USER_AGENT=BROWSER_UA)
        c2.cookies["dt_vid"] = vid
        c2.get("/")
        self.assertEqual(VisitorSession.objects.filter(visitor_id=vid).count(), 1)  # aynı kişi, tek kayıt
        again = VisitorSession.objects.get(visitor_id=vid)
        self.assertEqual(again.pk, first.pk)
        self.assertIn("price", again.intent_scores)  # ilk ziyaretteki "cheap" niyeti korunur

    def test_stage_moves_to_decision_after_whatsapp_click(self):
        html = self.client.get("/").content.decode()
        self.assertIn('data-stage="awareness"', html)
        self.client.post("/api/tracking/event/", data=json.dumps({"event_type": "whatsapp_click", "data": {}, "page_url": "/"}),
                         content_type="application/json")
        html = self.client.get("/").content.decode()
        self.assertIn('data-stage="decision"', html)
        self.assertIn("stage-dock", html)

    def test_event_with_localstorage_vid_restores_cookie(self):
        vid = "a" * 32
        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        r = c.post("/api/tracking/event/", data=json.dumps({"event_type": "cta_click", "vid": vid,
                                                            "attr": {"gclid": "G-123"}}), content_type="application/json")
        self.assertEqual(r.cookies["dt_vid"].value, vid)
