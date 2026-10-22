from django import forms
from django.utils.translation import gettext_lazy as _

from apps.treatments.models import Treatment


class ContactForm(forms.Form):
    name = forms.CharField(label=_("Full name"), max_length=200,
                           widget=forms.TextInput(attrs={"autocomplete": "name",
                                                         "placeholder": _("Your first and last name")}))
    phone = forms.CharField(label=_("Phone / WhatsApp"), max_length=30,
                            widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel",
                                                          "placeholder": "+49 / +31 / +44 / +90 …"}))
    email = forms.EmailField(label=_("Email"), required=False,
                             widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    treatment = forms.ModelChoiceField(label=_("Treatment of interest"), required=False,
                                       queryset=Treatment.objects.none(), empty_label=_("Not sure yet"))
    message = forms.CharField(label=_("Message"), required=False,
                              widget=forms.Textarea(attrs={"rows": 4,
                                                           "placeholder": _("Tell us about your dental situation…")}))
    page = forms.CharField(required=False, widget=forms.HiddenInput)
    consent = forms.BooleanField(label=_("I agree that my data is processed to answer my request (GDPR / KVKK)."))
    # Spam tuzağı — gerçek kullanıcı doldurmaz
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils.translation import get_language

        from apps.localization.memo import memo
        from apps.localization.models import with_translations

        lang = get_language()
        field = self.fields["treatment"]
        field.queryset = Treatment.objects.filter(is_active=True)  # yalnızca gönderimde (POST) doğrulama için

        def load():  # seçenek listesi dil başına süreç içi bellekte: formu taşıyan her sayfa 2 sorgu atmaz
            qs = with_translations(Treatment.objects.filter(is_active=True).defer("body", "faq", "short_description"), lang,
                                   tr_defer=("body", "faq", "short_description"))
            return [("", str(field.empty_label))] + [(t.pk, t.localized(lang).name) for t in qs]
        field.choices = memo(f"contact-choices:{lang}", 300, load, model=Treatment)

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("spam")
        return ""

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = sum(c.isdigit() for c in phone)
        if digits < 7:
            raise forms.ValidationError(_("Please enter a valid phone number with country code."))
        return phone
