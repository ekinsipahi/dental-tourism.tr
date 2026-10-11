"""
apps/tracking/models.py

Modüler tracking sistemi.
Google Ads (gclid) olabilir de olmayabilir de.
Meta Ads (fbclid) olabilir de olmayabilir de.
Organic, Direct, Referral hepsi takip edilir.

Temel mantık:
  Visitor → Session → Events → Conversion (opsiyonel)

Her şey VisitorSession üzerinden geçer.
"""
import uuid
from django.db import models
from django.utils import timezone


# ── Traffic Source ────────────────────────────────────────────────────────────

class TrafficSource:
    """UTM ve ad platform parametrelerinden trafik kaynağı tespiti."""
    GOOGLE_ADS    = "google_ads"
    META_ADS      = "meta_ads"
    GOOGLE_ORG    = "google_organic"
    BING_ORG      = "bing_organic"
    SOCIAL        = "social"
    REFERRAL      = "referral"
    DIRECT        = "direct"
    EMAIL         = "email"
    WHATSAPP      = "whatsapp_direct"
    UNKNOWN       = "unknown"

    CHOICES = [
        (GOOGLE_ADS,  "Google Ads"),
        (META_ADS,    "Meta Ads (FB/IG)"),
        (GOOGLE_ORG,  "Google Organic"),
        (BING_ORG,    "Bing Organic"),
        (SOCIAL,      "Social Media"),
        (REFERRAL,    "Referral"),
        (DIRECT,      "Direct"),
        (EMAIL,       "Email"),
        (WHATSAPP,    "WhatsApp Direct"),
        (UNKNOWN,     "Unknown"),
    ]


# ── VisitorSession ─────────────────────────────────────────────────────────────

