"""
Klinik / Hekim / Şehir modelleri — çok klinikli (marketplace) yapıya hazır.

Başlangıçta tek klinik (Dr. Devrim Sipahi, is_primary=True) yayında.
İleride başka klinikler eklendiğinde:
  - Clinic.owner → klinik sahibinin kullanıcı hesabı (admin'de sadece kendi kliniğini görür)
  - Clinic.status → pending ile başvurur, admin 'approved' yapınca yayına girer
  - Lead'ler clinic FK ile ilgili kliniğe yönlendirilir
"""
from django.conf import settings
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.localization.models import BaseTranslation, TranslatableModel

PRIMARY_CLINIC_CACHE_KEY = "clinics:primary"


# ── City ──────────────────────────────────────────────────────────────────────
class City(TranslatableModel):
    TRANSLATED_FIELDS = ("name", "slug", "description")

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    country_code = models.CharField(max_length=2, default="TR")
    description = models.TextField(blank=True, help_text="Şehir sayfalarında kısa tanıtım (Markdown).")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    airport_code = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class CityTranslation(BaseTranslation):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="translations")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = [("city", "language_code"), ("language_code", "slug")]


# ── Clinic ────────────────────────────────────────────────────────────────────
class ClinicQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Clinic.STATUS_APPROVED)


