"""Çeviri işleri — düz fonksiyonlar (Celery/Redis YOK). Periyodik: `python manage.py periodic --job translations`."""
import logging

logger = logging.getLogger(__name__)


def translate_missing(limit=None):
    """Eksik/başarısız/eskimiş çevirileri SENKRON tamamlar (cron komutu içinden çağrılır)."""
    from .llm import is_configured
    from .registry import all_specs
    from .service import languages_needing_work, translate_all

    if not is_configured():
        return {"skipped": "ANTHROPIC_API_KEY yok"}
    done = 0
    for spec in all_specs().values():
        for obj in spec.model.objects.all():
            if not spec.should_auto_translate(obj):
                continue
            langs = languages_needing_work(obj)
            if langs:
                result = translate_all(obj, languages=langs)
                logger.info("translate_missing %s#%s: %s", obj._meta.label_lower, obj.pk, result)
                done += 1
                if limit and done >= limit:
                    return {"objects": done}
    return {"objects": done}
