"""Kimliksiz uçların korunması: lead ucu (oturum çerezi + aynı köken + hız limiti + tuzak alan),
WhatsApp webhook'u (paylaşılan gizli anahtar; anahtar yoksa kapalı)."""
import json

from django.test import Client, override_settings

from .base import BROWSER_UA, SeededTestCase

LEAD = {"name": "Anna", "phone": "+491511234567", "page": "/en/contact/", "language": "en"}
URL = "/api/tracking/lead/"


def _post(client, body=LEAD, **extra):
    return client.post(URL, data=json.dumps(body), content_type="application/json", **extra)


class LeadEndpointTests(SeededTestCase):
    def test_lead_requires_a_prior_page_view(self):
        from apps.tracking.models import Lead

        self.assertEqual(_post(self.client).status_code, 403)  # oturum çerezi yok → script / bot
        self.assertEqual(Lead.objects.count(), 0)
        self.client.get("/")
        self.assertEqual(_post(self.client).status_code, 200)
        self.assertEqual(Lead.objects.count(), 1)

    def test_lead_rejects_foreign_origin_and_bots(self):
        from apps.tracking.models import Lead

        self.client.get("/")
        self.assertEqual(_post(self.client, HTTP_ORIGIN="https://evil.example").status_code, 403)
        self.assertEqual(_post(self.client, HTTP_REFERER="https://evil.example/form").status_code, 403)
        self.assertEqual(_post(self.client, HTTP_USER_AGENT="Googlebot/2.1").status_code, 403)
        self.assertEqual(Lead.objects.count(), 0)
        self.assertEqual(_post(self.client, HTTP_ORIGIN="http://testserver").status_code, 200)

    def test_lead_rejects_honeypot_and_bad_phone(self):
        from apps.tracking.models import Lead

        self.client.get("/")
        self.assertEqual(_post(self.client, {**LEAD, "website": "http://spam"}).status_code, 400)
        self.assertEqual(_post(self.client, {**LEAD, "phone": "123"}).status_code, 400)
        self.assertEqual(_post(self.client, [1, 2]).status_code, 400)
        self.assertEqual(Lead.objects.count(), 0)

    def test_lead_is_rate_limited_per_session_and_ip(self):
        from apps.tracking.models import Lead

        self.client.get("/")
        codes = [_post(self.client).status_code for _ in range(4)]
        self.assertEqual(codes, [200, 200, 200, 429])  # oturum başına 3 / saat
        for _ in range(3):  # aynı IP, yeni oturumlar: IP başına 5 / saat
            c = Client(HTTP_USER_AGENT=BROWSER_UA)
            c.get("/")
            codes.append(_post(c).status_code)
        self.assertEqual(codes[4:], [200, 200, 429])
        self.assertEqual(Lead.objects.count(), 5)


class WhatsAppWebhookTests(SeededTestCase):
    URL = "/api/tracking/whatsapp-webhook/"
    BODY = json.dumps({"phone": "+905551112233", "message": "Merhaba, implant fiyatı?"})

    def _post(self, **extra):
        return self.client.post(self.URL, data=self.BODY, content_type="application/json", **extra)

    @override_settings(WHATSAPP_WEBHOOK_SECRET="")
    def test_webhook_is_disabled_without_secret(self):
        from apps.tracking.models import WhatsAppMatch

        self.assertEqual(self._post().status_code, 404)
        self.assertEqual(self._post(HTTP_X_WEBHOOK_SECRET="anything").status_code, 404)
        self.assertEqual(WhatsAppMatch.objects.count(), 0)

    @override_settings(WHATSAPP_WEBHOOK_SECRET="s3cret-value")
    def test_webhook_requires_matching_secret(self):
        from apps.tracking.models import WhatsAppMatch

        self.assertEqual(self._post().status_code, 403)
        self.assertEqual(self._post(HTTP_X_WEBHOOK_SECRET="wrong").status_code, 403)
        self.assertEqual(self._post(HTTP_AUTHORIZATION="Bearer wrong").status_code, 403)
        self.assertEqual(WhatsAppMatch.objects.count(), 0)
        self.assertEqual(self._post(HTTP_X_WEBHOOK_SECRET="s3cret-value").status_code, 200)
        self.assertEqual(self._post(HTTP_AUTHORIZATION="Bearer s3cret-value").status_code, 200)
        self.assertEqual(WhatsAppMatch.objects.count(), 2)
