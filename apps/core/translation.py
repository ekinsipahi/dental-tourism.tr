from apps.localization.registry import Field, TranslationSpec, register

from .models import ContentBlock


@register
class ContentBlockSpec(TranslationSpec):
    model = ContentBlock
    content_kind = "website section heading / UI copy for a dental tourism clinic (short, persuasive, warm)"
    fields = [
        Field("eyebrow", instructions="Very short label (2-5 words)."),
        Field("title"),
        Field("subtitle"),
        Field("body", "markdown"),
        Field("button_text", instructions="Short call-to-action."),
        Field("items", "faq"),
    ]

    def should_auto_translate(self, obj):
        return obj.auto_translate and obj.is_active
