from apps.localization.registry import Field, TranslationSpec, register

from .models import City, Clinic, Doctor


@register
class CitySpec(TranslationSpec):
    model = City
    content_kind = "city name and short description of the city as a dental tourism destination"
    fields = [
        Field("name", instructions="The city's standard name in the target language."),
        Field("slug", "slug", "Just the city name, transliterated."),
        Field("description", "markdown"),
    ]


@register
class ClinicSpec(TranslationSpec):
    model = Clinic
    content_kind = "dental clinic profile page"
    fields = [
        Field("tagline", max_length=200),
        Field("short_description", max_length=400),
        Field("description", "markdown"),
        Field("faq", "faq"),
        Field("meta_title", max_length=70),
        Field("meta_description", max_length=170),
    ]

    def should_auto_translate(self, obj):
        return obj.auto_translate and obj.status == Clinic.STATUS_APPROVED


@register
class DoctorSpec(TranslationSpec):
    model = Doctor
    content_kind = "dentist biography / profile page"
    fields = [
        Field("title_display", instructions="Professional title, e.g. 'Dentist, Implantologist'."),
        Field("bio", "markdown"),
        Field("meta_title", max_length=70),
        Field("meta_description", max_length=170),
    ]

    def should_auto_translate(self, obj):
        return obj.auto_translate and obj.is_active and obj.clinic.status == Clinic.STATUS_APPROVED
