from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.localization.models import BaseTranslation, TranslatableModel


class Treatment(TranslatableModel):
    """Bir tedavi türü (implant, veneer...). Her dilde ayrı slug + içerik."""

    TRANSLATED_FIELDS = ("name", "slug", "short_description", "body", "faq",
                         "meta_title", "meta_description", "focus_keyword",
                         "price_factors", "program", "refusals")

    CATEGORY_CHOICES = [
        ("implant", "Implantology"), ("cosmetic", "Cosmetic"), ("restorative", "Restorative"),
        ("general", "General dentistry"), ("surgery", "Oral surgery"), ("ortho", "Orthodontics"),
    ]

    key = models.SlugField(max_length=60, unique=True, help_text="Dilden bağımsız sabit anahtar: dental-implants")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="general")
    icon = models.CharField(max_length=8, default="🦷")
    image = models.ImageField(upload_to="treatments/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text="Dosya yüklemek yerine görsel linki")
    image_alt = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True, help_text="Ana sayfada göster")

    # Tipik veriler (klinik fiyatı yoksa yedek olarak kullanılır)
    typical_price_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    typical_price_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(max_length=30, default="per tooth")
    stay_days = models.CharField(max_length=20, blank=True, help_text="İstanbul'da kalış, ör. '5-7'")
    visits = models.PositiveSmallIntegerField(null=True, blank=True)
    procedure_duration = models.CharField(max_length=50, blank=True, help_text="ör. '1-2 hours per implant'")
    anesthesia = models.CharField(max_length=50, blank=True, default="Local")
    body_location = models.CharField(max_length=50, default="Mouth")
    related = models.ManyToManyField("self", blank=True)

    # Kaynak dil içerik
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150)
    short_description = models.TextField(max_length=400, blank=True)
    body = models.TextField(blank=True, help_text="Markdown. H1 kullanmayın, H2'den başlayın.")
    faq = models.JSONField(default=list, blank=True, help_text='[{"question": "...", "answer": "..."}]')
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    focus_keyword = models.CharField(max_length=120, blank=True)
    # Hekimin notları (birinci ağızdan, düz metin; boş satırla paragraf) — şablon-dışı, sayfaya özgü içerik:
    price_factors = models.TextField(blank=True, help_text="Fiyat sayfası: fiyatı asıl belirleyen etkenler, hangi muayene bulgusu teklifi değiştirir")
    program = models.TextField(blank=True, help_text="Paket sayfası: yurt dışından gelen hasta için gün gün program, iki geliş arasında ne olur")
    refusals = models.TextField(blank=True, help_text="Tedavi sayfası: bu tedaviyi hangi hastaya yapmıyoruz, ne öneriyoruz")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.key:
            self.key = self.slug
        super().save(*args, **kwargs)

    @property
    def image_src(self):
        return self.image.url if self.image else self.image_url

    def get_absolute_url(self):
        return reverse("treatments:detail", kwargs={"slug": self.localized().slug})

    def price_range(self):
        """Yayındaki klinik tekliflerinden min-max fiyat; yoksa tipik fiyat."""
        agg = self.clinic_offers.filter(is_active=True, clinic__status="approved").aggregate(
            lo=models.Min("price_from"), hi=models.Max("price_to"))
        lo = agg["lo"] or self.typical_price_from
        hi = agg["hi"] or self.typical_price_to
        return lo, hi


class TreatmentTranslation(BaseTranslation):
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name="translations")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150)
    short_description = models.TextField(blank=True)
    body = models.TextField(blank=True)
    faq = models.JSONField(default=list, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    focus_keyword = models.CharField(max_length=120, blank=True)
    price_factors = models.TextField(blank=True)
    program = models.TextField(blank=True)
    refusals = models.TextField(blank=True)

    class Meta:
        unique_together = [("treatment", "language_code"), ("language_code", "slug")]

    def __str__(self):
        return f"{self.name} [{self.language_code}]"


class MarketPrice(models.Model):
    """Hastanın kendi ülkesindeki ortalama fiyat — programatik fiyat karşılaştırma sayfaları için.

    ÖNEMLİ: Kaynağı belli, güncel değerler girin (ör. ulusal diş hekimleri birliği
    tarifeleri, karşılaştırma siteleri). 'source' ve 'verified' alanlarını doldurun.
    """
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name="market_prices")
    country_code = models.CharField(max_length=2)
    currency = models.CharField(max_length=3)
    price_min = models.DecimalField(max_digits=10, decimal_places=2)
    price_max = models.DecimalField(max_digits=10, decimal_places=2)
    price_min_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_max_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    source = models.CharField(max_length=300, blank=True)
    verified = models.BooleanField(default=False, help_text="Kaynak kontrol edildi.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("treatment", "country_code")]
        ordering = ["treatment", "country_code"]

    def __str__(self):
        return f"{self.treatment} — {self.country_code}: {self.price_min}-{self.price_max} {self.currency}"
