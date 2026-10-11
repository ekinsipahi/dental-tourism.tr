"""
SEO — anahtar kelimeler ve programatik sayfalar.

Keyword       : Her dil için hedef anahtar kelime havuzu (seed / AI / CSV import / GSC).
                Her kelime bir hedef sayfaya (tedavi, şehir sayfası, fiyat sayfası, blog yazısı) atanır.
LandingPage   : Veri × dil kombinasyonlarından üretilen sayfalar:
                  - treatment_city  → /de/behandlungen/zahnimplantate/istanbul/
                  - treatment_price → /de/preise/zahnimplantate/
                Kaynak içerik AI ile üretilir, diğer dillere otomatik lokalize edilir.
"""
from django.conf import settings
from django.db import models

from apps.localization.models import BaseTranslation, TranslatableModel

INTENT_CHOICES = [
    ("informational", "Informational"),
    ("commercial", "Commercial investigation"),
    ("transactional", "Transactional"),
    ("navigational", "Navigational"),
]
FUNNEL_CHOICES = [("awareness", "Awareness"), ("consideration", "Consideration"), ("decision", "Decision")]


class Keyword(models.Model):
    STATUS_CHOICES = [
        ("new", "New"), ("planned", "Planned"), ("targeted", "Targeted (page exists)"),
        ("ranking", "Ranking"), ("ignored", "Ignored"),
    ]
    SOURCE_CHOICES = [("seed", "Seed matrix"), ("ai", "AI expansion"), ("import", "CSV import"),
                      ("gsc", "Search Console"), ("manual", "Manual")]
    PAGE_TYPE_CHOICES = [("treatment", "Treatment page"), ("treatment_city", "Treatment × city"),
                         ("treatment_price", "Cost page (no amounts)"), ("package", "Package page"),
                         ("guide", "Guide / topic page"), ("clinic", "Clinic"),
                         ("blog", "Blog post"), ("home", "Home")]

    term = models.CharField(max_length=200)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, db_index=True)
    country_code = models.CharField(max_length=2, blank=True, help_text="Hedef pazar (boş = dilin tümü)")
    treatment = models.ForeignKey("treatments.Treatment", null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="keywords")
    city = models.ForeignKey("clinics.City", null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="keywords")
    intent = models.CharField(max_length=20, choices=INTENT_CHOICES, default="commercial")
    funnel_stage = models.CharField(max_length=20, choices=FUNNEL_CHOICES, default="consideration")
    persona_hint = models.CharField(max_length=20, blank=True,
                                    help_text="Bu aramayı yapan muhtemel persona (price, fear, ...)")
    page_type = models.CharField(max_length=20, choices=PAGE_TYPE_CHOICES, default="treatment")

    search_volume = models.PositiveIntegerField(null=True, blank=True)
    difficulty = models.PositiveSmallIntegerField(null=True, blank=True, help_text="0-100")
    cpc = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    current_position = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    clicks_28d = models.PositiveIntegerField(null=True, blank=True)
    impressions_28d = models.PositiveIntegerField(null=True, blank=True)

    priority = models.PositiveSmallIntegerField(default=50, help_text="0-100, yüksek = önce")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="new", db_index=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="seed")
    is_primary = models.BooleanField(default=False, help_text="Hedef sayfanın ana anahtar kelimesi")
    target_url = models.CharField(max_length=500, blank=True)
    blog_post = models.ForeignKey("blog.BlogPost", null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="keywords")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("term", "language")]
        ordering = ["-priority", "-search_volume", "term"]
        indexes = [models.Index(fields=["language", "status"]), models.Index(fields=["treatment", "language"])]

    def __str__(self):
        return f"[{self.language}] {self.term}"

    @property
    def opportunity_score(self):
        """Basit fırsat skoru: hacim yüksek, zorluk düşük, pozisyon 4-20 arası → yüksek."""
        vol = self.search_volume or 0
        kd = self.difficulty if self.difficulty is not None else 50
        score = vol * (100 - kd) / 100
        if self.current_position and 4 <= float(self.current_position) <= 20:
            score *= 1.5
        return round(score)


