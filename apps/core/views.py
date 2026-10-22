from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language, gettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from apps.clinics.models import Review
from apps.localization.models import localize_list, with_translations
from apps.treatments.models import Treatment

from .forms import ContactForm
from .seo import page_meta, Seo, absolute, alternates_for, clinic_schema, faq_schema, organization_schema, proof, website_schema


def _home_faq(clinic):
    years = clinic.years_experience if clinic and clinic.years_experience else None
    return [
        {"question": _("Is it safe to get dental treatment in Turkey?"),
         "answer": _("Yes, when you choose a licensed clinic with experienced dentists and certified materials. "
                     "Ask for the dentist's credentials, the brands of implants and crowns, and a written "
                     "treatment plan before you travel.")},
        {"question": _("How much does dental treatment in Istanbul cost?"),
         "answer": _("Very affordable compared with Western Europe — with the same materials and techniques. "
                     "We do not publish one-size-fits-all prices: call us or send photos on WhatsApp and you "
                     "receive a fixed written quote before treatment starts.")},
        {"question": _("How long do I need to stay in Istanbul?"),
         "answer": _("It depends on the treatment: fillings, cleaning and composite veneers take 1–3 days, "
                     "crowns and porcelain veneers about 5–7 days, implants usually two visits a few months apart.")},
        {"question": _("Do you speak my language?"),
         "answer": _("We communicate with international patients in English and other languages, and you can "
                     "message the dentist directly on WhatsApp before, during and after your treatment.")},
    ] + ([{"question": _("How experienced is the dentist?"),
           "answer": _("Our lead dentist has %(years)s years of clinical experience.") % {"years": years}}]
         if years else [])


HOME_SECTIONS = ["hero", "treatments", "reviews", "how", "clinic-search", "contact", "faq", "cta"]


def home_sections():
    """Ana sayfa bölüm sırası/görünürlüğü — admin'de 'home-<bölüm>' content block'larının order/visible alanları."""
    from django.core.cache import caches

    from .models import ContentBlock

    cache = caches["local"]
    cached = cache.get("home:sections")
    if cached is not None:
        return cached
    blocks = {b.key: b for b in ContentBlock.objects.filter(key__in=[f"home-{n}" for n in HOME_SECTIONS])}
    out = []
    for i, name in enumerate(HOME_SECTIONS):
        b = blocks.get(f"home-{name}")
        if b is not None and not b.visible:
            continue
        order = -1 if name == "hero" else (b.order if b is not None and b.order else (i + 1) * 10)
        out.append({"name": name, "order": order, "template": f"home/sections/{name}.html"})
    out = sorted(out, key=lambda x: x["order"])
    cache.set("home:sections", out, 300)  # ContentBlock.save() 'home-*' için siler
    return out


def _home_data(clinic, lang):
    """Ana sayfanın her ziyaretçi için aynı olan verisi (tedaviler, yorumlar, videolar, SSS, slaytlar, vakalar, klinik
    schema'sı) — dil başına 5 dk süreç içi bellekte. Ziyaretçi başına ~15 Supabase sorgusu yerine işçi başına 5 dk'da 1 kez."""
    from django.core.cache import caches

    from apps.clinics.models import Clinic as _Clinic, light_reviews

    from .models import ContentBlock

    key = f"home-data:{clinic.pk if clinic else 0}:{lang}"
    data = caches["local"].get(key)
    if data is not None:
        return data
    treatments = localize_list(with_translations(Treatment.objects.filter(is_active=True, is_featured=True), lang), lang)
    # Tüm yayındaki kliniklerden yorumlar (öne çıkanlar önce) — çok klinikli yapıda karışık gelir
    live = _Clinic.objects.published()
    multi_clinic = live.count() > 1
    reviews = light_reviews(Review.objects.filter(is_published=True, clinic__in=live).exclude(text=""), lang) \
        .order_by("-is_featured", "order", "-review_date")
    videos = light_reviews(Review.objects.filter(is_published=True, clinic__in=live).exclude(video_id=""), lang) \
        .order_by("-is_featured", "order")
    if multi_clinic:  # yorum kartında klinik adı/linki yalnızca çok klinikli yapıda gösterilir
        reviews, videos = reviews.select_related("clinic"), videos.select_related("clinic")
    faq = _home_faq(clinic)
    block = ContentBlock.objects.filter(key="home-faq", is_active=True).first()
    if block:
        loc = block.localized(lang)
        if not loc.is_fallback and loc.items:
            faq = loc.items  # Admin'den düzenlenen SSS (FAQPage schema'sı da buradan üretilir)
    data = {
        "treatments": treatments, "multi_clinic": multi_clinic, "reviews": list(reviews[:12]), "videos": list(videos[:6]),
        "faq": faq, "slides": list(clinic.images.filter(show_in_hero=True)[:5]) if clinic else [],
        "cases": list(clinic.cases.filter(is_published=True, patient_consent=True)[:2]) if clinic else [],
        "clinic_schema": clinic_schema(clinic, url="/") if clinic else None,
    }
    caches["local"].set(key, data, 300)
    return data