class Clinic(TranslatableModel):
    TRANSLATED_FIELDS = ("tagline", "short_description", "description", "faq", "meta_title", "meta_description")

    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_SUSPENDED = "suspended"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PENDING, "Pending review"),
        (STATUS_APPROVED, "Approved / Live"),
        (STATUS_SUSPENDED, "Suspended"),
    ]

    # Yönetim
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                              related_name="clinics", help_text="Kliniği yöneten kullanıcı (klinik paneli).")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    is_primary = models.BooleanField(default=False, help_text="Sitenin ana kliniği (header/footer/WhatsApp).")
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False, help_text="Ruhsat/diploma doğrulandı.")
    order = models.PositiveIntegerField(default=0)

    # Kimlik
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    legal_name = models.CharField(max_length=250, blank=True)
    license_number = models.CharField(max_length=100, blank=True, help_text="Sağlık Bakanlığı ruhsat no.")
    logo = models.ImageField(upload_to="clinics/logos/", blank=True)
    cover_image = models.ImageField(upload_to="clinics/covers/", blank=True)
    logo_url = models.URLField(max_length=500, blank=True, help_text="Dosya yüklemek yerine görsel linki")
    cover_image_url = models.URLField(max_length=500, blank=True, help_text="Dosya yüklemek yerine görsel linki")

    # Kaynak dilde metinler
    tagline = models.CharField(max_length=200, blank=True)
    short_description = models.TextField(max_length=400, blank=True)
    description = models.TextField(blank=True, help_text="Markdown")
    faq = models.JSONField(default=list, blank=True, help_text='Klinik SSS: [{"question": "...", "answer": "..."}]')
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)

    # Konum
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="clinics")
    district = models.CharField(max_length=100, blank=True)
    neighborhood = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=300)
    postal_code = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    maps_url = models.URLField(blank=True)
    maps_embed_url = models.URLField(max_length=1000, blank=True)

    # İletişim
    phone = models.CharField(max_length=30)
    whatsapp = models.CharField(max_length=20, help_text="Sadece rakam, ülke koduyla: 905055771883")
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True, help_text="Kullanıcı adı (@ olmadan)")
    youtube_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    google_business_url = models.URLField(blank=True, help_text="Google Business Profile / Maps profil linki")
    google_review_url = models.URLField(blank=True,
                                        help_text="'Google'da yorum yaz' linki (g.page/r/.../review)")

    # Güven sinyalleri (gerçek, doğrulanabilir değerler girin)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    years_experience = models.PositiveIntegerField(null=True, blank=True, help_text="Baş hekimin meslek yılı")
    patients_treated = models.PositiveIntegerField(null=True, blank=True)
    countries_served = models.PositiveIntegerField(null=True, blank=True)
    google_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)])
    google_review_count = models.PositiveIntegerField(null=True, blank=True)
    google_place_id = models.CharField(max_length=200, blank=True)
    languages_spoken = models.JSONField(default=list, blank=True, help_text='["tr","en","de"]')
    accreditations = models.JSONField(default=list, blank=True,
                                      help_text='Sadece gerçek sertifikalar. ["ISO 9001", ...]')
    opening_hours = models.JSONField(default=list, blank=True,
                                     help_text='schema.org formatı: ["Mo-Fr 09:00-19:00", "Sa 10:00-16:00"]')
    price_range = models.CharField(max_length=10, default="€€")
    offers_airport_transfer = models.BooleanField(default=False)
    offers_hotel_booking = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ClinicQuerySet.as_manager()

    class Meta:
        ordering = ["-is_primary", "-is_featured", "order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.is_primary:
            Clinic.objects.exclude(pk=self.pk).filter(is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
        cache.delete(PRIMARY_CLINIC_CACHE_KEY)

    def get_absolute_url(self):
        return reverse("clinics:detail", kwargs={"slug": self.slug})

    @property
    def display_name(self):
        return self.short_name or self.name

    @property
    def logo_src(self):
        return self.logo.url if self.logo else self.logo_url

    @property
    def cover_src(self):
        return self.cover_image.url if self.cover_image else self.cover_image_url

    @property
    def display_image(self):
        """Kart/paylaşım görseli (URL): kapak, yoksa ilk galeri görseli."""
        if self.cover_src:
            return self.cover_src
        first = next(iter(self.images.all()), None)
        return first.src if first else ""

    @property
    def social_links(self):
        """Tüm profil linkleri (eski alanlar + ClinicLink kayıtları) — sayfada ikonlar ve schema sameAs için."""
        links = []
        legacy = [("website", self.website), ("google_business", self.google_business_url),
                  ("instagram", f"https://www.instagram.com/{self.instagram}/" if self.instagram else ""),
                  ("youtube", self.youtube_url), ("facebook", self.facebook_url)]
        seen = set()
        for platform, url in legacy:
            if url and url not in seen:
                links.append({"platform": platform, "url": url, "label": dict(ClinicLink.PLATFORM_CHOICES)[platform]})
                seen.add(url)
        for link in self.links.all():
            if link.url not in seen:
                links.append({"platform": link.platform, "url": link.url, "label": link.label or link.get_platform_display()})
                seen.add(link.url)
        return links

    def review_stats(self):
        """Sitenin kendi yorum sisteminden puan özeti (schema AggregateRating buradan)."""
        agg = self.reviews.filter(is_published=True, source=Review.SOURCE_SITE).aggregate(
            avg=models.Avg("rating"), n=models.Count("id"))
        return {"avg": round(agg["avg"], 1) if agg["avg"] else None, "count": agg["n"]}

    @property
    def gallery_preview(self):
        return list(self.images.all()[:4])

    @property
    def whatsapp_url(self):
        return f"https://wa.me/{self.whatsapp}"

    @property
    def phone_display(self):
        return self.phone

    @property
    def is_live(self):
        return self.status == self.STATUS_APPROVED

    @classmethod
    def primary(cls):
        """Sitenin ana kliniği (cache'li). Yoksa None."""
        clinic = cache.get(PRIMARY_CLINIC_CACHE_KEY)
        if clinic is None:
            qs = cls.objects.select_related("city")
            clinic = (
                (settings.PRIMARY_CLINIC_SLUG and qs.filter(slug=settings.PRIMARY_CLINIC_SLUG).first())
                or qs.filter(is_primary=True).first()
                or qs.published().first()
            )
            cache.set(PRIMARY_CLINIC_CACHE_KEY, clinic or False, 300)
        return clinic or None


class ClinicTranslation(BaseTranslation):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="translations")
    tagline = models.CharField(max_length=200, blank=True)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    faq = models.JSONField(default=list, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)

    class Meta:
        unique_together = [("clinic", "language_code")]


class ClinicLink(models.Model):
    """Klinik profil / sosyal medya linkleri — sınırsız eklenebilir."""
    PLATFORM_CHOICES = [
        ("website", "Website"), ("google_business", "Google Business Profile"), ("instagram", "Instagram"),
        ("facebook", "Facebook"), ("youtube", "YouTube"), ("tiktok", "TikTok"), ("linkedin", "LinkedIn"),
        ("x", "X / Twitter"), ("trustpilot", "Trustpilot"), ("whatclinic", "WhatClinic"),
        ("tripadvisor", "Tripadvisor"), ("doktortakvimi", "Doktortakvimi"), ("other", "Other"),
    ]
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="links")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    label = models.CharField(max_length=80, blank=True, help_text="Boşsa platform adı gösterilir")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "platform"]

    def __str__(self):
        return f"{self.get_platform_display()}: {self.url}"