class LandingPage(TranslatableModel):
    TRANSLATED_FIELDS = ("h1", "intro", "body", "faq", "meta_title", "meta_description", "focus_keyword")

    TYPE_TREATMENT_CITY = "treatment_city"
    TYPE_TREATMENT_PRICE = "treatment_price"
    TYPE_CHOICES = [(TYPE_TREATMENT_CITY, "Treatment in city"), (TYPE_TREATMENT_PRICE, "Treatment cost comparison")]

    page_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    treatment = models.ForeignKey("treatments.Treatment", on_delete=models.CASCADE, related_name="landing_pages")
    city = models.ForeignKey("clinics.City", null=True, blank=True, on_delete=models.CASCADE,
                             related_name="landing_pages")
    is_active = models.BooleanField(default=True)
    noindex = models.BooleanField(default=False)

    h1 = models.CharField(max_length=200)
    intro = models.TextField(blank=True, help_text="Markdown — ilk paragraf, anahtar kelimeyi içermeli")
    body = models.TextField(blank=True, help_text="Markdown — H2'den başlayın")
    faq = models.JSONField(default=list, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    focus_keyword = models.CharField(max_length=120, blank=True)

    generated_by_ai = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("page_type", "treatment", "city")]
        ordering = ["page_type", "treatment__order"]

    def __str__(self):
        city = f" — {self.city}" if self.city else ""
        return f"{self.get_page_type_display()}: {self.treatment}{city}"


class LandingPageTranslation(BaseTranslation):
    page = models.ForeignKey(LandingPage, on_delete=models.CASCADE, related_name="translations")
    h1 = models.CharField(max_length=200)
    intro = models.TextField(blank=True)
    body = models.TextField(blank=True)
    faq = models.JSONField(default=list, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    focus_keyword = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = [("page", "language_code")]


class Redirect(models.Model):
    """Eski URL → yeni URL (301). Slug değişince otomatik oluşturulabilir."""
    old_path = models.CharField(max_length=500, unique=True)
    new_path = models.CharField(max_length=500)
    permanent = models.BooleanField(default=True)
    hits = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.old_path} → {self.new_path}"


class SeoTopic(TranslatableModel):
    """
    Programatik SEO konu sayfası — /guide/<slug>/ (16 dilde, dile özel slug).
    Kaynak: apps/seo/topics.py (+ apps/seo/topic_content/<dil>.json), `python manage.py seed_topics` ile yüklenir;
    sonrasında her şey admin'den düzenlenebilir. FİYAT RAKAMI YAZILMAZ.
    """
    TRANSLATED_FIELDS = ("slug", "h1", "lead", "body", "faq", "meta_title", "meta_description")

    KIND_CHOICES = [("pillar", "Pillar / genel"), ("general", "Genel"), ("location", "Lokasyon"),
                    ("trust", "Güven / yorumlar"), ("guide", "Rehber"), ("service", "Hizmet"),
                    ("gallery", "Önce-sonra galerisi"), ("compare", "Ülke karşılaştırma"), ("b2b", "Ajans / B2B")]

    key = models.SlugField(max_length=80, unique=True, help_text="Sabit iç anahtar (topics.py ile eşleşir)")
    group = models.CharField(max_length=20, blank=True, help_text="Keyword grubu (G1, G5 …)")
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default="general")
    is_active = models.BooleanField(default=True)
    noindex = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=50)
    image = models.ForeignKey("clinics.ClinicImage", null=True, blank=True, on_delete=models.SET_NULL,
                              related_name="+", help_text="Kapak görseli (gerçek klinik fotoğrafı). Boşsa galeriden seçilir.")
    show_cases = models.BooleanField(default=False, help_text="Önce-sonra vakalarını göster")
    keywords = models.TextField(blank=True, help_text="Hedef keyword'ler (dil: keyword, satır başına) — dokümantasyon")

    slug = models.SlugField(max_length=150)
    h1 = models.CharField(max_length=200)
    lead = models.TextField(blank=True)
    body = models.TextField(blank=True, help_text="Markdown — ## ile başlayan bölümler")
    faq = models.JSONField(default=list, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "key"]
        verbose_name = "SEO konu sayfası"
        verbose_name_plural = "SEO konu sayfaları"

    def __str__(self):
        return f"{self.key} ({self.group})"

    def get_absolute_url(self, lang=None):
        from django.urls import reverse
        from django.utils import translation

        lang = lang or translation.get_language()
        with translation.override(lang):
            return reverse("guides:detail", kwargs={"slug": self.localized(lang).slug})


class SeoTopicTranslation(BaseTranslation):
    topic = models.ForeignKey(SeoTopic, on_delete=models.CASCADE, related_name="translations")
    slug = models.SlugField(max_length=150)
    h1 = models.CharField(max_length=200)
    lead = models.TextField(blank=True)
    body = models.TextField(blank=True)
    faq = models.JSONField(default=list, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)

    class Meta:
        unique_together = [("topic", "language_code"), ("language_code", "slug")]
