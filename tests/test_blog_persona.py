"""Blog → persona: kategori sinyali (güvenlik yazısı = korku + kanıt), yazı gövdesinde okuma süresi, yazı linki tıklaması,
yazar kutusu = hekim profili. Kardeş sitelerde şablon değişikliği gerekmez; href ve bölüm adları merkezde çözülür."""
import io
import json

from django.core.management import call_command

from apps.persona.models import VisitorSession

from .base import SeededTestCase, visit

ART = "/blog/safety-and-quality/is-it-safe-to-get-dental-implants-in-turkey/"


def _ev(c, etype, data, page_url=ART, page_type=""):
    body = {"event_type": etype, "data": data, "page_url": page_url}
    if page_type:
        body["page_type"] = page_type
    return c.post("/api/tracking/event/", data=json.dumps(body), content_type="application/json")


class BlogPersonaTests(SeededTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("seed_blog", stdout=io.StringIO())  # gerçek yazı (apps/blog/content)

    def _session(self):
        return VisitorSession.objects.get(session_key=self.client.session.session_key)

    def _labels(self, s):
        return json.dumps(s.evidence, ensure_ascii=False)

    def test_safety_article_view_adds_fear_and_skeptic(self):
        visit(self.client, ART)
        s = self._session()
        self.assertGreater(s.page_scores.get("fear", 0), 0)
        self.assertGreater(s.page_scores.get("skeptic", 0), 0)
        self.assertTrue(any(k.startswith("blog:safety-and-quality:") for k in s.pages_seen), s.pages_seen)

    def test_reading_body_for_a_minute_is_evidence_once(self):
        visit(self.client, ART)
        _ev(self.client, "section_time", {"section": "content", "seconds": 95}, page_type="blog_detail")
        _ev(self.client, "section_time", {"section": "content", "seconds": 40}, page_type="blog_detail")
        s = self._session()
        self.assertEqual(self._labels(s).count("Hekim yazısını okudu"), 1)
        # 20 sn göz atma okuma sayılmaz
        c2 = self.client_class(HTTP_USER_AGENT=self.client.defaults["HTTP_USER_AGENT"])
        visit(c2, ART)
        _ev(c2, "section_time", {"section": "content", "seconds": 20}, page_type="blog_detail")
        s2 = VisitorSession.objects.get(session_key=c2.session.session_key)
        self.assertNotIn("Hekim yazısını okudu", self._labels(s2))

    def test_author_box_counts_as_doctor_profile_glance(self):
        from apps.persona.engine import canonical_section

        self.assertEqual(canonical_section("author"), "doctor")
        self.assertEqual(canonical_section("yazi"), "blog")
        self.assertEqual(canonical_section("content"), "content")  # bilerek sinyalsiz kalır (okuma kuralı ayrı)

    def test_blog_link_click_is_a_research_signal(self):
        visit(self.client, "/guide/dental-care-turkey/")
        _ev(self.client, "nav_click", {"element": "blog", "label": "Is it safe to get dental implants in Turkey?",
                                       "href": ART}, page_url="/guide/dental-care-turkey/")
        _ev(self.client, "nav_click", {"element": "blog", "label": "Is it safe to get dental implants in Turkey?",
                                       "href": ART}, page_url="/guide/dental-care-turkey/")
        s = self._session()
        self.assertEqual(self._labels(s).count("Hekim yazısına tıkladı"), 1)
        # kardeş site biçimi: data-track olmadan, href'ten (soru-cevap)
        _ev(self.client, "ui_click", {"element": "ui", "label": "Gece diş ağrısı", "href": "/soru-cevap/gece-dis-agrisi/"},
            page_url="/")
        s = self._session()
        self.assertEqual(self._labels(s).count("Hekim yazısına tıkladı"), 2)
