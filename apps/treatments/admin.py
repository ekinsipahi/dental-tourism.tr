from django.contrib import admin

from apps.core.admin import image_preview
from apps.localization.admin import TranslatableAdmin, TranslationInlineBase

from .models import MarketPrice, Treatment, TreatmentTranslation


class TreatmentTranslationInline(TranslationInlineBase):
    model = TreatmentTranslation
    fields = ["language_code", "status", "name", "slug", "short_description", "body", "faq", "meta_title",
              "meta_description", "focus_keyword", "translated_at", "model_used", "error"]


class MarketPriceInline(admin.TabularInline):
    model = MarketPrice
    extra = 0


@admin.register(Treatment)
class TreatmentAdmin(TranslatableAdmin):
    list_display = ["name", "key", "category", "typical_price_from", "is_active", "is_featured", "order",
                    "translation_badge"]
    list_editable = ["is_active", "is_featured", "order"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "key", "focus_keyword"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["translation_matrix", "image_preview"]
    image_preview = image_preview("image_src", 140)
    filter_horizontal = ["related"]
    inlines = [MarketPriceInline, TreatmentTranslationInline]
    fieldsets = [
        (None, {"fields": ["key", "category", "icon", ("image", "image_url", "image_preview"), "image_alt", "order", "is_active", "is_featured",
                           "related"]}),
        ("Tipik veriler", {"fields": ["typical_price_from", "typical_price_to", "price_unit", "stay_days", "visits",
                                      "procedure_duration", "anesthesia", "body_location"]}),
        ("İçerik (kaynak dil)", {"fields": ["source_language", "auto_translate", "name", "slug", "short_description",
                                            "body", "faq", "meta_title", "meta_description", "focus_keyword",
                                            "translation_matrix"]}),
    ]


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ["treatment", "country_code", "price_min", "price_max", "currency", "price_min_eur", "verified",
                    "updated_at"]
    list_filter = ["country_code", "verified", "treatment"]
    list_editable = ["verified"]
