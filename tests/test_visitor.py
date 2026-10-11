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


class ReferrerTrackingTests(SeededTestCase):
    def test_organic_and_referral_visits_create_tracking_session(self):
        from apps.tracking.models import VisitorSession as TrackingSession

        for ref in ("https://www.google.com/search?q=dental+clinic+istanbul", "https://www.bing.com/",
                    "https://www.instagram.com/", "https://example.org/blog"):
            c = Client(HTTP_USER_AGENT=BROWSER_UA)
            self.assertEqual(c.get("/", HTTP_REFERER=ref).status_code, 200)
            s = TrackingSession.objects.get(session_key=c.session.session_key)
            self.assertEqual(s.referrer_url, ref)
            r = c.post("/api/tracking/event/", data=json.dumps({"event_type": "phone_click"}), content_type="application/json")
            self.assertEqual(r.status_code, 200)
            s.refresh_from_db()
            self.assertEqual(s.phone_clicks, 1)


class PageBehaviourTests(SeededTestCase):
    def test_browsing_price_pages_makes_price_persona(self):
        from apps.persona.models import VisitorSession

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        for url in ("/prices/", "/prices/dental-implants/", "/prices/porcelain-veneers/", "/packages/"):
            c.get(url)
        s = VisitorSession.objects.get(session_key=c.session.session_key)
        self.assertEqual(max(s.persona_scores, key=s.persona_scores.get), "price")

    def test_browsing_luxury_treatments_makes_premium_persona(self):
        from apps.persona.models import VisitorSession

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        for url in ("/treatments/porcelain-veneers/", "/treatments/zirconia-crowns/", "/treatments/all-on-4-implants/",
                    "/de/behandlungen/dental-implants/"):
            c.get(url)
        s = VisitorSession.objects.get(session_key=c.session.session_key)
        self.assertEqual(max(s.persona_scores, key=s.persona_scores.get), "premium")
        self.assertIn("treatments:detail:porcelain-veneers", s.pages_seen)

    def test_refreshing_same_page_does_not_inflate(self):
        from apps.persona.models import VisitorSession

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        for _ in range(6):
            c.get("/prices/")
        s = VisitorSession.objects.get(session_key=c.session.session_key)
        self.assertLessEqual(s.page_scores.get("price", 0), 2.6)


class ContactClickTrackingTests(SeededTestCase):
    def test_phone_click_is_logged_with_context_and_shown_in_admin(self):
        from django.contrib.auth import get_user_model

        from apps.tracking.models import ContactClick

        self.client.get("/", HTTP_REFERER="https://www.google.com/")
        r = self.client.post("/api/tracking/event/", data=json.dumps({
            "event_type": "phone_click", "page_url": "/en/contact/", "persona": "price", "stage": "decision",
            "lang": "en", "data": {"label": "Call now", "position": "hero", "href": "tel:+90"}}),
            content_type="application/json")
        self.assertEqual(r.status_code, 200)
        click = ContactClick.objects.get()
        self.assertEqual((click.label, click.position, click.event_type), ("Call now", "hero", "phone_click"))
        self.assertIsNotNone(click.session.ip_address)

        admin = get_user_model().objects.create_superuser("adm", "a@a.com", "pw")
        self.client.force_login(admin)
        page = self.client.get("/admin/tracking/contactclick/")
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Call now")
        self.assertEqual(self.client.get("/admin/tracking/lead/").status_code, 200)

    def test_lead_form_records_form_submit_event(self):
        from apps.tracking.models import ContactClick, Lead

        self.client.get("/")
        r = self.client.post("/api/tracking/lead/", data=json.dumps({"name": "Anna", "phone": "+491511234567",
                                                                     "page": "/en/contact/", "language": "en"}),
                             content_type="application/json")
        self.assertIn(r.status_code, (200, 201))
        lead = Lead.objects.get()
        self.assertIsNotNone(lead.session)
        self.assertTrue(ContactClick.objects.filter(event_type="form_submit", session=lead.session).exists())
