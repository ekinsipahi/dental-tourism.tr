"""Kardeş sitelerde (drdevrim.com, devrimbirikensipahi.com.tr) persona motoru: sayfa TÜRÜ + gezinme sırası + süre +
serbest metin SSS + iletişim tıklamaları + aramadan dönüş → kişilik ve huni aşaması. Gerçek uçlar üzerinden (/api/t/)."""
import json

from django.test import Client

from apps.persona.engine import funnel_stage
from apps.persona.mindset import faq_topic, snapshot
from apps.persona.models import VisitorSession as PersonaSession

from .base import BROWSER_UA, SeededTestCase

VID = "a" * 32
DRD, DBS = "https://drdevrim.com", "https://devrimbirikensipahi.com.tr"


class _Site:
    """Bir kardeş sitede gezinen tarayıcı: pageview + olay beacon'ları (text/plain, çerezsiz)."""

    def __init__(self, site, origin, sid):
        self.site, self.origin, self.sid = site, origin, sid
        self.c = Client()

    def _post(self, path, body):
        body.update({"site": self.site, "vid": VID, "sid": self.sid})
        return self.c.post(path, data=json.dumps(body), content_type="text/plain", HTTP_USER_AGENT=BROWSER_UA,
                           HTTP_ORIGIN=self.origin)

    def page(self, path, seconds=None, **extra):
        r = self._post("/api/t/pageview/", {"url": self.origin + path, "title": "t", **extra})
        assert r.status_code == 200, r.content
        if seconds is not None:
            self.event("time_on_page", {"seconds": seconds, "segment": 0}, path)
        return r

    def event(self, etype, data, path="/"):
        r = self._post("/api/t/event/", {"events": [{"event_type": etype, "data": data, "page_url": path}]})
        assert r.status_code == 200, r.content
        return r

    @property
    def session(self):
        return PersonaSession.objects.get(session_key=f"{self.site}:{self.sid}")

    def mind(self):
        return snapshot(self.session)


