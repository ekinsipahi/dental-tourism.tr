"""
Yorum çevirileri.

* Mevcut yorumlar: apps/clinics/review_translations.json → `python manage.py seed_review_translations`
* Yeni yayınlanan yorumlar: ANTHROPIC_API_KEY varsa arka planda (sınırlı thread havuzu) 15 dile çevrilir.
  Orijinal metin her zaman saklanır ve sitede "orijinali göster" ile görülebilir.
"""
import json
import logging

from dental_tourism.languages import LANGUAGE_META

logger = logging.getLogger(__name__)

SYSTEM = ("You translate patient reviews of a dental clinic in Istanbul. Translate faithfully and naturally, keep the "
          "patient's tone, emojis and names. Never add or remove claims, never add prices.")


def translate_review(review_id):
    from apps.localization import llm

    from .models import Review

    r = Review.objects.filter(pk=review_id).first()
    if r is None or not r.text or not llm.is_configured():
        return
    targets = [lg for lg in LANGUAGE_META if lg != r.language and lg not in (r.text_translations or {})]
    if not targets:
        return
    schema = {"type": "object", "properties": {lg: {"type": "string"} for lg in targets},
              "required": targets, "additionalProperties": False}
    data = llm.generate_json(system=SYSTEM, schema=schema, effort="low", max_tokens=8000, blocks=[
        {"text": f"Source language: {r.language or 'auto-detect'}\nReview:\n{r.text}\n\n"
                 f"Return a JSON object with these language codes as keys: {json.dumps(targets)}"}])
    merged = {**(r.text_translations or {}), **{k: v for k, v in data.items() if v}}
    Review.objects.filter(pk=r.pk).update(text_translations=merged)
    logger.info("review %s translated to %s languages", r.pk, len(data))


def on_review_saved(sender, instance, created=False, raw=False, **kwargs):
    if raw or not instance.is_published or not instance.text:
        return
    from apps.localization import llm
    from apps.localization.dispatch import run_in_background

    if llm.is_configured() and len(instance.text_translations or {}) < len(LANGUAGE_META) - 1:
        run_in_background(translate_review, instance.pk)