class ClinicImage(models.Model):
    KIND_CHOICES = [
        ("interior", "Interior"), ("room", "Treatment room"), ("team", "Team"),
        ("equipment", "Equipment"), ("exterior", "Exterior"), ("other", "Other"),
    ]
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="clinics/gallery/%Y/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text="Dosya yüklemek yerine görsel linki")
    alt = models.CharField(max_length=200, help_text="SEO alt metni — ne gösterdiğini açıklayın")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="interior")
    show_in_hero = models.BooleanField(default=True, help_text="Ana sayfa / klinik sayfası slider'ında göster")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.alt

    @property
    def src(self):
        return self.image.url if self.image else self.image_url

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.image and not self.image_url:
            raise ValidationError("Görsel dosyası yükleyin veya görsel linki girin.")


class BeforeAfterCase(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="cases")
    doctor = models.ForeignKey("Doctor", null=True, blank=True, on_delete=models.SET_NULL)
    treatment = models.ForeignKey("treatments.Treatment", null=True, blank=True, on_delete=models.SET_NULL)
    before_image = models.ImageField(upload_to="clinics/cases/", blank=True)
    before_image_url = models.URLField(max_length=500, blank=True)
    after_image = models.ImageField(upload_to="clinics/cases/", blank=True)
    after_image_url = models.URLField(max_length=500, blank=True)
    key = models.SlugField(max_length=60, blank=True, db_index=True, help_text="Sabit kimlik (seed_media eşlemesi)")
    title = models.CharField(max_length=120, blank=True, help_text="Kısa başlık — ör. 'Doğal monolitik zirkonya'")
    caption = models.CharField(max_length=300, blank=True)
    translations = models.JSONField(default=dict, blank=True,
                                    help_text='Dil başına {"de": {"title": "…", "caption": "…"}} — boşsa EN/TR metni gösterilir')
    patient_consent = models.BooleanField(default=False, help_text="Hastanın yazılı onayı alındı.")
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    @property
    def before_src(self):
        return self.before_image.url if self.before_image else self.before_image_url

    @property
    def after_src(self):
        return self.after_image.url if self.after_image else self.after_image_url

    def text_in(self, lang):
        """(başlık, açıklama) — istenen dilde; yoksa İngilizce, o da yoksa ana alanlar."""
        t = (self.translations or {})
        loc = t.get(lang) or t.get((lang or "")[:2]) or t.get("en") or {}
        return loc.get("title") or self.title, loc.get("caption") or self.caption


# ── Doctor ──────────────────────────────────────────────────────────────
class Doctor(TranslatableModel):
    TRANSLATED_FIELDS = ("title_display", "bio", "meta_title", "meta_description")

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="doctors")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name="doctor_profile")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    honorific = models.CharField(max_length=30, default="Dr. Dt.", help_text="Dr. Dt. / Prof. Dr. / Dt.")
    title_display = models.CharField(max_length=150, blank=True, help_text="Ör: Dentist, Implantologist")
    specialties = models.JSONField(default=list, blank=True)
    photo = models.ImageField(upload_to="doctors/", blank=True)
    photo_url = models.URLField(max_length=500, blank=True, help_text="Dosya yüklemek yerine görsel linki")
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    university = models.CharField(max_length=200, blank=True)
    diploma_number = models.CharField(max_length=100, blank=True)
    memberships = models.JSONField(default=list, blank=True, help_text='["Türk Diş Hekimleri Birliği"]')
    languages_spoken = models.JSONField(default=list, blank=True)
    bio = models.TextField(blank=True, help_text="Markdown")
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    is_active = models.BooleanField(default=True)
    is_lead_doctor = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_lead_doctor", "order", "name"]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.honorific} {self.name}".strip()

    @property
    def photo_src(self):
        return self.photo.url if self.photo else self.photo_url

    @property
    def years_experience(self):
        from django.utils import timezone

        return timezone.now().year - self.graduation_year if self.graduation_year else None

    def get_absolute_url(self):
        return reverse("doctors:detail", kwargs={"slug": self.slug})


