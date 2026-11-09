"""Bot tespiti: canlı veride oturum açtığı görülen tarayıcı-dışı istemciler (GoogleOther, Go-http-client, prefetch
proxy, kırpık "Mozilla/5.0" …) bot sayılır; gerçek tarayıcılar sayılmaz."""
from django.test import Client

from .base import SeededTestCase

BOTS = [
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.8010.52 Mobile Safari/537.36 (compatible; GoogleOther)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GoogleOther) Chrome/153.0.8010.52 Safari/537.36",
    "Chrome Privacy Preserving Prefetch Proxy", "Go-http-client/2.0", "Mozilla/5.0 (compatible; rust_sniffer/0.1; +https://github.com/)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) SkypeUriPreview Preview/0.5 skype-url-preview@microsoft.com",
    "Mozilla/5.0", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120", "python-requests/2.32", "",
]
HUMANS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]


class BotDetectionTests(SeededTestCase):
    def test_non_browser_clients_get_no_tracking_session(self):
        from apps.tracking.models import VisitorSession

        for ua in BOTS:
            c = Client(HTTP_USER_AGENT=ua)
            r = c.get("/")
            self.assertEqual(r.status_code, 200, ua)
            self.assertNotIn("sessionid", r.cookies, ua)  # oturum çerezi bile açılmaz
        self.assertEqual(VisitorSession.objects.count(), 0)

    def test_real_browsers_are_tracked(self):
        from apps.tracking.models import VisitorSession

        for ua in HUMANS:
            c = Client(HTTP_USER_AGENT=ua)
            self.assertEqual(c.get("/").status_code, 200, ua)
            self.assertIn("sessionid", c.cookies, ua)
        self.assertEqual(VisitorSession.objects.count(), len(HUMANS))
