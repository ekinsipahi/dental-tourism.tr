"""
Ana sayfa SSS'sindeki "neden daha uygun?" cevabı: eski sitedeki "%50–70 daha düşük… fark uçak ve konaklamayı
karşılar" cümlesi yerine yüzdesiz, uçak/konaklama vaadi olmayan satış cümlesi (16 dil).
Yalnızca eski "50–70" cevabı hâlâ duruyorsa değiştirir (admin düzenlemeleri korunur).
"""
import hashlib
import json
import re

from django.db import migrations

ANSWER = {'ar': 'تمنح تكاليف التشغيل وفارق سعر الصرف تركيا ميزة واضحة مقارنةً بالدول الأوروبية الأخرى. المواد هي نفسها أو '
       'مكافئة لها، لكن العلاج أقل تكلفة بكثير — فميزانيتك تذهب إلى خطة علاجك، وتتوفر أيضاً خيارات أقل تكلفة.',
 'az': 'Türkiyədəki əməliyyat xərcləri və valyuta məzənnəsi fərqi digər Avropa ölkələri ilə müqayisədə aydın '
       'üstünlük verir. Materiallar eyni və ya ekvivalentdir, amma müalicə xeyli sərfəlidir — büdcəniz müalicə '
       'planınıza gedir, daha sərfəli seçimlər də mövcuddur.',
 'da': 'Driftsomkostninger og valutakursen giver Tyrkiet en klar fordel i forhold til andre europæiske lande. '
       'Materialerne er de samme eller tilsvarende, men behandlingen er langt mere overkommelig — dit budget går til '
       'din behandlingsplan, og der findes også billigere muligheder.',
 'de': 'Die Betriebskosten in der Türkei und der Wechselkurs bieten einen klaren Vorteil gegenüber anderen '
       'europäischen Ländern. Die Materialien sind gleich oder gleichwertig, die Behandlung ist aber deutlich '
       'günstiger — Ihr Budget fließt in Ihren Behandlungsplan, und es gibt auch günstigere Optionen.',
 'en': 'Operating costs and the exchange rate give Turkey a clear advantage over other European countries. The '
       'materials are the same or equivalent, but treatment is much more affordable — your budget goes into your '
       'treatment plan, and more affordable options are available too.',
 'es': 'Los costes operativos y el tipo de cambio dan a Turquía una clara ventaja frente a otros países europeos. '
       'Los materiales son los mismos o equivalentes, pero el tratamiento es mucho más asequible: tu presupuesto va '
       'a tu plan de tratamiento, y también hay opciones más económicas.',
 'fr': 'Les coûts d’exploitation et le taux de change donnent à la Turquie un net avantage sur les autres pays '
       'européens. Les matériaux sont identiques ou équivalents, mais le traitement est bien plus abordable — votre '
       'budget va dans votre plan de traitement, et des options plus abordables existent aussi.',
 'it': 'I costi di gestione e il cambio danno alla Turchia un netto vantaggio rispetto agli altri paesi europei. I '
       'materiali sono gli stessi o equivalenti, ma il trattamento è molto più conveniente — il tuo budget va nel '
       'tuo piano di cura, e ci sono anche opzioni più economiche.',
 'nl': 'De operationele kosten in Turkije en het valutaverschil geven een duidelijk voordeel ten opzichte van andere '
       'Europese landen. De materialen zijn gelijk of gelijkwaardig, maar de behandeling is veel voordeliger — uw '
       'budget gaat naar uw behandelplan, en er zijn ook voordeligere opties.',
 'no': 'Driftskostnader og valutakursen gir Tyrkia en klar fordel sammenlignet med andre europeiske land. '
       'Materialene er de samme eller tilsvarende, men behandlingen er langt rimeligere — budsjettet ditt går til '
       'behandlingsplanen din, og det finnes også rimeligere alternativer.',
 'pl': 'Koszty prowadzenia działalności i kurs walut dają Turcji wyraźną przewagę nad innymi krajami Europy. '
       'Materiały są takie same lub równoważne, ale leczenie jest znacznie tańsze — Twój budżet idzie na plan '
       'leczenia, a dostępne są też tańsze opcje.',
 'ro': 'Costurile de operare și cursul de schimb oferă Turciei un avantaj clar față de alte țări europene. '
       'Materialele sunt aceleași sau echivalente, dar tratamentul este mult mai accesibil — bugetul tău merge în '
       'planul de tratament, iar opțiuni mai accesibile sunt disponibile și ele.',
 'ru': 'Операционные расходы и разница в курсе валют дают Турции явное преимущество перед другими европейскими '
       'странами. Материалы те же или равноценные, но лечение значительно доступнее — ваш бюджет идёт на план '
       'лечения, а также есть более доступные варианты.',
 'sv': 'Driftskostnader och växelkursen ger Turkiet en tydlig fördel jämfört med andra europeiska länder. Materialen '
       'är desamma eller likvärdiga, men behandlingen är mycket mer prisvärd — din budget går till din '
       'behandlingsplan, och det finns även mer prisvärda alternativ.',
 'tr': "Türkiye'deki işletme maliyetleri ve döviz kuru farkı, Avrupa ülkelerine kıyasla ciddi bir avantaj sağlar. "
       'Kullanılan malzemeler aynı ya da eşdeğerdir ama tedavi çok daha uygun fiyatlıdır — bütçeniz doğrudan tedavi '
       'planınıza gider, daha uygun seçenekler de mevcuttur.',
 'uk': 'Операційні витрати та різниця в курсі валют дають Туреччині явну перевагу над іншими європейськими країнами. '
       'Матеріали ті самі або рівноцінні, але лікування значно доступніше — ваш бюджет іде на план лікування, а '
       'також є доступніші варіанти.'}

OLD = re.compile(r"50\s*[–-]\s*70")
FIELDS = ("eyebrow", "title", "subtitle", "body", "button_text", "items")  # ContentBlock.TRANSLATED_FIELDS


def _hash(obj):
    raw = json.dumps({f: getattr(obj, f) for f in FIELDS}, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def _fix(items, lang):
    out, changed = [], False
    for it in items or []:
        if isinstance(it, dict) and OLD.search(str(it.get("answer", ""))) and lang in ANSWER:
            it = {**it, "answer": ANSWER[lang]}
            changed = True
        out.append(it)
    return out, changed


def forwards(apps, schema_editor):
    ContentBlock = apps.get_model("core", "ContentBlock")
    ContentBlockTranslation = apps.get_model("core", "ContentBlockTranslation")
    block = ContentBlock.objects.filter(key="home-faq").first()
    if block is None:
        return
    old_hash = _hash(block)
    items, changed = _fix(block.items, block.source_language or "en")
    if changed:
        block.items = items
        ContentBlock.objects.filter(pk=block.pk).update(items=items)
    new_hash = _hash(block)
    for tr in ContentBlockTranslation.objects.filter(block=block):
        changes = {}
        items, changed = _fix(tr.items, tr.language_code)
        if changed:
            changes["items"] = items
        if new_hash != old_hash and tr.source_hash == old_hash:
            changes["source_hash"] = new_hash
        if changes:
            ContentBlockTranslation.objects.filter(pk=tr.pk).update(**changes)


class Migration(migrations.Migration):
    dependencies = [("core", "0004_contentblock_image_url")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
