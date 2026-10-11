import json

from django.test import override_settings

from apps.persona import bandit
from apps.persona.engine import infer
from apps.persona.intent import score_text
from apps.persona.models import PersonaArmStat, PersonaExposure, VisitorSession

from .base import SeededTestCase


class IntentTests(SeededTestCase):
    def test_multilingual_price_intent(self):
        for q in ["dental implants turkey cost", "zahnimplantate türkei kosten", "tandimplantaten turkije prijs",
                  "цена зубных имплантов турция", "اسعار زراعة الأسنان في تركيا", "implant fiyatları istanbul"]:
            with self.subTest(q=q):
                scores = score_text(q)
                self.assertEqual(max(scores, key=scores.get), "price")

    def test_cheap_need_and_quality_are_different_intents(self):
        def top(q):
            sc = score_text(q)
            return max(sc, key=sc.get) if sc else None
        self.assertEqual(top("cheap dental turkey"), "price")
        self.assertEqual(top("zahnarzt türkei billig"), "price")
        self.assertEqual(top("dental work turkey"), "trust")
        self.assertEqual(top("türkiyede diş yaptırmak"), "trust")
        self.assertEqual(top("best dental clinic turkey"), "quality")
        self.assertEqual(top("high quality dentist istanbul"), "quality")
        self.assertEqual(top("kaliteli diş kliniği istanbul"), "quality")
        self.assertEqual(top("cheap dental work turkey"), "price")      # karışık: en güçlü sinyal
        self.assertEqual(top("best dental work turkey"), "quality")

    def test_quality_and_luxury_are_different_personas(self):
        def top(q):
            sc = score_text(q)
            return max(sc, key=sc.get) if sc else None
        # Kalite / kişiye özel tedavi arayan
        self.assertEqual(top("kişiye özel diş tedavisi istanbul"), "quality")
        self.assertEqual(top("natural looking veneers no shaving"), "quality")
        self.assertEqual(top("individuelle zahnbehandlung türkei"), "quality")
        # Lüks / VIP hissi arayan
        self.assertEqual(top("luxury dental clinic istanbul"), "premium")
        self.assertEqual(top("vip dental turkey"), "premium")
        self.assertEqual(top("lüks diş kliniği istanbul"), "premium")
        self.assertEqual(top("beste zahnklinik istanbul luxus"), "premium")
        self.assertNotEqual(top("dental tourism packages"), "price")    # paket ≠ ucuz

    def test_fear_and_skeptic_intent(self):
        self.assertEqual(max(score_text("is it safe veneers turkey horror"), key=lambda k: score_text(
            "is it safe veneers turkey horror")[k]), "fear")
        self.assertIn("skeptic", score_text("veneers türkei erfahrungen"))

    def test_short_words_need_word_boundary(self):
        self.assertNotIn("skeptic", score_text("dvs implant"))  # "vs" kelime içinde eşleşmemeli


class InferenceTests(SeededTestCase):
    def test_no_signal_defaults_to_unknown(self):
        s = VisitorSession(session_key="x")
        probs = infer(s)
        self.assertEqual(max(probs, key=probs.get), "unknown")

    def test_behavior_shifts_to_shame(self):
        s = VisitorSession(session_key="y", before_after_views=3, before_after_time=120, gallery_views=2)
        probs = infer(s)
        self.assertEqual(max(probs, key=probs.get), "shame")


@override_settings(PERSONA_EXPLORATION_RATE=0.0)
class BanditTests(SeededTestCase):
    def test_cold_start_follows_strong_inference(self):
        picks = [bandit.choose("price|mobile|paid", {"price": 0.8, "unknown": 0.05})[0] for _ in range(60)]
        self.assertGreater(picks.count("price") / len(picks), 0.8)

    def test_learned_rates_override_inference(self):
        seg = "price|desktop|organic"
        for level in (seg, "price|*"):
            PersonaArmStat.objects.create(segment=level, persona="price", impressions=2000, conversions=10)
            PersonaArmStat.objects.create(segment=level, persona="trust", impressions=2000, conversions=200)
        picks = [bandit.choose(seg, {"price": 0.6, "unknown": 0.1})[0] for _ in range(60)]
        self.assertGreater(picks.count("trust"), picks.count("price"))


class EndToEndPersonaTests(SeededTestCase):
    def test_visit_creates_exposure_and_whatsapp_click_converts(self):
        self.client.get("/de/?utm_term=zahnimplantate+kosten&gclid=x")
        session = VisitorSession.objects.get()
        self.assertEqual(session.search_query, "zahnimplantate kosten")
        exposure = PersonaExposure.objects.get(session=session)
        self.client.post("/api/tracking/event/", data=json.dumps({"event_type": "whatsapp_click", "data": {}}),
                         content_type="application/json")
        exposure.refresh_from_db()
        self.assertTrue(exposure.converted)
        stat = PersonaArmStat.objects.get(segment=exposure.segment, persona=exposure.persona)
        self.assertEqual((stat.impressions, stat.conversions), (1, 1))

    def test_one_exposure_per_visit(self):
        for _ in range(3):
            self.client.get("/")
        self.assertEqual(PersonaExposure.objects.count(), 1)

    def test_bots_are_not_tracked_and_see_default(self):
        r = self.client.get("/", HTTP_USER_AGENT="Mozilla/5.0 (compatible; Googlebot/2.1)")
        self.assertIn('data-persona="unknown"', r.content.decode())
        self.assertFalse(VisitorSession.objects.exists())

    def test_staff_preview_forces_variant_without_exposure(self):
        with override_settings(DEBUG=True):
            r = self.client.get("/?persona=premium")
            q = self.client.get("/?persona=quality")
        self.assertIn('data-persona="premium"', r.content.decode())
        self.assertIn('data-persona="quality"', q.content.decode())
        self.assertIn("Quality dental treatment in Istanbul", q.content.decode())
        self.assertFalse(PersonaExposure.objects.exists())

    def test_ml_train_reports_insufficient_data(self):
        from apps.persona.ml import train

        self.assertFalse(train()["trained"])