class DrDevrimJourneyTests(SeededTestCase):
    def test_bounce_only_visit_stays_unknown(self):
        b = _Site("drd", DRD, "1" * 24)
        b.page("/", seconds=4)
        s = b.session
        self.assertEqual((s.site, s.assigned_persona), ("drd", "unknown"))
        self.assertEqual(b.mind()["level"], "weak")
        self.assertEqual(funnel_stage(s), "awareness")

    def test_area_treatment_doctor_faq_phone_journey_is_a_decided_trust_or_price_persona(self):
        b = _Site("drd", DRD, "2" * 24)
        b.page("/en/dentist/sisli/nisantasi", seconds=20)
        b.page("/hizmetler/implant", seconds=45)
        b.page("/doktorlar", seconds=40)
        b.event("faq_open", {"q": "Fiyatlar?"}, "/doktorlar")
        b.event("faq_read", {"q": "Fiyatlar?", "seconds": 15}, "/doktorlar")
        r = b.event("phone_click", {"element": "phone", "label": "Hemen Ara", "position": "float"}, "/doktorlar")
        s = b.session
        self.assertNotEqual(s.assigned_persona, "unknown")
        m = b.mind()
        # Karışık yolculuk: hekim (güven) + fiyat SSS'si + telefon — ilk üçü bunlar, 'belirsiz' değil
        self.assertIn(m["top"], ("trust", "price", "ready"))
        self.assertEqual(set(m["scores"]) <= {"trust", "price", "ready", "skeptic"}, True)
        self.assertGreaterEqual(m["signals"], 6)
        self.assertEqual(s.assigned_persona, m["top"])
        self.assertEqual(funnel_stage(s), "decision")
        # Kanıt günlüğü: sayfa türleri, SSS ve tıklama okunabilir etiketlerle
        labels = " | ".join(e["l"] for e in s.evidence)
        self.assertIn("treatment@/hizmetler/implant — 45 sn", labels)
        self.assertIn("doctor@/doktorlar — 40 sn", labels)
        self.assertIn("SSS okudu (15 sn): Fiyatlar?", labels)
        self.assertIn("Telefonu tıkladı (float)", labels)
        self.assertIn("hekime baktı — güven arıyor", labels)
        self.assertGreater(s.page_scores.get("price", 0), 0.9)      # "Fiyatlar?" 15 sn okundu → tam puan
        self.assertGreater(s.page_scores.get("trust", 0), 0.9)      # hekim sayfası 40 sn + tedaviden sonra hekime geçiş
        self.assertEqual(s.phone_clicks, 1)
        self.assertEqual(r.status_code, 200)

    def test_switching_between_treatments_is_undecided_research(self):
        b = _Site("drd", DRD, "3" * 24)
        for path in ("/hizmetler/implant", "/hizmetler/zirkonyum-kaplama", "/hizmetler/lamina", "/hizmetler/dis-beyazlatma"):
            b.page(path, seconds=35)
        s = b.session
        m = b.mind()
        self.assertEqual(m["top"], "skeptic")
        self.assertNotEqual(m["level"], "weak")
        self.assertEqual(sum(1 for e in s.evidence if "Tedaviler arası geçiş" in e["l"]), 3)
        self.assertEqual(funnel_stage(s), "consideration")

    def test_reviews_after_doctor_is_skeptic_and_multiple_area_pages_add_urgency(self):
        b = _Site("drd", DRD, "4" * 24)
        b.page("/doktorlar", seconds=30)
        b.page("/hasta-yorumlari", seconds=80)
        s = b.session
        self.assertTrue(any("yorumlara geçti" in e["l"] for e in s.evidence))
        self.assertGreater(s.page_scores.get("skeptic", 0), 0.9)
        self.assertIn(b.mind()["top"], ("skeptic", "trust"))

        a = _Site("drd", DRD, "5" * 24)
        for path in ("/disci/sisli", "/disci/nisantasi", "/en/dentist/sisli/mecidiyekoy"):
            a.page(path, seconds=15)
        s = a.session
        self.assertTrue(any("bölge sayfası" in e["l"] for e in s.evidence))
        self.assertGreater(s.page_scores.get("urgency", 0), 0.7)
        self.assertGreater(s.page_scores.get("ready", 0), 0.7)

    def test_contact_return_maps_language_and_sections_feed_the_mind(self):
        b = _Site("drd", DRD, "6" * 24)
        b.page("/", seconds=50)
        b.event("language_switch", {"to": "en"}, "/")
        b.event("section_view", {"section": "yorumlar"}, "/")
        b.event("section_time", {"section": "yorumlar", "seconds": 60}, "/")
        b.event("section_view", {"section": "doktorlar"}, "/")
        b.event("section_time", {"section": "fiyatlar", "seconds": 40}, "/")
        b.event("scroll_depth", {"depth": 90}, "/")
        b.event("maps_click", {"element": "maps", "position": "footer"}, "/")
        b.event("contact_return", {"kind": "maps", "away_seconds": 25, "likely_contacted": True}, "/")
        s = b.session
        self.assertEqual((s.testimonial_reads, s.review_section_time, s.doctor_profile_views, s.price_section_time),
                         (1, 60, 1, 40))
        self.assertEqual(s.max_scroll_depth, 90)
        labels = " | ".join(e["l"] for e in s.evidence)
        self.assertIn("Dil değiştirdi → en", labels)
        self.assertIn("Yol tarifine baktı (harita) (footer)", labels)
        self.assertIn("maps sonrası siteye döndü (25 sn uzakta)", labels)
        self.assertGreaterEqual(s.page_scores.get("ready", 0), 2.4)   # harita 1.0 + dönüş 1.5
        self.assertEqual(s.events.filter(event_type__in=["maps_click", "contact_return", "language_switch"]).count(), 3)
        self.assertNotEqual(s.assigned_persona, "unknown")

    def test_immediate_call_from_landing_page_is_urgent_and_decided(self):
        b = _Site("drd", DRD, "7" * 24)
        b.page("/disci/sisli")
        b.event("phone_click", {"element": "phone", "position": "navbar"}, "/disci/sisli")
        s = b.session
        self.assertTrue(any(e["l"].startswith("Telefonu tıkladı") for e in s.evidence))
        self.assertGreaterEqual(s.page_scores.get("urgency", 0), 0.5)
        self.assertEqual(funnel_stage(s), "decision")
        self.assertIn(b.mind()["top"], ("ready", "urgency"))


class DbsJourneyTests(SeededTestCase):
    def test_booking_and_redirect_pages_are_ready_and_free_text_faq_in_german(self):
        b = _Site("dbs", DBS, "8" * 24)
        b.page("/de/", seconds=20)
        b.page("/de/implantat", seconds=50)
        b.event("faq_open", {"q": "Tut die Implantation weh?"}, "/de/implantat")
        b.event("faq_read", {"q": "Tut die Implantation weh?", "seconds": 12}, "/de/implantat")
        b.page("/de/randevu-al", seconds=25)
        b.page("/de/whatsapp-yonlendirme/")
        s = b.session
        self.assertEqual(s.site, "dbs")
        self.assertGreater(s.page_scores.get("fear", 0), 1.0)
        self.assertGreater(s.page_scores.get("ready", 0), 1.0)
        self.assertTrue(any("randevuya geçti" in e["l"] for e in s.evidence))
        self.assertIn(b.mind()["top"], ("ready", "fear"))
        self.assertNotEqual(b.mind()["level"], "weak")


