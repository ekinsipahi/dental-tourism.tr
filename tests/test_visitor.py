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


def _mind(c):
    from apps.persona.mindset import snapshot
    from apps.persona.models import VisitorSession

    return snapshot(VisitorSession.objects.get(session_key=c.session.session_key))


def _ev(c, etype, data, page_url="/"):
    return c.post("/api/tracking/event/", data=json.dumps({"event_type": etype, "data": data, "page_url": page_url}),
                  content_type="application/json")


class PageBehaviourTests(SeededTestCase):
    """Sayfa puanı = açılınca %25 + kalan %75 × okuma süresi (60 sn = tam)."""

    def _visit(self, c, url, seconds):
        c.get(url)
        _ev(c, "time_on_page", {"seconds": seconds}, url)

    def test_reading_price_pages_makes_price(self):
        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        for url in ("/prices/", "/prices/dental-implants/", "/prices/porcelain-veneers/"):
            self._visit(c, url, 60)
        m = _mind(c)
        self.assertEqual(m["top"], "price")
        self.assertNotEqual(m["level"], "weak")

    def test_glancing_at_price_page_is_not_price(self):
        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        self._visit(c, "/prices/", 3)       # 3 sn bakıp çıktı
        self.assertEqual(_mind(c)["level"], "weak")

    def test_browsing_treatments_is_research_not_luxury(self):
        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        for url in ("/treatments/zirconia-crowns/", "/treatments/all-on-4-implants/",
                    "/de/behandlungen/dental-implants/", "/treatments/porcelain-veneers/"):
            self._visit(c, url, 60)
        m = _mind(c)
        ranked = max(m["scores"], key=m["scores"].get)
        self.assertEqual(ranked, "skeptic")
        self.assertNotIn("premium", m["scores"])

    def test_refreshing_same_page_does_not_inflate(self):
        from apps.persona.models import VisitorSession

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        for _ in range(6):
            self._visit(c, "/prices/", 60)
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


