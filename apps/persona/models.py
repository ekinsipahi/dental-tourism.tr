"""
Persona tabanlı kişiselleştirme.

Üç katman:
  1. Inference  — Ziyaretçinin hangi persona'ya ait olduğunu tahmin eder
                  (arama niyeti / reklam kelimesi + sayfa içi davranış → olasılık dağılımı)
  2. Policy     — Hangi persona varyantının GÖSTERİLECEĞİNE karar verir.
                  Thompson Sampling (contextual bandit, segment bazlı) — dönüşümü maksimize eder.
                  Yeterli veri olunca supervised conversion modeli (sklearn) devreye girer.
  3. Feedback   — WhatsApp / telefon / form dönüşümleri exposure'a yazılır, bandit güncellenir.
"""
from django.db import models
from django.utils import timezone

PERSONA_UNKNOWN = "unknown"
PERSONA_SKEPTIC = "skeptic"   # Araştırmacı / şüpheci
PERSONA_PRICE = "price"       # Fiyat odaklı
PERSONA_PREMIUM = "premium"   # Lüks / kalite
PERSONA_READY = "ready"       # Karar vermiş
PERSONA_FEAR = "fear"         # Komplikasyon / yurtdışı korkusu
PERSONA_SHAME = "shame"       # Gülüşünden utanıyor / estetik
PERSONA_URGENCY = "urgency"   # Acil / düğün / tatil
PERSONA_TRUST = "trust"       # Güven odaklı, yavaş karar

PERSONAS = [PERSONA_SKEPTIC, PERSONA_PRICE, PERSONA_PREMIUM, PERSONA_READY,
            PERSONA_FEAR, PERSONA_SHAME, PERSONA_URGENCY, PERSONA_TRUST]

PERSONA_CHOICES = [
    (PERSONA_UNKNOWN, "Unknown"),
    (PERSONA_SKEPTIC, "Skeptic — research-focused"),
    (PERSONA_PRICE, "Price-sensitive"),
    (PERSONA_PREMIUM, "Premium — quality-focused"),
    (PERSONA_READY, "Ready — decision made"),
    (PERSONA_FEAR, "Fear — safety concerns"),
    (PERSONA_SHAME, "Aesthetic — smile confidence"),
    (PERSONA_URGENCY, "Urgency — time pressure"),
    (PERSONA_TRUST, "Trust — slow decision"),
]

PERSONA_THEME = {p: f"theme-{p}" for p in [PERSONA_UNKNOWN] + PERSONAS}
PERSONA_THEME[PERSONA_UNKNOWN] = "theme-default"


class VisitorSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    visitor_id = models.CharField(max_length=40, blank=True, db_index=True,
                                  help_text="Kalıcı ziyaretçi kimliği (dt_vid çerezi + localStorage) — oturum değişse de aynı kişi")
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    visit_started_at = models.DateTimeField(default=timezone.now)
    ip_hash = models.CharField(max_length=64, blank=True)
    country_code = models.CharField(max_length=5, blank=True)
    language_code = models.CharField(max_length=10, blank=True)
    device_type = models.CharField(max_length=10, blank=True)
    referral_source = models.CharField(max_length=100, blank=True)

    # Bağlam (ilk girişte yakalanır)
    landing_path = models.CharField(max_length=500, blank=True)
    search_query = models.CharField(max_length=300, blank=True, help_text="utm_term / reklam kelimesi")
    intent_scores = models.JSONField(default=dict, blank=True, help_text="Arama niyetinden persona öncülü")
    page_scores = models.JSONField(default=dict, blank=True,
                                   help_text="Site içinde gezilen sayfalardan persona kanıtı (fiyat sayfaları → price, "
                                             "lüks tedaviler / 'en iyi klinik' → premium …)")
    pages_seen = models.JSONField(default=list, blank=True, help_text="Son gezilen sayfa türleri (en fazla 30)")

    total_sessions = models.PositiveIntegerField(default=1)
    total_page_views = models.PositiveIntegerField(default=0)
    total_time_spent_sec = models.PositiveIntegerField(default=0)
    avg_scroll_depth = models.FloatField(default=0.0)
    max_scroll_depth = models.FloatField(default=0.0)

    # Davranış sinyalleri
    price_section_clicks = models.PositiveIntegerField(default=0)
    price_section_time = models.PositiveIntegerField(default=0)
    gallery_views = models.PositiveIntegerField(default=0)
    doctor_profile_views = models.PositiveIntegerField(default=0)
    before_after_views = models.PositiveIntegerField(default=0)
    before_after_time = models.PositiveIntegerField(default=0)
    faq_interactions = models.PositiveIntegerField(default=0)
    cta_clicks = models.PositiveIntegerField(default=0)
    whatsapp_clicks = models.PositiveIntegerField(default=0)
    phone_clicks = models.PositiveIntegerField(default=0)
    form_starts = models.PositiveIntegerField(default=0)
    form_submits = models.PositiveIntegerField(default=0)
    review_section_time = models.PositiveIntegerField(default=0)
    certification_clicks = models.PositiveIntegerField(default=0)
    urgency_keyword_hits = models.PositiveIntegerField(default=0)
    video_watch_time = models.PositiveIntegerField(default=0)
    video_plays = models.PositiveIntegerField(default=0)
    testimonial_reads = models.PositiveIntegerField(default=0)
    safety_section_time = models.PositiveIntegerField(default=0)
    blog_reads = models.PositiveIntegerField(default=0)

    # Persona
    assigned_persona = models.CharField(max_length=20, choices=PERSONA_CHOICES, default=PERSONA_UNKNOWN)
    persona_confidence = models.FloatField(default=0.0)
    persona_scores = models.JSONField(default=dict, blank=True, help_text="Inference olasılık dağılımı")
    persona_method = models.CharField(max_length=10, default="rule",
                                      choices=[("rule", "Rule"), ("bandit", "Bandit"), ("ml", "ML model"),
                                               ("forced", "Forced/preview")])
    persona_updated_at = models.DateTimeField(null=True, blank=True)
    persona_switches = models.PositiveIntegerField(default=0)
    previous_personas = models.JSONField(default=list)
    shown_persona = models.CharField(max_length=20, choices=PERSONA_CHOICES, default=PERSONA_UNKNOWN,
                                     help_text="Bu ziyarette gösterilen varyant (policy kararı)")

    last_persona_at_exit = models.CharField(max_length=20, blank=True)
    bounce_count = models.PositiveIntegerField(default=0)
    last_session_duration = models.PositiveIntegerField(default=0)

    converted = models.BooleanField(default=False)
    converted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["assigned_persona"]), models.Index(fields=["created_at"])]

    def __str__(self):
        return f"Session {self.session_key[:8]}… [{self.assigned_persona}]"

    def update_persona(self, new_persona, confidence, method="rule"):
        if new_persona != self.assigned_persona and new_persona != PERSONA_UNKNOWN:
            self.previous_personas = (self.previous_personas + [{
                "persona": self.assigned_persona,
                "switched_at": timezone.now().isoformat(),
                "confidence": self.persona_confidence,
            }])[-20:]
            self.persona_switches += 1
        self.assigned_persona = new_persona
        self.persona_confidence = confidence
        self.persona_method = method
        self.persona_updated_at = timezone.now()


