from django.contrib import admin, messages
from django.utils.html import format_html

from apps.localization.admin import TranslatableAdmin, TranslationInlineBase

from .models import Keyword, LandingPage, LandingPageTranslation, Redirect, SeoTopic, SeoTopicTranslation


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ["term", "language", "treatment", "city", "intent", "persona_hint", "page_type",
                    "search_volume", "difficulty", "current_position", "opportunity", "status", "priority"]
    list_filter = ["language", "status", "intent", "page_type", "source", "treatment", "persona_hint"]
    list_editable = ["status", "priority"]
    search_fields = ["term", "notes"]
    autocomplete_fields = ["blog_post"]
    actions = ["action_generate_posts"]
    list_per_page = 100

    @admin.display(description="Fırsat", ordering="search_volume")
    def opportunity(self, obj):
        return obj.opportunity_score

    @admin.action(description="✍️ Seçili kelimelerden blog taslağı üret (AI)")
    def action_generate_posts(self, request, queryset):
        from apps.blog.content_machine import ContentMachine
        from apps.localization.dispatch import run_in_background
        from apps.localization.llm import is_configured

        if not is_configured():
            self.message_user(request, "ANTHROPIC_API_KEY tanımlı değil (.env).", messages.ERROR)
            return
        ids = list(queryset.filter(blog_post__isnull=True).values_list("pk", flat=True)[:20])

        def _job():
            machine = ContentMachine()
            for kw in Keyword.objects.filter(pk__in=ids):
                machine.generate_post_from_keyword(kw)

        run_in_background(_job)
        self.message_user(request, f"{len(ids)} taslak arka planda üretiliyor (status=review).", messages.SUCCESS)


class LandingPageTranslationInline(TranslationInlineBase):
    model = LandingPageTranslation


@admin.register(LandingPage)
class LandingPageAdmin(TranslatableAdmin):
    list_display = ["__str__", "page_type", "treatment", "city", "is_active", "noindex", "generated_by_ai",
                    "translation_badge", "view_link"]
    list_filter = ["page_type", "is_active", "treatment", "city"]
    readonly_fields = ["translation_matrix"]
    inlines = [LandingPageTranslationInline]

    @admin.display(description="")
    def view_link(self, obj):
        t = obj.treatment.localized(obj.source_language)
        from django.urls import reverse
        from django.utils import translation

        with translation.override(obj.source_language):
            if obj.page_type == "treatment_city" and obj.city:
                url = reverse("treatments:city", kwargs={"slug": t.slug, "city_slug": obj.city.localized().slug})
            else:
                url = reverse("prices:detail", kwargs={"slug": t.slug})
        return format_html('<a href="{}" target="_blank">↗</a>', url)


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ["old_path", "new_path", "permanent", "hits", "created_at"]
    search_fields = ["old_path", "new_path"]


class SeoTopicTranslationInline(TranslationInlineBase):
    model = SeoTopicTranslation


@admin.register(SeoTopic)
class SeoTopicAdmin(TranslatableAdmin):
    list_display = ["key", "group", "kind", "h1", "is_active", "noindex", "order", "translation_badge", "view_link"]
    list_filter = ["group", "kind", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["key", "h1", "keywords"]
    readonly_fields = ["translation_matrix"]
    autocomplete_fields = []
    raw_id_fields = ["image"]
    inlines = [SeoTopicTranslationInline]
    fieldsets = [
        (None, {"fields": ["key", "group", "kind", "is_active", "noindex", "order", "image", "show_cases"]}),
        ("İçerik (kaynak dil) — fiyat rakamı yazmayın", {"fields": ["source_language", "auto_translate", "slug", "h1",
                                                                  "lead", "body", "faq"]}),
        ("SEO", {"fields": ["meta_title", "meta_description", "keywords"]}),
        ("Çeviriler", {"fields": ["translation_matrix"]}),
    ]

    @admin.display(description="")
    def view_link(self, obj):
        return format_html('<a href="{}" target="_blank">↗</a>', obj.get_absolute_url(obj.source_language))