class VisitorSession(models.Model):
    """
    Her ziyaretçi = 1 session.
    Session key cookie'den veya fingerprint'ten gelir.
    Tüm tracking bu model üzerinden döner.
    """
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key    = models.CharField(max_length=64, unique=True, db_index=True)
    visitor_id     = models.CharField(max_length=40, blank=True, db_index=True)  # dt_vid — kalıcı ziyaretçi
    created_at     = models.DateTimeField(auto_now_add=True)
    last_seen      = models.DateTimeField(auto_now=True)

    # ── Trafik kaynağı ──
    traffic_source = models.CharField(max_length=30, choices=TrafficSource.CHOICES, default=TrafficSource.UNKNOWN)
    landing_page   = models.CharField(max_length=500, blank=True)
    referrer_url   = models.CharField(max_length=1000, blank=True)

    # ── Google Ads ── (opsiyonel — gclid yoksa null)
    gclid          = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    google_campaign = models.CharField(max_length=255, blank=True)
    google_adgroup  = models.CharField(max_length=255, blank=True)
    google_keyword  = models.CharField(max_length=255, blank=True)
    google_matchtype = models.CharField(max_length=20, blank=True)
    google_network  = models.CharField(max_length=20, blank=True)

    # ── Meta Ads ── (opsiyonel — fbclid yoksa null)
    fbclid         = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    fb_campaign    = models.CharField(max_length=255, blank=True)
    fb_adset       = models.CharField(max_length=255, blank=True)
    fb_ad          = models.CharField(max_length=255, blank=True)
    fb_placement   = models.CharField(max_length=100, blank=True)

    # ── UTM parametreleri ── (herhangi bir kaynaktan gelebilir)
    utm_source   = models.CharField(max_length=255, blank=True)
    utm_medium   = models.CharField(max_length=255, blank=True)
    utm_campaign = models.CharField(max_length=255, blank=True)
    utm_content  = models.CharField(max_length=255, blank=True)
    utm_term     = models.CharField(max_length=255, blank=True)

    # ── Cihaz & teknik bilgi ──
    ip_hash        = models.CharField(max_length=64, blank=True)   # SHA256 - GDPR
    ip_country     = models.CharField(max_length=5, blank=True)    # TR, DE, NL...
    ip_city        = models.CharField(max_length=100, blank=True)
    # ipinfo.io zenginleştirmesi (IPINFO_TOKEN .env) — iletişim tıklamalarında "nereden" bilgisi
    ip_address     = models.GenericIPAddressField(null=True, blank=True)
    ip_region      = models.CharField(max_length=100, blank=True)
    ip_postal      = models.CharField(max_length=20, blank=True)
    ip_org         = models.CharField(max_length=200, blank=True, help_text="İnternet sağlayıcısı / kurum (ASN)")
    ip_timezone    = models.CharField(max_length=50, blank=True)
    ip_loc         = models.CharField(max_length=40, blank=True, help_text="enlem,boylam (yaklaşık)")
    geo_source     = models.CharField(max_length=20, blank=True)
    user_agent     = models.TextField(blank=True)
    device_type    = models.CharField(max_length=20, blank=True)   # desktop/mobile/tablet
    device_brand   = models.CharField(max_length=50, blank=True)   # Apple, Samsung...
    device_model   = models.CharField(max_length=50, blank=True)   # iPhone 15, Galaxy S24...
    os_name        = models.CharField(max_length=30, blank=True)   # iOS, Android, Windows
    os_version     = models.CharField(max_length=20, blank=True)
    browser_name   = models.CharField(max_length=30, blank=True)
    browser_version = models.CharField(max_length=20, blank=True)
    screen_width   = models.PositiveSmallIntegerField(null=True, blank=True)
    screen_height  = models.PositiveSmallIntegerField(null=True, blank=True)
    language_code  = models.CharField(max_length=10, blank=True)
    timezone_name  = models.CharField(max_length=50, blank=True)

    # ── Davranış metrikleri ──
    page_views          = models.PositiveIntegerField(default=0)
    total_time_sec      = models.PositiveIntegerField(default=0)
    avg_scroll_depth    = models.FloatField(default=0.0)
    session_count       = models.PositiveIntegerField(default=1)  # kaç kez döndü

    # ── Conversion sinyalleri ──
    whatsapp_clicks     = models.PositiveIntegerField(default=0)
    phone_clicks        = models.PositiveIntegerField(default=0)
    form_starts         = models.PositiveIntegerField(default=0)
    form_submits        = models.PositiveIntegerField(default=0)
    cta_clicks          = models.PositiveIntegerField(default=0)
    video_plays         = models.PositiveIntegerField(default=0)
    map_clicks          = models.PositiveIntegerField(default=0)

    # ── WhatsApp eşleştirme ──
    # Kullanıcı WA butonuna bastıktan sonra WA'dan mesaj atarsa eşleştirme
    whatsapp_clicked_at  = models.DateTimeField(null=True, blank=True)
    whatsapp_matched     = models.BooleanField(default=False)
    whatsapp_match_phone = models.CharField(max_length=30, blank=True)
    whatsapp_match_time  = models.DateTimeField(null=True, blank=True)

    # ── Persona ──
    assigned_persona   = models.CharField(max_length=30, blank=True)
    persona_confidence = models.FloatField(default=0.0)

    # ── Conversion durumu ──
    is_lead       = models.BooleanField(default=False)  # Form doldurdu / WA yazdı
    is_converted  = models.BooleanField(default=False)  # Hasta oldu
    is_qualified  = models.BooleanField(default=False)  # Uygun hasta
    lead_at       = models.DateTimeField(null=True, blank=True)
    converted_at  = models.DateTimeField(null=True, blank=True)

    # ── Notlar ──
    notes = models.TextField(blank=True)  # Admin manuel not

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["gclid"]),
            models.Index(fields=["fbclid"]),
            models.Index(fields=["traffic_source"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["ip_country"]),
            models.Index(fields=["is_lead"]),
            models.Index(fields=["whatsapp_clicked_at"]),
        ]

    def __str__(self):
        src = self.traffic_source
        country = f" [{self.ip_country}]" if self.ip_country else ""
        return f"{self.session_key[:12]}... | {src}{country} | {self.created_at.strftime('%d.%m %H:%M')}"

    @property
    def has_paid_source(self):
        return self.gclid or self.fbclid

    @property
    def conversion_intent_score(self):
        """0-100 arası intent skoru — admin'de gösterilir."""
        score = 0
        score += min(self.whatsapp_clicks * 25, 50)
        score += min(self.phone_clicks * 20, 40)
        score += min(self.form_submits * 30, 60)
        score += min(self.cta_clicks * 5, 20)
        score += min(self.video_plays * 5, 10)
        if self.total_time_sec > 120: score += 10
        if self.avg_scroll_depth > 70: score += 10
        if self.session_count > 1: score += 10
        return min(score, 100)

    def mark_lead(self):
        if not self.is_lead:
            self.is_lead = True
            self.lead_at = timezone.now()
            self.save(update_fields=["is_lead", "lead_at"])

    def mark_converted(self):
        self.is_converted = True
        self.converted_at = timezone.now()
        self.save(update_fields=["is_converted", "converted_at"])


