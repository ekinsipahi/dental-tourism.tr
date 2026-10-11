from dental_tourism.languages import LANGUAGE_META
from apps.localization.registry import Field, TranslationSpec, register

from .models import LandingPage, SeoTopic


@register
class LandingPageSpec(TranslationSpec):
    model = LandingPage
    content_kind = "programmatic SEO landing page for dental tourism"
    fields = [
        Field("h1", instructions="H1 containing the focus keyword as locals search it."),
        Field("intro", "markdown"),
        Field("body", "markdown"),
        Field("faq", "faq"),
        Field("meta_title", max_length=70),
        Field("meta_description", max_length=170),
        Field("focus_keyword", "keyword"),
    ]

    def should_auto_translate(self, obj):
        return obj.auto_translate and obj.is_active

    def extra_context(self, obj, lang):
        meta = LANGUAGE_META[lang]
        if obj.page_type == LandingPage.TYPE_TREATMENT_PRICE:
            return (f"This is a price comparison page. Readers are in {', '.join(meta['markets'])}. "
                    "The page template renders a data table with real prices separately, so keep the "
                    "text free of specific foreign price numbers unless they are in the source.")
        return ""


@register
class SeoTopicSpec(TranslationSpec):
    model = SeoTopic
    content_kind = "programmatic SEO guide page of a dental clinic in Istanbul (dental tourism)"
    fields = [
        Field("slug", "slug"),
        Field("h1", instructions="H1 phrased the way people in this language search for it."),
        Field("lead"),
        Field("body", "markdown"),
        Field("faq", "faq"),
        Field("meta_title", max_length=70),
        Field("meta_description", max_length=170),
    ]

    def should_auto_translate(self, obj):
        return obj.auto_translate and obj.is_active

    def extra_context(self, obj, lang):
        return ("Never add prices or currency amounts. Prices are described only as affordable; readers are invited "
                "to call or message on WhatsApp for a personal quote. Use the local search phrases of "
                f"{', '.join(LANGUAGE_META[lang]['markets'])}.")
