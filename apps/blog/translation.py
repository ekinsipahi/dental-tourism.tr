from dental_tourism.languages import LANGUAGE_META
from apps.localization.registry import Field, TranslationSpec, register

from .models import BlogCategory, BlogPost


@register
class BlogCategorySpec(TranslationSpec):
    model = BlogCategory
    content_kind = "blog category"
    fields = [
        Field("name"),
        Field("slug", "slug", "1-3 words."),
        Field("description"),
        Field("meta_title", max_length=70),
        Field("meta_description", max_length=170),
    ]


@register
class BlogPostSpec(TranslationSpec):
    model = BlogPost
    content_kind = "patient-education blog article for a dental tourism clinic in Istanbul"
    fields = [
        Field("title", instructions="Natural H1 headline containing the focus keyword."),
        Field("slug", "slug"),
        Field("excerpt", max_length=300),
        Field("content", "markdown"),
        Field("faq", "faq"),
        Field("featured_image_alt", instructions="Descriptive image alt text."),
        Field("meta_title", max_length=70),
        Field("meta_description", max_length=170),
        Field("focus_keyword", "keyword"),
    ]

    def should_auto_translate(self, obj):
        # Sadece yayınlanan yazılar çevrilir — taslaklar için API maliyeti oluşmaz
        return obj.auto_translate and obj.status == BlogPost.STATUS_PUBLISHED

    def dependencies(self, obj):
        return [obj.category]

    def extra_context(self, obj, lang):
        meta = LANGUAGE_META[lang]
        return (f"Where the article compares costs with the reader's home country, adapt the comparison "
                f"to {meta['compare_country']} only if the source gives numbers for it; otherwise keep "
                f"the source comparison. Do not invent prices.")
