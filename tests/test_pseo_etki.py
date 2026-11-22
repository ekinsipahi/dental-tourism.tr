from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.tracking.management.commands.pseo_etki import parse_landing
from apps.tracking.models import VisitorSession


class PseoEtkiCommandTests(TestCase):
    """pSEO budaması etki raporu: salt-okunur, kaldırılan sayfalara inişi işaretler."""

    def test_parse_landing_families(self):
        self.assertEqual(parse_landing("https://drdevrim.com/disci/silivri/selimpasa/"), ("disci", "silivri", "selimpasa"))
        self.assertEqual(parse_landing("/ru/stomatolog/kadikoy/"), ("ru/stomatolog", "kadikoy", None))
        self.assertEqual(parse_landing("/fr/dentiste/sisli/nisantasi/"), ("fr/dentiste", "sisli", "nisantasi"))
        self.assertEqual(parse_landing("/"), ("home", None, None))
        self.assertEqual(parse_landing("/blog/en-iyi-disci/pendik-acik-disci/"), ("blog/en-iyi-disci/pendik-acik-disci", None, None))

    def test_report_counts_humans_and_removed_landings(self):
        mk = VisitorSession.objects.create
        mk(session_key="a1", site="drd", landing_page="/disci/silivri/", page_views=2)
        mk(session_key="a2", site="drd", landing_page="/disci/sisli/", page_views=3, whatsapp_clicks=1)
        mk(session_key="a3", site="drd", landing_page="/disci/tuzla/", page_views=1, bot_reason="datacenter")
        mk(session_key="b1", site="dbs", landing_page="/blog/en-iyi-disci/pendik-acik-disci/", page_views=1)
        out = StringIO()
        call_command("pseo_etki", days=7, stdout=out)
        text = out.getvalue()
        self.assertIn("===== site=drd =====", text)
        self.assertIn("oturum: toplam=3 insan=2 bot=1", text)
        self.assertIn("kaldırılan sayfalara insan inişi: 1", text.split("===== site=dbs")[0])
        self.assertIn("silivri[KALDIRILDI]=1(0)", text)
        self.assertIn("sisli=1(1)", text)
        self.assertIn("iletişim (insan): oturum=1 whatsapp=1", text)
        dbs = text.split("===== site=dbs")[1]
        self.assertIn("kaldırılan sayfalara insan inişi: 1", dbs)
        self.assertEqual(VisitorSession.objects.count(), 4)  # hiçbir şey yazmaz
