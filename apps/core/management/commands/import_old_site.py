"""
Eski siteden (devrimbirikensipahi.com.tr) gerçek içerikleri aktarır — idempotent.

Kaynak: apps/core/data/old_site_content.json (eski sitenin TR orijinalleri + EN/DE/NL insan çevirileri)
  - Hekim özgeçmişi (Ankara Üni. mezunu, Marmara Üni. Ağız-Diş-Çene Radyolojisi), Dt. Ekin Sipahi
  - Klinik açıklaması, SSS, çalışma saatleri, gerçek profil linkleri (web sitesi, Google Haritalar, Instagram, YouTube)
  - 11 Google yorumu, ana sayfa diş turizmi SSS'si, tedavi SSS'leri, KVKK aydınlatma metni
  - Önce/sonra vakalarının açıklamaları (+ yayınlama — kullanıcı onayıyla)

    python manage.py import_old_site
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.clinics.models import BeforeAfterCase, Clinic, ClinicLink, Doctor, Review
from apps.core.models import ContentBlock
from apps.localization.models import TranslationStatus
from apps.treatments.models import Treatment

DATA = Path(__file__).resolve().parents[2] / "data" / "old_site_content.json"
HUMAN_LANGS = ("tr", "de", "nl")  # en = kaynak dil


def faq(items, lang):
    out = []
    for it in items:
        q, a = it["q"].get(lang), it["a"].get(lang)
        if q and a:
            out.append({"question": q, "answer": a})
    return out


def paragraphs(items, lang):
    return "\n\n".join(p[lang] for p in items if p.get(lang))


class Command(BaseCommand):
    help = "Eski sitenin gerçek içeriklerini (yorumlar, SSS, hekim, KVKK...) aktarır"

    def add_arguments(self, parser):
        parser.add_argument("--publish-cases", action="store_true", default=True)

    @transaction.atomic
    def handle(self, *args, publish_cases=True, **o):
        settings.AUTO_TRANSLATE_ON_PUBLISH = False  # insan çevirileri elle yazılıyor
        d = json.loads(DATA.read_text(encoding="utf-8"))
        clinic = Clinic.objects.get(slug="dr-devrim-sipahi")
        prof = d["profiles"]

        # ── Klinik ────────────────────────────────────────────────────────
        c = d["clinic"]
        clinic.website = prof["website"]
        clinic.maps_url = prof["google_maps"]
        clinic.google_business_url = prof["google_maps"]
        clinic.instagram = prof["instagram"]
        clinic.youtube_url = prof["youtube"]
        clinic.opening_hours = prof["opening_hours"]
        clinic.languages_spoken = ["tr", "en", "de"]
        clinic.tagline = c["tagline"]["en"]
        clinic.short_description = c["short"]["en"][:400]
        intro = paragraphs(d["doctor_bio"], "en")
        clinic.description = (f"{intro}\n\n## Open 7 days a week\n\n{c['hours_note']['en']} "
                              f"{c['weekend']['en']}\n\n## Location\n\n{c['areas']['en']}")
        clinic.faq = faq(d["clinic_faq"], "en")
        clinic.meta_title = c["meta_title"]["en"][:70]
        clinic.meta_description = c["meta_description"]["en"][:170]
        clinic.save()
        h = clinic.compute_source_hash()
        for lang in HUMAN_LANGS:
            body = (f"{paragraphs(d['doctor_bio'], lang)}\n\n{c['hours_note'][lang]} {c['weekend'][lang]}"
                    f"\n\n{c['areas'][lang]}")
            clinic.translations.update_or_create(language_code=lang, defaults={
                "tagline": c["tagline"][lang], "short_description": c["short"][lang][:400], "description": body,
                "faq": faq(d["clinic_faq"], lang), "meta_title": c["meta_title"][lang][:70],
                "meta_description": c["meta_description"][lang][:170],
                "status": TranslationStatus.REVIEWED, "source_hash": h})
        ClinicLink.objects.get_or_create(clinic=clinic, platform="youtube",
                                         url="https://www.youtube.com/@devrimbirikensipahi/shorts",
                                         defaults={"label": "YouTube Shorts"})
        self.stdout.write("✓ Klinik bilgileri, SSS, saatler, profil linkleri (EN + TR/DE/NL)")

        # ── Hekimler ──────────────────────────────────────────────────────
        doc = Doctor.objects.get(slug="devrim-biriken-sipahi")
        doc.university = "Ankara University, Faculty of Dentistry"
        doc.specialties = prof["specialties"]
        doc.title_display = "Dentist — Oral & Maxillofacial Radiology"
        doc.bio = paragraphs(d["doctor_bio"][:3], "en")
        doc.meta_title = "Dr. Dt. Devrim Biriken Sipahi — Dentist in Şişli, Istanbul"
        doc.meta_description = c["short"]["en"][:170]
        doc.save()
        titles = {"tr": "Diş Hekimi — Ağız, Diş ve Çene Radyolojisi", "de": "Zahnärztin — Mund-, Kiefer- und Gesichtsradiologie",
                  "nl": "Tandarts — Mond-, kaak- en aangezichtsradiologie"}
        h = doc.compute_source_hash()
        for lang in HUMAN_LANGS:
            doc.translations.update_or_create(language_code=lang, defaults={
                "title_display": titles[lang], "bio": paragraphs(d["doctor_bio"][:3], lang),
                "meta_title": f"Dr. Dt. Devrim Biriken Sipahi — {titles[lang].split(' — ')[0]}"[:70],
                "meta_description": c["short"][lang][:170], "status": TranslationStatus.REVIEWED, "source_hash": h})
        ekin, _ = Doctor.objects.update_or_create(slug="ekin-sipahi", defaults={
            "clinic": clinic, "name": "Ekin Sipahi", "honorific": "Dt.", "title_display": "Dentist",
            "is_lead_doctor": False, "order": 2, "languages_spoken": ["tr", "en"], "source_language": "en",
            "bio": d["doctor_bio"][3]["en"]})
        h = ekin.compute_source_hash()
        for lang in HUMAN_LANGS:
            ekin.translations.update_or_create(language_code=lang, defaults={
                "title_display": {"tr": "Diş Hekimi", "de": "Zahnärztin", "nl": "Tandarts"}[lang],
                "bio": d["doctor_bio"][3][lang], "status": TranslationStatus.REVIEWED, "source_hash": h})
        self.stdout.write("✓ Dr. Devrim Sipahi özgeçmişi + Dt. Ekin Sipahi")

        # ── Google yorumları ──────────────────────────────────────────────
        n = 0
        for i, r in enumerate(d["reviews"]):
            _, created = Review.objects.update_or_create(
                clinic=clinic, author_name=r["author"], source="google",
                defaults={"text": r["text"], "language": "tr", "rating": 5, "country_code": "TR",
                          "source_url": prof["google_maps"], "is_published": True, "order": i})
            n += created
        self.stdout.write(f"✓ {len(d['reviews'])} Google yorumu ({n} yeni), kaynak linki Google Haritalar")

        # ── Tedavi SSS'leri (EN kaynak; diğer diller AI çevirisiyle) ─────
        for key, items in d["treatment_faq"].items():
            t = Treatment.objects.filter(key=key).first()
            if not t:
                continue
            existing = {f["question"] for f in t.faq}
            t.faq = t.faq + [f for f in faq(items, "en") if f["question"] not in existing]
            t.save()
        self.stdout.write("✓ Tedavi SSS'leri (implant, kanal, lamina, kompozit)")

        # ── Ana sayfa SSS + KVKK (ContentBlock, TR/DE/NL insan çevirisi) ─
        blk, _ = ContentBlock.objects.get_or_create(key="home-faq", defaults={"page": "home", "label": "Ana sayfa — SSS"})
        blk.items = faq(d["home_faq"], "en")
        blk.save()
        h = blk.compute_source_hash()
        for lang in HUMAN_LANGS:
            blk.translations.update_or_create(language_code=lang, defaults={
                "title": {"tr": "Sıkça sorulan sorular", "de": "Häufig gestellte Fragen", "nl": "Veelgestelde vragen"}[lang],
                "items": faq(d["home_faq"], lang), "status": TranslationStatus.REVIEWED, "source_hash": h})

        def privacy_md(lang):
            """Eski sitenin KVKK satırlarını Markdown'a çevirir: başlıklar ##, ':' ile biten satırdan sonrası madde."""
            out, in_list = [], False
            for line in (x[lang] for x in d["privacy"]):
                if line.isupper():
                    continue
                if line[:2].rstrip(".").isdigit() and ". " in line[:4]:
                    out.append(f"\n## {line}\n")
                    in_list = False
                elif in_list and len(line) < 140 and not line.endswith((":", ";")):
                    out.append(f"- {line}")
                else:
                    out.append(("\n" if in_list else "") + line)
                    in_list = line.endswith(":") or line.endswith(";")
                    if in_list:
                        out.append("")  # Markdown listesi için boş satır
            return "\n".join(out).strip() + f"\n\n{clinic.email}"

        pv, _ = ContentBlock.objects.get_or_create(key="page-privacy", defaults={
            "page": "global", "label": "Gizlilik / KVKK aydınlatma metni"})
        pv.title = "Privacy Policy (KVKK)"
        pv.body = privacy_md("en")
        pv.save()
        h = pv.compute_source_hash()
        for lang in HUMAN_LANGS:
            pv.translations.update_or_create(language_code=lang, defaults={
                "title": d["privacy"][0][lang], "body": privacy_md(lang),
                "status": TranslationStatus.REVIEWED, "source_hash": h})
        self.stdout.write("✓ Ana sayfa SSS + KVKK aydınlatma metni")

        # ── Önce / sonra vakaları ─────────────────────────────────────────
        for name, caption_key in (("Front teeth restoration", "hazan"), ("Smile aesthetics", "sanem")):
            case = BeforeAfterCase.objects.filter(caption__in=[name, d["cases"][caption_key]["en"]]).first()
            if case:
                case.caption = d["cases"][caption_key]["en"][:200]
                if publish_cases:
                    case.patient_consent = True
                    case.is_published = True
                case.save()
        self.stdout.write(self.style.SUCCESS("✓ Önce/sonra vakaları açıklamalarıyla yayında (kullanıcı onayı)"))