def home(request):
    from apps.clinics.models import Clinic

    lang = get_language()
    clinic = Clinic.primary()
    d = _home_data(clinic, lang)
    treatments, multi_clinic, reviews, videos = d["treatments"], d["multi_clinic"], d["reviews"], d["videos"]
    faq, slides, cases = d["faq"], d["slides"], d["cases"]
    from apps.clinics.search import ClinicSearchForm

    search_form = ClinicSearchForm(lang=lang)

    _meta_home = page_meta("home", _("Dental Tourism Istanbul ★%(rating)s — Family Dentists, 35+ Years") % proof(),
                           _("We save your natural teeth first: root canals, fillings, minimal-prep veneers — implants only if a "
                             "tooth can't be saved. 35+ years, ★ %(rating)s on Google.") % proof())
    seo = Seo(
        title=_meta_home[0],
        description=_meta_home[1],
        canonical=absolute(request.path),
        alternates=alternates_for("core:home"),
        append_site_name=True,
        schema=[s for s in [organization_schema(), website_schema(), d["clinic_schema"], faq_schema(faq)] if s],
    )
    return render(request, "home.html", {
        "seo": seo, "treatments": treatments, "reviews": reviews, "videos": videos, "faq": faq,
        "form": ContactForm(), "page_type": "home", "search_form": search_form,
        "home_sections": home_sections(), "multi_clinic": multi_clinic, "slides": slides, "cases": cases,
    })


def about(request):
    from apps.clinics.models import Clinic, Doctor
    from apps.localization.memo import memo
    from apps.localization.models import with_all_translations

    clinic = Clinic.primary()
    # hekimler (tüm dillerdeki çevirileriyle) ve fotoğraflar klinik başına 5 dk süreç içi bellekte
    doctors = memo(f"about-doctors:{clinic.pk}", 300,
                   lambda: list(with_all_translations(clinic.doctors.filter(is_active=True))), model=Doctor) if clinic else []
    _meta_about = page_meta("about", _("About Us — Dr. Devrim & Dt. Ekin Sipahi, Family Dentists"),
                           _("A family dental clinic in Şişli, Istanbul: 35+ years' experience, diagnosis first and only "
                             "the treatment you need. Meet the dentists who will treat you."))
    seo = Seo(
        title=_meta_about[0],
        description=_meta_about[1],
        canonical=absolute(request.path),
        alternates=alternates_for("core:about"),
        breadcrumbs=[(_("Home"), reverse("core:home")), (_("About us"), request.path)],
    )
    from apps.seo.common import pseo_context

    ctx = pseo_context(request, offset=0, show_cases=True, photos=8)
    photos = memo(f"clinic-photos:{clinic.pk}", 300, lambda: list(clinic.images.all()), model=Clinic) if clinic else []
    ctx.update({"seo": seo, "doctors": [d.localized() for d in doctors], "page_type": "about",
                "about_photos": photos[:3], "story_photos": photos[3:5] or photos[:2],
                "clinic_loc": clinic.localized() if clinic else None})
    return render(request, "about.html", ctx)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            from apps.tracking.service import create_lead

            cd = form.cleaned_data
            create_lead(request, name=cd["name"], phone=cd["phone"], email=cd.get("email", ""),
                        message=cd.get("message", ""), page=cd.get("page") or request.path,
                        language=get_language(), treatment=cd.get("treatment"))
            return redirect(reverse("core:thanks"))
        messages.error(request, _("Please check the form and try again."))
    else:
        form = ContactForm()
    _meta_contact = page_meta("contact", _("Free Dental Assessment on WhatsApp — Answered by the Dentist"),
                           _("Send a photo or X-ray and receive a personal plan with a fixed written quote — answered by "
                             "the dentist, not a call centre. Open 7 days a week."))
    seo = Seo(
        title=_meta_contact[0],
        description=_meta_contact[1],
        canonical=absolute(request.path),
        alternates=alternates_for("core:contact"),
    )
    return render(request, "contact.html", {"seo": seo, "form": form, "page_type": "contact"})


