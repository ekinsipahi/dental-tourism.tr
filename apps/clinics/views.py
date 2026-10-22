from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import get_language, gettext as _

from apps.core.seo import Seo, absolute, alternates_for, clinic_schema, faq_schema, fill_proof, page_meta, proof
from apps.localization.models import localize_list, with_translations

from .models import Clinic, Doctor, Review


def _clinic_alternates(clinic):
    langs = clinic.live_languages()
    return alternates_for("clinics:detail", lambda lg: {"slug": clinic.slug} if lg in langs else None)


def clinic_list(request):
    from django.core.paginator import Paginator

    from .search import ClinicSearchForm, search_clinics

    lang = get_language()
    form = ClinicSearchForm(request.GET or None, lang=lang)
    results = search_clinics(form)
    page = Paginator(results, 12).get_page(request.GET.get("page"))
    rows = [{"c": clinic.localized(lang), "offer": offer, "min_price": min_price,
             "doctor": next(iter(clinic.doctors.all()), None)} for clinic, offer, min_price in page.object_list]
    filtered = bool(request.GET)
    _meta_clinics = page_meta("clinics", _("Our Dental Clinic in Istanbul — Şişli, ★%(rating)s, Open 7 Days") % proof(),
                           _("Dentist-led family clinic in Şişli, Istanbul: 35+ years' experience, ★ %(rating)s from "
                             "%(count)s Google reviews, languages spoken and real patient stories.") % proof())
    seo = Seo(
        title=_meta_clinics[0],
        description=_meta_clinics[1],
        canonical=absolute(reverse("clinics:list")),
        alternates={} if filtered else alternates_for("clinics:list"),
        # Filtre kombinasyonları indexlenmez (duplicate/ince içerik); canonical ana listeye
        robots="noindex,follow" if filtered else "index,follow,max-image-preview:large",
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Clinics"), request.path)],
        schema=[{"@context": "https://schema.org", "@type": "ItemList",
                 "itemListElement": [{"@type": "ListItem", "position": i, "url": absolute(r["c"].get_absolute_url()),
                                      "name": r["c"].name} for i, r in enumerate(rows, 1)]}],
    )
    return render(request, "clinics/list.html", {"seo": seo, "rows": rows, "page_obj": page, "search_form": form,
                                                 "total": len(results), "filtered": filtered,
                                                 "page_type": "clinic_list"})


def clinic_detail(request, slug):
    lang = get_language()
    clinic = get_object_or_404(Clinic.objects.published().select_related("city"), slug=slug)
    loc = clinic.localized(lang)
    from apps.localization.models import with_related_translations

    from .forms import ReviewForm
    from .models import light_reviews

    # tedavi adları + slug'lar tek sorguda (döngüde localized() → N sorgu olmasın); gövde/SSS çekilmez
    offers = with_related_translations(
        clinic.treatment_offers.filter(is_active=True, treatment__is_active=True).select_related("treatment")
        .defer("treatment__body", "treatment__faq"), "treatment", lang)
    offer_rows = [{"offer": o, "t": o.treatment.localized(lang)} for o in offers]
    doctors = localize_list(with_translations(clinic.doctors.filter(is_active=True), lang), lang)
    reviews = light_reviews(clinic.reviews.filter(is_published=True), lang)
    alternates = _clinic_alternates(clinic)

    seo = Seo(
        title=fill_proof(loc.meta_title) or _("%(clinic)s — Dental Clinic in %(city)s") % {"clinic": clinic.name,
                                                                          "city": clinic.city.localized(lang).name},
        description=fill_proof(loc.meta_description) or loc.short_description,
        canonical=alternates.get(lang) or absolute(request.path),
        alternates=alternates,
        robots="noindex,follow" if loc.is_fallback else "index,follow,max-image-preview:large",
        image=clinic.display_image,
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("Clinics"), reverse("clinics:list")),
                     (clinic.name, request.path)],
        schema=[s for s in [clinic_schema(clinic, loc, with_reviews=True), faq_schema(loc.faq)] if s],
    )
    return render(request, "clinics/detail.html", {
        "seo": seo, "c": loc, "offers": offer_rows, "doctors": doctors,
        "site_reviews": reviews.filter(source=Review.SOURCE_SITE).exclude(text="")[:20],
        "external_reviews": reviews.exclude(source=Review.SOURCE_SITE).exclude(text="")[:12],
        "videos": reviews.exclude(video_id="")[:8],
        "stats": clinic.review_stats(), "links": clinic.social_links,
        "review_form": ReviewForm(clinic=clinic),
        "images": clinic.images.all()[:12], "cases": clinic.cases.filter(is_published=True, patient_consent=True)[:6],
        "page_type": "clinic",
    })