class BestClinicReaderTests(SeededTestCase):
    """'best dental clinic turkey reviews' okuyan kişi fiyatçı DEĞİL, kalite arayandır."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from django.core.management import call_command

        call_command("seed_topics", "--no-keywords", verbosity=0, stdout=open("/dev/null", "w"))

    def _session(self, c):
        from apps.persona.models import VisitorSession

        return VisitorSession.objects.get(session_key=c.session.session_key)

    def _event(self, c, etype, data):
        c.post("/api/tracking/event/", data=json.dumps({"event_type": etype, "data": data}),
               content_type="application/json")

    def test_reading_best_clinic_guide_with_price_note_is_quality_not_price(self):
        from apps.seo.models import SeoTopic

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        for key in ("best-dental-clinic-turkey", "best-dental-clinic-istanbul"):
            slug = SeoTopic.objects.get(key=key).slug
            self.assertEqual(c.get(f"/guide/{slug}/").status_code, 200)
            _ev(c, "time_on_page", {"seconds": 90}, f"/guide/{slug}/")
            # Sayfadaki fiyat notu ve kenar kutusu ekranda göründü — bu fiyat ilgisi değildir
            self._event(c, "section_view", {"section": "price-note"})
            self._event(c, "section_time", {"section": "price-note", "seconds": 120})
            self._event(c, "section_time", {"section": "sidebar", "seconds": 300})
        s = self._session(c)
        self.assertEqual(s.price_section_clicks + s.price_section_time, 0)
        m = _mind(c)
        self.assertNotIn("price", m["scores"])
        self.assertEqual(max(m["scores"], key=m["scores"].get), "quality")

    def test_asking_price_in_price_note_is_a_price_signal(self):
        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        c.get("/")
        self._event(c, "whatsapp_click", {"position": "price-note", "label": "Ask for my price on WhatsApp"})
        self.assertEqual(self._session(c).price_section_clicks, 1)

    def test_old_price_browsing_fades_on_new_visit(self):
        from datetime import timedelta

        from django.utils import timezone

        from apps.persona.models import VisitorSession

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        c.get("/prices/")
        c.get("/?utm_term=cheap+dental+turkey")
        s = self._session(c)
        old_price = s.page_scores["price"]
        VisitorSession.objects.filter(pk=s.pk).update(last_seen=timezone.now() - timedelta(days=2))
        from django.core.cache import cache

        cache.clear()
        c.get("/guide/best-dental-clinic-turkey-reviews/")
        s = self._session(c)
        self.assertEqual(s.total_sessions, 2)
        self.assertLess(s.page_scores.get("price", 0), old_price)


class MindsetTests(SeededTestCase):
    """Persona motoru sayar: SSS / sayfa / tıklama → 'aklındaki'; arama anında admin'e yazılır, sayfada canlı mesaj."""

    def _event(self, c, etype, data):
        return c.post("/api/tracking/event/", data=json.dumps({"event_type": etype, "data": data}),
                      content_type="application/json")

    def test_pain_faq_makes_fear_and_call_records_it(self):
        from django.contrib.auth import get_user_model

        from apps.tracking.models import ContactClick

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        c.get("/")
        r = self._event(c, "faq_open", {"q": "Is dental surgery painful?"})
        self.assertIn("mind", r.json())                                 # sayfa yenilenmeden yeni teşhis (localStorage)
        self._event(c, "faq_read", {"q": "Is dental surgery painful?", "seconds": 9})
        self._event(c, "faq_open", {"q": "Acıtır mı?"})
        r = self._event(c, "faq_read", {"q": "Acıtır mı?", "seconds": 6})
        self.assertEqual(r.json().get("mind"), "fear")
        html = c.get("/").content.decode()
        self.assertIn('data-mind="fear"', html)
        self.assertIn('data-persona="unknown"', html)                  # gözlem modu: arayüz değişmez
        self.assertNotIn('class="mind-nudge"', html)
        self._event(c, "phone_click", {"label": "Call", "position": "navbar"})
        click = ContactClick.objects.get(event_type="phone_click")
        self.assertEqual(click.mind, "fear")
        self.assertTrue(any("Is dental surgery painful?" in w["l"] for w in click.mindset["why"]))

        admin = get_user_model().objects.create_superuser("adm2", "b@b.com", "pw")
        c.force_login(admin)
        page = c.get("/admin/tracking/contactclick/?mind=fear")
        self.assertContains(page, "Korku")
        self.assertEqual(c.get("/admin/persona/visitorsession/").status_code, 200)

    def test_same_question_counted_once_per_visit(self):
        from apps.persona.models import VisitorSession

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        c.get("/")
        for _ in range(4):
            self._event(c, "faq_open", {"q": "Does it hurt?"})
            self._event(c, "faq_read", {"q": "Does it hurt?", "seconds": 10})
        s = VisitorSession.objects.get(session_key=c.session.session_key)
        self.assertEqual(len([e for e in s.evidence if e["k"] == "faq"]), 1)
        self.assertEqual(len([e for e in s.evidence if e["k"] == "faqr"]), 1)

    def test_one_second_peek_is_weaker_than_reading(self):
        from apps.persona.models import VisitorSession

        peek, read = Client(HTTP_USER_AGENT=BROWSER_UA), Client(HTTP_USER_AGENT=BROWSER_UA)
        for c, secs in ((peek, 1), (read, 8)):
            c.get("/")
            self._event(c, "faq_open", {"q": "How much does dental treatment in Istanbul cost?", "mind": "price"})
            self._event(c, "faq_read", {"q": "How much does dental treatment in Istanbul cost?", "mind": "price",
                                        "seconds": secs})
        p = VisitorSession.objects.get(session_key=peek.session.session_key).page_scores["price"]
        r = VisitorSession.objects.get(session_key=read.session.session_key).page_scores["price"]
        self.assertAlmostEqual(p, 0.45, places=2)   # yalnızca açma payı (%30 × 1.5)
        self.assertAlmostEqual(r, 1.5, places=2)    # tam puan

    def test_safety_question_is_skeptic_not_fear(self):
        from apps.persona.mindset import score_content

        sc = score_content("Is dental care in Turkey safe?")
        self.assertEqual(max(sc, key=sc.get), "skeptic")
        self.assertNotIn("fear", sc)
        self.assertEqual(max(score_content("Why is dental care in Turkey so affordable?").items(),
                             key=lambda x: x[1])[0], "price")

    def test_lead_gets_mindset(self):
        from apps.tracking.models import Lead

        c = Client(HTTP_USER_AGENT=BROWSER_UA)
        for url in ("/prices/", "/prices/dental-implants/"):
            c.get(url)
            c.post("/api/tracking/event/", data=json.dumps({"event_type": "time_on_page", "data": {"seconds": 70},
                                                            "page_url": url}), content_type="application/json")
        self._event(c, "faq_open", {"q": "Can I pay in installments?"})
        self._event(c, "faq_read", {"q": "Can I pay in installments?", "seconds": 8})
        c.post("/api/tracking/lead/", data=json.dumps({"name": "Tom", "phone": "+447700900123", "page": "/prices/"}),
               content_type="application/json")
        self.assertEqual(Lead.objects.get().mind, "price")


class ResultsAndFaqEverywhereTests(SeededTestCase):
    """Önce/sonra sonuçları + ortak SSS her sayfada tek kez; sıra: zirkonya → kompozit → Sanem, Hazan."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from django.core.management import call_command

        call_command("seed_media", stdout=open("/dev/null", "w"))
        call_command("seed_topics", "--no-keywords", verbosity=0, stdout=open("/dev/null", "w"))

    def test_results_and_faq_on_every_page_once(self):
        for url in ("/", "/about/", "/prices/", "/treatments/dental-implants/", "/guide/dental-care-turkey/", "/de/"):
            html = self.client.get(url).content.decode()
            self.assertEqual(html.count('id="results"'), 1, url)
            self.assertEqual(html.count('id="faq-h2"'), 1, url)
            self.assertGreaterEqual(html.count("data-mind-q="), 9, url)

    def test_case_order_and_translation(self):
        import re

        html = self.client.get("/").content.decode()
        srcs = re.findall(r'cases/([a-z0-9-]+)-after\.jpg', html)
        self.assertEqual(srcs, ["zirconia-1", "zirconia-2", "composite-1", "composite-2", "sanem", "hazan"])
        self.assertLess(html.index('id="reviews-h2"'), html.index('id="results"'))   # ana sayfada yorumların altında
        de = self.client.get("/de/").content.decode()
        self.assertIn("Natürliches monolithisches Zirkon", de)
