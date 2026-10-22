from django import forms
from django.utils.translation import gettext_lazy as _

from dental_tourism.languages import LANGUAGE_META

COUNTRY_CHOICES = [("", _("Your country"))] + sorted(
    {(c, c) for meta in LANGUAGE_META.values() for c in meta["markets"]} | {("TR", "TR"), ("US", "US")})


class ReviewForm(forms.Form):
    author_name = forms.CharField(label=_("Your name"), max_length=60,
                                  help_text=_("Shown as first name and initial, e.g. 'Anna K.'"))
    email = forms.EmailField(label=_("Email"), help_text=_("Not published — only used to verify your review."))
    country_code = forms.ChoiceField(label=_("Country"), choices=COUNTRY_CHOICES, required=False)
    rating = forms.TypedChoiceField(label=_("Rating"), coerce=int, choices=[(i, "★" * i) for i in range(5, 0, -1)],
                                    widget=forms.RadioSelect)
    treatment = forms.ModelChoiceField(label=_("Treatment"), queryset=None, required=False,
                                       empty_label=_("Select treatment"))
    title = forms.CharField(label=_("Title"), max_length=120, required=False)
    text = forms.CharField(label=_("Your experience"), min_length=30, max_length=3000,
                           widget=forms.Textarea(attrs={"rows": 5}))
    consent = forms.BooleanField(label=_("I confirm this review describes my own experience as a patient."))
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def __init__(self, *args, clinic=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.treatments.models import Treatment

        from apps.localization.models import with_translations

        qs = Treatment.objects.filter(is_active=True).defer("body", "faq", "short_description")
        if clinic is not None:
            qs = qs.filter(clinic_offers__clinic=clinic).distinct()
        self.fields["treatment"].queryset = with_translations(qs, tr_defer=("body", "faq", "short_description"))
        self.fields["treatment"].label_from_instance = lambda t: t.localized().name

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("spam")
        return ""

    def clean_author_name(self):
        name = " ".join(self.cleaned_data["author_name"].split())
        parts = name.split(" ")
        # Gizlilik: soyadın sadece baş harfi
        if len(parts) > 1:
            name = f"{parts[0]} {parts[-1][0].upper()}."
        return name