# ── PageView ──────────────────────────────────────────────────────────────────

class PageView(models.Model):
    """Her sayfa görüntülemesi."""
    session    = models.ForeignKey(VisitorSession, on_delete=models.CASCADE, related_name="pageviews")
    url        = models.CharField(max_length=500)
    title      = models.CharField(max_length=300, blank=True)
    referrer   = models.CharField(max_length=500, blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)
    time_on_page_sec = models.PositiveIntegerField(default=0)
    scroll_depth     = models.FloatField(default=0.0)
    is_exit          = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["session", "timestamp"])]

    def __str__(self):
        return f"{self.url} @ {self.timestamp.strftime('%H:%M:%S')}"


# ── TrackingEvent ─────────────────────────────────────────────────────────────

class TrackingEvent(models.Model):
    """
    Kullanıcının yaptığı her eylem.
    Frontend JS → /api/tracking/event/ → buraya yazılır.
    """
    # Event tipleri
    WHATSAPP_CLICK   = "whatsapp_click"
    PHONE_CLICK      = "phone_click"
    MAPS_CLICK       = "maps_click"
    CTA_CLICK        = "cta_click"
    FORM_START       = "form_start"
    FORM_SUBMIT      = "form_submit"
    VIDEO_PLAY       = "video_play"
    VIDEO_PROGRESS   = "video_progress"
    SCROLL_DEPTH     = "scroll_depth"
    TIME_ON_PAGE     = "time_on_page"
    SECTION_VIEW     = "section_view"
    INSTAGRAM_CLICK  = "instagram_click"
    YOUTUBE_CLICK    = "youtube_click"
    BEFORE_AFTER     = "before_after_interact"
    CHATBOT_OPEN     = "chatbot_open"
    CHATBOT_MSG      = "chatbot_message"
    LANG_SWITCH      = "language_switch"
    REVIEW_READ      = "review_read"

    EVENT_CHOICES = [
        (WHATSAPP_CLICK,  "WhatsApp Click"),
        (PHONE_CLICK,     "Phone Click"),
        (MAPS_CLICK,      "Maps Click"),
        (CTA_CLICK,       "CTA Click"),
        (FORM_START,      "Form Start"),
        (FORM_SUBMIT,     "Form Submit"),
        (VIDEO_PLAY,      "Video Play"),
        (VIDEO_PROGRESS,  "Video Progress"),
        (SCROLL_DEPTH,    "Scroll Depth"),
        (TIME_ON_PAGE,    "Time on Page"),
        (SECTION_VIEW,    "Section View"),
        (INSTAGRAM_CLICK, "Instagram Click"),
        (YOUTUBE_CLICK,   "YouTube Click"),
        (BEFORE_AFTER,    "Before/After Interact"),
        (CHATBOT_OPEN,    "Chatbot Open"),
        (CHATBOT_MSG,     "Chatbot Message"),
        (LANG_SWITCH,     "Language Switch"),
        (REVIEW_READ,     "Review Read"),
    ]

    session    = models.ForeignKey(VisitorSession, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    timestamp  = models.DateTimeField(auto_now_add=True)
    page_url   = models.CharField(max_length=500, blank=True)
    data       = models.JSONField(default=dict)
    # Tıklama anının bağlamı (iletişim tıklamaları için): hangi buton, sayfanın neresi, o anki persona / aşama / dil
    label      = models.CharField(max_length=120, blank=True, help_text="Buton metni")
    position   = models.CharField(max_length=60, blank=True, help_text="navbar / hero / footer / stage-dock / wa-float…")
    persona    = models.CharField(max_length=20, blank=True)
    stage      = models.CharField(max_length=20, blank=True)
    language   = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["session", "event_type"]),
            models.Index(fields=["event_type", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.event_type} | {self.timestamp.strftime('%H:%M:%S')}"


CONTACT_EVENTS = (TrackingEvent.PHONE_CLICK, TrackingEvent.WHATSAPP_CLICK, TrackingEvent.FORM_SUBMIT)


class ContactClickManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(event_type__in=CONTACT_EVENTS).select_related("session")


class ContactClick(TrackingEvent):
    """Admin görünümü: telefon / WhatsApp / form — kim, ne zaman, hangi cihazla, nereden."""
    objects = ContactClickManager()

    class Meta:
        proxy = True
        ordering = ["-timestamp"]
        verbose_name = "İletişim tıklaması"
        verbose_name_plural = "📞 İletişim tıklamaları (telefon / WhatsApp / form)"


# ── Lead ──────────────────────────────────────────────────────────────────────

class Lead(models.Model):
    """
    Form dolduran, WA yazan veya telefon eden her potansiyel hasta.
    """
    SOURCE_FORM      = "form"
    SOURCE_WHATSAPP  = "whatsapp"
    SOURCE_PHONE     = "phone"
    SOURCE_CHATBOT   = "chatbot"
    SOURCE_CHOICES   = [
        (SOURCE_FORM,     "Contact Form"),
        (SOURCE_WHATSAPP, "WhatsApp"),
        (SOURCE_PHONE,    "Phone Call"),
        (SOURCE_CHATBOT,  "AI Chatbot"),
    ]

    STATUS_NEW       = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_QUALIFIED = "qualified"
    STATUS_BOOKED    = "booked"
    STATUS_TREATED   = "treated"
    STATUS_LOST      = "lost"
    STATUS_CHOICES   = [
        (STATUS_NEW,       "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_QUALIFIED, "Qualified"),
        (STATUS_BOOKED,    "Appointment Booked"),
        (STATUS_TREATED,   "Treated / Converted"),
        (STATUS_LOST,      "Lost"),
    ]

    session      = models.ForeignKey(VisitorSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    clinic       = models.ForeignKey("clinics.Clinic", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="leads", help_text="Lead'in yönlendirildiği klinik")
    treatment    = models.ForeignKey("treatments.Treatment", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="leads")
    persona      = models.CharField(max_length=20, blank=True)
    source       = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    # İletişim bilgileri
    name         = models.CharField(max_length=200, blank=True)
    phone        = models.CharField(max_length=30, blank=True)
    email        = models.EmailField(blank=True)
    message      = models.TextField(blank=True)

    # Sayfa bilgisi
    page         = models.CharField(max_length=500, blank=True)
    language     = models.CharField(max_length=10, blank=True)

    # Traffic source (session'dan kopyalanır — session silinse bile kalır)
    traffic_source = models.CharField(max_length=30, blank=True)
    gclid          = models.CharField(max_length=255, blank=True)
    fbclid         = models.CharField(max_length=255, blank=True)
    utm_campaign   = models.CharField(max_length=255, blank=True)
    utm_source     = models.CharField(max_length=255, blank=True)

    # Cihaz (session'dan kopyalanır)
    device_type    = models.CharField(max_length=20, blank=True)
    ip_country     = models.CharField(max_length=5, blank=True)
    ip_city        = models.CharField(max_length=100, blank=True)

    # Zaman
    created_at     = models.DateTimeField(auto_now_add=True)
    contacted_at   = models.DateTimeField(null=True, blank=True)
    qualified_at   = models.DateTimeField(null=True, blank=True)
    booked_at      = models.DateTimeField(null=True, blank=True)
    treated_at     = models.DateTimeField(null=True, blank=True)

    # Conversion değeri
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency         = models.CharField(max_length=5, default="EUR")

    # WhatsApp eşleştirme
    whatsapp_matched = models.BooleanField(default=False)
    whatsapp_match_confidence = models.FloatField(default=0.0)  # 0-1

    # Admin notları
    notes          = models.TextField(blank=True)
    assigned_to    = models.CharField(max_length=100, blank=True)  # Hangi staff

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["source"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["gclid"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self):
        name = self.name or "Anonymous"
        return f"{name} | {self.source} | {self.status} | {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    def mark_qualified(self):
        self.status = self.STATUS_QUALIFIED
        self.qualified_at = timezone.now()
        self.save(update_fields=["status", "qualified_at"])
        if self.session:
            self.session.is_qualified = True
            self.session.save(update_fields=["is_qualified"])


# ── WhatsAppMatch ─────────────────────────────────────────────────────────────

class WhatsAppMatch(models.Model):
    """
    Kullanıcı WA butonuna bastıktan sonra WA'dan mesaj attığında
    session ile eşleştirme yapılır.

    Eşleştirme mantığı:
    - Kullanıcı WA butonuna bastı → whatsapp_clicked_at kayıt
    - Max 30 dakika içinde WA'dan mesaj geldi → eşleştir
    - Telefon numarası + zaman penceresi kullanılır
    """
    session         = models.ForeignKey(VisitorSession, on_delete=models.SET_NULL, null=True, blank=True)
    lead            = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)

    wa_phone        = models.CharField(max_length=30)      # WA'dan gelen numara
    wa_message      = models.TextField(blank=True)          # İlk mesaj
    wa_received_at  = models.DateTimeField()

    button_clicked_at = models.DateTimeField(null=True, blank=True)  # Session'daki click zamanı
    time_diff_seconds = models.IntegerField(null=True, blank=True)   # Fark (saniye)

    match_confidence = models.FloatField(default=0.0)  # 0-1
    is_manual        = models.BooleanField(default=False)  # Manuel eşleştirme mi?
    matched_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-wa_received_at"]

    def __str__(self):
        conf = f"{self.match_confidence:.0%}"
        return f"WA: {self.wa_phone} → Session: {self.session_id} [{conf}]"


# ── AdConversion ─────────────────────────────────────────────────────────────

class AdConversion(models.Model):
    """
    Google Ads veya Meta Ads'e gönderilecek conversion event.
    Lead qualified/converted olduğunda oluşturulur.
    """
    PLATFORM_GOOGLE = "google"
    PLATFORM_META   = "meta"
    PLATFORM_CHOICES = [
        (PLATFORM_GOOGLE, "Google Ads"),
        (PLATFORM_META,   "Meta Ads"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SENT    = "sent"
    STATUS_FAILED  = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT,    "Sent"),
        (STATUS_FAILED,  "Failed"),
    ]

    lead            = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="ad_conversions")
    platform        = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    conversion_name = models.CharField(max_length=100)  # "lead", "qualified_lead", "booking"
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency        = models.CharField(max_length=5, default="EUR")

    # Platform-specific IDs
    gclid           = models.CharField(max_length=255, blank=True)
    fbclid          = models.CharField(max_length=255, blank=True)
    event_id        = models.CharField(max_length=255, blank=True)  # Meta dedup

    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    sent_at         = models.DateTimeField(null=True, blank=True)
    error_message   = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.platform} | {self.conversion_name} | {self.status}"
