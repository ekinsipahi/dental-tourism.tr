"""
Tüm programatik SEO sayfalarının ortak bileşenleri:

  * GERÇEK fotoğraflar  — klinik galerisi (ClinicImage), hekim fotoğrafı, önce-sonra vakaları. Stok görsel YOK.
  * Güven / backlink    — ana sayfa, hakkımızda, yorumlar, Instagram, Google profili ve
                          PROFILE_SITES (drdevrim.com, devrimbirikensipahi.com.tr) → /<dil>/ yolu ile.
  * Nöromarketing       — otorite (hekim yüzü + unvan), sosyal kanıt (gerçek puan / yorum sayısı),
                          karşılıklılık (ücretsiz değerlendirme), küçük ilk adım (fotoğraf gönder),
                          etik kayıptan kaçınma (sağlıklı dişi kaybetme), bilişsel kolaylık (3 adım),
                          persona'ya göre ana mesaj. Sahte aciliyet / sahte kıtlık KULLANILMAZ.
"""
import re

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _


def profile_site_links(lang):
    out = []
    for base, mode in settings.PROFILE_SITES:
        if mode == "lang":
            url = f"{base}/" if lang == "tr" else f"{base}/{lang}/"
        elif mode == "en":
            url = f"{base}/" if lang == "tr" else f"{base}/en/"
        else:  # root
            url = f"{base}/"
        out.append({"url": url, "label": base.split("://", 1)[-1]})
    return out


def trust_links(clinic, lang):
    links = [
        {"url": reverse("core:home"), "label": _("Home"), "icon": "🏠"},
        {"url": reverse("core:about"), "label": _("About us"), "icon": "👩‍⚕️"},
    ]
    if clinic:
        links.append({"url": clinic.get_absolute_url() + "#reviews", "label": _("Patient reviews"), "icon": "⭐"})
        if clinic.instagram:
            handle = clinic.instagram.strip("@/").rsplit("/", 1)[-1]
            links.append({"url": f"https://www.instagram.com/{handle}/", "label": "Instagram @" + handle,
                          "icon": "📷", "external": True})
        if clinic.google_business_url:
            links.append({"url": clinic.google_business_url, "label": _("Google reviews"), "icon": "📍",
                          "external": True})
        if getattr(clinic, "youtube_url", ""):
            links.append({"url": clinic.youtube_url, "label": "YouTube", "icon": "▶️", "external": True})
    for site in profile_site_links(lang):
        links.append({**site, "icon": "🔗", "external": True})
    return links


def real_photos(clinic, n=6, offset=0):
    """Galeriden n gerçek fotoğraf; offset ile her sayfada farklı bir kapak seçilir."""
    if not clinic:
        return []
    imgs, seen = [], set()
    for im in clinic.images.all():  # aynı dosyanın hash'li / hash'siz çift kaydı tek sayılır
        key = re.sub(r"\.[0-9a-f]{12}(\.\w+)$", r"\1", (im.src or "").rsplit("/", 1)[-1])
        if key and key not in seen:
            seen.add(key)
            imgs.append(im)
    if not imgs:
        return []
    k = offset % len(imgs)
    return (imgs[k:] + imgs[:k])[:n]


def persona_hook(persona):
    """Persona'ya göre üst mesaj (headline + alt metin). Hepsi doğru ve kanıtlanabilir iddialar."""
    p = (persona or {}).get("persona", "")
    hooks = {
        "fear": (_("Calm, pain-free and explained step by step"),
                 _("Local anaesthesia, a dentist who explains everything first, and no decision under pressure.")),
        "skeptic": (_("Check everything before you trust us"),
                    _("Real reviews with their source, named materials and a written plan before you travel.")),
        "price": (_("Very affordable — and a fixed price in writing"),
                  _("No hidden costs. Call or message us and receive your personal quote.")),
        "premium": (_("Time with your dentist, not with a sales team"),
                    _("One experienced dentist responsible for your whole treatment, premium materials, discreet care.")),
        "quality": (_("A treatment planned for you — not a template"),
                    _("Digital smile design, minimal preparation and one experienced dentist for every step. Healthy tooth tissue is saved first.")),
        "shame": (_("No judgement — only solutions"),
                  _("Whatever the state of your teeth, we have seen it before. We start with what can be saved.")),
        "trust": (_("A dentist-led clinic you can check"),
                  _("Qualifications, reviews and real photos — all on this page.")),
        "urgency": (_("Open 7 days a week in central Istanbul"),
                    _("Tell us your travel dates; we plan the appointments around your flights.")),
        "ready": (_("Plan your visit in one message"),
                  _("Send your photos and travel dates on WhatsApp — we reply with your personal plan.")),
    }
    return hooks.get(p, (_("Dental work is more than a Hollywood smile"),
                         _("We save healthy teeth first and plan a real treatment made only for you.")))


def pseo_context(request, *, offset=0, show_cases=False, photos=6):
    from apps.clinics.models import BeforeAfterCase, Clinic, Review

    lang = request.LANGUAGE_CODE
    try:
        clinic = Clinic.primary()
    except Exception:  # noqa: BLE001
        clinic = None
    doctor = clinic.doctors.filter(is_active=True).first() if clinic else None
    gallery = real_photos(clinic, photos, offset)
    hook_title, hook_text = persona_hook(getattr(request, "persona", None))
    ctx = {
        "clinic": clinic,
        "doctor": doctor,
        "doctor_loc": doctor.localized(lang) if doctor else None,
        "hero_photo": gallery[0] if gallery else None,
        "gallery": gallery[1:] if len(gallery) > 1 else gallery,
        "trust_links": trust_links(clinic, lang),
        "hook_title": hook_title,
        "hook_text": hook_text,
        "rating": clinic.google_rating if clinic else None,
        "rating_count": clinic.google_review_count if clinic else None,
        "proof_reviews": list(Review.objects.filter(is_published=True, clinic=clinic).exclude(text="")
                              .order_by("-rating", "-created_at")[:3]) if clinic else [],
        "tel_url": "tel:" + "".join(ch for ch in (clinic.phone if clinic else "") if ch.isdigit() or ch == "+"),
    }
    if clinic:  # hasta video yorumları (YouTube Shorts kapakları) — her pSEO sayfasında fotoğraf + video
        ctx["videos"] = list(Review.objects.filter(is_published=True, clinic=clinic).exclude(video_id="")
                             .select_related("treatment")[:4])
    if show_cases and clinic:
        ctx["cases"] = list(BeforeAfterCase.objects.filter(clinic=clinic, is_published=True, patient_consent=True)[:6])
    return ctx
