"""Admin ana sayfası: dönüşüm/ziyaretçi KPI'ları yalnızca gerçek (JS beacon'lı) oturumlardan hesaplanır."""
import json

from django.contrib.auth import get_user_model
from django.test import Client

from .base import BROWSER_UA, SeededTestCase, visit


class AdminKpiTests(SeededTestCase):
    def test_dashboard_counts_only_beacon_sessions(self):
        from apps.tracking.models import VisitorSession

        # 1 gerçek ziyaretçi (GET + beacon + WhatsApp tıklaması) ve 1 JS'siz oturum (yalnızca event API ile açılmış ama beacon yok)
        human = Client(HTTP_USER_AGENT=BROWSER_UA)
        visit(human, "/")
        human.post("/api/tracking/event/", data=json.dumps({"event_type": "whatsapp_click", "data": {}}), content_type="application/json")
        junk = Client(HTTP_USER_AGENT=BROWSER_UA)
        junk.get("/")
        junk.post("/api/tracking/event/", data=json.dumps({"event_type": "scroll_depth", "data": {"depth": 10}}), content_type="application/json")
        self.assertEqual(VisitorSession.objects.count(), 2)
        self.assertEqual(VisitorSession.objects.filter(page_views__gt=0).count(), 1)

        admin = get_user_model().objects.create_superuser("adm", "a@a.com", "pw")
        self.client.force_login(admin)
        html = self.client.get("/admin/").content.decode()
        self.assertIn("Gerçek ziyaretçi (30g)", html)
        self.assertIn('<div class="n">1</div><div class="l">Gerçek ziyaretçi', html)
        self.assertIn("%100.0", html)  # 1 ziyaretçi / 1 iletişim
        self.assertEqual(self.client.get("/admin/tracking/visitorsession/?human=yes").status_code, 200)
        stats = json.loads(self.client.get("/api/tracking/dashboard/").content)
        self.assertEqual(stats["total"]["sessions"], 1)
