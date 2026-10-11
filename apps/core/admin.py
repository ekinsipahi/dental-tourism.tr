from django.contrib import admin
from django.utils.html import format_html

from apps.localization.admin import TranslatableAdmin, TranslationInlineBase

from .models import ContentBlock, ContentBlockTranslation, SiteSettings


def image_preview(field_name, size=120, label="Önizleme"):
    """ModelAdmin/Inline için görsel önizleme alanı üretir."""
    @admin.display(description=label)
    def _preview(self, obj):
        f = getattr(obj, field_name, None) if obj else None
        url = (f.url if hasattr(f, "url") else f) if f else ""
        if not url:
            return "—"
        return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height:{1}px;max-width:{2}px;'
                           'border-radius:8px;object-fit:cover;border:1px solid #ddd"></a>', url, size, size * 2)
    _preview.__name__ = f"{field_name}_preview"
    return _preview


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ["logo_preview", "favicon_preview", "default_og_image_preview", "updated_at"]
    fieldsets = [
        ("Marka", {"fields": [("logo", "logo_preview"), ("favicon", "favicon_preview"),
                              ("default_og_image", "default_og_image_preview")]}),
        ("Duyuru bandı", {"fields": ["announcement", "announcement_url"]}),
        ("Gösterim", {"fields": ["show_prices", "maintenance_note", "updated_at"]}),
    ]
    logo_preview = image_preview("logo", 60)
    favicon_preview = image_preview("favicon", 48)
    default_og_image_preview = image_preview("default_og_image", 120)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect

        obj = SiteSettings.load()
        return redirect("admin:core_sitesettings_change", obj.pk)


class ContentBlockTranslationInline(TranslationInlineBase):
    model = ContentBlockTranslation


@admin.register(ContentBlock)
class ContentBlockAdmin(TranslatableAdmin):
    list_display = ["label", "key", "page", "title_short", "visible", "order", "translation_badge"]
    list_editable = ["visible", "order"]
    list_filter = ["page", "visible"]
    search_fields = ["key", "label", "title", "subtitle", "body"]
    readonly_fields = ["translation_matrix", "image_preview"]
    image_preview = image_preview("image_url", 140)
    inlines = [ContentBlockTranslationInline]
    fieldsets = [
        (None, {"fields": ["label", "key", "page", "visible", "order", "is_active"],
                "description": "Sıra ve 'visible' ana sayfa bölümlerinin düzenini belirler. Metinleri değiştirip "
                               "kaydettiğinizde diğer 15 dile otomatik çevrilir. 'seo-*' bloklarında title = meta "
                               "title, subtitle = meta description."}),
        ("Metinler (kaynak dil)", {"fields": ["source_language", "auto_translate", "eyebrow", "title", "subtitle",
                                              "body", "button_text", "button_url", "items", "translation_matrix"]}),
        ("Görsel", {"fields": ["image", "image_url", "image_preview"]}),
    ]

    @admin.display(description="Başlık")
    def title_short(self, obj):
        return (obj.title or obj.subtitle or "—")[:70]
