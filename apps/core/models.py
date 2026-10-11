from django.conf import settings
from django.core.cache import cache
from django.db import models

from apps.localization.models import BaseTranslation, TranslatableModel

SETTINGS_CACHE_KEY = "core:site_settings"


class SiteSettings(models.Model):
    """Admin'den düzenlenen site geneli ayarlar (tekil kayıt)."""

    logo = models.ImageField(upload_to="site/", blank=True, help_text="Header/footer logosu (SVG/PNG, yatay)")
    favicon = models.ImageField(upload_to="site/", blank=True, help_text="Kare PNG, en az 192×192")
    default_og_image = models.ImageField(upload_to="site/", blank=True,
                                         help_text="Sosyal medya paylaşım görseli — 1200×630 px")
    announcement = models.CharField(max_length=200, blank=True,
                                    help_text="Sitenin en üstünde gösterilecek kısa duyuru (boşsa gizli). "
                                              "Kaynak dil İngilizce; çeviri için UI metni olarak eklenmez.")
    announcement_url = models.CharField(max_length=300, blank=True)
    show_prices = models.BooleanField(default=True, help_text="Fiyatları sitede göster")
    maintenance_note = models.TextField(blank=True, help_text="İç not — sitede görünmez")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(SETTINGS_CACHE_KEY)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj = cache.get(SETTINGS_CACHE_KEY)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(SETTINGS_CACHE_KEY, obj, 300)
        return obj


class ContentBlock(TranslatableModel):
    """Sayfalardaki bölüm başlıkları / metinleri — admin'den düzenlenir, kaydedince 15 dile çevrilir.

    Şablonda: {% cblock "home-reviews" "title" _("Real patients, real results") %}
    Bir dilde çeviri henüz yoksa şablondaki (önceden çevrilmiş) varsayılan metin gösterilir.
    """
    TRANSLATED_FIELDS = ("eyebrow", "title", "subtitle", "body", "button_text", "items")

    PAGE_CHOICES = [("home", "Ana sayfa"), ("global", "Tüm site"), ("treatments", "Tedavi sayfaları"),
                    ("clinics", "Klinik sayfaları"), ("blog", "Blog"), ("contact", "İletişim")]

    key = models.SlugField(max_length=80, unique=True, help_text="Şablondaki anahtar — değiştirmeyin")
    page = models.CharField(max_length=20, choices=PAGE_CHOICES, default="home")
    label = models.CharField(max_length=150, help_text="Admin için açıklama: bu blok sayfada nerede?")
    eyebrow = models.CharField(max_length=150, blank=True, help_text="Başlığın üstündeki küçük etiket")
    title = models.CharField(max_length=250, blank=True)
    subtitle = models.TextField(blank=True)
    body = models.TextField(blank=True, help_text="Markdown")
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to="blocks/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text="Dosya yüklemek yerine görsel linki")
    items = models.JSONField(default=list, blank=True,
                             help_text='SSS vb. liste: [{"question": "...", "answer": "..."}]')
    is_active = models.BooleanField(default=True, help_text="Kapalıysa metinler şablondaki varsayılanı kullanır")
    visible = models.BooleanField(default=True, help_text="Bölümü sayfada göster / gizle (ana sayfa bölümleri)")
    order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["page", "order", "key"]
        verbose_name = "Content block (sayfa metni)"
        verbose_name_plural = "Content blocks (sayfa metinleri)"

    def __str__(self):
        return f"{self.get_page_display()} — {self.label}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete_many([f"cblock:{self.key}:{c}" for c, _ in settings.LANGUAGES])


class ContentBlockTranslation(BaseTranslation):
    block = models.ForeignKey(ContentBlock, on_delete=models.CASCADE, related_name="translations")
    eyebrow = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=250, blank=True)
    subtitle = models.TextField(blank=True)
    body = models.TextField(blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    items = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = [("block", "language_code")]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f"cblock:{self.block.key}:{self.language_code}")