def doctor_detail(request, slug):
    lang = get_language()
    doctor = get_object_or_404(Doctor.objects.select_related("clinic", "clinic__city"),
                               slug=slug, is_active=True, clinic__status=Clinic.STATUS_APPROVED)
    loc = doctor.localized(lang)
    langs = doctor.live_languages()
    alternates = alternates_for("doctors:detail", lambda lg: {"slug": doctor.slug} if lg in langs else None)
    person = {
        "@context": "https://schema.org",
        "@type": ["Person", "Physician"],
        "name": doctor.full_name,
        "jobTitle": loc.title_display or "Dentist",
        "url": alternates.get(lang) or absolute(request.path),
        "worksFor": {"@id": absolute(doctor.clinic.get_absolute_url()) + "#clinic", "name": doctor.clinic.name},
        "medicalSpecialty": "Dentistry",
        "knowsLanguage": doctor.languages_spoken or None,
        "alumniOf": {"@type": "CollegeOrUniversity", "name": doctor.university} if doctor.university else None,
        "memberOf": [{"@type": "Organization", "name": m} for m in doctor.memberships] or None,
        "image": absolute(doctor.photo_src) if doctor.photo_src else None,
    }
    seo = Seo(
        title=fill_proof(loc.meta_title) or _("%(doctor)s — Dentist in %(city)s") % {"doctor": doctor.full_name,
                                                                     "city": doctor.clinic.city.localized(lang).name},
        description=fill_proof(loc.meta_description) or (loc.bio or "")[:160],
        canonical=alternates.get(lang) or absolute(request.path),
        alternates=alternates,
        og_type="profile",
        robots="noindex,follow" if loc.is_fallback else "index,follow,max-image-preview:large",
        image=doctor.photo_src,
        breadcrumbs=[(_("Home"), reverse("core:home")), (doctor.clinic.name, doctor.clinic.get_absolute_url()),
                     (doctor.full_name, request.path)],
        schema=[{k: v for k, v in person.items() if v}],
    )
    return render(request, "clinics/doctor.html", {
        "seo": seo, "d": loc, "clinic": doctor.clinic, "reviews": doctor.reviews.filter(is_published=True)[:8],
        "posts": doctor.reviewed_posts.filter(status="published")[:6], "page_type": "doctor",
    })


def submit_review(request, slug):
    """Hasta yorumu — moderasyon kuyruğuna düşer (is_published=False)."""
    import hashlib

    from django.contrib import messages
    from django.core.cache import cache
    from django.core.mail import send_mail
    from django.conf import settings
    from django.shortcuts import redirect

    from apps.tracking.models import Lead

    from .forms import ReviewForm

    clinic = get_object_or_404(Clinic.objects.published(), slug=slug)
    if request.method != "POST":
        return redirect(clinic.get_absolute_url() + "#write-review")
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip()
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:32]
    rate_key = f"review-rate:{ip_hash}"
    if cache.get(rate_key, 0) >= 3:
        messages.error(request, _("Too many reviews from your connection. Please try again later."))
        return redirect(clinic.get_absolute_url() + "#write-review")
    form = ReviewForm(request.POST, clinic=clinic)
    if not form.is_valid():
        messages.error(request, _("Please check the review form and try again."))
        return redirect(clinic.get_absolute_url() + "#write-review")
    cd = form.cleaned_data
    lead = Lead.objects.filter(clinic=clinic, email__iexact=cd["email"]).first()
    review = Review.objects.create(
        clinic=clinic, treatment=cd.get("treatment"), author_name=cd["author_name"], email=cd["email"],
        country_code=cd.get("country_code") or "", language=get_language(), rating=cd["rating"],
        title=cd.get("title", ""), text=cd["text"], source=Review.SOURCE_SITE, is_published=False,
        is_verified_patient=bool(lead), lead=lead, ip_hash=ip_hash, review_date=timezone.now().date(),
    )
    cache.set(rate_key, cache.get(rate_key, 0) + 1, 60 * 60 * 24)
    recipient = clinic.email or settings.LEAD_NOTIFY_EMAIL
    if recipient and settings.EMAIL_ENABLED:
        send_mail(f"[Yorum onayı] {clinic.name} — {review.rating}★", f"{review.author_name}: {review.text}\n\n"
                  f"Onaylamak için: {settings.SITE_URL}/admin/clinics/review/{review.pk}/change/",
                  settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)
    messages.success(request, _("Thank you! Your review will be published after a short check."))
    return redirect(clinic.get_absolute_url() + "#reviews")
