"""Klinik arama / filtreleme (klinikler sayfası + ana sayfadaki arama kutusu)."""
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from dental_tourism.languages import LANGUAGE_META

from .models import City, Clinic, ClinicTreatment

SORT_CHOICES = [
    ("featured", _("Recommended")),
    ("rating", _("Highest rated")),
    ("experience", _("Most experienced")),
]


class ClinicSearchForm(forms.Form):
    q = forms.CharField(required=False, label=_("Search"),
                        widget=forms.TextInput(attrs={"placeholder": _("Clinic, dentist or district…"),
                                                      "type": "search"}))
    city = forms.ChoiceField(required=False, label=_("City"))
    treatment = forms.ChoiceField(required=False, label=_("Treatment"))
    language = forms.ChoiceField(required=False, label=_("Language spoken"))
    min_rating = forms.ChoiceField(required=False, label=_("Google rating"),
                                   choices=[("", _("Any")), ("4.5", "4.5+ ★"), ("4.8", "4.8+ ★")])
    verified = forms.BooleanField(required=False, label=_("Verified clinics only"))
    transfer = forms.BooleanField(required=False, label=_("Airport transfer"))
    hotel = forms.BooleanField(required=False, label=_("Hotel booking help"))
    sort = forms.ChoiceField(required=False, choices=SORT_CHOICES, label=_("Sort by"))

    def __init__(self, *args, lang="en", **kwargs):
        super().__init__(*args, **kwargs)
        from apps.treatments.models import Treatment

        self.fields["city"].choices = [("", _("All cities"))] + [
            (c.slug, c.localized(lang).name) for c in City.objects.filter(is_active=True, clinics__status="approved").distinct()]
        self.fields["treatment"].choices = [("", _("All treatments"))] + [
            (t.key, t.localized(lang).name) for t in Treatment.objects.filter(is_active=True)]
        self.fields["language"].choices = [("", _("Any language"))] + [
            (code, meta["native"]) for code, meta in LANGUAGE_META.items()]

    @property
    def is_filtered(self):
        return self.is_bound and any(v not in (None, "", False) for k, v in self.cleaned_data.items() if k != "sort")


def search_clinics(form):
    """Döner: [(clinic, offer_for_selected_treatment_or_None, min_price)]"""
    qs = Clinic.objects.published().select_related("city").prefetch_related("images", "doctors")
    cd = form.cleaned_data if form.is_valid() else {}
    treatment = cd.get("treatment")

    if cd.get("q"):
        q = cd["q"].strip()
        qs = qs.filter(Q(name__icontains=q) | Q(short_name__icontains=q) | Q(district__icontains=q)
                       | Q(neighborhood__icontains=q) | Q(doctors__name__icontains=q)
                       | Q(translations__short_description__icontains=q)).distinct()
    if cd.get("city"):
        qs = qs.filter(Q(city__slug=cd["city"]) | Q(city__translations__slug=cd["city"])).distinct()
    if treatment:
        qs = qs.filter(treatment_offers__treatment__key=treatment, treatment_offers__is_active=True)
    if cd.get("language"):
        # JSONField contains (SQLite/Postgres uyumlu basit yöntem)
        qs = qs.filter(languages_spoken__icontains=f'"{cd["language"]}"')
    if cd.get("min_rating"):
        qs = qs.filter(google_rating__gte=cd["min_rating"])
    if cd.get("verified"):
        qs = qs.filter(is_verified=True)
    if cd.get("transfer"):
        qs = qs.filter(offers_airport_transfer=True)
    if cd.get("hotel"):
        qs = qs.filter(offers_hotel_booking=True)

    qs = qs.distinct()

    sort = cd.get("sort") or "featured"
    order = {
        "featured": ["-is_primary", "-is_featured", "order", "name"],
        "rating": ["-google_rating", "-google_review_count", "name"],
        "experience": ["-years_experience", "name"],
    }[sort]
    qs = qs.order_by(*order)

    results = []
    offers = {}
    if treatment:
        offers = {o.clinic_id: o for o in ClinicTreatment.objects.filter(
            treatment__key=treatment, clinic__in=qs, is_active=True)}
    for clinic in qs:
        results.append((clinic, offers.get(clinic.pk), None))
    return results
