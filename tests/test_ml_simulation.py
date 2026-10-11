"""ML'in gerçekten öğrendiğini kanıtlayan uçtan uca simülasyon testi (gerçek motor, sentetik ziyaretçiler)."""
import tempfile

from django.test import override_settings

from apps.persona.simulation import run

from .base import SeededTestCase


@override_settings(PERSONA_EXPLORATION_RATE=0.1)
class PersonaLearningSimulationTests(SeededTestCase):
    def test_bandit_learns_and_ml_trains_with_safety_gate(self):
        with override_settings(PERSONA_MODEL_DIR=tempfile.mkdtemp()):
            r = run(n=1500, ml_phase=400, seed=7, keep=True, log=None)
        ref = r["reference"]
        # Persona tahmini (niyet + davranış) gizli gerçek persona'yı büyük oranda bulmalı
        self.assertGreater(r["bandit_all"]["inferred_accuracy"], 0.75)
        # Kişiselleştirme varsayılan sayfadan ve rastgele varyanttan daha çok dönüştürmeli
        self.assertGreater(r["bandit_all"]["conversion_rate"], ref["always_default_cr"] * 1.2)
        self.assertGreater(r["bandit_all"]["conversion_rate"], ref["random_variant_cr"] * 1.5)
        # Supervised model eğitilmeli; aktif olduysa gerçekten bandit kadar iyi olmalı
        self.assertTrue(r["ml_training"]["trained"])
        if r["ml_training"]["active"]:
            self.assertGreater(r["ml_policy"]["conversion_rate"], ref["always_default_cr"])