class BehaviorEvent(models.Model):
    EVENT_TYPES = [
        ("scroll", "Scroll"), ("time_on_page", "Time on page"), ("section_view", "Section view"),
        ("section_time", "Section dwell time"), ("cta_click", "CTA click"), ("whatsapp_click", "WhatsApp"),
        ("phone_click", "Phone"), ("form_start", "Form start"), ("form_submit", "Form submit"),
        ("video_play", "Video play"), ("video_time", "Video time"), ("gallery_view", "Gallery view"),
        ("price_hover", "Price hover"), ("review_read", "Review read"), ("faq_open", "FAQ open"),
        ("click", "Click"), ("bounce", "Bounce"), ("cert_click", "Certification click"),
        ("before_after", "Before/after"), ("urgency_cta", "Urgency CTA"), ("pageview", "Page view"),
    ]

    session = models.ForeignKey(VisitorSession, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)
    page_url = models.CharField(max_length=500, blank=True)
    page_type = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["session", "event_type"]), models.Index(fields=["event_type", "timestamp"])]


class PersonaExposure(models.Model):
    """Bir ziyarette gösterilen persona varyantı + sonucu. Bandit ve ML'in eğitim verisi."""
    session = models.ForeignKey(VisitorSession, on_delete=models.CASCADE, related_name="exposures")
    visit_number = models.PositiveIntegerField(default=1)
    persona = models.CharField(max_length=20, choices=PERSONA_CHOICES)
    inferred_persona = models.CharField(max_length=20, choices=PERSONA_CHOICES, default=PERSONA_UNKNOWN)
    segment = models.CharField(max_length=60, db_index=True)
    policy = models.CharField(max_length=10, default="bandit")
    propensity = models.FloatField(default=0.0, help_text="Policy'nin bu varyantı seçme olasılığı (tahmini)")
    features = models.JSONField(default=dict)
    model_version = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    converted = models.BooleanField(default=False)
    conversion_type = models.CharField(max_length=20, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["segment", "persona"])]

    def __str__(self):
        return f"{self.persona} @ {self.segment} ({'✓' if self.converted else '·'})"


class PersonaArmStat(models.Model):
    """Thompson Sampling için segment × persona başarı istatistikleri (Beta-Bernoulli)."""
    segment = models.CharField(max_length=60)
    persona = models.CharField(max_length=20, choices=PERSONA_CHOICES)
    impressions = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("segment", "persona")]
        ordering = ["segment", "persona"]

    @property
    def rate(self):
        return self.conversions / self.impressions if self.impressions else 0.0

    def __str__(self):
        return f"{self.segment} / {self.persona}: {self.conversions}/{self.impressions}"


class MLModelVersion(models.Model):
    version = models.CharField(max_length=30)
    kind = models.CharField(max_length=20, default="conversion")
    trained_at = models.DateTimeField(auto_now_add=True)
    training_samples = models.PositiveIntegerField()
    positives = models.PositiveIntegerField(default=0)
    accuracy = models.FloatField(help_text="CV ROC-AUC")
    metrics = models.JSONField(default=dict, blank=True)
    model_path = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)
    feature_names = models.JSONField(default=list)
    class_names = models.JSONField(default=list)

    class Meta:
        ordering = ["-trained_at"]

    def __str__(self):
        return f"{self.kind} v{self.version} (AUC {self.accuracy:.3f})"