class DoctorTranslation(BaseTranslation):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="translations")
    title_display = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)

    class Meta:
        unique_together = [("doctor", "language_code")]


# ── Klinik × Tedavi fiyatları ─────────────────────────────────────────────────
class ClinicTreatment(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="treatment_offers")
    treatment = models.ForeignKey("treatments.Treatment", on_delete=models.CASCADE, related_name="clinic_offers")
    price_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="EUR")
    price_unit = models.CharField(max_length=30, default="per tooth",
                                  help_text="per tooth / per arch / per session / per jaw")
    stay_days = models.CharField(max_length=20, blank=True, help_text="İstanbul'da kalış süresi, ör. 5-7")
    visits = models.PositiveSmallIntegerField(null=True, blank=True)
    warranty_years = models.PositiveSmallIntegerField(null=True, blank=True)
    brands = models.CharField(max_length=200, blank=True, help_text="Ör: Straumann, Osstem, E.max")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("clinic", "treatment")]
        ordering = ["treatment__order"]

    def __str__(self):
        return f"{self.clinic} — {self.treatment}"


# ── Reviews ───────────────────────────────────────────────────────────────────
class Review(models.Model):
    SOURCE_SITE = "site"
    SOURCE_CHOICES = [(SOURCE_SITE, "dentaltourism.tr (kendi sistemimiz)"), ("google", "Google"),
                      ("trustpilot", "Trustpilot"), ("youtube", "YouTube video"), ("whatcl", "WhatClinic"),
                      ("facebook", "Facebook"), ("instagram", "Instagram"), ("manual", "Direct / Manual")]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="reviews")
    doctor = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviews")
    treatment = models.ForeignKey("treatments.Treatment", null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="reviews")
    author_name = models.CharField(max_length=100, help_text="Ad + soyad baş harfi: 'Ece Y.'")
    email = models.EmailField(blank=True, help_text="Sadece doğrulama için — sitede gösterilmez")
    country_code = models.CharField(max_length=2, blank=True)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, blank=True)
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=150, blank=True)
    text = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="google")
    source_url = models.URLField(blank=True, help_text="Yorumun orijinal linki (Google, Trustpilot...)")
    video_id = models.CharField(max_length=30, blank=True, help_text="YouTube video/shorts ID")
    review_date = models.DateField(null=True, blank=True)
    treatment_date = models.DateField(null=True, blank=True)
    is_verified_patient = models.BooleanField(default=False,
                                              help_text="Hasta kayıtlarıyla eşleşti (lead/randevu) — rozet gösterilir")
    lead = models.ForeignKey("tracking.Lead", null=True, blank=True, on_delete=models.SET_NULL, related_name="reviews")
    text_translations = models.JSONField(default=dict, blank=True,
                                         help_text='Yorum metninin çevirileri: {"en": "...", "de": "..."} — '
                                                   "sitede ziyaretçinin dilinde gösterilir (orijinal her zaman görülebilir)")
    reply = models.TextField(blank=True, help_text="Kliniğin herkese açık yanıtı")
    reply_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Ana sayfada göster")
    order = models.PositiveIntegerField(default=0)
    ip_hash = models.CharField(max_length=64, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["-is_featured", "order", "-review_date", "-created_at"]

    def __str__(self):
        return f"{self.author_name} ({self.rating}★, {self.get_source_display()}) — {self.clinic}"

    @property
    def flag(self):
        if len(self.country_code) != 2:
            return ""
        return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in self.country_code.upper())

    def text_in(self, lang):
        """(metin, çeviri_mi) — ziyaretçinin dilinde metin; yoksa orijinal."""
        if not lang or lang == self.language or not self.text:
            return self.text, False
        tr = (self.text_translations or {}).get(lang)
        return (tr, True) if tr else (self.text, False)

    @property
    def is_internal(self):
        return self.source == self.SOURCE_SITE
