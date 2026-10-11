from django.contrib import admin, messages

from django.utils.html import format_html

from apps.core.admin import image_preview
from apps.localization.admin import TranslatableAdmin, TranslationInlineBase

from .models import BlogCategory, BlogCategoryTranslation, BlogPost, BlogPostTranslation, RelatedPost


class BlogCategoryTranslationInline(TranslationInlineBase):
    model = BlogCategoryTranslation


@admin.register(BlogCategory)
class BlogCategoryAdmin(TranslatableAdmin):
    list_display = ["name", "funnel_stage", "order", "translation_badge"]
    list_editable = ["funnel_stage", "order"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["translation_matrix"]
    inlines = [BlogCategoryTranslationInline]


class BlogPostTranslationInline(TranslationInlineBase):
    model = BlogPostTranslation
    fields = ["language_code", "status", "title", "slug", "excerpt", "content", "faq", "featured_image_alt",
              "meta_title", "meta_description", "focus_keyword", "translated_at", "model_used", "error"]


@admin.register(BlogPost)
class BlogPostAdmin(TranslatableAdmin):
    list_display = ["thumb", "title", "source_language", "category", "funnel_stage", "status", "published_at", "view_count",
                    "translation_badge"]
    list_filter = ["status", "source_language", "funnel_stage", "category", "content_source"]
    search_fields = ["title", "focus_keyword", "content"]
    prepopulated_fields = {"slug": ("title",)}
    list_display_links = ["thumb", "title"]
    readonly_fields = ["translation_matrix", "view_count", "created_at", "updated_at", "seo_check", "image_preview"]
    image_preview = image_preview("image_src", 160)
    autocomplete_fields = ["treatment"]
    inlines = [BlogPostTranslationInline]
    actions = TranslatableAdmin.actions + ["action_publish"]
    fieldsets = [
        ("Yayın", {"fields": ["status", "published_at", "source_language", "auto_translate", "translation_matrix"]}),
        ("İçerik", {"fields": ["title", "slug", "category", "excerpt", "content", "faq", ("featured_image", "image_preview"),
                               "featured_image_url", "featured_image_alt"]}),
        ("SEO", {"fields": ["meta_title", "meta_description", "focus_keyword", "seo_check", "schema_type",
                            "canonical_url", "noindex"]}),
        ("İlişkiler / E-E-A-T", {"fields": ["reviewed_by", "clinic", "treatment", "author"]}),
        ("Strateji", {"fields": ["funnel_stage", "target_personas", "content_source", "ai_generation_prompt"],
                      "classes": ["collapse"]}),
        ("İstatistik", {"fields": ["view_count", "created_at", "updated_at"], "classes": ["collapse"]}),
    ]

    @admin.display(description="")
    def thumb(self, obj):
        return format_html('<img src="{}" class="dt-thumb">', obj.image_src) if obj.image_src else "📝"

    @admin.display(description="SEO kontrol")
    def seo_check(self, obj):
        from apps.seo.audit import audit_post

        if not obj.pk:
            return "—"
        issues = audit_post(obj)
        if not issues:
            return "✅ Sorun yok"
        from django.utils.html import format_html_join

        return format_html_join("", "<div>⚠️ {}</div>", ((i,) for i in issues))

    @admin.action(description="📢 Yayınla (ve tüm dillere çevir)")
    def action_publish(self, request, queryset):
        n = 0
        for post in queryset.exclude(status=BlogPost.STATUS_PUBLISHED):
            post.status = BlogPost.STATUS_PUBLISHED
            post.save()
            n += 1
        self.message_user(request, f"{n} yazı yayınlandı; çeviriler arka planda başladı.", messages.SUCCESS)


@admin.register(RelatedPost)
class RelatedPostAdmin(admin.ModelAdmin):
    list_display = ["post", "related_post", "score", "is_manual"]
