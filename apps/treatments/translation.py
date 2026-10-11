from apps.localization.registry import Field, TranslationSpec, register

from .models import Treatment


@register
class TreatmentSpec(TranslationSpec):
    model = Treatment
    content_kind = "dental treatment landing page (patient-facing, SEO-optimized)"
    fields = [
        Field("name", instructions="Patient-friendly treatment name as locals search it."),
        Field("slug", "slug"),
        Field("short_description", max_length=400),
        Field("body", "markdown"),
        Field("faq", "faq"),
        Field("meta_title", max_length=70),
        Field("meta_description", max_length=170),
        Field("focus_keyword", "keyword"),
    ]

    def should_auto_translate(self, obj):
        return obj.auto_translate and obj.is_active
