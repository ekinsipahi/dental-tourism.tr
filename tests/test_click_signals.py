"""Tıklama sinyalleri: yanıtlanmayan telefon dönüşüm değil, CTA karar aşaması değil, Instagram güven sinyali,
"WhatsApp'tan arayın" admin'de sohbetten ayrı."""
import json

from django.contrib.auth import get_user_model
from django.test import override_settings

from apps.persona.models import PersonaExposure, VisitorSession

from .base import SeededTestCase


def _event(client, event_type, data=None):
    return client.post("/api/tracking/event/", data=json.dumps({"event_type": event_type, "data": data or {}}),
                       content_type="application/json")


@override_settings(PERSONA_UI_ENABLED=True)
class ClickSignalTests(SeededTestCase):
    def test_phone_click_is_decision_but_not_a_conversion(self):
        self.client.get("/")
        _event(self.client, "phone_click", {"position": "hero"})
        exposure = PersonaExposure.objects.get()
        self.assertFalse(exposure.converted)  # hat yanıtlanmıyor → bandit / ML ödüllendirilmez
        self.assertIn('data-stage="decision"', self.client.get("/").content.decode())

    def test_treatment_card_click_is_consideration_not_decision(self):
        self.client.get("/")
        _event(self.client, "cta_click", {"element": "cta"})
        _event(self.client, "nav_click", {"element": "treatment"})
        html = self.client.get("/").content.decode()
        self.assertIn('data-stage="consideration"', html)
        self.assertNotIn('data-stage="decision"', html)

    def test_instagram_click_is_a_trust_signal_and_listed_separately(self):
        from apps.tracking.models import ContactClick, SocialClick

        self.client.get("/")
        _event(self.client, "instagram_click", {"element": "instagram", "position": "ig-float"})
        session = VisitorSession.objects.get()
        self.assertEqual(session.testimonial_reads, 1)
        self.assertTrue(any("Instagram" in str(e) for e in session.evidence))
        self.assertEqual(SocialClick.objects.count(), 1)
        self.assertEqual(ContactClick.objects.count(), 0)  # iletişim listesine karışmaz

    def test_whatsapp_call_is_labelled_in_admin(self):
        self.client.get("/")
        _event(self.client, "whatsapp_click", {"element": "whatsapp_call", "label": "Call us on WhatsApp"})
        _event(self.client, "phone_click", {"element": "phone", "label": "Call us"})
        admin = get_user_model().objects.create_superuser("adm", "a@a.com", "pw")
        self.client.force_login(admin)
        page = self.client.get("/admin/tracking/contactclick/").content.decode()
        self.assertIn("📞 WhatsApp arama", page)
        self.assertIn("Telefon denemesi", page)
        self.assertEqual(self.client.get("/admin/tracking/socialclick/").status_code, 200)

    def test_logo_video_and_wa_call_markup(self):
        html = self.client.get("/").content.decode()
        self.assertIn('data-track="whatsapp_call"', html)
        self.assertIn('class="logo-video"', html)
