"""
Blog — çok dilli.

Akış:
  1. Admin'de yazıyı herhangi bir dilde yazın (source_language).
  2. status=published yapıp kaydedin.
  3. Yazı arka planda diğer 15 dile AI ile LOKALİZE edilir (dile özel slug,
     meta title/description, focus keyword dahil).
  4. Kaynağı sonradan düzenlerseniz değişen diller yeniden çevrilir; insan
     onaylı (reviewed) çeviriler ezilmez, 'outdated' olarak işaretlenir.

URL: /<dil>/blog/<kategori-slug>/<yazi-slug>/  (her ikisi de o dile ait)
"""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language
from slugify import slugify

from apps.localization.models import BaseTranslation, TranslatableModel

FUNNEL_CHOICES = [
    ("awareness", "Awareness — Top of funnel"),
    ("consideration", "Consideration — Mid funnel"),
    ("decision", "Decision — Bottom of funnel"),
]


class BlogCategory(TranslatableModel):
    TRANSLATED_FIELDS = ("name", "slug", "description", "meta_title", "meta_description")

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    funnel_stage = models.CharField(max_length=20, choices=FUNNEL_CHOICES, default="awareness")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Blog categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self, lang=None):
        from django.utils import translation

        lang = lang or get_language()
        loc = self.localized(lang)
        with translation.override(lang):
            return reverse("blog:category", kwargs={"category_slug": loc.slug})


class BlogCategoryTranslation(BaseTranslation):
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name="translations")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120)
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)

    class Meta:
        unique_together = [("category", "language_code"), ("language_code", "slug")]


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return (super().get_queryset()
                .filter(status=BlogPost.STATUS_PUBLISHED, published_at__lte=timezone.now())
                .select_related("category", "author", "treatment"))


class BlogPost(TranslatableModel):
    TRANSLATED_FIELDS = ("title", "slug", "excerpt", "content", "faq", "featured_image_alt",
                         "meta_title", "meta_description", "focus_keyword")

    STATUS_DRAFT = "draft"
    STATUS_REVIEW = "review"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [(STATUS_DRAFT, "Draft"), (STATUS_REVIEW, "In review"), (STATUS_PUBLISHED, "Published")]
    SOURCE_MANUAL = "manual"
    SOURCE_AI = "ai_generated"
    SOURCE_CHOICES = [(SOURCE_MANUAL, "Manual"), (SOURCE_AI, "AI generated")]
    SCHEMA_CHOICES = [("BlogPosting", "Blog posting"), ("Article", "Article"),
                      ("MedicalWebPage", "Medical web page"), ("HowTo", "How-to")]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.PROTECT, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_by = models.ForeignKey("clinics.Doctor", null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="reviewed_posts",
                                    help_text="Tıbbi içerik onayı (E-E-A-T): içeriği kontrol eden hekim")
    clinic = models.ForeignKey("clinics.Clinic", null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="posts", help_text="Boşsa site geneli yazı")
    treatment = models.ForeignKey("treatments.Treatment", null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="posts", help_text="İç linkleme: ilgili tedavi sayfası")

    excerpt = models.TextField(max_length=300, blank=True)
    content = models.TextField(help_text="Markdown. H1 kullanmayın (başlık zaten H1), ## ile başlayın.")
    faq = models.JSONField(default=list, blank=True, help_text='FAQPage schema: [{"question":..., "answer":...}]')
    featured_image = models.ImageField(upload_to="blog/images/%Y/%m/", blank=True)
    featured_image_url = models.URLField(max_length=500, blank=True, help_text="Dosya yüklemek yerine görsel linki")
    featured_image_alt = models.CharField(max_length=200, blank=True)

    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    focus_keyword = models.CharField(max_length=120, blank=True)
    canonical_url = models.URLField(blank=True, help_text="Sadece içerik başka sitede de varsa doldurun.")
    noindex = models.BooleanField(default=False)
    schema_type = models.CharField(max_length=30, choices=SCHEMA_CHOICES, default="BlogPosting")

    funnel_stage = models.CharField(max_length=20, choices=FUNNEL_CHOICES, default="awareness")
    target_personas = models.JSONField(default=list, blank=True)
    content_source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    ai_generation_prompt = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [models.Index(fields=["status", "published_at"]), models.Index(fields=["category", "status"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, max_length=180)
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED and self.published_at and self.published_at <= timezone.now()

    def get_absolute_url(self, lang=None):
        from django.utils import translation

        lang = lang or get_language()
        loc = self.localized(lang)
        cat = self.category.localized(lang if not loc.is_fallback else self.source_language)
        with translation.override(loc.lang):
            return reverse("blog:post_detail", kwargs={"category_slug": cat.slug, "post_slug": loc.slug})

    @property
    def image_src(self):
        return self.featured_image.url if self.featured_image else self.featured_image_url

    @staticmethod
    def reading_time_for(text):
        return max(1, round(len((text or "").split()) / 220))

    @property
    def reading_time(self):
        return self.reading_time_for(self.content)


class BlogPostTranslation(BaseTranslation):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="translations")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    faq = models.JSONField(default=list, blank=True)
    featured_image_alt = models.CharField(max_length=200, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    focus_keyword = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = [("post", "language_code"), ("language_code", "slug")]

    def __str__(self):
        return f"{self.post.title} [{self.language_code}]"

    @property
    def reading_time(self):
        return BlogPost.reading_time_for(self.content)


class RelatedPost(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="related_posts")
    related_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="related_to")
    score = models.FloatField(default=0.0)
    is_manual = models.BooleanField(default=False)

    class Meta:
        unique_together = [["post", "related_post"]]
        ordering = ["-score"]
