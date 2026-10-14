"""
Klinik otel / uçak / transfer ayarlamıyor → rehberlerdeki ilgili satırlar değişir (16 dil):
  dental-tourism-agency: "transfer ve konaklama koordinasyonu" → "randevular seyahat tarihlerine göre"
  istanbul-guide: "önceden ayarlanmış transfer" → "metro, taksi veya araç çağırma uygulaması"
Yalnızca eski cümle hâlâ duruyorsa değiştirir (admin düzenlemeleri korunur); senkron çevirilerin source_hash'i
yeni kaynağa taşınır, böylece çeviriler "eskimiş" sayılmaz.
"""
import hashlib
import json

from django.db import migrations

AGENCY = {'ar': ('- تنسيق المواعيد والتنقلات والإقامة', '- مواعيد مخططة وفق تواريخ سفر عملائكم'),
 'az': ('- Görüşlərin, transferlərin və yerləşmənin koordinasiyası',
        '- Görüşlər müştərilərinizin səfər tarixlərinə uyğun planlaşdırılır'),
 'da': ('- Koordinering af tider, transfer og overnatning', '- Tider planlagt efter dine kunders rejsedatoer'),
 'de': ('- Koordination von Terminen, Transfers und Unterkunft',
        '- Termine abgestimmt auf die Reisedaten Ihrer Kunden'),
 'en': ('- Coordination of appointments, transfers and accommodation',
        "- Appointments planned around your clients' travel dates"),
 'es': ('- Coordinación de citas, traslados y alojamiento',
        '- Citas planificadas según las fechas de viaje de tus clientes'),
 'fr': ('- Coordination des rendez-vous, transferts et hébergement',
        '- Rendez-vous planifiés selon les dates de voyage de vos clients'),
 'it': ('- Coordinamento di appuntamenti, transfer e alloggio',
        '- Appuntamenti pianificati in base alle date di viaggio dei vostri clienti'),
 'nl': ('- Coördinatie van afspraken, transfers en accommodatie',
        '- Afspraken afgestemd op de reisdata van uw klanten'),
 'no': ('- Koordinering av timer, transport og overnatting', '- Timer planlagt etter kundenes reisedatoer'),
 'pl': ('- Koordynacja wizyt, transferów i noclegów', '- Wizyty planowane pod terminy podróży Twoich klientów'),
 'ro': ('- Coordonarea programărilor, transferurilor și cazării',
        '- Programări planificate în funcție de datele de călătorie ale clienților tăi'),
 'ru': ('- Координация приёмов, трансферов и проживания', '- Приёмы планируются под даты поездки ваших клиентов'),
 'sv': ('- Samordning av tider, transfer och boende', '- Tider planerade efter dina kunders resedatum'),
 'tr': ('- Randevu, transfer ve konaklama koordinasyonu',
        '- Randevular, müşterilerinizin seyahat tarihlerine göre planlanır'),
 'uk': ('- Координація прийомів, трансферів і проживання', '- Прийоми плануються під дати поїздки ваших клієнтів')}