def thanks(request):
    seo = Seo(title=_("Thank you — we will contact you shortly"), robots="noindex,follow",
              canonical=absolute(request.path))
    return render(request, "thanks.html", {"seo": seo, "page_type": "thanks"})


def privacy(request):
    seo = Seo(title=_("Privacy Policy"), description=_("How we process and protect your personal data (GDPR / KVKK)."),
              canonical=absolute(request.path), alternates=alternates_for("core:privacy"),
              robots="noindex,follow")
    return render(request, "privacy.html", {"seo": seo, "page_type": "privacy"})


@require_GET
@cache_page(60 * 60, cache="local")
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /*?persona=",
        "Disallow: /*contact/thank-you/",
        "",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


@require_GET
@cache_page(60 * 60, cache="local")
def llms_txt(request):
    """AI arama motorları için site özeti (llms.txt önerisi)."""
    from apps.clinics.models import Clinic

    clinic = Clinic.primary()
    lines = [f"# {settings.SITE_NAME}", "",
             "> Dental tourism in Istanbul, Turkey: implants, veneers, crowns and full-mouth restorations "
             f"for international patients, in {len(settings.LANGUAGES)} languages.", ""]
    if clinic:
        lines += [f"- Clinic: {clinic.name}, {clinic.address}", f"- Phone/WhatsApp: {clinic.phone}", ""]
    lines += ["## Main pages"]
    for t in Treatment.objects.filter(is_active=True):
        lines.append(f"- [{t.name}]({absolute(t.get_absolute_url())})")
    lines += ["", f"Sitemap: {settings.SITE_URL}/sitemap.xml"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


def page_not_found(request, exception=None):
    seo = Seo(title=_("Page not found"), robots="noindex,follow")
    return render(request, "404.html", {"seo": seo, "page_type": "404"}, status=404)


# ── Favicon / manifest (Google arama sonuçlarındaki site ikonu için kök dizinden erişilebilir olmalı) ──
def favicon(request):
    from django.contrib.staticfiles.storage import staticfiles_storage
    from django.shortcuts import redirect

    from .models import SiteSettings

    site = SiteSettings.load()
    if site.favicon:
        return redirect(site.favicon.url, permanent=False)
    return redirect(staticfiles_storage.url("favicon.ico"), permanent=True)


def apple_touch_icon(request):
    from django.contrib.staticfiles.storage import staticfiles_storage
    from django.shortcuts import redirect

    return redirect(staticfiles_storage.url("icons/apple-touch-icon.png"), permanent=True)


@cache_page(60 * 60 * 24, cache="local")
def webmanifest(request):
    import json

    from django.contrib.staticfiles.storage import staticfiles_storage

    data = {
        "name": settings.SITE_NAME, "short_name": settings.SITE_NAME, "start_url": "/", "display": "standalone",
        "background_color": "#070d10", "theme_color": "#070d10",
        "icons": [{"src": staticfiles_storage.url(f"icons/favicon-{n}.png"), "sizes": f"{n}x{n}", "type": "image/png"}
                  for n in (48, 96, 144, 192, 512)],
    }
    return HttpResponse(json.dumps(data), content_type="application/manifest+json")



def healthz(request):
    """Render sağlık kontrolü. Başlıklarda önbellek arka ucu (redis / locmem) ve çalışıp çalışmadığı — deploy sonrası
    Redis'in gerçekten kullanıldığı buradan görülür; gövde her zaman "ok" (Redis kopsa da site ayakta)."""
    from django.core.cache import caches

    cache = caches["default"]
    backend = "redis" if "Redis" in type(cache).__name__ else "locmem"
    try:
        cache.set("healthz", "1", 30)
        ping = "ok" if cache.get("healthz") == "1" else "miss"
    except Exception:  # noqa: BLE001
        ping = "error"
    import os

    resp = HttpResponse("ok", content_type="text/plain")
    resp["X-Cache-Backend"], resp["X-Cache-Ping"] = backend, ping
    resp["X-Commit"] = os.environ.get("RENDER_GIT_COMMIT", "")[:12] or "dev"  # deploy'un yayına çıktığı buradan görülür
    return resp