class FaqTopicTests(SeededTestCase):
    def test_free_text_questions_in_many_languages(self):
        cases = {
            "Fiyatlar?": "price", "Taksit yapıyor musunuz?": "price", "Колко струва?": "price", "Доступна ли рассрочка?": "price",
            "İmplant ağrılı mı?": "fear", "Czy to boli?": "fear", "هل العلاج مؤلم؟": "fear", "Болит ли установка импланта?": "fear",
            "Tut die Implantation weh?": "fear", "Garanti var mı?": "fear",
            "Hangi marka implant kullanıyorsunuz?": "quality", "Wie lange hält ein Implantat?": "quality",
            "İmplant tedavisi kaç gün sürer?": "urgency", "Combien de jours faut-il rester?": "urgency",
            "Is the clinic safe?": "skeptic", "Hangisi daha iyi: zirkonyum mu porselen mi?": "skeptic",
            "Who will treat me?": "trust", "Kliniğe nasıl ulaşırım?": "ready", "Sarı dişlerim için ne yapabilirim?": "shame",
        }
        for q, want in cases.items():
            with self.subTest(q=q):
                self.assertEqual(faq_topic(q)[0], want)

    def test_section_aliases_keep_price_note_out(self):
        from apps.persona.engine import canonical_section

        self.assertEqual(canonical_section("yorumlar"), "reviews")
        self.assertEqual(canonical_section("hasta-yorumlari"), "reviews")
        self.assertEqual(canonical_section("doktorlar"), "doctor")
        self.assertEqual(canonical_section("sss"), "faq")
        self.assertEqual(canonical_section("fiyatlar"), "price")
        self.assertEqual(canonical_section("Preise"), "price")
        self.assertEqual(canonical_section("once-sonra"), "before_after")
        self.assertEqual(canonical_section("price-note"), "price-note")  # bilerek sayılmaz
        self.assertEqual(canonical_section("hero"), "hero")
        self.assertEqual(canonical_section("price"), "price")


class DecisionDeliveryTests(SeededTestCase):
    """Merkez kararı kardeş siteye verir: pageview/event yanıtında ve /api/t/persona/ ucunda {persona, level, message}."""

    def test_weak_signal_returns_persona_without_message(self):
        b = _Site("drd", DRD, "7" * 24)
        d = json.loads(b.page("/", seconds=None).content)["decision"]
        self.assertEqual(d["level"], "weak")
        self.assertIsNone(d["message"])

    def test_decided_visitor_gets_localized_message_in_the_sister_sites_language(self):
        # drdevrim İngilizce: /lang/en/… → mesaj İngilizce
        b = _Site("drd", DRD, "8" * 24)
        for path in ("/lang/en/hizmetler/implant", "/lang/en/hizmetler/zirkonyum-kaplama",
                     "/lang/en/hizmetler/lamina", "/lang/en/hizmetler/dis-beyazlatma"):
            b.page(path, seconds=35)
        r = b.event("faq_open", {"q": "Is it safe?"}, "/lang/en/hizmetler/lamina")
        d = json.loads(r.content)["decision"]
        self.assertEqual(d["persona"], "skeptic")
        self.assertNotEqual(d["level"], "weak")
        self.assertEqual(d["message"]["key"], "skeptic")
        self.assertEqual(d["message"]["title"], "Everything here is real")
        # Yeniden kontrol ucu (SPA geçişi): yazmaz, aynı kararı döner
        r2 = b._post("/api/t/persona/", {"url": DRD + "/lang/en/doktorlar"})
        self.assertEqual(json.loads(r2.content)["decision"]["message"]["title"], "Everything here is real")

        # devrimbirikensipahi Almanca: /de/… → aynı karar Almanca
        c = _Site("dbs", DBS, "9" * 24)
        for path in ("/de/implant", "/de/zirkonyum", "/de/lamina", "/de/beyazlatma"):
            c.page(path, seconds=35, page_type="treatment")
        d = json.loads(c._post("/api/t/persona/", {"url": DBS + "/de/"}).content)["decision"]
        self.assertEqual(d["persona"], "skeptic")
        self.assertNotEqual(d["message"]["title"], "Everything here is real")  # çevrilmiş metin

    def test_persona_endpoint_rejects_unknown_origin(self):
        c = Client()
        r = c.post("/api/t/persona/", data=json.dumps({"site": "drd", "vid": VID, "sid": "6" * 24, "url": DRD + "/"}),
                   content_type="text/plain", HTTP_USER_AGENT=BROWSER_UA, HTTP_ORIGIN="https://evil.example")
        self.assertEqual(r.status_code, 403)