GUIDE = {'ar': ('- من مطار إسطنبول: مترو M11 أو نقل محجوز مسبقاً',
        '- من مطار إسطنبول: مترو M11 أو سيارة أجرة أو تطبيق لطلب السيارات'),
 'az': ('- İstanbul hava limanından: M11 metrosu və ya əvvəlcədən sifariş edilmiş transfer',
        '- İstanbul hava limanından: M11 metrosu, taksi və ya taksi çağırma tətbiqi'),
 'da': ('- Fra Istanbul Lufthavn: metro M11 eller forudbestilt transfer',
        '- Fra Istanbul Lufthavn: metro M11, taxa eller en kørselsapp'),
 'de': ('- Vom Flughafen Istanbul: Metro M11 oder ein vorab gebuchter Transfer',
        '- Vom Flughafen Istanbul: Metro M11, Taxi oder eine Fahrdienst-App'),
 'en': ('- From Istanbul Airport: the M11 metro or a pre-booked transfer',
        '- From Istanbul Airport: the M11 metro, a taxi or a ride-hailing app'),
 'es': ('- Desde el aeropuerto de Estambul: metro M11 o un traslado reservado',
        '- Desde el aeropuerto de Estambul: metro M11, taxi o una app de transporte'),
 'fr': ('- Depuis l’aéroport d’Istanbul : métro M11 ou transfert réservé à l’avance',
        '- Depuis l’aéroport d’Istanbul : métro M11, taxi ou application de VTC'),
 'it': ('- Dall’aeroporto di Istanbul: metro M11 o transfer prenotato',
        '- Dall’aeroporto di Istanbul: metro M11, taxi o un’app di ride-hailing'),
 'nl': ('- Vanaf luchthaven Istanbul: metro M11 of een vooraf geboekte transfer',
        '- Vanaf luchthaven Istanbul: metro M11, een taxi of een taxi-app'),
 'no': ('- Fra Istanbul lufthavn: T-bane M11 eller forhåndsbestilt transport',
        '- Fra Istanbul lufthavn: T-bane M11, taxi eller en taxiapp'),
 'pl': ('- Z lotniska w Stambule: metro M11 lub zamówiony transfer',
        '- Z lotniska w Stambule: metro M11, taksówka lub aplikacja przewozowa'),
 'ro': ('- De la Aeroportul Istanbul: metroul M11 sau un transfer rezervat',
        '- De la Aeroportul Istanbul: metroul M11, taxi sau o aplicație de ride-sharing'),
 'ru': ('- Из аэропорта Стамбула: метро M11 или заказанный трансфер',
        '- Из аэропорта Стамбула: метро M11, такси или приложение для вызова такси'),
 'sv': ('- Från Istanbuls flygplats: tunnelbana M11 eller förbokad transfer',
        '- Från Istanbuls flygplats: tunnelbana M11, taxi eller en taxiapp'),
 'tr': ("- İstanbul Havalimanı'ndan: M11 metrosu veya önceden ayarlanmış transfer",
        "- İstanbul Havalimanı'ndan: M11 metrosu, taksi veya araç çağırma uygulamaları"),
 'uk': ('- З аеропорту Стамбула: метро M11 або замовлений трансфер',
        '- З аеропорту Стамбула: метро M11, таксі або застосунок для виклику таксі')}

FIELDS = ("slug", "h1", "lead", "body", "faq", "meta_title", "meta_description")  # SeoTopic.TRANSLATED_FIELDS


def _hash(obj):
    raw = json.dumps({f: getattr(obj, f) for f in FIELDS}, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def forwards(apps, schema_editor):
    SeoTopic = apps.get_model("seo", "SeoTopic")
    SeoTopicTranslation = apps.get_model("seo", "SeoTopicTranslation")
    for key, lines in (("dental-tourism-agency", AGENCY), ("istanbul-guide", GUIDE)):
        topic = SeoTopic.objects.filter(key=key).first()
        if topic is None:
            continue
        old_hash = _hash(topic)
        old, new = lines.get(topic.source_language or "en", lines["en"])
        if old in topic.body:
            topic.body = topic.body.replace(old, new)
            SeoTopic.objects.filter(pk=topic.pk).update(body=topic.body)
        new_hash = _hash(topic)
        for tr in SeoTopicTranslation.objects.filter(topic=topic):
            changes = {}
            old, new = lines.get(tr.language_code, ("", ""))
            if old and old in tr.body:
                changes["body"] = tr.body.replace(old, new)
            if new_hash != old_hash and tr.source_hash == old_hash:
                changes["source_hash"] = new_hash
            if changes:
                SeoTopicTranslation.objects.filter(pk=tr.pk).update(**changes)


class Migration(migrations.Migration):
    dependencies = [("seo", "0003_alter_keyword_page_type")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
