from dental_tourism.languages import LANGUAGE_META

from apps.clinics.models import Clinic, ClinicTreatment
from apps.localization.models import with_translations

from .models import MarketPrice


def offers_for(treatment, city=None):
    qs = (ClinicTreatment.objects.filter(treatment=treatment, is_active=True, clinic__status=Clinic.STATUS_APPROVED)
          .select_related("clinic", "clinic__city").order_by("price_from"))
    if city is not None:
        qs = qs.filter(clinic__city=city)
    return list(qs)


def market_prices(treatment, lang):
    """Okuyucunun pazarındaki (dile göre) yerel fiyatlar."""
    markets = LANGUAGE_META[lang]["markets"]
    rows = {m.country_code: m for m in MarketPrice.objects.filter(treatment=treatment, country_code__in=markets)}
    return [rows[c] for c in markets if c in rows]


def savings_pct(istanbul_eur, home_eur):
    if not istanbul_eur or not home_eur:
        return None
    return max(0, round((1 - float(istanbul_eur) / float(home_eur)) * 100))


def related_treatments(treatment, lang, limit=4):
    from apps.localization.models import localize_list

    from .models import Treatment

    qs = treatment.related.filter(is_active=True)
    if not qs.exists():
        qs = Treatment.objects.filter(is_active=True, category=treatment.category).exclude(pk=treatment.pk)
    return localize_list(with_translations(qs[:limit], lang), lang)
