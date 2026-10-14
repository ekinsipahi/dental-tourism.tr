"""
Başlangıç verisi — idempotent (tekrar çalıştırmak güvenli, mevcut kayıtları ezmez).

    python manage.py seed_data
    python manage.py seed_data --keywords   # 17 dil keyword matrisini de oluştur
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from slugify import slugify

from dental_tourism.languages import LANGUAGE_META

from apps.blog.models import BlogCategory
from apps.clinics.models import City, CityTranslation, Clinic, ClinicTreatment, Doctor, Review
from apps.core import seed_content as S
from apps.localization.models import TranslationStatus
from apps.seo.keyword_data import CITY_SLUGS, TREATMENT_KEYS, TREATMENT_NAMES, TREATMENT_SLUGS
from apps.seo.models import LandingPage
from apps.treatments.models import MarketPrice, Treatment, TreatmentTranslation


class Command(BaseCommand):
    help = "Ana kliniği, tedavileri, şehirleri, yorumları ve blog kategorilerini oluşturur."

    def add_arguments(self, parser):
        parser.add_argument("--keywords", action="store_true", help="Keyword matrisini de üret")

    @transaction.atomic
    def handle(self, *args, keywords=False, **opts):
        # AI çeviri sinyallerini seed sırasında tetikleme
        from django.conf import settings

        settings.AUTO_TRANSLATE_ON_PUBLISH = False

        city = self._city()
        treatments = self._treatments()
        clinic = self._clinic(city)
        self._offers(clinic, treatments)
        self._reviews(clinic, treatments)
        self._market_prices(treatments)
        self._blog_categories()
        self._landing_pages(treatments, city)
        from django.core.management import call_command

        call_command("sync_content_blocks", verbosity=0, stdout=self.stdout)
        if keywords:
            from apps.seo.services import seed_keywords

            n = seed_keywords()
            self.stdout.write(self.style.SUCCESS(f"✓ {n} keyword oluşturuldu"))
        self.stdout.write(self.style.SUCCESS("✓ Seed tamamlandı. Sonraki adım: "
                                             "python manage.py content generate-treatments && "
                                             "python manage.py translate_content --missing"))

    # ── City ──────────────────────────────────────────────────────────────
    def _city(self):
        city, created = City.objects.get_or_create(
            slug="istanbul",
            defaults={"name": "Istanbul", "country_code": "TR", "latitude": Decimal("41.0082"),
                      "longitude": Decimal("28.9784"), "airport_code": "IST", "source_language": "en"},
        )
        h = city.compute_source_hash()
        for lang, meta in LANGUAGE_META.items():
            if lang == city.source_language:
                continue
            slug = CITY_SLUGS.get(lang, {}).get("istanbul") or slugify(meta["istanbul"])
            CityTranslation.objects.get_or_create(
                city=city, language_code=lang,
                defaults={"name": meta["istanbul"], "slug": slug, "status": TranslationStatus.MACHINE,
                          "source_hash": h},
            )
        self.stdout.write(f"✓ City: {city} ({'yeni' if created else 'mevcut'})")
        return city

    # ── Treatments ────────────────────────────────────────────────────────
    def _treatments(self):
        out = {}
        for data in S.TREATMENTS:
            lo, hi = data["price"]
            t, created = Treatment.objects.get_or_create(key=data["key"], defaults={
                "category": data["category"], "icon": data["icon"], "order": data["order"],
                "typical_price_from": lo, "typical_price_to": hi, "price_unit": data["unit"],
                "stay_days": data["stay"], "visits": data["visits"], "procedure_duration": data["duration"],
                "name": data["name"], "slug": slugify(data["name"]), "short_description": data["short"],
                "body": data["body"], "faq": data["faq"], "meta_title": data["meta_title"],
                "meta_description": data["meta_description"], "focus_keyword": data["kw"],
                "source_language": "en",
            })
            out[t.key] = t
            # Tüm dillerde isim + kalıcı URL slug'ı (içerik AI çevirisiyle dolar → status pending)
            idx = TREATMENT_KEYS.index(t.key)
            for lang in LANGUAGE_META:
                if lang == t.source_language:
                    continue
                name = TREATMENT_NAMES[lang][idx]
                slug = (TREATMENT_SLUGS.get(lang) or [None] * 10)[idx] or slugify(name)
                TreatmentTranslation.objects.get_or_create(
                    treatment=t, language_code=lang,
                    defaults={"name": name, "slug": slug, "status": TranslationStatus.PENDING},
                )
        related = {"dental-implants": ["all-on-4", "zirconia-crowns", "root-canal"],
                   "porcelain-veneers": ["composite-veneers", "hollywood-smile", "teeth-whitening"],
                   "zirconia-crowns": ["porcelain-veneers", "dental-implants", "root-canal"],
                   "all-on-4": ["dental-implants", "zirconia-crowns"],
                   "hollywood-smile": ["porcelain-veneers", "zirconia-crowns", "teeth-whitening"],
                   "composite-veneers": ["porcelain-veneers", "teeth-whitening"],
                   "root-canal": ["zirconia-crowns", "tooth-filling"]}
        for key, rel in related.items():
            if key in out and not out[key].related.exists():
                out[key].related.set([out[r] for r in rel if r in out])
        self.stdout.write(f"✓ {len(out)} tedavi")
        return out

    # ── Clinic ────────────────────────────────────────────────────────────
    def _clinic(self, city):
        clinic, created = Clinic.objects.get_or_create(slug="dr-devrim-sipahi", defaults={
            "status": Clinic.STATUS_APPROVED, "is_primary": True, "is_verified": True,
            "name": "Dr. Dt. Devrim Biriken Sipahi Dental Clinic", "short_name": "Dr. Devrim Sipahi",
            "tagline": "Only the treatment your teeth actually need.",
            "short_description": "Ethical dentistry in Şişli, Istanbul: transparent diagnosis, single-doctor "
                                 "responsibility and direct WhatsApp contact with the dentist.",
            "description": "## Our approach\nThe most valuable thing decades of practice have taught us: good "
                           "medicine means knowing when to say no. We recommend only the treatment you need, "
                           "explain every option transparently and give you a fixed written quote.\n\n"
                           "## One doctor, full responsibility\nDr. Devrim Sipahi personally examines, plans and "
                           "follows up every patient — from the first WhatsApp message to aftercare at home.",
            "meta_title": "Dr. Devrim Sipahi — Dental Clinic in Şişli, Istanbul",
            "meta_description": "Dental clinic of Dr. Devrim Sipahi in Şişli, Istanbul. Ethical treatment, "
                                "transparent diagnosis, fixed prices. Free assessment via WhatsApp.",
            "city": city, "district": "Şişli", "neighborhood": "Osmanbey",
            "address": "Abide-i Hürriyet Cd No:148 D:11 Kat 4, 34360 Şişli/İstanbul", "postal_code": "34360",
            "latitude": Decimal("41.066152"), "longitude": Decimal("28.982098"),
            "maps_url": "https://maps.app.goo.gl/devrimklinik",
            "maps_embed_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3008.129955534435!2d28.982098085114472!3d41.06615189745108!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x14cab763e965bb4b%3A0x13b23dc999f216f8!2sDi%C5%9F%20hekimi%20Devrim%20Biriken%20Sipahi!5e0!3m2!1sen!2us!4v1749301527909!5m2!1sen!2us",
            "phone": "+90 505 577 18 83", "whatsapp": "905055771883", "email": "info@dentaltourism.tr",
            "website": "https://drdevrim.com", "instagram": "drdevrimbirikensipahi",
            "youtube_url": "https://www.youtube.com/@devrimbirikensipahi",
            "founded_year": 2020, "years_experience": 35, "patients_treated": 10000,
            "google_rating": Decimal("4.9"), "languages_spoken": ["tr", "en", "de", "nl"],
            "accreditations": [], "opening_hours": ["Mo-Fr 09:00-19:00", "Sa 10:00-16:00"],
            "source_language": "en",
        })
        Doctor.objects.get_or_create(slug="devrim-biriken-sipahi", defaults={
            "clinic": clinic, "name": "Devrim Biriken Sipahi", "honorific": "Dr. Dt.",
            "title_display": "Dentist", "is_lead_doctor": True, "languages_spoken": ["tr", "en"],
            "memberships": ["Türk Diş Hekimleri Birliği"],
            "bio": "Dr. Devrim Biriken Sipahi has more than 35 years of clinical experience. Her practice is "
                   "built on one principle: treat only what is necessary, explain everything, and save natural "
                   "teeth whenever possible.",
            "source_language": "en",
        })
        self.stdout.write(f"✓ Klinik: {clinic} ({'yeni' if created else 'mevcut'}) — "
                          "Google yorum sayısı / mezuniyet yılı gibi alanları admin'den tamamlayın")
        return clinic

    def _offers(self, clinic, treatments):
        for data in S.TREATMENTS:
            lo, hi = data["price"]
            ClinicTreatment.objects.get_or_create(clinic=clinic, treatment=treatments[data["key"]], defaults={
                "price_from": lo, "price_to": hi, "price_unit": data["unit"], "stay_days": data["stay"],
                "visits": data["visits"]})

    def _reviews(self, clinic, treatments):
        if clinic.reviews.exists():
            return
        for i, (name, cc, lang, text) in enumerate(S.REVIEWS):
            Review.objects.create(clinic=clinic, author_name=name, country_code=cc, language=lang, text=text,
                                  rating=5, source="google", order=i)
        for i, (name, cc, vid, tkey) in enumerate(S.VIDEOS):
            Review.objects.create(clinic=clinic, author_name=name, country_code=cc, video_id=vid, rating=5,
                                  source="youtube", treatment=treatments.get(tkey), order=10 + i)
        self.stdout.write("✓ Yorumlar ve video yorumlar")

    def _market_prices(self, treatments):
        for key, rows in S.MARKET_PRICES.items():
            for cc, cur, lo, hi, lo_eur, hi_eur in rows:
                MarketPrice.objects.get_or_create(treatment=treatments[key], country_code=cc, defaults={
                    "currency": cur, "price_min": lo, "price_max": hi, "price_min_eur": lo_eur,
                    "price_max_eur": hi_eur, "source": "Existing site copy — please verify", "verified": False})

    def _blog_categories(self):
        for i, (name, slug, funnel, desc) in enumerate(S.BLOG_CATEGORIES):
            BlogCategory.objects.get_or_create(slug=slug, defaults={
                "name": name, "funnel_stage": funnel, "description": desc, "order": i, "source_language": "en",
                "meta_description": desc})
        self.stdout.write("✓ Blog kategorileri")

    def _landing_pages(self, treatments, city):
        n = 0
        for t in treatments.values():
            _, c1 = LandingPage.objects.get_or_create(
                page_type=LandingPage.TYPE_TREATMENT_CITY, treatment=t, city=city,
                defaults={"h1": f"{t.name} in {city.name}", "noindex": True, "source_language": "en",
                          "intro": f"{t.short_description}", "meta_title": f"{t.name} {city.name} — Clinics & Prices"[:70],
                          "focus_keyword": f"{t.name.lower()} {city.name.lower()}"})
            _, c2 = LandingPage.objects.get_or_create(
                page_type=LandingPage.TYPE_TREATMENT_PRICE, treatment=t, city=None,
                defaults={"h1": f"{t.name} cost in Turkey", "noindex": True, "source_language": "en",
                          "meta_title": f"{t.name} Cost in Turkey vs UK"[:70],
                          "focus_keyword": f"{t.name.lower()} cost turkey"})
            n += c1 + c2
        self.stdout.write(f"✓ {n} programatik sayfa iskeleti (noindex — AI içerik üretilince indexlenir)")
